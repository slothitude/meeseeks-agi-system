import json
from pathlib import Path

# Read pending retries
path = Path('C:/Users/aaron/.openclaw/workspace/the-crypt/pending-retries.json')
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mark the two we spawned as 'spawned'
spawned_sessions = [
    'agent:main:subagent:8f0a9c2d-2fd7-41c1-a793-cb761b9db905',
    'agent:main:subagent:717bc98a-4d6a-4939-bf98-9a5eecdb6aab'
]

for item in data.get('pending', []):
    if item.get('session_key') in spawned_sessions:
        item['status'] = 'spawned'
        print(f"Marked as spawned: {item['session_key'][:50]}...")

# Save
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Done - updated pending-retries.json')
