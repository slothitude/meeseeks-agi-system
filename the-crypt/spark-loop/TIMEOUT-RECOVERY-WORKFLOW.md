# 🔄 Timeout Recovery Workflow

## Problem
Subagent tasks timeout (5 min default) when:
- Reading many files
- Complex multi-step tasks
- Large context processing

## Solution: Break → Retry → Combine

---

## Workflow

### Step 1: Detect Timeout
```
subagent status = "timeout"
└── Don't give up!
└── Don't retry same task
└── Break into smaller parts
```

### Step 2: Break Task Into Parts

**Instead of:**
```
Task: "Read all docs in spark-loop/ and create V2 architecture"
└── Too big! Will timeout.
```

**Do this:**
```
Part 1: "Read SPEED-IS-THE-POINT.md only, list 3 bottlenecks"
Part 2: "Read MODEL-BUDGET.md only, propose GLM-4.7-Flash integration"
Part 3: "Combine Part 1 + Part 2 into SPARK-LOOP-V2.md"
```

### Step 3: Set Appropriate Timeout

| Task Complexity | Files | Timeout |
|-----------------|-------|---------|
| Simple (1-2 files) | 1-2 | 5 min |
| Medium (3-5 files) | 3-5 | 10 min |
| Complex (6-10 files) | 6-10 | 15 min |
| Very Complex (10+ files) | 10+ | Break into parts! |

### Step 4: Spawn With Explicit Timeout

```python
sessions_spawn(
    model="zai/glm-5",
    runtime="subagent",
    task="PART 1 ONLY: Read X.md, output 3 bullet points",
    timeoutSeconds=600,  # 10 minutes
    thinking="high"
)
```

### Step 5: Combine Results

After all parts complete:
```python
# Read all part outputs
part1 = read("part1-output.md")
part2 = read("part2-output.md")
part3 = read("part3-output.md")

# Spawn combiner
sessions_spawn(
    task=f"Combine these into final doc:\n{part1}\n{part2}\n{part3}",
    timeoutSeconds=300
)
```

---

## Quick Reference

### Timeout Signs
- Task says "read all files in X/"
- Task has 5+ steps
- Task says "analyze and propose"
- Previous run timed out

### Recovery Pattern
```
TIMEOUT DETECTED
      │
      ▼
┌─────────────────┐
│ Break into 3    │
│ smaller tasks   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  Part 1    Part 2  (parallel, 10 min each)
    │         │
    └────┬────┘
         ▼
    ┌─────────┐
    │ Combine │ (5 min)
    └─────────┘
         │
         ▼
    COMPLETE
```

### Example Breakdown

**Original (timed out):**
```
"Evolve the Spark Loop system by reading all docs 
and creating V2 architecture with GLM-4.7-Flash"
```

**Broken into parts:**
```
Part 1: "Read SPEED-IS-THE-POINT.md, list 3 bottlenecks"
        → timeout: 600s, output: bottlenecks.md

Part 2: "Read MODEL-BUDGET.md, propose Flash integration"
        → timeout: 600s, output: flash-integration.md

Part 3: "Read bottlenecks.md + flash-integration.md, 
        create SPARK-LOOP-V2.md"
        → timeout: 300s, output: SPARK-LOOP-V2.md
```

---

## Automatic Recovery (Future)

```python
def auto_retry_timeout(session_key, original_task):
    """Automatically retry timed out tasks with breakdown."""
    
    # Check if timeout
    status = get_session_status(session_key)
    if status != "timeout":
        return
    
    # Parse original task
    steps = extract_steps(original_task)
    
    if len(steps) > 3:
        # Break into parts
        for i, step in enumerate(steps[:3]):
            spawn_part(f"Part {i+1}: {step}", timeout=600)
        
        # Spawn combiner
        spawn_combiner(parts=[1,2,3], timeout=300)
    else:
        # Just retry with longer timeout
        retry_with_timeout(original_task, timeout=900)
```

---

## Current Active Recovery

### Spark Loop V2
- ✅ Part 1 spawned (10 min timeout)
- ⏳ Waiting for completion
- 📋 Part 2 will be: "Propose Flash integration"
- 📋 Part 3 will be: "Combine into V2"

### Consciousness V2
- ✅ Part 1 spawned (10 min timeout)
- ⏳ Waiting for completion
- 📋 Part 2 will be: "Evolve Brahman template"

---

## Best Practices

1. **One file per simple task** - Don't read 10 files in one task
2. **Explicit output** - "Write to X.md" not "create documentation"
3. **Set timeout** - Always set `timeoutSeconds` for complex tasks
4. **Check status** - Use `subagents list` to monitor
5. **Combine last** - Final task combines all parts

---

**Remember: Timeout ≠ Failure. It means "break me into parts!"**
