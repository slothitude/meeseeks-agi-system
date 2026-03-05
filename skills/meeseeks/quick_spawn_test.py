#!/usr/bin/env python3
"""Quick spawn test."""

import sys
sys.path.insert(0, 'C:/Users/aaron/.openclaw/workspace/skills/meeseeks')

from spawn_meeseeks import spawn_prompt

config = spawn_prompt(
    task='Test the AGI system integrations',
    meeseeks_type='coder',
    inherit=True,
    atman=True
)

print('=' * 60)
print('SPAWN CONFIG TEST')
print('=' * 60)
print(f'Task length: {len(config["task"])} chars')
print(f'Thinking: {config.get("thinking")}')
print(f'Timeout: {config.get("timeout")}')
print()
print('Has ATMAN:', 'ATMAN' in config['task'])
print('Has dharma:', 'dharma' in config['task'].lower() or 'wisdom' in config['task'].lower())
print('Has cross-session:', 'Cross-Session' in config['task'])
print()
print('First 500 chars:')
print(config['task'][:500])
