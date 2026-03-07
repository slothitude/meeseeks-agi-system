#!/usr/bin/env python3
"""Debug the fetcher logic step by step."""
import requests
import time

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
    "category": "T"
}

r = requests.get(url, headers=HEADERS, params=params, timeout=10)
data = r.json()
meetings = data.get("data", {}).get("meetings", [])

print(f"Total meetings: {len(meetings)}")

# Filter for AUS
aus_meetings = [m for m in meetings if m.get('country') in ['AU', 'AUS']]
print(f"AUS meetings: {len(aus_meetings)}")

all_runners = []

for meeting in aus_meetings[:5]:  # Just first 5 for testing
    name = meeting.get('name')
    country = meeting.get('country')
    races = meeting.get('races', [])

    print(f"\n{name} ({country}): {len(races)} races")

    for race in races[:3]:  # Just first 3 races
        event_id = race.get('id')
        race_number = race.get('race_number')
        status = race.get('status')

        print(f"  R{race_number} ({status})...", end=' ')

        # Get event data
        event_url = f"{BASE_URL}/racing/events/{event_id}"
        event_r = requests.get(event_url, headers=HEADERS, timeout=10)

        if event_r.status_code != 200:
            print(f"ERROR {event_r.status_code}")
            continue

        event_data = event_r.json()
        runners = event_data.get('data', {}).get('runners', [])

        if not runners:
            print("NO RUNNERS")
            continue

        # Count runners with odds
        with_odds = 0
        for runner in runners:
            odds = runner.get('odds', {})
            fixed_win = odds.get('fixed_win', 0)

            if not runner.get('is_scratched') and fixed_win:
                with_odds += 1
                all_runners.append({
                    'name': runner.get('name'),
                    'fixed_win': fixed_win,
                    'track': name,
                    'race': race_number
                })

        print(f"{with_odds}/{len(runners)} with odds")

        time.sleep(0.15)

print(f"\n\nTotal runners collected: {len(all_runners)}")
if all_runners:
    print(f"First 5:")
    for r in all_runners[:5]:
        print(f"  {r['name']} @ {r['fixed_win']} ({r['track']} R{r['race']})")
