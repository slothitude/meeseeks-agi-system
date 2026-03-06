"""
MCP Extension for Meeseeks - Production Version

Uses async context managers properly to manage MCP server connections.
"""

import json
import asyncio
from pathlib import Path
from typing import Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPManager:
    """Manages multiple MCP server connections."""
    
    def __init__(self, config_path: str = ".mcp.json"):
        self.config_path = Path(config_path)
        self._exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[str, dict] = {}  # tool_name -> {server, tool_def}
        
    async def __aenter__(self):
        await self._exit_stack.__aenter__()
        await self._load_servers()
        return self
    
    async def __aexit__(self, *args):
        await self._exit_stack.__aexit__(*args)
    
    async def _load_servers(self):
        """Load and connect to all MCP servers."""
        if not self.config_path.exists():
            print(f"[MCP] Config not found: {self.config_path}")
            return
        
        with open(self.config_path) as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        print(f"[MCP] Found {len(servers)} server configurations")
        
        for name, server_config in servers.items():
            await self._connect_server(name, server_config)
    
    async def _connect_server(self, name: str, config: dict):
        """Connect to a single MCP server."""
        command = config.get("command")
        args = config.get("args", [])
        env = config.get("env", {})
        
        if not command:
            print(f"[MCP] {name}: no command, skipping")
            return
        
        try:
            print(f"[MCP] Connecting to {name}...")
            
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env if env else None
            )
            
            # Use exit stack to manage context
            read, write = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await session.initialize()
            
            # Discover tools
            tools_result = await session.list_tools()
            
            # Register tools with prefixed names
            for tool in tools_result.tools:
                prefixed_name = f"mcp_{name}_{tool.name}"
                self.tools[prefixed_name] = {
                    "server": name,
                    "original_name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
            
            self.sessions[name] = session
            print(f"[MCP] {name}: connected, {len(tools_result.tools)} tools")
            
        except asyncio.TimeoutError:
            print(f"[MCP] {name}: timeout")
        except Exception as e:
            print(f"[MCP] {name}: failed - {e}")
    
    async def call_tool(self, tool_name: str, arguments: dict = None) -> Any:
        """Call an MCP tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_info = self.tools[tool_name]
        server_name = tool_info["server"]
        original_name = tool_info["original_name"]
        
        if server_name not in self.sessions:
            raise ValueError(f"Server not connected: {server_name}")
        
        session = self.sessions[server_name]
        result = await session.call_tool(original_name, arguments or {})
        
        # Extract text content
        if hasattr(result, 'content'):
            texts = []
            for item in result.content:
                if hasattr(item, 'text'):
                    texts.append(item.text)
            return "\n".join(texts) if texts else result
        
        return result
    
    def list_tools(self) -> list[dict]:
        """List all available MCP tools."""
        return [
            {
                "name": name,
                "description": info["description"],
                "server": info["server"],
                "parameters": info["parameters"]
            }
            for name, info in self.tools.items()
        ]


# Convenience function for use in Meeseeks
_mcp_manager: MCPManager | None = None


async def get_mcp() -> MCPManager:
    """Get or create MCP manager singleton."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
        await _mcp_manager.__aenter__()
    return _mcp_manager


async def call_mcp(tool_name: str, arguments: dict = None) -> Any:
    """Call an MCP tool by name."""
    mcp = await get_mcp()
    return await mcp.call_tool(tool_name, arguments)


# CLI test
if __name__ == "__main__":
    async def main():
        async with MCPManager() as mcp:
            tools = mcp.list_tools()
            print(f"\n[MCP] {len(tools)} tools available:")
            for tool in tools[:20]:  # Show first 20
                desc = tool['description'][:50] + "..." if len(tool['description']) > 50 else tool['description']
                print(f"  {tool['name']}: {desc}")
            
            # Test git_status if available
            git_tools = [t for t in tools if t['server'] == 'git']
            if git_tools:
                print(f"\n[TEST] Testing git_log...")
                try:
                    result = await mcp.call_tool("mcp_git_git_log", {"repo_path": "."})
                    print(f"[TEST] Result: {result[:200]}...")
                except Exception as e:
                    print(f"[TEST] Error: {e}")
    
    asyncio.run(main())
