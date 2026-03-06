"""Test sequentialthinking MCP server."""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test():
    server_params = StdioServerParameters(
        command="docker",
        args=["run", "--rm", "-i", "mcp/sequentialthinking"],
    )
    
    print("[TEST] Connecting to sequentialthinking MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"[TEST] Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")
            
            # Test sequential thinking
            print("\n[TEST] Testing sequential thinking...")
            result = await session.call_tool("sequentialthinking", {
                "thought": "What is the meaning of consciousness in AI systems?",
                "thoughtNumber": 1,
                "totalThoughts": 3,
                "nextThoughtNeeded": True
            })
            print(f"[TEST] Result: {result.content}")


if __name__ == "__main__":
    asyncio.run(test())
