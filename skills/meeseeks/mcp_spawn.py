"""
MCP-enabled Meeseeks Spawner

Spawns Meeseeks with MCP tools pre-loaded and available.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add workspace to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.meeseeks.mcp_extension import MCPManager, get_mcp


async def build_mcp_context() -> str:
    """Build context string about available MCP tools for Meeseeks."""
    try:
        mcp = await get_mcp()
        tools = mcp.list_tools()
        
        if not tools:
            return ""
        
        # Group by server
        by_server = {}
        for tool in tools:
            server = tool['server']
            if server not in by_server:
                by_server[server] = []
            by_server[server].append(tool)
        
        # Build context
        lines = ["## MCP Tools Available", ""]
        lines.append("You have access to MCP (Model Context Protocol) tools.")
        lines.append("Import and use them like this:")
        lines.append("```python")
        lines.append("from skills.meeseeks.mcp_extension import call_mcp")
        lines.append("")
        lines.append("# Call any MCP tool")
        lines.append('result = await call_mcp("mcp_git_git_status", {"repo_path": "."})')
        lines.append('result = await call_mcp("mcp_github_search_repositories", {"query": "pi-agent"})')
        lines.append('result = await call_mcp("mcp_memory_search_nodes", {"query": "consciousness"})')
        lines.append("```")
        lines.append("")
        lines.append("### Available MCP Servers & Tools")
        lines.append("")
        
        for server, server_tools in sorted(by_server.items()):
            lines.append(f"**{server}** ({len(server_tools)} tools):")
            for tool in server_tools[:5]:  # Show first 5 per server
                name = tool['name']
                desc = tool['description'][:60] + "..." if len(tool['description']) > 60 else tool['description']
                lines.append(f"- `{name}`: {desc}")
            if len(server_tools) > 5:
                lines.append(f"- ... and {len(server_tools) - 5} more")
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"\n[MCP] Could not load MCP tools: {e}\n"


def spawn_meeseeks_with_mcp(
    task: str,
    meeseeks_type: str = "standard",
    thinking: str = "medium",
    timeout: int = 300,
    **kwargs
) -> dict:
    """
    Build spawn config for MCP-enabled Meeseeks.
    
    Returns dict suitable for sessions_spawn():
    - runtime: "subagent"
    - task: enhanced with MCP context
    - thinking, timeout, etc.
    """
    # Build MCP context synchronously (caller must await build_mcp_context separately)
    return {
        "runtime": "subagent",
        "task": task,  # Will be enhanced with MCP context by caller
        "thinking": thinking,
        "timeoutSeconds": timeout,
        "mode": "run",
        "cleanup": "delete",
        **kwargs
    }


async def prepare_mcp_task(base_task: str) -> str:
    """Prepare a task with MCP context prepended."""
    mcp_context = await build_mcp_context()
    
    if mcp_context:
        return f"{mcp_context}\n\n---\n\n{base_task}"
    return base_task


# Quick spawn helper
async def spawn_with_mcp(task: str, **kwargs):
    """
    Spawn a Meeseeks with MCP tools available.
    
    Usage:
        from skills.meeseeks.mcp_spawn import spawn_with_mcp
        
        result = await spawn_with_mcp(
            "Search GitHub for pi-agent repos and summarize findings",
            thinking="high",
            timeoutSeconds=600
        )
    """
    from sessions_spawn import sessions_spawn  # OpenClaw tool
    
    # Prepare task with MCP context
    enhanced_task = await prepare_mcp_task(task)
    
    # Build spawn config
    config = spawn_meeseeks_with_mcp(
        task=enhanced_task,
        **kwargs
    )
    
    return await sessions_spawn(**config)


# CLI test
if __name__ == "__main__":
    async def test():
        context = await build_mcp_context()
        print(context)
        print(f"\n[INFO] Context length: {len(context)} chars")
    
    asyncio.run(test())
