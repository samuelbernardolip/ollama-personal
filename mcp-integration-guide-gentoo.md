# Complete MCP Integration Guide for VS Code on Gentoo Linux: Antigravity, Claude Code, OpenAI Codex, GitHub Copilot, Continue, and GitLab Multi-Instance Mesh (Enterprise Edition v10)

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
| **GitHub Copilot Models** | Antigravity / Claude / Continue | Local Stdio Bridge (`github-models-mcp`) | `~/.config/antigravity-mcp/` | `github-models` | Copilot Subscription ($0 marginal / `auto` default) |
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

# Verify Copilot CLI runtime
~/.local/share/gh/copilot/copilot --version || gh copilot --version

# 6. Initialize Isolated Credential Directory for Legacy and Remote GitLab Instances (PAT)
mkdir -p ~/.config/antigravity-mcp ~/.mcp-auth
chmod 700 ~/.config/antigravity-mcp ~/.mcp-auth

# Configure gitlab.com (SaaS, 19.5+)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-com.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_GITLAB_COM_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-com.env

# Configure gitlab.modern.example.org (19.5.3 Production)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-modern.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_MODERN_PROD_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-modern.env

# Configure gitlab-admin.modern.example.org (19.5.3 Admin)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-admin-modern.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_MODERN_ADMIN_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-admin-modern.env

# Configure gitlab.legacy.example.org (v18.2.8 Legacy)
cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-legacy.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_LEGACY_TOKEN
GITLAB_API_URL=https://gitlab.legacy.example.org
GITLAB_TOOL_PREFIX=gllegacy_
GITLAB_TOOLSETS=issues,merge_requests,repositories,pipelines,wiki
# Optional: Enforce strict read-only mode if write operations should be blocked:
# GITLAB_PERMISSION_MODE=readonly
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-legacy.env

# Configure gitlab-admin.legacy.example.org (v16 latest Legacy Admin)
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

### Step 5.3: Install `github-models-mcp` (GitHub Copilot Models Bridge)

The standard `@modelcontextprotocol/server-github` (`github-mcp`) interfaces exclusively with GitHub's REST and GraphQL APIs for repository manipulation (pull requests, issues, branch commits, and code search). It exposes **zero endpoints for language model completions or inferences**. Furthermore, GitHub has retired the standalone public free tier of GitHub Models (`models.github.ai`), routing all personal model inference through authenticated **GitHub Copilot subscriptions**.

To expose your active GitHub Copilot model catalog (`claude-sonnet-5.5`, `grok-4.7`, `mai-code-2`, `mai-code-2-flash`, `openai/gpt-4o`, `openai/gpt-4o-mini`, `kimi-k3`) directly to Google Antigravity, Claude Code, and Continue as a callable subagent tool, install the dedicated standard-IO bridge **`github-models-mcp`**.

Deploy `~/.local/bin/github-models-mcp`:

```python
#!/usr/bin/env python3
"""
github-models-mcp - Standard-IO Model Context Protocol Bridge for GitHub Copilot Models.
Discovers available models dynamically from the official Copilot CLI via ACP,
caches catalog with configurable TTL, and exposes ask_github_model and list_github_models.
"""

import json
import os
import shutil
import subprocess
import sys
import time

CACHE_FILE = os.path.expanduser("~/.config/antigravity-mcp/models_cache.json")
DEFAULT_CACHE_TTL = 3600  # 1 hour

def get_cache_ttl():
    try:
        return int(os.environ.get("GITHUB_MODELS_CACHE_TTL", DEFAULT_CACHE_TTL))
    except ValueError:
        return DEFAULT_CACHE_TTL

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def locate_copilot_cli():
    candidate = os.path.expanduser("~/.local/share/gh/copilot/copilot")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate
    resolved = shutil.which("copilot")
    if resolved:
        return resolved
    return None

def fetch_available_models(copilot_bin):
    if os.path.exists(CACHE_FILE):
        try:
            mtime = os.path.getmtime(CACHE_FILE)
            if (time.time() - mtime) < get_cache_ttl():
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if isinstance(cached, list) and len(cached) > 0:
                        return cached
        except Exception:
            pass

    discovered_models = []
    try:
        proc = subprocess.Popen(
            [copilot_bin, "--acp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "antigravity-mcp", "version": "1.0"}}}
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()

        models_req = {"jsonrpc": "2.0", "id": 2, "method": "models/list", "params": {}}
        proc.stdin.write(json.dumps(models_req) + "\n")
        proc.stdin.flush()

        proc.stdin.close()
        for line in proc.stdout:
            try:
                resp = json.loads(line)
                if resp.get("id") == 2 and "result" in resp:
                    items = resp["result"].get("models", [])
                    discovered_models = [m.get("id") or m.get("name") for m in items if m.get("id") or m.get("name")]
                    break
            except json.JSONDecodeError:
                continue
        proc.terminate()
    except Exception:
        pass

    if not discovered_models:
        discovered_models = [
            "auto",
            "claude-sonnet-5.5",
            "grok-4.7",
            "mai-code-2",
            "mai-code-2-flash",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "kimi-k3"
        ]

    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(discovered_models, f, indent=2)
    except Exception:
        pass

    return discovered_models

def run():
    copilot_bin = locate_copilot_cli()
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method")
        req_id = req.get("id")

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
            models = fetch_available_models(copilot_bin) if copilot_bin else ["auto"]
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "ask_github_model",
                            "description": "Query GitHub Copilot model inference with your active Copilot subscription.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string", "description": "The coding prompt or instruction"},
                                    "model": {
                                        "type": "string",
                                        "enum": models,
                                        "default": "auto",
                                        "description": "Model identifier. Defaults to 'auto' for cost-discounted model selection."
                                    }
                                },
                                "required": ["prompt"]
                            }
                        },
                        {
                            "name": "list_github_models",
                            "description": "List all active models supported by your GitHub Copilot subscription.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "refresh": {"type": "boolean", "description": "Force cache invalidation"}
                                }
                            }
                        }
                    ]
                }
            })
        elif method == "tools/call":
            params = req.get("params", {})
            tname = params.get("name")
            args = params.get("arguments", {})

            if tname == "list_github_models":
                if args.get("refresh") and os.path.exists(CACHE_FILE):
                    try:
                        os.remove(CACHE_FILE)
                    except Exception:
                        pass
                models = fetch_available_models(copilot_bin) if copilot_bin else []
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"active_models": models}, indent=2)}],
                        "isError": False
                    }
                })
            elif tname == "ask_github_model":
                prompt = args.get("prompt", "")
                chosen_model = args.get("model") or "auto"
                if not copilot_bin:
                    send({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": "Copilot CLI not found. Run 'gh auth login --web -s copilot'."}],
                            "isError": True
                        }
                    })
                    continue

                cmd = [copilot_bin, "exec"]
                if chosen_model != "auto":
                    cmd.extend(["-m", chosen_model])
                cmd.append(prompt)

                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    out = res.stdout if res.returncode == 0 else f"Error ({res.returncode}): {res.stderr}"
                    send({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": out}],
                            "isError": res.returncode != 0
                        }
                    })
                except Exception as e:
                    send({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Execution failed: {str(e)}"}],
                            "isError": True
                        }
                    })
            else:
                send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": req_id, "result": {}})

if __name__ == "__main__":
    run()
```

Make the script executable:

```bash
chmod +x ~/.local/bin/github-models-mcp
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

# Register GitHub Models via Local Copilot Bridge
claude mcp add --scope user github-models \
  -- "/home/YOUR_USERNAME/.local/bin/github-models-mcp"

# Register GitLab.com (SaaS, 19.5+) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-com \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-com.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-com.env"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_'

# Register GitLab LIP (19.5.3) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-lip \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-modern.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-modern.env"; set +a && exec npx -y mcp-remote https://gitlab.modern.example.org/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_'

# Register GitLab Admin LIP (19.5.3) via mcp-remote + Bearer Header
claude mcp add --scope user gitlab-admin-lip \
  -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-admin-modern.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-admin-modern.env"; set +a && exec npx -y mcp-remote https://gitlab-admin.modern.example.org/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_'

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
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-modern.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-modern.env\"; set +a && exec npx -y mcp-remote https://gitlab.modern.example.org/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_\""
]

[mcp_servers.gitlab-admin-lip]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-admin-modern.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-admin-modern.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.modern.example.org/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_\""
]

[mcp_servers.gitlab-legacy]
command = "sh"
args = [
  "-c",
  "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
]

[mcp_servers.gitlab-admin-legacy]
command = "sh"
args = [
  "-c",
  "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
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
        "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-com.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\"
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

  # 7. GitHub Models MCP Server (Copilot AI Inference via Local Bridge)
  - name: github-models
    command: /home/YOUR_USERNAME/.local/bin/github-models-mcp
    args: []

  # 8. GitLab.com (SaaS, GitLab 19.5+) via Native Remote MCP + Bearer Header
  - name: gitlab-com
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-com.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-com.env"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_

  # 9. GitLab LIP (Self-Hosted Production, GitLab 19.5.3) via Native Remote MCP + Bearer Header
  - name: gitlab-lip
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-modern.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-modern.env"; set +a && exec npx -y mcp-remote https://gitlab.modern.example.org/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_

  # 10. GitLab Admin LIP (Self-Hosted Admin, GitLab 19.5.3) via Native Remote MCP + Bearer Header
  - name: gitlab-admin-lip
    command: sh
    args:
      - -c
      - set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-admin-modern.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-admin-modern.env"; set +a && exec npx -y mcp-remote https://gitlab-admin.modern.example.org/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_

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

### Step 7.3: Strategy to Optimize Token Costs with Local RAG and Antigravity Orchestration

Running small local models (3B–7B) directly as autonomous orchestrators across all 12 MCP servers is ineffective because loading the complete server catalog injects **15,000 to 30,000+ tokens of raw JSON tool schemas** into every turn. On consumer GPUs (GTX 1650 4GB or RTX 3050 8GB), tool schemas alone exhaust the KV cache, causing severe generation latency and malformed tool-call syntax.

The optimal architecture decouples **zero-cost local data preparation in Continue** from **high-context frontier orchestration in Google Antigravity**:
1. **Stage 1: Zero-Cost Local Pre-Processing (VS Code Continue + Ollama + CPU Reranker)**: Local hardware indexes, extracts, and pre-compresses raw files into dense Markdown architectural digests without spending a single cloud API token.
2. **Stage 2: High-Context Frontier Orchestration (VS Code Antigravity + Google AI Pro / Model Garden)**: Antigravity's 1M+ token context window ingests the clean local digest and orchestrates specialized MCP subagents (`claude-fable-gcp`, `gemini-carbon-gcp`, `openai-codex-plus`, `github-models`, and GitLab servers) to execute migration plans, code generation, and repository updates.

#### 1. Hardware Allocation Strategy (Laptop vs. Office Desktop)

| Workload Phase | Machine & Hardware | Model Roles | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Phase 1: Local Extraction & Indexing** | Laptop (GTX 1650 4GB + 16GB RAM) | `Laptop-Worker-3B` (`qwen2.5-coder:3b-instruct-q8_0`, port 11434) + `nomic-embed-text` (CPU Container, port 11435) | Extract single-file purpose, triggers, endpoints, and dependencies into `/digest` files. Zero thinking-token overhead (<think> disabled) to maximize speed. |
| **Phase 1: Full-Workspace Synthesis** | Desktop (RTX 3050 8GB + 32GB RAM) | `Office-Synthesizer-7B` (`qwen2.5-coder:7b-instruct-q4_K_M`, port 11434) + `bge-reranker-base` (CPU Container, port 8080) | Cross-repo `@codebase` semantic search and consolidation into master specification with reasoning distillation. |
| **Phase 2: Frontier MCP Orchestration** | Flat-Rate Cloud (Google AI Pro in Antigravity) | `gemini-3.1-pro` / `gemini-4-carbon` (1M+ context) | Dispatches tasks across MCP subagents; consumes 0 local VRAM for tool schemas. |

#### 2. How `nFinal` Works & Passing Reranked Chunks to Prompts

Under the `context:` block in `~/.continue/config.yaml`, the two-stage RAG pipeline is configured as follows:

```yaml
context:
  - provider: file
  - provider: tree
  - provider: open
  - provider: diff
  - provider: codebase
    params:
      nRetrieve: 12   # Candidate chunks fetched from LanceDB vector store
      nFinal: 3       # Top scored chunks sent to the LLM after CPU cross-encoder reranking
      useReranking: true
```

#### How the Pipeline Processes Your Query:

1. **Initial Vector Retrieval (`nRetrieve: 12`)**: When you invoke `@codebase`, Continue embeds your query using `embeddingsProvider` (`nomic-embed-text` on CPU port 11435) and retrieves the top 12 candidate snippets from local LanceDB (`~/.continue/index/`).
2. **Cross-Encoder Scoring**: Continue sends the 12 candidate chunks along with your query to `rerank-server` on port 8080 (`BAAI/bge-reranker-base`). The cross-encoder evaluates full attention across `[query, chunk]` pairs and assigns precise semantic relevance scores (0.0 to 1.0).
3. **Filtering to Top Chunks (`nFinal: 3`)**: Continue discards low-scoring noise and selects **only the top 3 scored chunks** (~1,500 tokens).
4. **Passing to Custom Prompts**: When a custom slash command (such as `/antigravity-spec-laptop` or `/antigravity-spec-workstation`) is executed in Continue Chat (**`Ctrl+L`**), Continue automatically binds these top 3 reranked chunks directly into the template's `{{ input }}` variable:
   ```text
   @codebase /antigravity-spec-laptop modernize the Jenkins quality verification pipeline
   ```
   The local model analyzes only these curated, high-relevance chunks and outputs a structured execution brief for Antigravity without seeing irrelevant files.

#### 3. Generative Orchestration Prompts

#### Prompt A: Laptop Worker (Zero Thinking-Token Overhead / 4GB VRAM)

Configured in `~/.continue/config.yaml` as `/antigravity-spec-laptop`:

```yaml
  - name: antigravity-spec-laptop
    description: "Generate Antigravity orchestration brief via Local RAG (Zero Thinking Overhead, 4GB VRAM)"
    prompt: |
      You are a technical lead preparing a strict, token-efficient execution brief for the Google Antigravity orchestrator.
      Analyze ONLY the retrieved codebase and documentation context below (reranked chunks). Do not invent file paths, symbols, or APIs.
      Output ONLY a copy-pasteable prompt for Antigravity structured exactly as follows (no thinking tags, no conversational fluff):

      ### 1. Goal & Grounded Scope
      - **Objective**: [1 clear sentence defining the deliverable]
      - **Target Files & Lines**: [Exact file paths and line ranges from retrieved context]
      - **Constraints**: [Key API signatures, versions, or library rules]

      ### 2. Multi-Agent MCP Routing Plan (Cost-Optimized)
      Instruct the Antigravity Orchestrator (`gemini-3.1-pro` flat-rate default, or `gemini-3.8-flash`) to execute sequentially:
      - **Stage 1 — Architecture & Edge-Case Check (Deep Reasoning)**:
        - Delegate via MCP to: `claude-fable-gcp` (`claude-fable-5-2`) or `gemini-carbon-gcp` (`gemini-4-carbon-medium`).
        - Rule: Pass ONLY file signatures and error logs; require a bulleted diff plan (<250 words).
      - **Stage 2 — Implementation (Coding)**:
        - Delegate via MCP to: `openai-codex-plus` (`ask_codex`) or `github-models` (model `auto` / `claude-sonnet-5.5`).
        - Rule: Apply exact edits to the target files in Section 1.
      - **Stage 3 — Tests & Verification (Quota-Saving)**:
        - Delegate via MCP to: `github-models` (model `auto` via Copilot quota) or `gitlab-com` / `gitlab-lip` CI tools.
        - Rule: Generate unit tests and verify build.

      ### 3. Exit Criteria
      - [Exact test or build command to run]
      - **Token Guardrail**: Pass only diffs and outlines between MCP subagents—never full raw files.

      User Request: {{ input }}
```

#### Prompt B: Workstation Synthesizer (Reasoning-Capable Distillation / 8GB VRAM)

Configured in `~/.continue/config.yaml` as `/antigravity-spec-workstation`:

```yaml
  - name: antigravity-spec-workstation
    description: "Generate dynamic, cache-aware MCP orchestration brief via Local RAG (Reasoning Distillation, 8GB VRAM)"
    prompt: |
      You are a principal technical architect preparing a token-minimized, cache-aware execution brief for Google Antigravity.
      Analyze ONLY the retrieved codebase and documentation context below (reranked chunks). Do not invent file paths, symbols, or APIs.

      Output ONLY a copy-pasteable prompt for Antigravity structured exactly as follows:

      ### 1. Grounded Task Context (From Local RAG)
      - **Objective**: [1 clear sentence defining the exact deliverable]
      - **Target Files & Line Ranges**: [Exact paths, functions, and lines from retrieved context]
      - **Technical & Doc Constraints**: [Required API signatures, schemas, or library rules]
      - **Task Profile**:
        - *Work Type*: [Boilerplate/CRUD | Focused Feature | Complex Refactor/Bugfix | System Architecture | Docs/Tests]
        - *Complexity & Reasoning Depth*: [Low | Medium | High]
        - *Expected Output Volume*: [Low (<300 tokens) | Medium (300–1,500 tokens) | High (>1,500 tokens)]

      ### 2. Phase 0: MCP Model Discovery & Local Cache Check
      Before routing any subtasks, execute this zero-waste discovery step:
      1. Check if `.agents/mcp_models_cache.json` exists in the workspace and is **less than 24 hours old**.
      2. **If valid cache exists**: Read `.agents/mcp_models_cache.json` directly and skip querying MCP servers.
      3. **If missing or stale**: Query each active MCP server (`github-models`, `openai-codex-api`, `claude-fable-gcp`, `gemini-carbon-gcp`) for currently available model IDs, context limits, and pricing tiers. Save the normalized result to `.agents/mcp_models_cache.json`.

      ### 3. Dynamic Cost-to-Capability Routing Matrix
      Using the verified models, select the optimal model per stage based on Task Type × Output Volume × Cost Ratio:
      - **Orchestration & Routing**: `gemini-3.1-pro` (Antigravity default flat-rate) or `gemini-3.8-flash`. Pass diffs/IDs only, never raw files.
      - **Deep Reasoning / Complex Refactor (Conditional)**: `claude-fable-5-2` (on GCP Model Garden) or `gemini-4-carbon` (on Vertex AI ADC). Output capped at <250 tokens diff plan.
      - **Focused Code Implementation**: `gpt-5.3-codex` via `openai-codex-plus` or `github-models` (model `auto` for discounted routing). Keep prompt <272K tokens.
      - **Docs & Test Generation (2-Step Split)**:
        - *Step A (Planner)*: `gemini-3.8-flash` emits <150-token outline of test cases and doc sections.
        - *Step B (Writer)*: `github-models` (Copilot quota, $0 marginal) or cheapest writer expands full Markdown docs and tests.

      ### 4. Execution & Verification Protocol
      1. **Dynamic Selection Log**: Print a compact 4-line summary mapping each stage to the chosen model and justification.
      2. **Sequential Execution**: Run only stages required by the Task Profile.
      3. **Verify & Self-Heal**: Run [exact test or build command]. Route stack traces to coder subagent; escalate to reasoning model only if initial fix fails.
      4. **Hygiene**: Ensure `.agents/mcp_models_cache.json` is listed in both `.gitignore` and `.continueignore`.

      User Request: {{ input }}
```

#### 4. Three-Phase Cost-Optimization Workflow

1. **Phase 1: Local Extraction (`/digest`)**:
   * Mode: **Chat Mode** in Continue (`Ctrl+L`).
   * Select 3–5 related files (or drag the folder) into Continue Chat and run `/digest`.
   * Save outputs to `migration-prep/01-ci.md`, `02-auth.md`, etc.
2. **Phase 2: Master Synthesis (`/synthesize`)**:
   * Attach the collected digests (`@File migration-prep/01-ci.md`, etc.) and run `/synthesize`.
   * Save output as `migration-prep/MASTER_ARCHITECTURE_SPEC.md` (< 12,000 words).
3. **Phase 3: Frontier Multi-Agent Orchestration in Antigravity**:
   * Open **Google Antigravity (`Ctrl+L`)** in **Agent** mode on your **Google AI Pro** (`gemini-3.1-pro`) subscription.
   * Attach `@migration-prep/MASTER_ARCHITECTURE_SPEC.md` and execute the generated orchestration brief across your MCP backends.


---

### Step 7.4: Automated Multi-IDE Ignore & Context Synchronization (`genignore.py`, `update-ai-ignore.sh`, and `pre-commit`)

Each AI assistant in your multi-agent workbench utilizes distinct configuration formats to restrict file indexing and prevent sensitive data exposure:
* **Continue**: Reads `.continueignore` (native glob patterns).
* **Antigravity**: Reads `.agentignore` (native glob patterns).
* **Claude Code**: Enforces permissions via `permissions.deny` with `Read(...)` rules in `.claude/settings.json`, alongside general project instructions in `CLAUDE.md`.
* **GitHub Copilot**: Enforces exclusions via `files.exclude` and `search.exclude` dictionaries in `.vscode/settings.json`, alongside workflow guidelines in `.github/copilot-instructions.md`.
* **OpenAI Codex**: Reads instruction-based exclusion guidelines in `AGENTS.md` (supplementing its native `.gitignore` support).

To automate the synchronization of exclusion rules across all five environments whenever `.gitignore` or `.gitattributes` change, deploy this unified automation toolchain.

#### 1. The Multi-Provider Generator Script (`genignore.py`)

Deploy `genignore.py` in your repository root (or `scripts/genignore.py`):

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

Make `genignore.py` executable:
```bash
chmod +x genignore.py
```

#### 2. The Git-Aware Shell Wrapper (`update-ai-ignore.sh`)

Deploy `update-ai-ignore.sh` to handle uncommitted change detection and automated staging:

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

Make the wrapper executable:
```bash
chmod +x update-ai-ignore.sh
```

#### 3. Automated Git Pre-Commit Hook (`pre-commit`)

Install `pre-commit` into `.git/hooks/pre-commit` to automatically synchronize and re-stage AI ignore files whenever `.gitignore` or `.gitattributes` are modified in a commit:

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

Make the hook executable:
```bash
chmod +x .git/hooks/pre-commit
```

#### 4. Installation and Common Workflows

#### Initializing Provider Files in a New Repository:

```bash
# Generate all missing provider files with safe defaults
./genignore.py --generate-ignore

# Or force overwrite if re-initializing from scratch
./genignore.py --generate-ignore --overwrite
```

#### Appending Custom Project Exclusions:

```bash
# Append custom binary and sensitive patterns without duplicating entries
./genignore.py --generate-ignore --append "*.rpm" "*.tar.gz" "*.png" "RPM-GPG-KEY-*"
```

#### Running the Shell Wrapper with Auto-Staging:

```bash
# Synchronize only if .gitignore or .gitattributes changed, and stage updated files
./update-ai-ignore.sh --stage

# Force run unconditionally and stage updated provider files
./update-ai-ignore.sh --force --stage
```


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
