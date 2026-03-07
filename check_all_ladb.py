#!/usr/bin/env python3
"""Check all Ladbrokes meetings - AU and others."""
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games"
}

# Get meetings for today
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

    print(f"Total meetings: {len(meetings)}\n")

    # Group by country
    by_country = {}
    for m in meetings:
        country = m.get('country', 'Unknown')
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(m)

    for country, country_meetings in sorted(by_country.items()):
        print(f"{country}: {len(country_meetings)} meetings")
        for m in country_meetings[:3]:
            name = m.get('name')
            races = m.get('races', [])
            upcoming = [r for r in races if r.get('status') != 'Final']
            print(f"  {name}: {len(upcoming)} upcoming races")

    # Check for AU specifically
    au = [m for m in meetings if m.get('country') == 'AU']
    print(f"\n\nAU meetings: {len(au)}")

    if not au:
        # Maybe AU is under a different code?
        print("\nChecking all meeting countries:")
        for m in meetings:
            name = m.get('name', '')
            country = m.get('country', '')
            state = m.get('state', '')
            print(f"  {name}: {country}/{state}")
else:
    print(f"Error: {r.status_code}")
