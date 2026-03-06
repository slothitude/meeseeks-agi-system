#!/usr/bin/env python3
"""Full debug - see what's in event data"""
import requests
import json

HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# Get one event
event_id = "bf1ba411-457b-4e1e-8c61-aac2b1437bec"  # From earlier debug

r = requests.get(f'https://api.ladbrokes.com.au/affiliates/v1/racing/events/{event_id}',
                 headers=HEADERS, timeout=10)

if r.status_code == 200:
    data = r.json()
    
    print("Event keys:", list(data.keys()))
    
    if 'data' in data:
        d = data['data']
        print("\nData keys:", list(d.keys()))
        
        if 'runners' in d:
            runners = d['runners']
            print(f"\nRunners: {len(runners)}")
            
            if runners:
                r = runners[0]
                print(f"\nFirst runner keys: {list(r.keys())}")
                print(f"\nOdds: {r.get('odds')}")
                print(f"\nIs scratched: {r.get('is_scratched')}")
        else:
            print("\nNo runners key")
    
    # Save full structure
    with open('event_structure.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\nSaved full structure to event_structure.json")
