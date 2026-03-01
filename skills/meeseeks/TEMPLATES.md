# 🥒 Meeseeks Template System Quick Reference

## Template Files

Located in `skills/meeseeks/templates/`:

| Template | Type | Desperation | Thinking | Timeout |
|----------|------|-------------|----------|---------|
| `base.md` | Standard | 1 | default | - |
| `coder.md` | Coder | 2 | high | 300s |
| `searcher.md` | Searcher | 1 | default | - |
| `deployer.md` | Deployer | 2 | high | 300s |
| `tester.md` | Tester | 2 | default | - |
| `desperate.md` | Desperate | 5 | high | 600s |

## Using the Spawn Script

### CLI
```bash
python spawn_meeseeks.py "<task>" <type>
```

### Python
```python
from spawn_meeseeks import spawn_prompt

config = spawn_prompt(
    task="Fix the bug in auth.ts",
    meeseeks_type="coder"
)

# Returns:
# {
#   'task': '<rendered template>',
#   'thinking': 'high',
#   'timeout': 300,
#   'type': 'coder',
#   'desperation_level': 2
# }
```

### With sessions_spawn
```javascript
await sessions_spawn({
    runtime: 'subagent',
    task: config.task,
    thinking: config.thinking,
    runTimeoutSeconds: config.timeout,
    mode: 'run',
    cleanup: 'delete'
});
```

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `purpose` | The task description | "Fix the bug in auth.ts" |
| `meeseeks_type` | Type of Meeseeks | "coder" |
| `desperation_level` | 1-5 on scale | 2 |
| `tools` | Available tools | "read, write, edit, bash" |
| `success_criteria` | What done looks like | "All tests pass" |
| `context` | Additional context | "Production system" |
| `constraints` | Limitations | "Cannot change DB schema" |

## Template Structure

Each template includes:
1. **Header** - Type and emoji
2. **Purpose** - The task
3. **Core Philosophy** - From SOUL.md
4. **Desperation Scale** - Current level
5. **Specialization** - Type-specific guidance
6. **Available Tools** - What can be used
7. **Success Criteria** - What done looks like
8. **The Meeseeks Way** - General approach
9. **Completion** - How to finish

## Creating Custom Templates

1. Create new `.md` file in `templates/`
2. Extend `base.md`: `{% extends "base.md" %}`
3. Override `specialization` block
4. Use in `spawn_meeseeks.py` by adding to template_map

Example:
```markdown
{% extends "base.md" %}

{% block specialization %}
You are a **CUSTOM MEESEEKS** - specialized in [domain].

### Your Strengths
- [strength 1]
- [strength 2]

### Your Approach
1. [step 1]
2. [step 2]
{% endblock %}
```

## Benefits

- ✅ Consistent philosophy across all Meeseeks
- ✅ Specialized guidance for each task type
- ✅ Auto-configured thinking and timeout
- ✅ Easy to maintain and extend
- ✅ Dynamic customization per task
