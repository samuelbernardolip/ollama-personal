# Complete MCP Integration Guide for VS Code on Gentoo Linux: Antigravity, Claude Code, OpenAI Codex, GitHub Copilot, Continue, and GitLab Multi-Instance Mesh (Enterprise Edition v7)

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

8. **GitLab Multi-Instance Mesh (SaaS, Enterprise & Institutional Infrastructure)**: Seamless multi-instance GitLab integration connecting agents to five distinct developer and administrative platforms: **GitLab.com** (SaaS, 19.5+), **gitlab.lip.pt** (LIP production, 19.5.3), **gitlab-admin.lip.pt** (LIP admin, 19.5.3), **gitlab.legacy.example.org** (Legacy, 18.2.8), and **gitlab-admin.legacy.example.org** (Admin legacy, 16.x latest). Modern instances communicate via native remote MCP (`mcp-remote`) with URL-isolated OAuth caching, while legacy instances communicate via local stdio `@zereight/mcp-gitlab` servers with dedicated `.env` credential files. Unique tool-name prefixes (`glcom_`, `gllip_`, `gladminlip_`, `gllegacy_`, `gladminleg_`) prevent tool namespace collisions across repositories.

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
| **GitLab.com** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth) | `~/.mcp-auth/` | `gitlab-com` | Included via SaaS Free/Premium (`glcom_` prefix) |
| **GitLab LIP (19.5.3)** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth/PAT) | `~/.mcp-auth/` | `gitlab-lip` | Institutional production instance (`gllip_` prefix) |
| **GitLab Admin LIP (19.5.3)** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via OAuth/PAT) | `~/.mcp-auth/` | `gitlab-admin-lip` | Institutional admin instance (`gladminlip_` prefix) |
| **GitLab Legacy (18.2.8)** | Antigravity / Claude / Codex / Copilot / Continue | Stdio MCP (`@zereight/mcp-gitlab`) + PAT | `~/.config/antigravity-mcp/` | `gitlab-legacy` | Self-hosted legacy instance (`gllegacy_` prefix) |
| **GitLab Admin Legacy (16 latest)** | Antigravity / Claude / Codex / Copilot / Continue | Stdio MCP (`@zereight/mcp-gitlab`) + PAT | `~/.config/antigravity-mcp/` | `gitlab-admin-legacy` | Self-hosted legacy admin instance (`gladminleg_` prefix) |
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
│   ├── antigravity-mcp/             ← Dedicated .env files for legacy/PAT GitLab instances (0700)
│   │   ├── gitlab-legacy.env         ← PAT, URL & tool prefix for gitlab.legacy.example.org (18.2.8)
│   │   └── gitlab-admin-legacy.env          ← PAT, URL & tool prefix for gitlab-admin.legacy.example.org (16 latest)
│   ├── gcloud/                      ← ADC tokens (Gemini 4 Carbon & Fable 5.2)
│   ├── gcloud-compose/              ← (Optional) Compose definition if using Section 3A
│   └── code-flags.conf              ← VS Code Wayland & KWallet 6 flags
├── .mcp-auth/                       ← mcp-remote automatic OAuth token cache (gitlab.com, lip.pt)
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

---

## 5. Universal Python MCP Bridges: Antigravity and OpenAI Codex

Both the **Google Antigravity CLI (`agy`)** and the **OpenAI Codex CLI (`codex`)** require lightweight, zero-dependency Python bridges to operate as standard-IO Model Context Protocol (MCP) servers:

* **Antigravity CLI**: Operates via the Agent Client Protocol (ACP). The `agy-mcp-bridge` wraps `agy -m ... -p ...` and automatically detects whether Gentoo is using native host `gcloud` (Section 3B) or containerized Docker Compose `gcloud` (Section 3A), validating ADC tokens before invocation.

* **OpenAI Codex CLI**: The Codex CLI does not run an MCP server daemon directly; its `codex mcp` subcommand is a client configuration registry for managing external servers. Passing `/usr/bin/codex mcp-server` causes Codex to interpret `"mcp-server"` as a positional prompt instruction, execute it, and immediately terminate—closing the standard IO stream and triggering `MCP error -32000: Connection closed` in Continue, Claude, Antigravity, and Copilot. Running bare `/usr/bin/codex` launches the interactive terminal TUI. The `codex-mcp-bridge` wraps `codex exec -m <model> <prompt>` over standard-IO JSON-RPC, enabling reliable multi-agent delegation without process crashes.

### Step 5.1: Install `agy-mcp-bridge` (Auto-Detecting)

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

# Discover native binary locations

AGY_BIN = shutil.which("agy") or "/usr/bin/agy"
GCLOUD_BIN = shutil.which("gcloud") or "/usr/bin/gcloud"

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def check_adc():
    """Auto-detect native gcloud ebuild vs containerized Docker Compose."""
    # Method 1: Check native gcloud binary
    if os.path.exists(GCLOUD_BIN) or shutil.which("gcloud"):
        res = subprocess.run(
            [GCLOUD_BIN, "auth", "application-default", "print-access-token"],
            capture_output=True, text=True
        )
        return res.returncode == 0

    # Method 2: Check Docker Compose container
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

    # Ignore protocol notifications lacking request IDs
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

### Step 5.2: Install `codex-mcp-bridge`

Deploy the dedicated bridge that executes non-interactive `codex exec` calls over JSON-RPC stdio:

```bash
mkdir -p ~/.local/bin

cat << 'EOF' > ~/.local/bin/codex-mcp-bridge
#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys

# Locate native codex binary from dev-util/codex::guru

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

If internal academic instances (e.g., `lip.pt`, `example.org`) use private or enterprise root certificates, Node.js can be configured to trust your host certificates by adding `NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` to the `.env` files or exporting it in your environment.

#### Configuration Path Resolution and Compatibility Symlink

Depending on the release channel of the Google Antigravity VS Code extension (`Google.google-antigravity`), configuration discovery may check either `~/.gemini/config/mcp_config.json` or `~/.gemini/antigravity/mcp_config.json`. To guarantee automatic detection across all extension updates, create a symlink:

```bash
mkdir -p ~/.gemini/antigravity
ln -sf ~/.gemini/config/mcp_config.json ~/.gemini/antigravity/mcp_config.json

```

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

# Register OpenAI Codex (ChatGPT Plus) via codex-mcp-bridge

claude mcp add --scope user openai-codex-plus \
  -e CODEX_HOME="$HOME/.codex" \
  -- "$HOME/.local/bin/codex-mcp-bridge"

# Register OpenAI Codex (API Key) via codex-mcp-bridge

claude mcp add --scope user openai-codex-api \
  -e CODEX_HOME="$HOME/.codex-api" \
  -- "$HOME/.local/bin/codex-mcp-bridge"

# Register Native GitHub MCP Server via npx (inheriting GITHUB_PERSONAL_ACCESS_TOKEN from environment)

claude mcp add --scope user github-mcp \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-github

# Register GitLab.com (SaaS, 19.5+) via mcp-remote

claude mcp add --scope user gitlab-com \
  -- npx -y mcp-remote https://gitlab.com \
  --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security \
  --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_

# Register GitLab LIP (19.5.3) via mcp-remote

claude mcp add --scope user gitlab-lip \
  -- npx -y mcp-remote https://gitlab.lip.pt \
  --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security \
  --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_

# Register GitLab Admin LIP (19.5.3) via mcp-remote

claude mcp add --scope user gitlab-admin-lip \
  -- npx -y mcp-remote https://gitlab-admin.lip.pt \
  --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security \
  --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_

# Register GitLab Legacy (18.2.8) via @zereight/mcp-gitlab + .env

claude mcp add --scope user gitlab-legacy \
  -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'

# Register GitLab Admin Legacy (16 latest) via @zereight/mcp-gitlab + .env

claude mcp add --scope user gitlab-admin-legacy \
  -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'

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

[mcp_servers.gitlab-com]
command = "npx"
args = [
  "-y",
  "mcp-remote",
  "https://gitlab.com",
  "--header",
  "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
  "--header",
  "X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_"
]

[mcp_servers.gitlab-lip]
command = "npx"
args = [
  "-y",
  "mcp-remote",
  "https://gitlab.lip.pt",
  "--header",
  "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
  "--header",
  "X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_"
]

[mcp_servers.gitlab-admin-lip]
command = "npx"
args = [
  "-y",
  "mcp-remote",
  "https://gitlab-admin.lip.pt",
  "--header",
  "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
  "--header",
  "X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_"
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
      "command": "/home/YOUR_USERNAME/.local/bin/codex-mcp-bridge",
      "env": {
        "CODEX_HOME": "/home/YOUR_USERNAME/.codex"
      }
    },
    "gitlab-com": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://gitlab.com",
        "--header",
        "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
        "--header",
        "X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_"
      ]
    },
    "gitlab-lip": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://gitlab.lip.pt",
        "--header",
        "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
        "--header",
        "X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_"
      ]
    },
    "gitlab-admin-lip": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://gitlab-admin.lip.pt",
        "--header",
        "X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security",
        "--header",
        "X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_"
      ]
    },
    "gitlab-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
    },
    "gitlab-admin-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
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

  # 7. GitLab.com (SaaS, GitLab 19.5+) via Native Remote MCP
  - name: gitlab-com
    command: npx
    args:
      - -y
      - mcp-remote
      - https://gitlab.com
      - --header
      - X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security
      - --header
      - X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_

  # 8. GitLab LIP (Self-Hosted Production, GitLab 19.5.3) via Native Remote MCP
  - name: gitlab-lip
    command: npx
    args:
      - -y
      - mcp-remote
      - https://gitlab.lip.pt
      - --header
      - X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security
      - --header
      - X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_

  # 9. GitLab Admin LIP (Self-Hosted Admin, GitLab 19.5.3) via Native Remote MCP
  - name: gitlab-admin-lip
    command: npx
    args:
      - -y
      - mcp-remote
      - https://gitlab-admin.lip.pt
      - --header
      - X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security
      - --header
      - X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_

  # 10. GitLab Legacy (Self-Hosted Legacy, GitLab 18.2.8) via @zereight/mcp-gitlab + .env
  - name: gitlab-legacy
    command: sh
    args:
      - -c
      - set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab

  # 11. GitLab Admin Legacy (Self-Hosted Legacy Admin, GitLab 16.x) via @zereight/mcp-gitlab + .env
  - name: gitlab-admin-legacy
    command: sh
    args:
      - -c
      - set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab

```

Because `GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"` dynamically pulls from your exported environment, your `config.yaml` remains completely free of credentials and can be safely committed to git repositories or shared across machines.

---

--------------------------------------------------------------------------------

### Two-Stage Local Token & Cost Optimization Architecture (Continue + Antigravity)

When modernizing or migrating multi-repository codebases with dozens of configuration files and pipelines, passing raw repositories directly into frontier reasoning models wastes hundreds of thousands of metered tokens and risks context truncation.

To achieve maximum cost efficiency and prevent out-of-memory (OOM) failures on developer hardware (such as laptops with 4GB VRAM or desktops with 8GB VRAM), this environment implements a **strict two-stage processing pipeline**:
1. **Stage 1: Zero-Cost Local Pre-Processing (VS Code Continue + Ollama + CPU Reranker)**: Local hardware indexes, extracts, and pre-compresses raw files into dense Markdown architectural digests without spending a single cloud API token.
2. **Stage 2: High-Context Frontier Orchestration (VS Code Antigravity + Google AI Pro / Model Garden)**: Antigravity's 1M+ token context window ingests the clean local digest and orchestrates specialized MCP subagents (`claude-fable-gcp`, `gemini-carbon-gcp`, `openai-codex-plus`) to generate migration plans, audit infrastructure, and generate code.

#### 1. Hardware Allocation Strategy (Laptop vs. Office Desktop)

| Workload Phase | Machine & Hardware | Model Roles | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Phase 1: Local Extraction & Indexing** | Laptop (GTX 1650 4GB + 16GB RAM) | `qwen2.5-coder:3b` (GPU) + `nomic-embed-text` (CPU Container, port 11435) | Extract single-file purpose, triggers, endpoints, and dependencies into `/digest` files. |
| **Phase 1: Full-Workspace Synthesis** | Desktop (RTX 3050 8GB + 32GB RAM) | `qwen2.5-coder:7b` (GPU) + `bge-reranker-base` (CPU Container, port 8080) | Cross-repo `@codebase` semantic search and consolidation into master specification. |
| **Phase 2: Frontier MCP Orchestration** | Flat-Rate Cloud (Google AI Pro in Antigravity) | `gemini-3.1-pro` / `gemini-4-carbon` (1M+ context) | Dispatches tasks across MCP subagents; consumes 0 local VRAM for tool schemas. |

#### 2. Local Two-Stage RAG Indexing & `.continueignore` Setup

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
   ```
4. **Local CPU Cross-Encoder Reranking**: Continue retrieves 12 candidate chunks via vector search, scores their exact relevance using `bge-reranker-base` on `http://localhost:8080`, and forwards only the top 3 highest-scoring snippets to the model.

#### 3. Automated Workspace Summarization Workflow

Using custom Continue prompts, process large repositories in two discrete steps:
1. **File-Level Extraction (`/digest`)**: Highlight 3 to 5 entry files (e.g., `Jenkinsfile`, Dockerfiles, playbooks) and invoke `/digest` to generate a 400-word structured technical summary in `migration-prep/`.
2. **Cross-Repository Synthesis (`/synthesize`)**: Open a fresh Continue chat, attach the generated digest files using `@file`, and execute `/synthesize` to produce `migration-prep/MASTER_ARCHITECTURE_SPEC.md` (< 12,000 words).

#### 4. Frontier MCP Orchestration in Antigravity

Loading 11 MCP servers injects 15,000 to 30,000+ tokens of JSON tool schemas into the system prompt. Local 3B–7B models choke on this schema overhead. By contrast, **Google Antigravity powered by Gemini Pro / Gemini 4 Carbon** features a 1M+ token context window, natively supporting all MCP servers simultaneously:
1. **Open Antigravity Chat (`Ctrl+L`)**: Select `gemini-3.1-pro` (flat-rate Google AI Pro) or `gemini-4-carbon` (Google Cloud Agent Platform).
2. **Attach the Synthesized Specification**: Reference `@migration-prep/MASTER_ARCHITECTURE_SPEC.md` directly.
3. **Sequential Subagent Prompting**: Instruct Antigravity to route subtasks across the MCP mesh:
   * *Architecture & Phased Planning*: Dispatched to `claude-fable-gcp` (`claude-fable-5-2`).
   * *Infrastructure Risk & Dependency Audit*: Dispatched to `gemini-carbon-gcp` (`gemini-4-carbon`).
   * *Code Generation & Test Templates*: Dispatched to `openai-codex-plus` (`ask_codex`).
   * *Repository Synchronization*: Pushed or queried via `gitlab-com`, `gitlab-lip`, or `github-mcp`.

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

Verify that all 11 configured servers (`gemini-carbon-gcp`, `claude-fable-gcp`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`, `gitlab-com`, `gitlab-lip`, `gitlab-admin-lip`, `gitlab-legacy`, `gitlab-admin-legacy`) display `Connected`.

### Step 10.3: Inspect Live Indicators and Utilize MCP Servers in VS Code Antigravity

#### Understanding the Antigravity UI Model

In the Google Antigravity VS Code extension, MCP servers do **not** appear as separate explorer sidebars, file trees, or dedicated window panes. Instead, they are embedded directly into the Antigravity agent execution harness as background callable tools.

#### Viewing and Inspecting MCP Servers in the UI

1. **The `/mcp` Slash Command**:
   * Open the Antigravity chat panel by clicking the Antigravity icon in the Activity Bar or pressing **`Ctrl+L`**.
   * In the chat prompt input, type **`/mcp`** and press **Enter**.
   * Antigravity opens a live diagnostic dashboard displaying connection status rings for every registered server (`gemini-carbon-gcp`, `claude-fable-gcp`, `claude-teams`, `openai-codex-plus`, `openai-codex-api`, `github-mcp`):
     * **Green Ring**: Server is healthy, connected, and tool schemas are successfully registered.
     * **Amber Ring**: Server process is initializing or undergoing protocol handshake.
     * **Red Ring**: Server process terminated, binary not found, or JSON-RPC handshake failed. Clicking the server reveals stdout/stderr logs.

2. **The Panel Header Tools / MCP Icon**:
   * In the top-right header of the Antigravity chat panel, click the **Tools / Plug icon** to open the registered tools modal and inspect active capabilities.

#### How to Use MCP Servers in Chat Conversations

* **Explicit Subagent Delegation**:
  Prompt the agent directly to route requests through specific subagent tools:
  * *"Ask `gemini-carbon-gcp` to audit this system architecture using model `gemini-4-carbon`."*
  * *"Have `claude-fable-gcp` review the diff proposed by `gemini-carbon-gcp` before applying changes."*
  * *"Use `openai-codex-plus` (via `ask_codex`) to provide a second-opinion refactoring for this module."*
  * *"Query `github-mcp` to list open pull requests and recent commit issues in this repository."*
* *"Query `gitlab-com` using tool `glcom_list_projects` to check my recent repositories."*
* *"Using `gitlab-lip` (tool `gllip_list_merge_requests`), review open MRs targeting production."*
* *"Inspect the latest CI pipeline failures on `gitlab.legacy.example.org` via `gitlab-legacy` (tool `gllegacy_list_pipelines`)."*
* *"Search recent issues on Admin GitLab using `gitlab-admin-legacy` (tool `gladminleg_list_issues`)."*
* **Autonomous Tool Execution**:
  When prompted with complex workflows (e.g. cross-repository analysis or deep static audits), the active Antigravity model autonomously selects and executes the appropriate MCP tool, surfacing an approval or execution card in the conversation stream.

#### Troubleshooting: If `/mcp` is Empty or Servers Fail to Connect

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

### Step 10.4: Verify Secondary Extension Status (Claude Code, Continue & Copilot)

1. **Claude Code**: Open Claude Code sidebar (**`Ctrl+Shift+P`** → `Claude Code: Open in Side Bar`) and execute `/mcp` in the prompt box. All five servers should report `Connected`.

2. **Continue Extension**: Open the Continue sidebar (**`Ctrl+L`**). The configured MCP tools will display active status in the prompt tool picker.

3. **GitHub Copilot Chat**: Open Copilot Chat (**`Ctrl+Alt+I`**) and verify tool availability.

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