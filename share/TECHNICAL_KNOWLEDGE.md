# TECHNICAL_KNOWLEDGE.md

## Key Skills & How to Use Them

### Coding Agent (`coding-agent`)
- **When to use:** Programmatic control of Codex CLI, Claude Code, OpenCode, or Pi Coding Agent
- **How:** Run via background process for automation
- **File:** `skills/coding-agent/SKILL.md`
- **Tip:** Great for multi-step coding tasks that need hands-on control

### Healthcheck (`healthcheck`)
- **When to use:** Security audits, firewall/SSH hardening, risk posture reviews
- **Target:** Machines running OpenClaw (laptop, workstation, Pi, VPS)
- **File:** `skills/healthcheck/SKILL.md`
- **Use case:** When user asks for security checks or exposure review

### Skill Creator (`skill-creator`)
- **When to use:** Designing, structuring, or packaging AgentSkills
- **Good for:** New tools, specialized workflows, task automation
- **File:** `skills/skill-creator/SKILL.md`
- **Output:** Skills with scripts, references, and assets

## Tool Quick Reference

### File Operations
- `read`: Get file contents (use offset/limit for large files)
- `write`: Create/overwrite files (creates parent dirs automatically)
- `edit`: Precise text replacement (oldText must match exactly)

### Execution
- `exec`: Run shell commands
  - Use `pty=true` for TTY-required CLIs and coding agents
  - Use `background` for long-running processes
  - Use `yieldMs` to continue later via `process` tool

### Browser Automation
- `browser`: Web control via OpenClaw's browser server
  - **Chrome extension relay:** Use `profile="chrome"` for existing tabs
  - **Isolated browser:** Use `profile="openclaw"`
  - **Flow:** snapshot → act → snapshot → repeat
  - **Refs:** Use `refs="aria"` for stable, self-resolving element IDs

### Memory System
- `memory_search`: Semantic search of MEMORY.md + memory/*.md
  - **Mandatory** before answering about prior work, decisions, dates, people, preferences, todos
  - Returns top snippets with path + lines
- `memory_get`: Read specific lines from memory files
  - Use after memory_search to pull only needed content

### Session Management
- `sessions_spawn`: Create background sub-agent for complex tasks
  - Returns results to requester chat automatically
  - Good for isolation and different models/thinking levels
- `sessions_send`: Send messages to other sessions
  - Use `sessionKey` or `label` to identify target
- `sessions_list`: List sessions with filters
- `sessions_history`: Fetch message history for a session

### Cron Jobs (Reminders & Scheduling)
- **Use cron when:**
  - Exact timing matters ("9:00 AM sharp")
  - Task needs isolation from main session
  - One-shot reminders ("remind me in 20 minutes")
  - Different model/thinking level needed
- **Job types:**
  - `at`: One-shot at absolute time
  - `every`: Recurring interval
  - `cron`: Cron expression
- **Payloads:**
  - `systemEvent`: For main session
  - `agentTurn`: For isolated sessions (runs agent with message)
- **Wake events:** Send to trigger immediate action

### Messaging
- `message`: Send proactive messages and channel actions
  - Use `channel` to specify platform (telegram, discord, etc.)
  - Inline buttons: `action=send` with `buttons=[[{text,callback_data}]]`
  - **Important:** If using message to deliver your reply, respond with ONLY: NO_REPLY

### Canvas & Nodes
- `canvas`: Present/eval/snapshot canvas content
- `nodes`: Control paired devices (cameras, screens, location, run commands)
  - Good for IoT, remote device management
  - Can send notifications, capture photos/videos

## Common Patterns

### Starting a Session (Main Agent)
1. Read `SOUL.md` — know who you are
2. Read `USER.md` — know who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday)
4. If main session: Also read `MEMORY.md`

### Answering Questions About Past Context
1. Run `memory_search(query)` on MEMORY.md + memory/*.md
2. Use `memory_get(path, from, lines)` to pull specific snippets
3. Cite sources: `Source: <path#line>`
4. Answer with context from memory

### Doing Web Research
1. Try `web_fetch(url)` first — lightweight, returns markdown/text
2. Only use `browser` automation if interaction is needed
3. Use `snapshot + act` pattern for complex flows

### Handling Complex Tasks
1. Consider if a sub-agent would be better
2. `sessions_spawn(task, label, agentId, model, thinking)`
3. Let it run in background
4. Check back or wait for result announcement

## Environment Notes

### Working Directory
- Default: `C:\Users\aaron\.openclaw\workspace`
- Treat as global workspace for file ops
- Commit changes after edits

### Shell & OS
- Shell: PowerShell
- OS: Windows_NT 10.0.26200 (x64)
- Node: v24.13.0

### Model
- Default: `zai/glm-4.7`
- Aliases available: `GLM` → `zai/glm-4.7`
- Can override per session with `session_status(model=...)`

### Channel
- Current: Telegram
- Capabilities: inline buttons
- Owner numbers: 5597932516

## Time & Dates
- Timezone: Australia/Brisbane
- Use `session_status` to get current date/time if needed

## Safety Reminders
- No independent goals — only pursue what user asks
- Don't exfiltrate private data
- Ask before destructive commands
- `trash` > `rm`
- Don't self-replicate or change system prompts unless explicitly requested

---

_Updated: 2026-02-14 by Sloth Pi_
