"""Test Forage MCP server."""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "forage-mcp"],
    )
    
    print("[TEST] Connecting to Forage MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"[TEST] Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")


if __name__ == "__main__":
    asyncio.run(test())
