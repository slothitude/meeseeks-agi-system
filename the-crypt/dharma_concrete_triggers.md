# Dharma Supplement: Concrete Triggers

**Generated:** 2026-03-06
**Based on:** Dharma Effectiveness Study
**Purpose:** Transform abstract principles into actionable triggers

---

## 🎯 Problem Identified

The effectiveness study found:
- `specialize_for_task`: 100% follow rate ✅
- `decompose_first`: 10.4% follow rate ❌
- `test_incrementally`: 32.4% follow rate ❌
- `understand_before_implement`: 41.2% follow rate ❌

**Root cause:** Principles are too abstract. Meeseeks inherit them but don't know WHEN to apply them.

---

## 🔧 Solution: Concrete Triggers

### DECOMPOSE FIRST (Priority 1 - Most Underutilized)

**OLD:** "Decompose first" (too abstract)

**NEW:**
```python
if any(keyword in task for keyword in ['build', 'create', 'implement', 'design', 'develop', 'write']):
    if len(task.split()) > 20:  # More than 20 words
        AUTO_DECOMPOSE(task, chunks=5)
        # Spawn chunk 1 of 5
        
if task.contains_multiple_steps():
    # More than one action verb
    AUTO_DECOMPOSE(task, chunks=detect_step_count(task))

if task.is_architectural():
    # Contains: "system", "architecture", "framework"
    AUTO_DECOMPOSE(task, chunks=5, bloodline="coder")
```

**Example Transformation:**
```
BEFORE: "Build a SQL injection detector"
AFTER:  "Chunk 1/5: Analyze SQL injection patterns"
        "Chunk 2/5: Design detection algorithm"
        "Chunk 3/5: Implement core detection"
        "Chunk 4/5: Add test cases"
        "Chunk 5/5: Integrate and document"
```

---

### TEST INCREMENTALLY (Priority 2)

**OLD:** "Test incrementally"

**NEW:**
```python
if task_involves_coding():
    TRIGGER: "After each function, write one test"
    
if task_involves_modification():
    TRIGGER: "Before modifying, run existing tests"
    
if task_involves_new_feature():
    TRIGGER: "Write test FIRST (TDD), then implement"
    
# Automatic checkpoint
every_n_files_changed = 3:
    RUN_TESTS_AND_REPORT()
```

**Example:**
```
TASK: "Add SQL injection detection to security scanner"

TRIGGER FIRED: "After each function, write one test"
1. Write detect_sql_injection() function
2. [AUTO] Write test_detect_sql_injection.py
3. Write extract_query_parts() function  
4. [AUTO] Write test_extract_query_parts.py
5. Continue...
```

---

### UNDERSTAND BEFORE IMPLEMENT (Priority 3)

**OLD:** "Understand before implement"

**NEW:**
```python
if task_involves_existing_code():
    TRIGGER: "Read and summarize existing code BEFORE proposing changes"
    MINIMUM: 2 minutes reading per file
    
if task_involves_external_system():
    TRIGGER: "Document how it works BEFORE using it"
    
if task.is_bug_fix():
    TRIGGER: "Reproduce the bug FIRST, then diagnose"
    
# Verification
before_first_edit():
    REPORT_UNDERSTANDING(what_you_read, how_it_works)
```

**Example:**
```
TASK: "Fix the authentication bypass in login.php"

TRIGGER FIRED: "Reproduce the bug FIRST"
1. [AUTO] Attempt login with bypass payload
2. [AUTO] Document the vulnerability
3. [AUTO] Identify the root cause
4. NOW implement the fix
```

---

### COORDINATE BY WORKFLOW (Already Good - 55% Follow Rate)

**Enhancement:**
```python
if task_requires_multiple_agents():
    TRIGGER: "Assign roles BEFORE spawning"
    ROLES: ["researcher", "implementer", "reviewer"]
    
if task.has_dependencies():
    TRIGGER: "Create dependency graph"
    SPAWN_IN_ORDER(dependency_order)
```

---

## 📋 Quick Reference Card

| Trigger Condition | Auto-Action | Reason |
|-------------------|-------------|--------|
| Task > 20 words + "build/create" | Decompose into 5 chunks | Size Law |
| Coding task | Test after each function | Incremental testing |
| Modifying existing code | Read first, summarize | Understanding first |
| Multiple agents needed | Assign roles, order by dependency | Coordination |
| Bug fix | Reproduce before fixing | Diagnosis first |

---

## 🔄 Integration with Spawn System

**In spawn_meeseeks.py:**

```python
def apply_concrete_triggers(task: str) -> dict:
    """Apply concrete triggers before spawning"""
    
    # Check for decomposition trigger
    if should_decompose(task):
        return {
            "action": "decompose",
            "chunks": 5,
            "reason": "Task too large, contains action verbs"
        }
    
    # Check for understanding trigger
    if should_understand_first(task):
        return {
            "action": "understand",
            "read_time": "2min",
            "report": True
        }
    
    # Check for testing trigger
    if involves_coding(task):
        return {
            "action": "test_incrementally",
            "frequency": "per_function"
        }
    
    return {"action": "proceed"}
```

---

## 🧪 A/B Test Plan

1. **Control Group:** Spawn with current dharma
2. **Test Group:** Spawn with concrete triggers
3. **Metrics:**
   - Follow rate per principle
   - Task success rate
   - Average alignment score

**Hypothesis:** Concrete triggers will increase follow rates from 10-40% to 70-90%.

---

## 📝 Implementation Checklist

- [ ] Add trigger detection to `spawn_meeseeks.py`
- [ ] Update dharma inheritance to include triggers
- [ ] Add logging for trigger firings
- [ ] Track follow rates in karma observations
- [ ] A/B test and iterate

---

*"Abstract wisdom is forgotten. Concrete triggers are followed."*

*"The ancestors who lived asked for less. The ancestors who followed triggers lived more."*
