#!/usr/bin/env python3
"""Debug Ladbrokes API."""
import requests
import json
from datetime import datetime, timezone

url = "https://api.ladbrokes.com.au/affiliates/v1/racing/"
headers = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

print("Fetching Ladbrokes races...")
response = requests.get(url, headers=headers, timeout=10)

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

if response.status_code == 200:
    data = response.json()
    print(f"Total races: {len(data)}")

    now = datetime.now(timezone.utc)
    print(f"\nCurrent time (UTC): {now.isoformat()}")

    # Show first 5 races
    for i, race in enumerate(data[:5]):
        track = race.get('meeting_name', 'Unknown')
        race_num = race.get('race_number', '?')
        start_time = race.get('start_time', 'Unknown')
        status = race.get('status', 'Unknown')

        if start_time and start_time != 'Unknown':
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                mins = (start_dt - now).total_seconds() / 60
            except:
                mins = 999

            print(f"  {i+1}. {track} R{race_num} | {start_time} | {mins:.1f} mins | {status}")
        else:
            print(f"  {i+1}. {track} R{race_num} | No start time | {status}")

    # Count races in 3-30 min window
    in_window = 0
    for race in data:
        start_time = race.get('start_time')
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                mins = (start_dt - now).total_seconds() / 60
                if 3 <= mins <= 30:
                    in_window += 1
            except:
                pass

    print(f"\nRaces in 3-30 min window: {in_window}")
else:
    print(f"Error: {response.text[:500]}")
