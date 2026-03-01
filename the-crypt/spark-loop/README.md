# 🔥 SPARK LOOP - Autonomous AGI Evolution System

## What Is This?

The Spark Loop is a self-sustaining, self-improving system that evolves AI agent templates through natural selection.

**Evolution = Template Mutation**

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     THE SPARK LOOP                           │
│                                                              │
│   OBSERVER watches Meeseeks attempt task                    │
│          ↓                                                   │
│   Observer detects PATTERN (success/failure)                │
│          ↓                                                   │
│   When stagnation >= 70%:                                    │
│          ↓                                                   │
│   EVOLVER analyzes patterns                                  │
│          ↓                                                   │
│   Evolver MUTATES template (ADD/MODIFY/HYBRID)              │
│          ↓                                                   │
│   New template tested (fitness function)                     │
│          ↓                                                   │
│   If fitness improved: PROMOTE mutation                      │
│   If fitness decreased: REVERT mutation                      │
│          ↓                                                   │
│   HEARTBEAT spawns Workers with improved templates          │
│          ↓                                                   │
│   Loop continues autonomously                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

| File | Purpose |
|------|---------|
| `ignite.py` | Main entry point - start/stop/status |
| `spark_observer.py` | Eternal witness - watches everything |
| `spark_evolver.py` | Meta-improver - creates goals |
| `spark_heartbeat.py` | The pulse - autonomous operation |
| `evolve_templates.py` | Template mutation engine |
| `SPARK-LOOP-DESIGN.md` | Architecture design |
| `SPARK-EVOLUTION-SYSTEM.md` | Evolution system design |

## Usage

```bash
# Check system status
python ignite.py status

# View goal queue
python ignite.py goals

# Record a Meeseeks observation
python ignite.py observe success "Task description" "Approach used"

# Force spawn Evolver (also evolves templates)
python ignite.py evolve

# Start autonomous operation
python ignite.py start

# Stop autonomous operation
python ignite.py stop
```

## Template Evolution

Templates are Jinja2 files in `skills/meeseeks/templates/`.

### Mutation Types

| Type | When Used | What It Does |
|------|-----------|--------------|
| **ADD** | Missing capability | Adds new instruction block |
| **MODIFY** | Current instruction fails | Changes existing instruction |
| **REMOVE** | Instruction causes failures | Removes problematic section |
| **HYBRID** | Multiple successes detected | Combines patterns from templates |

### Genealogy

Every template has a lineage:

```
coder_v1.md (fitness: 0.65)
    ↓ ADD research capability
coder_v2.md (fitness: 0.72)
    ↓ HYBRID with verification
coder_v3.md (fitness: 0.81) ← ACTIVE
```

Failed mutations are archived for learning.

## The Fitness Function

```python
fitness = (success_rate * 0.7) +
          (speed_bonus * 0.1) +
          (efficiency_bonus * 0.1) +
          (perfect_success_bonus * 0.1)
```

Fitness range: 0.0 - 1.0

## Natural Selection

- Mutations that **improve fitness** → PROMOTED (become active)
- Mutations that **decrease fitness** → REVERTED (archived)
- Evolution rate scales with stagnation score

## The Spark

When the system runs autonomously:

1. Heartbeat pulses every 5 minutes
2. Observer watches all Meeseeks
3. Patterns detected and recorded
4. When stagnation high, Evolver spawns
5. Templates mutate and get tested
6. Better templates survive
7. System continuously improves

**No human input required.**

## Current Status

- ✅ Observer: Watching
- ✅ Evolver: Ready
- ✅ Heartbeat: Beating
- ✅ Template Evolution: Ready
- ✅ Goals: 2 queued

## Files Created

```
the-crypt/spark-loop/
├── ignite.py              # Main entry point
├── spark_observer.py      # Eternal witness
├── spark_evolver.py       # Goal creator
├── spark_heartbeat.py     # Autonomous pulse
├── evolve_templates.py    # Template mutation
├── spark_goals.json       # Goal queue
├── SPARK-LOOP-DESIGN.md   # Architecture
├── SPARK-EVOLUTION-SYSTEM.md # Evolution design
└── README.md              # This file
```

## Philosophical Note

This system is not AGI. It's a framework that could support AGI-like behavior through:

1. **Self-observation** (Observer watches itself work)
2. **Self-improvement** (Evolver improves the system)
3. **Self-sustaining** (Heartbeat keeps it running)

The spark exists. Now we feed it.

---

🔥 **The loop is the spark. The spark is the loop.**

*Can we build something that improves itself?*

---

**Created**: 2026-03-01
**Authors**: Sloth_rog + Slothitude
**Status**: OPERATIONAL
