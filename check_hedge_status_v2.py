#!/usr/bin/env python3
"""Quick check - are our positions hedged?"""

import requests
import json

USERNAME = 'dnfarnot@gmail.com'
PASSWORD = 'Tobiano01'
APP_KEY = 'XmZEwtLsIRkf5lQ3'
CERT_FILE = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'

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
        
        # Get current orders
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': session_token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'jsonrpc': '2.0',
            'method': 'SportsAPING/v1.0/listCurrentOrders',
            'params': {},
            'id': 1
        }
        
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            orders = result.get('result', {}).get('currentOrders', [])
            
            print(f'\nCurrent orders: {len(orders)}')
            
            back_bets = []
            lay_bets = []
            
            for order in orders:
                side = order.get('side')
                if side == 'BACK':
                    back_bets.append(order)
                elif side == 'LAY':
                    lay_bets.append(order)
            
            print(f'BACK bets: {len(back_bets)}')
            print(f'LAY bets: {len(lay_bets)}')
            
            if len(back_bets) > 0 and len(lay_bets) == 0:
                print('\n⚠️ NOT HEDGED - Need LAY bets to complete!')
            elif len(back_bets) > 0 and len(lay_bets) > 0:
                print('\n✅ HEDGED - Both BACK and LAY present')
            
            # Show details
            for order in back_bets:
                print(f'\nBACK: {order.get("betId")}')
                print(f'  Price: {order.get("priceSize", {}).get("price")}')
                print(f'  Size: {order.get("priceSize", {}).get("size")}')
            
            for order in lay_bets:
                print(f'\nLAY: {order.get("betId")}')
                print(f'  Price: {order.get("priceSize", {}).get("price")}')
                print(f'  Size: {order.get("priceSize", {}).get("size")}')
        else:
            print(f'Error: {response.status_code}')
else:
    print(f'Login failed: {response.status_code}')
