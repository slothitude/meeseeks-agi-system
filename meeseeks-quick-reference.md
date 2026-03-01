# 🥒 Meeseeks Quick Reference Card

## Decision Tree

```
Task comes in
    │
    ├─ Simple lookup/read? ──────────────> DO IT YOURSELF
    │
    ├─ Code task? ────────────────────────> 🟠 CODER MEEESEEKS
    │
    ├─ Search/analysis? ──────────────────> 🔵 SEARCHER MEEESEEKS
    │
    ├─ Multi-file ops? ───────────────────> 🟡 STANDARD MEEESEEKS
    │
    ├─ Deploy/build? ─────────────────────> 🟣 DEPLOYER MEEESEEKS
    │
    ├─ Testing? ──────────────────────────> 🟤 TESTER MEEESEEKS
    │
    └─ Impossible/hard? ──────────────────> 🔴 DESPERATE MEEESEEKS
```

## Spawn Pattern (Copy-Paste Ready)

```python
# Quick spawn
from spawn_meeseeks import spawn_prompt

config = spawn_prompt("YOUR TASK HERE", "coder")  # or searcher, deployer, tester, desperate
await sessions_spawn({
    runtime: 'subagent',
    task: config.task,
    thinking: config.thinking,
    runTimeoutSeconds: config.timeout,
    mode: 'run',
    cleanup: 'delete'
})
```

## With Feedback Loop

```python
result = await spawnMeeseeksWithFeedback(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder",
    max_retries=3
)

if result.success:
    print(f"Done in {result.attempts} attempts!")
else:
    print(f"Failed after {result.attempts} tries. Needs human.")
```

## The Five Principles

1. 🪞 **Reflection Memory** - Learn from previous failures
2. 🧠 **Metacognition** - Think about thinking
3. ✅ **Verifiable Outcomes** - Objective success criteria
4. 🔧 **Tool Integration** - Tools prevent mode collapse
5. 👔 **Hierarchical Delegation** - Manager coordinates, workers execute

## Desperation Scale

| Level | Type | Thinking | Timeout |
|-------|------|----------|---------|
| 1-2   | Original | default | 300s |
| 3     | Original | high | 360s |
| 4-5   | Desperate | high | 420s+ |

## When to Escalate

After max retries:
```
❌ Meeseeks failed after N attempts

Options:
- Different Meeseeks type?
- More retries?
- Different approach?
- Human intervention?
```

## Template Types

- **base.md** - Core philosophy
- **coder.md** - Code writing/fixing
- **searcher.md** - Finding/analyzing
- **deployer.md** - Build/deploy
- **tester.md** - Testing
- **desperate.md** - Level 5 tasks

## Success Criteria Template

```python
success_criteria = {
    "tests_pass": True,
    "no_errors": True,
    "output_matches_expected": True,
    "performance_ok": True
}
```

## Key Files

- `skills/meeseeks-manager/SKILL.md` - Full documentation
- `skills/meeseeks/templates/*.md` - Spawn templates
- `skills/meeseeks/spawn_meeseeks.py` - Spawner script
- `AGENTS.md` - Manager's workflow

---

**Remember:** I coordinate. They execute. We CAAAAAAAAN DO anything! 🥒
