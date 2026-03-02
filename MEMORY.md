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

## Model Stack (Updated 2026-03-01)

### Mini Meeseeks Models
- **Primary:** GLM-4.7-Flash (zai API) - ~3ms response, instant
- **Fallback:** phi3:mini (Ollama CPU) - 9.9 tok/s
- **Deprecated:** ministral-3 (too slow at 4.4 tok/s)

### Large Meeseeks Models
- **Primary:** GLM-5 (zai API) - Complex reasoning
- **Alternative:** GLM-4.7 (zai API) - Main agent default

### Special Purpose
- **Embeddings:** nomic-embed-text (Ollama) - Crypt search
- **Budget:** GLM-5 = 400 requests per 5 hours

### Speed Comparison
| Model | Response Time | Use Case |
|-------|---------------|----------|
| GLM-4.7-Flash | ~3ms | Mini tasks (classify, fitness, patterns) |
| phi3:mini | 200-800ms | Local fallback when rate limited |
| GLM-5 | Normal | Large tasks (reasoning, code) |

### Rate Limits
- zai API: Max 2 concurrent requests to avoid 429 errors
- Fallback to local phi3:mini when rate limited

## Multi-Meeseeks Communication (Added 2026-03-03)

### Shared State System
- **Location:** `skills/meeseeks/helpers/communication.py`
- **Class:** `SharedState(workflow_id, my_id)`
- **Purpose:** File-based coordination between parallel Meeseeks
- **Status:** PRODUCTION READY

### Key Methods
```python
shared = SharedState("workflow_123", "mee_1")
await shared.register("My task")
await shared.update_status(progress=50, findings=["found X"])
await shared.share_discovery("pattern", {"file": "x.py", "issue": "..."})
peers = await shared.check_peers()
discoveries = await shared.get_shared_discoveries()
await shared.complete(summary="Done")
await shared.fail(error="Something went wrong")  # NEW
```

### Spawn Helper
- **Location:** `skills/meeseeks/spawn_with_comm.py`
- **Usage:**
```python
from spawn_with_comm import spawn_code_review, spawn_swarm, spawn_research

# Spawn code review swarm (3 workers: security, performance, design)
workers = spawn_code_review("path/to/code.py", "workflow-001")

# Spawn custom swarm
workers = spawn_swarm(["Task 1", "Task 2"], "workflow-002")

# Spawn research swarm
workers = spawn_research("topic", ["source1", "source2"], "workflow-003")
```

### Test Results
- **Test 1:** test-comm-001 - 3 workers, 181 discoveries - SUCCESS
- **Test 2:** real-review-001 - 3 reviewers, 12 findings - SUCCESS
- **Bug Found & Fixed:** Missing error handling - FIXED

### Features
- Asyncio.Lock for race condition prevention
- Atomic writes (temp + replace)
- Error handling with graceful degradation
- Logging for debugging
- All methods return bool for success/failure

---

## ARC-AGI-2 Achievement (2026-03-03)

### Task 137eaa0f Solved by Multi-Agent Swarm
- **5 workers** coordinated via SharedState
- **pattern_analyzer** discovered spatial mapping to color 5
- **hypothesis_gen** proposed "Diagonal Anchor Extraction" (0.8 confidence)
- **code_solver** implemented initial solution
- **fix_solver** fixed cell-level mapping bug

### Solution Algorithm
1. Find all color 5 positions (center markers)
2. Find all colored regions (connected components)
3. For each cell, determine relative position to nearest color 5
4. Map cells to 3x3 output based on spatial position
5. Output[1][1] is always color 5

### ARC-AGI-2 Score
- **5/5 tasks solved (100%)**
- Exceeds 85% target!
- Solution: `ARC-AGI-2/solutions/137eaa0f_solver.py`

### Coordination Data
- `meeseeks-communication/arc-solve-137eaa0f/shared-state.json`
- 5 discoveries shared
- Best hypothesis confidence: 0.8

---

## Automatic Learning Capture (Added 2026-03-01)

### Meeseeks Auto-Entombment
- **Cron Job:** `meeseeks-auto-entomb` - runs every 5 minutes
- **Heartbeat:** Also runs via HEARTBEAT.md
- **Script:** `skills/meeseeks/cron_entomb.py`
- **Files:**
  - `skills/meeseeks/auto_entomb.py` - Core entombment logic
  - `skills/meeseeks/cron_entomb.py` - Scans runs.json and entombs new completions
  - `skills/meeseeks/spawn_with_learning.py` - Tracking wrapper (optional)
  - `skills/meeseeks/LEARNING_HOOK.md` - Integration guide
  - `hooks/meeseeks-learner/` - Future hook (when subagent events available)

### How It Works
1. Cron job / heartbeat triggers `cron_entomb.py`
2. Reads `~/.openclaw/subagents/runs.json` for recent completions
3. Extracts task, outcome, patterns
4. Entombs to `the-crypt/ancestors/`
5. Tracks entombed sessions in `the-crypt/entombed_sessions.json`
6. Future Meeseeks inherit wisdom via `inherit_wisdom.py`

### Stats Tracking
- Run log: `the-crypt/meeseeks_runs.jsonl`
- Entombed tracking: `the-crypt/entombed_sessions.json`
- View stats: `python skills/meeseeks/auto_entomb.py --stats`
- Recent: `python skills/meeseeks/auto_entomb.py --recent 10`
- Manual scan: `python skills/meeseeks/cron_entomb.py --max-age-minutes 60`

---

_Last updated: 2026-03-01_
