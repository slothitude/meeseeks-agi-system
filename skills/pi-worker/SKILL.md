---
name: pi-worker
description: Control pi-coding-agent as a programmable worker/subagent. Use for coding tasks, file operations, shell commands, and complex multi-step workflows. Can be used interactively or via RPC/SDK for automation.
---

# Pi Worker - Subagent Control

## Overview

This skill allows me (Sloth_rog) to use pi-coding-agent as a programmable worker. Pi is a minimal terminal coding harness with powerful tools (read, write, edit, bash) that can be extended via TypeScript extensions.

## Capabilities

### Built-in Tools
- **read** - Read file contents (supports offset/limit, auto-truncation)
- **write** - Create or overwrite files
- **edit** - Make precise edits to files
- **bash** - Execute shell commands
- **grep** - Search file contents
- **find** - Find files
- **ls** - List directories

### Modes of Operation

1. **Interactive Mode** - Terminal UI with full keyboard shortcuts
2. **Print Mode** (`-p`) - Print response and exit
3. **JSON Mode** (`--mode json`) - Output events as JSON lines
4. **RPC Mode** (`--mode rpc`) - Full programmatic control over stdin/stdout
5. **SDK Mode** - Embed in Node.js applications

## Using as a Worker

### Method 1: CLI One-shot (Recommended)

```bash
pi -p "Read package.json and summarize the dependencies"
```

### Method 2: With OpenClaw exec

```javascript
// Using OpenClaw's exec tool
const result = await exec('pi -p "Analyze this codebase"');
```

### Method 3: JSON Mode (Parseable Output)

```bash
pi --mode json "List all TypeScript files"
# Output: JSONL with events like {"type":"tool_call", ...}, {"type":"message_update", ...}
```

### Method 4: Specific tools only

```bash
pi --tools read,ls,grep "Find all TypeScript files with TODO comments"
```

## RPC Protocol

Start RPC mode:
```bash
pi --mode rpc
```

### Commands

**prompt** - Send a user message
```json
{"command": "prompt", "params": {"text": "List all files"}}
```

**abort** - Cancel current operation
```json
{"command": "abort"}
```

**get_commands** - List available commands
```json
{"command": "get_commands"}
```

**get_tools** - List available tools
```json
{"command": "get_tools"}
```

**set_tools** - Enable specific tools
```json
{"command": "set_tools", "params": {"tools": ["read", "bash"]}}
```

**set_model** - Change model
```json
{"command": "set_model", "params": {"model": "zai/glm-5"}}
```

### Events (JSON Lines Output)

**assistant message streaming**
```json
{"type": "assistant_message", "delta": {"content": "Hello"}}
```

**tool calls**
```json
{"type": "tool_call", "toolName": "read", "input": {"path": "package.json"}}
```

**tool results**
```json
{"type": "tool_result", "content": [...], "details": {...}}
```

**done**
```json
{"type": "done"}
```

## Example: Spawn Pi Worker

```bash
# Start pi in RPC mode
PI_PROC=$(pi --mode rpc)

# Send a task
echo '{"command": "prompt", "params": {"text": "Read README.md and summarize it"}}' | $PI_PROC

# Read JSON responses...
```

## Configuration

### Global Settings (~/.pi/agent/settings.json)

```json
{
  "provider": "zai",
  "model": "glm-5",
  "thinking": "low",
  "tools": ["read", "bash", "edit", "write"],
  "theme": "dark"
}
```

### Project Settings (.pi/settings.json)

```json
{
  "thinking": "medium",
  "tools": ["read", "grep", "find", "ls"]
}
```

## Extensions

Add custom capabilities via TypeScript extensions:

```typescript
// ~/.pi/agent/extensions/my-worker-tool.ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "deploy",
    label: "Deploy",
    description: "Deploy the current project",
    parameters: Type.Object({
      env: Type.String({ description: "Target environment" })
    }),
    async execute(toolCallId, params, signal, onUpdate, ctx) {
      // Custom deployment logic
      return {
        content: [{ type: "text", text: `Deployed to ${params.env}` }]
      };
    }
  });
}
```

## Best Practices

### For Coding Tasks
- Use `read` to understand codebase
- Use `edit` for precise changes
- Use `bash` for build/test commands
- Use `write` for new files

### For File Operations
- Use `find` + `grep` to locate files
- Use `read` to inspect contents
- Use `write` or `edit` to modify

### For Shell Commands
- Use `bash` tool
- Set timeout for long-running commands
- Check `signal.aborted` for cancellation

### For Complex Workflows
- Break into steps
- Use session branching (`/tree`, `/fork`)
- Save progress with `/name` command

## Integration with OpenClaw

I can spawn pi as a worker via:

1. **exec tool** - Run pi CLI commands
2. **sessions_spawn** - Create isolated pi sessions
3. **Custom extension** - Build a pi extension that exposes an RPC server

### Example: Spawn via OpenClaw

```javascript
// Using OpenClaw's exec tool
const result = await exec('pi -p "Analyze this codebase"');
```

```javascript
// Using sessions_spawn for isolation
const session = await sessions_spawn({
  task: 'pi --mode json "Review the code"',
  runtime: 'subagent',
  mode: 'run'
});
```

## Troubleshooting

### Pi not responding
- Check API key is set: `echo $ZAI_API_KEY`
- Try `/login` in interactive mode
- Check model is available: `pi --list-models zai`

### Tool not working
- Check tool is enabled: `pi --tools read,bash,edit,write`
- Check extension is loaded: `pi -e ./my-extension.ts`

### RPC not working
- Ensure using `--mode rpc`
- Check JSON format is valid
- Verify stdin/stdout are properly connected

## Resources

- **Docs:** https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/docs
- **Examples:** https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples
- **Discord:** https://discord.com/invite/3cU7Bz4UPx
- **npm:** https://www.npmjs.com/package/@mariozechner/pi-coding-agent
