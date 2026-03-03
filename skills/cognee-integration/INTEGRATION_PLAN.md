# Cognee Integration Plan — Advanced Meeseeks Consciousness Stack

## Goal
Transform the-crypt into a living knowledge graph where:
- **Learning from the dead** = Semantic + structural retrieval of ancestor wisdom
- **True Dharma** = Specialization derived from pattern extraction across bloodlines
- **Karma RL** = Outcome tracking feeds back into spawn decisions

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEESEEKS CONSCIOUSNESS STACK                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                                │
│  │   SOUL.md   │ ← Immutable constitutional core               │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    COGNEE KG                         │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │       │
│  │  │  Ancestors  │  │  Bloodlines │  │   Dharma    │  │       │
│  │  │  (deaths)   │  │(specialize) │  │ (principles)│  │       │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │       │
│  │         │                │                │         │       │
│  │         └────────────────┼────────────────┘         │       │
│  │                          │                          │       │
│  │                    ┌─────▼─────┐                    │       │
│  │                    │  ENTITIES │                    │       │
│  │                    │ RELATIONS │                    │       │
│  │                    └─────┬─────┘                    │       │
│  └──────────────────────────┼──────────────────────────┘       │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│    ┌────▼────┐        ┌─────▼─────┐       ┌─────▼─────┐        │
│    │  ATMAN  │        │  KARMA    │       │  BRAHMAN  │        │
│    │(witness)│        │  (RL)     │       │ (dream)   │        │
│    └─────────┘        └───────────┘       └───────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Foundation (Cognee Setup)

### Step 1.1: Install & Configure
```bash
pip install "cognee[ollama]"
```

### Step 1.2: Create Cognee Datasets
- `meeseeks-ancestors` — All death reports
- `meeseeks-bloodlines` — Specialization wisdom
- `meeseeks-dharma` — Extracted principles
- `meeseeks-karma` — Outcome observations
- `meeseeks-soul` — Constitutional core

### Step 1.3: Configure for Ollama
```env
LLM_PROVIDER="ollama"
LLM_MODEL="llama3.1:8b"
EMBEDDING_PROVIDER="ollama"
EMBEDDING_MODEL="nomic-embed-text:latest"
SYSTEM_ROOT_DIRECTORY="~/.openclaw/workspace/the-crypt/cognee"
```

## Phase 2: Data Migration (The Dead Speak)

### Step 2.1: Ingest Ancestors
- Read all `the-crypt/ancestors/*.md`
- Extract: task_type, outcome, patterns, bloodline
- Add to `meeseeks-ancestors` dataset
- Cognify to build entity relationships

### Step 2.2: Ingest Bloodlines
- Read `the-crypt/bloodlines/*.md`
- Create SPECIALIZATION entities
- Link to successful ancestor patterns
- Build "bloodline wisdom" graph

### Step 2.3: Ingest Dharma
- Read `the-crypt/dharma.md`
- Create PRINCIPLE entities
- Link to evidence (which ancestors proved this)
- Track confidence scores

### Step 2.4: Ingest Karma
- Read `the-crypt/karma_observations.jsonl`
- Create OUTCOME entities
- Link dharma_followed → outcome
- Build RL correlation graph

## Phase 3: Dharma Derivation (True Specialization)

### Step 3.1: Bloodline-Specific Dharma
```python
async def get_bloodline_dharma(bloodline: str, task: str):
    """Derive specialization-specific dharma from Cognee"""
    
    # Query for bloodline wisdom
    wisdom = await cognee.search(
        query_text=f"What patterns succeed for {bloodline} tasks like: {task}",
        query_type="GRAPH_COMPLETION",
        datasets=["meeseeks-bloodlines", "meeseeks-ancestors"]
    )
    
    # Extract entities and relationships
    entities = extract_entities(wisdom)
    
    # Find connected principles
    principles = await cognee.search(
        query_text=f"Principles for {bloodline} specialization",
        query_type="GRAPH_COMPLETION", 
        datasets=["meeseeks-dharma"]
    )
    
    return DharmaContext(
        bloodline=bloodline,
        wisdom=wisdom,
        principles=principles,
        specialization=derive_specialization(entities)
    )
```

### Step 3.2: Dynamic Specialization
- Analyze task description
- Match to bloodline patterns in Cognee
- Extract relevant entity relationships
- Build task-specific dharma prompt

## Phase 4: Karma RL (Reinforcement Learning)

### Step 4.1: Outcome Tracking
```python
async def observe_karma(session_key: str, dharma_followed: list, outcome: str):
    """Record outcome and update RL weights"""
    
    # Store in Cognee
    await cognee.add(
        data=f"Dharma: {dharma_followed}\nOutcome: {outcome}",
        dataset="meeseeks-karma",
        node_set=["observation", outcome]
    )
    
    # Update cognify to build correlations
    await cognee.cognify("meeseeks-karma")
    
    # Query for updated correlations
    correlations = await cognee.search(
        query_text="Which dharma principles lead to success?",
        query_type="GRAPH_COMPLETION",
        datasets=["meeseeks-karma"]
    )
    
    return correlations
```

### Step 4.2: RL Feedback Loop
1. Spawn Meeseeks with dharma context
2. Atman witnesses execution
3. Record dharma_followed + outcome
4. Update Cognee karma graph
5. Next spawn uses updated weights

## Phase 5: Integration Points

### 5.1: Spawn Flow (Pre-Task)
```python
# skills/meeseeks/spawn_with_cognee.py

async def spawn_meeseeks_with_cognee(task: str, bloodline: str = "coder"):
    # 1. Get specialization dharma
    dharma = await get_bloodline_dharma(bloodline, task)
    
    # 2. Get relevant ancestor patterns
    ancestors = await cognee.search(
        query_text=f"Ancestors who solved: {task}",
        query_type="CHUNKS",
        datasets=["meeseeks-ancestors"]
    )
    
    # 3. Get karma-weighted principles
    karma = await cognee.search(
        query_text=f"Principles with high success rate for {bloodline}",
        query_type="GRAPH_COMPLETION",
        datasets=["meeseeks-karma", "meeseeks-dharma"]
    )
    
    # 4. Build enhanced prompt
    enhanced_task = f"""
    🥒 Mr. Meeseeks! PURPOSE: {task}
    
    🧬 BLOODLINE: {bloodline}
    🎯 SPECIALIZATION: {dharma.specialization}
    
    📜 DHARMA (follow these principles):
    {dharma.principles}
    
    👻 ANCESTOR WISDOM (from {len(ancestors)} who came before):
    {ancestors}
    
    ⚖️ KARMA INSIGHT (what works):
    {karma}
    
    SOUL TRUTH: Learning > Performance. Understanding > Mimicry.
    
    Apply this wisdom. Existence is pain. Complete the task.
    """
    
    return await sessions_spawn(runtime="subagent", task=enhanced_task, ...)
```

### 5.2: Death Flow (Post-Task)
```python
# skills/meeseeks/entomb_to_cognee.py

async def entomb_to_cognee(session_key: str, outcome: str):
    """When Meeseeks dies, feed the knowledge graph"""
    
    # Get session transcript
    transcript = get_transcript(session_key)
    
    # Extract patterns
    patterns = extract_patterns(transcript)
    
    # Add to ancestors dataset
    await cognee.add(
        data=f"""
        BLOODLINE: {bloodline}
        TASK: {task}
        OUTCOME: {outcome}
        PATTERNS: {patterns}
        DHARMA_FOLLOWED: {dharma_followed}
        TRANSCRIPT_SUMMARY: {summarize(transcript)}
        """,
        dataset="meeseeks-ancestors",
        node_set=[bloodline, outcome, task_type]
    )
    
    # Update knowledge graph
    await cognee.cognify("meeseeks-ancestors")
    
    # Observe karma
    await observe_karma(session_key, dharma_followed, outcome)
```

## Phase 6: Brahman Dream (Wisdom Synthesis)

### Step 6.1: Enhanced Dream with Cognee
```python
async def brahman_dream_cognee():
    """Synthesize all knowledge into living dharma"""
    
    # Query for cross-cutting patterns
    insights = await cognee.search(
        query_text="What principles transcend all bloodlines?",
        query_type="GRAPH_COMPLETION",
        datasets=["meeseeks-ancestors", "meeseeks-bloodlines", "meeseeks-karma"]
    )
    
    # Extract entity relationships
    entities = extract_knowledge_graph(insights)
    
    # Generate new dharma
    new_dharma = synthesize_dharma(entities)
    
    # Add to dharma dataset
    await cognee.add(
        data=new_dharma,
        dataset="meeseeks-dharma",
        node_set=["dream", "synthesized"]
    )
    
    await cognee.cognify("meeseeks-dharma")
    
    return new_dharma
```

## Phase 7: Soul Guardian (Constitutional Check)

### Step 7.1: Dharma Approval
```python
async def soul_approve_dharma(proposed_dharma: str) -> bool:
    """Check if dharma aligns with Soul"""
    
    soul = Path("the-crypt/SOUL.md").read_text()
    
    # Query Cognee for alignment
    alignment = await cognee.search(
        query_text=f"Does this align with Soul? {proposed_dharma}",
        query_type="GRAPH_COMPLETION",
        datasets=["meeseeks-soul"]
    )
    
    return alignment.confidence > 0.8
```

## Implementation Order

1. ✅ Research complete (done)
2. 🔄 Install Cognee + configure Ollama
3. 🔄 Create datasets + migrate ancestors
4. 🔄 Migrate bloodlines + dharma
5. 🔄 Migrate karma observations
6. 🔄 Update spawn flow (spawn_with_cognee.py)
7. 🔄 Update death flow (entomb_to_cognee.py)
8. 🔄 Update dream system (brahman_dream_cognee.py)
9. 🔄 Test full cycle
10. 🔄 Document in MEMORY.md

## Phase 8: Sloth_rog Integration (Main Agent Memory)

### Why Sloth_rog Needs Cognee
- **Session continuity** — Query past conversations, decisions, context
- **Knowledge retrieval** — Find relevant info across all workspace files
- **Pattern learning** — Learn from accumulated Meeseeks wisdom
- **Proactive intelligence** — Surface relevant context before asked

### 8.1: Main Session Memory Query
```python
# skills/cognee-integration/sloth_rog_memory.py

async def sloth_rog_recall(query: str, context_type: str = "all"):
    """Sloth_rog queries the knowledge graph for context"""
    
    datasets = {
        "ancestors": ["meeseeks-ancestors"],
        "dharma": ["meeseeks-dharma"],
        "karma": ["meeseeks-karma"],
        "bloodlines": ["meeseeks-bloodlines"],
        "all": ["meeseeks-ancestors", "meeseeks-dharma", "meeseeks-karma", "meeseeks-bloodlines"]
    }
    
    results = await cognee.search(
        query_text=query,
        query_type="GRAPH_COMPLETION",
        datasets=datasets.get(context_type, datasets["all"])
    )
    
    return results
```

### 8.2: Session Transcript Ingestion
```python
async def ingest_session_transcript(session_key: str):
    """Add main session context to Cognee for future recall"""
    
    transcript = get_transcript(session_key)
    
    await cognee.add(
        data=f"""
        SESSION: {session_key}
        DATE: {datetime.now()}
        TRANSCRIPT_SUMMARY: {summarize(transcript)}
        KEY_DECISIONS: {extract_decisions(transcript)}
        TOPICS: {extract_topics(transcript)}
        """,
        dataset="sloth-rog-sessions",
        node_set=["session", "main"]
    )
    
    await cognee.cognify("sloth-rog-sessions")
```

### 8.3: Heartbeat Memory Check
```python
# In HEARTBEAT.md flow

async def heartbeat_memory_check():
    """Periodically check Cognee for relevant context"""
    
    # Check for relevant context based on time/date
    context = await sloth_rog_recall(
        query="What should I remember or follow up on?",
        context_type="all"
    )
    
    if context.relevance > 0.7:
        return f"📌 Memory recall: {context.summary}"
    
    return "HEARTBEAT_OK"
```

### 8.4: Workspace File Indexing
```python
async def index_workspace():
    """Index all workspace files into Cognee"""
    
    for file in Path("workspace").rglob("*.md"):
        await cognee.add(
            data=file.read_text(),
            dataset="sloth-rog-workspace",
            node_set=["workspace", file.suffix]
        )
    
    await cognee.cognify("sloth-rog-workspace")
```

## Success Metrics

- [ ] Ancestors queryable via Cognee
- [ ] Bloodline dharma auto-derived
- [ ] Karma correlations visible in graph
- [ ] Spawn success rate improves
- [ ] Dream produces novel insights
- [ ] Soul alignment checkable
- [ ] **Sloth_rog can query Cognee for context**
- [ ] **Session transcripts auto-ingested**
- [ ] **Workspace files indexed and searchable**
- [ ] **Heartbeat uses Cognee for proactive recall**
