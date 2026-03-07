#!/usr/bin/env python3
"""Find upcoming Ladbrokes races."""
import requests
from datetime import datetime, timezone

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

    now = datetime.now(timezone.utc)
    print(f"Current time (UTC): {now.strftime('%H:%M')}")
    print(f"Total meetings: {len(meetings)}")

    upcoming = []

    for m in meetings:
        track = m.get("meeting_name", "Unknown")
        for race in m.get("races", []):
            start_time = race.get("start_time", "")
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    mins = (start_dt - now).total_seconds() / 60

                    if mins > 0:  # Future race
                        upcoming.append({
                            'track': track,
                            'race': race.get('race_number'),
                            'mins': mins,
                            'event_id': race.get('event_id')
                        })
                except:
                    pass

    # Sort by time
    upcoming.sort(key=lambda x: x['mins'])

    print(f"\nUpcoming races: {len(upcoming)}")

    for race in upcoming[:10]:
        print(f"  {race['track']} R{race['race']}: {race['mins']:.1f} mins")

    if not upcoming:
        print("  No upcoming races - day may be over")
else:
    print(f"Error: {r.status_code}")
