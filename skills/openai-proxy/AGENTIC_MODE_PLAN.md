# OpenAI Proxy - Agentic Mode / Function Calling Implementation

## Understanding OpenWebUI's Native Mode

Based on [OpenWebUI Tools Documentation](https://docs.openwebui.com/features/extensibility/plugin/tools/), OpenWebUI supports two tool calling modes:

### Mode 1: Default Mode (Prompt-based)
- Works with any model
- Tool selection via prompt templates
- Compatible with older/smaller models
- Slower, less reliable for complex workflows

### Mode 2: Native Mode (Agentic Mode) ⭐
- Leverages model's built-in function calling
- Requires high-quality models (GPT-5, Claude 4.5+, Gemini 3+)
- Structured tool calls (JSON format)
- Multi-step reasoning (Thought → Action → Thought → ...)
- Lower latency, higher reliability
- **Recommended for production agentic workflows**

## Implementation Plan

### Phase 1: Tools Endpoint (`/v1/tools`)

Expose OpenClaw and Goose tools as OpenAI-compatible tool definitions:

```json
{
  "id": "browser",
  "type": "function",
  "function": {
    "name": "browser",
    "description": "Browse websites and extract content",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "URL to browse"
        },
        "action": {
          "type": "string",
          "enum": ["screenshot", "extract_text", "search"],
          "description": "Action to perform"
        }
      },
      "required": ["url"]
    }
  }
}
```

### Phase 2: Tool Calling in Chat Completions

Support the `tools` parameter in requests/responses:

**Request:**
```json
{
  "model": "openclaw",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "browser",
        "arguments": {"url": "https://example.com", "action": "extract_text"}
      }
    }
  ]
}
```

**Response:**
```json
{
  "id": "...",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Here's what I found...",
        "tool_calls": [
          {
            "id": "call_123",
            "type": "function",
            "function": {
              "name": "browser",
              "arguments": "{\"url\": \"https://example.com\", \"action\": \"extract_text\"}"
            }
          }
        ],
        "tool_use": "browser" // OpenAI extension
      }
    }
  ]
}
```

### Phase 3: Tool Definitions

Define tools for each backend:

#### OpenClaw Tools
```javascript
const OPENCLAW_TOOLS = [
  {
    id: 'browser',
    name: 'browser',
    description: 'Browse websites, take screenshots, and interact with web pages',
    parameters: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'URL to browse' },
        action: { 
          type: 'string',
          enum: ['screenshot', 'navigate', 'click', 'scroll', 'extract_text'],
          description: 'Action to perform' 
        },
        selector: { type: 'string', description: 'CSS selector for click/scroll (optional)' }
      },
      required: ['url']
    }
  },
  {
    id: 'canvas',
    name: 'canvas',
    description: 'Visual workspace for collaboration and diagramming',
    parameters: {
      type: 'object',
      properties: {
        action: {
          type: 'string',
          enum: ['create', 'update', 'clear', 'screenshot'],
          description: 'Action to perform'
        },
        data: { type: 'object', description: 'Canvas data (optional)' }
      },
      required: ['action']
    }
  },
  {
    id: 'nodes',
    name: 'nodes',
    description: 'Device and system control (camera, screen recording, location, notifications)',
    parameters: {
      type: 'object',
      properties: {
        action: {
          type: 'string',
          enum: ['camera_snap', 'screen_record', 'location_get', 'system_notify'],
          description: 'Action to perform'
        },
        params: { type: 'object', description: 'Additional parameters (optional)' }
      },
      required: ['action']
    }
  },
  {
    id: 'files',
    name: 'files',
    description: 'File system operations (read, write, list, search)',
    parameters: {
      type: 'object',
      properties: {
        action: {
          type: 'string',
          enum: ['read', 'write', 'list', 'search', 'delete'],
          description: 'Action to perform'
        },
        path: { type: 'string', description: 'File path (for read/write)' },
        pattern: { type: 'string', description: 'Search pattern (for search)' }
      },
      required: ['action']
    }
  }
];
```

#### Goose Tools
```javascript
const GOOSE_TOOLS = [
  {
    id: 'memory',
    name: 'memory',
    description: 'Personalization memory for preferences and facts',
    parameters: {
      type: 'object',
      properties: {
        action: {
          type: 'string',
          enum: ['search', 'add', 'get'],
          description: 'Action to perform'
        },
        key: { type: 'string', description: 'Memory key (for get)' },
        value: { type: 'string', description: 'Memory value (for add)' }
      },
      required: ['action']
    }
  },
  {
    id: 'filesystem',
    name: 'filesystem',
    description: 'File system access via Goose extensions',
    parameters: {
      type: 'object',
      properties: {
        action: {
          type: 'string',
          enum: ['read', 'write', 'list', 'search'],
          description: 'Action to perform'
        },
        path: { type: "string", description: 'File path' }
      },
      required: ['action']
    }
  },
  {
    id: 'chatrecall',
    name: 'chatrecall',
    description: 'Search and retrieve from past conversations',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        count: { type: 'number', description: 'Number of results (default: 5)' }
      },
      required: ['query']
    }
  }
];
```

### Phase 4: Tool Execution

Map tool calls to actual backend commands:

**OpenClaw:**
```javascript
async function executeTool(toolCall, backendConfig) {
  const { name, arguments } = toolCall.function;
  const args = JSON.parse(arguments);

  switch (name) {
    case 'browser':
      return await executeOpenClawBrowser(args);
    case 'canvas':
      return await executeOpenClawCanvas(args);
    case 'nodes':
      return await executeOpenClawNodes(args);
    case 'files':
      return await executeOpenClawFiles(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
```

**Goose:**
```javascript
async function executeTool(toolCall, backendConfig) {
  const { name, arguments } = toolCall.function;
  const args = JSON.parse(arguments);

  switch (name) {
    case 'memory':
      return await executeGooseMemory(args);
    case 'filesystem':
      return await executeGooseFilesystem(args);
    case 'chatrecall':
      return await executeGooseChatrecall(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
```

## Tool Execution Strategy

### Option A: Model-Managed (Native Mode) ⭐ Recommended

Let OpenClaw/Goose model decide when and how to use tools:

**Request format:**
```json
{
  "model": "openclaw",
  "messages": [
    {
      "role": "system",
      "content": "You have access to these tools: browser, canvas, nodes, files. Use them when appropriate."
    }
  ]
}
```

**Response format:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Let me browse that site for you...",
        "tool_calls": [
          {
            "id": "call_abc",
            "type": "function",
            "function": {
              "name": "browser",
              "arguments": "{\"url\": \"https://example.com\", \"action\": \"extract_text\"}"
            }
          }
        ]
      }
    }
  ]
}
```

**Benefits:**
- ✅ True Agentic behavior (model decides)
- ✅ Multi-step reasoning
- ✅ Compatible with Native Mode (if model supports it)
- ✅ Works with Default Mode as fallback

### Option B: Proxy-Managed (Simpler)

Proxy intercepts tool calls and executes them:

**Request format:** Same as Option A

**Response format:** Proxy executes tools and injects results into context

**Benefits:**
- ✅ Simpler implementation
- ✅ Works with any model (even small ones)
- ✅ Guaranteed tool execution
- ⚠️ Less agentic (model doesn't decide)

## Implementation Approach

### For OpenWebUI Integration

**Option 1: Model-Managed (Preferred)**
1. Define tools in `/v1/tools` endpoint
2. Include tools in model's system prompt
3. Let model call tools via `tool_calls` in responses
4. Proxy validates and returns tool results

**Option 2: Hybrid Approach**
1. For capable models (OpenClaw with GPT-5, etc.): Use Model-Managed
2. For incapable models (small local models): Use Proxy-Managed
3. Auto-detect model capabilities

### Tool Call Flow

```
OpenWebUI → Request with tools
    ↓
Proxy → Process request
    ↓
    ↓ If Model-Managed:
    ↓ Pass tools to OpenClaw/Goose
    ↓ OpenClaw/Goose returns tool_calls
    ↓ Return tool_calls to OpenWebUI
    ↓ OpenWebUI displays tool results
    ↓ OpenWebUI sends tool_results in next request
    ↓ Proxy processes tool results and returns final response
    
    ↓ If Proxy-Managed:
    ↓ Proxy executes tools via OpenClaw/Goose CLI
    ↓ Returns tool results directly
    ↓ Final response to OpenWebUI
```

## Next Steps

### Week 1: Tools Endpoint
- [ ] Implement `/v1/tools` endpoint
- [ ] Define OpenClaw tools
- [ ] Define Goose tools
- [ ] Test tool discovery

### Week 2: Tool Execution
- [ ] Implement Model-Managed mode
- [ ] Implement Proxy-Managed mode
- [ ] Add tool execution functions
- [ ] Test tool calling with OpenWebUI

### Week 3: Streaming
- [ ] Implement SSE streaming for tool results
- [ ] Handle streaming tool calls
- [ ] Test streaming with OpenWebUI

### Week 4: Advanced Features
- [ ] Multi-step tool chains
- [ ] Tool result caching
- [ ] Tool error handling
- [ ] Tool usage metrics

## Success Metrics

**MVP (Minimum Viable Product):**
- [ ] Tools endpoint with OpenClaw tools
- [ ] Model-Managed tool calling
- [ ] Basic error handling
- [ ] Works with OpenWebUI's Native Mode

**Production Ready:**
- [ ] Tools for both OpenClaw and Goose
- [ ] Proxy-Managed fallback for any model
- [ ] SSE streaming
- [ ] Tool result caching
- [ ] Full OpenAI function calling compliance
- [ ] Multi-step reasoning support

---

**Next:** Implement `/v1/tools` endpoint and Model-Managed tool calling!
