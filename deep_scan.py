#!/usr/bin/env python3
"""Deep market scan - show ALL available markets"""
import requests
import json
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings()

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

def login():
    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', 
                     data=payload, cert=CERT_FILE, headers=headers, timeout=15, verify=False)
    if r.status_code == 200:
        data = r.json()
        if data.get('loginStatus') == 'SUCCESS':
            return data.get('sessionToken')
    print(f"Login failed: {r.status_code}")
    return None

def api(token, method, params):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    try:
        r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                         headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get('result')
        print(f"API error: {r.status_code}")
    except Exception as e:
        print(f"API exception: {e}")
    return None

print("="*70)
print("DEEP MARKET SCAN")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*70)

token = login()
if not token:
    exit()

print("\n[OK] Connected\n")

# Get all event types
event_types = api(token, "SportsAPING/v1.0/listEventTypes", {"filter": {}})

if not event_types:
    print("No event types found")
    exit()

print("SPORTS AVAILABLE:")
print("-"*70)
for et in event_types:
    print(f"  {et['eventType']['id']:>10}: {et['eventType']['name']}")

# Scan each major sport WITHOUT time filter
print("\n" + "="*70)
print("ALL MARKETS (No time filter)")
print("="*70)

for et in event_types[:20]:  # First 20 sports
    event_id = et['eventType']['id']
    sport_name = et['eventType']['name']
    
    # Get markets without time filter
    markets = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
        "filter": {
            "eventTypeIds": [event_id]
        },
        "maxResults": 20,
        "marketProjection": ["EVENT", "MARKET_START_TIME"]
    })
    
    if markets and len(markets) > 0:
        print(f"\n{sport_name} ({len(markets)} markets):")
        
        for m in markets[:5]:
            event = m.get('event', {}).get('eventName', 'Unknown')
            market = m.get('marketName', 'Unknown')
            start = m.get('marketStartTime', '?')
            mid = m.get('marketId', '?')
            
            # Parse time
            if start and start != '?':
                try:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    local_time = dt.astimezone().strftime('%m/%d %H:%M')
                except:
                    local_time = '?'
            else:
                local_time = '?'
            
            print(f"  {local_time} | {event} | {market}")

# In-play markets
print("\n" + "="*70)
print("IN-PLAY MARKETS")
print("="*70)

inplay = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
    "filter": {"inPlayOnly": True},
    "maxResults": 100,
    "marketProjection": ["EVENT", "MARKET_TYPE"]
})

if inplay:
    print(f"\n{len(inplay)} in-play markets:")
    
    # Group by event
    events = {}
    for m in inplay:
        event_name = m.get('event', {}).get('eventName', 'Unknown')
        country = m.get('event', {}).get('countryCode', '?')
        key = f"{country}: {event_name}"
        if key not in events:
            events[key] = []
        events[key].append(m)
    
    for event_key, event_markets in list(events.items())[:15]:
        market_types = [m.get('marketName', '?') for m in event_markets[:3]]
        print(f"\n  {event_key} ({len(event_markets)} markets)")
        for mt in market_types:
            print(f"    - {mt}")

print("\n" + "="*70)
