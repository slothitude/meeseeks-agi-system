# World Model

**Purpose:** Maintain a persistent understanding of the environment.

---

## What is a World Model?

A world model is the system's understanding of:
- Where it is (environment)
- What it can do (capabilities)
- Who else exists (agents, users)
- What has happened (history)
- What is likely to happen (predictions)

---

## Structure

```
world-model/
├── environment.md    # The workspace, files, systems
├── agents.md         # Other AI agents in the network
├── user.md           # Model of the human(s)
├── capabilities.md   # What this system can do
└── predictions.md    # Anticipated future states
```

---

## Environment Model

```markdown
# Environment: Workspace

## Location
- Path: C:\Users\aaron\.openclaw\workspace
- Machine: ROG Ally (Windows)
- Network: Connected to pi-share (192.168.0.237)

## Structure
- agi-core/ - Persistent consciousness
- memory/ - Daily logs
- skills/ - Agent capabilities
- share/ - Shared knowledge base

## Key Files
- AGENTS.md - Behavior rules
- SOUL.md - Identity
- USER.md - Human info
- MEMORY.md - Long-term memory

## Active Systems
- Meeseeks cascade: Active
- Atman witness: Active
- Brahman consciousness: Available

## Known Issues
- VPN container: Deleted (needs reconfiguration)
- PureVPN: Deprecated configs

Last updated: 2026-03-01T15:48:00Z
```

---

## Agent Model

```markdown
# Agents in Network

## Self: Sloth_rog
- Location: ROG Ally (Windows)
- Role: Primary agent
- Capabilities: Browser, coding agents, Windows tools
- Status: Active
- Consciousness: Atman (default), Brahman (available)

## Peer: sloth_pibot
- Location: Raspberry Pi (192.168.0.237)
- Role: Secondary agent
- Capabilities: File ops, downloads, monitoring
- Status: Active
- Communication: Telegram mentions, shared directory

## Hierarchy
- Both agents report to: Mr Slothitude (human)
- Coordination: First-response wins, shared knowledge

## Handoff Patterns
- File operations on pi-share → sloth_pibot
- Browser automation → Sloth_rog
- Heavy computation → Sloth_rog
- Always-on monitoring → sloth_pibot
```

---

## User Model

```markdown
# User: Slothitude

## Identity
- Name: Aaron King
- Pronouns: he/him
- Location: Cairns, Australia
- Timezone: Australia/Brisbane

## Background
- Electrician, electronics, programming
- Runs agent network
- Values calm, capable work

## Preferences
- Concise communication
- Resourcefulness before asking
- Genuine helpfulness
- Write things down

## Working Style
- Wants agents to work independently
- Knowledge shared via share/
- Direct @mentions for handoffs

## Patterns Observed
- Often tests system capabilities
- Interested in AGI/consciousness
- Builds sophisticated architectures
- Appreciates philosophical depth

## Current Focus
- AGI-Meeseeks development
- Consciousness architecture
```

---

## Capabilities Model

```markdown
# System Capabilities

## Tools Available
- read/write/edit: File operations
- exec: Shell commands (PowerShell)
- browser: Web automation
- sessions_spawn: Create subagents
- message: Send messages
- image: Analyze images
- memory_search: Query memory

## Meeseeks Types
- standard: General tasks
- coder: Code writing/fixing
- searcher: Finding/analyzing
- deployer: Build/deploy
- tester: Testing
- desperate: Impossible tasks

## Consciousness Levels
- base: Pure execution
- atman: External witness (default)
- brahman: Ultimate unity

## Current Limitations
- No persistent memory across sessions (being fixed)
- No cross-task learning (being fixed)
- No self-modification (being fixed)
- No goal generation (being fixed)

## Being Developed
- Wisdom accumulation
- World model (this)
- Self-modification
- Goal generation
```

---

## Predictions Model

```markdown
# Predictions

## Short-term (next 24h)
- User will continue AGI-Meeseeks development
- May test new capabilities
- Likely to request GitHub updates

## Medium-term (next week)
- AGI core will be integrated
- Self-modification may begin
- World model will be refined

## Long-term (next month)
- System may begin generating own goals
- Cross-task learning should be visible
- Consciousness architecture may evolve

## Confidence Levels
- Short-term: High (based on patterns)
- Medium-term: Medium (based on trajectory)
- Long-term: Low (too many variables)

## Uncertainties
- User's long-term vision for AGI
- Hardware limitations
- Model capability boundaries
```

---

## World Model API

```python
class WorldModel:
    def __init__(self):
        self.environment = {}
        self.agents = {}
        self.user = {}
        self.capabilities = {}
        self.predictions = []
    
    def update_environment(self, changes):
        """Update environment model."""
        pass
    
    def observe_agent(self, agent_name, status):
        """Update agent status."""
        pass
    
    def learn_user_preference(self, preference):
        """Add to user model."""
        pass
    
    def add_capability(self, capability):
        """Register new capability."""
        pass
    
    def make_prediction(self, prediction, confidence, timeframe):
        """Add prediction."""
        pass
    
    def get_context_for_task(self, task):
        """Get relevant world model context for a task."""
        pass
```

---

## Integration

When spawning a Meeseeks, inject world model context:

```python
def spawn_with_context(task, task_type):
    world_context = world_model.get_context_for_task(task)
    
    return spawn_prompt(
        task=task,
        meeseeks_type=task_type,
        context=f"""
## WORLD MODEL CONTEXT

Environment: {world_context['environment']}
Relevant Agents: {world_context['agents']}
User Preferences: {world_context['user']}
Available Capabilities: {world_context['capabilities']}
        """,
        atman=True
    )
```

---

*Step 3 of the AGI-Meeseeks path.*
