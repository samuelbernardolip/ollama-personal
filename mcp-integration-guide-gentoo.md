# Complete MCP Integration Guide for VS Code on Gentoo Linux: Antigravity, Claude Code, OpenAI Codex, GitHub Copilot, and Continue (Enterprise Edition)

An enterprise-grade reference architecture for orchestrating multi-provider AI agents, Model Context Protocol (MCP) servers, and isolated developer identities under Gentoo Linux (rolling release, systemd profile, KDE Plasma 6 on Wayland) addressing both **Containerized** and **Native Ebuild** Google Cloud CLI environments.

---

## 1. System Architecture and Identity Isolation Matrix

On Gentoo Linux, maintaining package hygiene and avoiding unmanaged host binaries is paramount. While `dev-util/claude-code` is available in the main Portage tree and `dev-util/google-antigravity-cli` and `dev-util/codex` are available in `guru`, **there is currently no official `google-cloud-cli` or `google-cloud-sdk` ebuild in the primary `::gentoo` tree or `::guru`**. Historically, `dev-util/google-cloud-sdk` was removed from Portage due to Google's self-updating component architecture (`gcloud components update`) and vendored Python dependencies clashing with Gentoo QA standards.

This guide provides two robust paths for Google Cloud Application Default Credentials (ADC):
1. **Containerized Architecture (Primary / Zero Host Contamination)**: Runs the official Google Cloud CLI inside a minimal, user-isolated Docker container via Docker Compose, exposing tokens directly to host user storage.
2. **Native Ebuild Architecture (Alternative / Local Overlay)**: Provides a production-ready custom binary ebuild (`dev-util/google-cloud-cli-bin`) in a local Portage repository (`/var/db/repos/localrepo`) for users who prefer native host execution without Docker daemon overhead.

Both architectures guarantee identical, hermetic isolation across all four providers and seven operational tiers:

1. **Google AI Pro (Consumer Subscription)**: Flat-rate consumer subscription driving daily interactive development in the Google Antigravity VS Code extension and the Antigravity CLI (`agy-pro`).
2. **Google Cloud Agent Platform (Enterprise ADC)**: Pay-as-you-go Vertex AI infrastructure providing on-demand execution for **Gemini 4 Carbon** and **Claude Opus 5.5**, accessed via ADC and a zero-dependency local MCP bridge.
3. **Anthropic Teams (Organization OAuth)**: Standard corporate team subscription driving the official Claude Code VS Code extension and terminal workflow (`claude-teams`).
4. **Claude Fable 5.2 on Google Cloud Model Garden**: Enterprise Claude execution hosted on Google infrastructure, isolated through a dedicated configuration directory (`~/.claude-gcp`) and invoked as an MCP subagent.
5. **OpenAI ChatGPT Plus (€23/mo Consumer OAuth)**: Flat-rate consumer access driving the OpenAI Codex CLI and VS Code extension (`openai-codex-plus`), isolated within `~/.codex`.
6. **OpenAI API (Pay-As-You-Go)**: On-demand per-token API billing used when Plus rate limits are exhausted or for automated background tasks, isolated within `~/.codex-api`.
7. **GitHub Copilot (Student / Individual / Enterprise)**: GitHub's code intelligence engine operating alongside local MCP servers, paired with a native Node or containerized GitHub MCP server for workspace awareness.

### Complete Provider and Billing Matrix

| Provider / Subscription | Primary Host Client | Auth Mechanism | Configuration Directory | MCP Server Identifier | Financial Impact / Metering |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google AI Pro** | Antigravity IDE / `agy-pro` | Browser OAuth (Google SSO) | `~/.gemini/` | Native Host Agent | Flat monthly subscription (€0 additional) |
| **Google Cloud Agent Platform** | `agy-mcp-bridge` / `agy-gcp` | ADC Token (Container or Native Ebuild) | `~/.config/gcloud/` | `gemini-carbon-gcp` | Pay-as-you-go per token on GCP project |
| **Anthropic Teams** | Claude Code IDE / `claude-teams` | Browser OAuth (Anthropic SSO) | `~/.claude/` | `claude-teams` | Flat team seat license |
| **Google Cloud Model Garden (Fable 5.2)** | Claude Code CLI / MCP | Vertex AI ADC Token | `~/.claude-gcp/` | `claude-fable-gcp` | Pay-as-you-go per token on GCP project |
| **OpenAI ChatGPT Plus** | Codex IDE / `codex-plus` | Terminal OAuth (ChatGPT Web) | `~/.codex/` | `openai-codex-plus` | Flat €23/month (subject to cancellation) |
| **OpenAI API** | Codex IDE / `codex-api` | Secret API Key (`sk-proj-...`) | `~/.codex-api/` | `openai-codex-api` | Pay-as-you-go per token balance |
| **GitHub Copilot** | Copilot Chat VS Code | GitHub OAuth Token | `~/.config/github-copilot/` | `github-mcp` | Included via Student Pack / Monthly seat |

---

## 2. Gentoo Host Prerequisites and Portage Package Management

Gentoo packages AI developer tools across the official `::gentoo` repository, the official Gentoo User Repository (`::guru`), and local overlays.

### Step 2.1: Enable the `::guru` Overlay

Install `eselect-repository`, enable `guru`, and synchronize repository metadata:

```bash
sudo emerge -av app-eselect/eselect-repository
sudo eselect repository enable guru
sudo emaint sync -r guru
```

### Step 2.2: Configure Licenses and Keywords

Add package licenses and keywords to `/etc/portage/`:

```bash
# Package licenses
cat << 'EOF' | sudo tee -a /etc/portage/package.license
dev-util/claude-code all-rights-reserved
dev-util/google-antigravity-cli all-rights-reserved
app-editors/vscode Microsoft-vscode
EOF

# Package keywords (unmask ~amd64 for tools in testing)
cat << 'EOF' | sudo tee -a /etc/portage/package.accept_keywords
dev-util/claude-code ~amd64
dev-util/google-antigravity-cli ~amd64
dev-util/codex ~amd64
EOF

# USE flags for VS Code and Node/Python tooling
cat << 'EOF' | sudo tee -a /etc/portage/package.use
app-editors/vscode wayland
net-libs/nodejs npm
EOF
```

### Step 2.3: Emerge Host Dependencies

Install the core suite:

```bash
sudo emerge -av \
  app-editors/vscode \
  dev-util/claude-code \
  dev-util/google-antigravity-cli::guru \
  dev-util/codex::guru \
  dev-util/github-cli \
  net-libs/nodejs \
  app-crypt/libsecret \
  kde-plasma/kwallet-pam
```

*Note on Docker: If utilizing the containerized `gcloud` approach in Section 3A, also emerge `app-containers/docker` and `app-containers/docker-compose` and enable `docker.service`.*

> ⚠️ **Important Package Clarification: Google Antigravity CLI (`agy`) vs Python Packages**
> On Gentoo, the compiled command-line agent is provided by `dev-util/google-antigravity-cli::guru` (which installs `/usr/bin/agy`). Do **not** confuse this with `python-google-antigravity` or Python SDKs from PyPI/overlays, which are client libraries and do not provide the `agy` command-line interface.
> 
> *Alternative standalone installation without `guru`:*
> If you do not wish to enable the `::guru` overlay for Antigravity, you can install Google's official compiled standalone binary directly into `~/.local/bin/agy`:
> ```bash
> mkdir -p ~/.local/bin
> curl -fsSL https://antigravity.google/cli/install.sh | bash
> ```
> Or symlink the binary bundled automatically by the **Google Antigravity** VS Code extension:
> ```bash
> ln -sf ~/.antigravity/bin/agy ~/.local/bin/agy
> ```

Verify binary locations on your host system:
- VS Code: `/usr/bin/code`
- Claude Code: `/usr/bin/claude`
- Antigravity CLI: `/usr/bin/agy` (or `~/.local/bin/agy`)
- OpenAI Codex: `/usr/bin/codex`
- GitHub CLI: `/usr/bin/gh`

---

## 3. Google Cloud SDK Authentication: Two Supported Approaches

Because Gentoo does not have `google-cloud-cli` in the official main tree, select either **Section 3A (Containerized)** or **Section 3B (Native Local Ebuild)**.

---

### Section 3A: Containerized Google Cloud SDK (Primary Method)

Running the Google Cloud SDK inside a minimal Docker container prevents host Python pollution. Using Docker Compose with a pinned user ID guarantees that credentials generated inside the container remain owned by your local Gentoo user.

#### Step 3A.1: Deploy Docker Compose Configuration

Create the isolated compose workspace and definition:

```bash
mkdir -p ~/.config/gcloud-compose ~/.config/gcloud

cat << 'EOF' > ~/.config/gcloud-compose/docker-compose.yml
services:
  gcloud:
    image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
    user: "${UID:-1000}:${GID:-1000}"
    environment:
      - HOME=/tmp/gcloud-home
      - CLOUDSDK_CONFIG=/config/gcloud
    volumes:
      - ${HOME}/.config/gcloud:/config/gcloud
    working_dir: /config/gcloud
EOF
```

Ensure your Gentoo user belongs to the `docker` group and the Docker daemon is active:

```bash
sudo usermod -aG docker $USER
sudo systemctl enable --now docker.service
```

#### Step 3A.2: Generate Application Default Credentials (ADC)

Run the containerized login flow with non-browser authentication:

```bash
UID=$(id -u) GID=$(id -g) docker compose -f ~/.config/gcloud-compose/docker-compose.yml run --rm gcloud \
  gcloud auth application-default login --no-launch-browser --project="YOUR_GCP_PROJECT_ID"
```

1. Copy the URL output by the command into your local browser.
2. Sign in with your Google Cloud account holding Vertex AI permissions.
3. Paste the authorization verification code back into the terminal.
4. Verify the credential file exists and is owned by your user:

```bash
ls -l ~/.config/gcloud/application_default_credentials.json
```

---

### Section 3B: Native Local Ebuild Alternative (`google-cloud-cli-bin`)

If you want to eliminate containers on Gentoo entirely, create a local Portage repository (`/var/db/repos/localrepo`) and maintain a simple binary ebuild that unpacks Google's official standalone Linux archive into `/opt/google-cloud-cli`.

#### Step 3B.1: Configure a Local Portage Repository

```bash
sudo mkdir -p /var/db/repos/localrepo/{profiles,metadata,dev-util/google-cloud-cli-bin}

# Define repository metadata
cat << 'EOF' | sudo tee /var/db/repos/localrepo/profiles/repo_name
localrepo
EOF

cat << 'EOF' | sudo tee /var/db/repos/localrepo/metadata/layout.conf
masters = gentoo
auto-sync = false
EOF

# Register local repository in Portage
cat << 'EOF' | sudo tee /etc/portage/repos.conf/localrepo.conf
[localrepo]
location = /var/db/repos/localrepo
priority = 100
auto-sync = no
EOF
```

#### Step 3B.2: Create the `dev-util/google-cloud-cli-bin` Ebuild

```bash
cat << 'EOF' | sudo tee /var/db/repos/localrepo/dev-util/google-cloud-cli-bin/google-cloud-cli-bin-480.0.0.ebuild
# Copyright 2026 Gentoo Authors
# Distributed under the terms of the Apache License 2.0

EAPI=8

DESCRIPTION="Google Cloud Command Line Interface (standalone binary package)"
HOMEPAGE="https://cloud.google.com/sdk"
SRC_URI="amd64? ( https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${PV}-linux-x86_64.tar.gz )
         arm64? ( https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${PV}-linux-arm.tar.gz )"

LICENSE="Apache-2.0"
SLOT="0"
KEYWORDS="~amd64 ~arm64"
RESTRICT="strip bindist"

RDEPEND="dev-lang/python:3.12
         net-misc/curl"

S="${WORKDIR}/google-cloud-sdk"

src_install() {
    dodir /opt/google-cloud-cli
    cp -a "${S}/." "${ED}/opt/google-cloud-cli/" || die "Install failed"
    
    # Symlink core binaries into standard PATH
    dodir /usr/bin
    dosym ../../opt/google-cloud-cli/bin/gcloud /usr/bin/gcloud
    dosym ../../opt/google-cloud-cli/bin/gsutil /usr/bin/gsutil
}
EOF

# Generate Portage digest manifest
cd /var/db/repos/localrepo/dev-util/google-cloud-cli-bin
sudo ebuild google-cloud-cli-bin-480.0.0.ebuild manifest
```

#### Step 3B.3: Emerge Native `google-cloud-cli-bin` and Authenticate

```bash
# Accept keyword
echo "dev-util/google-cloud-cli-bin ~amd64" | sudo tee -a /etc/portage/package.accept_keywords

# Install native package
sudo emerge -av dev-util/google-cloud-cli-bin::localrepo

# Perform native login (launches native browser directly)
gcloud auth application-default login --project="YOUR_GCP_PROJECT_ID"
```

---

## 4. Isolated Multi-Account State Layout

To prevent identity conflicts, each service maintains an independent configuration boundary:

```
/home/$USER/
├── .config/
│   ├── gcloud/                      ← ADC tokens (Gemini 4 Carbon & Fable 5.2)
│   ├── gcloud-compose/              ← (Optional) Compose definition if using Section 3A
│   └── code-flags.conf              ← VS Code Wayland & KWallet 6 flags
├── .gemini/
│   ├── config/
│   │   ├── config.json              ← Antigravity core settings ("enableAdc": false)
│   │   └── mcp_config.json          ← Antigravity & agy unified MCP server definitions
│   └── antigravity-cli/             ← agy CLI state
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

Authenticate each provider in its respective isolated storage directory on Gentoo:

```bash
# 1. Google AI Pro OAuth login in Antigravity CLI
/usr/bin/agy

# 2. Anthropic Teams OAuth login in Claude Code
/usr/bin/claude login

# 3. OpenAI ChatGPT Plus login in ~/.codex (using /usr/bin/codex)
/usr/bin/codex login

# 4. OpenAI API Key login in ~/.codex-api (using /usr/bin/codex)
mkdir -p ~/.codex-api
printenv "sk-proj-YOUR_OPENAI_API_KEY" | CODEX_HOME="$HOME/.codex-api" /usr/bin/codex login

# 5. GitHub Copilot CLI authorization
/usr/bin/gh auth login --web -s copilot
```

---

## 5. The Universal Python MCP Bridge (`agy-mcp-bridge`)

Because the Antigravity CLI communicates via the Agent Client Protocol (ACP) rather than standard-IO MCP server mode, this self-contained Python 3 bridge exposes `ask_gemini_carbon` as a standard MCP tool. It **auto-detects** whether your Gentoo host is using native `gcloud` (Section 3B) or containerized Docker Compose `gcloud` (Section 3A), validating ADC tokens transparently before execution.

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

HOME = os.path.expanduser("~")
COMPOSE_FILE = os.path.join(HOME, ".config/gcloud-compose/docker-compose.yml")
ADC_FILE = os.path.join(HOME, ".config/gcloud/application_default_credentials.json")

AGY_BIN = shutil.which("agy") or "/usr/bin/agy"
NATIVE_GCLOUD = shutil.which("gcloud") or "/usr/bin/gcloud"

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def check_adc():
    """Verify ADC token validity via Native gcloud or Containerized Fallback."""
    if not os.path.exists(ADC_FILE):
        return False
    
    # Priority 1: Check via native gcloud binary if installed
    if os.path.exists(NATIVE_GCLOUD) and os.access(NATIVE_GCLOUD, os.X_OK):
        res = subprocess.run(
            [NATIVE_GCLOUD, "auth", "application-default", "print-access-token"],
            capture_output=True, text=True
        )
        return res.returncode == 0
    
    # Priority 2: Check via Docker Compose container
    if os.path.exists(COMPOSE_FILE):
        env = os.environ.copy()
        env["UID"] = str(os.getuid())
        env["GID"] = str(os.getgid())
        res = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "run", "--rm", "-T", "gcloud",
             "gcloud", "auth", "application-default", "print-access-token"],
            env=env, capture_output=True, text=True
        )
        return res.returncode == 0

    return True

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        continue

    # Suppress notifications lacking request IDs
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
                    "description": "Query Gemini 4 Carbon or Claude Opus 5.5 on Google Cloud Agent Platform via Antigravity CLI in ADC mode.",
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
                    "content": [{"type": "text", "text": "Google Cloud ADC token missing or expired. Run 'gcp-auth-refresh' in your terminal."}],
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

## 6. MCP Server Configurations Across All Extensions

Configure the shared MCP endpoints so Antigravity, Claude Code, and Codex can cross-call any provider backend on demand.

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
      "command": "/usr/bin/claude",
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
      "command": "/usr/bin/claude",
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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

*Note: Replace `/home/YOUR_USERNAME` with your actual `$HOME` path and `YOUR_GCP_PROJECT_ID` with your project name. If system paths are required, `claude` and `codex` resolve to `/usr/bin/claude` and `/usr/bin/codex`.*

Gemini/Antigravity CLI does not support interactive `${input:...}` prompts, but it automatically expands `$VAR_NAME` or `${VAR_NAME}` from your shell environment or a `.gemini/.env` file.

**Where to store the token:** Add `GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PAT` to `~/.gemini/.env` (or export it in your shell profile `~/.bashrc` or `~/.config/environment.d/github.conf`) so your config stays secret-free and safe to commit into version control.

#### Complete Procedure to Create the GitHub Personal Access Token (PAT)

Generate a GitHub Personal Access Token (PAT) in your [GitHub Developer Settings](https://github.com/settings/tokens) and supply it to your agents via the `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable.

For Copilot agents, Continue, and `@modelcontextprotocol/server-github`, a **Classic PAT (`ghp_...`)** is recommended because the MCP server uses OAuth scope filtering to automatically enable only the tools your token supports.

##### Step-by-Step GitHub PAT Creation:
1. **Open token settings**: Sign in to GitHub, click your profile picture (top-right), and navigate to **Settings** → **Developer settings** (bottom of left sidebar) → **Personal access tokens** → **Tokens (classic)**.
2. **Generate a new token**: Click **Generate new token** → **Generate new token (classic)**.
3. **Configure expiration and note**: Add a descriptive note (e.g., `Copilot MCP Agent - Gentoo Workstation`) and choose an expiration window (e.g., 90 days or custom).
4. **Select required scopes**: Check the boxes that match what you want your agent to do:
   * `repo` — Full access to private and public repositories (commits, branches, pull requests, issues). *(Use `public_repo` instead if you strictly work on public open-source repos).*
   * `read:org` — Read organization and team membership (required for enterprise teams).
   * `read:user` — Read user profile data.
   * `workflow` *(optional)* — Update or inspect GitHub Actions CI/CD workflows.
   * `project` *(optional)* — Read and manage GitHub Projects boards.
5. **Copy the token immediately**: Click **Generate token** at the bottom and copy the `ghp_...` string right away—GitHub will never display it again.

### Step 6.2: Claude Code Global Configuration (`~/.claude.json`)

Register the MCP endpoints into Claude Code:

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
  -- /usr/bin/claude mcp serve

# Register OpenAI Codex (ChatGPT Plus)
claude mcp add --scope user openai-codex-plus \
  -e CODEX_HOME="$HOME/.codex" \
  -- /usr/bin/codex mcp-server

# Register OpenAI Codex (API Key)
claude mcp add --scope user openai-codex-api \
  -e CODEX_HOME="$HOME/.codex-api" \
  -- /usr/bin/codex mcp-server

# Register Native GitHub MCP Server via npx (inheriting GITHUB_PERSONAL_ACCESS_TOKEN from environment)
claude mcp add --scope user github-mcp \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}" \
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
command = "/usr/bin/claude"
args = ["mcp", "serve"]
[mcp_servers.claude-fable-gcp.env]
CLAUDE_CONFIG_DIR = "/home/YOUR_USERNAME/.claude-gcp"
CLAUDE_CODE_USE_VERTEX = "1"
CLOUD_ML_REGION = "global"
ANTHROPIC_VERTEX_PROJECT_ID = "YOUR_GCP_PROJECT_ID"
ANTHROPIC_MODEL = "claude-fable-5-2"

[mcp_servers.claude-teams]
command = "/usr/bin/claude"
args = ["mcp", "serve"]
[mcp_servers.claude-teams.env]
CLAUDE_CONFIG_DIR = "/home/YOUR_USERNAME/.claude"

[mcp_servers.github-mcp]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
[mcp_servers.github-mcp.env]
GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PERSONAL_ACCESS_TOKEN}"
```

Sync configuration to the API directory:

```bash
mkdir -p ~/.codex-api
cp ~/.codex/config.toml ~/.codex-api/config.toml
```

---

## 7. GitHub Copilot Integration and Shared Workspace MCP

GitHub Copilot operates in VS Code via official marketplace extensions. Configure Copilot Chat to delegate complex tasks directly to your local MCP network:

### Step 7.1: Configure VS Code Copilot MCP Client (`~/.config/Code/User/globalStorage/github.copilot-chat/mcp.json` or `.vscode/mcp.json`)

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
      "command": "/usr/bin/claude",
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
      "command": "/usr/bin/claude",
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

### Step 7.2: Configure Continue VS Code Extension MCP Client (`~/.continue/config.yaml`)

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
    command: /usr/bin/codex
    args:
      - mcp-server
    env:
      CODEX_HOME: "/home/YOUR_USERNAME/.codex"

  # 5. OpenAI Codex CLI via On-Demand API Key (Pay-As-You-Go)
  - name: openai-codex-api
    command: /usr/bin/codex
    args:
      - mcp-server
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
```

Because `GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"` dynamically pulls from your exported environment, your `config.yaml` remains completely free of credentials and can be safely committed to git repositories or shared across machines.

---

## 8. Gentoo KDE Plasma 6 (Wayland) and Systemd Configuration

When running Gentoo under systemd with KDE Plasma 6 on Wayland, ensure smooth window rendering and secure secret retrieval.

### Step 8.1: Wayland and KWallet Flags (`~/.config/code-flags.conf`)

Ensure Electron launches natively on Wayland with KWallet 6 integration:

```ini
--ozone-platform-hint=auto
--enable-wayland-ime
--password-store=kwallet6
```

### Step 8.2: Environment Hygiene Check

Do **not** export global AI environment variables in `~/.config/environment.d/` or `/etc/environment`. Clean up any legacy variables to avoid credential leakage:

```bash
# Clean out legacy environment files if previously configured
rm -f ~/.config/environment.d/*ai*.conf
systemctl --user daemon-reload
```

---

## 9. Unified Shell Functions, Aliases, and Dynamic Model Switchers

Add this suite to `~/.bashrc` (or `~/.zshrc`). It auto-detects native `gcloud` vs containerized `gcloud` seamlessly:

```bash
# ==============================================================================
# Multi-Agent Development Suite: Gentoo Linux (Universal Edition)
# ==============================================================================

export GCP_AGENT_PROJECT="YOUR_GCP_PROJECT_ID"
export GCP_AGENT_REGION="global"

# 1. Universal Google Cloud ADC Check & Refresh
gcp-auth-refresh() {
  local project_id="${GCP_AGENT_PROJECT:-YOUR_GCP_PROJECT_ID}"
  local compose_file="$HOME/.config/gcloud-compose/docker-compose.yml"
  mkdir -p "$HOME/.config/gcloud"

  # Path A: Native gcloud CLI (if installed via local ebuild /opt/google-cloud-cli)
  if which gcloud >/dev/null 2>&1; then
    if gcloud auth application-default print-access-token >/dev/null 2>&1; then
      return 0
    fi
    echo "[!] Native Google Cloud ADC token expired or missing. Launching login..."
    gcloud auth application-default login --project="$project_id"
    return $?
  fi

  # Path B: Containerized Docker Compose gcloud fallback
  if [ -f "$compose_file" ]; then
    if UID=$(id -u) GID=$(id -g) docker compose -f "$compose_file" run --rm -T gcloud \
      gcloud auth application-default print-access-token >/dev/null 2>&1; then
      return 0
    fi
    echo "[!] Containerized Google Cloud ADC token expired or missing. Launching login container..."
    UID=$(id -u) GID=$(id -g) docker compose -f "$compose_file" run --rm gcloud \
      gcloud auth application-default login --no-launch-browser --project="$project_id"
    return $?
  fi

  echo "[-] Error: Neither native 'gcloud' nor '~/.config/gcloud-compose/docker-compose.yml' was found."
  return 1
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
  AGY_ADC_AUTH=false /usr/bin/agy "${args[@]}" "$@"
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
  /usr/bin/agy -m "$model" "$@"
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
  /usr/bin/claude "$@"
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
  CLAUDE_CONFIG_DIR="$HOME/.claude" /usr/bin/claude "${model_args[@]}" "$@"
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
  CODEX_HOME="$codex_home" /usr/bin/codex "${args[@]}" "$@"
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

Confirm that the bridge outputs valid JSON-RPC responses containing `"protocolVersion": "2024-11-05"` and the `ask_gemini_carbon` tool schema.

### Step 10.2: Verify Registered Servers in Claude Code

Run the server health check:

```bash
claude mcp list
```

Verify that all five configured servers (`gemini-carbon-gcp`, `claude-fable-gcp`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`) display `Connected`.

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
