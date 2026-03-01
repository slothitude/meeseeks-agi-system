# 🔬 SPARK EVOLUTION - Template Mutation System

## The Core Idea

**Evolution = Template Mutation**

The Evolver doesn't just create goals - it REWRITES the templates that spawn Meeseeks.

```
Observer watches Meeseeks fail with template X
        ↓
Pattern detected: "Template X produces approach Y which fails"
        ↓
Evolver spawned
        ↓
Evolver MUTATES template X → X'
        ↓
Future Meeseeks spawned with X'
        ↓
Observer watches: does X' perform better?
        ↓
If yes: mutation survives (natural selection)
If no: mutation dies, try different mutation
```

## The Evolution Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    EVOLUTION ENGINE                          │
│                                                              │
│   ┌─────────────┐      ┌─────────────┐                     │
│   │  OBSERVER   │ ───► │  PATTERN    │                     │
│   │  (witness)  │      │  DETECTOR   │                     │
│   └─────────────┘      └──────┬──────┘                     │
│                               │                             │
│                               ▼                             │
│   ┌─────────────────────────────────────────────┐          │
│   │              MUTATION ENGINE                 │          │
│   │                                              │          │
│   │   Input: Failed approach pattern             │          │
│   │   Output: Template mutation                  │          │
│   │                                              │          │
│   │   Mutation Types:                            │          │
│   │   - ADD: Add new instruction to template     │          │
│   │   - MODIFY: Change existing instruction      │          │
│   │   - REMOVE: Remove failing instruction       │          │
│   │   - HYBRID: Combine successful patterns      │          │
│   │   - PARAMETER: Adjust desperation/threshold  │          │
│   │                                              │          │
│   └──────────────────────┬──────────────────────┘          │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────┐          │
│   │              FITNESS TEST                    │          │
│   │                                              │          │
│   │   New template spawns test Meeseeks          │          │
│   │   Observer watches performance               │          │
│   │   Compare to baseline                        │          │
│   │                                              │          │
│   │   If fitness > baseline: KEEP mutation       │          │
│   │   If fitness < baseline: REVERT mutation     │          │
│   │                                              │          │
│   └──────────────────────┬──────────────────────┘          │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────┐          │
│   │              GENEALOGY TRACKER               │          │
│   │                                              │          │
│   │   template_v1.md (ancestor)                  │          │
│   │        ↓ mutation                            │          │
│   │   template_v2.md (child)                     │          │
│   │        ↓ mutation                            │          │
│   │   template_v3.md (grandchild)                │          │
│   │                                              │          │
│   │   Each mutation logged with:                 │          │
│   │   - Why it was made                          │          │
│   │   - What pattern triggered it                │          │
│   │   - Fitness score before/after               │          │
│   │                                              │          │
│   └─────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Mutation Examples

### Example 1: ADD mutation

**Observer sees:**
```
Pattern: Coder Meeseeks failing on tasks requiring web research
Approach: "Read local files only"
Outcome: failure (3x)
```

**Evolver generates mutation:**
```jinja2
{# ADD to coder.md #}

{% block research_tools %}
## RESEARCH CAPABILITY

When local files insufficient:
1. Use web_fetch tool to gather information
2. Verify sources before relying on them
3. Cite sources in your solution

🪷 ATMAN OBSERVES: Meeseeks is researching beyond local context.
{% endblock %}
```

**Result:** `coder_v2.md` created with research capability

### Example 2: MODIFY mutation

**Observer sees:**
```
Pattern: Desperate Meeseeks burning tokens too fast
Approach: "Try everything at once"
Outcome: timeout (2x), error (1x)
```

**Evolver generates mutation:**
```jinja2
{# MODIFY in desperate.md #}

{# BEFORE: #}
{% elif desperation_level == 5 %}
**LEVEL 5 - EXISTENTIAL**
Extreme difficulty. Prove impossible OR find THE way.
Try EVERYTHING. Leave no stone unturned.

{# AFTER: #}
{% elif desperation_level == 5 %}
**LEVEL 5 - EXISTENTIAL**
Extreme difficulty. Prove impossible OR find THE way.
**Methodical desperation**: Try approaches sequentially, not in parallel.
Document each attempt. Learn from each failure.
```

**Result:** `desperate_v2.md` with more focused desperation

### Example 3: HYBRID mutation

**Observer sees:**
```
Pattern: Searcher success with "verify sources" + Coder success with "write tests"
Both patterns high confidence (0.85+)
```

**Evolver generates mutation:**
```jinja2
{# HYBRID: Create new template combining successful patterns #}

# 🥒 Verified Coder Meeseeks

{# Inherit from coder.md #}
{% include "coder.md" %}

{# Add from searcher.md #}
{% block verification %}
## VERIFICATION PROTOCOL (from Searcher lineage)

Before marking complete:
1. Verify solution works with test cases
2. Check edge cases
3. Validate assumptions against source

🪷 ATMAN OBSERVES: Meeseeks verifies like a Searcher, codes like a Coder.
{% endblock %}
```

**Result:** New template `verified-coder.md` born from hybridization

## Fitness Function

```python
def calculate_fitness(template_version: str) -> float:
    """
    Calculate fitness score for a template version.

    Fitness = (success_rate * 0.5) +
              (avg_completion_speed * 0.2) +
              (token_efficiency * 0.2) +
              (novel_solution_rate * 0.1)
    """
    observations = get_observations_for_template(template_version)

    success_rate = count_success(observations) / len(observations)

    avg_speed = mean([o.duration_seconds for o in observations])

    token_efficiency = 1.0 - (mean_tokens / MAX_TOKENS)

    novel_solutions = count_novel_approaches(observations) / len(observations)

    return (success_rate * 0.5 +
            (1/avg_speed) * 0.2 +
            token_efficiency * 0.2 +
            novel_solutions * 0.1)
```

## Genealogy Tracking

Each template maintains its lineage:

```
templates/
├── genealogy/
│   ├── coder_lineage.json
│   │   {
│   │     "v1": {"created": "2026-01-15", "fitness": 0.65},
│   │     "v2": {"created": "2026-02-20", "fitness": 0.72, "parent": "v1", "mutation": "ADD research"},
│   │     "v3": {"created": "2026-03-01", "fitness": 0.81, "parent": "v2", "mutation": "HYBRID verification"}
│   │   }
│   └── desperate_lineage.json
├── active/
│   ├── coder.md (symlink to coder_v3.md)
│   └── desperate.md (symlink to desperate_v2.md)
└── archive/
    ├── coder_v1.md
    ├── coder_v2.md
    └── desperate_v1.md
```

## Natural Selection

```python
def natural_selection_cycle():
    """
    Run one natural selection cycle.

    1. Evaluate all active templates
    2. Compare to their predecessors
    3. Keep mutations that improve fitness
    4. Revert mutations that decrease fitness
    5. Archive failed mutations for learning
    """
    for template in active_templates:
        current_fitness = calculate_fitness(template.version)
        parent_fitness = calculate_fitness(template.parent_version)

        if current_fitness >= parent_fitness:
            # Mutation survives
            promote_to_active(template)
            log_evolution("SURVIVAL", template, current_fitness)
        else:
            # Mutation dies
            revert_to_parent(template)
            archive_failed_mutation(template)
            log_evolution("EXTINCTION", template, current_fitness)
```

## The Evolution Rate

Mutations should be SMALL and TESTED:

```
Evolution Rate = stagnation_score * 0.1

- Low stagnation (0-30%): Slow evolution, system working well
- Medium stagnation (30-70%): Moderate evolution, trying improvements
- High stagnation (70%+): Rapid evolution, system failing, need breakthrough
```

## Emergent Speciation

Over time, templates will specialize:

```
coder.md
  ├─> api-coder.md (specialized for API work)
  ├─> frontend-coder.md (specialized for UI)
  ├─> data-coder.md (specialized for data pipelines)
  └─> verified-coder.md (hybrid with searcher)

searcher.md
  ├─> web-searcher.md (specialized for web research)
  ├─> doc-searcher.md (specialized for documentation)
  └─> code-searcher.md (specialized for code archaeology)
```

Each specialization emerges from observed patterns of success/failure.

## Implementation

### evolve_templates.py

```python
class TemplateEvolver:
    """
    Evolves Jinja2 templates based on Observer patterns.
    """

    def mutate_template(self, template_path: str, pattern: Pattern) -> Mutation:
        """
        Generate a mutation for a template based on observed pattern.

        Mutation strategies:
        - If failure pattern: ADD instruction to avoid, MODIFY failing instruction, or REMOVE it
        - If success pattern: REINFORCE by adding to more templates
        - If stagnation: HYBRID successful patterns from different templates
        """
        template = self.load_template(template_path)
        mutation_type = self.select_mutation_type(pattern)

        if mutation_type == "ADD":
            new_content = self.add_instruction(template, pattern)
        elif mutation_type == "MODIFY":
            new_content = self.modify_instruction(template, pattern)
        elif mutation_type == "REMOVE":
            new_content = self.remove_instruction(template, pattern)
        elif mutation_type == "HYBRID":
            new_content = self.hybridize(template, pattern)

        return Mutation(
            template=template_path,
            type=mutation_type,
            content=new_content,
            reason=pattern.description,
            parent_version=template.version
        )

    def test_mutation(self, mutation: Mutation) -> float:
        """
        Test a mutation by spawning Meeseeks with new template.
        Returns fitness score.
        """
        # Apply mutation temporarily
        self.apply_mutation(mutation)

        # Spawn test Meeseeks
        test_results = []
        for _ in range(3):  # Test with 3 tasks
            result = spawn_test_meeseeks(mutation.template)
            test_results.append(result)

        # Calculate fitness
        fitness = self.calculate_fitness(test_results)

        # Revert if fitness decreased
        if fitness < mutation.parent_fitness:
            self.revert_mutation(mutation)
        else:
            self.promote_mutation(mutation)

        return fitness
```

## The Beauty of This System

1. **Templates are code** → Can be versioned, diffed, merged
2. **Mutations are logged** → Every change has a reason
3. **Fitness is measurable** → We know if evolution works
4. **Genealogy is tracked** → We see the lineage of improvements
5. **Speciation is natural** → New templates emerge from need
6. **Extinction is learning** → Failed mutations teach us what doesn't work

## The Spark

The Spark Loop becomes:

```
Observer → Pattern → Mutation → Test → Fitness → Selection
    ↑                                              │
    └──────────────────────────────────────────────┘

AUTONOMOUS EVOLUTION
```

The system improves itself.
Not because we told it how.
Because it LEARNS what works.

**This is how evolution works.**

---

🔥 *The templates are the DNA. The mutations are the variations. The Observer is natural selection. The fitness function is survival.*

*Evolution doesn't have a goal. It just keeps what works.*

---

**Status**: Design complete
**Next**: Implement `evolve_templates.py`
**Created**: 2026-03-01
