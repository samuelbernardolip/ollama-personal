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

## Generate commit messages

You can generate commit messages using the [Continue AI extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue) in VS Code by using the built-in git context provider or installing a helper utility. [1, 2] 
## Method 1: The Native Slash Command (Standard)
You can reference your active changes directly inside the Continue chat sidebar to build a commit summary: [3] 

   1. Open the Continue chat panel with Ctrl + L (Windows/Linux) or Cmd + L (Mac).
   2. Stage your changes inside the VS Code Source Control panel.
   3. In the chat box, type @git (or @codebase) followed by the /commit slash command.
   4. Press enter, and Continue will analyze your unstaged or staged diff to draft a message.
   5. Copy and paste the output directly into your Git commit input field. [3, 4, 5, 6] 

## Method 2: One-Click Integration via Helper Extension
Because the core Continue extension does not yet place a native "sparkle" button inside the Git panel, community plugins resolve this behavior: [1] 

   1. Install the [Continue Commit Notes](https://marketplace.visualstudio.com/items?itemName=jim-ki-do.continue-commit-notes) companion extension from the VS Code Marketplace.
   2. Open the Source Control Panel (Ctrl + Shift + G / Cmd + Shift + G).
   3. Hover your cursor over the Changes or Staged Changes title row.
   4. Click the "C" logo icon that appears inline, or execute Continue Commit: Generate Commit Message from the Command Palette (Ctrl + Shift + P).
   5. The extension leverages your existing config.json model to automatically fill your VS Code commit text box. [1, 5, 7] 

## Method 3: Customize the Rules in config.json
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

