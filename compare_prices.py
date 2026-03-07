#!/usr/bin/env python3
"""Compare Ladbrokes vs Betfair prices."""
import requests
from datetime import datetime, timezone

# Login to Betfair
cert = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'
s = requests.Session()

resp = s.post(
    'https://identitysso-cert.betfair.com/api/certlogin',
    data='username=dnfarnot@gmail.com&password=Tobiano01',
    cert=cert,
    headers={'X-Application': 'XmZEwtLsIRkf5lQ3', 'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=15
)
token = resp.json().get('sessionToken')
h = {'X-Application': 'XmZEwtLsIRkf5lQ3', 'X-Authentication': token, 'Content-Type': 'application/json'}

# Get Flemington R8 market
book = s.post(
    'https://api.betfair.com/exchange/betting/json-rpc/v1',
    headers=h,
    json={
        'jsonrpc': '2.0',
        'method': 'SportsAPING/v1.0/listMarketBook',
        'params': {
            'marketIds': ['1.254776538'],  # Flemington R8
            'priceProjection': {'priceData': ['EX_ALL_OFFERS']}
        },
        'id': 1
    }
).json()

print('Flemington R8 Betfair LAY prices:')
for runner in book['result'][0]['runners'][:5]:
    ex = runner.get('ex', {})
    lay = ex['availableToLay'][0]['price'] if ex.get('availableToLay') else None
    print(f'  Selection {runner["selectionId"]}: LAY {lay}')

# Get Ladbrokes Flemington R8
event_r = requests.get(
    'https://api.ladbrokes.com.au/affiliates/v1/racing/events/3c57593e-5257-4a24-b1de-ab8e9fbb64fe',
    headers={'From': 'slothitudegames@gmail.com', 'X-Partner': 'Slothitude Games'},
    timeout=10
)

if event_r.status_code == 200:
    data = event_r.json()
    runners = data.get('data', {}).get('runners', [])
    print('\nLadbrokes Flemington BACK prices:')
    for r in runners[:5]:
        odds = r.get('odds', {})
        fw = odds.get('fixed_win')
        print(f"  {r['name']}: {fw}")
