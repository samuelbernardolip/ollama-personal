#!/usr/bin/env python3
"""
Model-Agnostic Google Cloud Agent Platform MCP Bridge.
Connects to Google Cloud Agent Platform via Application Default Credentials (ADC).
Dynamically discovers and caches all available GCP models with configurable TTL.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DEFAULT_CACHE_TTL = 3600
CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/gcp_models_cache.json")
AGY_BIN = (
    shutil.which("agy")
    or os.path.expanduser("~/.local/bin/agy")
    or "/usr/bin/agy"
)
GCLOUD_BIN = shutil.which("gcloud") or "/usr/bin/gcloud"
SANDBOX_DIR = os.path.expanduser("~/.gemini/antigravity-gcp-sandbox")

FALLBACK_MODELS = [
    {"id": "gemini-4-carbon-medium", "name": "Gemini 4 Carbon (Medium)", "description": "Default balanced reasoning effort on Vertex AI"},
    {"id": "gemini-4-carbon-low", "name": "Gemini 4 Carbon (Low)", "description": "Fast reasoning effort on Vertex AI"},
    {"id": "gemini-4-carbon-high", "name": "Gemini 4 Carbon (High)", "description": "Maximum reasoning effort for deep architecture"},
    {"id": "claude-opus-5-5", "name": "Claude Opus 5.5", "description": "Anthropic frontier reasoning model hosted on Google Cloud ADC"},
    {"id": "claude-sonnet-5-5", "name": "Claude Sonnet 5.5", "description": "High-speed coding model hosted on Google Cloud ADC"},
    {"id": "gemini-3.1-pro", "name": "Gemini 3.1 Pro (GCP)", "description": "Enterprise Gemini Pro hosted on Vertex AI project"}
]

TOOLS = [
    {
        "name": "ask_google_cloud_model",
        "description": "Query any Google Cloud Agent Platform model (Gemini 4 Carbon, Claude Opus, Gemini Pro) via Antigravity CLI in native ADC mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Task or architectural question for the model"},
                "model": {
                    "type": "string",
                    "description": "Target model ID (e.g. gemini-4-carbon-medium, gemini-4-carbon-high, claude-opus-5-5). Defaults to gemini-4-carbon-medium.",
                    "default": "gemini-4-carbon-medium"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_google_cloud_models",
        "description": "List all Google Cloud Agent Platform models dynamically discovered on your GCP project, with caching support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh the dynamic models catalog from GCP via `agy models`, bypassing cache.",
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
        return int(os.environ.get("GCP_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except Exception:
        return DEFAULT_CACHE_TTL

def ensure_adc_sandbox():
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    gcloud_src = os.path.expanduser("~/.config/gcloud")
    gcloud_dst = os.path.join(SANDBOX_DIR, ".config", "gcloud")
    if os.path.exists(gcloud_src) and not os.path.exists(gcloud_dst):
        os.makedirs(os.path.dirname(gcloud_dst), exist_ok=True)
        try:
            os.symlink(gcloud_src, gcloud_dst)
        except OSError:
            pass

def check_adc() -> bool:
    adc_file = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    if not os.path.exists(adc_file):
        return False
    res = subprocess.run([GCLOUD_BIN, "auth", "application-default", "print-access-token"], capture_output=True, text=True)
    return res.returncode == 0

def fetch_models_dynamically() -> list:
    ensure_adc_sandbox()
    env = os.environ.copy()
    env["AGY_ADC_AUTH"] = "true"
    env["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    env["HOME"] = SANDBOX_DIR

    proc = subprocess.run([AGY_BIN, "models"], env=env, capture_output=True, text=True, timeout=15)
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
        desc = parts[1].strip() if len(parts) > 1 else f"Google Cloud model: {m_id}"
        if m_id and ("carbon" in m_id or "claude" in m_id or "gcp" in m_id) and m_id not in seen:
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
        sys.stderr.write(f"Warning: Failed to fetch dynamic GCP models: {e}\n")

    return FALLBACK_MODELS

def normalize_model_name(name: str) -> str:
    cleaned = (name or "").strip().lower()
    if cleaned in ["gemini-4-carbon", "gemini-carbon", "carbon"]:
        return "gemini-4-carbon-medium"
    return name or "gemini-4-carbon-medium"

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
                    "serverInfo": {"name": "google-cloud-mcp", "version": "3.0.0"}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool_name == "list_google_cloud_models":
                force_refresh = bool(args.get("refresh", False))
                models = get_available_models(force_refresh=force_refresh)
                cache_info = {
                    "provider": "Google Cloud Agent Platform (Enterprise ADC)",
                    "cached": not force_refresh and os.path.exists(CACHE_FILE),
                    "total_models": len(models),
                    "models": models
                }
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(cache_info, indent=2)}]}
                })
            elif tool_name == "ask_google_cloud_model":
                if not check_adc():
                    send({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": "Google Cloud ADC token missing or expired. Run 'gcp-auth-refresh' or 'gcloud auth application-default login'."}],
                            "isError": True
                        }
                    })
                    continue

                prompt = args.get("prompt", "")
                raw_model = args.get("model", "gemini-4-carbon-medium")
                model = normalize_model_name(raw_model)

                ensure_adc_sandbox()
                env = os.environ.copy()
                env["AGY_ADC_AUTH"] = "true"
                env["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
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
