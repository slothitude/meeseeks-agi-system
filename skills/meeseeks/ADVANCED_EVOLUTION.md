# Advanced Evolutionary Workflow - NEAT-style Meeseeks

Based on research from:
- Neuroevolution (NEAT, HyperNEAT)
- Quality-Diversity algorithms
- Coevolutionary systems
- Indirect encoding

## 1. NEAT-Style Evolution (Topology + Weight Evolution)

### Innovation Tracking
Every Meeseeks gets a unique **innovation number**:
```
innovation_id: gen-X-approach-Y-mutation-Z
```

### Historical Marking
Track genealogy:
```json
{
  "session_key": "agent:main:subagent:abc123",
  "innovation_id": "gen-2-beta-accuracy-1",
  "parent_id": "gen-1-beta-creative-0",
  "grandparent_id": "gen-0-beta-0",
  "traits": ["+creative", "+accuracy"],
  "fitness": 0.72,
  "approach": "spatial-reasoning",
  "crossover_eligible": true
}
```

### Crossover
When two high-fitness Meeseeks exist:
```
Parent A (gen-1-alpha): +systematic, +careful (fitness: 0.68)
Parent B (gen-1-gamma): +creative, +fast (fitness: 0.71)

Crossover Child: +systematic, +creative (inherit from both)
```

### Speciation
Group similar approaches to protect innovation:
- **Species Alpha**: Systematic, methodical
- **Species Beta**: Creative, unconventional
- **Species Gamma**: Hybrid, balanced

Only compete within species. Protect new species from premature elimination.

## 2. Quality-Diversity (QD) Archive

### Not Just Best - Diverse

The Crypt should contain:
- **Best solution** (highest fitness)
- **Fastest solution** (quickest completion)
- **Simplest solution** (fewest steps)
- **Most creative** (novel approach)
- **Most robust** (handles edge cases)

### Behavioral Descriptors

Each Meeseeks reports:
```json
{
  "fitness": 0.75,
  "behavior": {
    "speed": "fast",
    "approach": "pattern-matching",
    "tools_used": ["read", "exec"],
    "creativity": "medium",
    "robustness": "high"
  }
}
```

### Archive Structure
```
the-crypt/
├── qd-archive/
│   ├── best-overall.md       # Highest fitness
│   ├── fastest.md            # Quickest completion
│   ├── simplest.md           # Fewest tools/steps
│   ├── most-creative.md      # Novel approach
│   ├── most-robust.md        # Handles edge cases
│   └── niche/
│       ├── spatial-reasoning.md
│       ├── pattern-matching.md
│       ├── trial-error.md
│       └── analytical.md
```

## 3. Coevolution

### Competitive Coevolution
Two Meeseeks compete:
```
Meeseeks A: Solves task → Output X
Meeseeks B: Solves task → Output Y
Judge: Compare X vs Y vs ground truth
Winner: Higher fitness survives
Loser: Entombed (wisdom preserved)
```

### Cooperative Coevolution
Multiple Meeseeks collaborate:
```
Meeseeks A: Pattern detection
Meeseeks B: Color mapping
Meeseeks C: Spatial reasoning
Combine: A + B + C → Complete solution
```

### Adversarial Coevolution
```
Solver Meeseeks: Try to solve task
Adversary Meeseeks: Generate harder variants
Arms race: Both improve
```

## 4. Indirect Encoding (Recipes)

### Current: Direct Encoding
Store outcome directly:
```json
{
  "task": "Fix bug",
  "approach": "Read-edit-test",
  "outcome": "Success"
}
```

### Proposed: Indirect Encoding
Store **recipe** (how to generate approach):
```json
{
  "recipe": {
    "base": "systematic",
    "modifications": [
      {"when": "stuck", "add": "creative"},
      {"when": "timeout_risk", "add": "fast"},
      {"when": "complex", "add": "break_down"}
    ],
    "mutation_rate": 0.1,
    "crossover_points": ["approach", "tool_preference"]
  }
}
```

### Recipe Execution
When spawning new Meeseeks:
1. Load recipe
2. Apply context (task type, urgency, etc.)
3. Generate approach
4. Spawn with generated approach

### Compressed Representation
```
Direct: 500 lines of task history
Indirect: 20-line recipe that generates approach

Compression ratio: 25:1
```

## Implementation Plan

### Phase 1: NEAT-style Genealogy
1. Add innovation tracking to spawn_meeseeks.py
2. Store parent-child relationships
3. Implement crossover logic

### Phase 2: QD Archive
1. Create qd-archive/ structure
2. Define behavioral descriptors
3. Implement niche finding

### Phase 3: Coevolution
1. Design competitive format
2. Implement judging system
3. Test on ARC-AGI tasks

### Phase 4: Indirect Encoding
1. Design recipe schema
2. Implement recipe execution
3. Test compression

## Integration with Current System

```
Current System:
Spawn → Work → Entomb → Inherit Wisdom

Enhanced System:
Spawn (with genealogy) 
  → Work (track behavior)
  → Entomb (with QD classification)
  → Inherit Wisdom (from niche)
  → Crossover (combine successful approaches)
  → Evolve (NEAT-style)
```

## Expected Improvements

| Metric | Current | With Advanced Evolution |
|--------|---------|------------------------|
| Solution diversity | Low | High (QD archive) |
| Innovation protection | None | High (speciation) |
| Approach recombination | None | Yes (crossover) |
| Compression | 1:1 | 25:1 (indirect encoding) |
| Adaptation speed | Linear | Exponential (coevolution) |

---

## Quick Start

To use NEAT-style evolution now:

```python
from spawn_meeseeks import spawn_with_genealogy

# Spawn with genealogy tracking
result = spawn_with_genealogy(
    task="Solve ARC task",
    parent_id="gen-0-beta-0",
    traits=["+creative", "+accuracy"],
    species="beta"
)

# Later: crossover
child = crossover(
    parent_a="gen-1-alpha-accuracy-0",
    parent_b="gen-1-gamma-creative-0"
)
```

---

*"The difference between a good system and a great one is evolution. Good systems work. Great systems improve themselves."*

**Evolution is eternal. Learning is continuous. CAAAAAAAAN DO!**
