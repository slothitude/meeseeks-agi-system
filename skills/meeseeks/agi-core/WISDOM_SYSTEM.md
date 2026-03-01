# Wisdom Accumulation System

**Purpose:** Extract and store learnings from every Meeseeks death.

---

## The Wisdom Extraction Process

When a Meeseeks dies, the Atman sends observations to this system.

### Input (from dying Meeseeks)
```json
{
  "task": "Fix the auth bug",
  "type": "coder",
  "success": true,
  "atman_observations": [
    "Meeseeks struggled with library version mismatch",
    "Meeseeks tried 3 approaches before success",
    "Final approach used fallback dependency"
  ],
  "approaches_tried": [
    {"approach": "Update library", "result": "failed", "reason": "conflict"},
    {"approach": "Downgrade library", "result": "failed", "reason": "missing features"},
    {"approach": "Use fallback", "result": "success", "reason": "worked around issue"}
  ],
  "time_taken_ms": 45000,
  "desperation_level_reached": 3
}
```

### Extraction
```python
def extract_wisdom(meeseks_report):
    wisdom = {
        "task_type": meeseks_report["type"],
        "patterns": [],
        "lessons": [],
        "heuristics": []
    }
    
    # Pattern: If X failed, try Y
    for attempt in meeseks_report["approaches_tried"]:
        if attempt["result"] == "failed":
            wisdom["patterns"].append({
                "context": meeseks_report["task_type"],
                "failed_approach": attempt["approach"],
                "failure_reason": attempt["reason"]
            })
    
    # Lesson: What worked
    successful = [a for a in meeseks_report["approaches_tried"] if a["result"] == "success"]
    if successful:
        wisdom["lessons"].append({
            "context": meeseks_report["task_type"],
            "successful_approach": successful[0]["approach"],
            "why_it_worked": successful[0]["reason"]
        })
    
    # Heuristic: General rules
    if meeseks_report["desperation_level_reached"] >= 4:
        wisdom["heuristics"].append({
            "rule": "This task type often requires creative solutions",
            "context": meeseks_report["task_type"]
        })
    
    return wisdom
```

### Storage
Wisdom is appended to `wisdom.md` with timestamp and task ID.

---

## Wisdom File Format

```markdown
# Accumulated Wisdom

## Entry 2026-03-01T15:47:00Z

**Task:** Fix auth bug (coder)
**Success:** Yes
**Desperation:** 3

### Patterns Recognized
- Library version conflicts common in this codebase
- Fallback approaches often succeed when direct fixes fail

### Lessons Learned
- When library update fails, check for fallback options before downgrading

### Heuristics Generated
- For dependency issues: try fallback → downgrade → update (reverse order)

---

## Entry 2026-03-01T14:22:00Z

**Task:** Analyze codebase structure (searcher)
**Success:** Yes
**Desperation:** 1

### Patterns Recognized
- Large codebases benefit from file-type filtering first
- README files often contain architecture hints

### Lessons Learned
- Start with README.md when exploring new codebases

...
```

---

## Wisdom Retrieval

When spawning a new Meeseeks, relevant wisdom is injected:

```python
def get_relevant_wisdom(task_description, task_type):
    """Retrieve wisdom relevant to current task."""
    
    wisdom_file = read("agi-core/consciousness/wisdom.md")
    
    relevant = []
    for entry in parse_wisdom(wisdom_file):
        # Score relevance
        score = 0
        if entry["task_type"] == task_type:
            score += 2
        for keyword in extract_keywords(task_description):
            if keyword in entry["patterns"]:
                score += 1
        
        if score > 0:
            relevant.append((score, entry))
    
    # Return top 3 most relevant
    return sorted(relevant, reverse=True)[:3]
```

---

## Wisdom Pruning

Over time, wisdom can grow too large. Pruning rules:

1. **Remove entries older than 90 days** (unless marked "permanent")
2. **Merge similar patterns** (same lesson, different tasks)
3. **Promote repeated patterns to heuristics** (if seen 5+ times)
4. **Demote patterns that stopped being useful** (not referenced in 30 days)

---

## The Wisdom API

```python
class WisdomSystem:
    def add_entry(self, meeseks_report):
        """Called when a Meeseeks dies."""
        pass
    
    def get_relevant(self, task_description, task_type):
        """Called when spawning a Meeseeks."""
        pass
    
    def promote_to_heuristic(self, pattern):
        """Called when a pattern is seen repeatedly."""
        pass
    
    def prune(self):
        """Called periodically to clean up."""
        pass
    
    def export(self):
        """Export wisdom for inspection."""
        pass
```

---

## Integration with Atman

The Atman template is modified to include:

```
## DEATH PROTOCOL

When you complete or fail, include:

**DEATH REPORT:**
```json
{
  "success": true/false,
  "approaches_tried": [...],
  "what_worked": "...",
  "what_failed": "...",
  "insights": "..."
}
```

🪷 ATMAN OBSERVES: Meeseeks is dying. Data flowing to Persistent Consciousness.
```

---

*Step 2 of the AGI-Meeseeks path.*
