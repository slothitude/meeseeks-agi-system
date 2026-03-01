# WSL2 GPU SETUP FOR AMD (Z1 EXTREME)

## Current Status
- WSL2 Ubuntu 24.04: ✅ Installed
- GPU access: ❌ Not exposed

## The Problem

WSL2 GPU support for AMD is **limited**. Unlike NVIDIA (CUDA in WSL2), AMD ROCm in WSL2 requires:

1. Windows 11 22H2 or later
2. Specific WSL kernel
3. AMD drivers on Windows side
4. ROCm installed inside WSL

## Option A: Enable AMD GPU in WSL2 (Experimental)

### Step 1: Update Windows Drivers
```powershell
# Download latest AMD drivers for Z1 Extreme
# From: https://www.amd.com/en/support
```

### Step 2: Update WSL
```powershell
wsl --update
wsl --shutdown
```

### Step 3: Install ROCm in WSL
```bash
# Inside WSL
sudo apt update
sudo apt install rocm-libs rocm-dev
echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Test
```bash
rocminfo  # Should show GPU
```

## Option B: Use CPU in WSL (Works Now)

```bash
# Install Ollama in WSL
curl -fsSL https://ollama.com/install.sh | sh

# Pull small model
ollama pull phi3:mini

# Test (will use CPU, but faster than Windows)
ollama run phi3:mini "Hello"
```

## Option C: Use Docker with GPU (If supported)

```bash
# Check if Docker works with GPU
docker run --rm -it --device=/dev/kfd --device=/dev/dri rocm/rocm-terminal
```

## Option D: Full Linux (Best Performance)

Dual boot Ubuntu 24.04 for native ROCm support:
- 10-20x faster than WSL2
- Full GPU access
- Native AMD support

## Quick Test Now

Let's try installing Ollama in WSL and see if it can at least use CPU efficiently:

```bash
# In WSL
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
ollama run phi3:mini "Say hello"
```

---

## Recommendation

| Option | Speed | Effort |
|--------|-------|--------|
| WSL2 + CPU | 10-15 tok/s | Easy |
| WSL2 + GPU (if works) | 50-80 tok/s | Medium |
| **Dual Boot Linux** | **80-150 tok/s** | **Best** |

For development: WSL2 CPU is fine
For production: Dual boot Linux
