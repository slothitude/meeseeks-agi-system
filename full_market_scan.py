#!/usr/bin/env python3
"""Quick scan - what markets are live RIGHT NOW"""
import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings()

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

def login():
    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=payload, cert=CERT_FILE, headers=headers, timeout=15, verify=False)
    if r.status_code == 200:
        data = r.json()
        if data.get('loginStatus') == 'SUCCESS':
            return data.get('sessionToken')
        print(f"Login failed: {data.get('loginStatus')}")
    else:
        print(f"HTTP {r.status_code}")
    return None

def api(token, method, params):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1', headers=headers, json=payload, timeout=10)
    return r.json().get('result') if r.status_code == 200 else None

print("="*60)
print("LIVE MARKET SCAN - ALL SPORTS")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*60)

token = login()
if not token:
    print("Login failed")
    exit()

print("\n[OK] Connected\n")

# Get all event types
event_types = api(token, "SportsAPING/v1.0/listEventTypes", {"filter": {}})

if event_types:
    print("Available sports:\n")
    for et in event_types:
        print(f"  {et['eventType']['id']:>5}: {et['eventType']['name']}")

# Scan each major sport
print("\n" + "="*60)
print("MARKETS NEXT 6 HOURS")
print("="*60)

for event_id, sport_name in [("1", "Horse Racing"), ("2", "Tennis"), ("4", "Cricket"), ("27", "Football")]:
    markets = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
        "filter": {
            "eventTypeIds": [event_id],
            "marketTypeCodes": ["MATCH_ODDS", "WIN"],
            "marketStartTime": {"from": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        },
        "maxResults": 20,
        "marketProjection": ["EVENT", "MARKET_START_TIME"]
    })
    
    if markets:
        print(f"\n{sport_name} ({len(markets)} markets):")
        for m in markets[:5]:
            event = m.get('event', {}).get('eventName', 'Unknown')
            market = m.get('marketName', 'Unknown')
            start = m.get('marketStartTime', '?')
            mid = m.get('marketId', '?')
            print(f"  {event} | {market}")
            print(f"    ID: {mid} | Start: {start}")

# In-play markets
print("\n" + "="*60)
print("IN-PLAY NOW")
print("="*60)

inplay = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
    "filter": {"inPlayOnly": True},
    "maxResults": 50,
    "marketProjection": ["EVENT"]
})

if inplay:
    print(f"\n{len(inplay)} in-play markets:")
    
    # Group by sport
    sports = {}
    for m in inplay:
        sport = m.get('event', {}).get('countryCode', 'Other')
        if sport not in sports:
            sports[sport] = []
        sports[sport].append(m)
    
    for sport, markets in sports.items():
        print(f"\n  {sport}: {len(markets)} markets")
        for m in markets[:3]:
            event = m.get('event', {}).get('eventName', 'Unknown')
            market = m.get('marketName', 'Unknown')
            print(f"    - {event} | {market}")
else:
    print("\nNo in-play markets")

print("\n" + "="*60)
