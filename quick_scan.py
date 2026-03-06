#!/usr/bin/env python3
"""Quick scan - all markets with prices"""
import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings()

USERNAME = 'dnfarnot@gmail.com'
PASSWORD = 'Tobiano01'
APP_KEY = 'XmZEwtLsIRkf5lQ3'
CERT_FILE = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'

print("="*60)
print("BETFAIR MARKET SCAN")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*60)

# Login
payload = f'username={USERNAME}&password={PASSWORD}'
headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', 
                 data=payload, cert=CERT_FILE, headers=headers, timeout=15, verify=False)

if r.status_code != 200:
    print(f"HTTP {r.status_code}")
    exit()

data = r.json()
if data.get('loginStatus') != 'SUCCESS':
    print(f"Login failed: {data.get('loginStatus')}")
    exit()

token = data.get('sessionToken')
print("[OK] Logged in\n")

# Get markets (3 hours)
now = datetime.now()
later = now + timedelta(hours=3)

headers = {
    'X-Application': APP_KEY,
    'X-Authentication': token,
    'Content-Type': 'application/json'
}

payload = {
    'jsonrpc': '2.0',
    'method': 'SportsAPING/v1.0/listMarketCatalogue',
    'params': {
        'filter': {
            'eventTypeIds': ['7'],
            'marketTypeCodes': ['WIN'],
            'marketStartTime': {
                'from': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'to': later.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        },
        'maxResults': 20,
        'marketProjection': ['EVENT', 'RUNNER_DESCRIPTION', 'MARKET_START_TIME']
    },
    'id': 1
}

r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                 headers=headers, json=payload, timeout=10)

if r.status_code != 200:
    print(f"API error: {r.status_code}")
    exit()

result = r.json().get('result', [])
print(f"Horse Racing Markets (3h): {len(result)}\n")

for m in result:
    event = m.get('event', {}).get('eventName', '?')
    start = m.get('marketStartTime', '?')
    mid = m.get('marketId', '?')
    
    # Parse time
    if start and start != '?':
        try:
            dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            local = dt.astimezone().strftime('%H:%M')
            mins = (dt.astimezone() - datetime.now().astimezone()).total_seconds() / 60
        except:
            local = '?'
            mins = 999
    else:
        local = '?'
        mins = 999
    
    print(f"\n{local} ({mins:.0f}min) | {event}")
    
    # Get prices
    book_payload = {
        'jsonrpc': '2.0',
        'method': 'SportsAPING/v1.0/listMarketBook',
        'params': {
            'marketIds': [mid],
            'priceProjection': {'priceData': ['EX_ALL_OFFERS']}
        },
        'id': 1
    }
    
    r2 = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                      headers=headers, json=book_payload, timeout=10)
    
    if r2.status_code == 200:
        books = r2.json().get('result', [])
        if books:
            book = books[0]
            
            if book.get('status') == 'OPEN':
                runners = m.get('runners', [])
                
                for runner in runners[:6]:  # Top 6
                    rid = runner.get('selectionId')
                    rname = runner.get('runnerName', '?')
                    
                    # Get prices
                    for rbook in book.get('runners', []):
                        if rbook.get('selectionId') == rid:
                            ex = rbook.get('ex', {})
                            back = ex.get('availableToBack', [])
                            lay = ex.get('availableToLay', [])
                            
                            if back and lay:
                                bp = back[0]['price']
                                lp = lay[0]['price']
                                spread = lp - bp
                                
                                # Show
                                print(f"  {rname[:20]:20s} | BACK {bp:6.2f} | LAY {lp:6.2f} | Spr {spread:.2f}")
                            break
            else:
                print(f"  Status: {book.get('status')}")

print("\n" + "="*60)
print("Markets starting 5-15 min are BEST for steam scalping")
print("="*60)
