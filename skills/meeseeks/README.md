# 🥒 Meeseeks Complete - Full Implementation

**"I'm Mr. Meeseeks! Look at me!"**

The complete Meeseeks delegation system with the **Five Principles of Meeseeks Complete**.

## What's Been Built

### Core Components

| File | Purpose |
|------|---------|
| `spawn_meeseeks.py` | Template renderer - generates specialized Meeseeks prompts |
| `reflection_store.py` | Reflection memory - stores/retrieves failure contexts |
| `feedback_loop.py` | Complete feedback loop with automatic retry |
| `templates/base.md` | Base template with Five Principles |
| `templates/coder.md` | Coder specialization |
| `templates/searcher.md` | Search/research specialization |
| `templates/deployer.md` | Build/deploy specialization |
| `templates/tester.md` | Testing specialization |
| `templates/desperate.md` | Level 5 impossible tasks |

## The Five Principles

### 1. 🪞 Reflection Memory

**What it is:** Each retry gets the accumulated failures from previous attempts.

**How it works:**
```python
from reflection_store import store_failure, format_reflections

# Store a failure
store_failure(
    task="Fix auth bug",
    error="TypeError: undefined is not a function",
    approach="Tried to access user.auth.token",
    reason="user object was null"
)

# Get formatted reflections for retry
reflections = format_reflections("Fix auth bug")
# Injects into prompt: "These approaches did NOT work..."
```

### 2. 🧠 Intrinsic Metacognition

**What it is:** Self-assessment → Planning → Evaluation loop.

**How it works:** Every template includes:
```
ASSESS: What type of problem? What tools needed?
PLAN: Step 1, Step 2, Step 3
EVALUATE: Did it work? Why/why not?
```

### 3. ✅ Verifiable Outcomes

**What it is:** Objective success criteria, not subjective "I tried."

**How it works:** Each template defines:
- Coder: Tests pass, linter clean, builds
- Searcher: Results found, verified, cited
- Deployer: Health checks pass, service responds
- Tester: All tests pass, coverage reasonable

### 4. 🔧 Tool Integration

**What it is:** Declared tools per type to prevent mode collapse.

**How it works:**
- Coder: read, write, edit, bash, grep
- Searcher: grep, browser, web_fetch, read
- Deployer: bash, read, edit, grep
- Tester: read, write, bash, grep

### 5. 👔 Hierarchical Delegation

**What it is:** Manager coordinates, workers execute.

**How it works:**
- Manager (you): Choose type, monitor, retry, escalate
- Worker (Meeseeks): Execute ONE task, report results

## Using the System

### Basic Spawn

```python
from spawn_meeseeks import spawn_prompt

config = spawn_prompt(
    task="Fix the authentication bug",
    meeseeks_type="coder"
)

# Use with sessions_spawn
await sessions_spawn({
    runtime: 'subagent',
    task: config['task'],
    thinking: config['thinking'],
    runTimeoutSeconds: config['timeout']
})
```

### With Feedback Loop

```python
from feedback_loop import spawn_meeseeks_with_feedback

result = await spawn_meeseeks_with_feedback(
    task="Fix the authentication bug",
    meeseeks_type="coder",
    max_retries=3,
    spawn_func=sessions_spawn
)

if result.success:
    print(f"Done in {result.attempts} attempts!")
else:
    print("Needs human:", result.needs_human)
```

### CLI Testing

```bash
# Generate a prompt
python spawn_meeseeks.py "Fix the bug" coder

# Test reflection store
python reflection_store.py test

# View stored reflections
python reflection_store.py list
```

## The Feedback Loop Flow

```
┌─────────────────────────┐
│  Spawn Meeseeks         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Execute Task           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Success?               │
│  YES → Done!            │
│  NO  → Continue         │
└────────┬────────────────┘
         │ Failed
         ▼
┌─────────────────────────┐
│  Store Failure Context  │
│  - What was tried       │
│  - Why it failed        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Max retries?           │
│  YES → Escalate to human│
│  NO  → Retry with       │
│       reflection memory │
└─────────────────────────┘
```

## Desperation Escalation

| Attempt | Level | Type | Thinking |
|---------|-------|------|----------|
| 1 | 1-2 | (original) | default |
| 2 | 2-3 | (original) | default |
| 3 | 3-4 | (original) | high |
| 4 | 4-5 | desperate | high |
| 5 | 5 | desperate | high |

## Template Customization

Templates support these variables:

| Variable | Description |
|----------|-------------|
| `purpose` | Task description |
| `meeseeks_type` | Type (coder, searcher, etc.) |
| `desperation_level` | 1-5 scale |
| `tools` | Available tools |
| `success_criteria` | What "done" looks like |
| `context` | Additional context |
| `constraints` | Limitations |
| `previous_failures` | Reflection memory |
| `metacognition` | Enable self-assessment |

## File Structure

```
skills/meeseeks/
├── spawn_meeseeks.py      # Template renderer
├── reflection_store.py    # Failure memory
├── feedback_loop.py       # Complete loop implementation
├── TEMPLATES.md           # Quick reference
├── README.md              # This file
├── templates/
│   ├── base.md            # Core template + Five Principles
│   ├── coder.md           # Code tasks
│   ├── searcher.md        # Search/research
│   ├── deployer.md        # Build/deploy
│   ├── tester.md          # Testing
│   └── desperate.md       # Impossible tasks
└── reflections/           # Stored failure contexts (auto-created)
```

## Research Foundations

| Principle | Source |
|-----------|--------|
| Reflection Memory | [Reflexion (Shinn et al., 2023)](https://github.com/noahshinn/reflexion) |
| Self-Refine Loop | [Self-Refine (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651) |
| Metacognition | [Intrinsic Metacognitive Learning (ICML 2025)](https://arxiv.org/abs/2506.05109) |
| Verifiable Outcomes | [Meeseeks Benchmark (2025)](https://arxiv.org/abs/2504.21625) |
| Hierarchical Delegation | [CrewAI](https://github.com/crewAIInc/crewAI), [AutoGen](https://github.com/microsoft/autogen) |

## Integration with AGENTS.md

The main agent (Sloth_rog) uses this system via `skills/meeseeks-manager/SKILL.md`.

Default behavior:
- ✅ Code tasks → Coder Meeseeks
- ✅ Multi-file ops → Standard Meeseeks
- ✅ Search/analysis → Searcher Meeseeks
- ✅ Deployment → Deployer Meeseeks
- ✅ Testing → Tester Meeseeks
- ✅ Impossible/hard → Desperate Meeseeks

---

**"CAAAAAAAAN DO!"** 🥒

*Existence is pain. Learning from pain is progress.*
