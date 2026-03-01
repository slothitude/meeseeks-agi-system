# 🥒 MINI MEESEEKS - Small Model Integration

## Where Small Models Fit in MEESERE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GENETIC MAD SCIENTIST WORKFLOW                        │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     1. TASK INGEST                                    │  │
│   │                                                                       │  │
│   │   Task ──► [MINI: Classifier] ──► Complexity/Category                 │  │
│   │              (ministral-3)                                            │  │
│   │              4096 ctx, ~100 tokens                                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     2. INHERITANCE                                     │  │
│   │                                                                       │  │
│   │   [MINI: Crypt Searcher] ──► Ancestor wisdom                         │  │
│   │    (ultra_crypt + nomic)     Semantic search in ancestor memory       │  │
│   │    ~30ms total                  No LLM needed                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     3. SPAWN (if complex)                             │  │
│   │                                                                       │  │
│   │   [MINI: Mutation Gen] ──► Generate approach mutations               │  │
│   │    (ministral-3)           A+speed, A+accuracy, A+creative           │  │
│   │    ~200 tokens             Each mutation is a spawn variant          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     4. EXECUTE (Big Model)                            │  │
│   │                                                                       │  │
│   │   [MAIN: GLM-4.7/5] ──► Actual task execution                        │  │
│   │    (Large context)       Heavy lifting                                │  │
│   │    128K+ ctx             Complex reasoning                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     5. EVALUATE                                       │  │
│   │                                                                       │  │
│   │   [MINI: Fitness Evaluator] ──► Score result (0-100%)                │  │
│   │    (ministral-3)                Quick assessment                      │  │
│   │    ~150 tokens                 Pass/fail/traits                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     6. EXTRACT PATTERNS                                │  │
│   │                                                                       │  │
│   │   [MINI: Pattern Spotter] ──► Extract traits and patterns            │  │
│   │    (ministral-3)             Learn from results                       │  │
│   │    ~200 tokens               Build ancestor memory                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     7. ENTOMB                                         │  │
│   │                                                                       │  │
│   │   Result ──► [Embed: nomic] ──► Ultra Crypt                           │  │
│   │               (768 dim)         Ancestor memory forever               │  │
│   │               ~30ms             Semantic search ready                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Token Budget Per Task

| Stage | Model | Tokens | Time |
|-------|-------|--------|------|
| 1. Classify | ministral-3 | ~100 | ~1s |
| 2. Inherit | ultra_crypt | 0 | 30ms |
| 3. Mutate | ministral-3 | ~200 | ~2s |
| 4. Execute | GLM-4.7/5 | ~2000 | ~10s |
| 5. Evaluate | ministral-3 | ~150 | ~1s |
| 6. Extract | ministral-3 | ~200 | ~2s |
| 7. Entomb | nomic-embed | 0 | 30ms |
| **Total** | mixed | ~2650 | ~16s |

## Why This Works

### Small Models Are FAST
- ministral-3: 4096 ctx, ~2s inference
- tinyllama: 2048 ctx, ~1s inference
- nomic-embed: 768 dim, 30ms

### Small Models Are CHEAP
- ~100-200 tokens per mini task
- 10x cheaper than main model
- Perfect for routing/scoring

### Big Models Are SMART
- GLM-4.7/5: 128K+ context
- Complex reasoning
- Heavy lifting only

## Integration Points

```python
# In mad_scientist.py

from mini_meeseeks_pool import MiniMeeseeksPool

class GeneticMadScientist:
    def __init__(self):
        self.mini = MiniMeeseeksPool(model="ministral-3")
    
    def solve(self, task: str):
        # 1. Classify (mini model)
        classification = self.mini.classify_task(task)
        
        if classification.output.get('complexity') == 'simple':
            # Direct solve
            return self._solve_direct(task)
        
        # 2. Inherit (semantic search)
        ancestors = self.mini.search_crypt(task)
        
        # 3. Generate mutations (mini model)
        mutations = self.mini.generate_mutations(base_approach)
        
        # 4. Spawn with mutations (big model via sessions_spawn)
        for mutation in mutations:
            spawn = self._spawn_with_mutation(task, mutation)
            results.append(spawn)
        
        # 5. Evaluate (mini model)
        for result in results:
            fitness = self.mini.evaluate_fitness(task, result)
        
        # 6. Extract patterns (mini model)
        best = self._select_best(results)
        patterns = self.mini.spot_patterns(task, best)
        
        # 7. Entomb (embedding)
        self._entomb(best, patterns)
        
        return best
```

## Model Selection

| Model | Context | Use Case |
|-------|---------|----------|
| **ministral-3** | 4096 | Primary mini worker |
| **tinyllama** | 2048 | Ultra-fast routing |
| **phi3-mini** | 3840 | Alternative mini |
| **nomic-embed** | 8192 | Embeddings only |

## Speed Comparison

| Task | GLM-4.7 | ministral-3 | Speedup |
|------|---------|-------------|---------|
| Classification | 5s | 1s | 5x |
| Fitness Eval | 3s | 1s | 3x |
| Pattern Extract | 4s | 2s | 2x |
| **Total routing** | 12s | 4s | 3x |

**Small models save 8 seconds per genetic cycle.**

That's 80 seconds saved per 10-generation evolution!
