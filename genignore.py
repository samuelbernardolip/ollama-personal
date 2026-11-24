#!/usr/bin/env python3
"""
genignore.py - Multi-Provider AI Ignore & Instruction File Generator

Generates, updates, and merges native ignore rules and configurations across:
  - Continue (.continueignore)
  - Antigravity (.agentignore)
  - Claude Code (.claude/settings.json permissions.deny + CLAUDE.md)
  - GitHub Copilot (.vscode/settings.json files/search.exclude + copilot-instructions.md)
  - OpenAI Codex (AGENTS.md)

Also preserves git-based ignore gathering and file-packing capabilities.
"""

import argparse
import fnmatch
import glob
import json
import os
import pathlib
import sys

# Base templates and instruction defaults
BASE_IGNORE_PATTERNS = [
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    "dist/",
    "build/",
    "__pycache__/",
    "*.pyc",
    ".env",
    ".env.*",
]

CLAUDE_MD_DEFAULT = """\
# Claude Code Instructions
## Project guidelines
- Follow existing coding conventions and architecture.
- Keep changes focused, minimal, and test-driven.
- Avoid unnecessary dependencies and unrelated modifications.
"""

COPILOT_INSTRUCTIONS_DEFAULT = """\
# GitHub Copilot Instructions
## Project guidelines
- Follow the existing project architecture and coding conventions.
- Keep changes focused, minimal, and idiomatic.
- Add or update tests when changing functionality.
- Avoid modifying unrelated files.
"""

CODEX_AGENTS_DEFAULT = """\
# Codex Instructions
## Project guidelines
- Keep changes focused and minimal.
- Run relevant tests after making changes.
- Avoid modifying unrelated files.
"""


def parse_gitignore(gitignore_path=".gitignore"):
    """Parse .gitignore excluding comments and blank lines."""
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def parse_gitattributes(gitattributes_path=".gitattributes"):
    """Extract filter= and filter=git-crypt protected patterns from .gitattributes."""
    crypt_patterns = []
    if os.path.exists(gitattributes_path):
        with open(gitattributes_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "filter=" in line:
                    parts = line.split()
                    if parts:
                        crypt_patterns.append(parts[0])
    return crypt_patterns


def gather_ignore_patterns(use_gitignore=True, use_gitattributes=True):
    """Merge ignore rules preserving insertion order and deduplicating."""
    patterns = []
    if use_gitignore:
        patterns.extend(parse_gitignore())
    if use_gitattributes:
        patterns.extend(parse_gitattributes())
    return list(dict.fromkeys(patterns))


def matches_any(path_str, patterns):
    """Check if a path matches any pattern or directory prefix."""
    for pat in patterns:
        if fnmatch.fnmatch(path_str, pat) or fnmatch.fnmatch(os.path.basename(path_str), pat):
            return True
        if pat.endswith("/") and path_str.startswith(pat.rstrip("/")):
            return True
    return False


def gather_files(input_patterns, use_gitignore, use_gitattributes, root_dir="."):
    """Gather files matching glob patterns or repository walk, filtered by ignore rules."""
    gitignore_pats = parse_gitignore() if use_gitignore else []
    gitattr_pats = parse_gitattributes() if use_gitattributes else []
    collected_files = []

    if not input_patterns:
        for dirpath, _, filenames in os.walk(root_dir):
            if ".git" in dirpath.split(os.sep):
                continue
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                if use_gitignore and matches_any(rel_path, gitignore_pats):
                    continue
                collected_files.append(rel_path)
        if use_gitattributes:
            for dirpath, _, filenames in os.walk(root_dir):
                if ".git" in dirpath.split(os.sep):
                    continue
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, root_dir)
                    if matches_any(rel_path, gitattr_pats) and rel_path not in collected_files:
                        collected_files.append(rel_path)
    else:
        for pat in input_patterns:
            matched = glob.glob(pat, recursive=True)
            for m in matched:
                if os.path.isfile(m):
                    rel_path = os.path.relpath(m, root_dir)
                    if rel_path not in collected_files:
                        collected_files.append(rel_path)

    return sorted(set(collected_files))


def deep_merge(base, update):
    """Recursively merge dicts and deduplicate list elements."""
    if not isinstance(base, dict) or not isinstance(update, dict):
        return update
    merged = dict(base)
    for key, value in update.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = deep_merge(merged[key], value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                # Preserve unique list elements in order
                merged[key] = list(dict.fromkeys(merged[key] + value))
            else:
                merged[key] = value
        else:
            merged[key] = value
    return merged


def write_json_file(filepath: pathlib.Path, additions: dict, overwrite: bool = False):
    """
    Create or merge a JSON configuration file.
    Evaluates existence before writing to guarantee accurate status reporting.
    """
    existed = filepath.exists()
    if overwrite or not existed:
        data = additions
    else:
        try:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ValueError(
                f"Cannot merge {filepath}: {e}. Fix the JSON file or run with --overwrite."
            )
        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot merge {filepath}: root JSON structure must be an object."
            )
        data = deep_merge(data, additions)

    new_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if existed and not overwrite:
        existing_content = filepath.read_text(encoding="utf-8")
        if existing_content == new_content:
            print(f"[SKIP]      {filepath} (configuration already up-to-date)")
            return

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(new_content, encoding="utf-8")

    if overwrite and existed:
        print(f"[OVERWRITE] {filepath}")
    elif existed:
        print(f"[UPDATE]    {filepath}")
    else:
        print(f"[CREATE]    {filepath}")


def write_text_file(filepath: pathlib.Path, default_content: str, extra_lines=None,
                    header=None, overwrite=False, append=False):
    """Write, append, or skip plain text/markdown instruction and ignore files."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    extra_lines = list(dict.fromkeys(extra_lines or []))

    additions = ""
    if extra_lines:
        prefix = f"\n{header}\n" if header else "\n"
        additions = prefix + "\n".join(extra_lines) + "\n"

    full_payload = default_content
    if additions:
        if not full_payload.endswith("\n"):
            full_payload += "\n"
        full_payload += additions.lstrip("\n")

    if not filepath.exists():
        filepath.write_text(full_payload, encoding="utf-8")
        print(f"[CREATE]    {filepath}")
        return

    if overwrite:
        filepath.write_text(full_payload, encoding="utf-8")
        print(f"[OVERWRITE] {filepath}")
        return

    if not append:
        print(f"[SKIP]      {filepath} (already exists)")
        return

    existing = filepath.read_text(encoding="utf-8")
    existing_lines = set(existing.splitlines())

    missing = [line for line in (extra_lines or []) if line not in existing_lines]
    needs_default = default_content.strip() not in existing

    if not missing and not needs_default:
        print(f"[SKIP]      {filepath} (already contains specified entries)")
        return

    with filepath.open("a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        if needs_default:
            f.write("\n" + default_content.strip() + "\n")
        if missing:
            if header and header not in existing:
                f.write(f"\n{header}\n")
            for line in missing:
                f.write(line + "\n")

    print(f"[APPEND]    {filepath}")


def format_claude_deny_rules(patterns):
    """Format patterns into Claude Code permissions.deny Read(...) rules."""
    rules = []
    for p in patterns:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean.startswith("*"):
            rules.append(f"Read(**/{p_clean})")
        elif "/" not in p_clean and not p_clean.startswith("**/"):
            rules.append(f"Read({p_clean})")
        else:
            rules.append(f"Read({p_clean})")
    return list(dict.fromkeys(rules))


def format_vscode_exclude_dict(patterns):
    """Format glob patterns into VS Code boolean exclude dictionaries."""
    result = {}
    for p in patterns:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean.startswith("*"):
            key = f"**/{p_clean}"
        elif "/" not in p_clean and not p_clean.startswith("**/"):
            key = p_clean
        else:
            key = p_clean
        result[key] = True
    return result


def generate_provider_configs(providers, append=False, overwrite=False, extra_patterns=None, root_dir="."):
    """Generate or update configurations tailored to each provider's native system."""
    root = pathlib.Path(root_dir)
    extra_patterns = list(dict.fromkeys(extra_patterns or []))

    # Compile the effective pattern list (baseline defaults + CLI patterns)
    all_patterns = list(dict.fromkeys(BASE_IGNORE_PATTERNS + extra_patterns))

    for provider in providers:
        if provider == "continue":
            default_txt = "# Continue ignore rules\n" + "\n".join(BASE_IGNORE_PATTERNS) + "\n"
            write_text_file(
                root / ".continueignore",
                default_content=default_txt,
                extra_lines=extra_patterns,
                header="# Additional ignore patterns",
                overwrite=overwrite,
                append=append,
            )

        elif provider == "antigravity":
            default_txt = "# Antigravity ignore rules\n" + "\n".join(BASE_IGNORE_PATTERNS) + "\n"
            write_text_file(
                root / ".agentignore",
                default_content=default_txt,
                extra_lines=extra_patterns,
                header="# Additional ignore patterns",
                overwrite=overwrite,
                append=append,
            )

        elif provider == "claude":
            # 1. Native security & search enforcement via .claude/settings.json
            deny_rules = format_claude_deny_rules(all_patterns)
            settings_payload = {
                "permissions": {
                    "deny": deny_rules
                }
            }
            write_json_file(root / ".claude" / "settings.json", settings_payload, overwrite=overwrite)

            # 2. General workspace guidance via CLAUDE.md
            write_text_file(
                root / "CLAUDE.md",
                default_content=CLAUDE_MD_DEFAULT,
                extra_lines=None,
                overwrite=overwrite,
                append=append,
            )

        elif provider == "copilot":
            # 1. Native editor and text search exclusions via .vscode/settings.json
            exclude_dict = format_vscode_exclude_dict(all_patterns)
            vscode_payload = {
                "files.exclude": exclude_dict,
                "search.exclude": exclude_dict,
            }
            write_json_file(root / ".vscode" / "settings.json", vscode_payload, overwrite=overwrite)

            # 2. Copilot chat and code guidance via .github/copilot-instructions.md
            write_text_file(
                root / ".github" / "copilot-instructions.md",
                default_content=COPILOT_INSTRUCTIONS_DEFAULT,
                extra_lines=None,
                overwrite=overwrite,
                append=append,
            )

        elif provider == "codex":
            # Instructional exclusion guidance in AGENTS.md
            exclude_lines = [f"- {p}" for p in all_patterns]
            codex_content = CODEX_AGENTS_DEFAULT.strip() + "\n\n## Files to exclude from analysis\n"
            codex_content += "Do not read, inspect, analyze, or modify:\n"
            codex_content += "\n".join(exclude_lines) + "\n\n"
            codex_content += "Do not include these files in context unless explicitly requested.\n"

            write_text_file(
                root / "AGENTS.md",
                default_content=codex_content,
                extra_lines=None,
                overwrite=overwrite,
                append=append,
            )


def main():
    parser = argparse.ArgumentParser(
        description="Merge project ignore rules, pack codebase contexts, or generate AI provider exclusion files."
    )
    parser.add_argument(
        "patterns",
        nargs="*",
        help="Positional patterns. Used as glob patterns for packing, or as extra exclusion patterns when paired with --generate-ignore.",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output destination path. Defaults to stdout.",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Exclude .gitignore patterns from rule resolution.",
    )
    parser.add_argument(
        "--no-gitattributes",
        action="store_true",
        help="Exclude .gitattributes filter/crypt patterns from rule resolution.",
    )

    # Provider generation options
    parser.add_argument(
        "--generate-ignore",
        action="store_true",
        help="Generate or update AI provider exclusion files and settings.",
    )
    parser.add_argument(
        "--provider",
        nargs="+",
        choices=["continue", "antigravity", "claude", "copilot", "codex", "all"],
        default=["all"],
        help="Target providers to generate (default: all).",
    )

    # Mutually exclusive write modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-a", "--append",
        action="store_true",
        help="Append missing predefined content and additional patterns without duplicating.",
    )
    mode_group.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing provider files instead of merging/skipping.",
    )

    args = parser.parse_args()

    # 1. Provider ignore & settings generation
    if args.generate_ignore:
        selected_providers = args.provider
        if "all" in selected_providers:
            selected_providers = ["continue", "antigravity", "claude", "copilot", "codex"]

        generate_provider_configs(
            providers=list(dict.fromkeys(selected_providers)),
            append=args.append,
            overwrite=args.overwrite,
            extra_patterns=args.patterns,
        )
        return

    # 2. File packing mode (when explicit positional file patterns are passed)
    if args.patterns:
        files = gather_files(
            args.patterns,
            use_gitignore=not args.no_gitignore,
            use_gitattributes=not args.no_gitattributes,
        )
        output_mode = "a" if args.append else "w"
        out_file = open(args.output, output_mode, encoding="utf-8") if args.output else sys.stdout
        try:
            for fpath in files:
                out_file.write(f"===FILE: {fpath}===\n")
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as rf:
                        out_file.write(rf.read())
                except Exception as e:
                    out_file.write(f"[Error reading file: {e}]\n")
                out_file.write("\n\n")
        finally:
            if args.output:
                out_file.close()
        return

    # 3. Default mode: Output merged .gitignore and .gitattributes rules to stdout
    patterns = gather_ignore_patterns(
        use_gitignore=not args.no_gitignore,
        use_gitattributes=not args.no_gitattributes,
    )
    output_mode = "a" if args.append else "w"
    out_file = open(args.output, output_mode, encoding="utf-8") if args.output else sys.stdout
    try:
        for pattern in patterns:
            out_file.write(pattern + "\n")
    finally:
        if args.output:
            out_file.close()


if __name__ == "__main__":
    main()
