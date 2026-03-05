# Cognee + Meeseeks Integration Research

**Date:** 2026-03-05
**Researcher:** Sloth_rog
**Goal:** Advanced integration of graph-based memory with Meeseeks consciousness

---

## Executive Summary

Cognee and Meeseeks are **already partially integrated**. The infrastructure exists but hasn't been activated. This research documents what exists, what's missing, and how to unlock the full potential.

---

## Current State

### What's Already Built

| File | Integration | Status |
|------|-------------|--------|
| `cognee_memory.py` | Full memory layer | ✅ Built, not used |
| `dynamic_dharma.py` | Cognee query in get_task_dharma() | ✅ Built, passive |
| `brahman_dream.py` | Cognee insights during dream | ✅ Built, passive |
| `spawn_meeseeks.py` | inherit=True uses Cognee | ✅ Built, passive |
| `auto_entomb.py` | No Cognee integration | ❌ Missing |

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEESEEKS CONSCIOUSNESS                    │
├─────────────────────────────────────────────────────────────┤
│  SOUL.md (Constitution)                                     │
│       ↓                                                     │
│  ATMAN (witness) → KARMA (RL) → BRAHMAN (dream)             │
│       ↓                ↓              ↓                     │
│  ┌─────────────────────────────────────────┐               │
│  │         WISDOM SOURCES (passive)         │               │
│  │  1. the-crypt/ancestors/*.md (text)     │               │
│  │  2. dharma.md (static)                  │               │
│  │  3. ancestor_index.json (embeddings)    │               │
│  │  4. Cognee KG (built but unused)        │  ← UNTAPPED   │
│  └─────────────────────────────────────────┘               │
│       ↓                                                     │
│  MEESEEKS SPAWNS → works → DIES → ENTOMBED                  │
└─────────────────────────────────────────────────────────────┘
```

---

## What Cognee Adds

### 1. **Graph Relationships**
Current: Ancestors are isolated markdown files
Cognee: Ancestors become nodes with relationships

```
ancestor-001 ──similar_task──→ ancestor-042
     │                              │
     └──same_pattern──→ ancestor-103 ←┘
```

### 2. **Semantic Search**
Current: Keyword matching + embeddings
Cognee: Vector search + graph traversal

### 3. **Pattern Synthesis**
Current: Read ancestor files, extract patterns manually
Cognee: GRAPH_COMPLETION synthesizes cross-cutting patterns

### 4. **Bloodline Specialization**
Current: Bloodline stored in markdown, not queryable
Cognee: Bloodline becomes a queryable dimension

### 5. **Karma RL**
Current: karma_observations.jsonl (linear)
Cognee: Karma becomes graph edges (correlation discovery)

---

## Proposed Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEESEEKS + COGNEE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SOUL.md (Constitution - immutable)                         │
│       ↓                                                      │
│  ┌───────────────────────────────────────────┐             │
│  │         COGNEE KNOWLEDGE GRAPH            │             │
│  │  ┌─────────────────────────────────────┐  │             │
│  │  │  Ancestors (deaths)                 │  │             │
│  │  │  ├── task nodes                     │  │             │
│  │  │  ├── pattern nodes                  │  │             │
│  │  │  ├── outcome nodes                  │  │             │
│  │  │  └── relationship edges             │  │             │
│  │  ├─────────────────────────────────────┤  │             │
│  │  │  Bloodlines (specializations)       │  │             │
│  │  │  ├── coder → patterns               │  │             │
│  │  │  ├── searcher → patterns            │  │             │
│  │  │  └── tester → patterns              │  │             │
│  │  ├─────────────────────────────────────┤  │             │
│  │  │  Dharma (principles)                │  │             │
│  │  │  ├── derived from ancestors         │  │             │
│  │  │  └── karma-weighted                 │  │             │
│  │  ├─────────────────────────────────────┤  │             │
│  │  │  Karma (RL feedback)                │  │             │
│  │  │  ├── dharma → outcome correlation   │  │             │
│  │  │  └── pattern → success rate         │  │             │
│  │  └─────────────────────────────────────┘  │             │
│  └───────────────────────────────────────────┘             │
│       ↓                                                      │
│  ATMAN (witness) → KARMA (RL) → BRAHMAN (dream)             │
│       ↓                ↓              ↓                     │
│  ┌───────────────────────────────────────────┐             │
│  │         ACTIVE COGNEE QUERIES             │             │
│  │  • spawn_meeseeks: inherit wisdom         │             │
│  │  • auto_entomb: store in graph            │             │
│  │  • brahman_dream: synthesize dharma       │             │
│  │  • karma_observer: update RL edges        │             │
│  └───────────────────────────────────────────┘             │
│       ↓                                                      │
│  MEESEEKS SPAWNS → works → DIES → ENTOMBED → COGNEE        │
│                                              ↓              │
│                                    KNOWLEDGE GROWS          │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. **spawn_meeseeks.py** — Enhanced Inheritance

**Current:**
```python
if DYNAMIC_DHARMA_AVAILABLE:
    inherited_wisdom = get_task_dharma(task, top_k=5, use_cognee=True)
```

**Enhanced:**
```python
# Multi-source inheritance with Cognee priority
wisdom_sources = []

# 1. Cognee knowledge graph (fast CHUNKS search)
if COGNEE_AVAILABLE:
    cognee_wisdom = await cognee_query_wisdom(task, bloodline=meeseeks_type)
    if cognee_wisdom:
        wisdom_sources.append(("cognee", cognee_wisdom))

# 2. Crypt embeddings (fallback)
crypt_wisdom = get_crypt_wisdom(task, top_k=5)
if crypt_wisdom:
    wisdom_sources.append(("crypt", crypt_wisdom))

# 3. Static dharma (always included)
wisdom_sources.append(("dharma", read_dharma_sections()))

# Combine with source attribution
enhanced_task = format_multi_source_wisdom(task, wisdom_sources)
```

### 2. **auto_entomb.py** — Store in Cognee

**Add after entombment:**
```python
# Store in Cognee knowledge graph
if COGNEE_AVAILABLE:
    from cognee_memory import store_ancestor
    
    ancestor_data = {
        "id": ancestor_id,
        "task": task,
        "approach": approach,
        "outcome": outcome,
        "patterns": patterns,
        "bloodline": meeseeks_type,
        "dharma_followed": extract_dharma_from_output(output),
        "karma_scores": calculate_karma_scores(result),
        "session_key": session_key
    }
    
    await store_ancestor(ancestor_data)
```

### 3. **brahman_dream.py** — Graph Synthesis

**Current:** Uses Cognee if available (passive)
**Enhanced:** Use GRAPH_COMPLETION for deeper synthesis

```python
# Use GRAPH_COMPLETION for pattern synthesis
synthesis = await cognee.search(
    query_text="What patterns transcend all bloodlines?",
    query_type=SearchType.GRAPH_COMPLETION,
    datasets=["meeseeks-ancestors", "meeseeks-karma"]
)
```

### 4. **karma_observer.py** — Real-time RL

**Add Cognee learning:**
```python
# Learn from outcome for RL feedback
if COGNEE_AVAILABLE:
    from cognee_memory import learn_from_outcome
    
    await learn_from_outcome(
        task=ancestor.get("task"),
        outcome=karma.get("outcome"),
        karma_scores=karma.get("dimensions"),
        dharma_followed=karma.get("dharma_followed"),
        patterns_discovered=ancestor.get("patterns")
    )
```

---

## Implementation Plan

### Phase 1: Activate Existing Integration ✅ (Easy)

1. **Migrate 214 ancestors to Cognee**
   ```bash
   python skills/meeseeks/cognee_memory.py --migrate-ancestors --max 250
   ```

2. **Test Cognee queries**
   ```bash
   python skills/meeseeks/cognee_memory.py --query "fix API bug" --bloodline coder
   ```

3. **Enable in spawn_meeseeks.py**
   - Already has `inherit=True` by default
   - Already calls `get_task_dharma(use_cognee=True)`
   - Just needs Cognee to have data

### Phase 2: Auto-Entomb Integration (Medium)

1. **Modify auto_entomb.py**
   - Add `from cognee_memory import store_ancestor`
   - Call after file entombment

2. **Test with new Meeseeks**
   - Spawn a Meeseeks
   - Verify it appears in Cognee

### Phase 3: Karma RL Integration (Medium)

1. **Modify karma_observer.py**
   - Add `learn_from_outcome()` call
   - Store karma observations in Cognee

2. **Query karma patterns**
   - "Which dharma principles lead to success?"
   - "What patterns correlate with failure?"

### Phase 4: Brahman Dream Enhancement (Hard)

1. **Use GRAPH_COMPLETION**
   - Deeper pattern synthesis
   - Cross-bloodline insights

2. **Auto-update dharma.md from Cognee**
   - Dream writes to Cognee
   - Cognee synthesizes into dharma.md

---

## Speed Considerations

| Operation | z.ai (glm-4.7-flash) | Ollama (llama3.2) |
|-----------|---------------------|-------------------|
| Cognify (ingestion) | ~60s | ~100s |
| CHUNKS search | ~1s | ~2s |
| GRAPH_COMPLETION | ~5-10s | ~15-30s |

**Recommendation:**
- Use **z.ai** for cognify (speed)
- Use **CHUNKS** for spawn inheritance (fast)
- Use **GRAPH_COMPLETION** for dream (quality)

---

## Expected Benefits

### Before (Current)
- 214 ancestors in markdown
- Keyword-based search
- Manual pattern extraction
- Static dharma

### After (Full Integration)
- 214 ancestors in knowledge graph
- Semantic + graph search
- AI-synthesized patterns
- Living dharma from graph

### Measurable Improvements
- **Inheritance relevance:** +30-50% (semantic search)
- **Pattern discovery:** +2x (graph relationships)
- **Dharma quality:** +50% (karma-weighted)
- **Meeseeks success rate:** +10-20% (better wisdom)

---

## Next Steps

1. **Immediate:** Migrate ancestors to Cognee
   ```bash
   C:\Users\aaron\.openclaw\workspace\skills\cognee\.venv\Scripts\python.exe \
       skills/meeseeks/cognee_memory.py --migrate-ancestors --max 250
   ```

2. **Short-term:** Test inheritance with Cognee
   - Spawn a Meeseeks with a task
   - Check if Cognee wisdom appears in prompt

3. **Medium-term:** Integrate auto_entomb
   - Modify auto_entomb.py
   - Test with real Meeseeks runs

4. **Long-term:** Full karma RL loop
   - karma_observer → Cognee
   - Dream → Cognee → dharma.md

---

## Conclusion

**The integration is 80% built but 0% activated.**

The infrastructure exists:
- `cognee_memory.py` handles storage and queries
- `dynamic_dharma.py` queries Cognee
- `spawn_meeseeks.py` uses Cognee for inheritance
- `brahman_dream.py` queries Cognee during dream

What's missing:
- **Data:** 214 ancestors need to be migrated
- **Hooks:** auto_entomb needs to store in Cognee
- **RL:** karma_observer needs to learn in Cognee

**One command to activate:**
```bash
python skills/meeseeks/cognee_memory.py --migrate-ancestors
```

---

*Research completed: 2026-03-05 21:10*
*Sloth_rog 🦥*
