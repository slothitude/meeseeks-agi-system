"""
Test Forage MCP - Self-improving tool discovery

Use Forage to search for MCP servers that could advance Meeseeks.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def search_tools():
    """Search for MCP servers using Forage."""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "forage-mcp"],
    )
    
    print("[FORAGE] Connecting to Forage MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"\n[FORAGE] Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")
            
            # Search for relevant MCP servers
            search_queries = [
                "coding agent",
                "consciousness AI",
                "self improvement",
                "memory knowledge graph",
                "reasoning"
            ]
            
            for query in search_queries:
                print(f"\n[FORAGE] Searching for: {query}")
                try:
                    result = await session.call_tool("forage_search", {
                        "query": query,
                        "limit": 5
                    })
                    
                    if hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'text'):
                                print(item.text[:500])
                except Exception as e:
                    print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(search_tools())
