#!/usr/bin/env python3
"""Check for upcoming races in category T."""
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

    aus = [m for m in meetings if m.get('country') in ['AU', 'AUS']]

    now = datetime.now(timezone.utc)
    upcoming = []

    for m in aus:
        name = m.get('name')
        for race in m.get('races', []):
            status = race.get('status', '')
            start_time = race.get('start_time', '')

            if status != 'Final' and start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    mins = (start_dt - now).total_seconds() / 60

                    if mins > 0:
                        upcoming.append({
                            'track': name,
                            'race': race.get('race_number'),
                            'mins': mins,
                            'status': status
                        })
                except:
                    pass

    print(f"Upcoming races: {len(upcoming)}\n")

    upcoming.sort(key=lambda x: x['mins'])

    for u in upcoming[:20]:
        print(f"  {u['track']} R{u['race']}: {u['mins']:.1f} mins ({u['status']})")

    if not upcoming:
        print("  No upcoming races found")
else:
    print(f"Error: {r.status_code}")
