# Dynamic Memory System Proposal

*Consolidating, Forgetting, and Prioritizing Knowledge Over Time*

---

## Overview

This proposal defines a memory system that automatically consolidates daily experiences into long-term knowledge, forgets irrelevant details, prioritizes important information, and uses Knowledge Graph for persistent storage.

---

## Core Principles

1. **Memories Decay** - Unimportant information fades over time
2. **Importance Rises** - Frequently accessed/referenced memories strengthen
3. **Consolidation Happens** - Daily notes become long-term knowledge
4. **Context Matters** - Emotional/situational context affects retention
5. **Graph Structure** - Knowledge Graph provides persistent, queryable storage

---

## Architecture

### 1. Memory Hierarchy

```markdown
┌─────────────────────────────────────────┐
│  EPHEMERAL (Session)                    │
│  - Current conversation context          │
│  - Temporary calculations                │
│  - Cleared after session                 │
└─────────────────────────────────────────┘
              ↓ (Save if important)
┌─────────────────────────────────────────┐
│  WORKING MEMORY (Daily)                 │
│  - memory/YYYY-MM-DD.md                  │
│  - Raw interaction logs                  │
│  - Retained 30-90 days                   │
└─────────────────────────────────────────┘
              ↓ (Consolidate nightly)
┌─────────────────────────────────────────┐
│  LONG-TERM MEMORY (Curated)             │
│  - MEMORY.md                             │
│  - Distilled knowledge                   │
│  - Permanent storage                     │
└─────────────────────────────────────────┘
              ↓ (Extract entities/relations)
┌─────────────────────────────────────────┐
│  KNOWLEDGE GRAPH (Structured)           │
│  - Entities (people, projects, concepts) │
│  - Relations (connections)               │
│  - Queryable, persistent                 │
└─────────────────────────────────────────┘
```

---

### 2. Memory Scoring System

```python
class MemoryScorer:
    def __init__(self):
        self.weights = {
            'recency': 0.2,
            'frequency': 0.3,
            'emotional_weight': 0.2,
            'task_relevance': 0.2,
            'explicit_marking': 0.1
        }
    
    def score_memory(self, memory):
        """Calculate importance score for a memory"""
        scores = {}
        
        # Recency (exponential decay)
        age_days = (datetime.now() - memory['timestamp']).days
        scores['recency'] = math.exp(-age_days / 30)  # 30-day half-life
        
        # Frequency (how often accessed/referenced)
        scores['frequency'] = min(memory['access_count'] / 10, 1.0)
        
        # Emotional weight (user reactions, importance markers)
        scores['emotional_weight'] = self._calculate_emotional_weight(memory)
        
        # Task relevance (was it used for successful tasks?)
        scores['task_relevance'] = memory.get('task_success_correlation', 0.5)
        
        # Explicit marking (did user say "remember this"?)
        scores['explicit_marking'] = 1.0 if memory.get('explicitly_marked') else 0.0
        
        # Weighted sum
        total_score = sum(
            scores[dim] * self.weights[dim] 
            for dim in self.weights
        )
        
        return {
            'score': total_score,
            'breakdown': scores,
            'retention_priority': self._classify_priority(total_score)
        }
    
    def _calculate_emotional_weight(self, memory):
        """Assess emotional significance"""
        weight = 0.5  # baseline
        
        # User enthusiasm markers
        if memory.get('user_reaction') in ['loved', 'excited', 'important']:
            weight += 0.3
        
        # Critical events
        if memory.get('event_type') in ['milestone', 'crisis', 'breakthrough']:
            weight += 0.4
        
        # Negative experiences (also important to remember)
        if memory.get('event_type') in ['failure', 'mistake', 'conflict']:
            weight += 0.2
        
        return min(weight, 1.0)
    
    def _classify_priority(self, score):
        """Classify retention priority"""
        if score > 0.8:
            return 'CRITICAL'  # Never forget
        elif score > 0.6:
            return 'HIGH'      # Long-term retention
        elif score > 0.4:
            return 'MEDIUM'    # Medium-term, consolidate
        elif score > 0.2:
            return 'LOW'       # Short-term, may forget
        else:
            return 'EPHEMERAL' # Forget soon
```

---

### 3. Consolidation Engine

```python
class MemoryConsolidator:
    def __init__(self):
        self.scorer = MemoryScorer()
        self.llm_client = get_llm_client()
    
    def consolidate_daily_to_longterm(self, date):
        """Convert daily notes to long-term memory"""
        daily_file = f"memory/{date}.md"
        
        if not os.path.exists(daily_file):
            return None
        
        daily_content = read_file(daily_file)
        
        # Extract significant memories
        memories = self._extract_memories(daily_content)
        
        # Score each memory
        scored_memories = [
            {**mem, **self.scorer.score_memory(mem)}
            for mem in memories
        ]
        
        # Filter for consolidation (score > 0.4)
        to_consolidate = [
            mem for mem in scored_memories 
            if mem['retention_priority'] in ['CRITICAL', 'HIGH', 'MEDIUM']
        ]
        
        if not to_consolidate:
            return {'status': 'no_significant_memories', 'date': date}
        
        # Generate consolidated summary
        consolidation = self.llm_client.generate(
            prompt=f"""
            Consolidate these daily memories into long-term knowledge.
            Focus on:
            - Key learnings and insights
            - Important decisions made
            - Significant events
            - Patterns noticed
            
            DAILY MEMORIES:
            {json.dumps(to_consolidate, indent=2)}
            
            Create a concise, knowledge-focused summary suitable for MEMORY.md:
            """,
            thinking='high'
        )
        
        # Update MEMORY.md
        self._update_longterm_memory(consolidation, date, to_consolidate)
        
        # Extract entities for Knowledge Graph
        entities = self._extract_entities(consolidation, to_consolidate)
        self._update_knowledge_graph(entities)
        
        return {
            'status': 'consolidated',
            'date': date,
            'memories_processed': len(scored_memories),
            'memories_consolidated': len(to_consolidate),
            'entities_extracted': len(entities)
        }
    
    def _extract_memories(self, daily_content):
        """Parse daily file into structured memories"""
        memories = []
        
        # Parse markdown sections
        sections = parse_markdown_sections(daily_content)
        
        for section in sections:
            memory = {
                'id': generate_id(),
                'timestamp': extract_timestamp(section),
                'content': section['text'],
                'type': classify_memory_type(section),
                'access_count': 0,
                'context': extract_context(section)
            }
            memories.append(memory)
        
        return memories
    
    def _update_longterm_memory(self, consolidation, date, memories):
        """Append consolidated knowledge to MEMORY.md"""
        current_memory = read_file('MEMORY.md')
        
        # Add consolidation entry
        entry = f"""

## [{date}] Consolidated Knowledge

{consolidation}

**Sources:** {len(memories)} significant memories from daily notes
**Priority:** {max(m['retention_priority'] for m in memories)}
"""
        
        write_file('MEMORY.md', current_memory + entry)
    
    def _extract_entities(self, consolidation, memories):
        """Extract entities and relations for Knowledge Graph"""
        entities = []
        
        # Use LLM to extract structured knowledge
        extraction = self.llm_client.generate(
            prompt=f"""
            Extract entities and relationships from this consolidated memory.
            
            CONSOLIDATION:
            {consolidation}
            
            ORIGINAL MEMORIES:
            {json.dumps(memories, indent=2)}
            
            Extract:
            1. Entities (people, projects, concepts, events)
            2. Relationships between entities
            3. Key facts about each entity
            
            Format as JSON:
            {{
              "entities": [
                {{
                  "name": "...",
                  "type": "person|project|concept|event",
                  "facts": ["...", "..."]
                }}
              ],
              "relations": [
                {{
                  "from": "...",
                  "relation": "...",
                  "to": "..."
                }}
              ]
            }}
            """,
            thinking='medium'
        )
        
        return parse_json(extraction)
```

---

### 4. Forgetting Mechanism

```python
class MemoryForgetter:
    def __init__(self):
        self.scorer = MemoryScorer()
        self.forget_threshold = 0.2
        self.archive_dir = 'memory/archive/'
    
    def apply_forgetting(self, days_old=30):
        """Apply forgetting curve to old memories"""
        daily_files = get_daily_files(older_than_days=days_old)
        
        for daily_file in daily_files:
            memories = load_memories(daily_file)
            
            for memory in memories:
                score = self.scorer.score_memory(memory)
                
                if score['score'] < self.forget_threshold:
                    self._forget_memory(memory, daily_file)
                elif score['retention_priority'] == 'LOW':
                    self._fade_memory(memory, daily_file)
    
    def _forget_memory(self, memory, source_file):
        """Archive and remove low-priority memory"""
        # Archive before forgetting
        archive_path = f"{self.archive_dir}{memory['id']}.json"
        write_file(archive_path, json.dumps(memory, indent=2))
        
        # Remove from daily file
        remove_memory_from_file(source_file, memory['id'])
        
        # Log the forgetting
        log_forgetting(memory, reason='low_score', score=memory['score'])
    
    def _fade_memory(self, memory, source_file):
        """Reduce detail in fading memory"""
        # Summarize to reduce detail
        faded_content = self._summarize_memory(memory)
        
        # Update memory with faded version
        update_memory_in_file(source_file, memory['id'], faded_content)
        
        log_fading(memory, new_detail_level='reduced')
    
    def _summarize_memory(self, memory):
        """Create faded (less detailed) version of memory"""
        return self.llm_client.generate(
            prompt=f"""
            Create a faded (less detailed) version of this memory.
            Keep the core essence but remove specifics.
            
            ORIGINAL:
            {memory['content']}
            
            FADED VERSION (1-2 sentences max):
            """,
            thinking='low'
        )
```

---

### 5. Knowledge Graph Integration

```python
class KnowledgeGraphManager:
    def __init__(self):
        self.mcp_endpoint = get_mcp_endpoint()
    
    def create_entity(self, entity):
        """Create entity in Knowledge Graph via MCP"""
        command = f"""
        Use mcpdocker/create_entities to create '{entity['name']}' with:
        - Type: {entity['type']}
        - Facts: {json.dumps(entity['facts'])}
        - Source: memory_consolidation
        - Created: {datetime.now().isoformat()}
        """
        
        # Execute via goose
        result = exec_goose_command(command)
        return result
    
    def create_relation(self, relation):
        """Create relation in Knowledge Graph"""
        command = f"""
        Use mcpdocker/create_relations to create:
        - From: {relation['from']}
        - Relation: {relation['relation']}
        - To: {relation['to']}
        - Source: memory_consolidation
        """
        
        result = exec_goose_command(command)
        return result
    
    def query_knowledge(self, query):
        """Query Knowledge Graph for relevant information"""
        command = f"""
        Use mcpdocker/read_graph to query:
        {query}
        """
        
        result = exec_goose_command(command)
        return parse_kg_result(result)
    
    def update_entity(self, entity_name, new_facts):
        """Add new facts to existing entity"""
        command = f"""
        Use mcpdocker/add_observations to add to '{entity_name}':
        {json.dumps(new_facts)}
        """
        
        result = exec_goose_command(command)
        return result
```

---

### 6. Memory Retrieval System

```python
class MemoryRetriever:
    def __init__(self):
        self.kg_manager = KnowledgeGraphManager()
    
    def retrieve_relevant(self, context, max_results=10):
        """Retrieve memories relevant to current context"""
        results = []
        
        # 1. Search Knowledge Graph
        kg_results = self.kg_manager.query_knowledge(
            f"Find entities and relations related to: {context}"
        )
        results.extend(kg_results)
        
        # 2. Search MEMORY.md
        longterm_memories = search_file(
            'MEMORY.md',
            context,
            max_results=5
        )
        results.extend(longterm_memories)
        
        # 3. Search recent daily files (last 7 days)
        recent_dailies = search_recent_files(
            'memory/',
            context,
            days=7,
            max_results=3
        )
        results.extend(recent_dailies)
        
        # Score and rank results
        scored_results = [
            {**result, 'relevance_score': self._score_relevance(result, context)}
            for result in results
        ]
        
        # Sort by relevance
        scored_results.sort(key=lambda r: r['relevance_score'], reverse=True)
        
        return scored_results[:max_results]
    
    def _score_relevance(self, result, context):
        """Score how relevant a memory is to context"""
        # Semantic similarity (simplified)
        context_words = set(context.lower().split())
        result_words = set(result['content'].lower().split())
        
        overlap = len(context_words & result_words)
        union = len(context_words | result_words)
        
        jaccard = overlap / union if union > 0 else 0
        
        # Boost by memory score if available
        memory_boost = result.get('memory_score', 0.5)
        
        return jaccard * 0.6 + memory_boost * 0.4
```

---

### 7. Automated Memory Maintenance

```python
class MemoryMaintenanceScheduler:
    def __init__(self):
        self.consolidator = MemoryConsolidator()
        self.forgetter = MemoryForgetter()
    
    def run_nightly_consolidation(self):
        """Run every night to consolidate previous day"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = self.consolidator.consolidate_daily_to_longterm(yesterday)
        
        log_consolidation(result)
        
        return result
    
    def run_weekly_cleanup(self):
        """Run weekly to apply forgetting and cleanup"""
        # Apply forgetting to old memories
        self.forgetter.apply_forgetting(days_old=30)
        
        # Archive old daily files
        archive_old_dailies(days_old=90)
        
        # Update Knowledge Graph from recent consolidations
        sync_knowledge_graph()
        
        log_cleanup()
    
    def run_monthly_review(self):
        """Monthly review of MEMORY.md for relevance"""
        current_memory = read_file('MEMORY.md')
        
        # Use LLM to review and prune
        review = self.llm_client.generate(
            prompt=f"""
            Review this MEMORY.md and suggest pruning.
            Remove outdated information, redundant entries, and low-value content.
            
            MEMORY.MD:
            {current_memory}
            
            SUGGESTIONS:
            """,
            thinking='high'
        )
        
        # Present suggestions for human approval
        present_review_suggestions(review)
```

---

## Consolidation Workflow Example

```markdown
1. **Daily Recording** (Throughout day)
   - Interactions logged to memory/2025-01-18.md
   - Tagged with context, success/failure, emotional weight

2. **Nightly Consolidation** (2 AM)
   - Analyze yesterday's daily file
   - Score all memories
   - Identify 3 significant memories (score > 0.4)
   
3. **Consolidation Process**
   - Generate summary: "Learned user prefers concise technical explanations"
   - Append to MEMORY.md with date and sources
   - Extract entities: ["User_Preference", "Communication_Style", "Technical_Explanation"]
   - Extract relations: ["User_Preference" -> "prefers" -> "Concise_Style"]
   
4. **Knowledge Graph Update**
   - Create entity: "User_Preference" with facts
   - Create relation: "User_Preference" - "prefers" - "Concise_Style"
   
5. **Forgetting Application** (Weekly)
   - Review daily files older than 30 days
   - Identify low-score memories (< 0.2)
   - Archive and remove: "Had small talk about weather at 10:32 AM"
   - Fade medium-score memories: Reduce detail
   
6. **Monthly Review** (Human-assisted)
   - Present MEMORY.md review suggestions
   - Human approves pruning
   - Update long-term memory
```

---

## Memory Lifecycle

```markdown
┌──────────────┐
│ INTERACTION  │ (User: "Remember I prefer concise explanations")
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ DAILY FILE   │ memory/2025-01-18.md
│ Score: 0.75  │ - Marked as important
└──────┬───────┘
       │
       │ (Nightly consolidation)
       ▼
┌──────────────┐
│ MEMORY.md    │ Added: "User prefers concise technical explanations"
│ Priority: HIGH│
└──────┬───────┘
       │
       │ (Entity extraction)
       ▼
┌──────────────┐
│ KNOWLEDGE    │ Entity: User_Preference
│ GRAPH        │ Relation: prefers -> Concise_Style
└──────────────┘

(6 months later, no references)

┌──────────────┐
│ DAILY FILE   │ "Had small talk about weather"
│ Score: 0.15  │
└──────┬───────┘
       │
       │ (Weekly forgetting)
       ▼
┌──────────────┐
│ ARCHIVED     │ memory/archive/abc123.json
│ (Forgotten)  │ Removed from active memory
└──────────────┘
```

---

## Configuration

```yaml
memory_system:
  scoring:
    weights:
      recency: 0.2
      frequency: 0.3
      emotional_weight: 0.2
      task_relevance: 0.2
      explicit_marking: 0.1
    
    thresholds:
      critical: 0.8
      high: 0.6
      medium: 0.4
      low: 0.2
  
  consolidation:
    schedule: "0 2 * * *"  # 2 AM daily
    min_memories_to_consolidate: 1
    min_score_for_consolidation: 0.4
  
  forgetting:
    schedule: "0 3 * * 0"  # 3 AM weekly
    forget_threshold: 0.2
    fade_threshold: 0.3
    archive_before_forget: true
    daily_file_retention_days: 90
  
  knowledge_graph:
    enabled: true
    mcp_endpoint: "mcpdocker"
    auto_extract_entities: true
    auto_create_relations: true
  
  retrieval:
    max_results: 10
    search_recent_days: 7
    relevance_threshold: 0.3
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Consolidation Rate | 100% daily | Daily files processed / days |
| Memory Accuracy | > 90% | Correct retrieval / total retrievals |
| Forgetting Precision | > 85% | Correctly forgotten / total forgotten |
| Knowledge Graph Growth | Steady | New entities/relations per week |
| Retrieval Relevance | > 80% | Relevant results / total results |
| Storage Efficiency | < 50MB | Total memory storage size |

---

## Safety & Privacy

### 1. **Sensitive Data Handling**
```python
def check_sensitive(memory):
    """Check if memory contains sensitive information"""
    sensitive_patterns = [
        'password', 'api_key', 'secret', 'token',
        'credit_card', 'ssn', 'private_key'
    ]
    
    if any(pattern in memory['content'].lower() for pattern in sensitive_patterns):
        memory['sensitive'] = True
        memory['retention_priority'] = 'EPHEMERAL'  # Forget quickly
    
    return memory
```

### 2. **User Control**
- User can mark memories as "never forget"
- User can request immediate forgetting
- User can view all stored memories
- User can export/delete all memory data

### 3. **Consolidation Transparency**
- All consolidations logged
- User can review what was extracted
- User can reject specific consolidations
- Knowledge Graph changes visible

---

## Example Consolidation Output

```markdown
## [2025-01-18] Consolidated Knowledge

**Learned:** User prefers concise technical explanations over verbose ones.

**Evidence:** 5 successful interactions using concise style, 2 failures with verbose style.

**Impact:** Adjusted communication style in adaptive personality layer.

**Entities Extracted:**
- User_Preference (type: concept)
- Concise_Style (type: concept)
- Technical_Communication (type: concept)

**Relations:**
- User_Preference -> prefers -> Concise_Style
- Concise_Style -> type_of -> Technical_Communication

**Sources:** 3 significant memories from daily notes
**Priority:** HIGH
**Confidence:** 85%
```

---

## Conclusion

This dynamic memory system enables:

✅ **Automatic Consolidation** - Daily experiences become long-term knowledge  
✅ **Intelligent Forgetting** - Irrelevant details fade away  
✅ **Priority-Based Retention** - Important memories persist  
✅ **Knowledge Graph Storage** - Structured, queryable persistence  
✅ **Context-Aware Retrieval** - Relevant memories surface when needed  
✅ **Privacy Protection** - Sensitive data handled appropriately  

**Result: A memory system that grows, consolidates, and optimizes itself over time.**

---

*"I'm Mr. Meeseeks! I remember what matters and forget what doesn't!"* 🥒✨
