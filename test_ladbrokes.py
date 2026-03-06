#!/usr/bin/env python3
"""Test Ladbrokes API structure"""
import requests
import json

HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

print("Fetching meetings...")
r = requests.get('https://api.ladbrokes.com.au/affiliates/v1/racing/meetings?date_from=today&category=H',
                 headers=HEADERS, timeout=10)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    
    # Save
    with open('ladbrokes_response.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Saved to ladbrokes_response.json")
    
    # Show structure
    print(f"\nTop keys: {list(data.keys())}")
    
    if 'data' in data:
        d = data['data']
        print(f"Data keys: {list(d.keys())}")
        
        meetings = d.get('meetings', [])
        print(f"\nMeetings: {len(meetings)}")
        
        if meetings:
            m = meetings[0]
            print(f"\nFirst meeting keys: {list(m.keys())}")
            print(f"\nFirst meeting sample:")
            print(json.dumps(m, indent=2)[:600])
else:
    print(f"Error: {r.text[:500]}")
