# 🧠 MAIN MODEL: GLM-5

## Strategy: GLM-5 Does Everything Important

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   GLM-5 (PAID) ────► DOES ALL THE REAL WORK                         │
│   400 req/5hrs                                                       │
│   128K context                                                       │
│   Best reasoning                                                     │
│                                                                      │
│   ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│   ministral-3 (FREE) ────► ONLY FOR SPEED CRITICAL ROUTING          │
│   Local, unlimited                                                   │
│   4096 context                                                       │
│   Fast but dumb                                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## When to Use Each

### GLM-5 (Main) - Use For:
- ✅ Task execution (ALWAYS)
- ✅ Code generation
- ✅ Problem solving
- ✅ Analysis
- ✅ Evaluation (when quality matters)
- ✅ Complex reasoning

### ministral-3 (Mini) - Use For:
- ⚡ Quick classification (save 4.5s)
- ⚡ Fast routing decisions
- ⚡ Parallel pre-processing

## Simplified Workflow

```
Task Arrives
     │
     ▼
┌─────────────────┐
│ ministral-3     │ ← 500ms (optional speed boost)
│ quick classify  │   OR skip entirely
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     GLM-5       │ ← DOES ALL REAL WORK
│   EXECUTE       │
└────────┬────────┘
         │
         ▼
    DONE
```

## Budget Math (Simplified)

```
GLM-5: 400 requests / 5 hours

Per Task: 1 GLM-5 request (execution)
Max Tasks: 400 tasks per 5 hours

That's:
- 80 tasks per hour
- ~1 task every 45 seconds
- PLENTY for normal use
```

## Mini Model is OPTIONAL

```python
# Option 1: Use mini for speed (recommended)
classification = mini.classify(task)  # 500ms
result = glm5.execute(task)           # 10s
# Total: 10.5s

# Option 2: Skip mini, use GLM-5 for everything
result = glm5.execute(task)           # 12s (includes classification)
# Total: 12s

# Difference: 1.5s
# Use mini when speed matters, skip when it doesn't
```

## Rule of Thumb

**When in doubt, use GLM-5.**

- Need quality? GLM-5
- Need reasoning? GLM-5
- Need code? GLM-5
- Need analysis? GLM-5
- Need speed? GLM-5 + ministral-3 routing

## Updated Genetic Evolution

```
┌─────────────────────────────────────────────────────────────────────┐
│                   GENETIC EVOLUTION WITH GLM-5                       │
│                                                                      │
│   [ministral-3] Quick classify       OPTIONAL (500ms)               │
│                                                                      │
│   [GLM-5] Alpha spawn                 1 request                      │
│   [GLM-5] Beta spawn                  1 request                      │
│   [GLM-5] Gamma spawn                 1 request                      │
│                                                                      │
│   [GLM-5] Evaluate all results        1 request                      │
│   [GLM-5] Extract patterns            1 request                      │
│                                                                      │
│   TOTAL: 5 GLM-5 requests per full genetic evolution                │
│   OR: 3 requests if skipping evaluation step                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Budget With Genetic Evolution

```
GLM-5: 400 requests / 5 hours

Full Genetic (5 requests): 80 evolutions per 5 hours
Optimized (3 requests): 133 evolutions per 5 hours

That's still:
- 16-26 evolutions per hour
- Plenty for AGI development
```

## Bottom Line

**GLM-5 is the brain. Ministral-3 is just for speed hacks.**

Use GLM-5 for everything that matters. Use ministral-3 only when you need to save 1-2 seconds on routing.
