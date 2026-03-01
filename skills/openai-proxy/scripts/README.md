# OpenAI Proxy for OpenClaw & Goose

Multi-agent OpenAI-compatible HTTP API proxy supporting both OpenClaw and Goose CLI backends.

## Status

✅ OpenClaw backend: Working (non-streaming)
✅ Goose backend: Implemented
✅ Multi-backend routing: Working
⚠️ Streaming: Not yet implemented
✅ Windows service: Supported

## Quick Start

### Start Multi-Agent Proxy Server

```bash
cd skills/openai-proxy/scripts
node openai-proxy-multi.js --port 3001
```

With backend selection:
```bash
# Use OpenClaw (default)
node openai-proxy-multi.js --backend openclaw

# Use Goose
node openai-proxy-multi.js --backend goose

# Auto-select based on model parameter
node openai-proxy-multi.js --backend auto
```

With verbose logging:
```bash
node openai-proxy-multi.js --port 3001 --verbose
```

## Configure Clients

### OpenWebUI

1. Open OpenWebUI (usually http://localhost:3000 or 8080)
2. Go to **Settings → Connections** (or **Providers → Add Connection**)
3. Add a new **OpenAI-compatible** connection:
   - **Name**: OpenClaw & Goose
   - **Base URL**: `http://localhost:3001/v1`
   - **API Key**: Any value (not validated)
   - **Model**: `openclaw` or `goose`

4. Switch between backends by changing the model name:
   - Use `openclaw` → Routes to OpenClaw
   - Use `goose` → Routes to Goose CLI

## Backend Selection

### Command Line
```bash
# Specify default backend
--backend openclaw    # Use OpenClaw by default
--backend goose       # Use Goose by default
--backend auto          # Auto-detect from model parameter
```

### Per-Request
Clients can specify backend via the `model` parameter:
- `openclaw` → Use OpenClaw agent
- `goose` → Use Goose CLI
- Any other name → Uses default backend

### Example Requests

**Using OpenClaw:**
```json
{
  "model": "openclaw",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

**Using Goose:**
```json
{
  "model": "goose",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

## API Endpoints

### POST /v1/chat/completions

Standard OpenAI Chat Completions endpoint with multi-backend routing.

**Request:**
```json
{
  "model": "openclaw",  // or "goose" to switch backends
  "messages": [...],
  "stream": false
}
```

### GET /v1/models

Lists available backends as models:
```json
{
  "object": "list",
  "data": [
    {"id": "openclaw", "object": "model", ...},
    {"id": "goose", "object": "model", ...}
  ]
}
```

### GET /backends

Returns backend status:
```json
{
  "default": "openclaw",
  "available": [
    {"name": "openclaw", "displayName": "OpenClaw"},
    {"name": "goose", "displayName": "Goose CLI"}
  ]
}
```

### GET /health

Health check with backend information.

## Backend Comparison

| Feature | OpenClaw | Goose CLI |
|---------|-----------|-----------|
| Response Time | 10-20s | 3-5s |
| Streaming | ❌ (needs WS) | ⚠️ (needs investigation) |
| Session Management | ✅ Built-in | ✅ Built-in |
| Tool Access | ✅ Full | ⚠️ CLI limited |
| Coordination | ✅ With other agents | ❌ Single agent |
| Warm Agent | ❌ Per request | ✅ Sessions warmed |

## Windows Service Setup

### Automatic Startup (Recommended)

Run as Administrator:
```bash
# Update install-service.ps1 to use multi-agent version
powershell -ExecutionPolicy Bypass -File install-service.ps1
```

The service will auto-start and run both backends.

## Troubleshooting

### Backend Not Found

Check if the CLI tool is installed:
```bash
# OpenClaw
where openclaw

# Goose
where goose
```

### Port Already in Use

Use a different port:
```bash
node openai-proxy-multi.js --port 3002
```

### Slow Responses

OpenClaw: ~10-20s per request (normal for CLI mode)
Goose: ~3-5s per request (faster due to session warming)

## Architecture

```
OpenWebUI/OpenAI Client
        ↓ HTTP (OpenAI format)
    OpenAI Proxy Server (Express)
        ↓ Backend Selector (from model field)
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
OpenClaw Agent        Goose CLI Agent
(backend: openclaw)    (backend: goose)
    │                     │
    ▼                     ▼
OpenClaw Gateway      Goose CLI Sessions
(RPC mode)            (custom_z.ai/GLM-5)
```

## Development

### Test Individual Backends

```bash
# Test OpenClaw
node C:\Users\aaron\AppData\Roaming\npm\node_modules\openclaw\dist\index.js agent --local --json --message "test"

# Test Goose
cd C:\Users\aaron\AppData\Roaming\Block\goose && goose run "test"
```

### Add More Backends

1. Implement execute function in `BACKENDS` object
2. Implement parseResponse function
3. Add backend name to determineBackend() logic
4. Test with --backend flag

## Future Improvements

- [ ] Streaming support (SSE)
- [ ] Persistent agent mode for OpenClaw
- [ ] Connection pooling
- [ ] Request/response caching
- [ ] Load balancing between backends
- [ ] Metrics and monitoring
- [ ] Function calling (tools)

## License

MIT
