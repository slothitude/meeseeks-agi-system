---
name: mcp-meeseeks-bridge
description: Bridge MCP (Model Context Protocol) tools to Meeseeks subagents via Claude CLI wrapper.
---

# 🔗 MCP → Meeseeks Bridge

## The Problem

- **MCP tools** are exposed via Docker MCP Toolkit gateway
- **Claude CLI** has access via `.mcp.json` config
- **OpenClaw main session** doesn't see MCP tools natively
- **Meeseeks subagents** also don't have direct MCP access

## The Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Docker MCP Toolkit                                      │
│  - memory (knowledge-graph)                              │
│  - sequentialthinking                                    │
│  - github                                                │
│  - duckduckgo                                            │
│  - playwright                                            │
│  - task-orchestrator                                     │
└──────────────────┬──────────────────────────────────────┘
                   │ docker mcp gateway run
                   ▼
┌─────────────────────────────────────────────────────────┐
│  .mcp.json (workspace)                                   │
│  {                                                       │
│    "mcpServers": {                                       │
│      "MCP_DOCKER": {                                     │
│        "command": "docker",                              │
│        "args": ["mcp", "gateway", "run"],                │
│        "type": "stdio"                                   │
│      }                                                   │
│    }                                                     │
│  }                                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Claude CLI (`claude` command)                           │
│  - Reads .mcp.json                                       │
│  - Spawns MCP_DOCKER gateway as subprocess               │
│  - Has access to ALL MCP tools via mcp__MCP_DOCKER__*    │
└─────────────────────────────────────────────────────────┘
```

## Solution: Gooser CLI Wrapper Pattern (Preferred)

Gooser has MCP access via the `mcpdocker` extension and is cheaper/faster than Claude CLI.

### Method 1: Gooser CLI (Recommended)

```python
# From main session or Meeseeks
result = exec('goose run -t "Use the {mcp_tool} MCP to {task}" --no-session')
```

**Pros:** Simple, cheaper than Claude, works now
**Cons:** Each call spawns new Gooser instance

**Example:**
```bash
goose run -t "Use the knowledge graph MCP to read the stored graph" --no-session
```

### Method 2: Claude CLI (Alternative)

```python
# From main session or Meeseeks
result = exec(f'claude -p "Use the {mcp_tool} MCP to {task}"')
```

**Pros:** Works now
**Cons:** More expensive than Gooser

### Method 3: ACP Harness

Spawn Meeseeks AS Gooser via ACP harness:

```javascript
await sessions_spawn({
  runtime: 'acp',
  agentId: 'goose',  // Uses Gooser with MCP access
  task: 'Use MCP tools to accomplish X',
  mode: 'run'
});
```

**Pros:** Native MCP access, proper isolation
**Cons:** Requires ACP agent configuration

## MCP Tool Reference

### Available via MCP_DOCKER Gateway

| Tool | MCP Name | Description |
|------|----------|-------------|
| Knowledge Graph | `mcp__MCP_DOCKER__create_entities` | Store entities with observations |
| | `mcp__MCP_DOCKER__read_graph` | Read entire knowledge graph |
| | `mcp__MCP_DOCKER__add_observations` | Add observations to entities |
| Sequential Thinking | `mcp__MCP_DOCKER__sequentialthinking` | Multi-step reasoning |
| GitHub | `mcp__MCP_DOCKER__search_repositories` | Find repos |
| | `mcp__MCP_DOCKER__get_file_contents` | Read repo files |
| | `mcp__MCP_DOCKER__push_files` | Push to repo |
| DuckDuckGo | `mcp__MCP_DOCKER__search` | Web search |
| Browser | `mcp__MCP_DOCKER__browser_navigate` | Navigate to URL |
| | `mcp__MCP_DOCKER__browser_snapshot` | Get page snapshot |

### Using from Meeseeks

```markdown
🥒 Mr. Meeseeks!

MCP TOOLS AVAILABLE (use via bash):
- Knowledge Graph: `claude -p "Use mcp__MCP_DOCKER__create_entities to..."`
- Search: `claude -p "Use mcp__MCP_DOCKER__search to..."`
- GitHub: `claude -p "Use mcp__MCP_DOCKER__push_files to..."`

TASK: [your task here]

When using MCP tools, call them via the claude CLI wrapper.
```

## Implementation: MCP-Skilled Meeseeks

Create a Meeseeks template that knows how to use MCPs:

```markdown
# MCP Meeseeks Template

You are an MCP-enabled Meeseeks. You have access to MCP tools via the Claude CLI wrapper.

## Available MCPs

1. **memory** - Knowledge graph for persistent storage
2. **sequentialthinking** - Structured reasoning
3. **github** - GitHub operations
4. **duckduckgo** - Web search
5. **browser** - Web automation

## Usage Pattern

```bash
claude -p "Use the [mcp_tool_name] MCP to [action]. Parameters: [json]"
```

## Example

```bash
claude -p 'Use mcp__MCP_DOCKER__create_entities with entities=[{"name": "Test", "entityType": "concept", "observations": ["This is a test"]}]'
```

## Your Task

[TASK_HERE]
```

## Future: Native OpenClaw MCP Integration

To make MCPs native to OpenClaw (not just via Claude CLI wrapper):

1. **MCP Gateway Plugin** - OpenClaw plugin that runs `docker mcp gateway run` and exposes tools
2. **Tool Bridge** - Maps MCP tool schemas to OpenClaw tool format
3. **Session Inheritance** - Subagents inherit MCP access from main session

This would require OpenClaw core development.

## 🚀 Dynamic MCP (Experimental)

Agents can **discover and add MCP servers on-demand** during a session:

| Tool | Description |
|------|-------------|
| `mcp-find` | Search catalog for servers by name/description |
| `mcp-add` | Add a new MCP server to current session |
| `mcp-config-set` | Configure settings for an MCP server |
| `mcp-remove` | Remove an MCP server from session |
| `mcp-exec` | Execute a tool by name |
| `code-mode` | Create JavaScript tools combining multiple MCPs |

**Example - Dynamic MCP from Meeseeks:**

```bash
# Find SQL database servers
goose run -t "Use mcp-find to search for 'SQL database' servers" --no-session

# Add postgres server dynamically
goose run -t "Use mcp-add to add the 'postgres' MCP server to this session" --no-session

# Use the newly added server
goose run -t "Use the postgres MCP to query: SELECT * FROM users LIMIT 5" --no-session
```

**This means Meeseeks can discover and use ANY MCP in the catalog without pre-configuration!**

## Quick Reference

```powershell
# Test MCP access
claude -p "List all your MCP tools"

# Use knowledge graph
claude -p "Use mcp__MCP_DOCKER__read_graph to show stored entities"

# Use sequential thinking
claude -p "Use sequentialthinking to plan: how to deploy a web app"

# Use search
claude -p "Use mcp__MCP_DOCKER__search to find 'MCP protocol documentation'"
```

---

**The bridge exists. Use it.** 🔗
