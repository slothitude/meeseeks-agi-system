"""
Smart MCP Tool Selector

Selects relevant MCP tools based on task analysis.
Instead of dumping all 143 tools, picks the 5-10 most relevant.
"""

import re
from typing import List, Dict
from pathlib import Path
import json


# Tool categories with keywords
TOOL_CATEGORIES = {
    "git": {
        "keywords": ["git", "commit", "branch", "merge", "push", "pull", "repository", "version control"],
        "servers": ["git", "github"],
        "priority": 10
    },
    "github": {
        "keywords": ["github", "issue", "pull request", "pr", "repo", "fork", "star"],
        "servers": ["github"],
        "priority": 9
    },
    "browser": {
        "keywords": ["browser", "website", "web page", "click", "navigate", "screenshot", "scrape"],
        "tools": ["playwright", "browser"],
        "priority": 8
    },
    "search": {
        "keywords": ["search", "find", "look up", "google", "duckduckgo", "web search"],
        "servers": ["duckduckgo"],
        "priority": 8
    },
    "memory": {
        "keywords": ["remember", "knowledge graph", "entity", "relation", "memory", "store", "recall"],
        "servers": ["memory"],
        "priority": 7
    },
    "filesystem": {
        "keywords": ["file", "directory", "folder", "read", "write", "path", "disk"],
        "servers": ["filesystem"],
        "priority": 6
    },
    "database": {
        "keywords": ["database", "sql", "query", "table", "record", "db"],
        "servers": ["database-server"],
        "priority": 7
    },
    "youtube": {
        "keywords": ["youtube", "video", "transcript", "caption"],
        "servers": ["youtube_transcript"],
        "priority": 6
    },
    "thinking": {
        "keywords": ["think", "reason", "analyze", "step by step", "breakdown", "consider"],
        "servers": ["sequentialthinking"],
        "priority": 5
    }
}

# Essential tools always included
ESSENTIAL_TOOLS = [
    "mcp_git_git_status",
    "mcp_filesystem_read_text_file",
    "mcp_filesystem_write_file",
]


def analyze_task(task: str) -> Dict[str, float]:
    """Analyze task to determine which categories are relevant."""
    task_lower = task.lower()
    scores = {}
    
    for category, config in TOOL_CATEGORIES.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in task_lower:
                score += config["priority"]
        
        if score > 0:
            scores[category] = score
    
    return scores


def select_tools(task: str, max_tools: int = 15) -> List[Dict]:
    """Select relevant MCP tools for a task."""
    
    # Load available tools from cache
    cache_file = Path(__file__).parent.parent.parent / "the-crypt" / "mcp_context_cache.json"
    
    if not cache_file.exists():
        return []
    
    try:
        with open(cache_file) as f:
            cache = json.load(f)
    except:
        return []
    
    # Parse available tools from context
    context = cache.get("context", "")
    available_tools = parse_tools_from_context(context)
    
    if not available_tools:
        return []
    
    # Analyze task
    category_scores = analyze_task(task)
    
    # Score each tool
    scored_tools = []
    for tool in available_tools:
        score = 0
        tool_name = tool.get("name", "").lower()
        tool_desc = tool.get("description", "").lower()
        
        # Check if essential
        if tool.get("name") in ESSENTIAL_TOOLS:
            score += 100
        
        # Check category matches
        for category, cat_score in category_scores.items():
            config = TOOL_CATEGORIES.get(category, {})
            
            # Check server match
            for server in config.get("servers", []):
                if f"mcp_{server}_" in tool_name:
                    score += cat_score * 2
            
            # Check keyword match in description
            for keyword in config.get("keywords", []):
                if keyword in tool_desc:
                    score += 1
        
        # Direct keyword match in tool name
        task_words = task.lower().split()
        for word in task_words:
            if len(word) > 3 and word in tool_name:
                score += 5
        
        if score > 0:
            tool["score"] = score
            scored_tools.append(tool)
    
    # Sort by score and return top N
    scored_tools.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Always include essentials if not already
    selected_names = {t["name"] for t in scored_tools[:max_tools]}
    for essential in ESSENTIAL_TOOLS:
        if essential not in selected_names:
            for tool in available_tools:
                if tool.get("name") == essential:
                    scored_tools.insert(0, tool)
                    break
    
    return scored_tools[:max_tools]


def parse_tools_from_context(context: str) -> List[Dict]:
    """Parse tool definitions from MCP context string."""
    tools = []
    
    # Pattern: `mcp_server_tool`: description
    import re
    pattern = r"`(mcp_\w+)`:\s*([^\n]+)"
    
    for match in re.finditer(pattern, context):
        tool_name = match.group(1)
        description = match.group(2).strip()
        
        # Extract server from name
        parts = tool_name.split("_")
        server = parts[1] if len(parts) > 1 else "unknown"
        
        tools.append({
            "name": tool_name,
            "server": server,
            "description": description
        })
    
    return tools


def build_smart_context(task: str, max_tools: int = 15) -> str:
    """Build smart MCP context with only relevant tools."""
    
    tools = select_tools(task, max_tools)
    
    if not tools:
        return ""
    
    # Group by server
    by_server = {}
    for tool in tools:
        server = tool.get("server", "unknown")
        if server not in by_server:
            by_server[server] = []
        by_server[server].append(tool)
    
    # Build context
    lines = ["## Relevant MCP Tools", ""]
    lines.append(f"Based on your task, these {len(tools)} MCP tools are most relevant:")
    lines.append("")
    lines.append("```python")
    lines.append("from skills.meeseeks.mcp_extension import call_mcp")
    lines.append("")
    lines.append("# Example usage:")
    lines.append('result = await call_mcp("TOOL_NAME", {"arg": "value"})')
    lines.append("```")
    lines.append("")
    
    for server, server_tools in sorted(by_server.items()):
        lines.append(f"**{server}** ({len(server_tools)} tools):")
        for tool in server_tools[:5]:
            desc = tool.get("description", "")[:50]
            if len(tool.get("description", "")) > 50:
                desc += "..."
            lines.append(f"- `{tool['name']}`: {desc}")
        lines.append("")
    
    return "\n".join(lines)


# CLI test
if __name__ == "__main__":
    import sys
    
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Search GitHub for pi-agent repositories and create an issue"
    
    print(f"Task: {task}")
    print()
    
    context = build_smart_context(task)
    print(context)
    print(f"\n[INFO] Selected context length: {len(context)} chars")
