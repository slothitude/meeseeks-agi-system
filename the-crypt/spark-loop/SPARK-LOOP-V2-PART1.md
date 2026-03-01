# 🧬 SPARK LOOP V2 - Part 1: Bottleneck Analysis

**Date:** 2026-03-01
**Focus:** Speed optimization with GLM-4.7-Flash

---

## Current Bottlenecks

### 1. Rate Limit Ceiling (CRITICAL)
- Max 2 concurrent GLM-4.7-Flash requests
- 3rd request → 429 error → fallback to phi3:mini (66-266x slower)
- **Impact:** Serial execution forced, parallel potential wasted

### 2. GLM-5 Budget Constraint
- 400 requests / 5 hours = ~133 generations max
- Each generation needs 3 GLM-5 calls (Alpha + Beta + Gamma)
- **Impact:** Hard ceiling on evolution cycles per session

### 3. Sequential Pipeline
- Current: Classify → Mutate → Spawn ×3 → Evaluate → Entomb
- GLM-4.7-Flash idle during GLM-5 execution (~500ms windows)
- **Impact:** Wasted time between operations

---

## 3 Proposed Improvements

### ⚡ Improvement 1: Request Batching

**Problem:** Each mini operation is a separate API call.

**Solution:** Batch similar operations into single requests:
```python
# OLD: 3 separate calls (~9ms total)
classify(task)      # 3ms
fitness(result)     # 3ms
patterns(result)    # 3ms

# NEW: 1 batched call (~3ms total)
batch_analyze([task, result, result], ops=["classify", "fitness", "patterns"])
```

**Speed Gain:** 3x faster for mini operations
**Rate Limit Benefit:** 3x fewer API calls = fewer 429 errors

---

### 🎯 Improvement 2: Classification Cache

**Problem:** Similar tasks re-classified every time (3ms each).

**Solution:** LRU cache with semantic hashing:
```python
cache = LRUCache(maxsize=1000)

def cached_classify(task):
    # Hash task by intent, not exact text
    key = semantic_hash(task)  # "fix bug in auth" → same hash as "repair authentication issue"
    
    if key in cache:
        return cache[key]  # 0ms
    
    result = glm_flash.classify(task)  # 3ms
    cache[key] = result
    return result
```

**Speed Gain:** ~80% of routine classifications → 0ms (cache hit)
**Rate Limit Benefit:** Dramatically fewer API calls

---

### 🔄 Improvement 3: Parallel Pipeline

**Problem:** GLM-4.7-Flash sits idle during GLM-5 execution.

**Solution:** Overlap operations across generations:
```
Timeline (BEFORE):
Gen 1: [Flash: classify] → [GLM-5: spawn] → [Flash: eval] → [Flash: entomb]
                                        ↑
                                   Flash idle 500ms

Timeline (AFTER):
Gen 1: [Flash: classify] → [GLM-5: spawn] → [Flash: eval] → [Flash: entomb]
                                 ↓ parallel ↓
Gen 2:     [Flash: pre-classify next batch while waiting...]
```

**Implementation:**
- While GLM-5 executes Alpha spawn, Flash pre-classifies next generation candidates
- While GLM-5 executes Beta spawn, Flash evaluates previous Alpha results
- Pipeline never stalls

**Speed Gain:** ~40% reduction in generation cycle time
**Throughput:** +60% generations per session

---

## Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Mini ops per generation | ~15ms | ~5ms | 3x faster |
| API calls per 100 gens | 300 | ~100 | 3x fewer |
| Cache hit rate | 0% | ~80% | Massive |
| Generation cycle time | ~1.5s | ~0.9s | 40% faster |
| Max generations/5hrs | 133 | ~213 | +60% |

---

## Next Steps

1. Implement batch_analyze() wrapper for GLM-4.7-Flash
2. Add semantic_hash() + LRU cache for classifications
3. Refactor pipeline to support overlapped execution
4. Benchmark V2 vs V1

**Goal:** 500x speed improvement maintained, 3x efficiency gain on API usage.
