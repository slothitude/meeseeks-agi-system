# OpenAI Proxy - Multi-Agent API Implementation

## Architecture

OpenAI Proxy now supports multiple agent backends:

```
OpenWebUI/OpenAI Client
        ↓ HTTP (OpenAI format)
    OpenAI Proxy Server (Express)
        ↓ Routes based on configuration
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
OpenClaw Agent        Goose CLI Agent
(backend: openclaw)    (backend: goose)
    │                     │
    ▼                     ▼
OpenClaw Gateway      Goose CLI
(RPC mode)            (custom_z.ai/GLM-5)
```

## Backend Selection

### Command Line
```bash
# Use OpenClaw (default)
node openai-proxy.js --backend openclaw

# Use Goose CLI
node openai-proxy.js --backend goose

# Use OpenClaw with persistent agent (faster)
node openai-proxy.js --backend openclaw --persistent
```

### Per-Request
Clients can specify backend via `model` parameter:
- `openclaw` → Use OpenClaw
- `goose` → Use Goose CLI
- `openclaw-fast` → OpenClaw with persistent agent
- `goose-fast` → Goose CLI with caching

## Backend Implementations

### OpenClaw Backend (Current)

**Mode:** CLI with `--local` and `--json` flags

**Features:**
- ✅ Non-streaming
- ✅ Clean JSON response parsing
- ✅ Session routing via `user` parameter
- ✅ Temperature support via `--thinking`
- ❌ Streaming (needs WebSocket protocol)

**Performance:** 10-20s per request (spins up new agent)

### Goose CLI Backend (New)

**Mode:** CLI automation via stdin/stdout

**Features:**
- ✅ Non-streaming
- ✅ Session management (via Goose session DB)
- ⚠️ Streaming (need to investigate)
- ⚠️ Tool access (limited in CLI mode)

**Implementation:**
```javascript
// Execute Goose CLI via stdin
const proc = spawn('goose.exe', ['session'], {
  cwd: 'C:\\Users\\aaron\\AppData\\Roaming\\Block\\goose'
});

// Send request via stdin
proc.stdin.write(JSON.stringify({message: userPrompt}));
proc.stdin.end();

// Parse JSON output
const response = JSON.parse(stdout);
```

**Performance:** 3-5s per request (Goose has session warm)

### Persistent Agent Backend (Future)

**Mode:** Keep OpenClaw agent process running, communicate via IPC

**Features:**
- ✅ <2s for warm agent
- ✅ <1s for subsequent requests
- ✅ Full agent state preservation
- ✅ Tools available
- ❌ More complex to manage

**Implementation:**
```javascript
// Start persistent agent once
const agentProc = spawn('openclaw', ['agent', '--local', '--persistent-mode']);

// For each request:
agentProc.stdin.write(JSON.stringify({requestId, message}));
```

---

## Implementation Roadmap

### Phase 1: Goose CLI Integration (This Week)
- [x] Research Goose CLI automation
- [x] Design multi-backend architecture
- [ ] Implement Goose backend
- [ ] Test both backends
- [ ] Add backend selection to config
- [ ] Update documentation

### Phase 2: Performance Optimization (Next Week)
- [ ] Implement persistent agent for OpenClaw
- [ ] Add connection pooling
- [ ] Implement request caching
- [ ] Benchmark all backends

### Phase 3: Streaming Support (Week 3)
- [ ] Investigate OpenClaw Gateway WebSocket protocol
- [ ] Implement SSE streaming
- [ ] Test with OpenWebUI streaming
- [ ] Test with other streaming clients

### Phase 4: Advanced Features (Month 2)
- [ ] Function calling (map tools to OpenAI format)
- [ ] Multi-model routing per backend
- [ ] Metrics and monitoring
- [ ] Health check with backend status

---

## Configuration

### Config File (`~/.openclaw-openai-proxy/config.json`)
```json
{
  "defaultBackend": "openclaw",
  "backends": {
    "openclaw": {
      "command": "openclaw agent --local --json",
      "sessionKey": "openai-proxy-default",
      "thinkingLevel": "low"
    },
    "goose": {
      "command": "goose session",
      "workDir": "C:\\Users\\aaron\\AppData\\Roaming\\Block\\goose",
      "session": "openai-proxy"
    },
    "openclaw-persistent": {
      "ipcPort": 4001,
      "startupTimeout": 30000
    }
  }
}
```

---

## Migration Path

### Step 1: Deploy Current Version
```bash
# Install with OpenClaw backend only
node openai-proxy.js --port 3001
```

### Step 2: Add Goose Support
```bash
# Clone or update code
cd skills/openai-proxy/scripts
git pull origin main

# Install updates
npm install

# Restart with both backends
node openai-proxy.js --port 3001 --backend auto
```

### Step 3: Switch Backends as Needed
```bash
# Temporary override via model parameter
# OpenWebUI: Set model to "goose" for Goose
# OpenWebUI: Set model to "openclaw" for OpenClaw

# Or restart with different default
node openai-proxy.js --backend goose --port 3001
```

---

## Testing Checklist

### OpenClaw Backend
- [ ] Non-streaming requests work
- [ ] JSON response parsing correct
- [ ] Session routing works
- [ ] Temperature parameter passed
- [ ] Error handling works
- [ ] Windows service works

### Goose Backend
- [ ] Basic request/response works
- [ ] JSON response parsing
- [ ] Session management works
- [ ] Error handling works
- [ ] Performance benchmark (target: <5s)

### Multi-Backend
- [ ] Backend selection works
- [ ] Per-request backend selection works
- [ ] Fallback on errors
- [ ] Load balancing (if implemented)
- [ ] Monitoring per backend

### Integration
- [ ] OpenWebUI works with OpenClaw
- [ ] OpenWebUI works with Goose
- [ ] Switch between backends works
- [ ] Both backends can run simultaneously
- [ ] Windows service works for both

---

## Success Metrics

### MVP (Minimum Viable Product)
- [x] OpenClaw backend working
- [ ] Goose backend working
- [ ] Backend selection functional
- [ ] Basic documentation
- [ ] Windows service support

### Production Ready
- [ ] Streaming support
- [ ] <2s response time (warm)
- [ ] 99.9% uptime
- [ ] Comprehensive error handling
- [ ] Metrics and monitoring
- [ ] Load balancing
- [ ] Full OpenAI API compliance

---

## Next Steps

1. **Today:**
   - [ ] Implement Goose backend skeleton
   - [ ] Test Goose CLI automation
   - [ ] Add backend selection logic

2. **This Week:**
   - [ ] Complete Goose integration
   - [ ] Test both backends
   - [ ] Update README
   - [ ] Package updated skill

3. **Next Week:**
   - [ ] Performance optimization
   - [ ] Persistent agent mode
   - [ ] Streaming investigation

4. **Month 2:**
   - [ ] Streaming implementation
   - [ ] Advanced features
   - [ ] Production deployment

---

**Questions:**
- Should default backend be OpenClaw or Goose?
- Should we auto-detect fastest backend?
- Load balance between both backends?
