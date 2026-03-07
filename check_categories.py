#!/usr/bin/env python3
"""Check Ladbrokes categories."""
import requests

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Try different categories
categories = ["H", "G", "R", "T", "D"]  # Harness, Greyhounds, Racing, Thoroughbreds, ?

for cat in categories:
    url = f"{BASE_URL}/racing/meetings"
    params = {
        "date_from": "today",
        "date_to": "today",
        "category": cat
    }

    r = requests.get(url, headers=HEADERS, params=params, timeout=10)

    if r.status_code == 200:
        data = r.json()
        meetings = data.get("data", {}).get("meetings", [])

        # Count AU meetings
        au = [m for m in meetings if m.get('country') == 'AUS']

        print(f"\nCategory '{cat}': {len(meetings)} meetings ({len(au)} AUS)")

        if au:
            for m in au[:5]:
                name = m.get('name')
                races = m.get('races', [])
                upcoming = [r for r in races if r.get('status') != 'Final']
                print(f"  {name}: {len(upcoming)} upcoming")
    else:
        print(f"\nCategory '{cat}': Error {r.status_code}")
