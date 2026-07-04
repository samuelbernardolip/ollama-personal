# ollama-personal
My personal configurations for Ollama and IDE integrations

Before running the compose file, your host system must meet these requirements:

1. NVIDIA Drivers: Your installed 595.71.05 driver is perfect. Ensure your user is in the video and render groups:

```bash
gpasswd -a <your_user> video
gpasswd -a <your_user> render
```

2. NVIDIA Container Toolkit: Install app-containers/nvidia-container-toolkit on Gentoo to allow Podman to pass the GPU into the container.

3. Podman Configuration: Generate the CDI (Container Device Interface) specification so Podman recognizes your hardware:

```bash
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

4. Verify GPU in Podman: Run a test container to check if Podman can see your RTX 3050:

```bash
podman run --rm --device nvidia.com/gpu=all docker.io/nvidia/cuda:13.2.1-base-rockylinux10 nvidia-smi
```

5. Load models into ollama

```bash
podman exec -it ollama ollama pull qwen2.5-coder:7b-instruct-q4_K_M
podman exec -it ollama ollama pull deepseek-r1:8b
podman exec -it ollama ollama pull qwen2.5-coder:3b-instruct-q8_0
podman exec -it ollama ollama pull qwen2.5-coder:1.5b-base-q8_0
podman exec -it ollama ollama pull llama3.1:8b-instruct-q4_K_M
podman exec -it ollama ollama pull gemma4:e4b
podman exec -it ollama ollama pull gemma2:9b-instruct-q4_K_M
podman exec -it ollama ollama pull gemma2:2b
podman exec -it ollama ollama pull llama3.2:3b-instruct-q8_0
podman exec -it ollama ollama pull nomic-embed-text
```

------------------------------

## Generate commit messages

You can generate commit messages using the [Continue AI extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue) in VS Code by using the built-in git context provider or installing a helper utility. [1, 2]

### Method 1: The Native Slash Command (Standard)

You can reference your active changes directly inside the Continue chat sidebar to build a commit summary: [3]

   1. Open the Continue chat panel with Ctrl + L (Windows/Linux) or Cmd + L (Mac).
   2. Stage your changes inside the VS Code Source Control panel.
   3. In the chat box, type @git (or @codebase) followed by the /commit slash command.
   4. Press enter, and Continue will analyze your unstaged or staged diff to draft a message.
   5. Copy and paste the output directly into your Git commit input field. [3, 4, 5, 6]

### Method 2: One-Click Integration via Helper Extension

Because the core Continue extension does not yet place a native "sparkle" button inside the Git panel, community plugins resolve this behavior: [1]

   1. Install the [Continue Commit Notes](https://marketplace.visualstudio.com/items?itemName=jim-ki-do.continue-commit-notes) companion extension from the VS Code Marketplace.
   2. Open the Source Control Panel (Ctrl + Shift + G / Cmd + Shift + G).
   3. Hover your cursor over the Changes or Staged Changes title row.
   4. Click the "C" logo icon that appears inline, or execute Continue Commit: Generate Commit Message from the Command Palette (Ctrl + Shift + P).
   5. The extension leverages your existing config.json model to automatically fill your VS Code commit text box. [1, 5, 7]

### Method 3: Customize the Rules in config.json

To dictate exactly how Continue formats your messages (such as forcing [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) layout), you can map a custom prompt: [3, 8]

   1. Click the gear icon at the bottom of the Continue panel to open your global config.json file.
   2. Add a custom shortcut under the customCommands block: [3, 9]

"customCommands": [
  {
    "name": "commit-msg",
    "prompt": "Review the following git diff and output a clean commit message following Conventional Commits guidelines. Do not output anything else except the message header and brief body points: {{{ input }}}",
    "description": "Generate a structured git commit message"
  }
]


   1. Run it inside the chat by highlighting your code or typing /commit-msg combined with the @git context tag.

If you have specific style criteria, let me know:

* Do you need your commits to follow a Conventional Commits (feat:, fix:) pattern?
* Are you looking to wire up a local LLM (Ollama, Llama) or a cloud provider (Claude, OpenAI) to run this task?
* Would you like assistance writing a custom bash script to automate this through the Continue CLI instead? [8]


[1] [https://marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=jim-ki-do.continue-commit-notes)
[2] [https://www.youtube.com](https://www.youtube.com/watch?v=C1g4_YQJEg8)
[3] [https://docs.continue.dev](https://docs.continue.dev/guides/understanding-configs)
[4] [https://code.visualstudio.com](https://code.visualstudio.com/docs/sourcecontrol/staging-commits)
[5] [https://marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=kevin-kidd.aicommit-vscode)
[6] [https://shawnhooper.ca](https://shawnhooper.ca/2022/08/12/make-a-useful-commit-message-from-composer-update-output/)
[7] [https://open-vsx.org](https://open-vsx.org/extension/jim-ki-do/continue-commit-notes)
[8] [https://www.continue.dev](https://www.continue.dev/hirahmatdev/conventional-commits-generator)
[9] [https://github.com](https://github.com/intel/ipex-llm/blob/main/docs/mddocs/Quickstart/continue_quickstart.md)

------------------------------

## Other prompts

Here are several high-utility, production-grade custom prompts tailored for your configuration. These are designed to be concise, minimize output token overhead (critical for keeping your RTX 3050 fast), and leverage the strict formatting your workspace uses. [1]

* Pair Prompts to the Right Model via Slash Commands: When running these inside Continue, use the model dropdown or keyboard shortcuts to map the task to the right tool:
* Run /refactor-dry or /doc-api using the Qwen2.5-Coder 3B [CHAT-FAST] model. It handles syntax adjustments instantly without risking VRAM limits.
   * Run /review or /sql-optimize using DeepSeek-R1 8B or Gemma 2 9B. These logical deep-dive models are slower, but their reasoning engines excel at locating architectural flaws.
* Keep Output Ceilings Tight: Notice that every prompt explicitly demands "Output ONLY the code" or "Use a dense markdown table". This is done deliberately to force the local model to stop generating tokens early, saving massive amounts of compute time on your GPU. [2]

[1] [https://stackoverflow.blog](https://stackoverflow.blog/2025/12/09/ai-is-a-crystal-ball-into-your-codebase/)
[2] https://prompts.danielrosehill.com

### Framework Templates

To build a highly specialized framework template, we want to target your exact stack. Since languages have vastly different optimization rules (e.g., React needs memoization fixes, Go needs explicit error handling, and Python needs vectorization), here are templates for the three most common ecosystems.

### How to use prompts with context shortcuts (@tags)

To prevent your RTX 3050 from choking when you execute these templates, combine them with precise context modifiers in your Continue chat bar:

   1. @file + /fix-react: Select the exact component file you are working on instead of your whole directory.
   2. Highlight Code + Ctrl+I: Instead of using the chat box, highlight a messy function, hit Ctrl+I (or Cmd+I on Mac), type /fix-python, and press Enter. This will perform an in-place code modification, allowing you to view an inline diff comparison directly in your active file.

Here is a complete, production-grade library of hyper-targeted quick-fix prompts designed for your exact technology list.
Every prompt is engineered to be token-efficient (forcing code-only outputs or tight markdown tables) to keep your RTX 3050 8GB running at maximum generation speed.
Copy and paste the blocks you need directly into your prompts array inside your configuration file:

### Model Fit Matrix for 8GB VRAM

Here is the optimal model allocation blueprint for each programming ecosystem, specifically tailored to maximize performance and avoid CPU fallback on your RTX 3050 8GB GPU.

| Ecosystem / Prompt | Best Model Match | RAM/VRAM Reason |
|---|---|---|
| React + Vite + Express | Qwen2.5-Coder 3B [CHAT-FAST] | Multi-file web stacks require frequent updates; 3B generates fast without memory stutter. |
| Next.js (App Router) | Qwen2.5-Coder 7B [AGENT/CHAT] | Complex framework logic requires a 7B engine to correctly map hybrid Server/Client boundaries. |
| Express Node.js (TS/JS) | Qwen2.5-Coder 3B [CHAT-FAST] | Middleware patterns are structurally simple; 3B completes them almost instantly. |
| Zod Schema Generation | Qwen2.5-Coder 3B [CHAT-FAST] | Translating interfaces to runtime validators is a highly predictable task well suited for 3B. |
| Django (Python) | DeepSeek-R1 8B [CHAT-REASONING] | Finding implicit database N+1 query loops needs a strong logical reasoning engine. |
| Flask (Python) | DeepSeek-R1 8B [CHAT-REASONING] | DeepSeek handles state evaluation and explicit context isolation safely. |
| Spring Boot (Java) | Google Gemma 2 9B [CHAT-COMPILER] | Gemma 2 excels at processing rigid class typing and heavy boilerplate syntax. |
| Rust | Google Gemma 2 9B [CHAT-COMPILER] | The strict compiler and borrow checker demand the raw intelligence of Gemma 2. |
| Scala | Meta Llama 3.1 8B [CHAT-DOCS] | Llama 3.1 balances complex functional structures with clean documentation syntax. |
| C++ | Google Gemma 2 9B [CHAT-COMPILER] | Managing pointers and raw memory requires a model optimized for explicit code precision. |

#### TypeScript / React & Next.js Quick-Fix

Best paired with: Qwen2.5-Coder 7B (for component layout) or Qwen2.5-Coder 3B (for rapid inline style adjustments).

#### Python (FastAPI / Data Processing) Quick-Fix

Best paired with: DeepSeek-R1 8B (excellent at algorithmic logic and vector math parsing).

#### Go (Golang Backend) Quick-Fix

Best paired with: Google Gemma 2 9B [CHAT-COMPILER] (highly literal, great at pointers and structure layout).

#### React + Vite + Express (Fullstack SPA)

* Best Local Model Match: Qwen2.5-Coder 3B [CHAT-FAST] (keeps operations rapid and snappy).

#### Next.js (App Router / Hybrid)

* Best Local Model Match: Qwen2.5-Coder 7B [AGENT/CHAT] (handles complex hybrid state mapping flawlessly).

#### Express Node.js (Standalone Backend)

* Best Local Model Match: Qwen2.5-Coder 3B [CHAT-FAST] (perfect for fast middleware restructuring).

#### Django (Monolith / REST Framework)

* Best Local Model Match: DeepSeek-R1 8B [CHAT-REASONING] (excellent for locating complex ORM bugs).

#### Flask (Micro-services / Small Apps)

* Best Local Model Match: DeepSeek-R1 8B [CHAT-REASONING] (great at logic verification within minimalist codebases).

#### Spring Boot (Java Enterprise)

* Best Local Model Match: Google Gemma 2 9B [CHAT-COMPILER] (handles rigid type declarations and deep inheritance structures very well).

#### Rust (Systems Programming)

* Best Local Model Match: Google Gemma 2 9B [CHAT-COMPILER] (great at working with the strict borrow checker).

#### Scala (Functional / Data Systems)

* Best Local Model Match: Meta Llama 3.1 8B [CHAT-DOCS] (balances deep functional constructs with structured explanations if required).

#### C++ (Systems / Performance Critical)

* Best Local Model Match: Google Gemma 2 9B [CHAT-COMPILER] (highly literal, great at identifying unmanaged memory bugs).

### Critical Operational Guideline for Your Setup

Because Gemma 2 9B and DeepSeek-R1 8B push the upper boundaries of your 8GB card, never run an aggressive multi-file search (@codebase) while using them.

* Use Qwen 3B/7B when you need to load broader project contexts into memory.
* Use Gemma 9B/DeepSeek 8B exclusively with targeted code highlights (Ctrl + I) or single files (@file) to prevent severe system lag.

### Allocation Tip for Your Machine:

To quickly run these specific prompts in VS Code using Continue, highlight the segment of code you want to touch, hit Ctrl + I (or Cmd + I), type the shortcut name (e.g., /fix-rust or /fix-next), and press Enter. This will run the instruction as an inline diff change on your screen, which bypasses the heavier chat layout to save system memory.
