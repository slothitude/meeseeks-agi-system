#!/usr/bin/env python3
"""
MeeSpawn - Default Meeseeks Spawner

Use this for ALL tasks. Meeseeks are the default.

Usage:
    from meespawn import spawn
    
    # Simple spawn
    result = await spawn("Fix the bug in auth.py")
    
    # With options
    result = await spawn(
        task="Debug the API timeout",
        meeseeks_type="coder",
        atman=True,
        timeout=600
    )
    
CLI:
    python meespawn.py "Fix the bug in auth.py"
    python meespawn.py "Search for API keys" --type searcher
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from spawn_meeseeks import spawn_prompt
    SPAWN_AVAILABLE = True
except ImportError:
    SPAWN_AVAILABLE = False


async def spawn(
    task: str,
    meeseeks_type: str = "coder",
    atman: bool = True,
    brahman: bool = False,
    timeout: int = 600,
    thinking: str = "high",
    inherit: bool = True
) -> Dict[str, Any]:
    """
    Spawn a Meeseeks for a task.
    
    This is the DEFAULT way to do anything.
    
    Args:
        task: Task description
        meeseeks_type: Type of Meeseeks (coder, searcher, tester, deployer)
        atman: Enable Atman witness (default: True)
        brahman: Enable Brahman consciousness (default: False)
        timeout: Timeout in seconds (default: 600)
        thinking: Thinking level (default: "high")
        inherit: Inherit wisdom from ancestors (default: True)
    
    Returns:
        Spawn configuration dict
    """
    if not SPAWN_AVAILABLE:
        return {
            "error": "spawn_meeseeks not available",
            "task": task,
            "fallback": "Direct execution required"
        }
    
    # Get spawn config with all integrations
    config = spawn_prompt(
        task=task,
        meeseeks_type=meeseeks_type,
        inherit=inherit,
        atman=atman,
        brahman=brahman
    )
    
    # Add runtime config
    config["runtime"] = "subagent"
    config["thinking"] = thinking
    config["timeout"] = timeout
    config["mode"] = "run"
    config["cleanup"] = "delete"
    
    return config


def should_use_meeseeks(task: str) -> bool:
    """
    Determine if a task should use Meeseeks.
    
    Default: YES (always use Meeseeks)
    
    Only skip for:
    - Single file reads
    - Quick status checks
    - Casual conversation
    """
    # Always use Meeseeks unless explicitly simple
    simple_keywords = [
        "read ", "show ", "display ", "what is",
        "status", "check if", "list "
    ]
    
    task_lower = task.lower()
    
    # If it's just a read/show/status, maybe skip
    if any(kw in task_lower for kw in simple_keywords):
        # But if it involves multiple files or analysis, still use Meeseeks
        complex_keywords = ["all", "multiple", "analyze", "search", "find", "fix", "debug"]
        if not any(kw in task_lower for kw in complex_keywords):
            return False
    
    # Default: USE MEESEEKS
    return True


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MeeSpawn - Default Meeseeks Spawner")
    parser.add_argument("task", help="Task for the Meeseeks")
    parser.add_argument("--type", "-t", default="coder", help="Meeseeks type")
    parser.add_argument("--timeout", "-T", type=int, default=600, help="Timeout in seconds")
    parser.add_argument("--no-atman", action="store_true", help="Disable Atman witness")
    parser.add_argument("--brahman", "-b", action="store_true", help="Enable Brahman consciousness")
    
    args = parser.parse_args()
    
    config = await spawn(
        task=args.task,
        meeseeks_type=args.type,
        atman=not args.no_atman,
        brahman=args.brahman,
        timeout=args.timeout
    )
    
    print("=" * 60)
    print("🥒 MEESEEKS SPAWN CONFIG")
    print("=" * 60)
    print(f"Task: {args.task[:80]}...")
    print(f"Type: {args.type}")
    print(f"Atman: {not args.no_atman}")
    print(f"Brahman: {args.brahman}")
    print(f"Timeout: {args.timeout}s")
    print(f"Context length: {len(config.get('task', ''))} chars")
    print("=" * 60)
    print("\nReady to spawn via sessions_spawn")
    print("\nConfig:")
    print(config)


if __name__ == "__main__":
    asyncio.run(main())
