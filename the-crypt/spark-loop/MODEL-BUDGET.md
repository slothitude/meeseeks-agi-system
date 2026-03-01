# 💰 MODEL BUDGET STRATEGY

## The Setup

| Model | Purpose | Cost | Speed | Context |
|-------|---------|------|-------|---------|
| **GLM-5** | Heavy lifting | 400 req/5hrs | ~500ms | 128K+ |
| **GLM-4.7-Flash** | Mini tasks | FREE | **~3ms** | 204K |
| phi3:mini (fallback) | Rate limited | FREE | 200-800ms | 4K |
| nomic-embed | Embeddings | FREE | 45ms | 8K |

## Budget Allocation

```
GLM-5: 400 requests per 5 hours
├── 80 per hour
├── ~1.3 per minute
└── USE SPARINGLY - ONLY FOR REAL WORK

GLM-4.7-Flash: UNLIMITED (but rate limited)
├── Classification (~3ms)
├── Fitness evaluation (~3ms)
├── Pattern extraction (~3ms)
├── Summarization (~3ms)
├── Max 2 concurrent requests
└── USE FREELY - IT'S INSTANT

phi3:mini: UNLIMITED (local)
├── Fallback when rate limited
├── 200-800ms response
└── USE WHEN 429 ERROR
```

## When to Use Each Model

### GLM-5 (LIMITED) - Use ONLY For:
- ✅ Complex code generation
- ✅ Deep reasoning and analysis
- ✅ Multi-step architecture
- ✅ Final execution of complex tasks

### GLM-4.7-Flash (INSTANT) - Use For:
- ✅ Task classification (~3ms)
- ✅ Fitness scoring (~3ms)
- ✅ Pattern extraction (~3ms)
- ✅ Summarization (~3ms)
- ✅ Quick evaluations (~3ms)

### phi3:mini (FALLBACK) - Use When:
- ✅ Rate limited (429 error)
- ✅ API unavailable
- ✅ Need local processing

### nomic-embed (LOCAL) - Use For:
- ✅ Crypt search (45ms)
- ✅ Ancestor matching
- ✅ Semantic similarity

## Genetic Evolution Budget

```
┌─────────────────────────────────────────────────────────────────────┐
│                   ONE EVOLUTION CYCLE                                │
│                                                                      │
│   [GLM-4.7-Flash] Classify task          ~3ms, FREE                 │
│   [nomic-embed] Search crypt             45ms, FREE                 │
│   [GLM-4.7-Flash] Generate mutations     ~3ms, FREE                 │
│                                                                      │
│   [GLM-5] Execute Alpha spawn            1 request                  │
│   [GLM-5] Execute Beta spawn             1 request                  │
│   [GLM-5] Execute Gamma spawn            1 request                  │
│                                                                      │
│   [GLM-4.7-Flash] Evaluate fitness       ~3ms, FREE                 │
│   [GLM-4.7-Flash] Extract patterns       ~3ms, FREE                 │
│                                                                      │
│   [nomic-embed] Entomb result            45ms, FREE                 │
│                                                                      │
│   TOTAL: 3 GLM-5 requests per generation                             │
│   MINI OPS: ~15ms total (instant!)                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Budget Math

```
GLM-5 Limit: 400 requests / 5 hours

Per Generation: 3 requests (Alpha + Beta + Gamma)
Max Generations: 400 / 3 = 133 generations per 5 hours

Mini operations: FREE and instant (~3ms each)
All classification/evaluation: FREE (GLM-4.7-Flash)

AVERAGE: 2 GLM-5 requests per task
MAX TASKS: 200 tasks per 5 hours
```

## Smart Routing

```python
def route_task(task: str) -> str:
    """
    Route based on complexity.
    Use GLM-4.7-Flash for routing (instant!).
    Save GLM-5 for execution.
    """
    
    # INSTANT: Classify with GLM-4.7-Flash
    classification = mini.classify(task)  # ~3ms, FREE
    
    if classification.complexity == "simple":
        # Mini can handle it directly - no GLM-5 needed
        return "mini"
    
    elif classification.complexity == "moderate":
        # 1-2 GLM-5 requests
        return "moderate"
    
    else:  # complex
        # Full genetic - 3 GLM-5 requests
        return "genetic"
```

## Rate Limit Handling

```python
class MiniMeeseeks:
    """
    GLM-4.7-Flash with rate limit fallback.
    """
    
    PRIMARY = "zai/glm-4.7-flash"  # ~3ms
    FALLBACK = "phi3:mini"         # 200-800ms
    
    def __init__(self):
        self.consecutive_429s = 0
    
    def execute(self, task: str) -> str:
        """Execute with automatic fallback."""
        
        # Try primary (GLM-4.7-Flash)
        try:
            result = self._call_api(self.PRIMARY, task)
            self.consecutive_429s = 0
            return result
            
        except RateLimitError:
            self.consecutive_429s += 1
            
            # Fallback to local
            return self._call_local(self.FALLBACK, task)
```

## Speed Comparison

| Model | Response | Cost | Use Case |
|-------|----------|------|----------|
| **GLM-4.7-Flash** | **~3ms** | FREE | Primary Mini ✅ |
| phi3:mini | 200-800ms | FREE | Rate limit fallback |
| GLM-5 | ~500ms | 1/400 | Complex tasks only |

**GLM-4.7-Flash is 166x faster than the 500ms target!**

## Workflow Summary

```
Task Arrives
     │
     ▼
┌─────────────────────┐
│  CLASSIFY           │ ← GLM-4.7-Flash (~3ms, FREE)
│  simple/complex     │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Simple    Complex
    │         │
    ▼         ▼
┌──────────┐ ┌─────────────────────────┐
│ GLM-4.7  │ │ GLM-4.7-Flash mutate    │ ← ~3ms, FREE
│ -Flash   │ │     ↓                   │
│ ~3ms     │ │ GLM-5 spawn ×3          │ ← 3 req
└────┬─────┘ │     ↓                   │
     │       │ GLM-4.7-Flash eval      │ ← ~3ms, FREE
     │       └──────────┬──────────────┘
     │                  │
     └────────┬─────────┘
              ▼
       ┌──────────────┐
       │ GLM-4.7-Flash│ ← ~3ms, FREE
       │ evaluate     │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │ nomic-embed  │ ← 45ms, FREE
       │ entomb       │
       └──────────────┘
```

## Rules

1. **GLM-5 for complex execution ONLY** - Never for routing/scoring
2. **GLM-4.7-Flash for everything else** - Classification, evaluation, patterns (~3ms!)
3. **phi3:mini for fallback** - When rate limited
4. **Max 2 concurrent Flash requests** - Avoid 429 errors
5. **Track GLM-5 budget** - Know how many requests remain

**Bottom line: GLM-4.7-Flash is instant and free. Use it for everything except complex execution.**
