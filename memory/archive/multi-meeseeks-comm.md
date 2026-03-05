# Multi-Meeseeks Communication (Added 2026-03-03)

## Shared State System

File-based coordination between parallel Meeseeks.

- **Location:** `skills/meeseeks/helpers/communication.py`
- **Class:** `SharedState(workflow_id, my_id)`
- **Status:** PRODUCTION READY

### Key Methods

```python
shared = SharedState("workflow_123", "mee_1")
await shared.register("My task")
await shared.update_status(progress=50, findings=["found X"])
await shared.share_discovery("pattern", {"file": "x.py", "issue": "..."})
peers = await shared.check_peers()
discoveries = await shared.get_shared_discoveries()
await shared.complete(summary="Done")
await shared.fail(error="Something went wrong")
```

### Spawn Helper

```python
from spawn_with_comm import spawn_code_review, spawn_swarm, spawn_research

workers = spawn_code_review("path/to/code.py", "workflow-001")
workers = spawn_swarm(["Task 1", "Task 2"], "workflow-002")
workers = spawn_research("topic", ["source1", "source2"], "workflow-003")
```

## Test Results

- **Test 1:** test-comm-001 - 3 workers, 181 discoveries - SUCCESS
- **Test 2:** real-review-001 - 3 reviewers, 12 findings - SUCCESS
