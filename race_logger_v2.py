#!/usr/bin/env python3
"""
Race Logger - Fixed Version
Logs top 4 horses every 5 seconds for races < 15 mins away
"""

import requests
import csv
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUTPUT_CSV = Path("race_prices_clean.csv")

headers = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

print("="*60)
print("RACE LOGGER v2 - Clean Output")
print(f"Started: {datetime.now()}")
print("="*60)
print()

while True:
    try:
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(minutes=15)

        # Get meetings
        r = requests.get(
            'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
            headers=headers,
            timeout=15
        )

        if r.status_code != 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP {r.status_code}")
            time.sleep(60)
            continue

        data = r.json()
        meetings = data.get('data', {}).get('meetings', [])
        au = [m for m in meetings if m.get('country') == 'AUS' and m.get('category') == 'T']

        # Find races < 15 mins
        upcoming = []
        for m in au:
            name = m.get('name')
            for race in m.get('races', []):
                race_id = race.get('id')
                race_number = race.get('race_number')
                start_str = race.get('start_time', '').replace('Z', '+00:00')
                
                if start_str:
                    try:
                        start = datetime.fromisoformat(start_str)
                        if now < start <= cutoff:
                            mins = (start - now).total_seconds() / 60
                            upcoming.append({
                                'meeting': name,
                                'race_id': race_id,
                                'race': race_number,
                                'mins': round(mins, 1)
                            })
                    except:
                        pass

        print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(upcoming)} races < 15 mins")

        if not upcoming:
            time.sleep(60)
            continue

        # Log each race
        rows = []
        for race_info in upcoming:
            # Get race details
            r2 = requests.get(
                f"https://api.ladbrokes.com.au/affiliates/v1/racing/events/{race_info['race_id']}",
                headers=headers,
                timeout=15
            )

            if r2.status_code != 200:
                continue

            rd = r2.json()
            data_obj = rd.get('data', {})
            runners = data_obj.get('runners', [])

            if not runners:
                continue

            # Sort by fixed win price
            sorted_runners = sorted(
                runners,
                key=lambda x: x.get('odds', {}).get('fixed_win', 999)
            )

            # Top 4 only
            for rank, runner in enumerate(sorted_runners[:4], 1):
                name = runner.get('name', '')
                if not name:
                    continue
                    
                odds = runner.get('odds', {})
                fixed_win = odds.get('fixed_win', 0)
                fixed_place = odds.get('fixed_place', 0)
                
                # Get flucs
                flucs = runner.get('flucs', [])
                open_price = flucs[0] if flucs else fixed_win
                
                # Calculate price change
                if open_price and open_price > 0:
                    price_change = round((fixed_win - open_price) / open_price * 100, 1)
                else:
                    price_change = 0.0
                
                # Build row with explicit field order
                row = [
                    datetime.now().isoformat(),
                    race_info['meeting'],
                    str(race_info['race']),
                    str(race_info['mins']),
                    str(rank),
                    name,
                    str(fixed_win),
                    str(fixed_place),
                    str(open_price),
                    str(price_change)
                ]
                rows.append(row)

            print(f"  {race_info['meeting']} R{race_info['race']}: {len(runners)} runners")

        # Write to CSV (append mode)
        if rows:
            file_exists = OUTPUT_CSV.exists()
            
            with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header if new file
                if not file_exists:
                    writer.writerow([
                        'timestamp',
                        'track',
                        'race',
                        'mins_to_start',
                        'rank',
                        'runner',
                        'win',
                        'place',
                        'open',
                        'change_pct'
                    ])
                
                # Write rows
                for row in rows:
                    writer.writerow(row)

            print(f"  Logged {len(rows)} rows")

        # Wait 5 seconds
        time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nStopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
