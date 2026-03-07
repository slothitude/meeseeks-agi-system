#!/usr/bin/env python3
"""Check race times and current status"""

import requests
from datetime import datetime, timezone

headers = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# Get meetings
r = requests.get(
    'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
    headers=headers,
    timeout=15
)

if r.status_code == 200:
    data = r.json()
    meetings = data.get('data', {}).get('meetings', [])
    
    print("="*60)
    print("RACE STATUS CHECK")
    print(f"Current time: {datetime.now(timezone.utc).strftime('%H:%M')} UTC")
    print("="*60)
    
    for m in meetings:
        track = m.get('name')
        if track in ['Edenhope', 'Eagle Farm']:
            print(f"\n{track}:")
            
            for race in m.get('races', []):
                race_num = race.get('race_number')
                start_str = race.get('start_time', '').replace('Z', '+00:00')
                
                if start_str:
                    try:
                        start = datetime.fromisoformat(start_str)
                        now = datetime.now(timezone.utc)
                        
                        diff = (start - now).total_seconds() / 60
                        
                        if diff > 0:
                            print(f"  R{race_num}: Starts in {diff:.1f} mins ({start.strftime('%H:%M')} UTC)")
                        else:
                            print(f"  R{race_num}: Started {abs(diff):.1f} mins ago ({start.strftime('%H:%M')} UTC)")
                    except:
                        pass
