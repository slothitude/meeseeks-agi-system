#!/usr/bin/env python3
"""Test Ladbrokes API v2."""
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Get meetings
print("Fetching meetings...")
url = f"{BASE_URL}/racing/meetings"
params = {
    "date_from": "today",
    "date_to": "today",
    "category": "H"  # Horse racing
}

r = requests.get(url, headers=HEADERS, params=params, timeout=10)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    meetings = data.get("data", {}).get("meetings", [])
    print(f"Meetings: {len(meetings)}")

    now = datetime.now(timezone.utc)

    for m in meetings[:3]:
        track = m.get("meeting_name", "Unknown")
        races = m.get("races", [])
        print(f"\n{track}: {len(races)} races")

        for race in races[:2]:
            race_num = race.get("race_number", "?")
            event_id = race.get("event_id", "")
            start_time = race.get("start_time", "")

            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    mins = (start_dt - now).total_seconds() / 60
                except:
                    mins = 999

                print(f"  R{race_num}: {mins:.1f} mins | event_id: {event_id}")
else:
    print(f"Error: {r.text[:200]}")
