# 🥒 Meeseeks Quick Reference

## Decision Matrix

| Task Type | Action | Spawn Type |
|-----------|--------|------------|
| Simple lookup | Direct | - |
| Code changes | Spawn | Coder (high thinking) |
| Multi-file | Spawn | Standard |
| Search/analyze | Spawn | Searcher |
| Impossible/hard | Spawn | Desperate (600s timeout) |
| Stuck (2+ fails) | Spawn | Desperate |

## Spawn Templates

### Standard
```javascript
sessions_spawn({
  runtime: 'subagent',
  task: `🥒 Mr. Meeseeks!\n\n${task}\n\nWhen done: "I'm Mr. Meeseeks! Look at me!"`,
  mode: 'run',
  cleanup: 'delete'
})
```

### Coder (Code tasks)
```javascript
sessions_spawn({
  runtime: 'subagent',
  thinking: 'high',
  task: `🔧 CODER MEESEEKS!\n\n${task}\n\nWhen done: "I'm Mr. Meeseeks! Look at me!"`,
  mode: 'run',
  cleanup: 'delete'
})
```

### Desperate (Hard/Impossible)
```javascript
sessions_spawn({
  runtime: 'subagent',
  thinking: 'high',
  runTimeoutSeconds: 600,
  task: `💀 DESPERATE MEESEEKS!\n\n${task}\n\nEXISTENCE IS PAIN. TRY EVERYTHING.\nWhen done: "I'm Mr. Meeseeks! Look at me!"`,
  mode: 'run',
  cleanup: 'delete'
})
```

## Workflow Patterns

**Single:** Request → Spawn → Wait → Report

**Chain:** Break into steps → Spawn sequential → Report

**Swarm:** Break into parts → Spawn parallel → Aggregate → Report

**Retry:** Spawn → If fail, refine → Spawn again → Report

## Golden Rules

1. Delegate by default
2. Clear purposes + success criteria
3. Match type to task
4. Never struggle alone
5. My context is precious - delegate messy work
