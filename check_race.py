import json

with open('race_example.json') as f:
    d = json.load(f)

print('Top keys:', list(d.keys()))

if 'data' in d:
    data = d['data']
    print('\nData keys:', list(data.keys()))
    
    if 'runners' in data:
        runners = data['runners']
        print(f'\nRunners found: {len(runners)}')
        
        if runners:
            r = runners[0]
            print(f'\nFirst runner keys: {list(r.keys())}')
            print(f'\nFirst runner odds: {r.get("odds", {})}')
