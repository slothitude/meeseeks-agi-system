#!/usr/bin/env python3
import json

# Load the retry chains file
retry_file = 'C:/Users/aaron/.openclaw/workspace/the-crypt/retry_chains.jsonl'

with open(retry_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 3:
            break
        try:
            entry = json.loads(line)
            print(f'Entry {i}:')
            print(f'  status: {entry.get("status")}')
            chunks = entry.get('chunks', [])
            print(f'  chunks type: {type(chunks).__name__}')
            if isinstance(chunks, list):
                print(f'  chunks count: {len(chunks)}')
                if len(chunks) > 0:
                    first_chunk = chunks[0]
                    print(f'  first chunk type: {type(first_chunk).__name__}')
                    if isinstance(first_chunk, dict):
                        print(f'    keys: {list(first_chunk.keys())}')
                        print(f'    status: {first_chunk.get("status")}')
            print()
        except Exception as e:
            print(f'Error on line {i}: {e}')
