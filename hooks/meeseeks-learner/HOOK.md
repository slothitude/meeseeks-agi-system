---
name: meeseeks-learner
description: "Auto-entombs completed Meeseeks to the Crypt for ancestral learning"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  openclaw:
    emoji: "🥒"
    events: ["message:received"]
    requires:
      config: ["workspace.dir"]
---

# Meeseeks Learner Hook

Automatically entombs completed Meeseeks to the Crypt when they announce their results.

## What It Does

1. Listens for message:received events
2. Detects subagent completion announcements
3. Extracts session key, task, and result
4. Auto-entombs to the Crypt for ancestral learning
5. Extracts patterns for future Meeseeks to inherit

## The Learning Cycle

```
Meeseeks spawned → Works → Announces completion
                              ↓
                      This hook fires
                              ↓
                      Auto-entomb to Crypt
                              ↓
                      Future Meeseeks inherit wisdom
```

## Configuration

Enable via:

```bash
openclaw hooks enable meeseeks-learner
```

## Requirements

- Python 3.x
- Workspace directory configured
- The `skills/meeseeks/auto_entomb.py` module
