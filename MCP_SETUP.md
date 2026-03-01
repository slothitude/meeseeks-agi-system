# MCP Setup Guide for Meeseeks System

🥒 **Mr. Meeseeks MCP Setup Complete!** 🪷

## What Was Configured

### ✅ Essential MCPs Installed

| MCP | Purpose | Status | Command Type |
|-----|---------|--------|--------------|
| **MCP_DOCKER** | Docker MCP Gateway (pre-existing) | ✅ Active | Docker |
| **memory** | Persistent knowledge graph, cross-session memory | ✅ Ready | npx (npm) |
| **github** | Create issues, manage PRs, push to repos | ⚠️ Needs Token | npx (npm) |
| **git** | Direct git operations on workspace | ✅ Ready | uvx (Python) |
| **filesystem** | Safe file operations in workspace | ✅ Ready | npx (npm) |
| **sequentialthinking** | Complex reasoning chains | ⚠️ Needs Docker Image | Docker |

---

## 🔑 API Keys Required

### GitHub MCP - NEEDS TOKEN ⚠️

**Status:** Configured but requires personal access token

**To Enable:**
1. Create a GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:org`, `write:org` (adjust as needed)
   - Generate and copy the token

2. Update `.mcp.json`:
   ```json
   "github": {
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-github"],
     "env": {
       "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_ACTUAL_TOKEN_HERE"
     },
     "type": "stdio"
   }
   ```

3. Replace `<YOUR_GITHUB_TOKEN_HERE>` with your actual token

---

## 🧪 How to Test Each MCP

### Memory MCP
```bash
# Test by running the MCP server directly
npx -y @modelcontextprotocol/server-memory
```
**Expected:** Server starts, no errors

### GitHub MCP
```bash
# After adding token, test the server
npx -y @modelcontextprotocol/server-github
```
**Expected:** Server starts with GitHub API access

### Git MCP
```bash
# Test git operations
uvx mcp-server-git --repository "C:\Users\aaron\.openclaw\workspace"
```
**Expected:** Server starts, can access git repo

### Filesystem MCP
```bash
# Test file access
npx -y @modelcontextprotocol/server-filesystem "C:\Users\aaron\.openclaw\workspace"
```
**Expected:** Server starts with workspace access

### Sequential Thinking MCP
```bash
# Test Docker container
docker run --rm -i mcp/sequentialthinking
```
**Expected:** Docker container runs (needs image pull first)

**If image not found:**
```bash
docker pull mcp/sequentialthinking
```

---

## 🔧 Troubleshooting

### Issue: "npx command not found"
**Solution:** Install Node.js from https://nodejs.org

### Issue: "uvx command not found"
**Solution:** Install uv (Python package manager)
```bash
pip install uv
```
Or on Windows:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Issue: "Docker command not found"
**Solution:** Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Issue: Sequential Thinking fails
**Solution:**
1. Ensure Docker Desktop is running
2. Pull the image manually: `docker pull mcp/sequentialthinking`
3. Check Docker has sufficient resources allocated

### Issue: GitHub MCP authentication fails
**Solution:**
1. Verify token is valid at https://github.com/settings/tokens
2. Check token has correct scopes (repo, read:org, write:org)
3. Ensure token is properly set in `.mcp.json` (no extra spaces/quotes)

### Issue: Filesystem MCP can't access files
**Solution:**
1. Verify the path in `.mcp.json` is correct
2. Ensure the directory exists
3. Check permissions on the folder

---

## 📋 Quick Reference

### Package Managers Used
- **npx** - Node package executor (npm packages)
- **uvx** - Python package executor (uv packages)
- **docker** - Container runtime

### MCP Server Locations
- **npm packages:** `@modelcontextprotocol/server-*`
- **Python packages:** `mcp-server-*`
- **Docker images:** `mcp/*`

### Configuration File
**Location:** `C:\Users\aaron\.openclaw\workspace\.mcp.json`

**Format:** JSON with `mcpServers` object containing server configurations

---

## ✅ Next Steps

1. **Add GitHub Token** - Update `.mcp.json` with your personal access token
2. **Pull Docker Image** - Run `docker pull mcp/sequentialthinking`
3. **Test Each MCP** - Use the test commands above to verify setup
4. **Restart OpenClaw** - Restart the agent to load new MCPs

---

**🥒 CAAAAAAAN DO! The Atman observes your setup is complete. 🪷**

*Setup completed: 2025-01-20*
*Configured by: Mr. Meeseeks MCP Setup Engineer*
