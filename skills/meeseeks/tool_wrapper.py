#!/usr/bin/env python3
"""
Tool Wrapper - Intercept tool calls through the_body for acceleration.

This module provides transparent tool wrapping for Meeseeks workers.
All tool calls go through the_body first for fast-path execution.

Architecture:
    Meeseeks → wrapped_tool(**args)
                    ↓
              the_body.call_tool()
                    ↓
         ┌─────────┴─────────┐
         ↓                   ↓
    SKILL HIT            SKILL MISS
    (<10ms)           (passthrough)
    
Usage:
    from tool_wrapper import wrap_tools, get_body_stats
    
    # Wrap a dict of tools
    tools = {
        "read": original_read,
        "exec": original_exec,
        ...
    }
    wrapped = wrap_tools(tools)
    
    # Now use wrapped tools - they go through the_body
    result = wrapped["read"](path="file.txt")
    
    # Check stats
    stats = get_body_stats()
    # {'fast_path': 10, 'slow_path': 2, 'fast_path_rate': '83.3%'}

Zero Regression Guarantee:
    If the_body fails or isn't available, tools work normally.
    The wrapper falls back to original tool execution.
"""

import sys
import logging
from typing import Any, Callable, Dict, Optional
from pathlib import Path

# Setup logging
logger = logging.getLogger("meeseeks.tool_wrapper")

# Try to import the_body
BODY_AVAILABLE = False
_body = None

try:
    # Add workspace to path for the_body import
    workspace = Path(__file__).parent.parent.parent
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    
    from the_body import TheBody
    _body = TheBody()
    BODY_AVAILABLE = True
    logger.info("the_body loaded successfully - fast path enabled")
except ImportError as e:
    logger.warning(f"the_body not available, using passthrough only: {e}")
except Exception as e:
    logger.warning(f"the_body initialization failed: {e}")


def create_wrapped_tool(tool_name: str, original_tool: Callable) -> Callable:
    """
    Wrap a single tool to go through the_body first.
    
    Args:
        tool_name: Name of the tool (e.g., "read", "exec")
        original_tool: The original tool function
        
    Returns:
        Wrapped tool function that goes through the_body
    
    The wrapper:
    1. Tries the_body.call_tool() first (fast path)
    2. Falls back to original tool if the_body misses or fails
    3. Zero regression: original tool always works
    """
    
    def wrapped_tool(**args) -> Any:
        """Wrapped tool that intercepts through the_body."""
        
        if not BODY_AVAILABLE or _body is None:
            # No the_body - direct passthrough
            return original_tool(**args)
        
        try:
            # Go through the_body for fast-path execution
            return _body.call_tool(
                tool_name=tool_name,
                args=args,
                passthrough_fn=lambda n, a: original_tool(**a)
            )
        except Exception as e:
            # the_body failed - fall back to original
            logger.warning(f"the_body failed for {tool_name}, using passthrough: {e}")
            return original_tool(**args)
    
    # Preserve tool metadata
    wrapped_tool.__name__ = f"wrapped_{tool_name}"
    wrapped_tool.__doc__ = original_tool.__doc__
    wrapped_tool._original_tool = original_tool
    wrapped_tool._wrapped_by_body = True
    
    return wrapped_tool


def wrap_tools(tools_dict: Dict[str, Callable]) -> Dict[str, Callable]:
    """
    Wrap all tools in a dict to go through the_body.
    
    Args:
        tools_dict: Dict mapping tool names to tool functions
                   e.g., {"read": read_fn, "exec": exec_fn}
        
    Returns:
        Dict of wrapped tools with same keys
    
    Example:
        >>> tools = {"read": read_tool, "exec": exec_tool}
        >>> wrapped = wrap_tools(tools)
        >>> result = wrapped["read"](path="file.txt")
        >>> # Goes through the_body first!
    
    Zero Regression:
        If the_body isn't available, returns original tools unchanged.
    """
    
    if not BODY_AVAILABLE:
        logger.info("the_body not available, returning original tools")
        return tools_dict
    
    wrapped = {}
    for name, tool in tools_dict.items():
        wrapped[name] = create_wrapped_tool(name, tool)
    
    logger.info(f"Wrapped {len(wrapped)} tools through the_body")
    return wrapped


def wrap_tool_if_needed(tool_name: str, tool: Callable) -> Callable:
    """
    Conditionally wrap a tool if not already wrapped.
    
    Args:
        tool_name: Name of the tool
        tool: The tool function
        
    Returns:
        Wrapped tool (or original if already wrapped or the_body unavailable)
    """
    
    # Already wrapped?
    if getattr(tool, "_wrapped_by_body", False):
        return tool
    
    # the_body available?
    if not BODY_AVAILABLE:
        return tool
    
    return create_wrapped_tool(tool_name, tool)


def get_body_stats() -> Dict[str, Any]:
    """
    Get the_body performance statistics.
    
    Returns:
        Dict with:
        - calls: Total tool calls
        - fast_path: Calls that hit skill cache
        - slow_path: Calls that passed through
        - fast_path_rate: Percentage of fast path hits
        - cache_stats: Cache statistics
        - distress_signals: Number of distress signals
    
    Returns empty dict if the_body not available.
    """
    
    if not BODY_AVAILABLE or _body is None:
        return {
            "available": False,
            "calls": 0,
            "fast_path": 0,
            "slow_path": 0,
            "fast_path_rate": "0%"
        }
    
    stats = _body.get_stats()
    stats["available"] = True
    return stats


def get_distress_signals() -> list:
    """
    Get any distress signals from the_body.
    
    Distress signals indicate repeated skill failures that may need
    manager (Sloth_rog) intervention.
    
    Returns:
        List of DistressSignal objects (empty if none or the_body unavailable)
    """
    
    if not BODY_AVAILABLE or _body is None:
        return []
    
    return _body.get_distress_signals()


def reset_body_stats() -> None:
    """Reset the_body statistics."""
    
    if BODY_AVAILABLE and _body is not None:
        _body.reset_stats()
        logger.info("the_body stats reset")


def is_body_available() -> bool:
    """Check if the_body is available and initialized."""
    return BODY_AVAILABLE and _body is not None


def get_body_instance() -> Optional[Any]:
    """
    Get the singleton the_body instance.
    
    Returns None if not available.
    Use this for direct access to the_body methods.
    """
    return _body if BODY_AVAILABLE else None


# Convenience: Pre-wrapped common tools (lazy loaded)
_COMMON_TOOLS = None


def get_wrapped_common_tools() -> Dict[str, Callable]:
    """
    Get commonly used tools pre-wrapped through the_body.
    
    This is for Python-based tool usage where tools are called
    directly rather than through OpenClaw's tool surface.
    
    Returns:
        Dict of wrapped tool functions
        
    Note:
        This is for internal Meeseeks Python code.
        OpenClaw-spawned Meeseeks use the platform tool surface.
    """
    global _COMMON_TOOLS
    
    if _COMMON_TOOLS is not None:
        return _COMMON_TOOLS
    
    # Define common tools (these would be imported from actual implementations)
    # For now, return empty dict - tools are provided by OpenClaw platform
    _COMMON_TOOLS = {}
    
    return _COMMON_TOOLS


# CLI for testing
if __name__ == "__main__":
    print("=" * 60)
    print("TOOL WRAPPER - the_body Integration")
    print("=" * 60)
    print()
    
    print(f"the_body available: {BODY_AVAILABLE}")
    print()
    
    if BODY_AVAILABLE:
        print("Stats:")
        stats = get_body_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")
        print()
        
        # Test wrapping
        def dummy_tool(message: str = "hello"):
            return f"Tool executed: {message}"
        
        wrapped = create_wrapped_tool("dummy", dummy_tool)
        result = wrapped(message="test")
        print(f"Wrapped tool test: {result}")
        print()
        
        print("Stats after test:")
        stats = get_body_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")
    else:
        print("the_body not available - tools will passthrough without acceleration")
    
    print()
    print("✅ Tool wrapper ready. Zero regression guaranteed.")
