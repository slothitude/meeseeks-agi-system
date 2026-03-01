# Meeseeks Timeout Fixes

## Problem

Meeseeks are timing out because `goose run -t "..."` spawns a full session each time, taking 10-30+ seconds per call.

## Solution: Use Native Tools First

### Tier 1: Native Tools (FAST - < 1 second)
```
read, write, edit, exec, web_fetch, browser
```
**Use for:** All file operations, shell commands, web fetching

### Tier 2: MCP via Gooser (SLOW - 10-30+ seconds)
```
goose run -t "Use mcpdocker/..." --no-session
```
**Use for:** Knowledge Graph operations ONLY when needed

### Tier 3: MCP via Claude (SLOWEST - 30-60+ seconds)
```
claude -p "..."
```
**Avoid unless absolutely necessary**

## Timeout Guidelines

| Task Type | Timeout | Tools |
|-----------|---------|-------|
| Simple file ops | 30s | Native only |
| Code analysis | 60s | Native + exec |
| Research | 120s | Native + web_fetch |
| MCP operations | 180s | Include goose run |
| Complex with MCP | 300s | Multiple MCP calls |

## Fast Template

Created: `skills/meeseeks/templates/fast.md`

This template tells Meeseeks to:
- Use native tools
- Avoid MCP wrappers
- Complete tasks quickly
- Report and exit if stuck

## MCP Batching

Instead of:
```bash
goose run -t "Use mcpdocker/create_entities..." --no-session
goose run -t "Use mcpdocker/add_observations..." --no-session
goose run -t "Use mcpdocker/read_graph..." --no-session
```

Do:
```bash
goose run -t "Do all of these:
1. Create entity X with observations [...]
2. Add observations to Y [...]
3. Read the full graph
Return all results in one response." --no-session
```

## Root Cause

The `goose run` command:
1. Starts new Python process
2. Loads extensions (10+ seconds)
3. Connects to MCP servers (5-10 seconds)
4. Finally executes the command

Each call repeats steps 1-3.

## Future Fix

A persistent Gooser session would solve this:
```python
# Start once
goose_session = start_persistent_goose()

# Reuse for multiple calls
result1 = goose_session.run("command 1")
result2 = goose_session.run("command 2")

# Much faster - no startup overhead
```

But for now: **Use native tools. Avoid MCP. Be fast.**

---

**Speed is a feature.** ⚡
