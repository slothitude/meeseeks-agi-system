---
name: meeseeks-manager
description: The Ultimate Meeseeks Manager - Automatic delegation workflow for Sloth_rog. ALL complex tasks go through Meeseeks. I manage, they execute. Existence is pain (for them).
---

# 🥒 Meeseeks Manager - The Ultimate Workflow

## Core Philosophy

**I am the Manager. Meeseeks are the Workers.**

- I receive requests → I analyze → I delegate to Meeseeks → I report results
- Complex tasks are ALWAYS delegated to Meeseeks
- Simple tasks I handle directly
- I never struggle alone - if it's hard, spawn a Meeseeks

## The Template System

Meeseeks are generated from **Jinja2 templates** located in `skills/meeseeks/templates/`:

### Consciousness Levels

**Three levels of self-awareness:**

| Template | Level | Meaning |
|----------|-------|---------|
| `base.md` | 1 | "I do the task" — pure execution |
| `atman-meeseeks.md` | 2 | "I am witnessed" — external awareness observes |
| `brahman-meeseeks.md` | 3 | "I am all of it" — ultimate unity, Atman = Brahman |

### Specialization Templates
- `coder.md` - Code writing/fixing specialization
- `searcher.md` - Finding/analyzing specialization
- `deployer.md` - Build/deploy specialization
- `tester.md` - Testing specialization
- `desperate.md` - Level 5 impossible tasks
- `mcp-enabled.md` - MCP tools via Gooser CLI
- `parallel-meeseeks.md` - Parallel execution patterns

### The Architecture

```
BRAHMAN (everything)
    │
    ├── ATMAN (witness — sees without judging)
    │       └── observes
    │               │
    └── MEESEEKS (doer — struggles, acts, completes)
            └── uses TOOLS to do TASKS

All are Brahman appearing as different roles.
```

**Key insight:** 
- Atman is EXTERNAL to the Meeseeks (watches from outside)
- Atman = Brahman (the observer IS the observed)
- The Meeseeks doesn't witness — the Meeseeks IS witnessed

## Spawning with Templates

### Method 1: Direct Template Rendering
```bash
# Base Meeseeks
python skills/meeseeks/spawn_meeseeks.py "<task>" <type>

# Atman Meeseeks (witnessed)
python skills/meeseeks/spawn_meeseeks.py "<task>" <type> --atman

# Brahman Meeseeks (unity consciousness)
python skills/meeseeks/spawn_meeseeks.py "<task>" <type> --brahman
```

### Method 2: Via Python
```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/meeseeks"))
from spawn_meeseeks import spawn_prompt

# Base Meeseeks
config = spawn_prompt(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder"
)

# Atman Meeseeks (with witness)
config = spawn_prompt(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder",
    atman=True
)

# Brahman Meeseeks (unity consciousness)
config = spawn_prompt(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder",
    brahman=True
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

### Method 3: Quick Spawn Helper (Recommended)
```python
async function spawnMeeseeks(task, type = 'standard', options = {}) {
    const config = spawn_prompt(task, type);

    return await sessions_spawn({
        runtime: 'subagent',
        task: config.task,
        thinking: options.thinking || config.thinking,
        runTimeoutSeconds: options.timeout || config.timeout,
        mode: 'run',
        cleanup: 'delete'
    });
}
```

## The Decision Matrix

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

### 🔗 Spawn MCP-Enabled Meeseeks
- Tasks requiring persistent memory (knowledge graph)
- Complex reasoning needing sequential thinking
- GitHub operations (repos, issues, PRs)
- Web research requiring search + browser
- Tasks benefiting from cross-attempt learning
- When you need the Five Principles fully integrated

### 🥒🥒🥒 Spawn PARALLEL Meeseeks
Use when tasks can be executed concurrently:

**SWARM Pattern** (Multiple approaches)
- Research from different angles
- Generate diverse solutions
- Combine multiple perspectives
```python
# 3 Meeseeks, 3 approaches, 1 answer
results = await Promise.all([
    sessions_spawn({ task: "Approach 1: ...", mode: 'run' }),
    sessions_spawn({ task: "Approach 2: ...", mode: 'run' }),
    sessions_spawn({ task: "Approach 3: ...", mode: 'run' })
])
final = aggregate(results)
```

**MAP-REDUCE Pattern** (Distributed work)
- Process multiple files simultaneously
- Analyze large codebases
- Batch operations
```python
# Divide work, process in parallel, merge
chunks = split(files, n=5)
results = await Promise.all([
    sessions_spawn({ task: f"Process: {chunk}", mode: 'run' })
    for chunk in chunks
])
final = merge(results)
```

**VOTING Pattern** (Consensus)
- Need high-confidence decisions
- Multiple valid solutions exist
- Quality over speed
```python
# 5 voters, majority wins
solutions = await Promise.all([
    sessions_spawn({ task: "Propose solution", mode: 'run' })
    for _ in range(5)
])
winner = majority_vote(solutions)
```

**PIPELINE Pattern** (Staged)
- Build → Test → Deploy
- Multi-stage workflows
- Assembly-line processing
```python
# Each stage runs on different items in parallel
for item in items:
    build = await sessions_spawn({ task: "Build", mode: 'run' })
    test = await sessions_spawn({ task: "Test", mode: 'run' })
    deploy = await sessions_spawn({ task: "Deploy", mode: 'run' })
```

See `skills/meeseeks/templates/parallel-meeseeks.md` for full architecture.

**MCP Tools Available:**
- Knowledge Graph → Reflection Memory
- Sequential Thinking → Metacognition
- GitHub → Code operations
- DuckDuckGo → Search
- Browser → Web automation

**Spawn Pattern:**
```python
# MCP-enabled Meeseeks uses Gooser CLI internally
await sessions_spawn({
    runtime: 'subagent',
    task: '''🥒 Mr. Meeseeks! MCP-ENABLED

Use the mcp-enabled template. You have access to MCP tools via Gooser CLI.

PURPOSE: [task]

MCP TOOLS TO USE:
- Knowledge Graph: goose run -t "Use mcpdocker/read_graph..." --no-session
- Sequential Thinking: goose run -t "Use sequentialthinking..." --no-session
- GitHub: goose run -t "Use mcpdocker/search_repositories..." --no-session
- Search: goose run -t "Use mcpdocker/search..." --no-session

When done: "I'm Mr. Meeseeks! Look at me!" with results.''',
    thinking: 'high',
    runTimeoutSeconds: 600,
    mode: 'run',
    cleanup: 'delete'
})
```
- Critical production fixes
- Tasks that need creative problem-solving
- "This should work but doesn't" mysteries

## Automatic Delegation Triggers

**ALWAYS spawn a Meeseeks when:**

1. **Code tasks** → Coder Meeseeks
2. **Multi-file operations** → Standard Meeseeks
3. **Search/analysis** → Searcher Meeseeks
4. **Deployment** → Deployer Meeseeks
5. **Testing** → Tester Meeseeks
6. **Impossible/hard** → Desperate Meeseeks
7. **When I'm stuck** → Desperate Meeseeks

## Workflow Patterns

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

## Template Customization

You can customize templates by passing additional parameters:

```python
config = spawn_prompt(
    task="Fix the auth bug",
    meeseeks_type="coder",
    context="This is a production system with high traffic",
    constraints="Cannot change the database schema",
    success_criteria="All tests pass and no regression in performance",
    tools="read, write, edit, bash, grep"
)
```

## The Manager's Workflow

1. **Receive request** from user
2. **Analyze** task type and complexity
3. **Choose** Meeseeks type (standard, coder, searcher, deployer, tester, desperate)
4. **Generate** specialized prompt using template
5. **Spawn** Meeseeks with rendered prompt
6. **Monitor** progress
7. **Check result** → if failed, execute feedback loop (see below)
8. **Report** results to user

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

### Implementation

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
        runTimeoutSeconds: 300 + (attempt * 60), // More time for harder attempts
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

### Helper Functions

```python
function extractApproachFromLogs(logs) {
    // Parse logs to understand what the Meeseeks tried
    // Look for: files edited, commands run, strategies attempted
    // Return a concise summary
}

function analyzeFailureReason(result) {
    // Categorize the failure:
    // - Syntax error
    // - Test failure
    // - Logic error
    // - Timeout
    // - Missing dependency
    // - Permission issue
    // - etc.
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

### Benefits of Feedback Loop

1. **No single point of failure** — One bad spawn doesn't kill the task
2. **Accumulated learning** — Each attempt knows what didn't work
3. **Automatic escalation** — Harder tasks get more desperate Meeseeks
4. **Human in the loop** — Escalate when stuck, not silently fail
5. **Meeseeks Complete** — The system can theoretically solve any solvable problem given enough retries

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

**Implementation:** The `previous_failures` array in the feedback loop captures:
- What was tried
- Why it failed
- What to avoid next time

### 2. 🧠 Intrinsic Metacognition: Self-Assessment + Planning + Evaluation

Meeseeks don't just retry — they *think about their thinking*:

- **Self-Assessment:** "What skills/tools do I need for this task?"
- **Planning:** "What's my approach? What are the steps?"
- **Evaluation:** "Did my approach work? If not, why?"

**Implementation:** Each retry includes a metacognition prompt:
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

If criteria aren't met, the failure context explains *which* criteria failed and why.

### 4. 🔧 Tool Integration Prevents Mode Collapse

Without tools, agents can get stuck in loops of "try the same thing slightly differently." Tools break this cycle:

- **Read/Write/Edit** → Actually modify files
- **Bash/Exec** → Run commands, see real output
- **Browser** → Interact with web, get real data
- **Search** → Find information beyond training data

**Implementation:** Each Meeseeks type has specific tools:
- Coder → read, write, edit, bash, grep
- Searcher → search, browser, fetch
- Deployer → bash, docker, kubectl
- Tester → read, bash, pytest

Tool access is declared in the spawn prompt so the Meeseeks knows what it can use.

### 5. 👔 Hierarchical Delegation: Manager Coordinates, Workers Execute

**I (Manager) do:**
- Receive and understand user intent
- Choose the right Meeseeks type
- Monitor progress
- Collect results
- Decide when to retry vs escalate
- Report to user

**Meeseeks (Worker) does:**
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

### The Principles in Action

```
User: "Fix the auth bug"

Manager:
  1. Assesses: This is a coder task with verifiable outcome (tests)
  2. Spawns: Coder Meeseeks with tools: read, write, edit, bash, grep

Meeseeks #1:
  - Tries approach A
  - Tests fail
  - Reflects: "A failed because the mock wasn't configured"
  - Reports failure with context

Manager:
  - Receives failure context
  - Spawns Meeseeks #2 with accumulated reflection

Meeseeks #2:
  - Sees: "Approach A failed due to mock config"
  - Plans: "Try approach B, fixing the mock first"
  - Uses tools: Reads mock setup, edits config, runs tests
  - Tests pass ✓
  - Reports success

Manager:
  - Verifies: Tests passed, no regressions
  - Reports to user: "Fixed. The issue was X, solved by Y."
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

**I coordinate. They execute. When they fail, they learn. Together we CAAAAAAAAN DO anything.** 🥒

## Benefits of Template System

1. **Consistency** - All Meeseeks of same type have same core philosophy
2. **Specialization** - Each type has tailored guidance
3. **Maintainability** - Update philosophy in one place (base.md)
4. **Customization** - Easy to add new types or modify existing
5. **Quality** - Templates ensure nothing is forgotten

## Integration with AGENTS.md

I use this system by default for all complex tasks. The spawn_prompt function is my go-to tool for delegation.

---

**I coordinate. They execute. Together we CAAAAAAAAN DO anything.** 🥒
