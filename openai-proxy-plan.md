# OpenAI Proxy - Updated Plan with Goose Discovery

## Discovery: Goose CLI Capabilities

**Goose** is actually a full AI agent framework (like OpenClaw), not just a web server:

**Current Setup:**
- Provider: `custom_z.ai`
- Model: `GLM-5`
- Extensions: chatrecall, skills, todo, code_execution, filesystem, memory, MCP servers
- Web interface: `goose web` (what we're running)
- Already on port 3000

**Key Question:** Should the OpenAI proxy use **OpenClaw** OR **Goose** as the backend?

---

## Decision Matrix

### Option A: Stick with OpenClaw Backend

**Pros:**
- ✅ Already working with OpenClaw's `--json` output
- ✅ OpenClaw integrates with your existing agent network
- ✅ Full tool access (browser, canvas, nodes)
- ✅ Multi-agent coordination (Sloth_rog + sloth_pibot)
- ✅ Session management built-in

**Cons:**
- ❌ 10-20s startup overhead per request (CLI mode)
- ❌ Streaming requires Gateway WebSocket protocol
- ❌ Slower than direct Goose integration

**Best For:**
- Integrating OpenWebUI with your OpenClaw ecosystem
- Using OpenClaw's advanced features (tools, agents)
- Production reliability (OpenClaw is stable)

### Option B: Switch to Goose Backend

**Pros:**
- ✅ Goose already has web interface (could expose API)
- ✅ Using GLM-5 (good model)
- ✅ Faster (no 10-20s overhead if Goose has API mode)
- ✅ Built-in extensions (chatrecall, skills, filesystem, MCP)
- ✅ Potentially native streaming support

**Cons:**
- ❌ Need to implement OpenAI API layer on top of Goose
- ❌ Unknown if Goose has programmatic API (CLI only so far)
- ❌ Lose OpenClaw's agent coordination
- ❌ Lose OpenClaw's advanced tools

**Best For:**
- Pure speed/performance focus
- Single-agent setup (no coordination needed)
- Using Goose's ecosystem

### Option C: Hybrid Backend (Recommended)

**Architecture:**
```
OpenWebUI → Proxy → Backend Selector → OpenClaw OR Goose
                              │
                              ├── OpenClaw: Full-featured, reliable
                              └── Goose: Faster, simpler
```

**Implementation:**
- Add configuration option: `--backend openclaw` or `--backend goose`
- Route requests to selected backend
- Allow per-request backend selection via OpenAI `model` field:
  - `openclaw` → Use OpenClaw
  - `goose` → Use Goose
  - `openclaw-fast` → Use OpenClaw with persistent agent

**Pros:**
- ✅ Best of both worlds
- ✅ Easy to switch between backends
- ✅ Can benchmark performance
- ✅ Gradual migration path

**Cons:**
- ⚠️ More complexity
- ⚠️ Need to implement Goose API integration

---

## Revised Implementation Plan

### Phase 1: Research (Today)

1. **Investigate Goose API capabilities**
   - Check if Goose has REST/HTTP API mode
   - Check if Goose CLI can be automated via stdin/stdout
   - Test streaming support in Goose

2. **Benchmarks**
   - Time OpenClaw CLI response time (average 5 requests)
   - Time Goose CLI response time (average 5 requests)
   - Compare with OpenClaw WebSocket (if implemented)

### Phase 2: Implementation Decision (Tomorrow)

**If Goose has API mode:**
- Implement Goose backend
- Create `goose-backend.js` module
- Add `--backend goose` option
- Support both backends in same proxy

**If Goose no API:**
- Stick with OpenClaw, optimize:
- Implement persistent OpenClaw agent
- Add connection pooling
- Focus on WebSocket streaming

### Phase 3: Streaming Support (Week 1)

**Regardless of backend choice:**

1. **OpenClaw WebSocket Protocol**
   - Reverse-engineer Gateway messages
   - Implement streaming SSE
   - Test with multiple clients

2. **Response Buffering**
   - Buffer responses for smoother streaming
   - Handle connection drops gracefully

### Phase 4: Performance (Week 2)

1. **Persistent Agent Process**
   - For chosen backend, keep process running
   - Use IPC for communication
   - Target: <2s first response, <1s subsequent

2. **Connection Pooling**
   - Pre-warm 2-3 agent instances
   - Load balance requests

### Phase 5: Advanced Features (Week 3+)

1. **Function Calling**
   - Map OpenClaw tools to OpenAI function format
   - Allow OpenWebUI to trigger tools
   - Support streaming function calls

2. **Multi-Model Support**
   - Route to different models based on `model` parameter
   - Support `openclaw:glm-4.7`, `goose:glm-5`, etc.

3. **Observability**
   - Prometheus metrics endpoint
   - Request/response logging
   - Health checks with backend status

---

## Recommendation

**Start with OpenClaw backend** because:
1. It's already working (`--json` output + parsing)
2. Integrates with your existing ecosystem
3. Full OpenClaw feature access
4. Reliable and well-tested

**Then add Goose backend** if:
1. Goose has programmatic API
2. Performance is critical requirement
3. You want to compare both backends

**Hybrid approach** gives you flexibility to:
- Use OpenClaw for production (reliability, features)
- Use Goose for speed (if API available)
- Switch easily based on workload
- A/B test different setups

---

## Next Immediate Actions

### Right Now (5 min)
- [x] Created plan document
- [ ] Check if Goose has API documentation
- [ ] Test basic Goose CLI automation

### This Week
- [ ] Implement OpenClaw WebSocket streaming
- [ ] Add backend selection (OpenClaw vs Goose)
- [ ] Performance benchmarks
- [ ] Update documentation

### This Month
- [ ] Production deployment
- [ ] Monitoring & logging
- [ ] Full OpenAI API compliance

---

## Questions for Slothitude

1. **Backend preference:**
   - Stay with OpenClaw (current working solution)?
   - Switch to Goose (need to implement integration)?
   - Hybrid (both, selectable)?

2. **Priority:**
   - Speed (fastest possible)?
   - Features (tools, agents)?
   - Reliability (production-ready)?

3. **Usage:**
   - OpenWebUI only?
   - Multiple clients (OpenWebUI + Cursor + custom apps)?
   - Concurrent users?

4. **Deployment:**
   - Windows only (your current setup)?
   - Cross-platform (Linux, macOS)?
   - Docker container for easy deployment?
