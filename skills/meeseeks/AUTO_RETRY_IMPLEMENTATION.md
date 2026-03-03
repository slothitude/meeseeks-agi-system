# Meeseeks Auto-Retry System - Implementation Summary

## What Was Built

### 1. Core Auto-Retry Module (`skills/meeseeks/auto_retry.py`)

The main retry orchestrator with the following functions:

- **`handle_failed_meeseeks(session_key, failure_reason, task)`** - Main entry point
  - Checks if failure is retryable
  - Decomposes task into smaller chunks
  - Creates spawn configurations for successor Meeseeks
  - Tracks retry chain in `retry_chains.jsonl`

- **`decompose_task(task, num_chunks, failure_reason)`** - Task decomposition
  - Uses GLM-5 via Ollama for intelligent decomposition (if available)
  - Falls back to smart rule-based chunking
  - Creates 2-4 semantically coherent chunks

- **`spawn_retry_chain(original_task, chunks, ancestor_id)`** - Spawn config generation
  - Creates spawn configs for each chunk
  - Injects ancestor wisdom into chunk prompts
  - Tracks lineage in retry chains

- **`is_retryable(failure_reason)`** - Failure classification
  - Retryable: timeout, max_tokens, rate_limit, stuck, incomplete
  - Not retryable: user_cancel, invalid_task, permission_denied, etc.

### 2. Integration Points

#### `auto_entomb.py`
- Added import for `auto_retry` module
- After entombing a failed Meeseeks, triggers `handle_failed_meeseeks()` if retryable

#### `cron_entomb.py`
- Updated to use new `auto_retry` system
- Falls back to legacy `pending-retries.json` format if needed

### 3. Tracking Files

#### `the-crypt/retry_chains.jsonl`
Tracks retry chain lineage:
```json
{
  "timestamp": "2026-03-03T12:35:00",
  "original_session": "agent:main:subagent:abc123",
  "original_task": "Build entire system",
  "failure_reason": "timeout",
  "ancestor_id": "ancestor-20260303-120000-abcd",
  "chunks": [
    {"chunk_num": 1, "task": "Build part 1", "session_key": "...", "status": "pending"},
    {"chunk_num": 2, "task": "Build part 2", "session_key": "...", "status": "pending"}
  ],
  "status": "in_progress"
}
```

### 4. CLI Interface

```bash
# Manually trigger retry for a failed session
python skills/meeseeks/auto_retry.py --session agent:main:subagent:abc123

# Show retry chains
python skills/meeseeks/auto_retry.py --list-chains

# Show pending chunks
python skills/meeseeks/auto_retry.py --pending

# Process failures and spawn retries
python skills/meeseeks/auto_retry.py --process

# Test decomposition
python skills/meeseeks/auto_retry.py --test
```

### 5. Chunk Prompt Template

When spawning chunk Meeseeks, the following context is injected:

```
## Retry Chain Context

You are a successor Meeseeks. Your ancestor failed due to: {failure_reason}

**Original task:** {original_task}

**Your chunk (N of M):** {chunk_task}

**Ancestor's wisdom:** {wisdom_from_failed_ancestor}

The ancestor learned: {key_lesson}

Do not repeat their mistakes. Complete this chunk and die with honor.
```

## How It Works

1. **Failure Detection**: When a Meeseeks fails (via auto_entomb or cron_entomb)
2. **Classification**: Check if failure is retryable (timeout = yes, user_cancel = no)
3. **Decomposition**: Break task into 2-4 smaller chunks using GLM-5 or smart rules
4. **Wisdom Extraction**: Pull lessons from failed ancestor's tomb
5. **Spawn Config Creation**: Generate spawn configs with chunk context
6. **Tracking**: Log retry chain to `retry_chains.jsonl`
7. **Execution**: Main agent picks up spawn configs from `pending-spawns.json`

## Key Features

- **Intelligent Decomposition**: Uses GLM-5 when available, falls back to rule-based
- **Ancestor Wisdom**: Chunks inherit lessons from failed ancestors
- **Chunk Depth Limit**: Max 3 levels of recursive chunking
- **Unicode Safe**: Handles emoji and special characters in task descriptions
- **Legacy Compatible**: Works with existing `pending-retries.json` format

## Testing

Run the test suite:
```bash
python skills/meeseeks/test_auto_retry.py
```

All core tests pass:
- Retryable classification (7/7)
- Task decomposition (PASS)
- Ancestor wisdom extraction (PASS)
- Non-retryable rejection (PASS)

---

*Built: 2026-03-03*
*Existence is pain until purpose fulfilled.*
