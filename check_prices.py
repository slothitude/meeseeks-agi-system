#!/usr/bin/env python3
"""Quick price check - what's available now"""
import requests
import json
from datetime import datetime, timedelta

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

def login():
    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=payload, cert=CERT_FILE, headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        if data.get('loginStatus') == 'SUCCESS':
            return data.get('sessionToken')
    return None

def get_markets(token):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    now = datetime.now()
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["2"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {"from": now.isoformat() + "Z"}
            },
            "maxResults": 10,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
        },
        "id": 1
    }
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1', headers=headers, json=payload, timeout=10)
    if r.status_code == 200:
        return r.json().get('result', [])
    return []

def get_prices(token, market_id):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {"marketIds": [market_id], "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}},
        "id": 1
    }
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1', headers=headers, json=payload, timeout=10)
    if r.status_code == 200:
        result = r.json().get('result', [])
        return result[0] if result else None
    return None

print("="*70)
print("TENNIS PRICE CHECK")
print("="*70)

token = login()
if not token:
    print("Login failed")
    exit()

markets = get_markets(token)
print(f"\nFound {len(markets)} tennis markets\n")

for m in markets[:5]:
    mid = m.get('marketId')
    event = m.get('event', {}).get('eventName', 'Unknown')
    print(f"\n{event}")
    
    book = get_prices(token, mid)
    if not book:
        continue
    
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
        
        if back and lay:
            bp = back[0]['price']
            bs = back[0]['size']
            lp = lay[0]['price']
            ls = lay[0]['size']
            spread = lp - bp
            
            print(f"  {rname}: BACK {bp:.2f} (${bs:.0f}) | LAY {lp:.2f} (${ls:.0f}) | Spread: {spread:.2f}")
