#!/usr/bin/env python3
"""
Upgraded OpenAI Codex MCP Bridge for Antigravity & VS Code.
Wraps non-interactive `codex exec` calls over JSON-RPC stdio.
Dynamically retrieves available Codex models and caches them with a configurable TTL.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DEFAULT_CACHE_TTL = 3600
CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/codex_models_cache.json")
CODEX_BIN = (
    shutil.which("codex")
    or os.path.expanduser("~/.local/bin/codex")
    or "/usr/bin/codex"
)
HOME = os.path.expanduser("~")

FALLBACK_MODELS = [
    {"id": "gpt-5.3-codex", "name": "GPT-5.3 Codex", "description": "Primary high-precision agent coding engine (Default)"},
    {"id": "gpt-6.1", "name": "GPT-6.1", "description": "Frontier general reasoning and complex algorithmic analysis"},
    {"id": "gpt-5.3-codex-mini", "name": "GPT-5.3 Codex Mini", "description": "Fast, cost-effective model for concise refactors"},
    {"id": "o3", "name": "o3", "description": "High-depth mathematical and algorithmic reasoner"},
    {"id": "o3-mini", "name": "o3-mini", "description": "Low-latency STEM and logic reasoning model"},
    {"id": "gpt-4o", "name": "GPT-4o", "description": "Versatile multimodal coding and tool-calling model"}
]

TOOLS = [
    {
        "name": "ask_codex",
        "description": "Execute an instruction or code query non-interactively using OpenAI Codex CLI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The coding task, prompt, or question for Codex"},
                "model": {
                    "type": "string",
                    "description": "Target OpenAI model (e.g. gpt-5.3-codex, gpt-6.1, gpt-5.3-codex-mini). Defaults to gpt-5.3-codex.",
                    "default": "gpt-5.3-codex"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_codex_models",
        "description": "List all OpenAI models available for your Codex CLI profile, with caching support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh the dynamic models catalog from `codex models`, bypassing cache.",
                    "default": False
                }
            }
        }
    }
]

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def get_cache_ttl() -> int:
    try:
        return int(os.environ.get("CODEX_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except Exception:
        return DEFAULT_CACHE_TTL

def fetch_models_dynamically(codex_home: str) -> list:
    env = os.environ.copy()
    env["CODEX_HOME"] = codex_home

    proc = subprocess.run([CODEX_BIN, "models"], env=env, capture_output=True, text=True, timeout=10)
    if proc.returncode != 0:
        return FALLBACK_MODELS

    models = []
    seen = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Available"):
            continue
        parts = line.split(maxsplit=1)
        m_id = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else f"OpenAI Codex model: {m_id}"
        if m_id and m_id not in seen:
            seen.add(m_id)
            models.append({"id": m_id, "name": m_id, "description": desc})

    return models if models else FALLBACK_MODELS

def get_available_models(codex_home: str, force_refresh: bool = False) -> list:
    now = time.time()
    cache_ttl = get_cache_ttl()
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if now - data.get("timestamp", 0) < cache_ttl and "models" in data:
                return data["models"]
        except Exception:
            pass

    try:
        models = fetch_models_dynamically(codex_home)
        if models:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": now, "models": models}, f, indent=2)
            return models
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to fetch dynamic Codex models: {e}\n")

    return FALLBACK_MODELS

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "id" not in req:
            continue

        req_id = req.get("id")
        method = req.get("method")

        env = os.environ.copy()
        codex_home = env.get("CODEX_HOME", os.path.join(HOME, ".codex"))

        if method == "initialize":
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "codex-mcp-bridge", "version": "2.0.0"}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool_name == "list_codex_models":
                force_refresh = bool(args.get("refresh", False))
                models = get_available_models(codex_home, force_refresh=force_refresh)
                cache_info = {
                    "provider": "OpenAI Codex CLI",
                    "profile_directory": codex_home,
                    "cached": not force_refresh and os.path.exists(CACHE_FILE),
                    "total_models": len(models),
                    "models": models
                }
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(cache_info, indent=2)}]}
                })
            elif tool_name == "ask_codex":
                prompt = args.get("prompt", "")
                model = args.get("model", "gpt-5.3-codex").strip() or "gpt-5.3-codex"

                proc = subprocess.run(
                    [CODEX_BIN, "exec", "-m", model, prompt],
                    env=env, capture_output=True, text=True
                )
                output = proc.stdout if proc.returncode == 0 else f"Codex Error ({proc.returncode}): {proc.stderr}"
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": output}], "isError": proc.returncode != 0}
                })

if __name__ == "__main__":
    main()
