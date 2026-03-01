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

