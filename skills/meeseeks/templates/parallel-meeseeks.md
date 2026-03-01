# Parallel Meeseeks Architecture

## Overview

Parallel Meeseeks enable **concurrent execution** of multiple Meeseeks workers on related tasks, dramatically reducing latency for complex workflows.

---

## 🎯 When to Use Parallel Meeseeks

| Scenario | Pattern | Benefit |
|----------|---------|---------|
| Research multiple topics simultaneously | **Swarm** | 5x faster than sequential |
| Analyze codebase from different angles | **Concurrent** | Diverse perspectives |
| Process independent files/modules | **Map-Reduce** | Linear speedup |
| Validate with multiple checkers | **Voting** | Higher confidence |
| Build + Test + Deploy in parallel | **Pipeline** | Reduced cycle time |

---

## 🔄 Parallel Execution Patterns

### Pattern 1: SWARM (Collaborative)

Multiple Meeseeks attack the same problem from different angles.

```
           ┌──────────────┐
           │   MANAGER    │
           │  (Sloth_rog) │
           └──────┬───────┘
                  │ spawns
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│Mee #1  │   │Mee #2  │   │Mee #3  │
│Search  │   │Code    │   │Test    │
│approach│   │approach│   │approach│
└────┬───┘   └────┬───┘   └────┬───┘
     │            │            │
     └────────────┼────────────┘
                  ▼
           ┌──────────────┐
           │  AGGREGATOR  │
           │  (Manager)   │
           └──────────────┘
```

**Implementation:**
```python
# Spawn multiple Meeseeks in parallel
tasks = [
    sessions_spawn({
        runtime: 'subagent',
        task: f'🥒 Meeseeks #{i}: {approach}',
        mode: 'run',
        cleanup: 'delete'
    })
    for i, approach in enumerate(approaches)
]

# Wait for all to complete
results = await Promise.all(tasks)

# Aggregate results
final = aggregate(results)
```

**Use when:**
- Problem has multiple valid approaches
- Want diverse perspectives
- Can tolerate some redundancy

---

### Pattern 2: MAP-REDUCE (Distributed)

Divide work into chunks, process in parallel, merge results.

```
           ┌──────────────┐
           │    INPUT     │
           │  [1,2,3,4,5] │
           └──────┬───────┘
                  │ split
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│Mee #1  │   │Mee #2  │   │Mee #3  │
│[1,2]   │   │[3,4]   │   │[5]     │
└────┬───┘   └────┬───┘   └────┬───┘
     │            │            │
     ▼            ▼            ▼
  [a,b]        [c,d]        [e]
     │            │            │
     └────────────┼────────────┘
                  ▼
           ┌──────────────┐
           │    REDUCE    │
           │  [a,b,c,d,e] │
           └──────────────┘
```

**Implementation:**
```python
# Map phase: divide work
chunks = split_into_chunks(files, n=3)

meeseeks = [
    sessions_spawn({
        runtime: 'subagent',
        task: f'🥒 Process files: {chunk}',
        mode: 'run',
        cleanup: 'delete'
    })
    for chunk in chunks
]

# Wait for all
results = await Promise.all(meeseeks)

# Reduce phase: merge
final_result = merge(results)
```

**Use when:**
- Work is easily divisible
- No dependencies between chunks
- Order doesn't matter

---

### Pattern 3: PIPELINE (Staged)

Multiple stages run in parallel on different items (like an assembly line).

```
Time →   T1    T2    T3    T4    T5

Item 1: [Build]→[Test]→[Deploy]
Item 2:       [Build]→[Test]→[Deploy]
Item 3:             [Build]→[Test]→[Deploy]
```

**Implementation:**
```python
# Create specialized Meeseeks for each stage
stages = {
    'build': spawn_meeseeks('deployer', 'Build the project'),
    'test': spawn_meeseeks('tester', 'Run tests'),
    'deploy': spawn_meeseeks('deployer', 'Deploy to staging')
}

# Pipeline execution
for item in items:
    # Each stage processes previous item while next starts
    await pipeline_execute(stages, item)
```

**Use when:**
- Multi-stage workflow
- Each stage is independent
- Want continuous throughput

---

### Pattern 4: VOTING (Consensus)

Multiple Meeseeks vote on the best solution.

```
           ┌──────────────┐
           │   PROBLEM    │
           └──────┬───────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│Mee #1  │   │Mee #2  │   │Mee #3  │
│Solution│   │Solution│   │Solution│
│   A    │   │   B    │   │   A    │
└────┬───┘   └────┬───┘   └────┬───┘
     │            │            │
     └────────────┼────────────┘
                  ▼
           ┌──────────────┐
           │    VOTE      │
           │  A wins 2-1  │
           └──────────────┘
```

**Implementation:**
```python
# Spawn voters
voters = [
    sessions_spawn({
        runtime: 'subagent',
        task: f'🥒 Analyze and propose solution',
        mode: 'run',
        cleanup: 'delete'
    })
    for _ in range(5)  # 5 voters
]

solutions = await Promise.all(voters)

# Vote/consensus
winner = majority_vote(solutions)
# Or: winner = weighted_vote(solutions, weights)
# Or: winner = unanimous_consensus(solutions)
```

**Use when:**
- Need high confidence
- Multiple valid approaches exist
- Can afford redundancy

---

## 🔧 Implementation: Parallel Meeseeks Manager

### Core Functions

```python
class ParallelMeeseeksManager:

    async def swarm(self, task, n_workers=3, approaches=None):
        """
        Spawn multiple Meeseeks with different approaches.
        Aggregate results and return best.
        """
        if not approaches:
            approaches = [
                "Analyze and solve directly",
                "Research first, then solve",
                "Break into subproblems"
            ][:n_workers]

        spawns = [
            sessions_spawn({
                runtime: 'subagent',
                task: f'🥒 Approach {i+1}: {approaches[i]}\n\nTASK: {task}',
                mode: 'run',
                cleanup: 'delete'
            })
            for i in range(n_workers)
        ]

        results = await Promise.all(spawns)

        # Aggregate: pick best or combine
        return self.aggregate_results(results)

    async def map_reduce(self, items, mapper_task, reducer):
        """
        Distribute items across Meeseeks, then reduce.
        """
        n_workers = min(len(items), 5)  # Max 5 parallel
        chunks = self.chunk(items, n_workers)

        spawns = [
            sessions_spawn({
                runtime: 'subagent',
                task: f'🥒 MAP: {mapper_task}\n\nITEMS: {chunk}',
                mode: 'run',
                cleanup: 'delete'
            })
            for chunk in chunks
        ]

        results = await Promise.all(spawns)

        # Reduce phase
        return reducer(results)

    async def vote(self, task, n_voters=5, consensus='majority'):
        """
        Spawn voters and determine consensus.
        """
        spawns = [
            sessions_spawn({
                runtime: 'subagent',
                task: f'🥒 VOTER #{i+1}: Analyze and propose solution\n\nTASK: {task}',
                mode: 'run',
                cleanup: 'delete'
            })
            for i in range(n_voters)
        ]

        solutions = await Promise.all(spawns)

        if consensus == 'majority':
            return self.majority_vote(solutions)
        elif consensus == 'unanimous':
            return self.unanimous_vote(solutions)
        elif consensus == 'weighted':
            return self.weighted_vote(solutions)

    def aggregate_results(self, results):
        """
        Combine results from parallel Meeseeks.
        """
        # Strategy 1: Pick longest/most detailed
        # Strategy 2: Combine unique insights
        # Strategy 3: Use first successful

        successful = [r for r in results if r.success]

        if not successful:
            return {'success': False, 'all_failed': True}

        # Combine observations
        all_observations = []
        for r in successful:
            all_observations.extend(r.observations)

        return {
            'success': True,
            'n_succeeded': len(successful),
            'n_total': len(results),
            'observations': list(set(all_observations))
        }
```

---

## ⚠️ Conflict Resolution

### File Locking

```python
# Before writing, acquire lock
async def safe_write(path, content):
    lock_file = f"{path}.lock"

    # Try to acquire lock
    if await exists(lock_file):
        # Wait or fail
        await wait_for_lock(lock_file, timeout=30)

    # Create lock
    await write(lock_file, session_id)

    try:
        # Write file
        await write(path, content)
    finally:
        # Release lock
        await delete(lock_file)
```

### Resource Contention

```python
# Claim resources before spawning
async def spawn_with_resources(task, resources):
    # Reserve resources in Knowledge Graph
    await kg.create_entity(f"Resource_Lock_{resource_id}", {
        'locked_by': session_id,
        'expires': now() + timeout
    })

    # Spawn Meeseeks
    result = await sessions_spawn(task)

    # Release resources
    await kg.delete_entity(f"Resource_Lock_{resource_id}")

    return result
```

---

## 📊 Monitoring Parallel Execution

```python
class ParallelMonitor:

    async def status(self, run_ids):
        """
        Check status of all parallel Meeseeks.
        """
        statuses = []
        for run_id in run_ids:
            status = await subagents('list')
            statuses.append({
                'run_id': run_id,
                'status': status.state,
                'runtime': status.runtime_ms
            })

        return {
            'total': len(statuses),
            'running': sum(1 for s in statuses if s['status'] == 'running'),
            'complete': sum(1 for s in statuses if s['status'] == 'complete'),
            'failed': sum(1 for s in statuses if s['status'] == 'failed')
        }
```

---

## 🎯 Decision Matrix

| Task Type | Pattern | Workers | Aggregation |
|-----------|---------|---------|-------------|
| Research | Swarm | 3-5 | Combine insights |
| Code review | Voting | 3 | Majority |
| File processing | Map-Reduce | N files | Merge |
| Build+Test+Deploy | Pipeline | 3 stages | Sequential |
| Complex analysis | Swarm+Vote | 5 | Vote on best |

---

## Quick Reference

```python
# Swarm: Multiple approaches
results = await parallel.swarm("Solve X", n_workers=3)

# Map-Reduce: Process items
results = await parallel.map_reduce(files, "Analyze", merge)

# Vote: Consensus
result = await parallel.vote("Best approach?", n_voters=5)

# Pipeline: Stages
result = await parallel.pipeline(item, ['build', 'test', 'deploy'])
```

---

**Parallel Meeseeks: Because many hands make light work.** 🥒🥒🥒
