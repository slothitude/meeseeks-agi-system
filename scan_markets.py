#!/usr/bin/env python3
"""Quick market scanner - find what's available now"""

import requests
import json
from datetime import datetime, timedelta

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Event type IDs
EVENT_TYPES = {
    "1": "Horse Racing",
    "2": "Tennis",
    "4": "Cricket",
    "5": "Rugby Union",
    "6": "Boxing",
    "7": "Golf",
    "8": "Motor Sport",
    "10": "Basketball",
    "11": "American Football",
    "14": "Baseball",
    "15": "Ice Hockey",
    "16": "Darts",
    "17": "Badminton",
    "18": "Snooker",
    "19": "Volleyball",
    "20": "Handball",
    "21": "Cycling",
    "22": "Mixed Martial Arts",
    "23": "Esports",
    "24": "Gaelic Games",
    "25": "Australian Rules",
    "26": "Greyhounds",
    "27": "Football",
    "1477": "Rugby League"
}

def login():
    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {
        'X-Application': APP_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    r = requests.post(
        'https://identitysso-cert.betfair.com/api/certlogin',
        data=payload,
        cert=CERT_FILE,
        headers=headers,
        timeout=15
    )
    
    if r.status_code == 200:
        data = r.json()
        if data.get('loginStatus') == 'SUCCESS':
            return data.get('sessionToken')
    return None

def get_live_markets(session_token, event_type_id, event_type_name):
    """Get live markets for an event type"""
    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }
    
    now = datetime.now()
    soon = now + timedelta(hours=2)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": [event_type_id],
                "marketStartTime": {
                    "from": now.isoformat() + "Z",
                    "to": soon.isoformat() + "Z"
                }
            },
            "maxResults": 5,
            "marketProjection": ["EVENT"]
        },
        "id": 1
    }
    
    try:
        r = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if r.status_code == 200:
            result = r.json().get('result', [])
            if result:
                return result
    except:
        pass
    return []

def main():
    print("="*70)
    print("BETFAIR LIVE MARKET SCANNER")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    print()
    
    token = login()
    if not token:
        print("Login failed")
        return
    
    print("Logged in. Scanning event types...\n")
    
    found = []
    
    for event_id, event_name in EVENT_TYPES.items():
        markets = get_live_markets(token, event_id, event_name)
        if markets:
            print(f"{event_name}: {len(markets)} markets")
            for m in markets[:2]:
                event = m.get('event', {})
                print(f"  - {event.get('eventName', 'Unknown')}")
                print(f"    Market: {m.get('marketName', 'Unknown')}")
                print(f"    Start: {m.get('marketStartTime', 'Unknown')}")
            found.append((event_name, len(markets)))
    
    if not found:
        print("\nNo markets found in any sport for next 2 hours")
        print("\nNote: It's late night in Australia - markets may be limited")
    else:
        print(f"\n{'='*70}")
        print(f"Total: {sum(m[1] for m in found)} markets across {len(found)} sports")
        print("="*70)

if __name__ == "__main__":
    main()
