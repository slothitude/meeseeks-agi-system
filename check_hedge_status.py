#!/usr/bin/env python3
"""
Check Hedge Status
==================

Are our bets properly hedged (green booked)?
"""

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
            
            print("="*60)
            print("HEDGE STATUS CHECK")
            print("="*60)
            
            if not orders:
                print("\nNo open orders - races may have completed")
            else:
                print(f"\nOpen positions: {len(orders)}")
                
                for order in orders:
                    market_id = order.get('marketId')
                    selection_id = order.get('selectionId')
                    side = order.get('side')
                    price = order.get('priceSize', {}).get('price', 0)
                    size = order.get('sizeMatched', 0)
                    status = order.get('status')
                    
                    print(f"\n  Market: {market_id}")
                    print(f"  Selection: {selection_id}")
                    print(f"  Side: {side}")
                    print(f"  Price: {price}")
                    print(f"  Matched: {size}")
                    print(f"  Status: {status}")
                    
                    # Check if hedged
                    if side == 'BACK':
                        print(f"  ⚠️  NOT HEDGED - Need LAY bet to green book")
                    elif side == 'LAY':
                        print(f"  ⚠️  NOT HEDGED - Need BACK bet to green book")
