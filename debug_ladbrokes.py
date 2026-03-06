#!/usr/bin/env python3
"""Debug Ladbrokes fetcher"""
import requests
import json

HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# Get meetings
r = requests.get('https://api.ladbrokes.com.au/affiliates/v1/racing/meetings?date_from=today&category=H',
                 headers=HEADERS, timeout=10)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    meetings = data['data']['meetings']
    
    print(f"Meetings: {len(meetings)}")
    
    # Find one with runners
    for m in meetings[:3]:
        print(f"\n{m['name']} ({m.get('country')})")
        
        if m.get('races'):
            race = m['races'][0]
            rid = race['id']
            
            print(f"  Race {race.get('race_number')}: {race.get('name')}")
            print(f"  Status: {race.get('status')}")
            
            # Get event
            r2 = requests.get(f'https://api.ladbrokes.com.au/affiliates/v1/racing/events/{rid}',
                             headers=HEADERS, timeout=10)
            
            if r2.status_code == 200:
                edata = r2.json()
                
                if 'data' in edata:
                    d = edata['data']
                    runners = d.get('runners', [])
                    
                    print(f"  Runners found: {len(runners)}")
                    
                    if runners:
                        # Show first 3
                        for runner in runners[:3]:
                            name = runner.get('name', '?')
                            odds = runner.get('odds', {})
                            fixed_win = odds.get('fixed_win', 0)
                            
                            print(f"    {name}: {fixed_win}")
                        
                        # Save full example
                        with open('runner_example.json', 'w') as f:
                            json.dump(runners[0], f, indent=2)
                        print(f"\n  Saved example to runner_example.json")
                    else:
                        print(f"  No runners array")
                        print(f"  Data keys: {list(d.keys())}")
            else:
                print(f"  Event error: {r2.status_code}")
