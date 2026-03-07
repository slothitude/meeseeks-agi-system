#!/usr/bin/env python3
"""Debug Ladbrokes API - see raw response."""
import requests
import json

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Get meetings
url = f"{BASE_URL}/racing/meetings"
params = {
    "date_from": "today",
    "date_to": "today",
    "category": "H"
}

r = requests.get(url, headers=HEADERS, params=params, timeout=10)

if r.status_code == 200:
    data = r.json()
    meetings = data.get("data", {}).get("meetings", [])

    print(f"Meetings: {len(meetings)}")

    # Check first meeting structure
    if meetings:
        m = meetings[0]
        print(f"\nFirst meeting keys: {list(m.keys())}")
        print(f"Name: {m.get('name', 'Unknown')}")
        print(f"Country: {m.get('country', 'Unknown')}")

        # Check races
        races = m.get("races", [])
        print(f"Races: {len(races)}")

        if races:
            race = races[0]
            print(f"\nFirst race keys: {list(race.keys())}")
            print(f"Race number: {race.get('race_number')}")
            print(f"Status: {race.get('status')}")

            # Check for event ID
            event_id = race.get('id') or race.get('event_id')
            print(f"Event ID: {event_id}")

            # Try to get event details
            if event_id:
                event_url = f"{BASE_URL}/racing/events/{event_id}"
                event_r = requests.get(event_url, headers=HEADERS, timeout=10)

                if event_r.status_code == 200:
                    event_data = event_r.json()
                    data = event_data.get('data', {})
                    runners = data.get('runners', [])

                    print(f"\nEvent runners: {len(runners)}")

                    if runners:
                        runner = runners[0]
                        print(f"First runner keys: {list(runner.keys())}")
                        print(f"Name: {runner.get('name')}")
                        print(f"Odds: {runner.get('odds')}")
                else:
                    print(f"Event fetch failed: {event_r.status_code}")
else:
    print(f"Error: {r.status_code}")
    print(r.text[:500])
