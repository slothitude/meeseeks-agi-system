#!/usr/bin/env python3
"""Debug category T meetings."""
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Get category T meetings
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

    print(f"Category T meetings: {len(meetings)}\n")

    # Show AUS meetings
    aus = [m for m in meetings if m.get('country') in ['AU', 'AUS']]

    print(f"AUS meetings: {len(aus)}\n")

    for m in aus[:5]:
        name = m.get('name')
        country = m.get('country')
        races = m.get('races', [])

        print(f"{name} ({country}): {len(races)} races")

        if races:
            race = races[0]
            print(f"  R{race.get('race_number')}: status={race.get('status')}")
            print(f"  Keys: {list(race.keys())}")

            # Try to get event data
            event_id = race.get('id')
            if event_id:
                event_url = f"{BASE_URL}/racing/events/{event_id}"
                event_r = requests.get(event_url, headers=HEADERS, timeout=10)

                if event_r.status_code == 200:
                    event_data = event_r.json()
                    print(f"  Event keys: {list(event_data.keys())}")

                    if 'data' in event_data:
                        data_keys = list(event_data['data'].keys())
                        print(f"  Data keys: {data_keys[:10]}")
                else:
                    print(f"  Event error: {event_r.status_code}")
else:
    print(f"Error: {r.status_code}")
