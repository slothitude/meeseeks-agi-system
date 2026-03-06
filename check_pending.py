"""Process pending retry chunks."""

import json
from pathlib import Path

pending_path = Path('the-crypt/pending-spawns.json')

with open(pending_path) as f:
    data = json.load(f)

print(f'Found {len(data["pending"])} pending chunks')

for p in data['pending']:
    retry_num = p.get('_retry_number', 0)
    chunk_idx = p['_retry_meta']['chunk_index']
    total = p['_retry_meta']['total_chunks']
    print(f'  Chunk {chunk_idx+1}/{total} - retry #{retry_num}')
