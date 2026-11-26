# Complete MCP Integration Guide for VS Code on Gentoo Linux: Antigravity, Claude Code, OpenAI Codex, GitHub Copilot, Continue, and GitLab Multi-Instance Mesh (Gentoo Public Edition v10)

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
| **Google AI Pro** | Antigravity IDE / `agy-pro` | Browser OAuth (Google SSO) | `~/.gemini/` | `google-pro` | Flat monthly subscription (€0 additional) |
| **Google Cloud Agent Platform** | `google-cloud-mcp` / `agy-gcp` | ADC Token via Native gcloud | `~/.config/gcloud/` | `google-cloud` | Pay-as-you-go per token on GCP project |
| **Anthropic Teams** | Claude Code IDE / `claude-teams` | Browser OAuth (Anthropic SSO) | `~/.claude/` | `claude-teams` | Flat team seat license |
| **Google Cloud Model Garden (Claude)** | `claude-gcp-mcp` / Vertex AI | Vertex AI ADC Token | `~/.claude-gcp/` | `claude-gcp` | Pay-as-you-go per token on GCP project |
| **OpenAI ChatGPT Plus** | Codex IDE / `codex-plus` | Terminal OAuth (ChatGPT Web) | `~/.codex/` | `openai-codex-plus` | Flat €23/month (subject to cancellation) |
| **OpenAI API** | Codex IDE / `codex-api` | Secret API Key (`sk-proj-...`) | `~/.codex-api/` | `openai-codex-api` | Pay-as-you-go per token balance |
| **GitHub Copilot** | Copilot Chat VS Code | GitHub OAuth Token | `~/.config/github-copilot/` | `github-mcp` | Included via Student Pack / Monthly seat |
| **GitHub Copilot Models** | Copilot CLI (`copilot --acp`) | Active GitHub Copilot Subscription | `~/.config/antigravity-mcp/` | `github-models` | Discounted `auto` routing / Included in seat |
| **Continue Local Vector DB & Reranker** | Continue Extension / LanceDB | Local CPU Embeddings & Cross-Encoder | `~/.continue/index/` | `continue-rag` | 100% Offline / Zero VRAM / €0 cost |
| **GitLab.com** | Antigravity / Claude / Codex / Copilot / Continue | Native Remote MCP (`mcp-remote` via Bearer PAT / OAuth) | `~/.mcp-auth/` | `gitlab-com` | Included via SaaS Free/Premium (`glcom_` prefix) |
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

# 6. Initialize Isolated Credential Directory for Legacy GitLab Instances (PAT)

mkdir -p ~/.config/antigravity-mcp ~/.mcp-auth
chmod 700 ~/.config/antigravity-mcp ~/.mcp-auth

# Configure GitLab.com (SaaS, 19.5+) Bearer PAT

cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-com.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_GITLAB_COM_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-com.env

# Configure GitLab LIP (19.5.3 Production) Bearer PAT

cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-lip.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_LIP_PROD_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-lip.env

# Configure GitLab Admin LIP (19.5.3 Admin) Bearer PAT

cat << 'EOF' > ~/.config/antigravity-mcp/gitlab-admin-lip.env
GITLAB_PERSONAL_ACCESS_TOKEN=glpat-YOUR_LIP_ADMIN_TOKEN
EOF
chmod 600 ~/.config/antigravity-mcp/gitlab-admin-lip.env

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

# Optional: Configure continue-rag.env for custom vector index or reranker endpoints

cat << 'EOF' > ~/.config/antigravity-mcp/continue-rag.env
OLLAMA_EMBED_URL=http://localhost:11435/api/embeddings
RERANK_URL=http://localhost:8080/rerank
RERANK_MODEL=BAAI/bge-reranker-base
LANCEDB_DIR=$HOME/.continue/index/lancedb
EOF
chmod 600 ~/.config/antigravity-mcp/continue-rag.env

---

## 5. Universal Python MCP Bridges: Antigravity, Claude, Codex & Copilot

All external CLI engines and custom RAG databases interface with VS Code extensions via dedicated Model Context Protocol (MCP) standard-IO bridges. Each bridge implements:
1. **Dynamic Model Discovery**: Queries the upstream CLI engine (`agy models`, `codex models`, `copilot --acp`) to auto-detect models available on your active subscription.
2. **Disk-Backed JSON Caching**: Caches the dynamic model list in `~/.config/antigravity-mcp/<provider>_models_cache.json` with a 3600-second (1-hour) configurable TTL to eliminate repetitive discovery overhead.
3. **On-Demand Cache Invalidation**: Supports `{"refresh": true}` on listing tools to invalidate disk cache immediately.
4. **Isolated Process Sandboxing**: Prevents parent-child recursion deadlocks during Antigravity tool calls.

### Step 5.1: Install `google-cloud-mcp` (Google Cloud Agent Platform ADC Bridge)

The `google-cloud-mcp` bridge (formerly `agy-mcp-bridge`) provides model-agnostic access to all Google Cloud Agent Platform models (`gemini-4-carbon-medium`, `gemini-4-carbon-high`, `gemini-4-carbon-low`, `claude-opus-5-5`, `claude-sonnet-5-5`, `gemini-3.1-pro`) via Application Default Credentials (ADC).

Save the script to `~/.local/bin/google-cloud-mcp`:

```python
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

```

Make executable:
```bash
chmod +x ~/.local/bin/google-cloud-mcp
```

### Step 5.2: Install `codex-mcp-bridge` (OpenAI Codex CLI Bridge)

Wraps non-interactive `codex exec` calls over JSON-RPC standard IO, dynamically discovering all available OpenAI models (`gpt-5.3-codex`, `gpt-6.1`, `gpt-5.3-codex-mini`, `o3`, `gpt-4o`) and caching the catalog.

Save to `~/.local/bin/codex-mcp-bridge`:

```python
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

```

Make executable:
```bash
chmod +x ~/.local/bin/codex-mcp-bridge
```

### Step 5.3: Install `github-models-mcp` (GitHub Copilot Models Bridge)

Connects to the official GitHub Copilot CLI executable (`copilot` or `gh copilot`) using Agent Client Protocol (ACP) discovery, caches available models, and defaults to `auto` for discounted cost routing.

Save to `~/.local/bin/github-models-mcp`:

```python
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

```

Make executable:
```bash
chmod +x ~/.local/bin/github-models-mcp
```

### Step 5.4: Install `continue-rag-mcp` (Continue Vector DB & Local Reranker Bridge)

Exposes Continue's local LanceDB vector database (`~/.continue/index/`) and the CPU cross-encoder reranker (`rerank_server.py` on port `8080`) as an MCP server.

Save to `~/.local/bin/continue-rag-mcp`:

```python
#!/usr/bin/env python3
"""
continue-rag-mcp - Local Vector Database & Python Reranker MCP Server
Implements Custom Code RAG per Continue Docs (https://docs.continue.dev/guides/custom-code-rag)
Connects to local LanceDB index, vectors via ollama-embed-cpu, and reranks via Python rerank-server.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

HOME = os.path.expanduser("~")
LANCEDB_DIR = os.getenv("LANCEDB_DIR", os.path.join(HOME, ".continue", "index", "lancedb"))
EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11435/api/embeddings")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
RERANK_URL = os.getenv("RERANK_URL", "http://localhost:8080/rerank")

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def get_query_embedding(query):
    """Generate query vector embedding via Ollama CPU instance (port 11435)."""
    payload = json.dumps({"model": EMBED_MODEL, "prompt": query}).encode("utf-8")
    req = urllib.request.Request(
        EMBED_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("embedding", [])

def rerank_candidate_chunks(query, candidates, top_k):
    """Rerank candidate snippets using the local Python Cross-Encoder on port 8080."""
    if not candidates:
        return []
    texts = [c["text"] for c in candidates]
    payload = json.dumps({"query": query, "texts": texts}).encode("utf-8")
    req = urllib.request.Request(
        RERANK_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            scores = json.loads(resp.read().decode("utf-8"))
            for item in scores:
                idx = item.get("index", 0)
                if idx < len(candidates):
                    candidates[idx]["score"] = item.get("score", 0.0)
            candidates.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return candidates[:top_k]
    except Exception:
        for c in candidates:
            c["score"] = "unranked (reranker offline)"
        return candidates[:top_k]

def search_lancedb(query, limit=3, table_name="code_chunks"):
    """Query LanceDB vector store and pass candidates to the local reranker."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return [{
                "filename": "NOTE",
                "text": f"LanceDB directory '{LANCEDB_DIR}' not yet indexed. Run codebase indexing in Continue first.",
                "score": 0.0
            }]
        db = lancedb.connect(LANCEDB_DIR)
        table_names = db.table_names()
        if not table_names:
            return [{
                "filename": "NOTE",
                "text": f"No tables found in LanceDB database at '{LANCEDB_DIR}'. Index repository files first.",
                "score": 0.0
            }]
        target_table = table_name if table_name in table_names else table_names[0]
        table = db.open_table(target_table)
        
        retrieve_pool = max(limit * 4, 15)
        raw_results = table.search(query).limit(retrieve_pool).to_list()
        
        candidates = []
        for r in raw_results:
            candidates.append({
                "filename": r.get("filename", "unknown"),
                "text": r.get("text", "")
            })
        
        return rerank_candidate_chunks(query, candidates, top_k=limit)
    except ImportError:
        return [{
            "filename": "DEPENDENCY_NOTICE",
            "text": "Python 'lancedb' package is not installed. Install via: pip install lancedb",
            "score": 0.0
        }]
    except Exception as e:
        return [{
            "filename": "ERROR",
            "text": f"Error querying vector database: {str(e)}",
            "score": 0.0
        }]

def get_file_chunks(filename, table_name="code_chunks"):
    """Fetch all indexed chunks belonging to a specific file path."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return f"LanceDB directory '{LANCEDB_DIR}' not found."
        db = lancedb.connect(LANCEDB_DIR)
        table_names = db.table_names()
        if not table_names:
            return "No indexed tables available in LanceDB."
        target_table = table_name if table_name in table_names else table_names[0]
        table = db.open_table(target_table)
        
        results = table.where(f"filename = '{filename}'").to_list()
        if not results:
            base = os.path.basename(filename)
            results = [r for r in table.to_list() if base in r.get("filename", "")]
        
        if not results:
            return f"No indexed chunks found for file: {filename}"
        
        chunks = [r.get("text", "") for r in results]
        return "\n\n---\n\n".join(chunks)
    except ImportError:
        return "Python 'lancedb' package is not installed. Install via: pip install lancedb"
    except Exception as e:
        return f"Error retrieving file context: {str(e)}"

def list_tables():
    """List all indexed repository tables in LanceDB."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return ["No LanceDB directory at: " + LANCEDB_DIR]
        db = lancedb.connect(LANCEDB_DIR)
        return db.table_names() or ["(database exists but has 0 tables)"]
    except ImportError:
        return ["(lancedb not installed)"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def handle_jsonrpc(req):
    req_id = req.get("id")
    method = req.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "continue-rag-mcp", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "search_codebase",
                        "description": "Search the local codebase vector database (LanceDB) with cross-encoder CPU reranking (bge-reranker-base on port 8080).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Semantic code search query, function description, or technical error"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of top reranked chunks to return (default: 3, matches Continue nFinal)",
                                    "default": 3
                                },
                                "table_name": {
                                    "type": "string",
                                    "description": "Optional LanceDB collection/table name (default: 'code_chunks')",
                                    "default": "code_chunks"
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_file_context",
                        "description": "Retrieve all indexed code chunks for a specific file path from the local vector database.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Relative or absolute file path to look up in the vector index"
                                },
                                "table_name": {
                                    "type": "string",
                                    "description": "Optional LanceDB collection/table name",
                                    "default": "code_chunks"
                                }
                            },
                            "required": ["filename"]
                        }
                    },
                    {
                        "name": "list_indexed_repositories",
                        "description": "List all indexed repository tables available in the local LanceDB vector store.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "search_codebase":
            query = args.get("query", "")
            limit = int(args.get("limit", 3))
            table_name = args.get("table_name", "code_chunks")
            results = search_lancedb(query, limit=limit, table_name=table_name)
            
            content_blocks = []
            for r in results:
                score_str = f" [Score: {r['score']:.4f}]" if isinstance(r.get("score"), float) else ""
                content_blocks.append({
                    "type": "text",
                    "text": f"=== File: {r['filename']}{score_str} ===\n{r['text']}"
                })
            
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": content_blocks, "isError": False}
            }
        elif tool_name == "get_file_context":
            filename = args.get("filename", "")
            table_name = args.get("table_name", "code_chunks")
            text = get_file_chunks(filename, table_name=table_name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"=== Context for {filename} ===\n{text}"}],
                    "isError": False
                }
            }
        elif tool_name == "list_indexed_repositories":
            tables = list_tables()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": "Indexed LanceDB Tables:\n- " + "\n- ".join(tables)}],
                    "isError": False
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
                }
            }

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
        resp = handle_jsonrpc(req)
        send(resp)

if __name__ == "__main__":
    main()

```

Make executable:
```bash
chmod +x ~/.local/bin/continue-rag-mcp
```

### Step 5.5: Install `google-pro-mcp` (Google AI Pro Consumer Subscription Bridge)

Exposes all models included in your flat-rate **Google AI Pro** personal subscription (`gemini-4-hydrogen`, `gemini-4-neon`, `gemini-4-argon`, `gemini-3.1-pro`, `gemini-3.8-flash`, `claude-sonnet-5-5`, `claude-opus-5-5`) to any MCP client.

Save to `~/.local/bin/google-pro-mcp`:

```python
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

```

Make executable:
```bash
chmod +x ~/.local/bin/google-pro-mcp
```

### Step 5.6: Install `claude-gcp-mcp` (Model Garden Claude Vertex AI Bridge)

Connects to Anthropic Claude models hosted on Google Cloud Vertex AI Model Garden via ADC (`claude-fable-5-2`, `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-3-7-sonnet`).

Save to `~/.local/bin/claude-gcp-mcp`:

```python
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

```

Make executable:
```bash
chmod +x ~/.local/bin/claude-gcp-mcp
```

---

## 6. MCP Server Configurations Across All Extensions

### Step 6.1: Antigravity Extension & CLI Configuration (`~/.gemini/config/mcp_config.json`)

Configure `~/.gemini/config/mcp_config.json` with all 14 local and cloud MCP servers:

```json
{
  "mcpServers": {
    "google-pro": {
      "command": "/home/YOUR_USERNAME/.local/bin/google-pro-mcp"
    },
    "google-cloud": {
      "command": "/home/YOUR_USERNAME/.local/bin/google-cloud-mcp",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_GCP_PROJECT_ID",
        "GOOGLE_CLOUD_LOCATION": "global"
      }
    },
    "claude-gcp": {
      "command": "/home/YOUR_USERNAME/.local/bin/claude-gcp-mcp",
      "env": {
        "CLAUDE_CONFIG_DIR": "/home/YOUR_USERNAME/.claude-gcp",
        "CLAUDE_CODE_USE_VERTEX": "1",
        "CLOUD_ML_REGION": "global",
        "ANTHROPIC_VERTEX_PROJECT_ID": "YOUR_GCP_PROJECT_ID"
      }
    },
    "claude-teams": {
      "command": "/usr/bin/claude",
      "args": [
        "mcp",
        "serve"
      ],
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
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    },
    "github-models": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"/home/sandbox/.gemini/.env\" ] && . \"/home/sandbox/.gemini/.env\"; [ -f \"/home/sandbox/.config/antigravity-mcp/github-models.env\" ] && . \"/home/sandbox/.config/antigravity-mcp/github-models.env\"; set +a && exec /home/YOUR_USERNAME/.local/bin/github-models-mcp"
      ]
    },
    "continue-rag": {
      "command": "/home/YOUR_USERNAME/.local/bin/continue-rag-mcp"
    },
    "gitlab-com": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"/home/sandbox/.config/antigravity-mcp/gitlab-com.env\" ] && . \"/home/sandbox/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer \" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_\""
      ]
    },
    "gitlab-lip": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"/home/sandbox/.config/antigravity-mcp/gitlab-lip.env\" ] && . \"/home/sandbox/.config/antigravity-mcp/gitlab-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header \"Authorization: Bearer \" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_\""
      ]
    },
    "gitlab-admin-lip": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && [ -f \"/home/sandbox/.config/antigravity-mcp/gitlab-admin-lip.env\" ] && . \"/home/sandbox/.config/antigravity-mcp/gitlab-admin-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header \"Authorization: Bearer \" --header \"X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security\" --header \"X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_\""
      ]
    },
    "gitlab-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . \"/home/sandbox/.config/antigravity-mcp/gitlab-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
    },
    "gitlab-admin-legacy": {
      "command": "sh",
      "args": [
        "-c",
        "set -a && . \"/home/sandbox/.config/antigravity-mcp/gitlab-admin-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"
      ]
    }
  }
}
```

###### Configuration Path Resolution and Compatibility Symlink

Depending on the release channel of the Google Antigravity VS Code extension, configuration discovery checks either `~/.gemini/config/mcp_config.json` or `~/.gemini/antigravity/mcp_config.json`. To guarantee automatic detection across all updates:
```bash
mkdir -p ~/.gemini/antigravity
ln -sf ~/.gemini/config/mcp_config.json ~/.gemini/antigravity/mcp_config.json
```

#### Complete Architecture & Configuration Guide for GitLab Multi-Instance Mesh

##### 1. Modern Instances (GitLab 19.5+): `gitlab.com`, `gitlab.lip.pt` & `gitlab-admin.lip.pt`

* **Native Remote Endpoint**: Starting with GitLab 19.5, the MCP server is natively hosted at `https://<gitlab-host>/api/v4/mcp`.
* **Bearer Authentication via POSIX Subshell**: `mcp-remote` requires an HTTP `Authorization: Bearer <PAT>` header. Sourcing environment files via subshell wrappers (`sh -c 'set -a && . ... && set +a && exec npx -y mcp-remote ...'`) injects tokens without leaking secrets to global environments.
* **Toolset Optimization**: The `X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security` header loads essential developer tools while excluding unused agent platforms, saving ~20k tokens.
* **Namespace Isolation**: `X-Gitlab-Mcp-Server-Tool-Name-Prefix:<prefix>_` prevents collision across instances:
  * `gitlab.com` -> `glcom_` (e.g. `glcom_list_projects`)
  * `gitlab.lip.pt` -> `gllip_` (e.g. `gllip_list_projects`)
  * `gitlab-admin.lip.pt` -> `gladminlip_` (e.g. `gladminlip_list_projects`)

##### 2. Legacy Instances (GitLab < 19.5): `gitlab.legacy.example.org` & `gitlab-admin.legacy.example.org`

* **Compatibility Stdio Server**: Connects via `@zereight/mcp-gitlab` with `GITLAB_TOOL_PREFIX=gllegacy_` and `gladminleg_`.
* **Scoped Toolsets**: `GITLAB_TOOLSETS=issues,merge_requests,repositories,pipelines,wiki` trims unnecessary schemas, saving ~50k tokens.

##### 3. How to Create Personal Access Tokens (PAT)

1. Sign in to your GitLab instance -> User Profile -> **Access Tokens**.
2. Create token with name `VSCode-Agent-MCP`, set an expiration window, and check required scopes:
   * `api` — Full read/write access (commits, merge requests, pipelines).
   * `read_api` — Read-only access for auditing agents.
3. Copy the token immediately into `~/.config/antigravity-mcp/<instance>.env` with `chmod 600` permissions.

##### 4. Institutional SSL / Custom CA Certificates

If internal instances use private certificates, add `NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` into the respective `.env` files.

### Step 6.2: Claude Code Global Configuration (`~/.claude.json`)

Register all MCP servers into Claude Code:
```bash
claude mcp add --scope user google-pro -- "$HOME/.local/bin/google-pro-mcp"
claude mcp add --scope user google-cloud -e GOOGLE_CLOUD_PROJECT="YOUR_GCP_PROJECT_ID" -e GOOGLE_CLOUD_LOCATION="global" -- "$HOME/.local/bin/google-cloud-mcp"
claude mcp add --scope user claude-gcp -e CLAUDE_CONFIG_DIR="$HOME/.claude-gcp" -e CLAUDE_CODE_USE_VERTEX=1 -e CLOUD_ML_REGION=global -e ANTHROPIC_VERTEX_PROJECT_ID="YOUR_GCP_PROJECT_ID" -- "$HOME/.local/bin/claude-gcp-mcp"
claude mcp add --scope user openai-codex-plus -e CODEX_HOME="$HOME/.codex" -- "$HOME/.local/bin/codex-mcp-bridge"
claude mcp add --scope user openai-codex-api -e CODEX_HOME="$HOME/.codex-api" -- "$HOME/.local/bin/codex-mcp-bridge"
claude mcp add --scope user github-mcp -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN" -- npx -y @modelcontextprotocol/server-github
claude mcp add --scope user github-models -- "$HOME/.local/bin/github-models-mcp"
claude mcp add --scope user continue-rag -- "$HOME/.local/bin/continue-rag-mcp"
claude mcp add --scope user gitlab-com -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-com.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-com.env"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_'
claude mcp add --scope user gitlab-lip -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-lip.env"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_'
claude mcp add --scope user gitlab-admin-lip -- sh -c 'set -a && [ -f "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env" ] && . "$HOME/.config/antigravity-mcp/gitlab-admin-lip.env"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header "Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_'
claude mcp add --scope user gitlab-legacy -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'
claude mcp add --scope user gitlab-admin-legacy -- sh -c 'set -a && . "$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env" && set +a && exec npx -y @zereight/mcp-gitlab'
```

### Step 6.3: OpenAI Codex Global Configuration (`~/.codex/config.toml` & `~/.codex-api/config.toml`)

```toml
[mcp_servers.google-pro]
command = "/home/YOUR_USERNAME/.local/bin/google-pro-mcp"

[mcp_servers.google-cloud]
command = "/home/YOUR_USERNAME/.local/bin/google-cloud-mcp"
[mcp_servers.google-cloud.env]
GOOGLE_CLOUD_PROJECT = "YOUR_GCP_PROJECT_ID"
GOOGLE_CLOUD_LOCATION = "global"

[mcp_servers.claude-gcp]
command = "/home/YOUR_USERNAME/.local/bin/claude-gcp-mcp"
[mcp_servers.claude-gcp.env]
CLAUDE_CONFIG_DIR = "/home/YOUR_USERNAME/.claude-gcp"
CLAUDE_CODE_USE_VERTEX = "1"
CLOUD_ML_REGION = "global"
ANTHROPIC_VERTEX_PROJECT_ID = "YOUR_GCP_PROJECT_ID"

[mcp_servers.github-mcp]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
[mcp_servers.github-mcp.env]
GITHUB_PERSONAL_ACCESS_TOKEN = "YOUR_GITHUB_PAT"

[mcp_servers.github-models]
command = "/home/YOUR_USERNAME/.local/bin/github-models-mcp"

[mcp_servers.continue-rag]
command = "/home/YOUR_USERNAME/.local/bin/continue-rag-mcp"

[mcp_servers.gitlab-com]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-com.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_"
]

[mcp_servers.gitlab-lip]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_"
]

[mcp_servers.gitlab-admin-lip]
command = "sh"
args = [
  "-c",
  "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_"
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

Configure `mcpServers:` in `~/.continue/config.yaml`:
```yaml
mcpServers:
  - name: google-pro
    command: /home/YOUR_USERNAME/.local/bin/google-pro-mcp
  - name: google-cloud
    command: /home/YOUR_USERNAME/.local/bin/google-cloud-mcp
    env:
      GOOGLE_CLOUD_PROJECT: "YOUR_GCP_PROJECT_ID"
      GOOGLE_CLOUD_LOCATION: "global"
  - name: claude-gcp
    command: /home/YOUR_USERNAME/.local/bin/claude-gcp-mcp
    env:
      CLAUDE_CONFIG_DIR: "/home/YOUR_USERNAME/.claude-gcp"
      CLAUDE_CODE_USE_VERTEX: "1"
      CLOUD_ML_REGION: "global"
      ANTHROPIC_VERTEX_PROJECT_ID: "YOUR_GCP_PROJECT_ID"
  - name: claude-teams
    command: /usr/bin/claude
    args: ["mcp", "serve"]
    env:
      CLAUDE_CONFIG_DIR: "/home/YOUR_USERNAME/.claude"
  - name: openai-codex-plus
    command: /home/YOUR_USERNAME/.local/bin/codex-mcp-bridge
    env:
      CODEX_HOME: "/home/YOUR_USERNAME/.codex"
  - name: openai-codex-api
    command: /home/YOUR_USERNAME/.local/bin/codex-mcp-bridge
    env:
      CODEX_HOME: "/home/YOUR_USERNAME/.codex-api"
  - name: github-mcp
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  - name: github-models
    command: /home/YOUR_USERNAME/.local/bin/github-models-mcp
  - name: continue-rag
    command: /home/YOUR_USERNAME/.local/bin/continue-rag-mcp
  - name: gitlab-com
    command: sh
    args: ["-c", "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-com.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-com.env\"; set +a && exec npx -y mcp-remote https://gitlab.com/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:glcom_"]
  - name: gitlab-lip
    command: sh
    args: ["-c", "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gllip_"]
  - name: gitlab-admin-lip
    command: sh
    args: ["-c", "set -a && [ -f \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\" ] && . \"$HOME/.config/antigravity-mcp/gitlab-admin-lip.env\"; set +a && exec npx -y mcp-remote https://gitlab-admin.lip.pt/api/v4/mcp --header \"Authorization: Bearer $GITLAB_PERSONAL_ACCESS_TOKEN\" --header X-Gitlab-Enabled-Mcp-Server-Toolsets:core,merge_requests,work_items,repository,ci,wikis,code_security --header X-Gitlab-Mcp-Server-Tool-Name-Prefix:gladminlip_"]
  - name: gitlab-legacy
    command: sh
    args: ["-c", "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"]
  - name: gitlab-admin-legacy
    command: sh
    args: ["-c", "set -a && . \"$HOME/.config/antigravity-mcp/gitlab-admin-legacy.env\" && set +a && exec npx -y @zereight/mcp-gitlab"]
```

### Step 7.3: Strategy to Optimize Token Costs via Local RAG & Orchestration

Loading all 14 MCP servers into Continue injects **15,000 to 30,000+ tokens of raw JSON tool schemas** into every model turn. On consumer hardware (GTX 1650 4GB or RTX 3050 8GB), this saturates the KV-cache, inflates latency, and leads to malformed tool-call JSON.

The optimal workflow decouples **local RAG data preparation** from **frontier cloud orchestration**:
1. **Continue** runs locally in **Chat mode** with zero active MCP schemas in the prompt. It retrieves relevant codebase context via CPU embeddings (`ollama-embed-cpu` on port 11435) and scores them via the CPU cross-encoder reranker on port 8080.
2. Continue executes a generative slash command (`/antigravity-spec-laptop` or `/antigravity-spec-workstation`) to condense the reranked code into an execution brief.
3. **Google Antigravity** (`Ctrl+L`), running under your flat-rate **Google AI Pro** subscription (`gemini-4-hydrogen` or `gemini-3.1-pro`), ingests the brief and orchestrates your external MCP tools (`claude-gcp`, `google-cloud`, `openai-codex-plus`, `github-models`, and GitLab instances).

#### Hardware Allocation & Memory Profile

| Workload Phase | Machine & Hardware | Model Configuration | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Phase 1: Local Extraction & Indexing** | Laptop (GTX 1650 4GB + 16GB RAM) | `Laptop-Worker-3B` (`qwen2.5-coder:3b-instruct-q8_0`) | Zero thinking-token overhead, 16k context, 100% in VRAM (~2.5GB). |
| **Phase 1: Full-Workspace Synthesis** | Desktop (RTX 3050 8GB + 32GB RAM) | `Office-Synthesizer-7B` (`qwen2.5-coder:7b-instruct-q4_K_M`) | Reasoning distillation, multi-repo dependency graphs (~5.2GB VRAM). |
| **Phase 1: Background Vector Embeddings** | Shared CPU Service (`ollama-embed-cpu`, port 11435) | `nomic-embed-text` | Pinned to system RAM (`NVIDIA_VISIBLE_DEVICES=none`), 0 MB VRAM used. |
| **Phase 1: Cross-Encoder Reranking** | Shared CPU Service (`rerank-server`, port 8080) | `BAAI/bge-reranker-base` | Fast cross-entropy scoring on CPU, 0 MB VRAM used. |
| **Phase 2: Frontier Multi-Agent Orchestration** | Flat-Rate Cloud (Google AI Pro in Antigravity) | `gemini-4-hydrogen` / `gemini-3.1-pro` (1M+ context) | Dispatches tasks across MCP subagents; consumes 0 local VRAM for tool schemas. |

#### How `nFinal` Works and Passing Reranked Chunks to Prompts

Under Continue's `context:` block:
```yaml
context:
  - provider: codebase
    params:
      nRetrieve: 12
      nFinal: 3
      useReranking: true
```
* **`nRetrieve: 12`**: Continue fetches 12 candidate chunks from LanceDB (`~/.continue/index/`).
* **Cross-Encoder Scoring**: Forwards all 12 candidates to `rerank-server` on port 8080 (`BAAI/bge-reranker-base`).
* **`nFinal: 3`**: Discards lower-scoring chunks and injects **only the top 3 scored snippets** (~1,500 tokens total) into the active prompt's `{{ input }}` block.

#### 3-Phase Migration Pipeline

1. **Phase 1: File Digests (`/digest`)**: Attach 3–5 core files in Continue chat -> run `/digest` -> save to `migration-prep/`.
2. **Phase 2: Master Synthesis (`/synthesize`)**: Attach markdown digests -> run `/synthesize` -> output `migration-prep/MASTER_ARCHITECTURE_SPEC.md`.
3. **Phase 3: Antigravity Multi-Agent Orchestration**: Paste brief into Antigravity (`Ctrl+L`) running on Gemini 4 Hydrogen to execute across your MCP mesh.

### Step 7.4: Automated Multi-IDE Ignore & Context Synchronization (`genignore.py`, `update-ai-ignore.sh`, and `pre-commit`)

Synchronizes ignore and context exclusion rules across all AI development extensions from your repository's `.gitignore` and `.gitattributes`.

#### Script 1: `genignore.py` (Multi-Provider Exclusion & JSON Deep-Merger)

Save to `genignore.py` (or `~/.local/bin/genignore.py`):
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

#### Script 2: `update-ai-ignore.sh` (Change-Detection Shell Wrapper)

Save to `update-ai-ignore.sh` (or `~/.local/bin/update-ai-ignore.sh`):
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

#### Script 3: Git Pre-Commit Hook (`pre-commit`)

Install to `.git/hooks/pre-commit`:
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

#### Setup & Verification:

```bash
chmod +x genignore.py update-ai-ignore.sh
cp pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
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

---

## 10. End-to-End Verification and Diagnostics

### Step 10.1: Test Python MCP Bridges Protocol Handshake

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | ~/.local/bin/google-cloud-mcp
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | ~/.local/bin/google-pro-mcp
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | ~/.local/bin/codex-mcp-bridge
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | ~/.local/bin/github-models-mcp
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | ~/.local/bin/continue-rag-mcp
```

### Step 10.2: Verify Registered Servers in Claude Code

```bash
claude mcp list
```
Confirm all 14 servers report `Connected`.

### Step 10.3: Inspect Live Indicators and Utilize MCP Servers in VS Code Antigravity

Open Antigravity chat (**`Ctrl+L`**), type **`/mcp`**, and confirm all 14 servers show green connection status rings.

###### Sample Invocations in Antigravity:

* *"Query `google-pro` using `list_google_pro_models` to inspect active models on my subscription."*
* *"Ask `google-pro` with model `gemini-4-hydrogen` to architect this service refactoring."*
* *"Ask `google-cloud` using model `gemini-4-carbon-medium` to audit our concurrency safeguards."*
* *"Query `continue-rag` using `search_codebase` to find definitions of `WorkerPool` in LanceDB."*
* *"Ask `openai-codex-plus` using model `gpt-5.3-codex` to generate unit tests."*
* *"Ask `github-models` with model `auto` to review this pull request diff."*
* *"Using `gitlab-com` (tool `glcom_list_projects`), check my recent repositories."*

### Step 10.4: Verify Secondary Extension Status (Claude Code, Continue & Copilot)

1. **Claude Code**: Run `/mcp` inside the Claude Code panel.
2. **Continue Extension**: Confirm all 14 servers appear in the prompt tool picker.
3. **GitHub Copilot Chat**: Open Copilot Chat (**`Ctrl+Alt+I`**) and verify tool discovery.

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