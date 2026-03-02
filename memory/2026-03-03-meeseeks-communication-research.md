# Meeseeks-to-Meeseeks Communication Research

**Date:** 2026-03-03
**Context:** Researching multi-agent communication patterns for OpenClaw's Meeseeks system
**Goal:** Enable parallel Meeseeks coordination and inter-subagent communication

---

## Executive Summary

**Current State:** OpenClaw subagents (Meeseeks) are **isolated workers** with no built-in inter-subagent communication. All coordination happens through the parent agent (Sloth_rog).

**Key Finding:** Multi-agent frameworks use three primary communication patterns:
1. **Message Passing** (AutoGen, LangGraph)
2. **Shared State/Memory** (CrewAI, LangGraph)
3. **Hierarchical Coordination** (CrewAI, AutoGen AgentTool)

**Recommendation:** Implement **hybrid architecture** combining:
- Parent-as-coordinator (current model, enhanced)
- Shared file-based state (simple, works now)
- Future: Direct message passing via message bus

---

## Part 1: Current Capabilities in OpenClaw

### Subagent Architecture

OpenClaw's subagent system creates **isolated execution contexts**:

```typescript
type SubagentRunRecord = {
    runId: string;
    childSessionKey: string;        // Isolated session
    requesterSessionKey: string;    // Parent session
    task: string;
    cleanup: "delete" | "keep";
    // ... no inter-subagent fields
}
```

**Key Characteristics:**
- ✅ Each Meeseeks gets its own session
- ✅ Parent can monitor all children
- ✅ Results flow back to parent
- ❌ No direct subagent-to-subagent messaging
- ❌ No shared state between subagents
- ❌ No coordination primitives (locks, semaphores)

### Current Communication Pattern

```
┌──────────────────┐
│  Sloth_rog       │  ← MANAGER
│  (Main Session)  │
└────────┬─────────┘
         │ spawns
    ┌────┴─────┬─────────┐
    ▼          ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│Mee #1  │ │Mee #2  │ │Mee #3  │  ← ISOLATED
│(task1) │ │(task2) │ │(task3) │
└────┬───┘ └────┬───┘ └────┬───┘
     │          │         │
     └──────────┴─────────┘
                │
         Results → Manager
```

**All communication flows through the parent.** Subagents cannot:
- Send messages to each other
- Share files directly (must go through workspace)
- Coordinate timing
- Access each other's state

### Parallel Meeseeks Patterns (Already Documented)

From `parallel-meeseeks.md`, we have patterns for:
- **SWARM**: Multiple approaches, aggregate results
- **MAP-REDUCE**: Divide work, process in parallel, merge
- **PIPELINE**: Staged execution
- **VOTING**: Consensus building

**Limitation:** These patterns require the **parent to aggregate results**. No coordination happens at the subagent level.

---

## Part 2: Multi-Agent Framework Comparison

### AutoGen (Microsoft)

**Communication Model:** Message Passing + Event-Driven

```python
# AgentTool for orchestration
math_agent_tool = AgentTool(math_agent, return_value_as_last_message=True)
chemistry_agent_tool = AgentTool(chemistry_agent)

# Agents as tools - can call each other
assistant = AssistantAgent(
    tools=[math_agent_tool, chemistry_agent_tool]
)
```

**Key Features:**
- **AgentTool**: Wrap agents as callable tools
- **Message passing**: Structured messages between agents
- **Event-driven**: Agents respond to events
- **GroupChat**: Multiple agents in shared conversation

**Communication Patterns:**
1. **Direct messaging**: `agent.send(message, recipient)`
2. **Group chat**: Shared conversation space
3. **Agent as tool**: Call agent like a function
4. **Event hooks**: React to agent lifecycle events

**Pros:**
- Flexible messaging
- Clear separation of concerns
- Works well for conversational agents

**Cons:**
- Requires explicit message routing
- Complex state management
- Learning curve for patterns

---

### CrewAI

**Communication Model:** Shared Memory + Hierarchical Coordination

```python
# Hierarchical process with manager
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.hierarchical,  # Manager coordinates
    manager_llm=GPT_4,
    memory=True  # Shared memory
)
```

**Key Features:**
- **Memory system**: Short-term, long-term, entity memory
- **Hierarchical process**: Manager agent coordinates
- **Sequential process**: Linear task execution
- **Task delegation**: Agents can delegate to each other

**Communication Patterns:**
1. **Task context**: Output of one task feeds into next
2. **Shared memory**: All agents access crew memory
3. **Manager coordination**: Hierarchical delegation
4. **Tool sharing**: Agents can use same tools

**Pros:**
- Built-in memory system
- Clear process models (sequential/hierarchical)
- Easy to define workflows

**Cons:**
- Less flexible than message passing
- Memory can become stale
- Hierarchical only with manager LLM

---

### LangGraph

**Communication Model:** State Graph + Durable Execution

```python
from langgraph.graph import StateGraph

class State(TypedDict):
    messages: List[Message]
    next_agent: str

# Define state transitions
graph = StateGraph(State)
graph.add_node("agent_a", agent_a)
graph.add_node("agent_b", agent_b)
graph.add_edge("agent_a", "agent_b")
```

**Key Features:**
- **State management**: Explicit state schema
- **Graph-based workflow**: Define agent transitions
- **Durable execution**: Persists through failures
- **Human-in-the-loop**: Interrupt and modify state

**Communication Patterns:**
1. **Shared state**: All nodes access/update state
2. **Conditional edges**: Route based on state
3. **Checkpoints**: Save/restore state
4. **Subgraphs**: Nested workflows

**Pros:**
- Explicit state management
- Visualizable workflows
- Built-in persistence
- Supports complex branching

**Cons:**
- More boilerplate
- Tight coupling to LangChain ecosystem
- Steeper learning curve

---

## Part 3: Communication Channel Options

### Option 1: Shared Files (Works Now)

**Implementation:** Use workspace files as message buffers

```python
# meeseeks-communication/shared-state.json
{
  "workers": {
    "mee_1": {
      "status": "running",
      "progress": 45,
      "findings": ["found X", "found Y"]
    },
    "mee_2": {
      "status": "complete",
      "result": "solution found"
    }
  },
  "shared_insights": [
    "Pattern A detected in multiple files"
  ]
}
```

**Pattern:**
```python
# In Meeseeks:
async def update_status(findings):
    state = await read_json("shared-state.json")
    state["workers"][my_id]["findings"].extend(findings)
    await write_json("shared-state.json", state)

async def check_peers():
    state = await read_json("shared-state.json")
    return state["workers"]
```

**Pros:**
- ✅ Works with current OpenClaw
- ✅ Simple to implement
- ✅ No infrastructure changes
- ✅ Human-readable

**Cons:**
- ⚠️ Race conditions (need file locking)
- ⚠️ Polling-based (not event-driven)
- ⚠️ Doesn't scale to many workers
- ⚠️ Manual cleanup required

---

### Option 2: Message Bus (Requires Infrastructure)

**Implementation:** Redis Pub/Sub or similar

```python
# Pseudo-code
bus = MessageBus("redis://localhost")

# Meeseeks #1
await bus.publish("meeseeks.progress", {
    "from": "mee_1",
    "status": "found pattern X"
})

# Meeseeks #2
async for msg in bus.subscribe("meeseeks.progress"):
    if msg["from"] != my_id:
        handle_peer_update(msg)
```

**Pros:**
- ✅ Real-time communication
- ✅ Scales to many workers
- ✅ Event-driven
- ✅ Decoupled architecture

**Cons:**
- ❌ Requires Redis/infrastructure
- ❌ More complex setup
- ❌ Not in current OpenClaw stack
- ❌ Debugging harder

---

### Option 3: Parent-as-Broker (Enhanced Current Model)

**Implementation:** Parent coordinates all communication

```python
# In Sloth_rog (manager)
class MeeseeksCoordinator:

    async def spawn_parallel(self, tasks):
        self.workers = {}

        # Spawn all
        for task in tasks:
            run_id = await sessions_spawn(task)
            self.workers[run_id] = {
                "task": task,
                "status": "running",
                "messages": []
            }

        # Monitor and relay
        while self.workers_running():
            for run_id, worker in self.workers.items():
                # Check for messages from worker
                msg = await check_worker_message(run_id)
                if msg:
                    # Relay to other workers
                    await self.broadcast(run_id, msg)

                # Check for completion
                if await is_complete(run_id):
                    await self.handle_completion(run_id)
```

**Pros:**
- ✅ Works with current architecture
- ✅ Centralized control
- ✅ Easy to debug
- ✅ No race conditions

**Cons:**
- ⚠️ Parent becomes bottleneck
- ⚠️ Latency (all messages through parent)
- ⚠️ Doesn't scale to many workers

---

### Option 4: Knowledge Graph as Blackboard (MCP-Enabled)

**Implementation:** Use MCP Knowledge Graph as shared state

```python
# In MCP-enabled Meeseeks
await kg.create_entity("Meeseeks_1_Status", {
    "progress": 50,
    "findings": ["found X"],
    "relations": [
        ("collaborating_with", "Meeseeks_2")
    ]
})

# Query peer status
peers = await kg.search_entities("Meeseeks_*_Status")
```

**Pros:**
- ✅ Structured data model
- ✅ Query capabilities
- ✅ Relations between entities
- ✅ Already available (MCP)

**Cons:**
- ⚠️ Requires MCP-enabled Meeseeks
- ⚠️ Learning curve
- ⚠️ Not all Meeseeks need MCP
- ⚠️ Overhead for simple coordination

---

## Part 4: Proposed Architecture

### Recommended: Hybrid Approach

Combine multiple patterns based on use case:

```
┌─────────────────────────────────────────┐
│          SLOTH_ROG (MANAGER)             │
│  ┌────────────────────────────────────┐ │
│  │   Coordinator + Message Broker     │ │
│  └────────────────────────────────────┘ │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴──────────┐
    │  SHARED STATE      │  ← File-based (Phase 1)
    │  (shared.json)     │     KG-based (Phase 2)
    └─────────┬──────────┘
              │
    ┌─────────┴──────────┬──────────────┐
    ▼                    ▼              ▼
┌────────┐          ┌────────┐    ┌────────┐
│Mee #1  │          │Mee #2  │    │Mee #3  │
│        │←────────→│        │←───→│        │
└────────┘          └────────┘    └────────┘
    │                    │              │
    └────────────────────┴──────────────┘
                   │
          Read/Write Shared State
```

### Phase 1: File-Based Shared State (Immediate)

**Implementation:**

1. **Create shared state schema:**

```python
# meeseeks-communication/shared-state.json
{
  "meta": {
    "created_at": "2026-03-03T12:00:00Z",
    "coordinator": "sloth_rog",
    "workflow_id": "wf_12345"
  },
  "workers": {
    "mee_1": {
      "session_id": "agent:main:subagent:abc",
      "task": "Analyze authentication",
      "status": "running",
      "progress": 45,
      "started_at": "2026-03-03T12:00:00Z",
      "last_update": "2026-03-03T12:05:00Z",
      "findings": [],
      "needs_help": false
    }
  },
  "shared": {
    "discoveries": [
      {
        "from": "mee_1",
        "type": "pattern",
        "data": "Auth bypass in /api/v1/login",
        "timestamp": "2026-03-03T12:03:00Z"
      }
    ],
    "decisions": [
      {
        "by": "consensus",
        "type": "approach",
        "value": "Use OAuth2 instead",
        "voters": ["mee_1", "mee_2"]
      }
    ]
  }
}
```

2. **Create communication helpers:**

```python
# skills/meeseeks/helpers/communication.py

import json
from pathlib import Path
from datetime import datetime
import asyncio

class SharedState:
    def __init__(self, workflow_id, my_id):
        self.path = Path(f"meeseeks-communication/{workflow_id}/shared-state.json")
        self.my_id = my_id
        self.lock = asyncio.Lock()

    async def read(self):
        """Read current shared state."""
        async with self.lock:
            if not self.path.exists():
                return self._initial_state()
            return json.loads(self.path.read_text())

    async def write(self, state):
        """Write shared state atomically."""
        async with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix('.tmp')
            temp.write_text(json.dumps(state, indent=2))
            temp.rename(self.path)

    async def update_status(self, **kwargs):
        """Update my status in shared state."""
        state = await self.read()
        state["workers"][self.my_id].update(kwargs)
        state["workers"][self.my_id]["last_update"] = datetime.utcnow().isoformat()
        await self.write(state)

    async def share_discovery(self, discovery_type, data):
        """Share a finding with other workers."""
        state = await self.read()
        state["shared"]["discoveries"].append({
            "from": self.my_id,
            "type": discovery_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.write(state)

    async def check_peers(self):
        """Check status of other workers."""
        state = await self.read()
        return {
            wid: winfo
            for wid, winfo in state["workers"].items()
            if wid != self.my_id
        }

    async def get_shared_discoveries(self):
        """Get all shared discoveries."""
        state = await self.read()
        return state["shared"]["discoveries"]

    async def propose_decision(self, decision_type, value):
        """Propose a decision for voting."""
        state = await self.read()
        # Implementation for voting mechanism
        pass

    def _initial_state(self):
        return {
            "meta": {
                "created_at": datetime.utcnow().isoformat(),
                "workflow_id": self.workflow_id
            },
            "workers": {},
            "shared": {
                "discoveries": [],
                "decisions": []
            }
        }
```

3. **Enhanced Meeseeks spawn with communication:**

```python
# In spawn_meeseeks.py

def spawn_prompt(task, meeseeks_type, workflow_id=None, enable_comm=False):
    base = load_template(meeseeks_type)

    if enable_comm and workflow_id:
        comm_code = f"""
# COMMUNICATION: You can coordinate with other Meeseeks!
from skills.meeseeks.helpers.communication import SharedState

shared = SharedState("{workflow_id}", "{my_id}")

# Update your status
await shared.update_status(progress=50, findings=["found X"])

# Share discoveries
await shared.share_discovery("pattern", "Found SQL injection in /api/users")

# Check what peers are doing
peers = await shared.check_peers()
for peer_id, info in peers.items():
    print(f"Peer {{peer_id}}: {{info['status']}} - {{info['task']}}")

# Get shared discoveries
discoveries = await shared.get_shared_discoveries()
"""
        task = task + "\n\n" + comm_code

    return {"task": task}
```

---

### Phase 2: Knowledge Graph Integration (Future)

**For MCP-enabled Meeseeks:**

```python
# Create worker entity in KG
await kg_create_entity(
    f"Meeseeks_{workflow_id}_{my_id}",
    {
        "type": "worker",
        "task": task_description,
        "status": "running",
        "progress": 0
    }
)

# Create relations
await kg_create_relation(
    f"Meeseeks_{workflow_id}_{my_id}",
    "part_of",
    f"Workflow_{workflow_id}"
)

# Query peers
peers = await kg_search(
    f"Meeseeks_{workflow_id}_*",
    filters={"status": "running"}
)

# Share findings as entities
await kg_create_entity(
    f"Discovery_{workflow_id}_{timestamp}",
    {
        "type": "finding",
        "from_worker": my_id,
        "data": finding_data
    }
)
```

**Benefits:**
- Structured queries
- Relation tracking
- Persistent history
- Cross-workflow learning

---

### Phase 3: Message Bus (Future, If Needed)

**When to implement:**
- 10+ parallel Meeseeks regularly
- Real-time coordination critical
- Latency unacceptable with file-based

**Implementation:**
```python
# Redis Pub/Sub
import redis

r = redis.Redis()

# Publisher (Meeseeks)
r.publish('meeseeks:workflow_123', json.dumps({
    'from': 'mee_1',
    'type': 'progress',
    'data': {'percent': 50}
}))

# Subscriber (other Meeseeks)
pubsub = r.pubsub()
pubsub.subscribe('meeseeks:workflow_123')

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        if data['from'] != my_id:
            handle_peer_message(data)
```

---

## Part 5: Use Cases and Patterns

### Pattern 1: Collaborative Code Analysis

**Scenario:** 3 Meeseeks analyze different aspects of a codebase

```python
# Sloth_rog spawns:
mee_1 = spawn("Find security vulnerabilities")
mee_2 = spawn("Find performance bottlenecks")
mee_3 = spawn("Find code quality issues")

# Meeseeks share discoveries:
# mee_1 finds: "SQL injection in /api/users"
# mee_2 notices: "/api/users is slow due to N+1 queries"
# mee_3 observes: "/api/users has complex nested logic"

# Shared state reveals connection:
# All three found issues in SAME endpoint → Priority fix!
```

**Implementation:**
```python
# In each Meeseeks:
async def analyze_code():
    findings = await my_analysis()

    for finding in findings:
        await shared.share_discovery("code_issue", {
            "location": finding.location,
            "type": finding.type,
            "severity": finding.severity
        })

    # Check if others found related issues
    all_discoveries = await shared.get_shared_discoveries()
    related = find_related(findings, all_discoveries)

    if related:
        await shared.update_status(
            progress=100,
            findings=findings,
            note=f"Found {len(related)} related issues from peers"
        )
```

---

### Pattern 2: Distributed Research

**Scenario:** 5 Meeseeks research different aspects of a topic

```python
# SWARM pattern with communication
tasks = [
    "Research ML approaches",
    "Research rule-based approaches",
    "Research hybrid approaches",
    "Research existing tools",
    "Research academic papers"
]

# All spawned in parallel, each updates shared state

# Discovery: mee_1 and mee_3 both find "transformer models"
# → Manager identifies convergence point
```

---

### Pattern 3: Voting on Solutions

**Scenario:** Multiple solutions proposed, need consensus

```python
# In Meeseeks:
async def propose_solution():
    solution = await my_approach()

    await shared.propose_decision("solution", {
        "approach": solution,
        "confidence": 0.85,
        "pros": [...],
        "cons": [...]
    })

    # Check other proposals
    proposals = await shared.get_proposals()

    # Vote
    votes = {}
    for prop in proposals:
        votes[prop.id] = evaluate(prop)

    await shared.vote(votes)
```

---

## Part 6: Current Limitations

### OpenClaw Subagent System

1. **No native inter-subagent messaging**
   - All communication must go through parent
   - No broadcast/subscribe mechanism

2. **No shared memory**
   - Each subagent has isolated context
   - No persistent state between runs

3. **No coordination primitives**
   - No locks, semaphores, barriers
   - No built-in synchronization

4. **Limited observability**
   - Parent can see results
   - Cannot see intermediate state
   - No real-time progress tracking

5. **No subagent discovery**
   - Subagents don't know about peers
   - Cannot address messages to specific subagent

### What We Can Do Now

✅ **File-based shared state** (recommended Phase 1)
✅ **Parent-as-broker** (current model, enhanced)
✅ **Knowledge Graph** (if MCP-enabled)
✅ **Polling for updates** (simple, works)

### What Requires Infrastructure

❌ **Real-time message passing** (needs Redis/similar)
❌ **Distributed locks** (needs coordination service)
❌ **Event streaming** (needs message bus)
❌ **Service discovery** (needs registry)

---

## Part 7: Implementation Roadmap

### Immediate (Phase 1): File-Based Communication

**Time:** 1-2 days
**Effort:** Low
**Impact:** High

**Steps:**
1. Create `SharedState` helper class
2. Add communication template to Meeseeks
3. Update `spawn_meeseeks.py` to inject comm code
4. Create workflow directory structure
5. Test with 2-3 parallel Meeseeks

**Deliverables:**
- `skills/meeseeks/helpers/communication.py`
- Updated spawn templates
- Example workflow

---

### Short-Term (Phase 2): Enhanced Coordinator

**Time:** 3-5 days
**Effort:** Medium
**Impact:** High

**Steps:**
1. Create `MeeseeksCoordinator` in Sloth_rog
2. Implement status monitoring
3. Add message relay capability
4. Create aggregation logic
5. Build monitoring dashboard (optional)

**Deliverables:**
- Coordinator class in main agent
- Real-time status tracking
- Intelligent result aggregation

---

### Medium-Term (Phase 3): Knowledge Graph Integration

**Time:** 1-2 weeks
**Effort:** Medium
**Impact:** Medium

**Steps:**
1. Define KG schema for Meeseeks workflows
2. Create KG helper functions
3. Update MCP-enabled Meeseeks template
4. Build query interface
5. Test cross-workflow learning

**Deliverables:**
- KG schema
- Helper functions
- Updated templates
- Documentation

---

### Long-Term (Phase 4): Message Bus (Optional)

**Time:** 2-4 weeks
**Effort:** High
**Impact:** High (for scale)

**Steps:**
1. Evaluate message bus options (Redis, NATS, etc.)
2. Design message protocol
3. Implement publisher/subscriber
4. Add to OpenClaw core or plugin
5. Update Meeseeks to use bus
6. Load testing and optimization

**Deliverables:**
- Message bus infrastructure
- Protocol documentation
- Updated Meeseeks system
- Performance benchmarks

**Trigger:** When regularly running 10+ parallel Meeseeks

---

## Part 8: Recommendations

### Start With (Immediate)

1. **Implement file-based shared state**
   - Low risk, high value
   - Works with current architecture
   - Easy to test and debug

2. **Enhance parallel patterns**
   - Add coordination to SWARM, MAP-REDUCE
   - Enable peer discovery
   - Support shared discoveries

3. **Create workflow templates**
   - Pre-configured communication patterns
   - Reusable across projects
   - Document best practices

### Build Toward (Next 3 months)

1. **Knowledge Graph integration**
   - For MCP-enabled Meeseeks
   - Cross-workflow learning
   - Structured state management

2. **Smart coordinator**
   - Better result aggregation
   - Conflict resolution
   - Priority-based scheduling

3. **Monitoring and observability**
   - Real-time progress tracking
   - Performance metrics
   - Debugging tools

### Consider for Future (6+ months)

1. **Message bus infrastructure**
   - If scale demands it
   - For real-time coordination
   - When file-based becomes bottleneck

2. **Distributed locking**
   - For resource contention
   - Critical sections
   - Transactional operations

3. **Service mesh**
   - Service discovery
   - Load balancing
   - Circuit breakers

---

## Part 9: Code Examples

### Example: Coordinated Code Review

```python
# In Sloth_rog (manager)

async def coordinated_code_review(files):
    workflow_id = generate_workflow_id()

    # Initialize shared state
    state = SharedState(workflow_id, "coordinator")
    await state.write(state._initial_state())

    # Spawn parallel reviewers
    tasks = [
        spawn_meeseeks(
            task=f"🥒 Review {f} for security issues",
            meeseeks_type="coder",
            workflow_id=workflow_id,
            enable_comm=True
        )
        for f in files
    ]

    # Wait for completion
    results = await Promise.all(tasks)

    # Aggregate findings
    final_state = await state.read()
    all_findings = final_state["shared"]["discoveries"]

    # Identify cross-file patterns
    patterns = identify_patterns(all_findings)

    return {
        "individual_results": results,
        "shared_discoveries": all_findings,
        "cross_file_patterns": patterns
    }
```

### Example: Meeseeks with Communication

```python
# In Meeseeks (injected code)

from skills.meeseeks.helpers.communication import SharedState

async def review_file(file_path):
    workflow_id = get_workflow_id()  # From spawn context
    my_id = get_my_id()

    shared = SharedState(workflow_id, my_id)

    # Register myself
    await shared.update_status(
        task=f"Reviewing {file_path}",
        status="running",
        progress=0
    )

    # Do analysis
    issues = await analyze_security(file_path)

    # Update progress
    await shared.update_status(progress=50)

    # Share discoveries
    for issue in issues:
        await shared.share_discovery("security_issue", {
            "file": file_path,
            "line": issue.line,
            "type": issue.type,
            "severity": issue.severity
        })

    # Check what peers found
    peer_discoveries = await shared.get_shared_discoveries()
    related = [
        d for d in peer_discoveries
        if d["data"]["file"] == file_path
    ]

    if related:
        # Found same issues as peers → high confidence
        await shared.update_status(
            progress=100,
            status="complete",
            confidence="high",
            note=f"Corroborated by {len(related)} peers"
        )

    return issues
```

---

## Conclusion

**Current state:** OpenClaw subagents are isolated, requiring all coordination through the parent agent.

**Immediate solution:** File-based shared state provides simple, effective coordination for parallel Meeseeks.

**Future direction:** Knowledge Graph integration and potentially a message bus for scale.

**Key insight:** We don't need complex infrastructure to enable coordination. File-based shared state + smart patterns = 80% of the value with 20% of the effort.

**Next step:** Implement Phase 1 (file-based shared state) and test with existing parallel Meeseeks patterns.

---

## References

- **AutoGen**: https://github.com/microsoft/autogen
- **CrewAI**: https://github.com/crewAIInc/crewAI
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **Parallel Meeseeks**: `skills/meeseeks/templates/parallel-meeseeks.md`
- **OpenClaw Subagent Types**: `openclaw/dist/plugin-sdk/agents/subagent-registry.types.d.ts`

---

**Document Status:** ✅ Complete
**Next Review:** After Phase 1 implementation
**Owner:** Sloth_rog (Main Agent)
