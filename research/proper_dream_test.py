#!/usr/bin/env python3
"""
Proper Dream v2 Effectiveness Test
==================================

Task must be:
- Complex enough that workflow helps
- Measurable (right/wrong answer)
- Repeatable

Test: Parse a file and extract specific pattern counts
- Without wisdom: worker figures out approach alone
- With workflow: worker gets 5-step checklist

Measure: Correctness, time, approach quality
"""

# The task - complex enough to benefit from structure
TASK = """
Analyze the file the-crypt/dharma.md and answer these 3 questions:
1. How many principles are listed (numbered items)?
2. How many times does the word "chunk" appear?
3. What is the last principle number?

Answer in format: principles:N, chunk:N, last:N
"""

WORKFLOW = """
## Workflow for analyze tasks
  1. Read the file completely first
  2. Identify what patterns you're counting
  3. Use systematic counting (don't guess)
  4. Verify each count separately
  5. Report in exact format requested
(Based on 5 successful examples)
"""

# Expected answers (pre-calculated)
EXPECTED = {
    "principles": 26,  # Will need to verify
    "chunk": None,     # Will count
    "last": 26
}

print("=" * 60)
print("PROPER DREAM V2 TEST")
print("=" * 60)
print()
print("Task: Multi-part analysis of dharma.md")
print("Format: principles:N, chunk:N, last:N")
print()
print("Spawning 4 workers:")
print("  - 2 WITHOUT workflow (control)")
print("  - 2 WITH workflow (treatment)")
print()
print("Run this manually with the spawns below...")
print()

# Generate the spawn commands
print("WORKER 1 (no workflow):")
print(f'  Task: {TASK.strip()}')
print()

print("WORKER 2 (with workflow):")
print(f'  Task: {TASK.strip()}\n{WORKFLOW}')
print()
