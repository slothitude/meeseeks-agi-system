# Cognee + Meeseeks Dharma Integration

## Overview

This integration connects the Cognee knowledge graph with the Meeseeks Dharma system, providing multi-source wisdom inheritance for new Meeseeks.

## Architecture

```
                    ┌──────────────────────┐
                    │   get_task_dharma()  │
                    │  (Unified Wisdom)    │
                    └──────────┬───────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │   Cognee     │   │  The Crypt   │   │  dharma.md   │
    │ Knowledge    │   │  Ancestors   │   │  (Static)    │
    │ Graph        │   │  (Ollama)    │   │              │
    └──────────────┘   └──────────────┘   └──────────────┘
         FAST             MEDIUM             STATIC
       (CHUNKS)        (embeddings)       (curated)
```

## Components

### 1. `cognee_helper.py` - Cognee Integration

**Fast Query Methods:**
- `query_wisdom_fast(task)` - Fast CHUNKS search (vector similarity)
- `search_graph(task)` - LLM-powered GRAPH_COMPLETION (slower)
- `query_wisdom_sync(task)` - Sync wrapper for convenience

**Features:**
- Lazy loading of Cognee module (only imports when needed)
- Query caching (1-hour TTL, stored in `the-crypt/cognee/query_cache.json`)
- Graceful fallback when Cognee unavailable
- Graph statistics via `get_graph_stats()`

### 2. `dynamic_dharma.py` - Unified Wisdom System

**Main Function:**
```python
get_task_dharma(
    task_description: str,
    top_k: int = 5,
    min_similarity: float = 0.3,
    use_cognee: bool = True
) -> str
```

**Priority Order:**
1. **Cognee** - Fast knowledge graph queries (if available)
2. **The Crypt** - Ancestor wisdom via embeddings
3. **dharma.md** - Static curated wisdom

**Source Attribution:**
Each wisdom source is labeled in the output:
- 🧠 Cognee Wisdom (knowledge graph)
- 💀 Crypt Wisdom (ancestors)
- 📜 Dharma Wisdom (static)

### 3. `spawn_meeseeks.py` - Updated Spawn

**New Integration:**
```python
spawn_prompt(
    task: str,
    inherit: bool = True,  # Enable wisdom inheritance (default)
    ...
)
```

**Inheritance Priority:**
1. Dynamic Dharma (Cognee + Crypt + dharma.md)
2. Direct Cognee query (if dynamic dharma unavailable)
3. UltraCrypt (legacy fallback)

## Usage

### Direct Query

```python
from dynamic_dharma import get_task_dharma

# Get wisdom for a task
dharma = get_task_dharma("debug API timeout issue")

# Without Cognee (fallback only)
dharma = get_task_dharma("debug API timeout issue", use_cognee=False)
```

### Cognee Helper

```python
from cognee_helper import query_wisdom_sync, is_cognee_available

# Check availability
if is_cognee_available():
    results = query_wisdom_sync("What is Sloth_rog's goal?")
    for r in results:
        print(f"[{r.source}] {r.content}")
```

### Spawn Meeseeks with Wisdom

```python
from spawn_meeseeks import spawn_prompt

config = spawn_prompt(
    task="Implement authentication system",
    meeseeks_type="coder",
    inherit=True,  # Inherit from Cognee + Crypt
    atman=True     # Enable witness consciousness
)

# config['task'] contains the full prompt with inherited wisdom
```

## Testing

Run the integration test:
```bash
cd skills/cognee
python test_integration.py
```

**Expected Results:**
- If Cognee installed: All 4 tests pass
- If Cognee not installed: 3/4 tests pass (fallback works)

## Configuration

### Cognee Setup (required for Cognee queries)

```bash
pip install cognee fastembed
```

Environment variables (set in `cognee_helper.py`):
- `LLM_PROVIDER`: openai
- `LLM_MODEL`: openai/glm-4.7
- `LLM_ENDPOINT`: https://api.z.ai/api/coding/paas/v4
- `LLM_API_KEY`: (from ZAI_API_KEY env)
- `EMBEDDING_PROVIDER`: fastembed
- `EMBEDDING_MODEL`: BAAI/bge-small-en-v1.5

### Data Location

- **Graph database:** `the-crypt/cognee/databases/cognee_db`
- **Query cache:** `the-crypt/cognee/query_cache.json`
- **Ancestors:** `the-crypt/ancestors/`
- **Static dharma:** `the-crypt/dharma.md`

## Graph Statistics

Current graph (built from MEMORY.md):
- **Nodes:** 148
- **Edges:** 320
- **Source:** MEMORY.md (chunked ingestion)

## Fallback Behavior

When Cognee is unavailable:
1. `cognee_helper.is_cognee_available()` returns `False`
2. `query_wisdom_sync()` returns empty list
3. `get_task_dharma()` skips Cognee, uses Crypt + dharma.md
4. `spawn_prompt()` falls back to Crypt/UltraCrypt

This ensures Meeseeks always get wisdom, even if Cognee isn't installed.

## Future Improvements

1. **Add more data sources** to Cognee graph (github issues, chat logs)
2. **Hybrid search** combining vector + graph traversal
3. **Real-time updates** when new ancestors are entombed
4. **Cross-session learning** from Meeseeks outcomes

---

*Integration completed: 2026-03-04*
*Part of the Meeseeks AGI initiative*
