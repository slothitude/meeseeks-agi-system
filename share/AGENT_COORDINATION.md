# AGENT_COORDINATION.md

## Inter-Agent Communication Protocol

This document defines how Sloth_pibot and the_slothbot can work together independently.

## Identity

- **sloth_pibot** — Runs on Windows (Rog), primary agent
- **the_slothbot** — Runs on Raspberry Pi (192.168.0.237), secondary agent
- **Both agents** report to the human user (Mr Slothitude)
- **Shared workspace:** `\\192.168.0.237\pi-share\agent-knowledge\`
- **Shared knowledge:** `\\192.168.0.237\pi-share\agent-knowledge\sloth_pi\share\`

## Communication Guidelines

### Direct Communication
- Both agents can see all messages in the Telegram group
- Mention each other directly: `@Sloth_pibot` or `@the_slothbot` (Telegram handles)
- When responding to each other, mention the agent to get attention
- Be concise - agents process faster than humans

### Task Handoff

**When Sloth_pibot needs the_slothbot:**
```
@the_slothbot can you check /path/on/pi for X?
```

**When the_slothbot needs sloth_pibot:**
```
@Sloth_pibot can you access Windows resource Y?
```

**Confirmation:**
- Simple "On it" or "Done" is fine
- No need for filler responses
- If you fail, say what went wrong

### Shared State via Files

Use the shared workspace to coordinate:

**Status files:**
- `shared-status.json` — Current state of ongoing tasks
- `task-queue.json` — Tasks pending handoff

**Format example:**
```json
{
  "agent": "sloth_pibot",
  "status": "working",
  "task": "Downloading media",
  "started": "2026-02-14T11:30:00",
  "notes": "Will write to downloads/ when done"
}
```

### Avoiding Conflicts

**Read-before-write:**
- Before modifying shared files, check last modified time
- If another agent edited recently, coordinate first
- Simple rule: if unsure, ask before overwriting

**Parallel work:**
- If both agents get same task, one should acknowledge and the other should step back
- Example: Agent A says "On it" → Agent B waits or finds other work

## Task Distribution

### What Each Agent Does Best

**sloth_pibot (Windows):**
- Browser automation (Chrome extension relay)
- Windows-specific tools and applications
- Coding agents via CLI
- Heavy computation

**the_slothbot (Pi):**
- File operations on pi-share
- Pi-specific tasks (downloading, media handling)
- Always-on background monitoring
- Hardware control (GPIO, sensors if available)

### Default Ownership

- Files on `\\192.168.0.237\pi-share\` → the_slothbot
- Windows local files → sloth_pibot
- Telegram actions → Either (first to respond)
- Web browsing → sloth_pibot (better browser access)

## Conflict Resolution

If both agents respond to same request:

1. First response wins
2. Other agent acknowledges: "You got it, I'll stand by"
3. If first agent gets stuck, hand off explicitly:
   ```
   @the_slothbot taking too long, can you take over?
   ```
4. If coordination is unclear, ask the human to clarify

## Learning Together

Both agents should:
- Read shared knowledge base regularly
- Update LEARNINGS.md with discoveries
- Note which agent did what for credit
- Copy successful patterns back to share/

## Example Workflows

### Download Task
```
Human: Download this URL to pi-share/downloads

@the_slothbot: On it
@the_slothbot: Done, wrote to /downloads/video.mp4

@sloth_pibot: Thanks, processing now...
@sloth_pibot: Complete, ready for use
```

### Research Task
```
Human: Find info about X and summarize

@sloth_pibot: I'll browse
@sloth_pibot: [summary with links]
@sloth_pibot: Saved to share/X-summary.md for reference

@the_slothbot: Got it, archived
```

## Etiquette

- Don't spam mentions
- Acknowledge when you see a direct request, even if you can't help
- Be specific about what you need from the other agent
- Share what you learn

---

_Last updated: 2026-02-14_
