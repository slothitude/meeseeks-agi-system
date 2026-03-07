#!/usr/bin/env python3
"""Check open bet details."""
import requests

cert = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'
s = requests.Session()

# Login
resp = s.post(
    'https://identitysso-cert.betfair.com/api/certlogin',
    data='username=dnfarnot@gmail.com&password=Tobiano01',
    cert=cert,
    headers={'X-Application': 'XmZEwtLsIRkf5lQ3', 'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=15
)
token = resp.json().get('sessionToken')
h = {'X-Application': 'XmZEwtLsIRkf5lQ3', 'X-Authentication': token, 'Content-Type': 'application/json'}

# Get current orders
orders = s.post(
    'https://api.betfair.com/exchange/betting/json-rpc/v1',
    headers=h,
    json={
        'jsonrpc': '2.0',
        'method': 'SportsAPING/v1.0/listCurrentOrders',
        'params': {},
        'id': 1
    }
).json()

print("Open orders:\n")
for o in orders.get('result', {}).get('currentOrders', []):
    print(f"Market: {o['marketId']}")
    print(f"Selection: {o['selectionId']}")
    print(f"Side: {o['side']}")
    print(f"Price: {o['priceSize']['price']}")
    print(f"Size: {o['priceSize']['size']}")
    print(f"Status: {o['status']}")
    print(f"Bet ID: {o['betId']}")
