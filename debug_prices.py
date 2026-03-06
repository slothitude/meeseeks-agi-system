#!/usr/bin/env python3
"""Debug price fetching"""
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
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                     headers=headers, json=payload, timeout=15)
    return r.json().get('result') if r.status_code == 200 else None

token = login()
if not token:
    exit()

print(f"[OK] Logged in\n")

# Get horse racing markets
print("Getting horse racing markets...")
markets = api(token, "SportsAPING/v1.0/listMarketCatalogue", {
    "filter": {"eventTypeIds": ["7"]},
    "maxResults": 5,
    "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
})

if not markets:
    print("No markets found")
    exit()

print(f"Found {len(markets)} markets\n")

for i, m in enumerate(markets):
    mid = m.get('marketId')
    event = m.get('event', {}).get('eventName', 'Unknown')
    market_name = m.get('marketName', 'Unknown')
    start = m.get('marketStartTime', '?')
    
    print(f"{i+1}. {event} - {market_name}")
    print(f"   ID: {mid}")
    print(f"   Start: {start}")
    print(f"   Runners: {len(m.get('runners', []))}")
    
    # Get prices
    print(f"   Fetching prices...")
    book = api(token, "SportsAPING/v1.0/listMarketBook", {
        "marketIds": [mid],
        "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
    })
    
    if not book or not book[0]:
        print(f"   ❌ No book data")
        print()
        continue
    
    book = book[0]
    print(f"   Status: {book.get('status')}")
    print(f"   Total runners: {len(book.get('runners', []))}")
    
    # Show first 3 runners with prices
    for j, runner in enumerate(book.get('runners', [])[:3]):
        rid = runner.get('selectionId')
        status = runner.get('status')
        ex = runner.get('ex', {})
        
        back = ex.get('availableToBack', [])
        lay = ex.get('availableToLay', [])
        
        # Find runner name
        rname = "Unknown"
        for r in m.get('runners', []):
            if r.get('selectionId') == rid:
                rname = r.get('runnerName', 'Unknown')
                break
        
        if back and lay:
            print(f"     {j+1}. {rname}: BACK {back[0]['price']:.2f} | LAY {lay[0]['price']:.2f}")
        else:
            print(f"     {j+1}. {rname}: No prices (status={status})")
    
    print()

print("\n" + "="*70)
print("Testing with multiple market IDs at once...")
print("="*70)

market_ids = [m['marketId'] for m in markets[:3]]
print(f"Requesting {len(market_ids)} markets...")

books = api(token, "SportsAPING/v1.0/listMarketBook", {
    "marketIds": market_ids,
    "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
})

if books:
    print(f"Got {len(books)} books")
    for book in books:
        mid = book.get('marketId')
        status = book.get('status')
        runners_with_prices = sum(1 for r in book.get('runners', []) 
                                  if r.get('ex', {}).get('availableToBack'))
        print(f"  {mid}: {status}, {runners_with_prices} runners with prices")
else:
    print("No books returned")
