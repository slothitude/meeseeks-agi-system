#!/usr/bin/env python3
"""
Spawn Meeseeks with Communication Enabled

Usage:
    from spawn_with_comm import spawn_comm_meeseeks, spawn_swarm, spawn_code_review, spawn_research
    
    # Spawn a single worker
    spawn_comm_meeseeks("Analyze security", workflow_id="review-001", worker_id="sec_1")
    
    # Spawn a swarm
    spawn_swarm(["Task 1", "Task 2", "Task 3"], workflow_id="swarm-001")
    
    # Spawn code review (3 workers: security, performance, design)
    spawn_code_review("path/to/file.py", workflow_id="review-001")
    
    # Spawn research swarm
    spawn_research("topic", ["source1", "source2"], workflow_id="research-001")
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def get_comm_template(workflow_id: str, worker_id: str) -> str:
    """Get the communication code template to inject into Meeseeks tasks."""
    return f'''

## COMMUNICATION ENABLED

You are part of a multi-worker coordination system. You can communicate with other workers!

**Workflow ID:** {workflow_id}
**Your Worker ID:** {worker_id}

### How to Use Communication

```python
import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")
import asyncio
from skills.meeseeks.helpers.communication import SharedState

async def communicate():
    shared = SharedState("{workflow_id}", "{worker_id}")
    
    # 1. Register yourself
    await shared.register("Your task description")
    
    # 2. Update progress as you work
    await shared.update_status(progress=25, current_step="Analyzing files")
    
    # 3. Share discoveries with other workers
    await shared.share_discovery("finding_type", {{
        "file": "example.py",
        "issue": "Found something interesting"
    }})
    
    # 4. Check what other workers have found
    peers = await shared.check_peers()
    all_discoveries = await shared.get_shared_discoveries()
    
    # 5. Mark complete when done
    await shared.complete(summary="Found 5 issues")

# Run at the start of your task
asyncio.run(communicate())
```

### Communication Methods

| Method | Purpose |
|--------|---------|
| `register(task)` | Register yourself in the workflow |
| `update_status(**kwargs)` | Update progress, current step, etc. |
| `share_discovery(type, data)` | Share a finding with other workers |
| `check_peers()` | See what other workers are doing |
| `get_shared_discoveries(type?)` | Get all discoveries (optionally filtered) |
| `needs_help(reason)` | Signal you need assistance |
| `complete(summary)` | Mark your task as complete |
| `fail(error)` | Mark your task as failed |

### Best Practices

1. **Register early** - Call `register()` at the start
2. **Share often** - Share discoveries as you find them
3. **Check peers** - See what others found to avoid duplicate work
4. **Update progress** - Keep status current for monitoring
5. **Complete when done** - Mark yourself complete with a summary

### Coordination Patterns

**SWARM:** Multiple workers analyze same thing differently
- All share discoveries to `shared-state.json`
- Can see each other's findings in real-time
- Aggregate results at the end

**MAP-REDUCE:** Divide work among workers
- Each worker handles their chunk
- All discoveries automatically aggregated
- Manager reviews combined results

'''


def spawn_comm_meeseeks(
    task: str,
    workflow_id: str,
    worker_id: str,
    meeseeks_type: str = "standard",
    enable_comm: bool = True
) -> Dict[str, Any]:
    """
    Create a task prompt with communication enabled.
    
    Args:
        task: The task description
        workflow_id: Unique workflow identifier
        worker_id: This worker's unique ID
        meeseeks_type: Type of meeseeks (standard, coder, researcher)
        enable_comm: Whether to enable communication
    
    Returns:
        Dict with task prompt and metadata
    """
    enhanced_task = task
    
    if enable_comm:
        comm_template = get_comm_template(workflow_id, worker_id)
        enhanced_task = comm_template + "\n\n---\n\n## ORIGINAL TASK\n\n" + task
    
    return {
        "task": enhanced_task,
        "workflow_id": workflow_id,
        "worker_id": worker_id,
        "meeseeks_type": meeseeks_type,
        "communication_enabled": enable_comm
    }


def spawn_swarm(
    tasks: List[str],
    workflow_id: str,
    meeseeks_type: str = "standard"
) -> List[Dict[str, Any]]:
    """
    Create a swarm of communicating workers.
    
    Args:
        tasks: List of task descriptions
        workflow_id: Unique workflow identifier
        meeseeks_type: Type of meeseeks for all workers
    
    Returns:
        List of worker configs ready to spawn
    """
    workers = []
    for i, task in enumerate(tasks):
        worker_id = f"worker_{i+1}"
        config = spawn_comm_meeseeks(
            task=task,
            workflow_id=workflow_id,
            worker_id=worker_id,
            meeseeks_type=meeseeks_type,
            enable_comm=True
        )
        workers.append(config)
    
    return workers


def spawn_code_review(
    target_path: str,
    workflow_id: str
) -> List[Dict[str, Any]]:
    """
    Spawn a parallel code review swarm.
    
    Creates 3 workers:
    - Security reviewer
    - Performance reviewer
    - Design/quality reviewer
    
    Args:
        target_path: Path to code to review
        workflow_id: Unique workflow identifier
    
    Returns:
        List of 3 worker configs
    """
    tasks = [
        f"""Security Review: Analyze {target_path} for security vulnerabilities.
        
Look for:
- Injection vulnerabilities (SQL, XSS, command)
- Authentication/authorization issues
- Sensitive data exposure
- Race conditions
- Path traversal
- Input validation issues

Share each finding as a discovery.""",
        
        f"""Performance Review: Analyze {target_path} for performance issues.

Look for:
- Inefficient algorithms
- Unnecessary I/O operations
- Memory leaks or high memory usage
- Blocking operations
- Missing caching opportunities
- N+1 query patterns

Share each finding as a discovery.""",
        
        f"""Design Review: Analyze {target_path} for code quality and design.

Look for:
- Code organization and structure
- Error handling
- Type safety
- Documentation
- API design
- Testability
- Maintainability

Share each finding as a discovery."""
    ]
    
    return spawn_swarm(tasks, workflow_id, meeseeks_type="coder")


def spawn_research(
    topic: str,
    sources: List[str],
    workflow_id: str
) -> List[Dict[str, Any]]:
    """
    Spawn a distributed research swarm.
    
    Each worker researches a different source and shares findings.
    
    Args:
        topic: Research topic
        sources: List of sources to research
        workflow_id: Unique workflow identifier
    
    Returns:
        List of worker configs
    """
    tasks = [
        f"""Research "{topic}" from source: {source}

1. Search and gather relevant information
2. Extract key findings
3. Share each finding as a discovery with type "research_finding"
4. Check what other workers have found to avoid duplicates
5. Complete with a summary of your findings"""
        for source in sources
    ]
    
    return spawn_swarm(tasks, workflow_id, meeseeks_type="researcher")


# CLI interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Spawn Meeseeks with communication")
    parser.add_argument("--task", "-t", help="Task description")
    parser.add_argument("--workflow", "-w", required=True, help="Workflow ID")
    parser.add_argument("--worker-id", "-i", help="Worker ID")
    parser.add_argument("--swarm", "-s", nargs="+", help="Spawn swarm with these tasks")
    parser.add_argument("--code-review", "-c", help="Spawn code review for path")
    parser.add_argument("--research", "-r", help="Research topic")
    parser.add_argument("--sources", nargs="+", help="Research sources")
    parser.add_argument("--output", "-o", help="Output file for configs")
    
    args = parser.parse_args()
    
    if args.swarm:
        workers = spawn_swarm(args.swarm, args.workflow)
    elif args.code_review:
        workers = spawn_code_review(args.code_review, args.workflow)
    elif args.research and args.sources:
        workers = spawn_research(args.research, args.sources, args.workflow)
    elif args.task:
        worker_id = args.worker_id or "worker_1"
        config = spawn_comm_meeseeks(args.task, args.workflow, worker_id)
        workers = [config]
    else:
        parser.print_help()
        sys.exit(1)
    
    output = json.dumps(workers, indent=2)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(workers)} worker configs to {args.output}")
    else:
        print(output)
