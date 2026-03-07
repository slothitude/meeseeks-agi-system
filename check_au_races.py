#!/usr/bin/env python3
"""Check for AU meetings."""
import requests

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

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

    au_meetings = [m for m in meetings if m.get('country') == 'AU']

    print(f"Total meetings: {len(meetings)}")
    print(f"AU meetings: {len(au_meetings)}")

    if au_meetings:
        print("\nAU tracks:")
        for m in au_meetings:
            name = m.get('name')
            races = m.get('races', [])
            print(f"  {name}: {len(races)} races")

            for race in races[:2]:
                status = race.get('status')
                start = race.get('start_time', '')[:16]
                print(f"    R{race.get('race_number')}: {status} @ {start}")
    else:
        print("\nNo AU meetings found - day may be over")
else:
    print(f"Error: {r.status_code}")
