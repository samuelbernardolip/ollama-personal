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


