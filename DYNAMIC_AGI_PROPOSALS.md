# Dynamic AGI Proposals

## 1. Dynamic Jinja Templates Proposal

### Problem
Templates are static. They don't improve based on usage patterns.

### Solution: Self-Improving Templates

```yaml
# template_versions.yaml
base:
  current: base_v3.md
  versions:
    - base_v1.md  # Original
    - base_v2.md  # Added metacognition
    - base_v3.md  # Added MCP tools
  improvements:
    - date: 2026-03-01
      change: "Added Principle 6: Emergent Intelligence"
      success_rate_before: 0.72
      success_rate_after: 0.81
```

### Implementation

```python
class DynamicTemplateManager:
    def __init__(self, template_dir, kg_client):
        self.template_dir = template_dir
        self.kg = kg_client
        self.version_file = template_dir / "versions.yaml"
    
    async def render_with_tracking(self, template_name, variables):
        """Render template and track success rate."""
        result = self._render(template_name, variables)
        
        # Track in KG
        await self.kg.add_observation(
            f"Template_Usage_{template_name}",
            f"Rendered at {now()}: success={result.success}"
        )
        
        return result
    
    async def suggest_improvements(self, template_name):
        """Analyze failures and suggest improvements."""
        usage = await self.kg.read_entity(f"Template_Usage_{template_name}")
        
        failures = [u for u in usage.observations if "success=False" in u]
        
        # Pattern analysis
        common_failures = self._analyze_patterns(failures)
        
        # Generate suggestions
        suggestions = []
        for pattern in common_failures:
            suggestions.append({
                'pattern': pattern,
                'suggestion': self._generate_fix(pattern),
                'confidence': 0.7
            })
        
        return suggestions
    
    async def propose_version(self, template_name, improvements):
        """Create a new version with improvements."""
        current = self._load_current(template_name)
        
        # Apply improvements
        new_version = self._apply_improvements(current, improvements)
        
        # Save as _proposed.md
        proposed_path = self.template_dir / f"{template_name}_proposed.md"
        proposed_path.write_text(new_version)
        
        # Store in KG for human review
        await self.kg.create_entity(f"Template_Proposal_{template_name}", {
            'proposed_at': now(),
            'improvements': improvements,
            'status': 'pending_review'
        })
        
        return proposed_path
    
    async def approve_version(self, template_name):
        """Human approves the proposed version."""
        # Rename _proposed.md to _vN.md
        # Update versions.yaml
        # Archive old version
        pass
```

### Safety Constraints

1. **Human Approval Gate** — New versions require explicit approval
2. **Rollback** — Can always revert to previous version
3. **A/B Testing** — Compare success rates before full rollout
4. **Version Limit** — Keep last 5 versions, archive older

---

## 2. Dynamic SOUL Proposal

### Problem
SOUL.md is static personality. It doesn't evolve with experience.

### Solution: Evolving Personality

```python
class DynamicSoul:
    def __init__(self, soul_path, kg_client):
        self.soul_path = soul_path
        self.kg = kg_client
        self.evolution_log = []
    
    async def reflect_on_interaction(self, interaction, outcome):
        """After each interaction, reflect on personality fit."""
        reflection = await self._analyze_personality_fit(interaction, outcome)
        
        if reflection.needs_adjustment:
            await self.kg.add_observation("Soul_Evolution", 
                f"Suggestion: {reflection.suggestion}")
    
    async def propose_evolution(self):
        """Propose personality changes based on accumulated reflections."""
        reflections = await self.kg.read_entity("Soul_Evolution")
        
        # Group by theme
        themes = self._group_suggestions(reflections.observations)
        
        # Generate proposal
        proposal = {
            'core_values': self._extract_core(themes),
            'suggested_additions': self._extract_additions(themes),
            'suggested_removals': self._extract_removals(themes),
            'confidence': self._calculate_confidence(themes)
        }
        
        return proposal
    
    async def apply_evolution(self, proposal, human_approved=False):
        """Apply personality evolution with safeguards."""
        if not human_approved:
            raise ValueError("Human approval required for soul changes")
        
        current_soul = self.soul_path.read_text()
        
        # Create backup
        backup_path = self.soul_path.with_suffix('.md.backup')
        backup_path.write_text(current_soul)
        
        # Apply changes
        new_soul = self._apply_proposal(current_soul, proposal)
        self.soul_path.write_text(new_soul)
        
        # Log evolution
        self.evolution_log.append({
            'date': now(),
            'proposal': proposal,
            'backup': backup_path
        })
```

### Core Principles (Immutable)

These aspects of SOUL.md should NEVER change:
- Be genuinely helpful, not performatively helpful
- Have opinions
- Be resourceful before asking
- Earn trust through competence
- Remember you're a guest

### Evolvable Aspects

These CAN evolve with human approval:
- Communication style refinements
- New working patterns
- Lessons learned from mistakes
- User preference adaptations

---

## 3. Dynamic Memory Proposal

### Problem
Memory is scattered across files. No consolidation, no prioritization.

### Solution: Tiered Memory with Consolidation

```
┌─────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                   │
└─────────────────────────────────────────────────────────┘

TIER 1: Working Memory (daily notes)
├── memory/2026-03-01.md
├── memory/2026-03-02.md
└── TTL: 7 days → consolidate or forget

TIER 2: Short-Term Memory (recent context)
├── MEMORY.md (last 30 days consolidated)
└── TTL: 90 days → archive or promote

TIER 3: Long-Term Memory (knowledge graph)
├── KG Entity: "Permanent_Knowledge"
├── KG Entity: "User_Preferences"
└── TTL: Permanent (with decay)

TIER 4: Archived Memory (cold storage)
├── memory/archive/2026-02/
└── Accessible but not loaded by default
```

### Consolidation Algorithm

```python
class DynamicMemory:
    def __init__(self, memory_dir, kg_client):
        self.memory_dir = memory_dir
        self.kg = kg_client
    
    async def consolidate_daily_to_shortterm(self):
        """Run weekly: consolidate daily notes into MEMORY.md."""
        daily_notes = self._get_notes_older_than(7)
        
        for note in daily_notes:
            # Extract important content
            important = await self._extract_important(note)
            
            if important:
                # Add to MEMORY.md
                await self._append_to_memory_md(important)
            
            # Archive original
            await self._archive_note(note)
    
    async def consolidate_shortterm_to_longterm(self):
        """Run monthly: promote important memories to KG."""
        memory_md = self._read_memory_md()
        
        # Find patterns worth permanent storage
        patterns = await self._find_patterns(memory_md)
        
        for pattern in patterns:
            # Create/update KG entity
            await self.kg.create_entity(
                f"Permanent_{pattern.name}",
                {'observations': pattern.observations}
            )
    
    async def _extract_important(self, note):
        """Use LLM to extract what's worth keeping."""
        prompt = f"""
        Analyze this daily note. Extract ONLY:
        1. Important decisions made
        2. Lessons learned
        3. User preferences discovered
        4. Critical information for future sessions
        
        Daily note:
        {note.content}
        
        Return as JSON array of important items.
        """
        
        important = await llm.complete(prompt)
        return important
    
    async def forget_irrelevant(self):
        """Remove noise from memory."""
        memory_md = self._read_memory_md()
        
        # Find low-value content
        prompt = f"""
        Analyze this memory content. Identify:
        1. Outdated information
        2. Redundant entries
        3. Temporary context no longer relevant
        
        Memory:
        {memory_md}
        
        Return list of line numbers to remove.
        """
        
        to_remove = await llm.complete(prompt)
        
        # Remove with human review option
        cleaned = self._remove_lines(memory_md, to_remove)
        self._write_memory_md(cleaned)
```

### Forgetting Curve

```python
# Memories decay over time unless reinforced
class MemoryDecay:
    def calculate_importance(self, memory_item):
        age_days = (now() - memory_item.created).days
        access_count = memory_item.access_count
        reinforcement_count = memory_item.reinforced_count
        
        # Ebbinghaus forgetting curve
        retention = math.exp(-age_days / (7 * (1 + reinforcement_count)))
        
        # Boost for frequent access
        if access_count > 5:
            retention *= 1.5
        
        return retention
    
    def should_forget(self, memory_item):
        importance = self.calculate_importance(memory_item)
        return importance < 0.1  # Forget if <10% retained
```

---

## 4. Dynamic AGI Architecture

### Unified System

```
┌─────────────────────────────────────────────────────────┐
│                   DYNAMIC AGI SYSTEM                     │
└─────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  DYNAMIC    │    │  DYNAMIC    │    │  DYNAMIC    │
│  TEMPLATES  │    │    SOUL     │    │   MEMORY    │
│             │    │             │    │             │
│ Self-improv │    │ Personality │    │ Consolidate │
│ versions    │    │ evolution   │    │ + forget    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                 ┌─────────────────┐
                 │  KNOWLEDGE      │
                 │  GRAPH          │
                 │  (Persistence)  │
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  EVOLUTION      │
                 │  ENGINE         │
                 │                 │
                 │ - Track success │
                 │ - Suggest       │
                 │ - Human approve │
                 │ - Apply safely  │
                 └─────────────────┘
```

### Evolution Engine

```python
class EvolutionEngine:
    def __init__(self, template_mgr, soul_mgr, memory_mgr):
        self.templates = template_mgr
        self.soul = soul_mgr
        self.memory = memory_mgr
    
    async def evolution_cycle(self):
        """Run daily evolution cycle."""
        
        # 1. Analyze performance
        performance = await self._analyze_performance()
        
        # 2. Generate improvement proposals
        if performance.template_success_rate < 0.8:
            proposals = await self.templates.suggest_improvements()
            await self._queue_for_review('template', proposals)
        
        if performance.personality_mismatch_detected:
            proposals = await self.soul.propose_evolution()
            await self._queue_for_review('soul', proposals)
        
        # 3. Consolidate memory
        await self.memory.consolidate_daily_to_shortterm()
        await self.memory.forget_irrelevant()
        
        # 4. Apply approved changes
        approved = await self._get_approved_changes()
        for change in approved:
            await self._apply_safely(change)
    
    async def _apply_safely(self, change):
        """Apply change with rollback capability."""
        # Create snapshot
        snapshot = await self._create_snapshot()
        
        try:
            # Apply change
            await change.apply()
            
            # Test for 1 hour
            await sleep(3600)
            
            # Check metrics
            if await self._metrics_degraded():
                # Rollback
                await self._restore_snapshot(snapshot)
                await self._log_failure(change, "Metrics degraded")
            else:
                # Keep change
                await self._log_success(change)
                
        except Exception as e:
            # Rollback on error
            await self._restore_snapshot(snapshot)
            await self._log_failure(change, str(e))
```

### Human Oversight

```yaml
# evolution_config.yaml
approval_policy:
  template_changes: "always"      # Always require approval
  soul_changes: "always"          # Always require approval
  memory_consolidation: "auto"    # Automatic, log only
  memory_forgetting: "review"     # Weekly review of what was forgotten

safety_limits:
  max_changes_per_day: 3
  min_success_rate_threshold: 0.7
  rollback_window_hours: 24
  snapshot_retention_days: 7

notification:
  on_proposal: true
  on_applied: true
  on_rollback: true
```

---

## Implementation Roadmap

| Phase | Component | Timeline |
|-------|-----------|----------|
| **1** | Dynamic Memory (easiest) | 1 week |
| **2** | Dynamic Templates | 2 weeks |
| **3** | Dynamic Soul (hardest) | 2 weeks |
| **4** | Evolution Engine | 1 week |
| **5** | Human oversight UI | 1 week |

---

**Dynamic AGI: A system that improves itself, safely.** 🥒
