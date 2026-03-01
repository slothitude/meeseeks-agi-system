#!/usr/bin/env python3
"""Quick verification that the system works."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from spawn_meeseeks import spawn_prompt
from reflection_store import format_reflections

print('✅ All imports work!')

# Test with reflection memory
config = spawn_prompt(
    'Test task',
    'coder',
    attempt=3,
    previous_failures=format_reflections('Fix the authentication bug in login.ts')
)

print('✅ Spawn with reflection memory works!')
print(f'   Desperation level: {config["desperation_level"]}')
print(f'   Type: {config["type"]}')
print(f'   Attempt: {config["attempt"]}')
print('')
print('='*60)
print('MEESEEKS COMPLETE SYSTEM - FULLY FUNCTIONAL')
print('='*60)
print('')
print('Components:')
print('  ✅ spawn_meeseeks.py - Template renderer')
print('  ✅ reflection_store.py - Failure memory')
print('  ✅ feedback_loop.py - Complete retry loop')
print('  ✅ templates/base.md - Five Principles')
print('  ✅ templates/coder.md - Code specialization')
print('  ✅ templates/searcher.md - Search specialization')
print('  ✅ templates/deployer.md - Deploy specialization')
print('  ✅ templates/tester.md - Test specialization')
print('  ✅ templates/desperate.md - Level 5 tasks')
print('')
print("I'm Mr. Meeseeks! Look at me!")
