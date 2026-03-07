#!/usr/bin/env python3
"""Check Betfair balance and settled bets"""

import requests
import json

USERNAME = 'dnfarnot@gmail.com'
PASSWORD = 'Tobiano01'
APP_KEY = 'XmZEwtLsIRkf5lQ3'
CERT_FILE = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'

print('='*60)
print('BETFAIR ACCOUNT - POST-RACE CHECK')
print('='*60)
print()

# Login
payload = f'username={USERNAME}&password={PASSWORD}'
headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.post(
    'https://identitysso-cert.betfair.com/api/certlogin',
    data=payload,
    cert=CERT_FILE,
    headers=headers,
    timeout=15
)

if response.status_code == 200:
    result = response.json()
    if result.get('loginStatus') == 'SUCCESS':
        session_token = result.get('sessionToken')
        print('Login: SUCCESS')
        print()

        # Get account balance
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': session_token,
            'Content-Type': 'application/json'
        }

        payload = {
            'jsonrpc': '2.0',
            'method': 'AccountAPING/v1.0/getAccountFunds',
            'params': {},
            'id': 1
        }

        response = requests.post(
            'https://api.betfair.com/exchange/account/json-rpc/v1',
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json().get('result', {})
            available = result.get('availableToBetBalance', 0)
            balance = result.get('balance', 0)
            exposure = result.get('exposure', 0)

            print('ACCOUNT STATUS:')
            print(f'  Available: ${available:.2f} AUD')
            print(f'  Balance: ${balance:.2f} AUD')
            print(f'  Exposure: ${exposure:.2f} AUD')
            print()

            # Calculate P&L
            starting = 20.67
            pnl = available - starting

            print('PERFORMANCE:')
            print(f'  Started with: ${starting:.2f}')
            print(f'  Current: ${available:.2f}')
            print(f'  P&L: ${pnl:+.2f}')
            print()

            # Get cleared orders (settled bets)
            payload2 = {
                'jsonrpc': '2.0',
                'method': 'SportsAPING/v1.0/listClearedOrders',
                'params': {
                    'betStatus': 'SETTLED',
                    'pageSize': 100
                },
                'id': 1
            }

            response2 = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=payload2,
                timeout=10
            )

            if response2.status_code == 200:
                result2 = response2.json()
                orders = result2.get('result', {}).get('clearedOrders', [])

                if orders:
                    print(f'SETTLED BETS: {len(orders)}')
                    print()

                    total_profit = 0

                    for order in orders:
                        bet_id = order.get('betId')
                        market_name = order.get('marketName', 'Unknown')
                        selection_name = order.get('selectionName', 'Unknown')
                        side = order.get('side')
                        price = order.get('price')
                        size = order.get('size')
                        profit = order.get('profit', 0)

                        total_profit += profit

                        print(f'  Bet: {bet_id}')
                        print(f'  Market: {market_name}')
                        print(f'  Selection: {selection_name}')
                        print(f'  Side: {side}')
                        print(f'  Price: {price}')
                        print(f'  Size: {size}')
                        print(f'  Profit: ${profit:+.2f}')
                        print()

                    print(f'TOTAL PROFIT: ${total_profit:+.2f}')
                else:
                    print('No settled bets found yet.')
        else:
            print(f'Error: {response.status_code}')
else:
    print(f'Login failed: {response.status_code}')

print()
print('='*60)
