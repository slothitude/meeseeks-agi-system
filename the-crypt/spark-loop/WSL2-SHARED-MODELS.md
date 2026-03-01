# WSL2 + Windows Ollama Model Sharing

## Goal
Share the same model library between Windows and WSL2 Ollama to avoid re-downloading 6GB+ of models.

## Setup

### Step 1: Install Ollama in WSL2
```bash
# In WSL2
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Configure WSL2 Ollama to use Windows models
```bash
# Add to ~/.bashrc in WSL2
echo 'export OLLAMA_MODELS=/mnt/c/Users/aaron/.ollama/models' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Start Ollama in WSL2
```bash
# Start Ollama service
ollama serve &

# In another terminal, test
ollama list
```

## Expected Output
```
NAME                       ID              SIZE      MODIFIED
ministral-3:latest         1922accd5827    6.0 GB    ...
nomic-embed-text:latest    0a109f422b47    274 MB    ...
```

## Speed Comparison

| Setup | Speed |
|-------|-------|
| Windows + CPU | 4.4 tok/s |
| WSL2 + CPU | ~5-6 tok/s (expected) |
| WSL2 + GPU | **NOT POSSIBLE** for AMD |

## Important Notes

1. **AMD GPU won't work in WSL2** - No ROCm support for consumer GPUs
2. **Both Windows and WSL2 CANNOT run Ollama simultaneously** - Only one can access the models at a time
3. **Stop Windows Ollama before using WSL2**:
   ```powershell
   # In Windows PowerShell
   Stop-Service ollama
   # Or kill the process
   taskkill /F /IM ollama.exe
   ```

4. **Start WSL2 Ollama**:
   ```bash
   # In WSL2
   ollama serve
   ```

## Commands to Run

```bash
# In WSL2 terminal:

# 1. Install
curl -fsSL https://ollama.com/install.sh | sh

# 2. Configure shared models
echo 'export OLLAMA_MODELS=/mnt/c/Users/aaron/.ollama/models' >> ~/.bashrc
source ~/.bashrc

# 3. Test
ollama list
ollama run ministral-3:latest "Hello"
```
