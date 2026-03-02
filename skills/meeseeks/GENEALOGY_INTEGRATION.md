# Genealogy Integration Guide

## Where the Genealogy System Fits

The genealogy system integrates at **three key points** in the Meeseeks lifecycle:

### 1. BIRTH - When Spawning

**File:** `skills/meeseeks/spawn_meeseeks.py` or directly in your spawn code

```python
from genealogy import spawn_with_genealogy

# When spawning a new Meeseeks
spawn_info = spawn_with_genealogy(
    session_key=result["childSessionKey"],
    task="Fix the authentication bug",
    approach="systematic",
    traits=["+systematic", "+careful", "+debugging"],
    generation=0  # First generation
)

print(f"Spawned: {spawn_info['name']}")
print(f"Species: {spawn_info['species']} ({spawn_info['pokemon_type']})")
```

### 2. LIFE - Recording Fitness

**File:** `skills/meeseeks/auto_entomb.py` (in the auto_entomb function)

```python
from genealogy import MeeseeksGenealogy

genealogy = MeeseeksGenealogy()

# Record fitness when task completes
fitness = calculate_fitness(result)  # 0.0 to 1.0
genealogy.record_fitness(
    session_key=session_key,
    fitness=fitness,
    behavior={
        "speed": "fast",
        "approach": "pattern-matching",
        "tools_used": ["read", "exec"]
    }
)

# Check for legendary promotion
if fitness >= 0.85:
    legendary_species = SpeciesManager.promote_to_legendary(fitness)
    if legendary_species:
        print(f"🎉 Promoted to {legendary_species}!")
```

### 3. DEATH - Entombment with Genealogy

**File:** `skills/meeseeks/auto_entomb.py`

The entombment already happens, but now ancestors include genealogy data:

```python
# Ancestor file now includes:
- name: "Flash Meeseeks"
- species: "Swiftmoth"
- pokemon_type: "Flyer"
- generation: 2
- parent_id: "gen-1-approach-5"
- traits: ["+fast", "+efficient", "+agile"]
- fitness: 0.82
```

### 4. REBIRTH - Crossover for Next Generation

**File:** `skills/meeseeks/spawn_meeseeks.py` or evolution scripts

```python
from genealogy import crossover_parents, MeeseeksGenealogy

genealogy = MeeseeksGenealogy()

# Get top performers
top = genealogy.get_top_performers(limit=2)

# Crossover to create child
child = crossover_parents(
    parent_a_key=top[0]["session_key"],
    parent_b_key=top[1]["session_key"],
    child_session_key="new-spawn-session-key",
    generation=max(top[0]["generation"], top[1]["generation"]) + 1
)

# Spawn the child with inherited traits
spawn_info = spawn_with_genealogy(
    session_key=child["session_key"],
    task=task,
    approach=child["approach"],
    traits=child["traits"],
    generation=child["generation"],
    parent_id=top[0]["session_key"],
    second_parent_id=top[1]["session_key"]
)
```

## Integration Points

### Current Files to Update

1. **`spawn_meeseeks.py`**
   - Add genealogy registration on spawn
   - Use generated names in prompts
   - Pass species info to Meeseeks

2. **`auto_entomb.py`**
   - Record fitness before entombment
   - Check for legendary promotion
   - Include genealogy in ancestor files

3. **`cron_entomb.py`**
   - Already calls auto_entomb
   - Genealogy tracking happens automatically

4. **`templates/*.md`**
   - Add "Your name is {name}" to prompts
   - Add "Your species is {species}" for personality

### Example Template Update

```markdown
# Coder Meeseeks Template

You are **{name}**, a {species} Meeseeks.

Your type is {pokemon_type}. Your traits are: {traits}.

PURPOSE: {purpose}

...
```

## The Full Flow

```
1. USER REQUEST
   ↓
2. SPAWN WITH GENEALOGY
   - Generate name (e.g., "Flash Meeseeks")
   - Classify species (e.g., "Swiftmoth")
   - Register birth in genealogy.json
   ↓
3. MEESEEKS WORKS
   - Uses its traits/approach
   - Reports progress
   ↓
4. AUTO_ENTOMB ON COMPLETION
   - Calculate fitness (0.0-1.0)
   - Record fitness in genealogy
   - Check for legendary promotion
   - Entomb to Crypt with genealogy
   ↓
5. NEXT GENERATION
   - Query top performers
   - Crossover to create children
   - Children inherit traits
   - Repeat from step 2
```

## Storage Locations

```
the-crypt/
├── genealogy.json          # Birth/death/fitness records
├── ancestors/              # Entombed Meeseeks
│   └── ancestor-*.md       # Include genealogy data
├── meeseeks_runs.jsonl     # Run log
└── species/                # Species statistics
    ├── glimworm-stats.md
    ├── sparkmote-stats.md
    └── ...
```

## Quick Start

To use genealogy right now:

```python
from genealogy import spawn_with_genealogy

# Simple spawn
info = spawn_with_genealogy(
    session_key="my-test-123",
    task="Test task",
    approach="creative",
    traits=["+creative", "+fast"]
)

print(info)
# Output:
# {
#   'name': 'Spark Meeseeks',
#   'species': 'Sparkmote',
#   'pokemon_type': 'Elemental',
#   'generation': 0,
#   'traits': ['+creative', '+fast'],
#   ...
# }
```

---

*"I'm Mr. Meeseeks! Look at me! I have a name and species now!"* 🥒
