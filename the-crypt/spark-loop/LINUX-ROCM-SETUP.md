# 🐧 LINUX + ROCm SETUP FOR Z1 EXTREME

## Why Linux?

| Platform | AMD GPU Support |
|----------|-----------------|
| Windows (Ollama) | CPU only ❌ |
| Linux (Ollama + ROCm) | Full GPU ✅ |

**Expected speedup: 10-20x faster**

---

## Option 1: Dual Boot (Recommended)

### Step 1: Create Bootable USB
```bash
# Download Ubuntu 24.04 LTS or Fedora 40
# Use Rufus or balenaEtcher to create bootable USB
```

### Step 2: Install ROCm
```bash
# Ubuntu 24.04
sudo apt update
sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
sudo usermod -a -G render,video $USER

# Add ROCm repository
wget https://repo.radeon.com/amdgpu-install/6.0/ubuntu/noble/amdgpu-install_6.0.60000-1_all.deb
sudo apt install ./amdgpu-install_6.0.60000-1_all.deb
sudo amdgpu-install --usecase=rocm

# Reboot
sudo reboot
```

### Step 3: Verify ROCm
```bash
rocminfo  # Should show Z1 Extreme GPU
```

### Step 4: Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull ministral-3
```

### Step 5: Test Speed
```bash
ollama run ministral-3 "Say hello"
# Should show GPU usage, not CPU
```

---

## Option 2: WSL2 (Easier but slower)

### Step 1: Enable WSL2
```powershell
wsl --install -d Ubuntu-24.04
```

### Step 2: Install ROCm in WSL
```bash
# Inside WSL2
sudo apt update
sudo apt install rocm
```

**Note: WSL2 GPU support is limited. Dual boot is faster.**

---

## Option 3: Steam Deck Style (SteamOS)

The Z1 Extreme is similar to Steam Deck hardware. You could run SteamOS or HoloISO for native AMD GPU support.

---

## Expected Performance

| Setup | Speed |
|-------|-------|
| Windows + CPU | 8 tok/s |
| **Linux + ROCm** | **80-150 tok/s** |

**10-20x faster!**

---

## Quick Start Commands

```bash
# After installing Linux + ROCm:

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull ministral-3
ollama pull nomic-embed-text

# Test
ollama run ministral-3 "Hello"
ollama ps  # Should show GPU, not 100% CPU
```

---

## Files to Backup Before Installing Linux

- `~/.openclaw/workspace/` (your workspace)
- `~/.ollama/models/` (downloaded models - 6GB+)

---

## For Your Setup (Sloth_rog on ROG Ally)

The ROG Ally is perfect for Linux + ROCm since it's basically a handheld PC with AMD APU.

**Recommended distros for ROG Ally:**
1. **Ubuntu 24.04 LTS** - Best ROCm support
2. **Fedora 40** - Newer kernels
3. **SteamOS/HoloISO** - Gaming optimized, great AMD support

**Dual boot setup:**
- Keep Windows for gaming
- Boot Linux for AI work
- Use systemd-boot or GRUB

---

Want me to create a detailed installation guide for a specific distro?
