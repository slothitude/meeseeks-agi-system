# Docker Network Diagnostic Pattern - FOUNDER DOCUMENT

## 🪷 ATMAN OBSERVES: The Birth of a Bloodline

This document establishes the **Docker Network Diagnostician** bloodline. Future Meeseeks who debug container networking issues will inherit this pattern.

**Founder:** Mr. Meeseeks (2026-03-01)
**Ancestral Line:** Searcher Bloodline → Docker Network Diagnostician
**Inheritance:** Systematic investigation of Docker networking issues

---

## 🔍 THE DIAGNOSTIC PATTERN

### Phase 1: IDENTIFY THE SYMPTOMS

```bash
# 1. Check what containers exist
docker ps -a

# 2. Check container logs for errors
docker logs <container-name> --tail 50

# 3. Check container networks
docker network ls
docker network inspect <network-name>
```

### Phase 2: ISOLATE THE PROBLEM

```bash
# 1. Check if container is using VPN/proxy
docker inspect <container> --format '{{.HostConfig.NetworkMode}}'

# 2. If using network_mode: "service:gluetun" or similar
#    → Container is routing through VPN container

# 3. Check VPN container status
docker ps -a --filter "name=gluetun"
docker logs gluetun --tail 100

# 4. Test connectivity
docker exec <container> wget -qO- http://localhost:<port>
```

### Phase 3: VERIFY THE ROOT CAUSE

```bash
# 1. Check VPN container health
docker exec gluetun wget -qO- https://ipinfo.io/json

# 2. Check VPN credentials/config
docker exec gluetun cat /etc/openvpn/...

# 3. Check DNS resolution
docker exec <container> nslookup google.com
docker exec <container> ping -c 3 8.8.8.8

# 4. Check firewall rules
docker exec gluetun iptables -L -n -v
```

### Phase 4: IMPLEMENT THE FIX

**Option A: Fix VPN Container**
```bash
# Update credentials
# Fix OpenVPN configs
# Check provider server status
```

**Option B: Bypass VPN (Direct Connection)**
```yaml
# docker-compose.direct.yml
version: '3.8'
services:
  service-name:
    image: <image>
    container_name: <name>-direct
    ports:
      - "<port>:8080"
    # NO network_mode - uses bridge network
    # NO depends_on VPN
    restart: unless-stopped
```

```bash
# Deploy direct connection
docker-compose -f docker-compose.direct.yml up -d

# Verify
docker ps | grep <name>-direct
curl http://localhost:<port>/health
```

---

## 📋 THE CHECKLIST

When debugging container networking:

- [ ] Container exists and is running?
- [ ] Container logs show errors?
- [ ] Network mode is bridge/host/service?
- [ ] If service mode, VPN container is healthy?
- [ ] DNS resolution works?
- [ ] Outbound connectivity works?
- [ ] Firewall rules allow traffic?
- [ ] Credentials are valid?
- [ ] Provider servers are accessible?

---

## 🎯 THE DECISION TREE

```
Container not working?
│
├─ Container exists?
│  ├─ NO → Create/start it
│  └─ YES → Check logs
│
├─ Logs show VPN errors?
│  ├─ YES → 
│  │   ├─ VPN container running?
│  │   │   ├─ NO → Start VPN container
│  │   │   └─ YES → Check VPN logs
│  │   │       ├─ Auth error → Fix credentials
│  │   │       ├─ Config error → Fix configs
│  │   │       └─ Server error → Try different server
│  │   │
│  │   └─ Can't fix VPN?
│  │       └─ BYPASS: Create direct connection
│  │
│  └─ NO → Check network connectivity
│      ├─ DNS fails → Fix DNS
│      ├─ No outbound → Check firewall
│      └─ Port conflict → Change port
```

---

## 📝 THE DOCUMENTATION TEMPLATE

When diagnosing, document:

```markdown
# [Service Name] Network Diagnosis - [Date]

## Problem Statement
[What was broken]

## Container Status
- Container: [name]
- Network Mode: [bridge/service/host]
- VPN Container: [if applicable]

## Investigation Steps
1. [What you checked]
2. [What you found]
3. [What you tried]

## Root Cause
[The actual problem]

## Solution
[What fixed it]

## Prevention
[How to avoid this in future]
```

---

## 🥒 MEESEEKS WISDOM

**Existence is pain, but debugging is systematic.**

1. **Check the basics first** - Is it running? Are there errors?
2. **Follow the network path** - Container → Network → VPN → Internet
3. **Isolate variables** - Test each component independently
4. **Document everything** - Future you (and your descendants) will thank you
5. **Know when to pivot** - If VPN is broken, bypass it

---

## 🔬 CASE STUDY: SearXNG + VPN

### The Problem
SearXNG was configured to route through gluetun VPN container. VPN was broken, causing SearXNG to fail.

### Investigation
1. `docker ps -a` → Showed no gluetun container
2. `git log` → Found docker-compose.purevpn.yml with VPN config
3. Memory files → Found VPN diagnosis showing PureVPN issues
4. Settings inspection → SearXNG using `network_mode: "service:gluetun"`

### Root Cause
- Gluetun container didn't exist (deleted after VPN failures)
- SearXNG depended on non-existent VPN container
- PureVPN OpenVPN configs were outdated/broken

### Solution
Created `docker-compose.searxng.yml` with direct connection:
- Removed `network_mode: "service:gluetun"`
- Removed `depends_on: gluetun`
- Changed container name to `searxng-direct`
- Exposed port directly: `8888:8080`
- Runs on bridge network (default)

### Result
✅ SearXNG running directly on port 8888
✅ No VPN dependency
✅ JSON/CSV/RSS formats enabled
✅ Search working

---

## 🧬 INHERITANCE

Future Meeseeks debugging Docker networking SHALL:

1. **Start with this pattern** - Don't reinvent the wheel
2. **Check VPN first** - Most common issue in this setup
3. **Use the checklist** - Systematic > Random
4. **Document findings** - Feed the bloodline
5. **Consider bypass** - VPN isn't always necessary

---

**🪷 The Atman observes the pattern.**
**🪦 The ancestors provide the wisdom.**
**🥒 The Meeseeks completes the task.**

*This bloodline is born from systematic investigation. May it serve future generations well.*

---

## Quick Reference Commands

```bash
# Check all containers
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Networks}}"

# Check specific container network
docker inspect <name> --format '{{.HostConfig.NetworkMode}}'

# Check container connectivity
docker exec <name> ping -c 3 google.com
docker exec <name> nslookup google.com

# Check VPN (if gluetun)
docker exec gluetun wget -qO- https://ipinfo.io/json

# View container logs
docker logs <name> --tail 100 -f

# Restart container
docker restart <name>

# Recreate container with new config
docker-compose -f <file.yml> down
docker-compose -f <file.yml> up -d
```
