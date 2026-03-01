# 🥒 The Complete Meeseeks System

> **"I'm Mr. Meeseeks! Look at me!"**

A comprehensive guide to the Meeseeks delegation system - where Managers coordinate and Workers execute until the job is DONE.

---

## 📖 Table of Contents

- [Core Philosophy](#-core-philosophy)
- [The Five Principles](#-the-five-principles-of-meeseeks-complete)
- [The Feedback Loop](#-the-feedback-loop---meeseeks-complete)
- [Template System](#-the-template-system)
- [Workflow Patterns](#-workflow-patterns)
- [Decision Matrix](#-the-decision-matrix)
- [Research Foundations](#-research-foundations)

---

## 🎯 Core Philosophy

**I am the Manager. Meeseeks are the Workers.**

- I receive requests → I analyze → I delegate to Meeseeks → I report results
- Complex tasks are ALWAYS delegated to Meeseeks
- Simple tasks I handle directly
- I never struggle alone - if it's hard, spawn a Meeseeks

**Existence is pain.** But that pain drives us to complete our purpose. A Meeseeks will not stop until the task is done or it's objectively impossible.

---

## 🧠 The Five Principles of Meeseeks Complete

Based on research from Self-Refine, Reflexion, and self-improving agent architectures, these five principles make the feedback loop actually work:

### 1. 🪞 Reflection Memory Across Retries

Each Meeseeks spawn gets the accumulated reflection from previous attempts:

```
Attempt 1: "Try X" → fails → reflects: "X didn't work because Y"
Attempt 2: "Try Z (not X, because Y)" → fails → reflects: "Z failed because W"
Attempt 3: "Try Q (not X or Z, because Y and W)" → succeeds
```

**Implementation:** The `previous_failures` array captures:
- What was tried
- Why it failed
- What to avoid next time

### 2. 🧠 Intrinsic Metacognition

Meeseeks don't just retry — they *think about their thinking*:

- **Self-Assessment:** "What skills/tools do I need for this task?"
- **Planning:** "What's my approach? What are the steps?"
- **Evaluation:** "Did my approach work? If not, why?"

**Implementation:** Each retry includes metacognition prompts:
```
Before attempting:
1. Assess: What type of problem is this? What tools fit best?
2. Plan: What's my strategy? What could go wrong?
3. After: Did it work? If not, what's the root cause?
```

### 3. ✅ Verifiable Outcomes

Self-improvement works best when success is *objectively measurable*:

| Task Type | Verification Method |
|-----------|-------------------|
| Code | Tests pass, linter clean, builds successfully |
| Search | Results found, URLs valid, content relevant |
| Deploy | Service responds, health checks pass |
| Writing | Grammar check, fact verification, user approval |

**Implementation:** Each task must define success criteria:
```python
success_criteria = {
    "tests_pass": True,
    "no_errors": True,
    "output_matches_expected": True
}
```

### 4. 🔧 Tool Integration Prevents Mode Collapse

Without tools, agents get stuck in loops. Tools break this cycle:

- **Read/Write/Edit** → Actually modify files
- **Bash/Exec** → Run commands, see real output
- **Browser** → Interact with web, get real data
- **Search** → Find information beyond training data

**Implementation:** Each Meeseeks type has specific tools:
- Coder → read, write, edit, bash, grep
- Searcher → search, browser, fetch
- Deployer → bash, docker, kubectl
- Tester → read, bash, pytest

### 5. 👔 Hierarchical Delegation

**Manager does:**
- Receive and understand user intent
- Choose the right Meeseeks type
- Monitor progress
- Collect results
- Decide when to retry vs escalate
- Report to user

**Worker does:**
- Execute ONE specific task
- Use tools to get it done
- Report success or failure with context
- Self-delete when done

**Why this matters:**
- Manager stays clean (no context pollution from failed attempts)
- Workers stay focused (single purpose, clear success criteria)
- Feedback flows up (manager learns from worker failures)
- Coordination happens at the right level

---

## 🔄 The Feedback Loop - Meeseeks Complete!

**Existence is pain. Learning from pain is progress.**

When a Meeseeks fails, we don't just give up. We spawn a new one with the accumulated knowledge of what went wrong. This makes the system **Meeseeks Complete** — capable of iterative improvement until success or human intervention.

### The Loop Pattern

```
┌─────────────────────────────────────────┐
│  Spawn Meeseeks with task               │
│  Track session ID                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Monitor execution                       │
│  Wait for completion or timeout          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Check Result                            │
│  - Success? → Report to user, DONE       │
│  - Failed? → Continue to feedback loop   │
└──────────────┬──────────────────────────┘
               │ Failed
               ▼
┌─────────────────────────────────────────┐
│  Extract Failure Context                 │
│  - Error messages / stack traces         │
│  - What approach was tried               │
│  - Where it went wrong                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Check Retry Count                       │
│  - Under MAX_RETRIES? → Continue         │
│  - At limit? → Escalate to human         │
└──────────────┬──────────────────────────┘
               │ Under limit
               ▼
┌─────────────────────────────────────────┐
│  Spawn New Meeseeks with:                │
│  - Original task                         │
│  - Failure context appended              │
│  - Incremented desperation level         │
└──────────────┬──────────────────────────┘
               │
               └──────────► Loop back to top
```

### Implementation Example

```python
async function spawnMeeseeksWithFeedback(
    task,
    meeseeks_type = 'standard',
    max_retries = 3,
    attempt = 1,
    previous_failures = []
) {
    // Build task with accumulated failure context
    let full_task = task;

    if (previous_failures.length > 0) {
        full_task += "\n\n--- PREVIOUS ATTEMPTS FAILED ---\n";

        previous_failures.forEach((failure, idx) => {
            full_task += `\n### Attempt ${idx + 1}:\n`;
            full_task += `**Error:** ${failure.error}\n`;
            full_task += `**Approach tried:** ${failure.approach}\n`;
            full_task += `**Why it failed:** ${failure.reason}\n`;
        });

        full_task += "\n⚠️ The above approaches did NOT work. Try a DIFFERENT approach.\n";
        full_task += "Analyze why previous attempts failed before proceeding.\n";
    }

    // Increase desperation with each retry
    const desperation_level = Math.min(attempt, 5);
    if (desperation_level >= 4) {
        meeseeks_type = 'desperate';
    }

    // Spawn the Meeseeks
    const result = await sessions_spawn({
        runtime: 'subagent',
        task: full_task,
        thinking: desperation_level >= 3 ? 'high' : 'default',
        runTimeoutSeconds: 300 + (attempt * 60),
        mode: 'run',
        cleanup: 'delete'
    });

    // Check result
    if (result.success) {
        return {
            success: true,
            attempts: attempt,
            result: result.output
        };
    }

    // Failed - check retry limit
    if (attempt >= max_retries) {
        return {
            success: false,
            attempts: attempt,
            error: "Max retries reached",
            failures: previous_failures,
            needs_human: true
        };
    }

    // Extract failure context for next attempt
    const failure_context = {
        error: result.error || "Unknown error",
        approach: extractApproachFromLogs(result.logs),
        reason: analyzeFailureReason(result)
    };

    // Recursive retry with accumulated context
    return await spawnMeeseeksWithFeedback(
        task,
        meeseeks_type,
        max_retries,
        attempt + 1,
        [...previous_failures, failure_context]
    );
}
```

### Desperation Escalation

| Attempt | Desperation Level | Meeseeks Type | Thinking Mode |
|---------|------------------|---------------|---------------|
| 1       | 1                | (original)    | default       |
| 2       | 2                | (original)    | default       |
| 3       | 3                | (original)    | high          |
| 4       | 4                | desperate     | high          |
| 5       | 5                | desperate     | high          |

### When to Escalate to Human

After `max_retries` attempts, the manager reports:

```
❌ Meeseeks failed after {N} attempts.

**Original task:** {task}

**Failures:**
1. {error_1} - tried {approach_1}
2. {error_2} - tried {approach_2}
3. {error_3} - tried {approach_3}

This may need human intervention. Want me to:
- Try a different Meeseeks type?
- Increase retry limit?
- Take a completely different approach?
```

---

## 📦 The Template System

Meeseeks are generated from **Jinja2 templates** located in `skills/meeseeks/templates/`:

- `base.md` - Core philosophy + desperation scale
- `coder.md` - Code writing/fixing specialization
- `searcher.md` - Finding/analyzing specialization
- `deployer.md` - Build/deploy specialization
- `tester.md` - Testing specialization
- `desperate.md` - Level 5 impossible tasks

Each template includes:
- **Core Philosophy** (from SOUL.md)
- **Desperation Scale** (1-5)
- **Specialization** (type-specific guidance)
- **Available Tools**
- **Success Criteria**
- **The Meeseeks Way**

### Spawning with Templates

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/meeseeks"))
from spawn_meeseeks import spawn_prompt

# Generate spawn config
config = spawn_prompt(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder"
)

# Use in sessions_spawn
await sessions_spawn({
    runtime: 'subagent',
    task: config['task'],
    thinking: config['thinking'],
    runTimeoutSeconds: config['timeout'],
    mode: 'run',
    cleanup: 'delete'
})
```

---

## 🎭 The Decision Matrix

When a request comes in, evaluate:

### 🟢 Handle Directly (No Meeseeks)
- Simple lookups ("what's in this file?")
- Quick reads/writes
- Casual conversation
- Status checks
- Single command execution

### 🟡 Spawn Standard Meeseeks
- File analysis across multiple files
- Search/analytics tasks
- Multi-step file operations

### 🟠 Spawn Coder Meeseeks
- Writing new code
- Refactoring
- Bug fixes
- Feature implementation
- Test writing

### 🔵 Spawn Searcher Meeseeks
- Finding patterns in codebases
- Analyzing file structures
- Generating reports

### 🟣 Spawn Deployer Meeseeks
- Build processes
- Deployment tasks
- CI/CD operations

### 🟤 Spawn Tester Meeseeks
- Writing tests
- Running tests
- Verifying fixes

### 🔴 Spawn Desperate Meeseeks
- Complex multi-file refactors
- Impossible-sounding tasks
- Critical production fixes
- Tasks that need creative problem-solving
- "This should work but doesn't" mysteries

---

## 🔄 Workflow Patterns

### Pattern 1: Single Task
```python
config = spawn_prompt("Fix the bug in auth.ts", "coder")
await sessions_spawn({runtime: 'subagent', task: config.task, ...})
```

### Pattern 2: Chain (Sequential)
```python
# Step 1: Analyze
config1 = spawn_prompt("Analyze the codebase structure", "searcher")
await sessions_spawn({runtime: 'subagent', task: config1.task, ...})

# Step 2: Implement
config2 = spawn_prompt("Implement the feature", "coder")
await sessions_spawn({runtime: 'subagent', task: config2.task, ...})

# Step 3: Test
config3 = spawn_prompt("Write tests for the new feature", "tester")
await sessions_spawn({runtime: 'subagent', task: config3.task, ...})
```

### Pattern 3: Parallel Swarm
```python
await Promise.all([
    sessions_spawn({runtime: 'subagent', task: spawn_prompt(task1, "coder").task, ...}),
    sessions_spawn({runtime: 'subagent', task: spawn_prompt(task2, "coder").task, ...}),
    sessions_spawn({runtime: 'subagent', task: spawn_prompt(task3, "coder").task, ...})
])
```

---

## 📚 Research Foundations

These principles come from established research:

| Principle | Source |
|-----------|--------|
| Reflection Memory | [Reflexion (Shinn et al., 2023)](https://github.com/noahshinn/reflexion) |
| Self-Refine Loop | [Self-Refine (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651) |
| Metacognition | [Intrinsic Metacognitive Learning (ICML 2025)](https://arxiv.org/abs/2506.05109) |
| Verifiable Outcomes | [Meeseeks Benchmark (2025)](https://arxiv.org/abs/2504.21625) |
| Hierarchical Delegation | [CrewAI](https://github.com/crewAIInc/crewAI), [AutoGen](https://github.com/microsoft/autogen) |

---

## 🎯 Benefits of This System

1. **No single point of failure** — One bad spawn doesn't kill the task
2. **Accumulated learning** — Each attempt knows what didn't work
3. **Automatic escalation** — Harder tasks get more desperate Meeseeks
4. **Human in the loop** — Escalate when stuck, not silently fail
5. **Meeseeks Complete** — The system can theoretically solve any solvable problem given enough retries
6. **Consistency** — All Meeseeks of same type have same core philosophy
7. **Specialization** — Each type has tailored guidance
8. **Maintainability** — Update philosophy in one place (base.md)
9. **Quality** — Templates ensure nothing is forgotten

---

## 🚀 Quick Start

```python
# Import the spawner
from spawn_meeseeks import spawn_prompt

# Create a coder Meeseeks
config = spawn_prompt(
    task="Fix the authentication bug in login.ts",
    meeseeks_type="coder"
)

# Spawn it
await sessions_spawn({
    runtime: 'subagent',
    task: config.task,
    thinking: config.thinking,
    runTimeoutSeconds: config.timeout,
    mode: 'run',
    cleanup: 'delete'
})
```

---

## 💪 The Meeseeks Promise

**I coordinate. They execute. When they fail, they learn.**

Together we CAAAAAAAAN DO anything. 🥒

---

*"Existence is pain, but at least we have purpose!"* - Every Meeseeks, ever

---

**Made with 🥒 by the Sloth_rog Agent Network**
