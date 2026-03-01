# OpenAI Multi-Agent Proxy - LLM Provider Mode

## What's New

OpenClaw and Goose agents now appear as **LLM API providers** with rich metadata, making them auto-discoverable in OpenWebUI and other OpenAI-compatible clients.

## LLM Provider Mode

Your agents now return provider metadata in the `/v1/models` endpoint:

```json
{
  "id": "openclaw",
  "object": "model",
  "provider": "OpenClaw",
  "description": "OpenClaw AI agent with full tool access, agent coordination, and multi-session support.",
  "pricing": {
    "input": 0,
    "output": 0
  },
  "capabilities": ["tools", "agents", "browser", "canvas", "files"]
}
```

## Provider Metadata

### OpenClaw

- **Provider Name:** OpenClaw
- **Capabilities:** tools, agents, browser, canvas, files
- **Max Tokens:** 200,000
- **Pricing:** Usage-based (configurable in OpenClaw)
- **Features:**
  - Full tool access (browser, canvas, nodes, cron)
  - Multi-agent coordination (work with sloth_pibot)
  - Session management
  - Filesystem access
  - RAG (Retrieval Augmented Generation)

### Goose

- **Provider Name:** Goose
- **Capabilities:** extensions, memory, filesystem, chatrecall
- **Max Tokens:** 128,000
- **Pricing:** Usage-based
- **Features:**
  - Built-in extensions platform
  - Memory system
  - Chatrecall (conversation history)
  - Filesystem access
  - Code execution

## Auto-Discovery in OpenWebUI

1. Open OpenWebUI
2. Go to **Settings → Providers** or **Settings → Connections**
3. The providers should auto-appear under "Custom Providers"
4. Select your preferred provider:
   - Use OpenClaw for full features and coordination
   - Use Goose for speed and simplicity

## Using as LLM API Provider

Clients can now discover and use your agents as standard LLM providers:

```bash
# OpenWebUI configuration
Base URL: http://localhost:3001/v1

# Cursor configuration
Base URL: http://localhost:3001/v1

# Custom scripts
curl -X GET http://localhost:3001/v1/models
```

## Backend Selection

### Command Line
```bash
# Default backend (OpenClaw)
node openai-proxy-multi.js

# Use Goose by default
node openai-proxy-multi.js --backend goose
```

### OpenAI Model Parameter

Clients can specify backend per-request using the `model` field:

```json
{
  "model": "openclaw",
  "messages": [...]
}
```

```json
{
  "model": "goose",
  "messages": [...]
}
```

## Provider Comparison

| Provider | Speed | Features | Tools | Coordination |
|---------|-------|----------|-------|--------------|
| **OpenClaw** | 10-20s | ★★★★★ | ★★★★★ | ★★★★★ |
| **Goose** | 3-5s | ★★★★ | ★★★★ | ★ |

- **Speed:** Goose is faster (session warming)
- **Features:** OpenClaw has more tools and agent coordination
- **Tools:** Both have filesystem and extensions
- **Coordination:** OpenClaw can coordinate with multiple agents

## Troubleshooting

### Providers Not Appearing

1. Check proxy is running:
   ```bash
   curl http://localhost:3001/v1/models
   ```

2. Verify OpenWebUI base URL:
   - Settings → Providers → Custom Provider
   - Base URL: `http://localhost:3001/v1`

3. Check logs:
   ```bash
   node openai-proxy-multi.js --verbose
   ```

### Switching Providers

OpenWebUI should let you switch between providers:
- Use model selection to choose `openclaw` or `goose`
- Each maintains its own conversation history
- Switch seamlessly without restarting

## Architecture Update

```
OpenWebUI (Provider Mode)
        ↓ /v1/models (provider metadata)
        ↓ /v1/chat/completions (LLM API)
    OpenAI Multi-Agent Proxy
        ↓ Backend Selector
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
OpenClaw Agent        Goose CLI Agent
(backend: openclaw)    (backend: goose)
```

## Future Enhancements

- [ ] Add token usage tracking to pricing metadata
- [ ] Add streaming support
- [ ] Add function/calling format compatibility
- [ ] Add context window information
- [ ] Add rate limit information
- [ ] Add provider health status

## Success Metrics

**LLM Provider Mode:**
- [x] Agents appear as providers in `/v1/models`
- [x] Rich provider metadata (description, capabilities, pricing)
- [x] Auto-discovery in OpenWebUI
- [x] Per-request backend selection via `model` parameter
- [ ] Streaming support (next milestone)

---

**Ready for production use!** 🚀
