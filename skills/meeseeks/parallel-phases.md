# Parallel Meeseeks Implementation Phases

## Phase 1: Basic Parallel Spawn (Static Distribution) ✅

**Status:** IMPLEMENTED

**What it does:**
- Spawn multiple Meeseeks simultaneously
- Static work distribution (pre-defined chunks)
- Wait for all to complete
- Aggregate results

**Implementation:**
```python
# Phase 1: Static parallel spawn
async def parallel_spawn_static(tasks):
    """
    Spawn multiple Meeseeks with pre-defined tasks.
    Static distribution - work is divided upfront.
    """
    spawns = [
        sessions_spawn({
            runtime: 'subagent',
            task: task,
            mode: 'run',
            cleanup: 'delete'
        })
        for task in tasks
    ]
    
    # Wait for ALL to complete
    results = await Promise.all(spawns)
    
    return {
        'pattern': 'static_parallel',
        'n_workers': len(tasks),
        'results': results,
        'success_rate': sum(1 for r in results if r.success) / len(results)
    }
```

**Test Results:**
- 3 workers spawned simultaneously
- Each analyzes different aspect
- All run in parallel
- Manager aggregates results

**Limitations:**
- No coordination between workers
- No shared state
- If one fails, others continue (no retry)
- Static distribution can't adapt

---

## Phase 2: Coordination Layer (Shared State, Claims) 🔄

**Status:** READY TO IMPLEMENT

**What it adds:**
- Shared state via Knowledge Graph
- Resource claims to prevent conflicts
- Progress tracking
- Inter-worker communication

**Implementation:**
```python
# Phase 2: Coordinated parallel spawn
async def parallel_spawn_coordinated(tasks, session_id):
    """
    Spawn with coordination via Knowledge Graph.
    Workers can see each other's progress.
    """
    # Initialize coordination entity
    await kg.create_entity(f"Parallel_Session_{session_id}", {
        'status': 'running',
        'n_workers': len(tasks),
        'started': now(),
        'workers': []
    })
    
    spawns = []
    for i, task in enumerate(tasks):
        # Each worker claims its work
        worker_id = f"worker_{i}"
        await kg.add_observation(f"Parallel_Session_{session_id}", 
            f"Worker {worker_id} claimed task {i}")
        
        spawns.append(
            sessions_spawn({
                runtime: 'subagent',
                task: f"{task}\n\nCOORDINATION:\n- Session: {session_id}\n- Your ID: {worker_id}\n- Report progress to KG: Parallel_Session_{session_id}",
                mode: 'run',
                cleanup: 'delete'
            })
        )
    
    results = await Promise.all(spawns)
    
    # Mark complete
    await kg.add_observation(f"Parallel_Session_{session_id}", 
        f"Session complete. Success rate: {success_rate}")
    
    return results
```

**Benefits:**
- Workers can check KG for sibling progress
- Manager sees real-time updates
- Claims prevent duplicate work
- Post-mortem analysis possible

**To Implement:**
```python
# Add to parallel-meeseeks.py
class CoordinatedParallelManager:
    def __init__(self, kg_client):
        self.kg = kg_client
    
    async def spawn_with_claims(self, tasks):
        session_id = generate_uuid()
        await self._init_session(session_id, tasks)
        
        # Spawn with coordination context
        spawns = [
            self._spawn_with_claim(task, session_id, i)
            for i, task in enumerate(tasks)
        ]
        
        return await Promise.all(spawns)
    
    async def _spawn_with_claim(self, task, session_id, worker_id):
        # Claim in KG
        await self.kg.create_entity(
            f"Claim_{session_id}_{worker_id}",
            {'claimed_at': now(), 'task': task[:100]}
        )
        
        # Spawn with coordination instructions
        return await sessions_spawn({
            runtime: 'subagent',
            task: self._add_coordination(task, session_id, worker_id),
            mode: 'run',
            cleanup: 'delete'
        })
    
    def _add_coordination(self, task, session_id, worker_id):
        return f"""{task}

---
## COORDINATION PROTOCOL

You are Worker #{worker_id} in parallel session {session_id}.

BEFORE STARTING:
- Claim: goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': 'Worker {worker_id} starting'" --no-session

DURING WORK:
- Progress: goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': 'Worker {worker_id} progress: [update]'" --no-session

ON COMPLETE:
- Report: goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': 'Worker {worker_id} complete: [summary]'" --no-session

ON FAILURE:
- Report: goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': 'Worker {worker_id} FAILED: [error]'" --no-session
"""
```

---

## Phase 3: Resilience (Retries, Circuit Breakers) 📋

**Status:** DESIGN READY

**What it adds:**
- Automatic retry on failure
- Circuit breaker (stop spawning if too many fail)
- Timeout handling
- Fallback strategies

**Implementation:**
```python
# Phase 3: Resilient parallel spawn
class ResilientParallelManager(CoordinatedParallelManager):
    
    def __init__(self, kg_client, max_retries=2, circuit_threshold=0.3):
        super().__init__(kg_client)
        self.max_retries = max_retries
        self.circuit_threshold = circuit_threshold  # Break if <30% success
    
    async def spawn_with_resilience(self, tasks):
        session_id = generate_uuid()
        results = []
        failures = []
        
        for i, task in enumerate(tasks):
            # Circuit breaker check
            if len(results) > 0:
                success_rate = sum(1 for r in results if r.success) / len(results)
                if success_rate < self.circuit_threshold:
                    await self._trip_circuit(session_id, success_rate)
                    break
            
            # Retry loop
            for attempt in range(self.max_retries + 1):
                try:
                    result = await self._spawn_with_claim(task, session_id, i)
                    results.append(result)
                    
                    if result.success:
                        break  # Success, no retry
                    else:
                        failures.append({
                            'task_id': i,
                            'attempt': attempt,
                            'error': result.error
                        })
                        
                        if attempt < self.max_retries:
                            # Wait before retry
                            await sleep(2 ** attempt)  # Exponential backoff
                            
                except TimeoutError:
                    failures.append({
                        'task_id': i,
                        'attempt': attempt,
                        'error': 'timeout'
                    })
        
        return {
            'session_id': session_id,
            'results': results,
            'failures': failures,
            'success_rate': sum(1 for r in results if r.success) / len(results),
            'circuit_tripped': len(failures) > 0 and len(results) / (len(results) + len(failures)) < self.circuit_threshold
        }
    
    async def _trip_circuit(self, session_id, success_rate):
        await self.kg.add_observation(
            f"Parallel_Session_{session_id}",
            f"CIRCUIT BREAKER TRIPPED: Success rate {success_rate:.1%} below threshold"
        )
```

---

## Phase 4: Work-Stealing Queues 🚀

**Status:** DESIGN READY

**What it adds:**
- Dynamic work distribution
- Fast workers steal from slow workers
- Adaptive load balancing
- Optimal resource utilization

**Implementation:**
```python
# Phase 4: Work-stealing parallel spawn
class WorkStealingManager(ResilientParallelManager):
    
    def __init__(self, kg_client, n_workers=5):
        super().__init__(kg_client)
        self.n_workers = n_workers
    
    async def spawn_with_work_stealing(self, tasks):
        session_id = generate_uuid()
        
        # Create work queue in KG
        await self.kg.create_entity(f"WorkQueue_{session_id}", {
            'pending': tasks,
            'in_progress': [],
            'completed': [],
            'failed': []
        })
        
        # Spawn workers
        workers = [
            self._spawn_worker(session_id, worker_id)
            for worker_id in range(self.n_workers)
        ]
        
        # Wait for all workers to finish
        results = await Promise.all(workers)
        
        # Get final queue state
        queue_state = await self.kg.read_entity(f"WorkQueue_{session_id}")
        
        return {
            'session_id': session_id,
            'queue_state': queue_state,
            'worker_results': results
        }
    
    async def _spawn_worker(self, session_id, worker_id):
        return await sessions_spawn({
            runtime: 'subagent',
            task: f"""🥒 Worker #{worker_id} - WORK STEALING PROTOCOL

Session: {session_id}

## YOUR MISSION

Keep working until the queue is empty:

1. CLAIM WORK:
   goose run -t "Use mcpdocker/read_entity 'WorkQueue_{session_id}' to get pending tasks" --no-session
   goose run -t "Use mcpdocker/add_observation to 'WorkQueue_{session_id}': Move task X from pending to in_progress (worker {worker_id})" --no-session

2. DO WORK:
   [Execute the claimed task]

3. MARK COMPLETE:
   goose run -t "Use mcpdocker/add_observation to 'WorkQueue_{session_id}': Move task X from in_progress to completed (worker {worker_id})" --no-session

4. REPEAT:
   Go back to step 1 until no pending tasks remain.

## WORK STEALING

If you see a task in `in_progress` for >5 minutes:
- You can "steal" it by claiming it yourself
- Mark the original worker as "timed out"

## STOP CONDITION

When `pending` is empty and `in_progress` only has your tasks, you're done.

When done: "I'm Worker #{worker_id}! Queue empty!"
""",
            mode: 'run',
            cleanup: 'delete',
            runTimeoutSeconds: 300  # 5 min max per worker
        })
```

---

## Implementation Roadmap

| Phase | Feature | Status | Test |
|-------|---------|--------|------|
| **1** | Static parallel | ✅ Done | 3 workers spawned |
| **2** | Coordination | 📋 Ready | Next: Add KG claims |
| **3** | Resilience | 📋 Designed | Add retries |
| **4** | Work-stealing | 📋 Designed | Dynamic load balancing |

---

## Quick Reference

```python
# Phase 1: Static (current)
results = await parallel_spawn_static([task1, task2, task3])

# Phase 2: Coordinated (next)
results = await parallel_spawn_coordinated([task1, task2, task3], session_id)

# Phase 3: Resilient (future)
results = await spawn_with_resilience([task1, task2, task3])

# Phase 4: Work-stealing (future)
results = await spawn_with_work_stealing(all_tasks, n_workers=5)
```

---

**Phase 1 tested. Phase 2-4 designed. Ready to implement.** 🥒🥒🥒
