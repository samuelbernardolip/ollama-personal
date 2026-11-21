# Complete MCP Integration Guide for VS Code on Arch Linux: Antigravity, Claude Code, OpenAI Codex, and GitHub Copilot (Native Edition)

An enterprise-grade reference architecture for orchestrating multi-provider AI agents, Model Context Protocol (MCP) servers, and isolated developer identities under Arch Linux (rolling release, systemd, KDE Plasma 6 on Wayland) using **100% native host binaries** without container overhead.

---

## 1. System Architecture and Identity Isolation Matrix

On Arch Linux, rolling updates and cutting-edge upstream packages in the Arch User Repository (AUR) provide native access to official AI developer tooling. With `google-cloud-cli` available natively via the AUR, container runtimes (such as Docker or Podman) are completely unnecessary for Google Cloud SDK authentication, token verification, and Application Default Credentials (ADC) lifecycle management.

This architecture establishes strict credential boundaries across four AI providers and seven operational models and subscriptions:

1. **Google AI Pro (Consumer Subscription)**: Flat-rate consumer subscription driving daily interactive development in the Google Antigravity VS Code extension and the Antigravity CLI (`agy-pro`).
2. **Google Cloud Agent Platform (Enterprise ADC)**: Pay-as-you-go Vertex AI infrastructure providing on-demand execution for **Gemini 4 Carbon** and **Claude Opus 5.5**, accessed via native Arch `google-cloud-cli` ADC authentication and a zero-dependency local MCP bridge.
3. **Anthropic Teams (Organization OAuth)**: Standard corporate team subscription driving the official Claude Code VS Code extension and terminal workflow (`claude-teams`).
4. **Claude Fable 5.2 on Google Cloud Model Garden**: Enterprise Claude execution hosted on Google infrastructure, isolated through a dedicated configuration directory (`~/.claude-gcp`) and invoked as an MCP subagent.
5. **OpenAI ChatGPT Plus (€23/mo Consumer OAuth)**: Flat-rate consumer access driving the OpenAI Codex CLI and VS Code extension (`openai-codex-plus`), isolated within `~/.codex`.
6. **OpenAI API (Pay-As-You-Go)**: On-demand per-token API billing used when Plus rate limits are exhausted or for automated background tasks, isolated within `~/.codex-api`.
7. **GitHub Copilot (Student / Individual / Enterprise)**: GitHub's code intelligence engine operating alongside local MCP servers, paired with a native Node-based GitHub MCP server to provide workspace awareness and repository telemetry across all agents.

### Complete Provider and Billing Matrix

| Provider / Subscription | Primary Host Client | Auth Mechanism | Configuration Directory | MCP Server Identifier | Financial Impact / Metering |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google AI Pro** | Antigravity IDE / `agy-pro` | Browser OAuth (Google SSO) | `~/.gemini/` | Native Host Agent | Flat monthly subscription (€0 additional) |
| **Google Cloud Agent Platform** | `agy-mcp-bridge` / `agy-gcp` | ADC Token via Native `gcloud` | `~/.config/gcloud/` | `gemini-carbon-gcp` | Pay-as-you-go per token on GCP project |
| **Anthropic Teams** | Claude Code IDE / `claude-teams` | Browser OAuth (Anthropic SSO) | `~/.claude/` | `claude-teams` | Flat team seat license |
| **Google Cloud Model Garden (Fable 5.2)** | Claude Code CLI / MCP | Vertex AI ADC Token | `~/.claude-gcp/` | `claude-fable-gcp` | Pay-as-you-go per token on GCP project |
| **OpenAI ChatGPT Plus** | Codex IDE / `codex-plus` | Terminal OAuth (ChatGPT Web) | `~/.codex/` | `openai-codex-plus` | Flat €23/month (subject to cancellation) |
| **OpenAI API** | Codex IDE / `codex-api` | Secret API Key (`sk-proj-...`) | `~/.codex-api/` | `openai-codex-api` | Pay-as-you-go per token balance |
| **GitHub Copilot** | Copilot Chat VS Code | GitHub OAuth Token | `~/.config/github-copilot/` | `github-mcp` | Included via Student Pack / Monthly seat |

---

## 2. Arch Linux Host Prerequisites and Package Management

Arch Linux relies on `pacman` for official core packages and the Arch User Repository (AUR) for third-party developer tools and AI agents. By utilizing AUR packages, the entire stack runs natively on the bare metal, removing container layers, volume permission mapping, and virtualization latency.

### Step 2.1: Install Core System Dependencies and OpenAI Codex via `pacman`

Arch Linux provides the official **OpenAI Codex CLI** package directly in the **`[extra]`** repository as **`openai-codex`**, which installs the native `/usr/bin/codex` executable directly into your system PATH. Install it alongside standard build tools, desktop secret storage, and Node.js runtimes:

```bash
# Install core tools and openai-codex from official [extra] repository
sudo pacman -Syu --needed \
  base-devel \
  git \
  github-cli \
  nodejs \
  npm \
  python \
  python-pip \
  libsecret \
  kwallet \
  kwallet-pam \
  xdg-utils \
  openai-codex
```

Verify that `codex` is immediately available from `/usr/bin/`:

```bash
which codex
# Output: /usr/bin/codex

pacman -Q openai-codex
# Output: openai-codex <version>
```

*Note: Ensure `kwallet-pam` is active in your PAM configuration (`/etc/pam.d/sddm` or `/etc/pam.d/login`) so your KWallet 6 keyring unlocks automatically at graphical login.*

### Step 2.2: Install VS Code and Native AI Agents via AUR (`yay` / `paru`)

Using an AUR helper like `yay` or `paru`, install the official VS Code binary, the native Google Cloud CLI, Claude Code, and the official Google Antigravity CLI package (`aur/antigravity-cli`):

```bash
# 1. Install official VS Code binary (recommended over Code - OSS for extension marketplace compatibility)
yay -S --needed visual-studio-code-bin

# 2. Install native Google Cloud CLI (eliminates Docker containers completely)
yay -S --needed google-cloud-cli

# 3. Install AI CLI packages from the AUR
yay -S --needed \
  claude-code \
  antigravity-cli
```

*Notes on package selection:*
* **`aur/antigravity-cli`**: Installs the genuine Google Antigravity command-line binary (`/usr/bin/agy`). Do **not** install `aur/python-google-antigravity`, which is an unrelated Python client SDK and does not provide the `agy` command-line executable.
* **`google-cloud-cli`**: If you prefer precompiled binary archives rather than building from source, `yay -S --needed google-cloud-cli-bin` can be used.

### Step 2.3: Alternative Installation Methods for Google Antigravity CLI (`agy`)

If `aur/antigravity-cli` is ever undergoing upstream maintenance, you can obtain the exact same binary through either of these direct fallbacks:

#### Method A: Official Standalone Installer
Install Google's official static binary directly into user space (`~/.local/bin/agy`):

```bash
mkdir -p ~/.local/bin
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Ensure `~/.local/bin` is in your shell `PATH` in `~/.bashrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

#### Method B: Symlink from the VS Code Extension
If you already use the official **Google Antigravity** extension in VS Code (`Google.google-antigravity`), it automatically bundles the compiled `agy` service engine under `~/.antigravity/bin/agy` (or `~/.gemini/antigravity/bin/agy`). You can symlink it into your path:

```bash
mkdir -p ~/.local/bin
ln -sf ~/.antigravity/bin/agy ~/.local/bin/agy
```

#### Optional: Standalone User-Space Fallbacks
If any package is undergoing upstream maintenance:
```bash
# Anthropic Claude Code CLI via user-space Node runtime
npm install -g @anthropic-ai/claude-code --prefix ~/.local

# OpenAI Codex CLI via user-space Node runtime (fallback if extra/openai-codex is unavailable)
npm install -g @openai/codex --prefix ~/.local
```

Verify binary paths using `which code gcloud claude agy codex gh`. All tools resolve cleanly to native system paths:
* **VS Code**: `/usr/bin/code` (via AUR `visual-studio-code-bin`)
* **Google Cloud CLI**: `/usr/bin/gcloud` (via AUR `google-cloud-cli`)
* **Claude Code**: `/usr/bin/claude` (via AUR `claude-code`)
* **Antigravity CLI**: `/usr/bin/agy` (via AUR `antigravity-cli` or `~/.local/bin/agy`)
* **OpenAI Codex**: `/usr/bin/codex` (via official `extra/openai-codex`)
* **GitHub CLI**: `/usr/bin/gh` (via official `extra/github-cli`)

---

## 3. Native Google Cloud SDK Authentication (No Containers)

Because `google-cloud-cli` is installed natively from the AUR, Docker and container compose files are entirely avoided. Authentication runs directly against host user files in `~/.config/gcloud/`, integrating cleanly with KDE Plasma 6 default web browsers.

### Step 3.1: Initialize Google Cloud CLI Configuration

Set your active Google Cloud project and target region:

```bash
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud config set compute/region global
```

### Step 3.2: Generate Application Default Credentials (ADC)

Generate the host ADC credential file:

```bash
gcloud auth application-default login --project="YOUR_GCP_PROJECT_ID"
```

1. The command automatically opens your default KDE Plasma browser (e.g., Firefox, Chromium, Brave).
2. Authenticate using your Google Cloud account associated with Vertex AI / Agent Platform permissions.
3. Upon granting consent, `gcloud` automatically writes the credential payload directly to your local user directory:

```bash
ls -l ~/.config/gcloud/application_default_credentials.json
```

4. Confirm that the token is active by printing an access token:

```bash
gcloud auth application-default print-access-token
```

If a valid OAuth token string prints to stdout, native host ADC authentication is completely configured.

---

## 4. Isolated Multi-Account State Layout

Independent directories maintain identity boundaries across tools on your Arch Linux filesystem:

```
/home/$USER/
├── .config/
│   ├── gcloud/                      ← Native ADC tokens (Gemini 4 Carbon & Fable 5.2)
│   └── code-flags.conf              ← VS Code Wayland & KWallet 6 flags
├── .gemini/
│   ├── config/
│   │   ├── config.json              ← Antigravity core settings ("enableAdc": false)
│   │   └── mcp_config.json          ← Antigravity & agy unified MCP server definitions
│   └── antigravity-cli/             ← agy CLI session state
├── .claude/                         ← Anthropic Teams interactive session state
├── .claude-gcp/                     ← Claude Fable 5.2 Vertex AI isolated state
├── .codex/                          ← OpenAI ChatGPT Plus OAuth session state
└── .codex-api/                      ← OpenAI Pay-As-You-Go API session state
```

### Step 4.1: Ensure Clean Default Antigravity Settings

Antigravity must default to your **Google AI Pro** personal subscription without routing into GCP project billing:

```bash
mkdir -p ~/.gemini/config

cat << 'EOF' > ~/.gemini/config/config.json
{
  "userSettings": {
    "enableAdc": false
  }
}
EOF
```

### Step 4.2: Initial Login for Each Identity

Authenticate each provider in its respective isolated storage directory:

```bash
# 1. Google AI Pro OAuth login in Antigravity CLI
agy login

# 2. Anthropic Teams OAuth login in Claude Code
claude login

# 3. OpenAI ChatGPT Plus login in ~/.codex (using /usr/bin/codex)
/usr/bin/codex login

# 4. OpenAI API Key login in ~/.codex-api (using /usr/bin/codex)
mkdir -p ~/.codex-api
CODEX_HOME="$HOME/.codex-api" /usr/bin/codex login --api-key "sk-proj-YOUR_OPENAI_API_KEY"

# 5. GitHub Copilot CLI authorization
gh auth login --web -s copilot
```

---

## 5. The Native Python MCP Bridge for Google Cloud Agent Platform

Because the Antigravity CLI communicates via the Agent Client Protocol (ACP) rather than standard-IO MCP server mode, this self-contained Python 3 bridge exposes `ask_gemini_carbon` as a standard MCP tool. It validates the host ADC token directly via native `gcloud` without container overhead, safely handles MCP protocol handshakes, and suppresses protocol notification warnings.

### Step 5.1: Install `agy-mcp-bridge`

```bash
mkdir -p ~/.local/bin

cat << 'EOF' > ~/.local/bin/agy-mcp-bridge
#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys

# Locate native binaries
AGY_BIN = shutil.which("agy") or os.path.expanduser("~/.local/bin/agy") or "/usr/bin/agy"
GCLOUD_BIN = shutil.which("gcloud") or "/usr/bin/gcloud"

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def check_adc():
    """Verify host ADC token validity natively without containers."""
    if not os.path.exists(os.path.expanduser("~/.config/gcloud/application_default_credentials.json")):
        return False
    res = subprocess.run(
        [GCLOUD_BIN, "auth", "application-default", "print-access-token"],
        capture_output=True, text=True
    )
    return res.returncode == 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        continue
    
    # Ignore protocol notifications lacking request IDs (e.g. notifications/initialized)
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
                "serverInfo": {"name": "agy-gcp-bridge", "version": "2.0.0"}
            }
        })
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [{
                    "name": "ask_gemini_carbon",
                    "description": "Query Gemini 4 Carbon or Claude Opus 5.5 on Google Cloud Agent Platform via Antigravity CLI in native ADC mode.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Prompt or instruction for model"},
                            "model": {"type": "string", "default": "gemini-4-carbon"}
                        },
                        "required": ["prompt"]
                    }
                }]
            }
        })
    elif method == "tools/call":
        if not check_adc():
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": "Native Google Cloud ADC token missing or expired. Run 'gcp-auth-refresh' in your terminal."}],
                    "isError": True
                }
            })
            continue

        args = req.get("params", {}).get("arguments", {})
        prompt = args.get("prompt", "")
        model = args.get("model", "gemini-4-carbon")

        env = os.environ.copy()
        env["AGY_ADC_AUTH"] = "true"
        env["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

        proc = subprocess.run(
            [AGY_BIN, "-m", model, "-p", prompt],
            env=env, capture_output=True, text=True
        )
        output = proc.stdout if proc.returncode == 0 else f"Execution Error ({proc.returncode}): {proc.stderr}"
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": output}],
                "isError": proc.returncode != 0
            }
        })
EOF

chmod +x ~/.local/bin/agy-mcp-bridge
```

---

## 6. MCP Server Configurations Across All Extensions (Zero Containers)

Configure the shared MCP endpoints so Antigravity, Claude Code, and Codex can cross-call any provider backend on demand. All servers, including the GitHub server, run natively via host runtimes.

### Step 6.1: Antigravity Extension & CLI Configuration (`~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "gemini-carbon-gcp": {
      "command": "/home/YOUR_USERNAME/.local/bin/agy-mcp-bridge",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_GCP_PROJECT_ID",
        "GOOGLE_CLOUD_LOCATION": "global"
      }
    },
    "claude-fable-gcp": {
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {
        "CLAUDE_CONFIG_DIR": "/home/YOUR_USERNAME/.claude-gcp",
        "CLAUDE_CODE_USE_VERTEX": "1",
        "CLOUD_ML_REGION": "global",
        "ANTHROPIC_VERTEX_PROJECT_ID": "YOUR_GCP_PROJECT_ID",
        "ANTHROPIC_MODEL": "claude-fable-5-2"
      }
    },
    "claude-teams": {
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {
        "CLAUDE_CONFIG_DIR": "/home/YOUR_USERNAME/.claude"
      }
    },
    "openai-codex-plus": {
      "command": "/usr/bin/codex",
      "args": ["mcp-server"],
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex"
      }
    },
    "openai-codex-api": {
      "command": "/usr/bin/codex",
      "args": ["mcp-server"],
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex-api"
      }
    },
    "github-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
      }
    }
  }
}
```

*Note: Replace `/home/YOUR_USERNAME` with your actual `$HOME` path and `YOUR_GCP_PROJECT_ID` with your project name. If system paths are required, `claude` and `codex` resolve to `/usr/bin/claude` and `/usr/bin/codex`.*

### Step 6.2: Claude Code Global Configuration (`~/.claude.json`)

Register the native MCP servers into Claude Code:

```bash
# Register Google Cloud Gemini 4 Carbon
claude mcp add --scope user gemini-carbon-gcp \
  -e GOOGLE_CLOUD_PROJECT="YOUR_GCP_PROJECT_ID" \
  -e GOOGLE_CLOUD_LOCATION="global" \
  -- "$HOME/.local/bin/agy-mcp-bridge"

# Register Google Cloud Model Garden Claude Fable 5.2
claude mcp add --scope user claude-fable-gcp \
  -e CLAUDE_CONFIG_DIR="$HOME/.claude-gcp" \
  -e CLAUDE_CODE_USE_VERTEX=1 \
  -e CLOUD_ML_REGION=global \
  -e ANTHROPIC_VERTEX_PROJECT_ID="YOUR_GCP_PROJECT_ID" \
  -e ANTHROPIC_MODEL="claude-fable-5-2" \
  -- claude mcp serve

# Register OpenAI Codex (ChatGPT Plus) via /usr/bin/codex
claude mcp add --scope user openai-codex-plus \
  -e CODEX_HOME="$HOME/.codex" \
  -- /usr/bin/codex mcp-server

# Register OpenAI Codex (API Key) via /usr/bin/codex
claude mcp add --scope user openai-codex-api \
  -e CODEX_HOME="$HOME/.codex-api" \
  -- /usr/bin/codex mcp-server

# Register Native GitHub MCP Server via npx
claude mcp add --scope user github-mcp \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_PAT" \
  -- npx -y @modelcontextprotocol/server-github
```

### Step 6.3: OpenAI Codex Global Configuration (`~/.codex/config.toml` & `~/.codex-api/config.toml`)

```toml
[mcp_servers.gemini-carbon-gcp]
command = "/home/YOUR_USERNAME/.local/bin/agy-mcp-bridge"
[mcp_servers.gemini-carbon-gcp.env]
GOOGLE_CLOUD_PROJECT = "YOUR_GCP_PROJECT_ID"
GOOGLE_CLOUD_LOCATION = "global"

[mcp_servers.claude-fable-gcp]
command = "claude"
args = ["mcp", "serve"]
[mcp_servers.claude-fable-gcp.env]
CLAUDE_CONFIG_DIR = "/home/YOUR_USERNAME/.claude-gcp"
CLAUDE_CODE_USE_VERTEX = "1"
CLOUD_ML_REGION = "global"
ANTHROPIC_VERTEX_PROJECT_ID = "YOUR_GCP_PROJECT_ID"
ANTHROPIC_MODEL = "claude-fable-5-2"

[mcp_servers.claude-teams]
command = "claude"
args = ["mcp", "serve"]
[mcp_servers.claude-teams.env]
CLAUDE_CONFIG_DIR = "/home/YOUR_USERNAME/.claude"

[mcp_servers.github-mcp]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
[mcp_servers.github-mcp.env]
GITHUB_PERSONAL_ACCESS_TOKEN = "YOUR_GITHUB_PAT"
```

Sync configuration to the API directory:

```bash
mkdir -p ~/.codex-api
cp ~/.codex/config.toml ~/.codex-api/config.toml
```

---

## 7. GitHub Copilot Integration and Shared Workspace MCP

GitHub Copilot operates in VS Code via the official `GitHub.copilot` and `GitHub.copilot-chat` extensions. Students can activate free Copilot Pro via the GitHub Student Developer Pack.

### Step 7.1: Configure VS Code Copilot MCP Client (`~/.config/Code/User/globalStorage/github.copilot-chat/mcp.json` or `.vscode/mcp.json`)

Configure user-level MCP servers for Copilot Chat:

```json
{
  "mcpServers": {
    "gemini-carbon-gcp": {
      "command": "/home/YOUR_USERNAME/.local/bin/agy-mcp-bridge",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_GCP_PROJECT_ID",
        "GOOGLE_CLOUD_LOCATION": "global"
      }
    },
    "claude-fable-gcp": {
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {
        "CLAUDE_CONFIG_DIR": "/home/YOUR_USERNAME/.claude-gcp",
        "CLAUDE_CODE_USE_VERTEX": "1",
        "CLOUD_ML_REGION": "global",
        "ANTHROPIC_VERTEX_PROJECT_ID": "YOUR_GCP_PROJECT_ID",
        "ANTHROPIC_MODEL": "claude-fable-5-2"
      }
    },
    "claude-teams": {
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {
        "CLAUDE_CONFIG_DIR": "/home/YOUR_USERNAME/.claude"
      }
    },
    "openai-codex": {
      "command": "/usr/bin/codex",
      "args": ["mcp-server"],
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex"
      }
    }
  }
}
```

This configuration enables prompting Copilot Chat to delegate complex architecture or verification tasks to your Google Cloud or Anthropic subagents:

> *"@copilot Ask gemini-carbon-gcp to analyze this memory-safety profile, then have claude-fable-gcp suggest zero-cost abstractions."*

---

## 8. Arch Linux KDE Plasma 6 (Wayland) and Systemd Configuration

Arch Linux ships KDE Plasma 6 on Wayland as default. Configure Wayland parameters and ensure clean environment variable loading.

### Step 8.1: Wayland and KWallet Flags (`~/.config/code-flags.conf`)

Create or update `~/.config/code-flags.conf`:

```ini
--ozone-platform-hint=auto
--enable-wayland-ime
--password-store=kwallet6
```

### Step 8.2: Environment Hygiene Check

Ensure no AI variables are exported globally in `~/.config/environment.d/` or `/etc/environment`. Global exports override extension settings and cause authentication failures:

```bash
# Verify clean environment generators
rm -f ~/.config/environment.d/*ai*.conf
systemctl --user daemon-reload
```

---

## 9. Unified Shell Functions, Aliases, and Dynamic Model Switchers

Add this suite to `~/.bashrc` (or `~/.zshrc`) to manage tokens, providers, and models natively:

```bash
# ==============================================================================
# Multi-Agent Development Suite: Arch Linux (Native Edition)
# ==============================================================================

export GCP_AGENT_PROJECT="YOUR_GCP_PROJECT_ID"
export GCP_AGENT_REGION="global"

# Binary Discovery
_CLAUDE_BIN=$(which claude 2>/dev/null || echo "$HOME/.local/bin/claude")
_AGY_BIN=$(which agy 2>/dev/null || echo "$HOME/.local/bin/agy")
_CODEX_BIN="/usr/bin/codex"
_GCLOUD_BIN=$(which gcloud 2>/dev/null || echo "/usr/bin/gcloud")

# 1. Native Google Cloud ADC Check & Refresh
gcp-auth-refresh() {
  local project_id="${GCP_AGENT_PROJECT:-YOUR_GCP_PROJECT_ID}"
  mkdir -p "$HOME/.config/gcloud"

  if "$_GCLOUD_BIN" auth application-default print-access-token >/dev/null 2>&1; then
    return 0
  fi

  echo "[!] Google Cloud ADC token expired or missing. Launching native gcloud login..."
  "$_GCLOUD_BIN" auth application-default login --project="$project_id"
}

# 2. Antigravity CLI via Google AI Pro Subscription (Consumer OAuth)
# Flags: -f (Flash), -p (Pro), -s (Claude Sonnet), -o (Claude Opus)
agy-pro() {
  local args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -f|--flash)  args+=(-m "gemini-3.8-flash"); shift ;;
      -p|--pro)    args+=(-m "gemini-3.1-pro"); shift ;;
      -s|--sonnet) args+=(-m "claude-sonnet-5-5"); shift ;;
      -o|--opus)   args+=(-m "claude-opus-5-5"); shift ;;
      -m|--model)  args+=(-m "$2"); shift 2 ;;
      *)           break ;;
    esac
  done
  AGY_ADC_AUTH=false "$_AGY_BIN" "${args[@]}" "$@"
}

# 3. Antigravity CLI via Google Cloud Agent Platform (Gemini 4 Carbon / ADC)
# Flags: -g (Gemini 4 Carbon), -o (Claude Opus 5.5), -s (Claude Sonnet 5.5)
agy-gcp() {
  local model="gemini-4-carbon"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -g|--gemini) model="gemini-4-carbon"; shift ;;
      -o|--opus)   model="claude-opus-5-5"; shift ;;
      -s|--sonnet) model="claude-sonnet-5-5"; shift ;;
      -m|--model)  model="$2"; shift 2 ;;
      *)           break ;;
    esac
  done

  gcp-auth-refresh || return 1
  AGY_ADC_AUTH=true \
  GOOGLE_GENAI_USE_VERTEXAI=True \
  GOOGLE_CLOUD_PROJECT="$GCP_AGENT_PROJECT" \
  GOOGLE_CLOUD_LOCATION="$GCP_AGENT_REGION" \
  "$_AGY_BIN" -m "$model" "$@"
}
alias agy-carbon='agy-gcp -g'

# 4. Claude Code CLI via Google Cloud Model Garden (Fable 5.2 / ADC)
# Flags: -f (Fable 5.2), -o (Opus 5.5), -s (Sonnet 5.5)
claude-gcp() {
  local model="claude-fable-5-2"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -f|--fable)  model="claude-fable-5-2"; shift ;;
      -o|--opus)   model="claude-opus-5-5"; shift ;;
      -s|--sonnet) model="claude-sonnet-5-5"; shift ;;
      -m|--model)  model="$2"; shift 2 ;;
      *)           break ;;
    esac
  done

  gcp-auth-refresh || return 1
  CLAUDE_CONFIG_DIR="$HOME/.claude-gcp" \
  CLAUDE_CODE_USE_VERTEX=1 \
  CLOUD_ML_REGION="$GCP_AGENT_REGION" \
  ANTHROPIC_VERTEX_PROJECT_ID="$GCP_AGENT_PROJECT" \
  ANTHROPIC_MODEL="$model" \
  ANTHROPIC_SMALL_FAST_MODEL="claude-sonnet-5-5" \
  "$_CLAUDE_BIN" "$@"
}
alias claude-fable='claude-gcp -f'

# 5. Claude Code CLI via Anthropic Teams (Standard OAuth)
# Flags: -o (Opus), -s (Sonnet), -h (Haiku)
claude-teams() {
  local model_args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -o|--opus)   model_args=(--model opus); shift ;;
      -s|--sonnet) model_args=(--model sonnet); shift ;;
      -h|--haiku)  model_args=(--model haiku); shift ;;
      *)           break ;;
    esac
  done
  CLAUDE_CONFIG_DIR="$HOME/.claude" "$_CLAUDE_BIN" "${model_args[@]}" "$@"
}

# 6. Shared Flag Parser for OpenAI Codex CLI
_codex_run() {
  local codex_home="$1"; shift
  local args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -c|--codex)  args+=(-m "gpt-5.3-codex"); shift ;;
      -g|--gpt)    args+=(-m "gpt-6.1"); shift ;;
      --mini)      args+=(-m "gpt-5.3-codex-mini"); shift ;;
      -H|--high)   args+=(-c 'model_reasoning_effort="high"'); shift ;;
      -X|--xhigh)  args+=(-c 'model_reasoning_effort="xhigh"'); shift ;;
      -m|--model)  args+=(-m "$2"); shift 2 ;;
      *)           break ;;
    esac
  done
  CODEX_HOME="$codex_home" "$_CODEX_BIN" "${args[@]}" "$@"
}

# 7. OpenAI Codex CLI Profiles
codex-plus() { _codex_run "$HOME/.codex" "$@"; }
codex-api()  { _codex_run "$HOME/.codex-api" "$@"; }
```

Reload shell configuration:

```bash
source ~/.bashrc
```

---

## 10. End-to-End Verification and Diagnostics

### Step 10.1: Test `agy-mcp-bridge` Protocol Handshake

Send initialization and tool listing requests:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' \
  | ~/.local/bin/agy-mcp-bridge
```

Confirm that the bridge outputs valid JSON-RPC responses containing `"protocolVersion": "2024-11-05"` and the `ask_gemini_carbon` tool schema without executing Docker.

### Step 10.2: Verify Registered Servers in Claude Code

Run the server health check:

```bash
claude mcp list
```

Verify that all configured servers (`gemini-carbon-gcp`, `claude-fable-gcp`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`) display `Connected`.

### Step 10.3: Inspect Live Indicators in VS Code

1. Launch VS Code from KRunner or your application menu.
2. Open Antigravity (Activity Bar or `Ctrl+L`) and execute `/mcp`. Confirm all servers show green status rings.
3. Open Claude Code (`Ctrl+Shift+P` -> `Claude Code: Open in Side Bar`) and execute `/mcp` in the prompt box. Verify all servers report active.
4. Open GitHub Copilot Chat (`Ctrl+Alt+I`) and verify tool availability.

---

## 11. Lifecycle Maintenance Playbook: Retiring ChatGPT Plus

When your €23/month ChatGPT Plus billing cycle concludes:

1. **Remove Plus from Antigravity**: Delete the `"openai-codex-plus"` block from `~/.gemini/config/mcp_config.json`.
2. **Remove Plus from Claude Code**:
   ```bash
   claude mcp remove --scope user openai-codex-plus
   ```
3. **Clean Configuration Files**:
   ```bash
   rm -rf ~/.codex
   ```
4. **Retain On-Demand API**: Keep `"openai-codex-api"` active across all configs. It incurs zero cost when idle and meters tokens only when an agent is explicitly instructed to execute an OpenAI call.
