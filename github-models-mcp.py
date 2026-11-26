#!/usr/bin/env python3
"""
GitHub Copilot Models MCP Bridge for Antigravity & VS Code.
Connects directly to the GitHub Copilot CLI executable (`copilot` or `gh copilot`).
Dynamically discovers available models via Agent Client Protocol (ACP) handshake,
caches the catalog with configurable TTL, and defaults to `auto` for discounted cost routing.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DEFAULT_CACHE_TTL = 3600  # 1 hour
CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/models_cache.json")

FALLBACK_MODELS = [
    {"id": "auto", "name": "Auto (Cost-Discounted Routing)", "description": "GitHub Copilot auto-selected model; discounted credit multiplier (Default)"},
    {"id": "claude-sonnet-5.5", "name": "Claude Sonnet 5.5", "description": "High-speed coding and analysis model"},
    {"id": "grok-4.7", "name": "Grok 4.7", "description": "Advanced algorithmic reasoning model"},
    {"id": "mai-code-2", "name": "MAI Code 2", "description": "Specialized codebase synthesis and refactoring"},
    {"id": "mai-code-2-flash", "name": "MAI Code 2 Flash", "description": "Ultra-fast code completions and quick checks"},
    {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o", "description": "Versatile multimodal coding and tool-calling model"},
    {"id": "openai/gpt-4o-mini", "name": "OpenAI GPT-4o Mini", "description": "Lightweight, fast model for simple edits"},
    {"id": "kimi-k3", "name": "Kimi K3", "description": "Long-context reasoning and repository comprehension"}
]

TOOLS = [
    {
        "name": "ask_github_model",
        "description": "Query GitHub Copilot model inference with your active GitHub Copilot subscription. Defaults to `auto` for discounted cost routing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The coding question, prompt, or task for the model"},
                "model": {
                    "type": "string",
                    "description": "Target model ID (e.g. auto, claude-sonnet-5.5, grok-4.7, mai-code-2, mai-code-2-flash, openai/gpt-4o). Defaults to `auto`.",
                    "default": "auto"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_github_models",
        "description": "List all AI models dynamically discovered on your GitHub Copilot subscription, with caching support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh the dynamic models catalog from Copilot CLI, bypassing disk cache.",
                    "default": False
                }
            }
        }
    }
]

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def get_copilot_bin() -> str:
    path = os.path.expanduser("~/.local/share/gh/copilot/copilot")
    if os.path.exists(path) and os.access(path, os.X_OK):
        return path
    for name in ["copilot", "gh-copilot"]:
        b = shutil.which(name)
        if b:
            return b
    return "copilot"

def get_cache_ttl() -> int:
    try:
        return int(os.environ.get("GITHUB_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except Exception:
        return DEFAULT_CACHE_TTL

def fetch_models_dynamically() -> list:
    copilot_bin = get_copilot_bin()
    try:
        proc = subprocess.Popen([copilot_bin, "--acp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        return FALLBACK_MODELS

    init_msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "github-models-mcp", "version": "1.0"}}}
    try:
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        if line:
            resp = json.loads(line)
            caps = resp.get("result", {}).get("capabilities", {})
            m_list = caps.get("models", {}).get("available", [])
            if m_list:
                models = [{"id": "auto", "name": "Auto (Cost-Discounted Routing)", "description": "GitHub Copilot auto-selected model; discounted credit multiplier (Default)"}]
                for m in m_list:
                    m_id = m.get("id") if isinstance(m, dict) else str(m)
                    if m_id and m_id != "auto":
                        models.append({"id": m_id, "name": m_id, "description": f"GitHub Copilot model: {m_id}"})
                proc.terminate()
                return models
    except Exception:
        pass
    finally:
        try:
            proc.terminate()
        except Exception:
            pass

    return FALLBACK_MODELS

def get_available_models(force_refresh: bool = False) -> list:
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
        models = fetch_models_dynamically()
        if models:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": now, "models": models}, f, indent=2)
            return models
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to fetch dynamic Copilot models: {e}\n")

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

        if method == "initialize":
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "github-models-mcp", "version": "2.0.0"}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool_name == "list_github_models":
                force_refresh = bool(args.get("refresh", False))
                models = get_available_models(force_refresh=force_refresh)
                cache_info = {
                    "provider": "GitHub Copilot",
                    "cached": not force_refresh and os.path.exists(CACHE_FILE),
                    "total_models": len(models),
                    "models": models
                }
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(cache_info, indent=2)}]}
                })
            elif tool_name == "ask_github_model":
                prompt = args.get("prompt", "")
                model = args.get("model", "auto").strip() or "auto"
                copilot_bin = get_copilot_bin()

                cmd = [copilot_bin, "-p", prompt]
                if model != "auto":
                    cmd.extend(["--model", model])

                proc = subprocess.run(cmd, capture_output=True, text=True)
                output = proc.stdout if proc.returncode == 0 else f"Copilot CLI Error ({proc.returncode}): {proc.stderr}"
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": output}], "isError": proc.returncode != 0}
                })

if __name__ == "__main__":
    main()
