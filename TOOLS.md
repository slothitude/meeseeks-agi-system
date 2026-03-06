# TOOLS.md - Local Notes

## Network Shares

- **pi-share** → `C:\Users\aaron\AppData\Roaming\Microsoft\Windows\Network Shortcuts\pi-share` (192.168.0.237)
  - Type: Samba 4.22.3-Ubuntu-4.22.3+dfsg-4ubuntu2.2
  - Device: Raspberry Pi
  - Purpose: Shared workspace for agent coordination

## 🎙️ Voice Workflow

### ⚠️ CRITICAL: No Duplicate Audio!

**The TTS tool auto-delivers audio.** Do NOT also use the message tool to send audio.

### Incoming Voice (Transcription)

Use `whisper` to transcribe incoming voice messages:

```bash
whisper <audio_file> --model base
```

### Outgoing Voice (TTS)

**Use the `tts` tool ONLY:**

```
tts(text="Your response here")
```

**❌ WRONG:**
```
tts(text="Response")
message(action="send", buffer=audio_data)  # NO! Creates duplicate
```

**✅ CORRECT:**
```
tts(text="Response")
# Then reply with "NO_REPLY" to avoid duplicate text
```

### Pattern Summary

1. **Transcribe incoming:** Use `whisper`
2. **Respond with voice:** Use `tts` tool ONLY
3. **After TTS:** Reply with NO_REPLY (audio auto-delivered)

## 🥒 Meeseeks Timeout Guidelines

### The Problem

Meeseeks were timing out at 3 minutes because `runTimeoutSeconds` was set too low for complex tasks.

### The Fix

Use appropriate timeout based on task complexity:

| Task Type | Timeout | Example |
|-----------|---------|---------|
| **Simple** | 60-180s | Search, lookup, single file edit |
| **Medium** | 300s | Multi-file changes, debugging |
| **Complex** | 600s | Building systems, architecture |

### Usage

```python
# Simple task (default)
sessions_spawn(task="Search for X", runTimeoutSeconds=180)

# Complex task
sessions_spawn(task="Build entire system", runTimeoutSeconds=600)
```

### Rules of Thumb

- If creating new files from scratch → 600s
- If modifying 3+ files → 300s+
- If just reading/searching → 180s
- When in doubt, go longer

### Why It Matters

- Too short = Meeseeks times out mid-task, wastes tokens
- Too long = Slower feedback loop
- Right size = Task completes, results delivered

**Default to 600s for implementation tasks.**

---

## 🎙️ Voice Transcription (Whisper)

### Installed
- **whisper** (openai-whisper)
- **torch** (CPU version)
- **numba** + **llvmlite** (JIT)

### Usage
```python
import whisper
model = whisper.load_model('tiny')  # or 'base', 'small', 'medium'
result = model.transcribe('audio.ogg')
print(result['text'])
```

### Models
| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| **tiny** | Fastest | Low | Quick transcription |
| **base** | Fast | Medium | General use |
| **small** | Medium | Good | Better accuracy |
| **medium** | Slow | High | Critical transcription |

### Notes
- GPU acceleration (ROCm/DirectML) not available for Python 3.13
- CPU handles short clips fine
- Longer audio = better results

