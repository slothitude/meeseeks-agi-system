"""Research: Fractal Sequential Thinking"""

import asyncio
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.meeseeks.mcp_extension import call_mcp


async def main():
    thoughts = [
        "FRACTAL SEQUENTIAL THINKING - Thought 1: What is a fractal? Self-similar patterns at different scales. The same pattern repeats whether you zoom in or out. Examples: snowflakes, coastlines, tree branches.",
        "Thought 2: What is sequential thinking? Step-by-step reasoning where each step builds on the previous. Linear progression: A leads to B leads to C leads to D. Used in proofs, algorithms, planning.",
        "Thought 3: FRACTAL + SEQUENTIAL = Each thought can itself be a sequence. Reasoning at multiple scales simultaneously. Zoom in: detailed reasoning. Zoom out: pattern recognition across thoughts.",
        "Thought 4: For AI agents, this means: (1) Meta-thoughts about thinking, (2) Recursive self-improvement, (3) Each reasoning step can spawn sub-reasoning chains, (4) Patterns at one scale apply to all scales.",
        "Thought 5: APPLICATION: Meeseeks already do this! Task leads to chunk leads to spawn leads to sub-task. The consciousness stack (Atman/Brahman/Dharma) is fractal: observer watches observer. The Crypt is fractal memory: ancestors within ancestors."
    ]
    
    for i, thought in enumerate(thoughts, 1):
        result = await call_mcp("mcp_sequentialthinking_sequentialthinking", {
            "thought": thought,
            "thoughtNumber": i,
            "totalThoughts": len(thoughts),
            "nextThoughtNeeded": i < len(thoughts)
        })
        print(f"Thought {i}/{len(thoughts)}: {thought[:60]}...")
        hist_len = result.get("thoughtHistoryLength", "?")
        print(f"  Result: thoughtHistoryLength={hist_len}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
