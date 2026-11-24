### Complete MCP Integration Guide for VS Code on Arch Linux: Antigravity, Claude Code, OpenAI Codex, GitHub Copilot, Continue, and GitLab Multi-Instance Mesh (Native Public Edition v10)

An enterprise-grade reference architecture for orchestrating multi-provider AI agents, Model Context Protocol (MCP) servers, and isolated developer identities under Arch Linux (rolling release, systemd, KDE Plasma 6 on Wayland) using  **100% native host binaries**  without container overhead.

--------------------------------------------------------------------------------

#### 1. System Architecture and Identity Isolation Matrix

On Arch Linux, rolling updates and cutting-edge upstream packages in the Arch User Repository (AUR) provide native access to official AI developer tooling. With google-cloud-cli available natively via the AUR, container runtimes (such as Docker or Podman) are completely unnecessary for Google Cloud SDK authentication, token verification, and Application Default Credentials (ADC) lifecycle management.
This architecture establishes strict credential boundaries across four AI providers and seven operational models and subscriptions:
1.  **Google AI Pro (Consumer Subscription)** : Flat-rate consumer subscription driving daily interactive development in the Google Antigravity VS Code extension and the Antigravity CLI (agy-pro).
2.  **Google Cloud Agent Platform (Enterprise ADC)** : Pay-as-you-go Vertex AI infrastructure providing on-demand execution for  **Gemini 4 Carbon**  and  **Claude Opus 5.5** , accessed via native Arch google-cloud-cli ADC authentication and a zero-dependency local MCP bridge.
3.  **Anthropic Teams (Organization OAuth)** : Standard corporate team subscription driving the official Claude Code VS Code extension and terminal workflow (claude-teams).
4.  **Claude Fable 5.2 on Google Cloud Model Garden** : Enterprise Claude execution hosted on Google infrastructure, isolated through a dedicated configuration directory (~/.claude-gcp) and invoked as an MCP subagent.
5.  **OpenAI ChatGPT Plus (€23/mo Consumer OAuth)** : Flat-rate consumer access driving the OpenAI Codex CLI and VS Code extension (openai-codex-plus), isolated within ~/.codex.
6.  **OpenAI API (Pay-As-You-Go)** : On-demand per-token API billing used when Plus rate limits are exhausted or for automated background tasks, isolated within ~/.codex-api.
7.  **GitHub Copilot (Student / Individual / Enterprise)** : GitHub's code intelligence engine operating alongside local MCP servers, paired with a native Node-based GitHub MCP server to provide workspace awareness and repository telemetry across all agents.
8.  **GitLab Multi-Instance Mesh (SaaS, Enterprise & Institutional Infrastructure)** : Seamless multi-instance GitLab integration connecting agents to five distinct developer and administrative platforms: **GitLab.com** (SaaS, 19.5+), **gitlab.lip.pt** (LIP production, 19.5.3), **gitlab-admin.lip.pt** (LIP admin, 19.5.3), **gitlab.legacy.example.org** (Legacy, 18.2.8), and **gitlab-admin.legacy.example.org** (Admin legacy, 16.x latest). Modern instances communicate via native remote MCP (`mcp-remote`) with URL-isolated OAuth caching, while legacy instances communicate via local stdio `@zereight/mcp-gitlab` servers with dedicated `.env` credential files. Unique tool-name prefixes (`glcom_`, `gllip_`, `gladminlip_`, `gllegacy_`, `gladminleg_`) prevent tool namespace collisions across repositories.

##### Complete Provider and Billing Matrix

| Provider / Subscription | Primary Host Client | Auth Mechanism | Configuration Directory | MCP Server Identifier | Financial Impact / Metering |
| ------ | ------ | ------ | ------ | ------ | ------ |
| **Google AI Pro** | Antigravity IDE / agy-pro | Browser OAuth (Google SSO) | ~/.gemini/ | Native Host Agent | Flat monthly subscription (€0 additional) |
| **Google Cloud Agent Platform** | agy-mcp-bridge / agy-gcp | ADC Token via Native gcloud | ~/.config/gcloud/ | gemini-carbon-gcp | Pay-as-you-go per token on GCP project |
| **Anthropic Teams** | Claude Code IDE / claude-teams | Browser OAuth (Anthropic SSO) | ~/.claude/ | claude-teams | Flat team seat license |
| **Google Cloud Model Garden (Fable 5.2)** | Claude Code CLI / MCP | Vertex AI ADC Token | ~/.claude-gcp/ | claude-fable-gcp | Pay-as-you-go per token on GCP project |
| **OpenAI ChatGPT Plus** | Codex IDE / codex-plus | Terminal OAuth (ChatGPT Web) | ~/.codex/ | openai-codex-plus | Flat €23/month (subject to cancellation) |
| **OpenAI API** | Codex IDE / codex-api | Secret API Key (sk-proj-...) | ~/.codex-api/ | openai-codex-api | Pay-as-you-go per token balance |
| **GitHub Copilot** | Copilot Chat VS Code | GitHub OAuth Token | ~/.config/github-copilot/ | github-mcp | Included via Student Pack / Monthly seat |
| **GitHub Copilot Models** | Antigravity / Claude / Continue | Copilot CLI Runtime (`copilot --acp`) | ~/.config/antigravity-mcp/ | github-models | Included via Copilot Subscription (`auto` default discount) |
| **GitLab.com** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth) | `~/.mcp-auth/` | `gitlab-com` | Included via SaaS Free/Premium (`glcom_` prefix) |
| **GitLab LIP (19.5.3)** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth/PAT) | `~/.mcp-auth/` | `gitlab-lip` | Institutional production instance (`gllip_` prefix) |
| **GitLab Admin LIP (19.5.3)** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth/PAT) | `~/.mcp-auth/` | `gitlab-admin-lip` | Institutional admin instance (`gladminlip_` prefix) |
| **GitLab Legacy (18.2.8)** | Antigravity / Claude / Codex / Copilot / Continue | Stdio MCP (`@zereight/mcp-gitlab`) + PAT | `~/.config/antigravity-mcp/` | `gitlab-legacy` | Self-hosted legacy instance (`gllegacy_` prefix) |
| **GitLab Admin Legacy (16 latest)** | Antigravity / Claude / Codex / Copilot / Continue | Stdio MCP (`@zereight/mcp-gitlab`) + PAT | `~/.config/antigravity-mcp/` | `gitlab-admin-legacy` | Self-hosted legacy admin instance (`gladminleg_` prefix) |


--------------------------------------------------------------------------------

#### 2. Arch Linux Host Prerequisites and Package Management

Arch Linux relies on pacman for official core packages and the Arch User Repository (AUR) for third-party developer tools and AI agents. By utilizing AUR packages, the entire stack runs natively on the bare metal, removing container layers, volume permission mapping, and virtualization latency.

##### Step 2.1: Install Core System Dependencies and OpenAI Codex via pacman

Arch Linux provides the official  **OpenAI Codex CLI**  package directly in the  **[extra]**  repository as  **openai-codex** , which installs the native /usr/bin/codex executable directly into your system PATH. Install it alongside standard build tools, desktop secret storage, and Node.js runtimes:
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
Verify that codex is immediately available from /usr/bin/:
```bash
which codex
# Output: /usr/bin/codex

pacman -Q openai-codex
# Output: openai-codex <version>

```
*Note: Ensure kwallet-pam is active in your PAM configuration (/etc/pam.d/sddm or /etc/pam.d/login) so your KWallet 6 keyring unlocks automatically at graphical login.*

##### Step 2.2: Install VS Code and Native AI Agents via AUR (yay / paru)

Using an AUR helper like yay or paru, install the official VS Code binary, the native Google Cloud CLI, Claude Code, and the official Google Antigravity CLI package (aur/antigravity-cli):
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
*   **aur/antigravity-cli** : Installs the genuine Google Antigravity command-line binary (/usr/bin/agy). Do  **not**  install aur/python-google-antigravity, which is an unrelated Python client SDK and does not provide the agy command-line executable.
*   **google-cloud-cli** : If you prefer precompiled binary archives rather than building from source, yay -S --needed google-cloud-cli-bin can be used.

##### Step 2.3: Alternative Installation Methods for Google Antigravity CLI (agy)

If aur/antigravity-cli is ever undergoing upstream maintenance, you can obtain the exact same binary through either of these direct fallbacks:

###### Method A: Official Standalone Installer

Install Google's official static binary directly into user space (~/.local/bin/agy):
```bash
mkdir -p ~/.local/bin
curl -fsSL https://antigravity.google/cli/install.sh | bash

```
Ensure ~/.local/bin is in your shell PATH in ~/.bashrc:
```bash
export PATH="$HOME/.local/bin:$PATH"

```

###### Method B: Symlink from the VS Code Extension

If you already use the official  **Google Antigravity**  extension in VS Code (Google.google-antigravity), it automatically bundles the compiled agy service engine under ~/.antigravity/bin/agy (or ~/.gemini/antigravity/bin/agy). You can symlink it into your path:
```bash
mkdir -p ~/.local/bin
ln -sf ~/.antigravity/bin/agy ~/.local/bin/agy

```

###### Optional: Standalone User-Space Fallbacks

If any package is undergoing upstream maintenance:
```bash
# Anthropic Claude Code CLI via user-space Node runtime
npm install -g @anthropic-ai/claude-code --prefix ~/.local

# OpenAI Codex CLI via user-space Node runtime (fallback if extra/openai-codex is unavailable)
npm install -g @openai/codex --prefix ~/.local

```
Verify binary paths using which code gcloud claude agy codex gh. All tools resolve cleanly to native system paths:
*   **VS Code** : /usr/bin/code (via AUR visual-studio-code-bin)
*   **Google Cloud CLI** : /usr/bin/gcloud (via AUR google-cloud-cli)
*   **Claude Code** : /usr/bin/claude (via AUR claude-code)
*   **Antigravity CLI** : /usr/bin/agy (via AUR antigravity-cli or ~/.local/bin/agy)
*   **OpenAI Codex** : /usr/bin/codex (via official extra/openai-codex)
*   **GitHub CLI** : /usr/bin/gh (via official extra/github-cli)

--------------------------------------------------------------------------------

#### 3. Native Google Cloud SDK Authentication (No Containers)

Because google-cloud-cli is installed natively from the AUR, Docker and container compose files are entirely avoided. Authentication runs directly against host user files in ~/.config/gcloud/, integrating cleanly with KDE Plasma 6 default web browsers.

##### Step 3.1: Initialize Google Cloud CLI Configuration

Set your active Google Cloud project and target region:
```bash
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud config set compute/region global

```

##### Step 3.2: Generate Application Default Credentials (ADC)

Generate the host ADC credential file:
```bash
gcloud auth application-default login --project="YOUR_GCP_PROJECT_ID"

```
1. The command automatically opens your default KDE Plasma browser (e.g., Firefox, Chromium, Brave).
2. Authenticate using your Google Cloud account associated with Vertex AI / Agent Platform permissions.
3. Upon granting consent, gcloud automatically writes the credential payload directly to your local user directory:
```bash
ls -l ~/.config/gcloud/application_default_credentials.json

```
4. Confirm that the token is active by printing an access token:
```bash
gcloud auth application-default print-access-token

```
If a valid OAuth token string prints to stdout, native host ADC authentication is completely configured.

--------------------------------------------------------------------------------

#### 4. Isolated Multi-Account State Layout

Independent directories maintain identity boundaries across tools on your Arch Linux filesystem:
```
/home/$USER/
├── .config/
│   ├── antigravity-mcp/             ← Dedicated .env files for legacy/PAT GitLab instances (0700)
│   │   ├── gitlab-legacy.env         ← PAT, URL & tool prefix for gitlab.legacy.example.org (18.2.8)
│   │   └── gitlab-admin-legacy.env          ← PAT, URL & tool prefix for gitlab-admin.legacy.example.org (16 latest)
│   ├── gcloud/                      ← Native ADC tokens (Gemini 4 Carbon & Fable 5.2)
│   └── code-flags.conf              ← VS Code Wayland & KWallet 6 flags
├── .mcp-auth/                       ← mcp-remote automatic OAuth token cache (gitlab.com, lip.pt)
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

##### Step 4.1: Ensure Clean Default Antigravity Settings

Antigravity must default to your  **Google AI Pro**  personal subscription without routing into GCP project billing:
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

##### Step 4.2: Initial Login for Each Identity

Authenticate each provider in its respective isolated storage directory:
```bash
# 1. Google AI Pro OAuth login in Antigravity CLI
agy

# 2. Anthropic Teams OAuth login in Claude Code
claude login

# 3. OpenAI ChatGPT Plus login in ~/.codex (using /usr/bin/codex)
codex login

# 4. OpenAI API Key login in ~/.codex-api (using /usr/bin/codex)
mkdir -p ~/.codex-api
printenv "sk-proj-YOUR_OPENAI_API_KEY" | CODEX_HOME="$HOME/.codex-api" /usr/bin/codex login

# 5. GitHub Copilot CLI authorization
gh auth login --web -s copilot

# 6. Initialize Isolated Credential Directory for Legacy GitLab Instances (PAT)
mkdir -p ~/.config/antigravity-mcp ~/.mcp-auth
chmod 700 ~/.config/antigravity-mcp ~/.mcp-auth

# Configure gitlab.legacy.example.org (v18.2.8)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-legacy.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_LEGACY_TOKEN
GITLAB_API_URL=https://gitlab.legacy.example.org
GITLAB_TOOL_PREFIX=gllegacy_
GITLAB_TOOLSETS=issues,merge_requests,repositories,pipelines,wiki
# Optional: Enforce strict read-only mode if write operations should be blocked:
# GITLAB_PERMISSION_MODE=readonly
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-legacy.env

# Configure gitlab-admin.legacy.example.org (v16 latest)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-admin-legacy.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_ADMIN_LEGACY_TOKEN
GITLAB_API_URL=https://gitlab-admin.legacy.example.org
GITLAB_TOOL_PREFIX=gladminleg_
GITLAB_TOOLSETS=issues,merge_requests,repositories,pipelines,wiki
# Optional: Enforce strict read-only mode if write operations should be blocked:
# GITLAB_PERMISSION_MODE=readonly
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-admin-legacy.env

```

--------------------------------------------------------------------------------

#### 5. Native Python MCP Bridges: Antigravity and OpenAI Codex

Both the **Google Antigravity CLI (`agy`)** and the **OpenAI Codex CLI (`codex`)** communicate natively via interactive protocols (Agent Client Protocol for Antigravity, and terminal TUI/prompt forwarding for Codex) rather than standard-IO Model Context Protocol server loops.

* **Antigravity CLI**: Operates via ACP. The `agy-mcp-bridge` wraps `agy -m ... -p ...` and validates native Google Cloud ADC credentials.
* **OpenAI Codex CLI**: In the Codex CLI, the `codex mcp` subcommand is an *MCP client manager* (for adding external MCP servers to Codex), not an MCP server itself. Passing `codex mcp-server` causes Codex to treat `"mcp-server"` as a user prompt instruction, execute it, and exit immediately—closing standard IO and triggering `MCP error -32000: Connection closed` in VS Code extensions (Continue, Claude Code, Copilot). Bare `/usr/bin/codex` launches the interactive full-screen TUI. To expose Codex cleanly as a persistent subagent tool, `codex-mcp-bridge` wraps `codex exec -m <model> <prompt>` over standard-IO JSON-RPC.

##### Step 5.1: Install `agy-mcp-bridge`

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

##### Step 5.2: Install `codex-mcp-bridge`

Create the zero-dependency Python bridge that executes non-interactive `codex exec` calls over JSON-RPC stdio:

```bash
mkdir -p ~/.local/bin

cat << 'EOF' > ~/.local/bin/codex-mcp-bridge
#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys

# Locate native codex binary from extra/openai-codex
CODEX_BIN = shutil.which("codex") or "/usr/bin/codex"
HOME = os.path.expanduser("~")

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        continue

    # Ignore notifications lacking an ID (e.g. notifications/initialized)
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
                "serverInfo": {"name": "codex-mcp-bridge", "version": "1.0.0"}
            }
        })
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [{
                    "name": "ask_codex",
                    "description": "Execute an instruction or code query non-interactively using OpenAI Codex CLI.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The coding task, prompt, or question for Codex"
                            },
                            "model": {
                                "type": "string",
                                "default": "gpt-5.3-codex",
                                "description": "Target OpenAI model (e.g. gpt-5.3-codex, gpt-6.1, gpt-5.3-codex-mini)"
                            }
                        },
                        "required": ["prompt"]
                    }
                }]
            }
        })
    elif method == "tools/call":
        args = req.get("params", {}).get("arguments", {})
        prompt = args.get("prompt", "")
        model = args.get("model", "gpt-5.3-codex")

        env = os.environ.copy()
        # Default to ~/.codex if not explicitly injected
        if "CODEX_HOME" not in env:
            env["CODEX_HOME"] = os.path.join(HOME, ".codex")

        # Run Codex non-interactively using 'codex exec'
        proc = subprocess.run(
            [CODEX_BIN, "exec", "-m", model, prompt],
            env=env,
            capture_output=True,
            text=True
        )

        output = proc.stdout if proc.returncode == 0 else f"Codex Error ({proc.returncode}): {proc.stderr}"
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": output}],
                "isError": proc.returncode != 0
            }
        })
EOF

chmod +x ~/.local/bin/codex-mcp-bridge
```

##### Step 5.3: Install `github-models-mcp` (GitHub Copilot Models Bridge)

The standard GitHub MCP server (`@modelcontextprotocol/server-github`) integrates exclusively with repository REST/GraphQL APIs (issues, pull requests, commits, and code search) and **cannot perform AI model completions**. Because GitHub retired the standalone, public free tier of GitHub Models (`models.github.ai`) in favor of authenticated **GitHub Copilot subscriptions**, model completions are routed directly through your local Copilot CLI runtime session.

This zero-dependency Python bridge (`~/.local/bin/github-models-mcp`) interacts with the official Copilot CLI via its Agent Client Protocol (`copilot --acp`), dynamically discovers your available models (e.g. `claude-sonnet-5.5`, `grok-4.7`, `mai-code-2`, `mai-code-2-flash`, `openai/gpt-4o`, `kimi-k3`), caches them with a configurable TTL, and defaults to Copilot's cost-discounted `auto` model routing:

```bash
mkdir -p ~/.local/bin ~/.config/antigravity-mcp

cat << 'EOF' > ~/.local/bin/github-models-mcp
#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import time

COPILOT_BIN = (
    os.path.expanduser('~/.local/share/gh/copilot/copilot')
    if os.path.exists(os.path.expanduser('~/.local/share/gh/copilot/copilot'))
    else shutil.which('copilot') or 'copilot'
)
CACHE_DIR = os.path.expanduser('~/.config/antigravity-mcp')
CACHE_FILE = os.path.join(CACHE_DIR, 'models_cache.json')
CACHE_TTL = int(os.environ.get('GITHUB_MODELS_CACHE_TTL', '3600'))

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def get_cached_models(force_refresh=False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            mtime = os.path.getmtime(CACHE_FILE)
            if (time.time() - mtime) < CACHE_TTL:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
        except Exception:
            pass

    # Discover models dynamically via copilot --acp
    try:
        res = subprocess.run([COPILOT_BIN, '--acp'], input='{"method":"models/list"}\n',
                             capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    p = json.loads(line)
                    if 'result' in p and 'models' in p['result']:
                        models = p['result']['models']
                        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                            json.dump(models, f, indent=2)
                        return models
                except Exception:
                    continue
    except Exception:
        pass

    # High-quality fallback models available on Copilot subscriptions
    fallback = [
        {"id": "auto", "name": "Auto (Cost-Discounted Selection)", "description": "Default: Let Copilot automatically select the best model at discounted quota rate."},
        {"id": "claude-sonnet-5.5", "name": "Claude Sonnet 5.5", "description": "Anthropic frontier coding & reasoning engine via Copilot."},
        {"id": "grok-4.7", "name": "xAI Grok 4.7", "description": "xAI reasoning & algorithmic intelligence model via Copilot."},
        {"id": "mai-code-2", "name": "Microsoft AI Code 2", "description": "Microsoft specialized code generation and refactoring engine."},
        {"id": "mai-code-2-flash", "name": "Microsoft AI Code 2 Flash", "description": "Ultra-low-latency code completion engine via Copilot."},
        {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o", "description": "Flagship multimodal developer model via Copilot."},
        {"id": "openai/gpt-4o-mini", "name": "OpenAI GPT-4o-mini", "description": "Fast, lightweight cost-effective coding model."},
        {"id": "kimi-k3", "name": "Moonshot Kimi K3", "description": "Long-context reasoning & document analysis model."}
    ]
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(fallback, f, indent=2)
    except Exception:
        pass
    return fallback

TOOLS = [
    {
        "name": "ask_github_model",
        "description": "Query GitHub Copilot model inference with your active GitHub Copilot personal subscription. Defaults to auto for discounted quota usage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The coding prompt, task, or question for Copilot model inference."
                },
                "model": {
                    "type": "string",
                    "default": "auto",
                    "description": "Target Copilot model ID (e.g. auto, claude-sonnet-5.5, grok-4.7, mai-code-2, mai-code-2-flash, openai/gpt-4o). Defaults to auto."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "list_github_models",
        "description": "List all models available on your active GitHub Copilot subscription, including dynamic cached catalog.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "default": False,
                    "description": "Force refresh the models catalog from Copilot runtime, bypassing local cache."
                }
            }
        }
    }
]

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except Exception:
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
                "serverInfo": {"name": "github-models-mcp", "version": "1.0.0"}
            }
        })
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        })
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "list_github_models":
            force_refresh = args.get("refresh", False)
            models = get_cached_models(force_refresh=force_refresh)
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(models, indent=2)}],
                    "isError": False
                }
            })
        elif tool_name == "ask_github_model":
            prompt = args.get("prompt", "")
            model = args.get("model", "auto")
            if not model or model.strip() == "":
                model = "auto"

            cmd = [COPILOT_BIN, "-p", prompt] if model == "auto" else [COPILOT_BIN, "--model", model, "-p", prompt]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                output = proc.stdout if proc.returncode == 0 else f"Copilot Error ({proc.returncode}): {proc.stderr}"
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": output}],
                        "isError": proc.returncode != 0
                    }
                })
            except Exception as e:
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Bridge Execution Error: {str(e)}"}],
                        "isError": True
                    }
                })
EOF

chmod +x ~/.local/bin/github-models-mcp
```

Verify the bridge protocol handshake directly in your terminal:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' \
  | ~/.local/bin/github-models-mcp
```

Confirm that the output returns `protocolVersion: 2024-11-05` and registers both `ask_github_model` (with default `auto`) and `list_github_models`.


---

#### 6. MCP Server Configurations Across All Extensions (Zero Containers)

Configure the shared MCP endpoints so Antigravity, Claude Code, and Codex can cross-call any provider backend on demand. All servers, including the GitHub server, run natively via host runtimes.

##### Step 6.1: Antigravity Extension & CLI Configuration (~/.gemini/config/mcp_config.json)

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
      "command": "/home/YOUR_USERNAME/.local/bin/codex-mcp-bridge",
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex"
      }
    },
    "openai-codex-api": {
      "command": "/home/YOUR_USERNAME/.local/bin/codex-mcp-bridge",
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex-api"
      }
    },
    "github-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "github-models": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"$HOME/.gemini/.env\" ] && . \"$HOME/.gemini/.env\"; [ -f \"$HOME/.config/antigravity-mcp/github-models.env\" ] && . \"$HOME/.config/antigravity-mcp/github-models.env\"; set +a && exec /home/YOUR_USERNAME/.local/bin/github-models-mcp"
      ]
    },
    "gitlab-com": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-com.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_\""
      ]
    },
    "gitlab-lip": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_\""
      ]
    },
    "gitlab-admin-lip": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_\""
      ]
    },
    "gitlab-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
    },
    "gitlab-admin-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
    }
  }
}

```
*Note: Replace /home/YOUR_USERNAME with your actual $HOME path and YOUR_GCP_PROJECT_ID with your project name. If system paths are required, claude and codex resolve to /usr/bin/claude and /usr/bin/codex.*
Gemini/Antigravity CLI does not support interactive ${input:...} prompts, but it automatically expands $VAR_NAME or ${VAR_NAME} from your shell environment or a .gemini/.env file.
Where to store the token: Add GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PAT to ~/.gemini/.env (or export it in your shell profile) so your config stays secret-free and safe to commit. [[1](https://www.google.com/goto?url=CAESiwEBxCJF1ys4tlgyOZtRY9so0zfbbVFOXFvRAj4OrNWSYKlg3oU4JlA3JMljakZMgQ9lMsLrg7m--paOm8mBJ_VLy6qNfZbr_0zz05xeTKQq8baxjC1dO8K_m9Pzs3EQTmU1Dhyihh05W2plJIo4r2UOaZt_SMr_dQ7nS7L1iXDgEtWZvV7isllfNRme), [2](https://www.google.com/goto?url=CAESaAHEIkXXppRU6EKp8A5LdgzSUfmnLbxMkFmZN3ywkc5Wq1YymCcuOLhjHZK2_z7iiDML8rdh7DUwEF8mLp5FzgC5yC8tVh4mW1lpCpCbTpRc-AHNVsN-fhYtQRoIsqYy-IsceT9PIAPg), [3](https://www.google.com/goto?url=CAESaQHEIkXXvWC9iXzuU3BhN6-povsb7WN_pVC6eT831cQ7bMhdcnuCAZILD3uJc878epyg9rzkyMloezR54hbTE5Mpjkd1R8eKg9VyLdPNJ9U7dIEY2JRwMxGVJpXZOnSVLy4uCYquYOkYnQ), [4](https://www.google.com/goto?url=CAESbQHEIkXX57LoMQVFJPv4qyci0J-wonn6ZMpyG5bkIGWSImhw2GNEdTuMhyEGz8LvdAxYQasoahqQkd92JtQbW62y7rI4ordRwSM74L4DhgSUx2JagxRG2oIEuIUlm5i8rLtBtclKrHAFhZCSP8U)]
Generate a GitHub Personal Access Token (PAT) in your [GitHub Developer Settings](https://www.google.com/goto?url=CAESXwHEIkXXoBL9CLpY3QagjZu7WH2Z64FNPK3hSs14j-t4u2p1QdezF4fHi_jh3J4X6o4dQ7XsZcAONQmRUk6LQdrGeq3egdu8SWHHIb109Vqy_yI_C5KTH8Tb8eN8JXLB) and paste it into your GITHUB_PERSONAL_ACCESS_TOKEN field.
For Copilot agents and @modelcontextprotocol/server-github, a Classic PAT (ghp_...) is recommended because the MCP server uses OAuth scope filtering to automatically enable only the tools your token supports. [[1](https://www.google.com/goto?url=CAESsgEBxCJF14_zK1CNMzSqcpO82oWjD--p0-GioXb4OouUSZNkRftZtsZAfQwSMj3EbGlbNNhNJY5BoDTuBWh_yFwgLwe6e5BnjNQ7Hp_rjLrl5b8d4KSU55tr0Zq9lAyaqhBOP_x4H4Of3cC8E4GZTjzxgj_Qw8Z7cYCWcOoeb5UupVm_rp24iMwRj52cxUKh5N1eVvvoUghA6choKdxuwtt8y4wW-hSoM5RQ-vyfb9fzKnuz), [2](https://www.google.com/goto?url=CAESigEBxCJF1w1-161jkd3mxbT-Mp1vlwvvyeHlObLsT2ZjmHVD_u93j_il-sboFCea4lJ1VMvkISinsk0kPQSyNc_RNIDcVnsQY4CmAJfTKlOW3vBU5vS_EWEb-C3VdvOKVyn3K_d_ttOUsI87qgVRYoh6o1ae5LFLOEz9CZIDf9q5k9ev5r9k66lC27A)]

###### Create the GitHub PAT

1. Open token settings. Sign in to GitHub, click your profile picture (top-right), and go to Settings → Developer settings (bottom of the left sidebar) → Personal access tokens → Tokens (classic). [[1](https://www.google.com/goto?url=CAESegHEIkXXHf1T_p2spekdI16aOR1ZrCeH0GFHBVDZ0aAP1K-0JwHyxAy5FLb9wrF6LmDjCbDvXYr524lDemyJraZ72NO8u8f8z3Q5MmH5cDq5su8y-suWhL-EGrgctnqcQUve2HyjX4o8zvsSlUzh5DwTAhJ_3w9ccL6M)]
2. Generate a new token. Click Generate new token → Generate new token (classic). [[1](https://www.google.com/goto?url=CAESegHEIkXXHf1T_p2spekdI16aOR1ZrCeH0GFHBVDZ0aAP1K-0JwHyxAy5FLb9wrF6LmDjCbDvXYr524lDemyJraZ72NO8u8f8z3Q5MmH5cDq5su8y-suWhL-EGrgctnqcQUve2HyjX4o8zvsSlUzh5DwTAhJ_3w9ccL6M)]
3. Configure expiration and note. Add a descriptive note (e.g., Copilot MCP Agent) and choose an expiration window. [[1](https://www.google.com/goto?url=CAESmQEBxCJF12gHlfpvcpN8c7kCbGpuAuXGJSexL5cNLN3ZVo7-lSC4d3JEvSgPXfdlna5mzL-VVse0NOkL1qNOk4CchMSwAX3Rk9gjgO3Aq9yxrkJlpW23V4jyfLRrWgDABlWy8YZI2o4-2ldTItS8l-HPwYb4-ZXKDhFFxZHYAbAQVXQVCOAPP3QydroKbQiBK8umEcaaDf58aro), [2](https://www.google.com/goto?url=CAESegHEIkXXHf1T_p2spekdI16aOR1ZrCeH0GFHBVDZ0aAP1K-0JwHyxAy5FLb9wrF6LmDjCbDvXYr524lDemyJraZ72NO8u8f8z3Q5MmH5cDq5su8y-suWhL-EGrgctnqcQUve2HyjX4o8zvsSlUzh5DwTAhJ_3w9ccL6M)]
4. Select required scopes. Check the boxes that match what you want your agent to do:
*  repo --- Full access to private and public repositories (commits, branches, pull requests, issues).  *(Use public_repo instead if you only work on public repos).*
    *  read:org --- Read organization and team membership.
    *  read:user --- Read user profile data.
    *  workflow  *(optional)*  --- Update or inspect GitHub Actions workflows.
    *  project  *(optional)*  --- Read and manage GitHub Projects. [[1](https://www.google.com/goto?url=CAESgAEBxCJF15klQ_L7HorVgf4JnPB2DYx5G3T8qXfMR6AjkvIadnZ9F2_ZFwxDyEL3IJWh9qJ3exA3E57gcfrA-mD7JhQpVkbzhmLwEX4XK2wkEQOffFGqKt43NeCuraq3Rmz4bVC4_Fn2CDtz--PKPiXYkXceuEkStVemEgpmJcicGQ), [2](https://www.google.com/goto?url=CAESegHEIkXXHf1T_p2spekdI16aOR1ZrCeH0GFHBVDZ0aAP1K-0JwHyxAy5FLb9wrF6LmDjCbDvXYr524lDemyJraZ72NO8u8f8z3Q5MmH5cDq5su8y-suWhL-EGrgctnqcQUve2HyjX4o8zvsSlUzh5DwTAhJ_3w9ccL6M), [3](https://www.google.com/goto?url=CAESYgHEIkXX0yPdmS9w-c9_esdMKfyAJuSfCxEW-q1Wd2WqFfYJ7AdLmgLiscqDrorM1lgvB4OLg8Ux3V47DCjqLd82LcsyDBA0hDrFD6vnbzfjXt0sN_7QfvQ7zuS8FqLS0AEl), [4](https://www.google.com/goto?url=CAESmQEBxCJF12gHlfpvcpN8c7kCbGpuAuXGJSexL5cNLN3ZVo7-lSC4d3JEvSgPXfdlna5mzL-VVse0NOkL1qNOk4CchMSwAX3Rk9gjgO3Aq9yxrkJlpW23V4jyfLRrWgDABlWy8YZI2o4-2ldTItS8l-HPwYb4-ZXKDhFFxZHYAbAQVXQVCOAPP3QydroKbQiBK8umEcaaDf58aro)]
5. Copy the token immediately. Click Generate token at the bottom and copy the ghp_... string right away---GitHub will not display it again.

#### Complete Architecture & Configuration Guide for GitLab Multi-Instance Mesh

Connecting multiple GitLab servers across distinct versions requires a hybrid architecture tailored to each instance's underlying MCP capabilities:

##### 1. Modern Instances (GitLab 19.5+): `gitlab.com`, `gitlab.lip.pt` & `gitlab-admin.lip.pt`

* **Native Remote Endpoint**: GitLab 19.5+ includes a native `/api/v4/mcp` endpoint.
* **Client Architecture (`mcp-remote`)**: The `mcp-remote` proxy acts as a local stdio client that speaks to remote HTTP MCP endpoints, implementing OAuth 2.0 Dynamic Client Registration.
* **Automatic Browser Login**: On the first tool invocation, `mcp-remote` intercepts the 401 challenge, opens your default web browser to the GitLab login screen, and caches the granted session token in `~/.mcp-auth/<url-hash>/`.
* **Toolset Optimization**: GitLab's MCP endpoint exposes groups of tools controlled by the `X-Gitlab-Enabled-Mcp-Server-Toolsets` HTTP header. By declaring `core,merge_requests,work_items,repository,ci,wikis,code_security`, you retain all essential developer tools while enabling opt-in `wikis` and `code_security`, and trimming `duo_agent_platform` (which is unavailable or unneeded on standard/free accounts, saving ~20k tokens from the agent context window). Note that `meta` (e.g. `get_mcp_server_version`) is always included automatically.
* **Tool-Name Prefixes**: Declaring `X-Gitlab-Mcp-Server-Tool-Name-Prefix:<prefix>_` prefixes every tool exposed by that server:
  * `gitlab.com` -> `glcom_` (e.g. `glcom_list_projects`, `glcom_get_file_contents`)
  * `gitlab.lip.pt` -> `gllip_` (e.g. `gllip_list_projects`, `gllip_create_merge_request`)
  * `gitlab-admin.lip.pt` -> `gladminlip_` (e.g. `gladminlip_list_projects`, `gladminlip_list_users`)
  This completely prevents tool namespace collisions when multiple GitLab instances are loaded into the same agent session.

##### 2. Legacy Instances (GitLab < 19.5): `gitlab.legacy.example.org` (18.2.8) & `gitlab-admin.legacy.example.org` (16.x latest)

* **API Compatibility**: GitLab 18.2.8 and 16.x predate the native `/api/v4/mcp` endpoint.
* **Client Architecture (`@zereight/mcp-gitlab`)**: Connects to the standard GitLab REST/GraphQL API via the `@zereight/mcp-gitlab` stdio MCP server.
* **Zero Secret Leakage via POSIX Subshells**: Sourcing the `.env` file via `sh -c 'set -a && . "$HOME/.config/antigravity-mcp/<name>.env" && set +a && exec npx -y @zereight/mcp-gitlab'` guarantees that:
  1. Secrets (`GITLAB_PERSONAL_ACCESS_TOKEN`) are confined strictly to that child process and never leak into global environment tables.
  2. The `exec` call replaces the shell with the Node runtime, ensuring clean termination when sessions close.
  3. `GITLAB_TOOL_PREFIX=gllegacy_` and `GITLAB_TOOL_PREFIX=gladminleg_` isolate legacy tools cleanly.
  4. Setting `GITLAB_TOOLSETS=issues,merge_requests,repositories,pipelines,wiki` loads the exact essential tools while saving ~50k tokens compared to `GITLAB_TOOLSETS=all`.

##### 3. How to Create Personal Access Tokens (PAT) for Legacy Instances

1. Sign in to your self-hosted GitLab instance (`https://gitlab.legacy.example.org` or `https://gitlab-admin.legacy.example.org`).
2. Go to **User Settings** (or click your profile avatar) -> **Access Tokens**.
3. Click **Add new token**, provide a descriptive name (e.g. `VSCode-Agent-MCP`), and set an expiration window.
4. Select the necessary scopes:
   * `api` — Full read/write access to repository, issues, merge requests, and pipelines.
   * `read_api` — Read-only access to projects and issues. (If selected, also add `GITLAB_PERMISSION_MODE=readonly` to the `.env` file).
5. Click **Create personal access token** and copy the `glpat-...` string immediately into your `.env` file (`~/.config/antigravity-mcp/gitlab-legacy.env` or `gitlab-admin-legacy.env`).

##### 4. Institutional SSL / Custom CA Certificates

If internal academic instances (e.g., `lip.pt`, `example.org`) use private or enterprise root certificates, Node.js can be configured to trust your host certificates by adding `NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` to the `.env` files or exporting it in your environment. [[1](https://www.google.com/goto?url=CAESsgEBxCJF14_zK1CNMzSqcpO82oWjD--p0-GioXb4OouUSZNkRftZtsZAfQwSMj3EbGlbNNhNJY5BoDTuBWh_yFwgLwe6e5BnjNQ7Hp_rjLrl5b8d4KSU55tr0Zq9lAyaqhBOP_x4H4Of3cC8E4GZTjzxgj_Qw8Z7cYCWcOoeb5UupVm_rp24iMwRj52cxUKh5N1eVvvoUghA6choKdxuwtt8y4wW-hSoM5RQ-vyfb9fzKnuz), [2](https://www.google.com/goto?url=CAESegHEIkXXHf1T_p2spekdI16aOR1ZrCeH0GFHBVDZ0aAP1K-0JwHyxAy5FLb9wrF6LmDjCbDvXYr524lDemyJraZ72NO8u8f8z3Q5MmH5cDq5su8y-suWhL-EGrgctnqcQUve2HyjX4o8zvsSlUzh5DwTAhJ_3w9ccL6M)]

###### Configuration Path Resolution and Compatibility Symlink

Depending on the release channel of the Google Antigravity VS Code extension (`Google.google-antigravity`), configuration discovery may check either `~/.gemini/config/mcp_config.json` or `~/.gemini/antigravity/mcp_config.json`. To guarantee automatic detection across all extension updates, create a symlink:
```bash
mkdir -p ~/.gemini/antigravity
ln -sf ~/.gemini/config/mcp_config.json ~/.gemini/antigravity/mcp_config.json
```

##### Step 6.2: Claude Code Global Configuration (~/.claude.json)

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

# Register OpenAI Codex (ChatGPT Plus) via codex-mcp-bridge
claude mcp add --scope user openai-codex-plus \
  -e CODEX_HOME="$HOME/.codex" \
  -- "$HOME/.local/bin/codex-mcp-bridge"

# Register OpenAI Codex (API Key) via codex-mcp-bridge
claude mcp add --scope user openai-codex-api \
  -e CODEX_HOME="$HOME/.codex-api" \
  -- "$HOME/.local/bin/codex-mcp-bridge"

# Register Native GitHub MCP Server via npx
claude mcp add --scope user github-mcp \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_PAT" \
  -- npx -y @modelcontextprotocol/server-github

# Register GitHub Models Bridge via Copilot Runtime
claude mcp add --scope user github-models \
  -- "/home/YOUR_USERNAME/.local/bin/github-models-mcp"

# Register GitLab.com (SaaS, 19.5+) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-com \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-com.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-com.env"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_

# Register GitLab LIP (19.5.3) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-lip \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-lip.env"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_

# Register GitLab Admin LIP (19.5.3) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-admin-lip \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_

# Register GitLab Legacy (18.2.8) via @zereight/mcp-gitlab + .env
claude mcp add --scope user gitlab-legacy \
  -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'

# Register GitLab Admin Legacy (16 latest) via @zereight/mcp-gitlab + .env
claude mcp add --scope user gitlab-admin-legacy \
  -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'

```

##### Step 6.3: OpenAI Codex Global Configuration (~/.codex/config.toml & ~/.codex-api/config.toml)

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

[mcp_servers.github-models]
command = "/home/YOUR_USERNAME/.local/bin/github-models-mcp"

[mcp_servers.gitlab-com]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-com.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_\""
]

[mcp_servers.gitlab-lip]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_\""
]

[mcp_servers.gitlab-admin-lip]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_\""
]

[mcp_servers.gitlab-legacy]
command = "sh"
args = [
  "-c",
  "set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab"
]

[mcp_servers.gitlab-admin-legacy]
command = "sh"
args = [
  "-c",
  "set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab"
]

```
Sync configuration to the API directory:
```bash
mkdir -p ~/.codex-api
cp ~/.codex/config.toml ~/.codex-api/config.toml

```

--------------------------------------------------------------------------------

#### 7. GitHub Copilot Integration and Shared Workspace MCP

GitHub Copilot operates in VS Code via the official GitHub.copilot and GitHub.copilot-chat extensions. Students can activate free Copilot Pro via the GitHub Student Developer Pack.

##### Step 7.1: Configure VS Code Copilot MCP Client (~/.config/Code/User/globalStorage/github.copilot-chat/mcp.json or .vscode/mcp.json)

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
      "command": "/home/YOUR_USERNAME/.local/bin/codex-mcp-bridge",
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex"
      }
    }
  }
}

```
This configuration enables prompting Copilot Chat to delegate complex architecture or verification tasks to your Google Cloud or Anthropic subagents:
*"@copilot Ask gemini-carbon-gcp to analyze this memory-safety profile, then have claude-fable-gcp suggest zero-cost abstractions."*

##### Step 7.2: Configure Continue VS Code Extension MCP Client (`~/.continue/config.yaml`)

The Continue extension (`Continue.continue`) connects to the exact same MCP server pool and seamlessly supports environment variable expansion (`${VAR_NAME}`) to avoid baking secrets into `config.yaml`.

Configure the `mcpServers` block in `~/.continue/config.yaml`:

```yaml
mcpServers:
  # 1. Google Cloud Gemini 4 Carbon via Native agy-mcp-bridge
  - name: gemini-carbon-gcp
    command: /home/YOUR_USERNAME/.local/bin/agy-mcp-bridge
    args: []
    env:
      GOOGLE_CLOUD_PROJECT: "YOUR_GCP_PROJECT_ID"
      GOOGLE_CLOUD_LOCATION: "global"

  # 2. Claude Fable 5.2 on Google Cloud Model Garden (Vertex AI ADC)
  - name: claude-fable-gcp
    command: /usr/bin/claude
    args:
      - mcp
      - serve
    env:
      CLAUDE_CONFIG_DIR: "/home/YOUR_USERNAME/.claude-gcp"
      CLAUDE_CODE_USE_VERTEX: "1"
      CLOUD_ML_REGION: "global"
      ANTHROPIC_VERTEX_PROJECT_ID: "YOUR_GCP_PROJECT_ID"
      ANTHROPIC_MODEL: "claude-fable-5-2"
      ANTHROPIC_SMALL_FAST_MODEL: "claude-sonnet-5-5"

  # 3. Anthropic Teams (Interactive Claude Code)
  - name: claude-teams
    command: /usr/bin/claude
    args:
      - mcp
      - serve
    env:
      CLAUDE_CONFIG_DIR: "/home/YOUR_USERNAME/.claude"

  # 4. OpenAI Codex CLI via ChatGPT Plus Subscription (€23/mo OAuth)
  - name: openai-codex-plus
    command: /home/YOUR_USERNAME/.local/bin/codex-mcp-bridge
    args: []
    env:
      CODEX_HOME: "/home/YOUR_USERNAME/.codex"

  # 5. OpenAI Codex CLI via On-Demand API Key (Pay-As-You-Go)
  - name: openai-codex-api
    command: /home/YOUR_USERNAME/.local/bin/codex-mcp-bridge
    args: []
    env:
      CODEX_HOME: "/home/YOUR_USERNAME/.codex-api"

  # 6. GitHub MCP Server (Secret-Free via Environment Variable Expansion)
  - name: github-mcp
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-github"
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"

  # 7. GitHub Models MCP Server (Copilot AI Inference via Local Bridge)
  - name: github-models
    command: /home/YOUR_USERNAME/.local/bin/github-models-mcp
    args: []

  # 8. GitLab.com (SaaS, GitLab 19.5+) via Native Remote MCP + Bearer PAT
  - name: gitlab-com
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-com.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-com.env"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_

  # 9. GitLab LIP (Self-Hosted Production, GitLab 19.5.3) via Native Remote MCP
  - name: gitlab-lip
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-lip.env"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_

  # 10. GitLab Admin LIP (Self-Hosted Admin, GitLab 19.5.3) via Native Remote MCP
  - name: gitlab-admin-lip
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_

  # 11. GitLab Legacy (Self-Hosted Legacy, GitLab 18.2.8) via @zereight/mcp-gitlab + .env
  - name: gitlab-legacy
    command: sh
    args:
      - -c
      - set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab

  # 12. GitLab Admin Legacy (Self-Hosted Legacy Admin, GitLab 16.x) via @zereight/mcp-gitlab + .env
  - name: gitlab-admin-legacy
    command: sh
    args:
      - -c
      - set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab
```

Because `GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"` dynamically pulls from your exported environment, your `config.yaml` remains completely free of credentials and can be safely committed to git repositories or shared across machines.

---


--------------------------------------------------------------------------------

##### Step 7.3: Strategy to Optimize Token Costs via Local RAG and Chat Mode

To maintain high development velocity across resource-constrained hardware (e.g. laptop with AMD Ryzen 7 5800H, 16GB RAM, and NVIDIA GTX 1650 4GB VRAM) while orchestrating across 12 MCP backends, local execution must be decoupled from frontier cloud orchestration:

1. **Stage 1: Zero-Cost Local Pre-Processing (VS Code Continue + Ollama + CPU Reranker)**: Local hardware indexes, extracts, and pre-compresses raw files into dense Markdown architectural digests without spending a single cloud API token.
2. **Stage 2: High-Context Frontier Orchestration (VS Code Antigravity + Google AI Pro / Model Garden)**: Antigravity's 1M+ token context window ingests the clean local digest and orchestrates specialized MCP subagents (`claude-fable-gcp`, `gemini-carbon-gcp`, `openai-codex-plus`, `github-models`) to generate migration plans, audit infrastructure, and produce production code.

###### 1. Hardware Allocation Strategy (Laptop vs. Office Desktop)

| Workload Phase | Machine & Hardware | Model Roles | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Phase 1: Local Extraction & Indexing** | Laptop (GTX 1650 4GB + 16GB RAM) | `qwen2.5-coder:3b` (GPU) + `nomic-embed-text` (CPU Container, port 11435) | Extract single-file purpose, triggers, endpoints, and dependencies into `/digest` files. |
| **Phase 1: Full-Workspace Synthesis** | Desktop (RTX 3050 8GB + 32GB RAM) | `qwen2.5-coder:7b` (GPU) + `bge-reranker-base` (CPU Container, port 8080) | Cross-repo `@codebase` semantic search and consolidation into master specification. |
| **Phase 2: Frontier MCP Orchestration** | Flat-Rate Cloud (Google AI Pro in Antigravity) | `gemini-3.1-pro` / `gemini-4-carbon` (1M+ context) | Dispatches tasks across MCP subagents; consumes 0 local VRAM for tool schemas. |

###### 2. Local Two-Stage RAG Indexing & `.continueignore` Setup

To index all project code locally without memory exhaustion or index pollution:
1. **Parallel CPU Embedding Engine (`ollama-embed-cpu`)**: Run the dedicated CPU Ollama service on port 11435 (`NVIDIA_VISIBLE_DEVICES=none`). This allows Continue's `@codebase` indexer to embed files across all 16 Ryzen CPU threads in system RAM while your GPU coding model stays permanently loaded in VRAM on port 11434.
2. **Embedded Vector Database (LanceDB)**: Continue stores vectors locally in `~/.continue/index/` using embedded LanceDB and SQLite metadata caches, requiring zero standalone vector database daemons.
3. **Workspace Filtering via `.continueignore`**: Exclude static assets, build outputs, and lockfiles by placing `.continueignore` in the repository root:
   ```text
   node_modules/
   dist/
   build/
   target/
   .git/
   .venv/
   venv/
   __pycache__/
   *.lock
   *.min.js
   *.map
   *.sqlite3
   *.html
   *.json
   !package.json
   !composer.json
   migration-prep/
   ```

###### 3. Mandatory Chat Mode (Avoid Agent & Plan Modes on Low VRAM)

When working with local 3B to 7B models in Continue:
* **Zero Schema Overhead**: Agent and Plan modes inject internal file-editing, terminal, and search tool schemas (**4,000 to 6,000 tokens of JSON bloat**) into every single model turn and enforce rigid JSON tool-calling loops. On a 3B model (`qwen2.5-coder:3b`), tool calls frequently stall, emit malformed syntax, or enter infinite retries.
* **Deterministic Single-Pass Execution**: **Chat mode** performs single-pass completions directly against the exact files you attach, dedicating 100% of the 16k context window to source code.

###### 4. Attaching Folders Without Deprecated `@Folder`

In modern Continue releases, `@Folder` and `@Codebase` context provider syntax are officially deprecated in `config.yaml`. To attach entire directories cleanly:
1. In the VS Code Explorer sidebar, **right-click the target repository folder** (or select 3–5 related files with `Ctrl+Click`).
2. Select **Continue → Add to Chat** (or drag the folder directly into the Continue chat input box).
3. Continue automatically expands the directory and attaches all allowed files as individual `@File` pills while strictly honoring your `.continueignore` rules.

###### 5. The 3-Phase Migration Pipeline

####### Phase 1: Local File Extraction (`/digest`)
1. Open Continue chat (**`Ctrl+L`**), verify **Chat** mode is selected with model `Laptop-Worker-3B`.
2. Attach 3 to 5 related files (or a folder under 12,000 tokens), type `/digest`, and press Enter.
3. Save the dense Markdown output to thematic files in `migration-prep/` (e.g. `01-ci.md`, `02-verification.md`, `03-ansible.md`).
4. Click **`+` (New Session)** between batches to clear the context window.

####### Phase 2: Master Consolidation (`/synthesize`)
1. Open a fresh Chat session (**`+`**).
2. Attach only your digest files (`@File migration-prep/01-ci.md`, `@File migration-prep/02-verification.md`, etc.).
3. Type `/synthesize` and press Enter.
4. Save the consolidated output as `migration-prep/MASTER_ARCHITECTURE_SPEC.md` (< 12,000 words).

####### Phase 3: Frontier Multi-Agent Orchestration in Antigravity
1. Open **Google Antigravity (`Ctrl+L`)** in **Agent** mode on your **Google AI Pro** (`gemini-3.1-pro`) or **Google Cloud Agent Platform** (`gemini-4-carbon`) subscription.
2. Attach `@migration-prep/MASTER_ARCHITECTURE_SPEC.md` and execute the master orchestration prompt:

```markdown
Read `@migration-prep/MASTER_ARCHITECTURE_SPEC.md`. You are the lead enterprise migration architect orchestrating our specialized MCP subagents to modernize this software infrastructure.

Execute this 3-stage multi-agent workflow sequentially, passing only the compact outputs from each stage to the next:

### Stage 1: Architectural Migration Plan (`claude-fable-gcp`)
Call `claude-fable-gcp` (model `claude-fable-5-2`) with the contents of `@migration-prep/MASTER_ARCHITECTURE_SPEC.md` and instruct it to:
1. Design a 3-wave phased migration plan replacing legacy Jenkins and monolithic recipes with modern containerized CI/CD (GitHub Actions or GitLab CI) and decoupled validation gates.
2. Structure the deliverables, dependencies, and cutover milestones for each repository.

### Stage 2: Infrastructure & Risk Audit (`gemini-carbon-gcp`)
Call `gemini-carbon-gcp` (using model `gemini-4-carbon-medium`) with the Wave 1–3 plan from Stage 1 and the Infrastructure Coupling section of `@migration-prep/MASTER_ARCHITECTURE_SPEC.md`. Instruct it to:
1. Identify single points of failure, hardcoded external endpoints, base-image incompatibilities (e.g., EL7 to Rocky/Alma 9), and credential migration risks.
2. Specify rollback procedures and parallel validation checks to ensure zero downtime.

### Stage 3: Starter CI Implementation (`openai-codex-plus` or `github-models`)
Call `openai-codex-plus` (`ask_codex` with model `gpt-5.3-codex`) or `github-models` (`ask_github_model` with model `auto` / `claude-sonnet-5.5`) with the Wave 1 specification from Stage 1. Instruct it to:
1. Generate clean, parameterized CI workflow templates and container build matrices for the core verification pipeline.
2. Provide a smoke-test parity checklist comparing legacy outputs with the new pipeline.

### Final Output
Synthesize all subagent deliverables into a clean, publication-ready `MIGRATION_ROADMAP.md` in my workspace root.
```


---

##### Step 7.4: Automated Multi-IDE Ignore & Context Synchronization (`genignore.py`, `update-ai-ignore.sh`, and `pre-commit`)

###### 1. Why Multi-Provider Ignore Synchronization is Critical

When orchestrating across multiple agentic tools (Continue, Antigravity, Claude Code, GitHub Copilot, and OpenAI Codex), each tool employs its own mechanism for excluding files from codebase discovery, vector indexing, and tool execution. If rules fall out of sync:
* **Token Bleed**: Background indexers attempt to chunk massive minified JavaScript bundles, binary archives, and database dumps into local or cloud context windows.
* **Secret Leakage**: Sensitive credentials (`.env`, `.env.*`, keys, certs) risk being injected into agent prompts or context snippets.
* **Context Thrashing**: Large language models receive irrelevant test fixtures, lockfiles, and compiler outputs instead of high-signal source code.

###### 2. Multi-Provider Ignore Architecture

Rather than treating instructional Markdown files as exclusion filters, this automated toolchain configures each provider's native exclusion engine:

| Provider | Target Files | Mechanism & Rules Applied |
| :--- | :--- | :--- |
| **Continue** | `.continueignore` | **Native Ignore Rules**: Standard glob exclusion syntax (`.git/`, `.venv/`, `node_modules/`, `dist/`, build artifacts). |
| **Antigravity** | `.agentignore` | **Native Ignore Rules**: Standard glob exclusion syntax preventing file discovery and context ingestion. |
| **Claude Code** | `.claude/settings.json`<br>`CLAUDE.md` | **Enforced Permissions**: Deep-merges `permissions.deny` with `Read(...)` rules into `.claude/settings.json`; provides baseline project conventions in `CLAUDE.md`. |
| **GitHub Copilot** | `.vscode/settings.json`<br>`.github/copilot-instructions.md` | **Workspace Exclusions**: Deep-merges `files.exclude` and `search.exclude` dictionaries into `.vscode/settings.json`; adds developer guidelines in `.github/copilot-instructions.md`. |
| **OpenAI Codex** | `AGENTS.md` | **Instruction Guidance**: Structured `AGENTS.md` instructions with a dedicated `## Files to exclude from analysis` section (alongside `.gitignore` fallback). |

###### 3. Component Scripts and Automation Architecture

####### A. The Generator: `genignore.py`
The core Python script (`genignore.py`) parses your project `.gitignore` and `.gitattributes` (including `filter=git-crypt` filters), merges baseline exclusions, and writes or deep-merges native configurations for all providers without destroying existing IDE settings:

```python
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
```

####### B. The Shell Wrapper: `update-ai-ignore.sh`
The standalone shell wrapper (`update-ai-ignore.sh`) automates execution by checking if `.gitignore` or `.gitattributes` have uncommitted changes before invoking `genignore.py`, with an optional `--stage` flag to automatically run `git add` on updated files:

```bash
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
```

####### C. The Git Pre-Commit Hook: `pre-commit`
The pre-commit hook (`.git/hooks/pre-commit`) inspects staged files in your Git index. If `.gitignore` or `.gitattributes` are modified, it triggers `genignore.py --generate-ignore --append` and automatically re-stages all resulting provider files so rules and configurations are committed atomically:

```bash
#!/usr/bin/env bash
# ==============================================================================
# Git Pre-Commit Hook: Auto-Sync AI Provider Ignore Files
# ==============================================================================
# Install to: .git/hooks/pre-commit (make executable with chmod +x)
#
# Inspects staged files before every commit. If .gitignore or .gitattributes
# are modified in the index, it automatically runs genignore.py --generate-ignore --append
# and re-stages the synchronized AI provider ignore and instruction files.
# ==============================================================================

set -euo pipefail

# 1. Verify we are in a Git working tree
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    exit 0
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# 2. Check if .gitignore or .gitattributes are staged in this commit
STAGED_RULES="$(git diff --cached --name-only | grep -E '^(\.gitignore|\.gitattributes)$' || true)"

if [[ -z "$STAGED_RULES" ]]; then
    # Neither file is being modified in this commit; exit cleanly
    exit 0
fi

echo "[pre-commit] Staged changes detected in: ${STAGED_RULES//$'\n'/, }"
echo "[pre-commit] Synchronizing AI provider ignore files via genignore.py..."

# 3. Locate genignore.py or wrapper script
GENIGNORE_BIN=""
WRAPPER_SCRIPT="$PROJECT_ROOT/update-ai-ignore.sh"

if [[ -f "$WRAPPER_SCRIPT" && -x "$WRAPPER_SCRIPT" ]]; then
    # Execute the wrapper with --stage and --force to ensure auto-staging
    "$WRAPPER_SCRIPT" --stage --force
    exit 0
fi

# Fallback to direct genignore.py invocation
CANDIDATE_PATHS=(
    "$PROJECT_ROOT/genignore.py"
    "$PROJECT_ROOT/scripts/genignore.py"
    "$PROJECT_ROOT/.config/genignore.py"
    "$(which genignore.py 2>/dev/null || true)"
)

for candidate in "${CANDIDATE_PATHS[@]}"; do
    if [[ -n "$candidate" && -f "$candidate" ]]; then
        GENIGNORE_BIN="$candidate"
        break
    fi
done

if [[ -z "$GENIGNORE_BIN" ]]; then
    echo "[pre-commit] Warning: genignore.py not found. Skipping AI ignore synchronization." >&2
    exit 0
fi

PYTHON_BIN="$(which python3 2>/dev/null || which python 2>/dev/null || true)"
if [[ -z "$PYTHON_BIN" ]]; then
    echo "[pre-commit] Warning: python3 not found. Skipping AI ignore synchronization." >&2
    exit 0
fi

# 4. Execute genignore.py to append/merge missing patterns
"$PYTHON_BIN" "$GENIGNORE_BIN" --generate-ignore --append

# 5. Automatically stage generated or updated provider files
PROVIDER_FILES=(
    ".continueignore"
    ".agentignore"
    ".claude/settings.json"
    "CLAUDE.md"
    ".vscode/settings.json"
    ".github/copilot-instructions.md"
    "AGENTS.md"
)

STAGED_COUNT=0
for target in "${PROVIDER_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$target" ]]; then
        git add "$PROJECT_ROOT/$target"
        ((STAGED_COUNT++)) || true
    fi
done

echo "[pre-commit] Re-staged updated AI provider files into the current commit."
exit 0
```

###### 4. Installation and Setup Instructions

####### Step 1: Install Scripts into Project or System Path
Place `genignore.py` and `update-ai-ignore.sh` in your project root or `scripts/` directory (or system `~/.local/bin/` for global availability) and make them executable:

```bash
# Make scripts executable
chmod +x genignore.py update-ai-ignore.sh

# Optional: Link to ~/.local/bin for global availability across all projects
mkdir -p ~/.local/bin
ln -sf "$(pwd)/genignore.py" ~/.local/bin/genignore.py
ln -sf "$(pwd)/update-ai-ignore.sh" ~/.local/bin/update-ai-ignore.sh
```

####### Step 2: Install the Git Pre-Commit Hook
Install the hook directly into your repository's `.git/hooks/` directory:

```bash
# Install to repository hooks
cp pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

*Alternative for `pre-commit` Framework (`.pre-commit-config.yaml`)*:
If your repository utilizes the Python `pre-commit` package, add the local hook to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: sync-ai-ignore
        name: Sync AI Provider Ignore Files
        entry: ./update-ai-ignore.sh --force --stage
        language: script
        files: ^(\.gitignore|\.gitattributes)$
        pass_filenames: false
```

###### 5. Command-Line Usage and Practical Examples

####### Example 1: Generate All Provider Files for a New Repository
Generates baseline `.continueignore`, `.agentignore`, `.claude/settings.json`, `CLAUDE.md`, `.vscode/settings.json`, `.github/copilot-instructions.md`, and `AGENTS.md`:

```bash
./genignore.py --generate-ignore
```

####### Example 2: Append Custom Exclusion Patterns Across All Tools
Appends binary, archive, key, or secret patterns to `.continueignore` and `.agentignore`, while deep-merging them into `.claude/settings.json` (`permissions.deny`) and `.vscode/settings.json` (`files.exclude`/`search.exclude`):

```bash
./genignore.py --generate-ignore --append \
  "*.rpm" "*.tar.gz" "*.png" "*.jpg" "*.svg" \
  "RPM-GPG-KEY-*" "*.secret.env"
```

####### Example 3: Target Specific AI Providers
Update only designated agent platforms:

```bash
# Generate only Continue and Antigravity ignore files
./genignore.py --generate-ignore --provider continue antigravity

# Update only Claude Code and Codex settings
./genignore.py --generate-ignore --append --provider claude codex "*.sqlite3"
```

####### Example 4: Manual Wrapper Execution with Automatic Git Staging
Force an update of all provider files and automatically stage them in Git:

```bash
./update-ai-ignore.sh --force --stage
```

####### Example 5: Automated Pre-Commit Workflow in Action
Whenever you edit `.gitignore` or `.gitattributes` and run `git commit`, the hook automatically runs:

```bash
# 1. Edit .gitignore
echo "*.data" >> .gitignore
git add .gitignore

# 2. Run git commit - hook automatically triggers
git commit -m "chore: ignore data files"
# Output:
# [pre-commit] Staged changes detected in: .gitignore
# [pre-commit] Synchronizing AI provider ignore files via genignore.py...
# [*] Synchronizing AI provider ignore files using genignore.py...
# [APPEND]    .continueignore
# [APPEND]    .agentignore
# [UPDATE]    .claude/settings.json
# [UPDATE]    .vscode/settings.json
# [APPEND]    AGENTS.md
# [*] Automatically staged updated AI provider files: .continueignore .agentignore .claude/settings.json CLAUDE.md .vscode/settings.json .github/copilot-instructions.md AGENTS.md
# [✓] AI ignore and instruction files successfully synchronized.
# [pre-commit] Re-staged updated AI provider files into the current commit.
```


---

#### 8. Arch Linux KDE Plasma 6 (Wayland) and Systemd Configuration

Arch Linux ships KDE Plasma 6 on Wayland as default. Configure Wayland parameters and ensure clean environment variable loading.

##### Step 8.1: Wayland and KWallet Flags (~/.config/code-flags.conf)

Create or update ~/.config/code-flags.conf:
```ini
--ozone-platform-hint=auto
--enable-wayland-ime
--password-store=kwallet6

```

##### Step 8.2: Environment Hygiene Check

Ensure no AI variables are exported globally in ~/.config/environment.d/ or /etc/environment. Global exports override extension settings and cause authentication failures:
```bash
# Verify clean environment generators
rm -f ~/.config/environment.d/*ai*.conf
systemctl --user daemon-reload

```

--------------------------------------------------------------------------------

#### 9. Unified Shell Functions, Aliases, and Dynamic Model Switchers

Add this suite to ~/.bashrc (or ~/.zshrc) to manage tokens, providers, and models natively:
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
      -X|--xhigh)  arg
```
```bash
s+=(-c 'model_reasoning_effort="xhigh"'); shift ;;
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

--------------------------------------------------------------------------------

#### 10. End-to-End Verification and Diagnostics

##### Step 10.1: Test agy-mcp-bridge Protocol Handshake

Send initialization and tool listing requests:
```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' \
  | ~/.local/bin/agy-mcp-bridge

```
Confirm that the bridge outputs valid JSON-RPC responses containing "protocolVersion": "2024-11-05" and the ask_gemini_carbon tool schema without executing Docker.

##### Step 10.2: Verify Registered Servers in Claude Code

Run the server health check:
```bash
claude mcp list

```
Verify that all 12 configured servers (`gemini-carbon-gcp`, `claude-fable-gcp`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`, `github-models`, `gitlab-com`, `gitlab-lip`, `gitlab-admin-lip`, `gitlab-legacy`, `gitlab-admin-legacy`) display `Connected`.

##### Step 10.3: Inspect Live Indicators and Utilize MCP Servers in VS Code Antigravity

###### Understanding the Antigravity UI Model

In the Google Antigravity VS Code extension, MCP servers do **not** appear as separate explorer sidebars, file trees, or dedicated window panes. Instead, they are embedded directly into the Antigravity agent execution harness as background callable tools.

###### Viewing and Inspecting MCP Servers in the UI

1. **The `/mcp` Slash Command**:
   * Open the Antigravity chat panel by clicking the Antigravity icon in the Activity Bar or pressing **`Ctrl+L`**.
   * In the chat prompt input, type **`/mcp`** and press **Enter**.
   * Antigravity opens a live diagnostic dashboard displaying connection status rings for every registered server (`gemini-carbon-gcp`, `claude-fable-gcp`, `claude-teams`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`):
     * **Green Ring**: Server is healthy, connected, and tool schemas are successfully registered.
     * **Amber Ring**: Server process is initializing or undergoing protocol handshake.
     * **Red Ring**: Server process terminated, binary not found, or JSON-RPC handshake failed. Clicking the server reveals stdout/stderr logs.
2. **The Panel Header Tools / MCP Icon**:
   * In the top-right header of the Antigravity chat panel, click the **Tools / Plug icon** to open the registered tools modal and inspect active capabilities.

###### How to Use MCP Servers in Chat Conversations

* **Explicit Subagent Delegation**:
  Prompt the agent directly to route requests through specific subagent tools:
  * *"Ask `gemini-carbon-gcp` to audit this system architecture using model `gemini-4-carbon`."*
  * *"Have `claude-fable-gcp` review the diff proposed by `gemini-carbon-gcp` before applying changes."*
  * *"Use `openai-codex-plus` (via `ask_codex`) to provide a second-opinion refactoring for this module."*
  * *"Query `github-mcp` to list open pull requests and recent commit issues in this repository."*
* *"Query `github-models` using tool `list_github_models` to inspect available Copilot models."*
* *"Using `github-models` with default `auto` model routing, write a unit test for this parser."*
* *"Ask `github-models` with model `grok-4.7` to evaluate this edge case."*
* *"Ask `github-models` with model `mai-code-2-flash` to optimize this loop."*
* *"Use `github-models` with model `claude-sonnet-5.5` to review the architectural plan."*
* *"Query `gitlab-com` using tool `glcom_list_projects` to check my recent repositories."*
* *"Using `gitlab-lip` (tool `gllip_list_merge_requests`), review open MRs targeting production."*
* *"Inspect the latest CI pipeline failures on `gitlab.legacy.example.org` via `gitlab-legacy` (tool `gllegacy_list_pipelines`)."*
* *"Search recent issues on Admin GitLab using `gitlab-admin-legacy` (tool `gladminleg_list_issues`)."*
* **Autonomous Tool Execution**:
  When prompted with complex workflows (e.g. cross-repository analysis or deep static audits), the active Antigravity model autonomously selects and executes the appropriate MCP tool, surfacing an approval or execution card in the conversation stream.

###### Troubleshooting: If `/mcp` is Empty or Servers Fail to Connect

1. **Path Symlink**: Ensure both configuration paths point to your active configuration:
   ```bash
   mkdir -p ~/.gemini/antigravity
   ln -sf ~/.gemini/config/mcp_config.json ~/.gemini/antigravity/mcp_config.json
   ```
2. **Absolute Binary Paths**: Desktop launcher environments (KDE Plasma Wayland / systemd) do not inherit shell profile additions to `$PATH`. Ensure all `command` entries in `mcp_config.json` use full absolute paths (`/home/YOUR_USERNAME/.local/bin/agy-mcp-bridge`, `/home/YOUR_USERNAME/.local/bin/codex-mcp-bridge`, `/usr/bin/claude`, `/usr/bin/npx`).
3. **Execution Permissions**: Verify bridge scripts are executable:
   ```bash
   chmod +x ~/.local/bin/agy-mcp-bridge ~/.local/bin/codex-mcp-bridge
   ```
4. **Reload Window**: After modifying `mcp_config.json`, reload VS Code to re-initialize the MCP client:
   * Press **`Ctrl+Shift+P`** → run **`Developer: Reload Window`**.

##### Step 10.4: Verify Secondary Extension Status (Claude Code, Continue & Copilot)

1. **Claude Code**: Open Claude Code sidebar (**`Ctrl+Shift+P`** → `Claude Code: Open in Side Bar`) and execute `/mcp` in the prompt box. All five servers should report `Connected`.
2. **Continue Extension**: Open the Continue sidebar (**`Ctrl+L`**). The configured MCP tools will display active status in the prompt tool picker.
3. **GitHub Copilot Chat**: Open Copilot Chat (**`Ctrl+Alt+I`**) and verify tool availability.

--------------------------------------------------------------------------------

#### 11. Lifecycle Maintenance Playbook: Retiring ChatGPT Plus

When your €23/month ChatGPT Plus billing cycle concludes:
1.  **Remove Plus from Antigravity** : Delete the "openai-codex-plus" block from ~/.gemini/config/mcp_config.json.
2.  **Remove Plus from Claude Code** :
```bash
claude mcp remove --scope user openai-codex-plus

```
3.  **Clean Configuration Files** :
```bash
rm -rf ~/.codex

```
4.  **Retain On-Demand API** : Keep "openai-codex-api" active across all configs. It incurs zero cost when idle and meters tokens only when an agent is explicitly instructed to execute an OpenAI call.