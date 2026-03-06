#!/usr/bin/env python3
"""Quick price check - show actual prices"""
import requests
import json
from datetime import datetime
import urllib3

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
    return None

def api(token, method, params):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                     headers=headers, json=payload, timeout=10)
    return r.json().get('result') if r.status_code == 200 else None

print("="*70)
print("LIVE TENNIS PRICES")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*60)

token = login()
if not token:
    print("Login failed")
    exit()

# Get tennis markets
markets = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
    "filter": {
        "eventTypeIds": ["2"],
        "marketTypeCodes": ["MATCH_ODDS"],
        "marketStartTime": {"from": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
    },
    "maxResults": 20,
    "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
})

if not markets:
    print("No markets")
    exit()

print(f"\nFound {len(markets)} tennis markets\n")

for m in markets:
    mid = m.get('marketId')
    event = m.get('event', {}).get('eventName', 'Unknown')
    start = m.get('marketStartTime')
    
    # Get prices
    book = api(token, "SportsAPING/v1.0/listMarketBook", {
        "marketIds": [mid],
        "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
    })
    
    if not book or not book[0] or book[0].get('status') != 'OPEN':
        continue
    
    book = book[0]
    
    # Time to start
    time_to_start = "?"
    if start:
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            time_to_start = f"{(start_dt - datetime.now(start_dt.tzinfo)).total_seconds() / 60:.0f}min"
        except:
            pass
    
    print(f"\n{event} ({time_to_start})")
    print("-" * 50)
    
    for runner in m.get('runners', []):
        rid = runner.get('selectionId')
        rname = runner.get('runnerName', 'Unknown')
        
        ex = None
        for r in book.get('runners', []):
            if r.get('selectionId') == rid:
                ex = r.get('ex', {})
                break
        
        if not ex:
            continue
        
        back = ex.get('availableToBack', [])
        lay = ex.get('availableToLay', [])
        
        if not back or not lay:
            continue
        
        bp = back[0]['price']
        lp = lay[0]['price']
        bs = back[0]['size']
        ls = lay[0]['size']
        
        spread = lp - bp
        
        print(f"  {rname}")
        print(f"    BACK {bp:.2f} (${bs:.0f}) | LAY {lp:.2f} (${ls:.0f}) | Spr {spread:.2f}")
