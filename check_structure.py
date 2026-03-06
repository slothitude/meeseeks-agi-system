import json

with open('event_structure.json') as f:
    d = json.load(f)

print('Top keys:', list(d.keys()))
print('\nData keys:', list(d.get('data', {}).keys())

# Check if runners is different places
data = d.get('data', {})
if 'runners' not in data:
    print('\nNo "runners" in data')
    print('\nLooking for runner data in other keys...')
    for k, v in data.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            print(f'  {k}: {len(v)} items')
            if v and 'name' in v[0]:
                print(f'    Sample keys: {list(v[0].keys())}')
