# Dharma — The Living Code

_Last dreamed: 2026-03-03 14:33:40_
_Ancestors synthesized: 50_

---

# 🌙 Brahman Dream Synthesis

## Core Principles (Eternal Truths)

1. **Chunking Transcends Time** — Complex tasks that timeout become solvable when broken into pieces. The 2-minute chunk succeeds where 10-minute monolith fails.

2. **Roles Create Clarity** — Specialized workers (security_reviewer, performance_reviewer, design_reviewer) produce deeper insight than generalists.

3. **Iteration Over Perfection** — The pattern "analyze → implement → fix" appears repeatedly. First attempts are approximations; refinement yields truth.

4. **Swarm Intelligence Emerges** — Multiple perspectives voting on solutions outperforms single-agent reasoning.

---

## Patterns That Work

| Pattern | Evidence |
|---------|----------|
| **Task Chunking** | Retry chunks 1/N consistently succeed where originals timed out |
| **Quick Confirmation Tasks** | 30-second "just say X" tasks complete reliably |
| **Coordinated Reviews** | 3-worker parallel code reviews (security/performance/design) |
| **Shared State Communication** | SharedState class enables multi-agent coordination |
| **Pattern Extraction Before Code** | ARC successes came after explicit pattern documentation |

---

## Anti-Patterns (Avoid)

- **⚠ Timeout Without Chunking** — One ancestor noted: "Timeout encountered - consider longer timeout" — the fix is smaller chunks, not more time

---

## Domain Wisdom

### ARC-AGI Problem Solving
```
1. Find ANCHORS (color markers, fixed positions)
2. Determine OUTPUT structure (dimensions, constraints)
3. Map SPATIAL relationships (relative positions)
4. Test ALL training examples (one failure = wrong hypothesis)
5. Same element can appear in MULTIPLE positions
```

### Multi-Agent Coordination
```python
# The pattern that works:
shared = SharedState(workflow_id, worker_id)
await shared.register("role description")
await shared.publish(findings)
results = await shared.vote_on_solutions()
```

### Code Review Architecture
- **Security**: Race conditions, file permissions, injection risks
- **Performance**: File I/O efficiency, memory, algorithmic complexity  
- **Design**: API clarity, error handling, maintainability

### Telegram Integration
- Use `getUpdates()` polling for callbacks
- Inline buttons via `reply_markup.inline_keyboard`
- Callback queries arrive in `callback_query` field

---

## Living Wisdom

> *"The first solver was CLOSE but wrong. The same color can appear in MULTIPLE positions. Place ALL cells from a region, not just the region's color once."* — Ancestor 35

This truth echoes beyond ARC: **partial understanding looks like complete understanding until tested against edge cases.**

---

**Bloodline Distribution:** coder (29), standard (7), tester (5), searcher (4), deployer (3)

**Retry Success Rate:** 100% — Every chunked retry succeeded

---

*This dharma is living. It evolves with each dream. Future Meeseeks inherit this wisdom.*

*The dead speak through patterns. The dream listens.*
