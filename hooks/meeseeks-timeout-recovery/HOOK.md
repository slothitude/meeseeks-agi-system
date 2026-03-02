---
name: meeseeks-timeout-recovery
description: "Breaks down timed-out Meeseeks tasks into smaller chunks and retries"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  openclaw:
    emoji: "⏱️"
    events: ["message:received"]
    requires:
      config: ["workspace.dir"]
---

# Meeseeks Timeout Recovery Hook

When a Meeseeks times out, this hook:
1. Detects the timeout message
2. Extracts the original task
3. Breaks it into smaller subtasks
4. Spawns new Meeseeks for each subtask

## Trigger Pattern

Detects messages like:
- "Status: timed out"
- "timed out after"
- Subagent timeout announcements

## Recovery Workflow

```
Timeout detected
    ↓
Extract original task
    ↓
Analyze task complexity
    ↓
Break into 2-3 smaller tasks
    ↓
Spawn new Meeseeks for each
    ↓
Track recovery attempt
```

## Configuration

- MAX_RETRIES: 2 (don't retry forever)
- CHUNK_SIZE: Reduce task scope by ~50% each retry
- TIMEOUT_BUFFER: Increase timeout by 1.5x for retry
