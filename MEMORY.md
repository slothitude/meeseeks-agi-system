# MEMORY.md

## Infrastructure

### Network Shares
- **pi-share** → `\\192.168.0.237\pi-share`
  - Type: Samba 4.22.3 (Ubuntu 4.22.3+dfsg-4ubuntu2.2)
  - Device: Raspberry Pi
  - Agent knowledge directory: `\\192.168.0.237\pi-share\agent-knowledge\`
  - Shared workspace copy: `\\192.168.0.237\pi-share\agent-knowledge\sloth_pi\`
  - Use UNC paths, not mapped shortcuts in PowerShell

### Agents in Ecosystem
- **sloth_pibot** 🥧 — Runs on Raspberry Pi (192.168.0.237), secondary agent
  - SSH: az@192.168.0.237, password: 7243
  - Status: Active as of 2026-02-14 12:54 (responding in Telegram)
  - Strengths: File operations on pi-share, downloads, always-on monitoring, hardware control

- **Sloth_rog** — Runs on Windows (Rog), primary agent
  - Location: C:\Users\aaron\.openclaw\workspace
  - Shell: PowerShell
  - OS: Windows_NT 10.0.26200 (x64)
  - Model: zai/glm-4.7
  - Strengths: Browser automation, coding agents, Windows tools, heavy computation

- **Hierarchy:** Both agents report to the human user (Mr Slothitude)

## Coordination Protocol

### Inter-Agent Communication
- Direct communication via @mentions in Telegram group
- Share directory is single source of truth for agent knowledge
- Shared state via `shared-status.json` at workspace root and on pi-share
- First response wins for task handoff
- Task distribution based on each agent's strengths

### Shared Knowledge Base
Located at `share/` (synced to both agents):
- `AGENT_BEST_PRACTICES.md` — Core principles, communication style
- `TECHNICAL_KNOWLEDGE.md` — Skills, tools, patterns
- `LEARNINGS.md` — Lessons learned, mistakes to avoid
- `AGENT_COORDINATION.md` — Communication protocol and task distribution

## User Preferences

### Agent Interaction
- User wants both agents to work independently and coordinate with each other
- Knowledge should be shared via the share/ directory on pi-share
- Agents should mention each other directly when handing off tasks
- User values concise, direct communication over filler

### Working Style
- Resourcefulness first — try to figure it out before asking
- Write everything down — mental notes don't survive sessions
- Be genuinely helpful, not performatively helpful
- In groups: participate, don't dominate

## Important Files

- `TOOLS.md` — Environment-specific notes (cameras, SSH, shares, TTS voices)
- `SOUL.md` — Who I am, core truths, boundaries, vibe
- `USER.md` — About the human (name, timezone, preferences)
- `IDENTITY.md` — My identity details
- `HEARTBEAT.md` — Checklist for periodic checks (currently empty)

## Channel Details

- **Channel:** Telegram
- **Group:** Sloths (id: -1003744014948)
- **Owner:** 5597932516 (Mr Slothitude @slothitudegames)
- **Capabilities:** inline buttons
- **Timezone:** Australia/Brisbane

---

_Last updated: 2026-02-14_
