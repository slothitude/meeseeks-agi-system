#!/usr/bin/env python3
"""Find IN-PLAY tennis matches"""
import requests
from datetime import datetime

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

def login():
    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=payload, cert=CERT_FILE, headers=headers, timeout=15)
    if r.status_code == 200 and r.json().get('loginStatus') == 'SUCCESS':
        return r.json().get('sessionToken')
    return None

def get_inplay(token):
    headers = {'X-Application': APP_KEY, 'X-Authentication': token, 'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["1", "2", "4"],  # Horse, Tennis, Cricket
                "marketBettingTypes": ["ODDS"],
                "inPlayOnly": True
            },
            "maxResults": 20,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        },
        "id": 1
    }
    r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1', headers=headers, json=payload, timeout=10)
    if r.status_code == 200:
        return r.json().get('result', [])
    return []

token = login()
if not token:
    print("Login failed")
    exit()

print("="*70)
print("IN-PLAY MARKETS")
print("="*70)

markets = get_inplay(token)
print(f"\nFound {len(markets)} in-play markets\n")

for m in markets:
    event = m.get('event', {})
    print(f"{event.get('eventName', 'Unknown')}")
    print(f"  Market: {m.get('marketName')}")
    print(f"  ID: {m.get('marketId')}")
    print()
