#!/usr/bin/env python3
"""Check runner odds structure for category T."""
import requests

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Get a race from category T
url = f"{BASE_URL}/racing/meetings"
params = {
    "date_from": "today",
    "date_to": "today",
    "category": "T"
}

r = requests.get(url, headers=HEADERS, params=params, timeout=10)

if r.status_code == 200:
    data = r.json()
    meetings = data.get("data", {}).get("meetings", [])

    # Find first AU meeting with upcoming race
    for m in meetings:
        if m.get('country') not in ['AU', 'AUS']:
            continue

        for race in m.get('races', []):
            if race.get('status') == 'Open':
                event_id = race.get('id')
                track = m.get('name')
                race_num = race.get('race_number')

                print(f"{track} R{race_num}\n")

                # Get event data
                event_url = f"{BASE_URL}/racing/events/{event_id}"
                event_r = requests.get(event_url, headers=HEADERS, timeout=10)

                if event_r.status_code == 200:
                    event_data = event_r.json()
                    runners = event_data.get('data', {}).get('runners', [])

                    print(f"Runners: {len(runners)}\n")

                    if runners:
                        # Check first runner
                        runner = runners[0]
                        print(f"Runner keys: {list(runner.keys())[:20]}")
                        print(f"\nName: {runner.get('name')}")
                        print(f"Odds: {runner.get('odds')}")

                        # Check if odds exist
                        odds = runner.get('odds', {})
                        print(f"\nOdds keys: {list(odds.keys()) if odds else 'None'}")
                        print(f"fixed_win: {odds.get('fixed_win', 'NOT FOUND')}")
                        print(f"fixed_place: {odds.get('fixed_place', 'NOT FOUND')}")

                break
        break
else:
    print(f"Error: {r.status_code}")
