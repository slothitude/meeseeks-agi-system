"""Test sequentialthinking MCP server."""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test():
    server_params = StdioServerParameters(
        command="docker",
        args=["run", "--rm", "-i", "mcp/sequentialthinking"],
    )
    
    print("[TEST] Connecting to sequentialthinking...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            print(f"\n[TEST] {len(tools.tools)} tool(s) available:")
            for tool in tools.tools:
                print(f"  - {tool.name}")
                print(f"    {tool.description[:100]}...")
            
            # Test a thought chain
            print("\n[TEST] Running thought chain...")
            
            thoughts = [
                "What makes an AI system truly autonomous?",
                "How does self-improvement work in biological systems?",
                "Can we apply evolutionary principles to AI?"
            ]
            
            for i, thought in enumerate(thoughts, 1):
                result = await session.call_tool("sequentialthinking", {
                    "thought": thought,
                    "thoughtNumber": i,
                    "totalThoughts": len(thoughts),
                    "nextThoughtNeeded": i < len(thoughts)
                })
                print(f"\n  Thought {i}: {thought[:50]}...")
                if hasattr(result, 'content'):
                    for item in result.content:
                        if hasattr(item, 'text'):
                            print(f"  → {item.text[:100]}")


if __name__ == "__main__":
    asyncio.run(test())
