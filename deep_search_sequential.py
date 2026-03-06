"""Deep search workflow analysis with sequential thinking."""

import asyncio
import sys
sys.path.insert(0, '.')
from skills.meeseeks.mcp_extension import call_mcp


async def deep_analysis():
    thoughts = [
        "THOUGHT 1: Define scope - Deep search workflow includes: MCP integration, spawning, inheritance, karma/RL, retry, entombment. Need to check ALL systems for issues.",
        "THOUGHT 2: Critical paths - Task spawns Meeseeks which inherits wisdom, uses MCP tools, completes, gets entombed, karma observed, dharma updated. Issues could be at ANY step.",
        "THOUGHT 3: Known issues fixed today - Inheritance fallback added, pending spawn processor created, retry limits exist. But are they being USED?",
        "THOUGHT 4: Hidden issues to check - Is karma observation triggered on entombment? Is RL update actually applied? Do Meeseeks actually USE MCP tools?",
        "THOUGHT 5: Testing strategy - After finding issues, spawn test Meeseeks to verify inheritance, MCP usage, entombment, and karma observation."
    ]

    for i, thought in enumerate(thoughts, 1):
        result = await call_mcp('mcp_sequentialthinking_sequentialthinking', {
            'thought': thought,
            'thoughtNumber': i,
            'totalThoughts': len(thoughts),
            'nextThoughtNeeded': i < len(thoughts)
        })
        hist = result.get('thoughtHistoryLength', '?')
        print(f'Thought {i}/{len(thoughts)}: history={hist}')
        print(f'  {thought[:100]}...')
        print()

    return 'Sequential analysis complete'


if __name__ == '__main__':
    result = asyncio.run(deep_analysis())
    print(result)
