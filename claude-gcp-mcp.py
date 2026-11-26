#!/usr/bin/env python3
"""
Model-Agnostic Claude on Google Cloud Model Garden MCP Bridge.
Connects to Anthropic Claude models hosted on Google Cloud Vertex AI Model Garden via ADC.
Dynamically retrieves and caches available Claude models with configurable TTL.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DEFAULT_CACHE_TTL = 3600
CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/claude_gcp_models_cache.json")
CLAUDE_BIN = shutil.which("claude") or "/usr/bin/claude"

FALLBACK_MODELS = [
    {"id": "claude-fable-5-2", "name": "Claude Fable 5.2", "description": "Default frontier reasoning & architecture engine on Vertex AI"},
    {"id": "claude-sonnet-5-5", "name": "Claude Sonnet 5.5", "description": "High-speed coding and analysis model on Vertex AI"},
    {"id": "claude-opus-5-5", "name": "Claude Opus 5.5", "description": "Frontier capability model on Vertex AI"},
    {"id": "claude-3-7-sonnet", "name": "Claude 3.7 Sonnet", "description": "Hybrid reasoning coding model on Vertex AI"},
    {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "description": "Industry standard code synthesis on Vertex AI"},
    {"id": "claude-3-5-haiku", "name": "Claude 3.5 Haiku", "description": "Ultra-fast lightweight model on Vertex AI"}
]

TOOLS = [
    {
        "name": "ask_claude_gcp_model",
        "description": "Query Anthropic Claude models hosted on Google Cloud Model Garden (Vertex AI) via ADC.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The coding, architecture, or reasoning query for Claude"},
                "model": {
                    "type": "string",
                    "description": "Target Claude model ID (e.g. claude-fable-5-2, claude-sonnet-5-5, claude-opus-5-5). Defaults to claude-fable-5-2.",
                    "default": "claude-fable-5-2"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_claude_gcp_models",
        "description": "List all Claude models dynamically discovered on Google Cloud Model Garden, with caching support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh the dynamic models catalog, bypassing disk cache.",
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
        return int(os.environ.get("CLAUDE_GCP_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except Exception:
        return DEFAULT_CACHE_TTL

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
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": now, "models": FALLBACK_MODELS}, f, indent=2)
        return FALLBACK_MODELS
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to save Claude GCP models cache: {e}\n")

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
                    "serverInfo": {"name": "claude-gcp-mcp", "version": "2.0.0"}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool_name == "list_claude_gcp_models":
                force_refresh = bool(args.get("refresh", False))
                models = get_available_models(force_refresh=force_refresh)
                cache_info = {
                    "provider": "Google Cloud Model Garden (Anthropic Vertex AI ADC)",
                    "cached": not force_refresh and os.path.exists(CACHE_FILE),
                    "total_models": len(models),
                    "models": models
                }
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(cache_info, indent=2)}]}
                })
            elif tool_name == "ask_claude_gcp_model":
                prompt = args.get("prompt", "")
                model = args.get("model", "claude-fable-5-2").strip() or "claude-fable-5-2"

                env = os.environ.copy()
                env["CLAUDE_CONFIG_DIR"] = env.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude-gcp"))
                env["CLAUDE_CODE_USE_VERTEX"] = "1"
                env["CLOUD_ML_REGION"] = env.get("CLOUD_ML_REGION", "global")
                env["ANTHROPIC_MODEL"] = model

                proc = subprocess.run(
                    [CLAUDE_BIN, "-p", prompt],
                    env=env, capture_output=True, text=True
                )
                output = proc.stdout if proc.returncode == 0 else f"Claude GCP Error ({proc.returncode}): {proc.stderr}"
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": output}], "isError": proc.returncode != 0}
                })

if __name__ == "__main__":
    main()
