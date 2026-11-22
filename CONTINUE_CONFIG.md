# VS Code Continue Extension: Comprehensive Architecture & Setup Guide (v3)

An enterprise-grade, hardware-optimized configuration for the **Continue VS Code extension (`Continue.continue`)** paired with a unified **Ollama + CPU Reranker Docker Compose** stack, hardware-aware **RAG indexing**, and a native **Model Context Protocol (MCP)** multi-agent mesh on Arch Linux and Gentoo.

---

## 1. Executive Summary & Feasibility Assessment: Containerized Reranker

### Feasibility: YES (100% Compatible & Recommended)
Running `rerank_server` directly inside your `docker-compose.yml` alongside `ollama` and `open-webui` is not only possible, it is the optimal architectural pattern for your hardware:

1. **Zero Port Collisions**: 
   * `ollama` binds to host `127.0.0.1:11434`.
   * `open-webui` maps host `127.0.0.1:3000` to internal container port `8080`.
   * `rerank-server` maps host `127.0.0.1:8080` to internal container port `8080`.
   Each service operates on a distinct host port with zero interference.
2. **Absolute VRAM Protection (0 MB VRAM Used)**:
   The reranker container runs entirely on your AMD Ryzen 7 5800H CPU using 8 dedicated threads. It never accesses the NVIDIA container toolkit or GPU devices, guaranteeing that 100% of the GTX 1650's 4GB VRAM remains dedicated to your active LLM.
3. **Optimized Local Build (`Dockerfile.reranker`)**:
   Using standard upstream PyTorch images pulls ~4.5 GB of unused CUDA and cuDNN binaries. Our custom `Dockerfile.reranker` pulls the official **CPU-only PyTorch wheel** (`--index-url https://download.pytorch.org/whl/cpu`), resulting in an ultra-lean image (~750 MB) that builds in under two minutes.
4. **Persistent Model Cache**:
   By mounting `/var/lib/ollama/rerank-cache` to `/root/.cache/huggingface`, model weights (`BAAI/bge-reranker-base`, ~1.1 GB) are downloaded only once and persist across container restarts or image rebuilds.
5. **Unified Lifecycle Management**:
   A single command (`docker compose up -d --build` or `podman-compose up -d --build`) starts your entire local AI infrastructure: inference engine, web GUI, and two-stage RAG reranker.

---

## 2. System Hardware Allocation Profile

* **Host Model**: HP Pavilion Gaming Laptop 15-ec2xxx
* **CPU**: AMD Ryzen 7 5800H (8 physical Zen 3 cores, 16 threads, up to 4.45 GHz)
* **System RAM**: 16 GiB DDR4 (2x 8GB SODIMM @ 3200 MT/s)
* **GPU**: NVIDIA GeForce GTX 1650 Mobile (4096 MiB VRAM, Turing NVENC/NVDEC)
* **Storage**: 1.0 TB NVMe PCIe SSD (WDC WDS100T2B0C)
* **OS / Desktop**: Arch Linux (rolling release, KDE Plasma 6 Wayland session) / Gentoo Linux

### Hardware Budgeting Strategy

| Workload | Container / Component | Target Device | Rationale & Memory Budget |
| :--- | :--- | :--- | :--- |
| **Primary Agent & Edits** | `qwen2.5-coder:7b-instruct-q4_K_M` | GPU + CPU Split | Offloads ~24–28 layers to 4GB VRAM; remaining layers execute in RAM. |
| **Fast In-line Chat** | `qwen2.5-coder:3b-instruct-q8_0` | 100% GPU VRAM | Fits 100% into 4GB VRAM (~3.4GB footprint) for instantaneous zero-latency edits. |
| **Deep Reasoning** | `deepseek-r1:8b` / `gemma2:9b` | Hybrid GPU / CPU | Executes complex logical evaluation; KV cache capped to 4096 tokens. |
| **Codebase Embeddings** | `nomic-embed-text` | **100% CPU (0 VRAM)** | Pinned to CPU via `num_gpu: 0` in Continue. Prevents chat model eviction. |
| **Tab Autocomplete** | `qwen2.5-coder:1.5b-base-q8_0` | **100% CPU (0 VRAM)** | Background ghost-text execution pinned to CPU (8 threads). |
| **RAG Semantic Reranking** | `rerank-server` (Container) | **100% CPU (0 VRAM)** | Local FastAPI container on port 8080 (~1.1GB RAM, 0 MB VRAM). |
| **Cloud Escalation** | Gemini 4 Carbon, Claude Fable, Codex | Native Host MCP | High-level architectural reasoning routed via stdio MCP subagents. |

---

## 3. Directory Layout & Stack Artifacts

```
/var/lib/ollama/
├── data/                            # Persistent Ollama model weights (~/root/.ollama)
├── ui/                              # Open-WebUI database & user configurations
└── rerank-cache/                    # Hugging Face model weights cache (~1.1 GB)

~/workspace/ollama-stack/            # (or your preferred compose project directory)
├── docker-compose.yml               # Unified 3-tier stack (Ollama, WebUI, Reranker)
├── Dockerfile.reranker              # CPU-only Python 3.11 container definition
└── rerank_server.py                 # FastAPI TEI-compatible cross-encoder endpoint

~/.continue/
├── config.yaml                      # Active Continue extension runtime configuration
├── index/                           # Embedded LanceDB vector store & SQLite metadata
└── .continueignore                  # Workspace ignore rules (prevents index bloat)

~/.local/bin/
└── agy-mcp-bridge                   # Native Python bridge for Antigravity ACP -> MCP
```

---

## 4. Compose Service Architecture & Build Files

### 4.1 The Complete `docker-compose.yml`
Save this unified specification in your compose workspace:

```yaml
services:
  # ----------------------------------------------------------------------------
  # 1. Ollama Inference Engine (NVIDIA GPU Accelerated - Coding & Chat)
  # ----------------------------------------------------------------------------
  ollama:
    image: docker.io/ollama/ollama:latest
    container_name: ollama
    hostname: ollama
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_NUM_PARALLEL=1          # Limits KV cache allocations to prevent CUDA OOM
      - OLLAMA_MAX_LOADED_MODELS=1     # Keeps the coder model permanently pinned in VRAM
      - OLLAMA_KEEP_ALIVE=24h
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - OLLAMA_FLASH_ATTENTION=1       # Halves KV-cache memory allocation
      - OLLAMA_KV_CACHE_TYPE=q8_0      # 8-bit quantization prevents memory thrashing
    volumes:
      - /var/lib/ollama/data:/root/.ollama
    ports:
      - "127.0.0.1:11434:11434"
    devices:
      - "nvidia.com/gpu=all"
    security_opt:
      - label=disable

  # ----------------------------------------------------------------------------
  # 2. CPU Embedding Engine (16-Thread Ryzen 7 5800H - Zero GPU VRAM Used)
  # ----------------------------------------------------------------------------
  ollama-embed-cpu:
    image: docker.io/ollama/ollama:latest
    container_name: ollama-embed-cpu
    hostname: ollama-embed-cpu
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_NUM_PARALLEL=2          # Allows concurrent background embedding requests
      - OLLAMA_MAX_LOADED_MODELS=1
      - OLLAMA_NUM_THREAD=12           # Allocates 12 threads across physical Zen 3 cores
      - NVIDIA_VISIBLE_DEVICES=none    # Enforces 100% CPU execution; 0 MB VRAM used
    volumes:
      - /var/lib/ollama/data:/root/.ollama  # Shared volume avoids duplicate model downloads
    ports:
      - "127.0.0.1:11435:11434"       # Host port 11435 -> container port 11434
    security_opt:
      - label=disable

  # ----------------------------------------------------------------------------
  # 3. Open-WebUI (Web Management Interface)
  # ----------------------------------------------------------------------------
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    hostname: open-webui
    restart: unless-stopped
    ports:
      # Host 3000 -> Container 8080 (Leaves host 8080 completely free for reranker)
      - "127.0.0.1:3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_AUTH=false
      - ENABLE_OPENAI_API=false
    volumes:
      - /var/lib/ollama/ui:/app/backend/data
    depends_on:
      - ollama
    security_opt:
      - label=disable

  # ----------------------------------------------------------------------------
  # 4. Local CPU Cross-Encoder Reranker (100% CPU, 0 MB VRAM)
  # ----------------------------------------------------------------------------
  rerank-server:
    build:
      context: .
      dockerfile: Dockerfile.reranker
    image: localhost/continue-reranker:latest
    container_name: rerank-server
    hostname: rerank-server
    restart: unless-stopped
    environment:
      - MODEL_NAME=BAAI/bge-reranker-base
      - DEVICE=cpu
      - OMP_NUM_THREADS=8
      - MKL_NUM_THREADS=8
      - PORT=8080
      - HOST=0.0.0.0
    volumes:
      # Persists downloaded weights on host disk (~/root/.cache/huggingface)
      - /var/lib/ollama/rerank-cache:/root/.cache/huggingface
    ports:
      # Exposes port 8080 on 127.0.0.1 for Continue's huggingface-tei provider
      - "127.0.0.1:8080:8080"
    security_opt:
      - label=disable
```

---

### 4.2 The Container Definition (`Dockerfile.reranker`)
This file builds a dedicated, lightweight CPU container using CPU-only PyTorch wheels:

```dockerfile
# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface \
    MODEL_NAME=BAAI/bge-reranker-base \
    DEVICE=cpu \
    PORT=8080 \
    HOST=0.0.0.0 \
    OMP_NUM_THREADS=8 \
    MKL_NUM_THREADS=8

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch wheel (~500MB vs ~4GB CUDA build)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install FastAPI and sentence-transformers
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    sentence-transformers

COPY rerank_server.py /app/rerank_server.py

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "/app/rerank_server.py"]
```

---

### 4.3 The Reranker Application Script (`rerank_server.py`)
This script implements Hugging Face TEI and Cohere compatible endpoints:

```python
#!/usr/bin/env python3
import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import CrossEncoder

MODEL_NAME = os.getenv("MODEL_NAME", "BAAI/bge-reranker-base")
DEVICE = os.getenv("DEVICE", "cpu")
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

app = FastAPI(
    title="Continue Local CPU Reranker",
    description="TEI-compatible local cross-encoder rerank API for VS Code Continue RAG",
    version="1.0.0",
)

print(f"[*] Initializing CrossEncoder model '{MODEL_NAME}' on {DEVICE}...")
try:
    model = CrossEncoder(MODEL_NAME, device=DEVICE)
    # Perform warmup inference to load weights into RAM immediately
    _ = model.predict([["Warmup query", "Warmup passage"]])
    print(f"[+] Model '{MODEL_NAME}' loaded successfully. Ready for requests.")
except Exception as e:
    print(f"[!] Error loading model '{MODEL_NAME}': {e}", file=sys.stderr)
    model = None

class RerankRequest(BaseModel):
    query: str
    texts: Optional[List[str]] = Field(default=None, description="Candidate snippets (TEI format)")
    documents: Optional[List[str]] = Field(default=None, description="Candidate snippets (Cohere format)")

@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Reranker model failed to initialize")
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}

@app.post("/rerank")
def rerank(req: RerankRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Reranker model not available")
    
    candidates = req.texts if req.texts is not None else req.documents
    if not candidates:
        return []

    pairs = [[req.query, doc] for doc in candidates]
    scores = model.predict(pairs).tolist()
    return [{"index": i, "score": float(s)} for i, s in enumerate(scores)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
```

---

## 5. Deployment & Execution Instructions

### Step 5.1: Create Host Storage Directories
Ensure the persistent host volume mount directories exist:
```bash
sudo mkdir -p /var/lib/ollama/data /var/lib/ollama/ui /var/lib/ollama/rerank-cache
sudo chown -R $USER:$USER /var/lib/ollama
```

### Step 5.2: Build and Launch the Stack

#### Option A: Docker Compose (Standard)
```bash
docker compose up -d --build
```

#### Option B: Podman Compose (Gentoo / Arch CDI Environment)
As documented in your project notes, if using Podman with CDI on Arch or Gentoo:
```bash
# Generate CDI device specification if not already present
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# Launch container stack with Btrfs driver and podman-compose provider
STORAGE_DRIVER=btrfs PODMAN_COMPOSE_PROVIDER=podman-compose podman compose up -d --build
```

### Step 5.3: Verify Container Health
Check running containers and test the reranker endpoint:
```bash
# Check container status
docker ps  # or podman ps

# Test reranker health endpoint
curl -s http://localhost:8080/health
# Response: {"status":"ok","model":"BAAI/bge-reranker-base","device":"cpu"}

# Test scoring endpoint
curl -s -X POST http://localhost:8080/rerank \
  -H "Content-Type: application/json" \
  -d '{"query": "sorting algorithms", "texts": ["QuickSort is divide-and-conquer", "The sky is blue today"]}'
# Response: [{"index":0,"score":0.98...},{"index":1,"score":-0.95...}]
```

### Step 5.4: Pull Ollama Local Models
Once the `ollama` container is healthy, pull the models required by your Continue `config.yaml`:
```bash
docker exec -it ollama ollama pull qwen2.5-coder:7b-instruct-q4_K_M
docker exec -it ollama ollama pull qwen2.5-coder:3b-instruct-q8_0
docker exec -it ollama ollama pull deepseek-r1:8b
docker exec -it ollama ollama pull gemma2:9b-instruct-q4_K_M
docker exec -it ollama ollama pull gemma4:e4b
docker exec -it ollama ollama pull llama3.1:8b-instruct-q4_K_M
docker exec -it ollama ollama pull gemma2:2b
docker exec -it ollama ollama pull llama3.2:3b-instruct-q8_0
docker exec -it ollama ollama pull qwen2.5-coder:1.5b

# Embeddings & Autocomplete (Pinned to CPU via config.yaml)
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull qwen2.5-coder:1.5b-base-q8_0
```

---

## 6. Continue Configuration & RAG Tuning (`config.yaml`)

Your `~/.continue/config.yaml` is pre-configured to link seamlessly to the containerized reranker and Ollama engine:

```yaml
# Reranker role definition in ~/.continue/config.yaml
models:
  - name: BGE Reranker (CPU Container)
    provider: huggingface-tei
    model: BAAI/bge-reranker-base
    apiBase: http://localhost:8080
    roles:
      - rerank

# Two-Stage RAG context provider tuning
context:
  - provider: codebase
    params:
      nRetrieve: 12   # Retrieve 12 candidate chunks via embedded LanceDB
      nFinal: 3       # Rerank via container on port 8080 and pass top 3 chunks to LLM
      useReranking: true
```

### 6.1 Embedded LanceDB Vector Storage
Continue manages vector search internally using **LanceDB** inside `~/.continue/index/`. It requires no external vector databases (such as Qdrant or Milvus). 

### 6.2 Workspace Filtering (`.continueignore`)
Place a `.continueignore` file in the root of your repositories to prevent indexing noise:
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
```

---

## 7. Operational Diagnostics & Performance Verification

### Diagnostic 1: Confirm Zero VRAM Consumption on Embeddings & Reranker
Execute a codebase query in VS Code (`@codebase test`), then open a terminal and inspect Ollama processes:
```bash
docker exec -it ollama ollama ps
```
* **`qwen2.5-coder:7b-instruct-q4_K_M`**: Displays active GPU allocation (e.g. `2.8 GB / 4.0 GB`).
* **`nomic-embed-text`**: Displays **`100% CPU`** under processor.
* **`qwen2.5-coder:1.5b-base-q8_0`**: Displays **`100% CPU`** under processor.
* **`rerank-server`**: Runs in its own container with 0 GPU attachments.

### Diagnostic 2: Inspect Reranker Container Logs
```bash
docker logs -f rerank-server
```
You will see incoming `POST /rerank` requests logged by Uvicorn in real-time as Continue scores code snippets.

--------------------------------------------------------------------------------

## 8. Continue Chat Mode Operational Guidelines & Token Optimization Strategy

To achieve maximum performance and prevent token/memory exhaustion on consumer hardware (such as laptops with a 4GB GTX 1650 or workstations with an 8GB RTX 3050), follow this operational methodology derived from the Continue Chat Mode optimization specifications.

### 8.1 Mandatory Chat Mode Enforcement (Avoid Agent & Plan Modes)

When executing local extraction, refactoring, and summarization tasks:
* **Stay Strictly in Chat Mode**: Open Continue (**`Ctrl+L`**) and ensure the mode selector at the bottom is set to **Chat**.
* **Why Agent and Plan Modes Must Be Avoided on Low VRAM**:
  * Agent and Plan modes inject Continue's internal tool schemas (`read_file`, `create_new_file`, `run_terminal_command`, etc.), adding **4,000 to 6,000 tokens of JSON schema overhead** to every prompt.
  * Local 3B and 7B models frequently struggle with strict multi-turn JSON tool-calling loops, emitting malformed syntax or getting stuck in repetitive execution loops.
  * **Chat mode** performs single-pass, deterministic completions directly against the exact files attached, leaving 100% of your context window available for source code.

### 8.2 Why `@Codebase` Fails for Phase 1 Full-Project Summarization

While `@Codebase` is powerful for answering specific semantic questions, it must **never** be used for full-project architectural extraction or repository inventorying:
1. **Incomplete Coverage (Top-K Truncation)**: `@Codebase` embeds your prompt and retrieves only the top 10–20 chunks (512 tokens each) that semantically match the keywords. It does **not** read every file in your repository, silently skipping critical configuration files (such as `Jenkinsfile`, `Dockerfile`, CI pipelines, and playbooks).
2. **Context Fragmentation**: Receiving disconnected 512-token snippets from a dozen files confuses small local models (`qwen2.5-coder:3b`), causing them to hallucinate relationships across files.
3. **Latency Overhead**: Every `@Codebase` call incurs vector search and cross-encoder reranking latency before generation starts.
4. **The Remedy**: For Phase 1 repository digests, use direct file attachment (**`@File`**) to guarantee 100% exhaustive code inspection.

### 8.3 Folder Attachment & Deprecation of `@Folder`

* **Deprecation Notice**: In modern releases of Continue, `@Folder` and `@Codebase` context provider syntax are officially deprecated in favor of native file providers and drag-and-drop actions.
* **Modern Folder Attachment via Explorer**:
  * In the VS Code Explorer sidebar, **right-click the target repository folder** (or select 3–5 related files with `Ctrl+Click` / `Shift+Click`).
  * Select **Continue → Add to Chat** (or simply drag the folder directly from the Explorer into the Continue chat input box).
  * Continue automatically expands the directory and attaches all valid source files as individual `@File` pills while strictly honoring your `.continueignore` rules.

### 8.4 Complete 3-Phase Migration Workflow

This end-to-end pipeline decouples zero-cost local code preparation from frontier cloud reasoning:

```
[ Local Raw Code & Repositories ]
                │
                ▼ (Filtered via .continueignore)
[ Continue Local Chat Mode (Ctrl+L): Port 11434 (3B GPU) + Port 11435 (CPU Embed) ]
                │
                ▼ (Pre-processed via /digest & /synthesize)
[ migration-prep/MASTER_ARCHITECTURE_SPEC.md (< 12,000 words / zero cloud tokens) ]
                │
                ▼ (Ingested into Antigravity Agent Mode via Ctrl+L)
[ Google Antigravity Frontier Orchestrator (Gemini 3.1 Pro / Gemini 4 Carbon, 1M+ context) ]
        │                       │                       │
        ▼                       ▼                       ▼
  claude-fable-gcp        gemini-carbon-gcp       openai-codex-plus / gitlab-mcp
  (Phased Planning)     (Architecture Audit)     (Code Templates & Git Sync)
```

#### Phase 1: Local File Extraction (`/digest`)
1. Open a clean chat session (**`Ctrl+L`**), confirm mode is **Chat**, and select `Laptop-Worker-3B`.
2. Attach files for a single repository (either the entire folder for repos under 12k tokens via right-click, or 3–5 file batches for large repos).
3. Type **/digest** and press **Enter**.
4. Copy the Markdown response and save it into a thematic file in `migration-prep/` (e.g. `migration-prep/01-ci-jenkins.md`, `02-verification.md`, `03-ansible-roles.md`).
5. Click **`+` (New Session)** to clear context between batches so prior tokens do not pollute subsequent prompts.

#### Phase 2: Master Context Consolidation (`/synthesize`)
1. Open a fresh Chat session (**`+`**), confirm mode is **Chat**.
2. Attach *only* the generated digest files using `@File` (e.g. `@File migration-prep/01-ci-jenkins.md`, `@File migration-prep/02-verification.md`). Do **not** use `@Codebase` here.
3. Type **/synthesize** and press **Enter**.
4. Save the unified specification as **`migration-prep/MASTER_ARCHITECTURE_SPEC.md`** (target length: < 12,000 words / ~16k tokens).

#### Phase 3: Frontier Multi-Agent Orchestration in Antigravity
1. Close Continue and switch to **Google Antigravity (`Ctrl+L`)** in **Agent** mode on your **Google AI Pro** (`gemini-3.1-pro`) subscription or **Google Cloud Agent Platform** (`gemini-4-carbon`).
2. Attach `@migration-prep/MASTER_ARCHITECTURE_SPEC.md`.
3. Dispatch specialized tasks across your local MCP subagents:
   * **Stage 1 (`claude-fable-gcp`)**: Design a 3-wave phased migration plan replacing legacy Jenkins/Puppet with modern CI/CD.
   * **Stage 2 (`gemini-carbon-gcp`)**: Audit infrastructure coupling, hardcoded endpoints, and rollback risks.
   * **Stage 3 (`openai-codex-plus`)**: Generate starter CI workflow templates and container build matrices.

### 8.5 Toggling MCP in Continue on Low-VRAM Hardware

Loading all 11 MCP servers injects **15,000 to 30,000+ tokens of raw JSON tool schemas** into every model turn. On a 4GB or 8GB GPU, this schema overhead saturates the KV cache, causes extreme generation latency, and triggers malformed tool calls.

To maximize context space for code files during Phase 1 bulk extraction, temporarily disable MCP servers in Continue:
* **Option A**: In `~/.continue/config.yaml`, set `mcpServers: []` (empty list).
* **Option B**: Highlight the `mcpServers:` block in VS Code and press **`Ctrl+/`** to comment it out.
* Reload VS Code (**`Ctrl+Shift+P` → `Developer: Reload Window`**).
* *Note: Because Antigravity reads `~/.gemini/config/mcp_config.json`—not Continue's `config.yaml`—all 11 MCP servers remain permanently active and accessible inside Antigravity.*

### 8.6 Workspace Filtering via `.continueignore`

Create a `.continueignore` file in your workspace root to exclude static assets, build outputs, and lockfiles:

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
