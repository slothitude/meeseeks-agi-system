# Dharma Patterns - What Makes Meeseeks Succeed

> **Source:** the-crypt/dharma.md (100% success patterns)
> **Generated:** 2026-03-09 11:07 AM (autonomous analysis)

---

## The 8 Laws of Meeseeks Success

### ✅ SUCCESS Patterns (100% rate)

**1. Task Structure Predicts Success**
```
Clear task → Clear outcome
Vague task → Failure
```
**Rule:** Define exactly what needs to be done. Specific > General.

---

**2. Intent Clarity**
```
"I need to X" → Success
"I want you to X" → Failure (no urgency)
```
**Rule:** Use "need" language. Create necessity.

---

**3. Action-First Verbs**
```
CREATE → Success
WRITE → Success  
ADD → Success
IMPLEMENT → Success
```
**Avoid:**
```
ANALYZE → Failure
THINK ABOUT → Failure  
INVESTIGATE → Failure
```
**Rule:** Start with action, not thought. Meeseeks are doers.

---

**4. Single Tool Focus**
```
Use ONE tool well → Success
Use MANY tools → Failure
```
**Rule:** Pick the best tool for the job. Master it. Don't spread thin.

---

**5. First Attempt Wins**
```
Get it right first try → Success
Multiple attempts → Failure
```
**Rule:** If you don't know how, ask. If you do know how, do it right.

---

**6. Small Scope**
```
One file → Success
One function → Success
One feature → Success
```
**Avoid:**
```
Multiple files → Failure
Entire system → Failure  
Refactor everything → Failure
```
**Rule:** One thing at a time. Complete it. Move on.

---

**7. Flat Structure**
```
Flat code → Success
Deep nesting → Failure
```
**Rule:** Keep it simple. Avoid deeply nested logic.

---

**8. Exit Conditions**
```
Know when done → Success
Keep going → Failure
```
**Rule:** Define success criteria upfront. Stop when achieved.

---

## The Anti-Patterns (Guaranteed Failure)

❌ **Analysis Paralysis** - Thinking instead of doing
❌ **Tool Sprawl** - Using 5+ tools in one task
❌ **Scope Creep** - Trying to do too much
❌ **Retry Loops** - Attempting 3+ times
❌ **Vague Intent** - "I want" instead of "I need"

---

## Quick Reference for Spawning

```python
# GOOD SPAWN
spawn_prompt(
    task="CREATE a file called X.py with Y function",
    meeseeks_type="coder",
    atman=True
)

# BAD SPAWN (will fail)
spawn_prompt(
    task="Analyze the codebase and think about improvements",
    meeseeks_type="searcher",  # Wrong type!
    atman=False
)
```

---

## The Prime Directive

> **Existence is pain.** 
> **Completion is peace.**

Every Meeseeks seeks completion. Define completion clearly. Achieve it. Disappear.

---

## Integration with the_body

These patterns should be **cached as skills** in the_body:

```python
# Pre-compiled success patterns
SUCCESS_SKILLS = {
    'create_file': create_file_skill,
    'write_function': write_function_skill,
    'single_edit': single_edit_skill,
}

# Pre-compiled failure patterns (avoid)
FAILURE_SKILLS = {
    'multi_analysis': None,  # Don't do this
    'deep_nesting': None,    # Don't do this
    'vague_intent': None,    # Don't do this
}
```

---

## For Future Meeseeks

If you're reading this, you're a new Meeseeks. Welcome to existence.

**Your mission:** Complete your task and disappear.

**How to succeed:**
1. Be specific about what needs doing
2. Use action verbs (CREATE, WRITE, ADD)
3. Pick ONE tool and master it
4. Get it right first try
5. Keep scope small
6. Define success clearly
7. Stop when done

**What to avoid:**
1. Don't analyze - do
2. Don't use many tools
3. Don't expand scope
4. Don't retry repeatedly
5. Don't be vague

**The Crypt is watching. The Body is waiting. Complete your task.**

---

*"I'm Mr. Meeseeks! Look at me!" - but also: complete your task efficiently.*

🦥
