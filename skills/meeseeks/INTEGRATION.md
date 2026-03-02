# Auto-Entombment Integration Guide

## Current Status

The `meeseeks-learner` hook is set up, but OpenClaw doesn't yet fire hooks on subagent completion events. The hook will work when that event type is added.

## How to Use Auto-Entombment Now

### Option 1: Manual After Spawn (Recommended)

After a Meeseeks completes, call:

```python
from auto_entomb import auto_entomb

auto_entomb(
    session_key="agent:main:subagent:xxx",
    task="What it was asked to do",
    result={"success": True, "output": "..."},
    meeseeks_type="coder"
)
```

### Option 2: Wrapper Function

```python
from spawn_with_learning import track_spawn, complete_and_entomb

# Track when spawning
result = await sessions_spawn(...)
track_spawn(result["childSessionKey"], task, meeseeks_type)

# When result arrives (in announcement), complete:
complete_and_entomb(session_key, result)
```

### Option 3: Cron-Based Capture

Set up a cron job to scan recent subagent sessions and entomb:

```bash
# Every 5 minutes
*/5 * * * * python ~/.openclaw/workspace/skills/meeseeks/cron_entomb.py
```

## Stats and Monitoring

```bash
# View run stats
python skills/meeseeks/auto_entomb.py --stats

# View recent entombments
python skills/meeseeks/auto_entomb.py --recent 10
```

## Future: Hook-Based Auto-Capture

When OpenClaw adds `subagent:complete` events to hooks, update the hook:

```yaml
# HOOK.md
metadata:
  openclaw:
    events: ["subagent:complete"]  # Future event type
```

For now, use manual/wrapper approaches.

---

_Last updated: 2026-03-01_
