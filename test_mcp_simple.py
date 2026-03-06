"""
Simple MCP test with git server.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_git():
    """Test git MCP server."""
    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-server-git", "--repository", "C:\\Users\\aaron\\.openclaw\\workspace"],
    )
    
    print("[TEST] Connecting to git MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"[TEST] Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:50]}...")
            
            # Call git_status
            print("\n[TEST] Calling git_status...")
            result = await session.call_tool("git_status", {})
            print(f"[TEST] Result: {result.content}")


if __name__ == "__main__":
    asyncio.run(test_git())
