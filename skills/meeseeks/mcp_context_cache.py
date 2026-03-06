"""
MCP Context Cache

Caches MCP tool context to avoid reconnecting on every spawn.
Refreshes periodically or on demand.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

# Cache file path
CACHE_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "mcp_context_cache.json"
CONTEXT_TTL_SECONDS = 300  # 5 minutes


async def get_cached_mcp_context(force_refresh: bool = False) -> str:
    """
    Get MCP context from cache or refresh if stale.
    
    Returns context string for injection into Meeseeks tasks.
    """
    # Check cache
    if not force_refresh and CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
            
            cached_at = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
            age = (datetime.now() - cached_at).total_seconds()
            
            if age < CONTEXT_TTL_SECONDS:
                return cache.get("context", "")
        except:
            pass
    
    # Refresh cache
    context = await _build_fresh_context()
    
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "context": context
        }, f)
    
    return context


async def _build_fresh_context() -> str:
    """Build MCP context by connecting to servers."""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from contextlib import AsyncExitStack
        
        config_path = Path(__file__).parent.parent.parent / ".mcp.json"
        
        if not config_path.exists():
            return ""
        
        with open(config_path) as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        
        all_tools = []
        
        async with AsyncExitStack() as stack:
            for name, server_config in servers.items():
                command = server_config.get("command")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if not command:
                    continue
                
                try:
                    server_params = StdioServerParameters(
                        command=command,
                        args=args,
                        env=env if env else None
                    )
                    
                    read, write = await stack.enter_async_context(
                        stdio_client(server_params)
                    )
                    
                    session = await stack.enter_async_context(
                        ClientSession(read, write)
                    )
                    
                    await session.initialize()
                    tools_result = await session.list_tools()
                    
                    for tool in tools_result.tools:
                        all_tools.append({
                            "server": name,
                            "name": f"mcp_{name}_{tool.name}",
                            "original": tool.name,
                            "description": tool.description or ""
                        })
                        
                except Exception:
                    pass  # Skip failed servers
        
        if not all_tools:
            return ""
        
        # Group by server
        by_server = {}
        for tool in all_tools:
            server = tool['server']
            if server not in by_server:
                by_server[server] = []
            by_server[server].append(tool)
        
        # Build context
        lines = ["## MCP Tools Available", ""]
        lines.append("You have access to MCP (Model Context Protocol) tools.")
        lines.append("Use the `exec` tool to call them via Python:")
        lines.append("```bash")
        lines.append('python -c "')
        lines.append("import asyncio")
        lines.append("from skills.meeseeks.mcp_extension import call_mcp")
        lines.append("")
        lines.append("async def main():")
        lines.append('    result = await call_mcp("TOOL_NAME", {"arg": "value"})')
        lines.append("    print(result)")
        lines.append("")
        lines.append("asyncio.run(main())")
        lines.append('"')
        lines.append("```")
        lines.append("")
        lines.append("### Available Tools by Server")
        lines.append("")
        
        for server, tools in sorted(by_server.items()):
            lines.append(f"**{server}** ({len(tools)} tools):")
            for tool in tools[:3]:
                desc = tool['description'][:50] + "..." if len(tool['description']) > 50 else tool['description']
                lines.append(f"- `{tool['name']}`: {desc}")
            if len(tools) > 3:
                lines.append(f"- ... and {len(tools) - 3} more")
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"\n[MCP] Error loading tools: {e}\n"


def refresh_mcp_context():
    """Force refresh of MCP context cache."""
    asyncio.run(get_cached_mcp_context(force_refresh=True))


if __name__ == "__main__":
    context = asyncio.run(get_cached_mcp_context(force_refresh=True))
    print(context)
    print(f"\n[INFO] Context length: {len(context)} chars")
