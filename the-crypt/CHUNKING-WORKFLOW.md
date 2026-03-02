# Task Chunking Workflow

## Visual Flow

```
┌─────────────────────┐
│  Task Execution     │
│  (Main Session)     │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  Completed?  │───── YES ─────▶ Entomb to Crypt
    └──────┬───────┘
           │ NO (timeout)
           ▼
    ┌──────────────────┐
    │ Check Chunk Depth│
    │   depth < 3?     │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐      ┌─────────────────────┐
    │   Parse Task     │─────▶│ Extract Structure   │
    │   Structure      │      │ - Steps             │
    └──────┬───────────┘      │ - Dependencies      │
           │                  │ - Outputs           │
           ▼                  └─────────────────────┘
    ┌──────────────────┐
    │  Chunk Strategy  │
    │  Selector        │
    └──────┬───────────┘
           │
           ├───── Strategy 1: Split by numbered steps
           ├───── Strategy 2: Split by paragraphs
           └───── Strategy 3: Halve by text length
           │
           ▼
    ┌──────────────────┐
    │  Create Chunks   │
    │  - Add metadata  │
    │  - Track depth   │
    │  - Queue retry   │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Spawn Retries   │
    │  (max 2 concur)  │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Track Results   │
    │  - Success?      │
    │  - Timeout?      │
    │  - Failed?       │
    └──────┬───────────┘
           │
           ├───── SUCCESS ──────▶ Mark chunk done
           │                          │
           │                          ▼
           │                    All chunks done?
           │                          │
           │                     YES │
           │                          ▼
           │                    Task Complete ──▶ Entomb
           │
           ├───── TIMEOUT ──────▶ Go back to top (depth now +1)
           │
           └───── FAILED ───────▶ If depth = 3: Alert for manual review
```

## Decision Tree

```
START: Task timed out
  │
  ├─ Is task already chunked?
  │   │
  │   ├─ NO → First timeout
  │   │        │
  │   │        └─▶ Chunk into 2-3 pieces (depth = 1)
  │   │
  │   └─ YES → Check depth
  │            │
  │            ├─ depth = 1 → Re-chunk (depth = 2)
  │            ├─ depth = 2 → Re-chunk (depth = 3)
  │            └─ depth = 3 → STOP - Manual review needed
  │
  └─ Queue for retry
```

## Chunk Depth Examples

### Depth 0 (Fresh Task)
```
Task: "Read all ancestors, extract tricks, update library, create report"
Runtime: 180s → Timeout
Action: Chunk into smaller pieces
```

### Depth 1 (First Chunk)
```
Chunk 1/3: "Read all ancestors from the-crypt/ancestors/"
Runtime: 120s → Timeout
Action: Re-chunk this piece
```

### Depth 2 (Second Chunk)
```
Chunk 1/2 of Chunk 1/3: "Read first 10 ancestors from the-crypt/ancestors/"
Runtime: 90s → Timeout
Action: Re-chunk again
```

### Depth 3 (Third Chunk - MAX)
```
Chunk 1/2 of Chunk 1/2 of Chunk 1/3: "Read first 5 ancestors"
Runtime: 60s → Timeout
Action: STOP - Manual review required
```

## Retry Queue State Machine

```
         ┌─────────┐
         │ PENDING │ ← New retry added
         └────┬────┘
              │ Spawn
              ▼
         ┌─────────┐
         │ RUNNING │ ← Executing chunk
         └────┬────┘
              │
      ┌───────┼───────┐
      │       │       │
      ▼       ▼       ▼
   ┌──────┐ ┌──────┐ ┌──────┐
   │ DONE │ │TIMEOUT│ │FAILED│
   └──┬───┘ └───┬──┘ └───┬──┘
      │         │        │
      │         │        └─▶ depth < 3? → PENDING
      │         │              depth = 3? → MANUAL_REVIEW
      │         │
      │         └─▶ depth < 3? → PENDING (re-chunk)
      │              depth = 3? → MANUAL_REVIEW
      │
      └─▶ All chunks done? → TASK_COMPLETE
```

## Implementation Checklist

### Core Functions
- [x] `break_task_into_chunks()` - Text-based splitting
- [x] `create_retry_chunks()` - Queue management
- [x] `get_pending_retries()` - Retrieve next chunks
- [x] Chunk depth tracking (max 3)
- [ ] `analyze_task_structure()` - Semantic parsing
- [ ] `detect_dependencies()` - Find step relationships
- [ ] `score_chunk_quality()` - Coherence metric
- [ ] `should_chunk_task()` - Atomic task detection

### Data Structures
- [x] pending-retries.json - Retry queue
- [x] entombed_sessions.json - Tracking
- [ ] chunk-success-log.json - Success metrics
- [ ] retry-patterns.json - Learning data

### Monitoring
- [x] Auto-entombment on completion
- [x] Failure capture system
- [ ] Retry success dashboard
- [ ] Chunk depth visualization
- [ ] Token overhead tracking

## Quick Reference

### Chunk Depth Limits
- **Depth 0:** Fresh task → Can chunk
- **Depth 1:** 1 level of chunking → Can chunk
- **Depth 2:** 2 levels → Can chunk
- **Depth 3:** 3 levels → **STOP**

### Timeout Scaling (Proposed)
- **Depth 0:** Original timeout (180s default)
- **Depth 1:** 120s
- **Depth 2:** 90s
- **Depth 3:** 60s

### Concurrent Limits
- **Max concurrent retries:** 2
- **Max retry attempts:** 3 per chunk

### File Locations
- Retry queue: `the-crypt/pending-retries.json`
- Entombed tracking: `the-crypt/entombed_sessions.json`
- Ancestors: `the-crypt/ancestors/*.md`
- This workflow: `the-crypt/CHUNKING-WORKFLOW.md`
