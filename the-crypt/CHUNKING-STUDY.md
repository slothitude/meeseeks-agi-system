# Task Chunking Study - 2026-03-02

## Objective
Analyze the task chunking system to create an optimal workflow for retrying timed-out Meeseeks tasks.

## Current System

### How Chunking Works
Location: `skills/meeseeks/cron_entomb.py`

#### Trigger Conditions
- Subagent task times out (status = "timeout")
- Task not already in pending-retries.json
- Chunk depth < 3 (allows 3 levels of nesting)

#### Chunking Strategies (in order)
1. **Split by numbered steps** - Regex: `\d+[.\)]`
2. **Split by paragraphs** - Double newlines `\n\n`
3. **Halve by character count** - Simple mid-point split

#### Retry Configuration
- **Max chunk depth:** 3 levels
- **Max concurrent retries:** 2
- **Chunk timeout:** 120 seconds (shorter than original)
- **Max retry attempts:** 3 per task

### Current Flow
```
Task Execution → Timeout → Check Depth → Chunk → Queue → Spawn → Track
     ↓                                          ↓
   Complete → Entomb                        Retry (depth++)
```

## Issues Identified

### 1. Re-chunking Already Chunked Tasks
**Problem:** Tasks get wrapped in "RETRY CHUNK" headers multiple times
**Example:**
```
RETRY CHUNK 1/2
  RETRY CHUNK 1/2
    RETRY CHUNK 1/2
      Original task
```
**Impact:** Tasks become verbose, hard to parse, waste tokens

### 2. Chunking Quality
**Problem:** Simple text splitting doesn't preserve task coherence
**Example:**
- Original: "Read file X, analyze it, write report to Y"
- Chunk 1: "Read file X, analyze"
- Chunk 2: "it, write report to Y"
**Impact:** Chunks may be incomplete or nonsensical

### 3. No Semantic Understanding
**Problem:** Splitting by steps/paragraphs doesn't understand task dependencies
**Example:** Step 2 might depend on Step 1 output
**Impact:** Chunks fail independently, can't complete overall goal

### 4. Token Overhead
**Problem:** Each retry adds ~200 tokens of "RETRY CHUNK" wrapper text
**Impact:** 3 levels = 600+ tokens of overhead before actual task

## Proposed Improvements

### A. Smart Chunk Detection
Instead of re-wrapping, track chunk metadata separately:
```json
{
  "original_task": "...",
  "chunk_index": 0,
  "total_chunks": 3,
  "chunk_depth": 2,
  "chunk_text": "...",  // Clean chunk without wrappers
  "parent_task_id": "..."
}
```

### B. Semantic Chunking
Before splitting, analyze task structure:
1. Identify dependencies (Step 2 needs Step 1 output)
2. Group related operations
3. Create self-contained chunks
4. Add context for dependent chunks

Example:
```
Chunk 1: "Read file X and analyze patterns. Save analysis to temp file."
Chunk 2: "Read analysis from temp file. Write final report to Y."
```

### C. Progressive Timeout Scaling
Increase timeout for deeper chunks (they're already smaller):
- Depth 1: 120s (current)
- Depth 2: 90s
- Depth 3: 60s

### D. Chunk Success Tracking
Track which chunks completed successfully:
```json
{
  "chunks_completed": [0, 2],
  "chunks_pending": [1],
  "chunks_failed": []
}
```

## Study Questions

### Q1: What types of tasks timeout most?
**Hypothesis:** Complex multi-step tasks (evolution, coding, analysis)
**Data needed:** Analyze pending-retries.json history

### Q2: How effective is current chunking?
**Hypothesis:** 50% of chunked tasks still timeout
**Data needed:** Track retry success rate by depth

### Q3: What's the optimal chunk size?
**Hypothesis:** Chunks should complete in 60-90 seconds
**Data needed:** Analyze successful task runtimes

### Q4: Should some tasks never be chunked?
**Hypothesis:** Yes - tasks requiring atomic operations
**Data needed:** Identify non-chunkable task patterns

## Proposed Workflow

### Phase 1: Detection & Analysis
```
1. Task times out
2. Analyze task type (code/search/evolution/etc)
3. Check if chunkable (atomic operations check)
4. Calculate current depth
5. If depth < 3, proceed to chunking
```

### Phase 2: Smart Chunking
```
1. Parse task structure (steps, dependencies, outputs)
2. Identify natural breakpoints
3. Create self-contained chunks
4. Add context/dependencies to each chunk
5. Estimate chunk complexity (tokens, operations)
```

### Phase 3: Retry Management
```
1. Queue chunks with metadata
2. Spawn chunks concurrently (max 2)
3. Track chunk completion
4. If all chunks succeed → Mark task complete
5. If any chunk fails at depth 3 → Alert for manual review
```

### Phase 4: Learning
```
1. Record chunk success/failure patterns
2. Update chunking heuristics
3. Build library of "good chunk patterns"
4. Share learnings via The Crypt
```

## Implementation Plan

### Step 1: Enhanced Metadata Tracking
- Add chunk_depth to all retry entries
- Track parent-child relationships
- Record chunk success independently

### Step 2: Chunk Quality Analyzer
- Function to score chunk coherence (0-10)
- Detect incomplete chunks
- Suggest better breakpoints

### Step 3: Task Type Detection
- Infer task type from description
- Apply type-specific chunking strategies
- Skip chunking for atomic tasks

### Step 4: Retry Dashboard
- Visual view of retry queue
- Depth tree visualization
- Success rate metrics

## Metrics to Track

1. **Retry Success Rate** by depth (1, 2, 3)
2. **Average Chunks per Task** by type
3. **Time to Complete** chunked vs non-chunked
4. **Token Overhead** from wrappers
5. **Manual Intervention Rate** (depth 3 failures)

## Next Steps

1. Run cron_entomb for 24 hours with current system
2. Collect data on retry patterns
3. Analyze failure modes
4. Implement smart chunking
5. Compare before/after metrics

## Questions for Slothitude

1. Should complex tasks (evolution, ARC-AGI) be chunked at all?
2. Preferred balance: faster retries vs task coherence?
3. Allow manual task tagging (chunkable: yes/no)?
4. Priority system for retry queue?
