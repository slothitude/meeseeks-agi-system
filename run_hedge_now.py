#!/usr/bin/env python3
"""Run hedge completion NOW"""

import requests
import json

USERNAME = 'dnfarnot@gmail.com'
PASSWORD = 'Tobiano01'
APP_KEY = 'XmZEwtLsIRkf5lQ3'
CERT_FILE = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'

print('='*60)
print('HEDGE COMPLETION - RUNNING NOW')
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

            print(f'Current orders: {len(orders)}')
            print()

            if len(orders) == 0:
                print('No open orders found.')
                print()
                print('This means:')
                print('  - Races may have already completed')
                print('  - Bets may have been settled')
                print('  - Markets closed')
                print()
                print('Check Betfair account for settled bets.')
            else:
                back_bets = [o for o in orders if o.get('side') == 'BACK']
                lay_bets = [o for o in orders if o.get('side') == 'LAY']

                print(f'BACK bets: {len(back_bets)}')
                print(f'LAY bets: {len(lay_bets)}')
                print()

                if len(back_bets) > 0 and len(lay_bets) == 0:
                    print('STATUS: NOT HEDGED')
                    print()
                    print('Open BACK positions:')
                    for bet in back_bets:
                        bet_id = bet.get('betId')
                        price = bet.get('priceSize', {}).get('price', 0)
                        size = bet.get('priceSize', {}).get('size', 0)
                        market_id = bet.get('marketId')
                        selection_id = bet.get('selectionId')

                        print(f'  Bet ID: {bet_id}')
                        print(f'  Price: {price}')
                        print(f'  Size: {size}')
                        print(f'  Market: {market_id}')
                        print(f'  Selection: {selection_id}')
                        print()

                        # Get current LAY price
                        payload2 = {
                            'jsonrpc': '2.0',
                            'method': 'SportsAPING/v1.0/listRunnerBook',
                            'params': {
                                'marketId': market_id,
                                'selectionId': selection_id,
                                'priceProjection': {
                                    'priceData': ['EX_BEST_OFFERS'],
                                    'virtualise': True
                                }
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
                            result2 = response2.json().get('result', [])
                            if result2:
                                book = result2[0]
                                ex = book.get('ex', {})
                                lay_offers = ex.get('availableToLay', [])

                                if lay_offers:
                                    current_lay = lay_offers[0].get('price', 0)
                                    lay_size = lay_offers[0].get('size', 0)

                                    target_lay = price * 0.95  # 5% lower

                                    print(f'  Current LAY: {current_lay}')
                                    print(f'  Target LAY: {target_lay:.2f}')
                                    print(f'  Liquidity: {lay_size}')

                                    if current_lay <= target_lay:
                                        print('  STATUS: CAN HEDGE NOW!')

                                        # Calculate lay stake
                                        lay_stake = (size * price) / current_lay

                                        print(f'  Would LAY: {lay_stake:.2f} @ {current_lay}')

                                        # Calculate profit
                                        if_wins = (size * (price - 1)) - (lay_stake * (current_lay - 1))
                                        if_loses = lay_stake - size
                                        guaranteed = min(if_wins, if_loses)

                                        print(f'  Green book: +{guaranteed:.2f} guaranteed')

                                        # PLACE BET
                                        print()
                                        print('  PLACING LAY BET...')

                                        payload3 = {
                                            'jsonrpc': '2.0',
                                            'method': 'SportsAPING/v1.0/placeOrders',
                                            'params': {
                                                'marketId': market_id,
                                                'instructions': [{
                                                    'selectionId': selection_id,
                                                    'handicap': '0',
                                                    'side': 'LAY',
                                                    'orderType': 'LIMIT',
                                                    'limitOrder': {
                                                        'size': lay_stake,
                                                        'price': current_lay,
                                                        'persistenceType': 'LAPSE'
                                                    }
                                                }],
                                                'customerRef': f'hedge_{bet_id}'
                                            },
                                            'id': 1
                                        }

                                        response3 = requests.post(
                                            'https://api.betfair.com/exchange/betting/json-rpc/v1',
                                            headers=headers,
                                            json=payload3,
                                            timeout=10
                                        )

                                        if response3.status_code == 200:
                                            result3 = response3.json()
                                            status = result3.get('result', {}).get('status')

                                            if status == 'SUCCESS':
                                                instructions = result3.get('result', {}).get('instructionReports', [])
                                                if instructions:
                                                    new_bet_id = instructions[0].get('betId')
                                                    matched = instructions[0].get('sizeMatched', 0)

                                                    print(f'  SUCCESS! LAY bet placed')
                                                    print(f'  Bet ID: {new_bet_id}')
                                                    print(f'  Matched: {matched}')
                                                    print(f'  GREEN BOOK COMPLETE!')
                                            else:
                                                error = result3.get('result', {}).get('errorCode', 'UNKNOWN')
                                                print(f'  FAILED: {error}')
                                        else:
                                            print(f'  FAILED: {response3.status_code}')
                                    else:
                                        print('  STATUS: Waiting for price to drop')
                                else:
                                    print('  No LAY liquidity')
                elif len(lay_bets) > 0:
                    print('STATUS: HEDGED (LAY bets present)')
        else:
            print(f'Error: {response.status_code}')
else:
    print(f'Login failed: {response.status_code}')

print()
print('='*60)
print('HEDGE COMPLETION FINISHED')
print('='*60)
