#!/usr/bin/env python3
"""Fetch a specific race with runner odds"""
import requests
import json

HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# Get meetings
r = requests.get('https://api.ladbrokes.com.au/affiliates/v1/racing/meetings?date_from=today&category=H',
                 headers=HEADERS, timeout=10)

data = r.json()
meetings = data['data']['meetings']

print(f"Found {len(meetings)} meetings")

# Use first meeting
if meetings:
    m = meetings[0]
    mid = m['meeting']
    name = m['name']
    
    print(f"\n{name} ({m.get('country')})")
    
    # Get first race
    if m.get('races'):
        race = m['races'][0]
        rid = race['id']
        
        print(f"  Race {race.get('race_number')}: {race.get('name')}")
        print(f"  Start: {race.get('start_time')}")
        print(f"  Status: {race.get('status')}")
        
        # Fetch full event details
        r2 = requests.get(f'https://api.ladbrokes.com.au/affiliates/v1/racing/events/{rid}',
                         headers=HEADERS, timeout=10)
        
        if r2.status_code == 200:
            event_data = r2.json()
            
            # Save
            with open('race_example.json', 'w') as f:
                json.dump(event_data, f, indent=2)
            
            print(f"\n  Saved full race to race_example.json")
            
            # Show structure
            if 'data' in event_data:
                d = event_data['data']
                print(f"\n  Event data keys: {list(d.keys())}")
                
                if 'runners' in d:
                    runners = d['runners']
                    print(f"  Runners: {len(runners)}")
                    
                    if runners:
                        print(f"\n  First runner keys: {list(runners[0].keys())}")
                        print(f"\n  First runner sample:")
                        print(json.dumps(runners[0], indent=2)[:800])
        else:
            print(f"  Event error: {r2.status_code}")
