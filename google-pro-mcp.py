#!/usr/bin/env python3
"""
Google AI Pro MCP Bridge for Antigravity & VS Code.
Connects directly to the Antigravity CLI (agy) under consumer Google AI Pro OAuth.
Dynamically fetches available models via `agy models` and caches them with a configurable TTL.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DEFAULT_CACHE_TTL = 3600  # 1 hour
CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/google_pro_models_cache.json")
AGY_BIN = (
    shutil.which("agy")
    or os.path.expanduser("~/.local/bin/agy")
    or "/usr/bin/agy"
)

# Sandbox directory to break recursive mcp_config.json loading
SANDBOX_DIR = os.path.expanduser("~/.gemini/antigravity-pro-sandbox")

FALLBACK_MODELS = [
    {"id": "gemini-4-hydrogen", "name": "Gemini 4 Hydrogen", "description": "Flagship multimodal agent orchestrator (Default)"},
    {"id": "gemini-4-neon", "name": "Gemini 4 Neon", "description": "High-efficiency balanced multimodal model"},
    {"id": "gemini-4-argon", "name": "Gemini 4 Argon", "description": "High-throughput rapid response model"},
    {"id": "gemini-3.1-pro", "name": "Gemini 3.1 Pro", "description": "Deep reasoning and structural planning"},
    {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash", "description": "Low-latency lightweight generation"},
    {"id": "claude-sonnet-5-5", "name": "Claude Sonnet 5.5", "description": "Anthropic coding and analysis model on AI Pro"},
    {"id": "claude-opus-5-5", "name": "Claude Opus 5.5", "description": "Anthropic frontier reasoning model on AI Pro"},
    {"id": "gpt-oss-120b-medium", "name": "GPT-OSS 120B Medium", "description": "Open weights high-capacity reasoning model"}
]

TOOLS = [
    {
        "name": "ask_google_pro_model",
        "description": "Query Google AI models included in your Google AI Pro subscription via Antigravity CLI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The coding task, prompt, or architectural query"},
                "model": {
                    "type": "string",
                    "description": "Target model ID (e.g. gemini-4-hydrogen, gemini-4-neon, gemini-3.1-pro, claude-sonnet-5-5). Defaults to gemini-4-hydrogen.",
                    "default": "gemini-4-hydrogen"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_google_pro_models",
        "description": "List all Google AI models dynamically discovered on your Google AI Pro subscription, with caching support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh the dynamic models catalog from `agy models`, bypassing disk cache.",
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
        return int(os.environ.get("GOOGLE_PRO_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except Exception:
        return DEFAULT_CACHE_TTL

def ensure_sandbox():
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    gemini_home = os.path.expanduser("~/.gemini")
    for item in ["oauth_credentials.json", "antigravity-cli"]:
        src = os.path.join(gemini_home, item)
        dst = os.path.join(SANDBOX_DIR, item)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                os.symlink(src, dst)
            except OSError:
                pass

def fetch_models_dynamically() -> list:
    ensure_sandbox()
    env = os.environ.copy()
    env["AGY_ADC_AUTH"] = "false"
    env["HOME"] = SANDBOX_DIR

    proc = subprocess.run([AGY_BIN, "models"], env=env, capture_output=True, text=True, timeout=15)
    if proc.returncode != 0:
        raise RuntimeError(f"agy models failed ({proc.returncode}): {proc.stderr}")

    models = []
    seen = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Available"):
            continue
        parts = line.split(maxsplit=1)
        m_id = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else f"Google AI Pro model: {m_id}"
        if m_id and m_id not in seen:
            seen.add(m_id)
            models.append({"id": m_id, "name": m_id, "description": desc})

    return models if models else FALLBACK_MODELS

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
        sys.stderr.write(f"Warning: Failed to fetch dynamic Google Pro models: {e}\n")

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("models", FALLBACK_MODELS)
        except Exception:
            pass

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
                    "serverInfo": {"name": "google-pro-mcp", "version": "1.0.0"}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool_name == "list_google_pro_models":
                force_refresh = bool(args.get("refresh", False))
                models = get_available_models(force_refresh=force_refresh)
                cache_info = {
                    "provider": "Google AI Pro (Consumer Subscription)",
                    "cached": not force_refresh and os.path.exists(CACHE_FILE),
                    "total_models": len(models),
                    "models": models
                }
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(cache_info, indent=2)}]}
                })
            elif tool_name == "ask_google_pro_model":
                prompt = args.get("prompt", "")
                model = args.get("model", "gemini-4-hydrogen").strip() or "gemini-4-hydrogen"

                ensure_sandbox()
                env = os.environ.copy()
                env["AGY_ADC_AUTH"] = "false"
                env["HOME"] = SANDBOX_DIR

                proc = subprocess.run(
                    [AGY_BIN, "--disable-slash-commands", "--model", model, "-p", prompt],
                    env=env, capture_output=True, text=True
                )
                output = proc.stdout if proc.returncode == 0 else f"Execution Error ({proc.returncode}): {proc.stderr}"
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": output}], "isError": proc.returncode != 0}
                })

if __name__ == "__main__":
    main()
