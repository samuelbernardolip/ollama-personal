#!/usr/bin/env bash
# ==============================================================================
# update-ai-ignore.sh - Shell Wrapper for Multi-Provider AI Ignore Generation
# ==============================================================================
# Synchronizes AI provider ignore and instruction files using genignore.py.
# Supports manual execution, automated cron, or invocation via Git hooks.
# ==============================================================================

set -euo pipefail

# 1. Resolve project root directory
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    PROJECT_ROOT="$(git rev-parse --show-toplevel)"
else
    PROJECT_ROOT="$(pwd)"
fi

cd "$PROJECT_ROOT"

# 2. Locate genignore.py executable or script
GENIGNORE_PATH=""
CANDIDATE_PATHS=(
    "$PROJECT_ROOT/genignore.py"
    "$PROJECT_ROOT/scripts/genignore.py"
    "$PROJECT_ROOT/.config/genignore.py"
    "$(readlink -f "$0")"
    "$(which genignore.py 2>/dev/null || true)"
)

for candidate in "${CANDIDATE_PATHS[@]}"; do
    if [[ -n "$candidate" && -f "$candidate" ]]; then
        GENIGNORE_PATH="$candidate"
        break
    fi
done

if [[ -z "$GENIGNORE_PATH" ]]; then
    echo "[!] Error: genignore.py not found in project root, scripts/, or system PATH." >&2
    echo "    Please place genignore.py in '$PROJECT_ROOT/' or make it executable in PATH." >&2
    exit 1
fi

# Ensure Python 3 interpreter is available
PYTHON_BIN="$(which python3 2>/dev/null || which python 2>/dev/null || true)"
if [[ -z "$PYTHON_BIN" ]]; then
    echo "[!] Error: python3 interpreter not found." >&2
    exit 1
fi

# 3. Parse options and extra patterns
STAGE_FILES=false
FORCE_RUN=false
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --stage|-s)
            STAGE_FILES=true
            shift
            ;;
        --force|-f)
            FORCE_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $(basename "$0") [--stage|-s] [--force|-f] [EXTRA_PATTERNS...]"
            echo ""
            echo "Options:"
            echo "  --stage, -s    Automatically 'git add' generated/updated provider files."
            echo "  --force, -f    Run genignore.py regardless of whether .gitignore or .gitattributes changed."
            echo "  --help, -h     Show this help message."
            exit 0
            ;;
        *)
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# 4. Check if .gitignore or .gitattributes have uncommitted changes
CHANGED=false

if [[ "$FORCE_RUN" == true ]]; then
    CHANGED=true
elif git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Check both staged and unstaged changes for .gitignore or .gitattributes
    if git diff --name-only HEAD 2>/dev/null | grep -qE '^(\.gitignore|\.gitattributes)$' || \
       git status --porcelain 2>/dev/null | grep -qE '(^\?\?|^.[MD]|^[MD].)[[:space:]]+(\.gitignore|\.gitattributes)'; then
        CHANGED=true
    fi
else
    # If not a git repository, run by default
    CHANGED=true
fi

if [[ "$CHANGED" == false ]]; then
    echo "[*] Neither .gitignore nor .gitattributes have changed. Nothing to do."
    exit 0
fi

echo "[*] Synchronizing AI provider ignore files using genignore.py..."

# 5. Execute genignore.py with --generate-ignore --append and any extra patterns
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    "$PYTHON_BIN" "$GENIGNORE_PATH" --generate-ignore --append "${EXTRA_ARGS[@]}"
else
    "$PYTHON_BIN" "$GENIGNORE_PATH" --generate-ignore --append
fi

# 6. Auto-stage files if requested and in a Git repository
if [[ "$STAGE_FILES" == true ]] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    PROVIDER_FILES=(
        ".continueignore"
        ".agentignore"
        ".claude/settings.json"
        "CLAUDE.md"
        ".vscode/settings.json"
        ".github/copilot-instructions.md"
        "AGENTS.md"
    )

    FILES_TO_STAGE=()
    for f in "${PROVIDER_FILES[@]}"; do
        if [[ -f "$PROJECT_ROOT/$f" ]]; then
            FILES_TO_STAGE+=("$f")
        fi
    done

    if [[ ${#FILES_TO_STAGE[@]} -gt 0 ]]; then
        git add "${FILES_TO_STAGE[@]}"
        echo "[*] Automatically staged updated AI provider files: ${FILES_TO_STAGE[*]}"
    fi
fi

echo "[✓] AI ignore and instruction files successfully synchronized."
