#!/usr/bin/env python3
"""Check settled bets and balance."""
import requests
import json
from datetime import datetime, timedelta

# Login
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
print(f"Login: {'OK' if token else 'FAILED'}")

# Get balance
h = {'X-Application': 'XmZEwtLsIRkf5lQ3', 'X-Authentication': token, 'Content-Type': 'application/json'}
bal_resp = s.post(
    'https://api.betfair.com/exchange/account/json-rpc/v1',
    headers=h,
    json={'jsonrpc': '2.0', 'method': 'AccountAPING/v1.0/getAccountFunds', 'params': {}, 'id': 1}
)
balance = bal_resp.json().get('result', {}).get('availableToBetBalance')
exposure = bal_resp.json().get('result', {}).get('exposure')
print(f"Balance: ${balance} | Exposure: {exposure}")

# Get settled orders
from_date = (datetime.utcnow() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
settled = s.post(
    'https://api.betfair.com/exchange/betting/json-rpc/v1',
    headers=h,
    json={
        'jsonrpc': '2.0',
        'method': 'SportsAPING/v1.0/listClearedOrders',
        'params': {
            'betStatus': 'SETTLED',
            'settledDateRange': {'from': from_date}
        },
        'id': 1
    }
).json()

orders = settled.get('result', {}).get('clearedOrders', [])
print(f"\nSettled bets: {len(orders)}")

total_profit = 0
for o in orders:
    profit = o.get('profit', 0)
    total_profit += profit
    print(f"  Selection {o['selectionId']}: {o['betOutcome']} @ {o['priceMatched']} | P/L: {profit:+.1f}")

print(f"\nTotal P/L: {total_profit:+.1f}")
