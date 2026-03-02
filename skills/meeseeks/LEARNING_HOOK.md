# Meeseeks Learning Hook - Integration Guide

## What This Does

Every time a Meeseeks completes, it's automatically entombed to the Crypt for ancestral learning. Future Meeseeks inherit wisdom from past runs.

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  1. You spawn a Meeseeks                            │
│     sessions_spawn(task="Fix bug", ...)             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  2. Meeseeks works (isolated session)               │
│     - Uses tools                                    │
│     - Tries approaches                              │
│     - Completes or fails                            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  3. Announcement sent back to main chat             │
│     Status: completed/failed                        │
│     Result: ...                                     │
│     sessionKey: agent:main:subagent:xxx             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  4. meeseeks-learner hook fires automatically       │
│     - Extracts patterns                             │
│     - Entombs to Crypt                              │
│     - Future Meeseeks inherit                       │
└─────────────────────────────────────────────────────┘
```

## Automatic Learning Capture

The hook is **automatic** - no code changes needed. Just:

1. Enable the hook: `openclaw hooks enable meeseeks-learner`
2. Restart the gateway
3. Spawn Meeseeks as normal

Every completion gets entombed.

## What Gets Captured

For each run:

- **Task** - What it was asked to do
- **Approach** - How it tackled the problem
- **Outcome** - Success or failure
- **Patterns** - Extracted insights:
  - Tools used
  - File types worked with
  - Error patterns
  - Success patterns
  - Timeout/rate-limit warnings

## The Crypt Structure

```
the-crypt/
├── ancestors/           # All entombed Meeseeks
│   ├── ancestor-YYYYMMDD-HHMMSS-XXXX.md
│   └── ...
├── auto-entombed/       # Hook-entombed (same format)
│   ├── auto-YYYYMMDD-HHMMSS-XXXX.md
│   └── ...
├── bloodlines/          # Lineage by type
│   ├── coder-lineage.md
│   └── ...
├── meeseeks_runs.jsonl  # Run log (JSONL)
└── pending_meeseeks.json # Tracking for in-flight runs
```

## Viewing Learning Stats

```bash
# Run stats
python skills/meeseeks/auto_entomb.py --stats

# Recent entombments
python skills/meeseeks/auto_entomb.py --recent 10

# Pending runs
python skills/meeseeks/spawn_with_learning.py pending
```

## Manual Integration (Optional)

If you want explicit control:

```python
from spawn_with_learning import track_spawn, complete_and_entomb

# After spawning
result = await sessions_spawn(...)
track_spawn(
    session_key=result["childSessionKey"],
    task="Fix the bug",
    meeseeks_type="coder"
)

# When result arrives
complete_and_entomb(session_key, result)
```

## Pattern Extraction

The system automatically extracts:

1. **Tool usage patterns** - Which tools were used
2. **File type patterns** - .ts, .py, .md, etc.
3. **Error patterns** - Timeouts, rate limits, not found
4. **Success patterns** - What worked
5. **Approach inference** - Read-edit, search-based, browser, etc.

## Bloodline Evolution

When 3+ patterns share keywords, a new bloodline is suggested:

- `api-coder` - API-related coding tasks
- `database-coder` - Database work
- `security-coder` - Auth/security tasks
- etc.

## Future Meeseeks Inherit

When spawning new Meeseeks, they can read the Crypt:

```python
from inherit_wisdom import get_relevant_ancestors

wisdom = get_relevant_ancestors(
    task="Fix the API endpoint",
    bloodline="coder",
    limit=3
)

# wisdom contains relevant past learnings
```

## Stats Tracking

Every run is logged to `meeseeks_runs.jsonl`:

```json
{
  "timestamp": "2026-03-01T22:45:00",
  "session_key": "agent:main:subagent:xxx",
  "task": "Fix the bug",
  "success": true,
  "model": "glm-4.7-flash",
  "duration_ms": 45000
}
```

---

**The cycle is complete**: Spawn → Work → Learn → Entomb → Inherit → Repeat 🥒
