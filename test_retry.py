#!/usr/bin/env python3
import traceback
import sys
sys.path.insert(0, 'C:/Users/aaron/.openclaw/workspace/skills/meeseeks')

# Test the spawn_retry_chain function
try:
    from auto_retry import spawn_retry_chain
    
    chunks = ['Chunk 1 task', 'Chunk 2 task', 'Chunk 3 task']
    result = spawn_retry_chain('Original task', chunks, 'ancestor-123', 'timeout', 'session-key')
    
    print(f'Success! Got {len(result)} spawn configs')
    for i, cfg in enumerate(result):
        task_preview = cfg.get('task', '')[:50]
        print(f'  {i+1}. {task_preview}...')
except Exception as e:
    traceback.print_exc()
