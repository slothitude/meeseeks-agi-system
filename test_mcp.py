"""Quick MCP test with just git server."""

import asyncio
import sys
sys.path.insert(0, '.')

from skills.meeseeks.mcp_extension import MCPServer

async def test():
    config = {
        "command": "uvx",
        "args": ["mcp-server-git", "--repository", "C:\\Users\\aaron\\.openclaw\\workspace"],
        "type": "stdio"
    }
    
    server = MCPServer("git", config)
    success = await server.start()
    
    if success:
        print(f"\n[TEST] Git server connected!")
        print(f"[TEST] Tools: {[t['name'] for t in server.tools]}")
        
        # Try calling a tool
        result = await server.call_tool("git_status", {})
        print(f"\n[TEST] git_status result: {result}")
        
        await server.stop()
    else:
        print("[TEST] Failed to start git server")

if __name__ == "__main__":
    asyncio.run(test())
