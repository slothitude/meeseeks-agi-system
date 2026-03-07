#!/usr/bin/env python3
"""Get actual race results and learn from our bets"""

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
    print("RACE RESULTS - LEARNING FROM OUR BETS")
    print("="*60)
    
    for m in meetings:
        track = m.get('name')
        if track in ['Edenhope', 'Eagle Farm']:
            print(f"\n{track}:")
            
            for race in m.get('races', []):
                race_num = race.get('race_number')
                race_id = race.get('id')
                start_str = race.get('start_time', '').replace('Z', '+00:00')
                
                if start_str:
                    try:
                        start = datetime.fromisoformat(start_str)
                        now = datetime.now(timezone.utc)
                        
                        # If race has started
                        if now > start:
                            # Get race details
                            r2 = requests.get(
                                f'https://api.ladbrokes.com.au/affiliates/v1/racing/events/{race_id}',
                                headers=headers,
                                timeout=15
                            )
                            
                            if r2.status_code == 200:
                                rd = r2.json().get('data', {})
                                runners = rd.get('runners', [])
                                
                                # Find our bets
                                our_runners = []
                                if track == 'Edenhope' and race_num == 3:
                                    our_runners = ['Popthebubbly']
                                elif track == 'Eagle Farm' and race_num == 3:
                                    our_runners = ['Laydownlily']
                                
                                if our_runners:
                                    print(f"\n  R{race_num} (started {start.strftime('%H:%M')} UTC):")
                                    
                                    # Find winner
                                    winner = None
                                    for runner in runners:
                                        if runner.get('result') == 1:
                                            winner = runner.get('name')
                                            print(f"  Winner: {winner}")
                                    
                                    # Check our bets
                                    for our_runner in our_runners:
                                        for runner in runners:
                                            if runner.get('name') == our_runner:
                                                result = runner.get('result', 'N/A')
                                                print(f"  Our bet: {our_runner} - Position: {result}")
                                                
                                                if result == 1:
                                                    print(f"  *** WE WON! ***")
                                                elif result and result > 1:
                                                    print(f"  Placed {result}")
                                                else:
                                                    print(f"  Lost")
                    except:
                        pass
