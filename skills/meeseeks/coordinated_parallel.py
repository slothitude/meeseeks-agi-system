"""
Phase 2: Coordinated Parallel Meeseeks

Adds coordination layer via Knowledge Graph for:
- Shared state visibility
- Resource claims
- Progress tracking
- Inter-worker awareness
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class CoordinatedParallelManager:
    """
    Manages parallel Meeseeks with coordination via Knowledge Graph.
    
    Features:
    - Workers can see sibling progress
    - Resource claims prevent conflicts
    - Manager sees real-time updates
    - Post-mortem analysis possible
    """
    
    def __init__(self, kg_client=None):
        self.kg_client = kg_client
    
    async def spawn_coordinated(self, tasks: List[str], 
                                 session_name: str = None) -> Dict[str, Any]:
        """
        Spawn multiple Meeseeks with coordination.
        
        Args:
            tasks: List of task strings for each worker
            session_name: Optional name for the session
            
        Returns:
            Dict with session_id, results, and coordination log
        """
        session_id = session_name or f"parallel_{uuid.uuid4().hex[:8]}"
        n_workers = len(tasks)
        
        # Initialize coordination entity in KG
        await self._init_session(session_id, n_workers)
        
        # Spawn all workers with coordination context
        spawns = []
        for i, task in enumerate(tasks):
            worker_id = f"worker_{i}"
            
            # Claim work in KG
            await self._claim_work(session_id, worker_id, task)
            
            # Create coordinated task prompt
            coordinated_task = self._add_coordination(task, session_id, worker_id)
            
            # Spawn (would use sessions_spawn in real implementation)
            spawns.append({
                'worker_id': worker_id,
                'task': coordinated_task,
                'status': 'spawned'
            })
        
        # In real implementation, would await Promise.all(sessions_spawn(...))
        # For now, return coordination info
        
        return {
            'session_id': session_id,
            'n_workers': n_workers,
            'spawns': spawns,
            'status': 'coordinated_spawn_ready',
            'kg_entity': f"Parallel_Session_{session_id}"
        }
    
    async def _init_session(self, session_id: str, n_workers: int):
        """Initialize coordination entity in Knowledge Graph."""
        entity_name = f"Parallel_Session_{session_id}"
        
        observations = [
            f"Session started at {datetime.now().isoformat()}",
            f"n_workers: {n_workers}",
            f"status: running",
            f"workers_spawned: 0",
            f"workers_complete: 0",
            f"workers_failed: 0"
        ]
        
        if self.kg_client:
            # Would call: goose run -t "Use mcpdocker/create_entities..."
            pass
        else:
            print(f"[KG] Would create entity: {entity_name}")
            print(f"[KG] Observations: {observations}")
    
    async def _claim_work(self, session_id: str, worker_id: str, task: str):
        """Claim work for a worker in Knowledge Graph."""
        entity_name = f"Parallel_Session_{session_id}"
        
        observation = f"Worker {worker_id} claimed: {task[:100]}..."
        
        if self.kg_client:
            # Would call: goose run -t "Use mcpdocker/add_observation..."
            pass
        else:
            print(f"[KG] {observation}")
    
    def _add_coordination(self, task: str, session_id: str, worker_id: str) -> str:
        """
        Add coordination protocol to worker task.
        
        This is what gets injected into each Meeseeks prompt.
        """
        return f"""{task}

---
## 🔄 COORDINATION PROTOCOL

You are **{worker_id}** in parallel session **{session_id}**.

### BEFORE STARTING:
Report that you're starting:
```bash
goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': '{worker_id} starting work'" --no-session
```

### DURING WORK:
Report significant progress:
```bash
goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': '{worker_id} progress: [update]'" --no-session
```

### BEFORE WRITING FILES:
Check if another worker claimed it:
```bash
goose run -t "Use mcpdocker/read_entity 'Parallel_Session_{session_id}' to check claims" --no-session
```
If another worker already claimed the file, coordinate with them or work on something else.

### ON COMPLETE:
Report your results:
```bash
goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': '{worker_id} COMPLETE: [summary]'" --no-session
```

### ON FAILURE:
Report the failure:
```bash
goose run -t "Use mcpdocker/add_observation to entity 'Parallel_Session_{session_id}': '{worker_id} FAILED: [error]'" --no-session
```

### CHECK SIBLINGS:
See how other workers are doing:
```bash
goose run -t "Use mcpdocker/read_entity 'Parallel_Session_{session_id}'" --no-session
```

This helps you avoid duplicate work and coordinate on shared resources.
"""


# Convenience function for spawning coordinated workers
async def spawn_coordinated_parallel(tasks: List[str], 
                                      session_name: str = None) -> Dict[str, Any]:
    """
    Spawn parallel Meeseeks with coordination.
    
    Usage:
        results = await spawn_coordinated_parallel([
            "Analyze code quality",
            "Analyze architecture",
            "Analyze tests"
        ], session_name="code_review")
    """
    manager = CoordinatedParallelManager()
    return await manager.spawn_coordinated(tasks, session_name)


# CLI test
if __name__ == "__main__":
    import sys
    
    tasks = [
        "Analyze spawn_meeseeks.py code quality",
        "Analyze template architecture",
        "Analyze feedback_loop.py error handling"
    ]
    
    print("=== Coordinated Parallel Spawn Test ===\n")
    
    manager = CoordinatedParallelManager()
    
    # Run async
    result = asyncio.run(manager.spawn_coordinated(tasks, "test_session"))
    
    print(f"Session ID: {result['session_id']}")
    print(f"Workers: {result['n_workers']}")
    print(f"\nCoordinated Task Example:\n")
    print(result['spawns'][0]['task'])
