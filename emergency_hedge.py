#!/usr/bin/env python3
"""Emergency hedge - get current Ninja price and BACK."""
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

# Get current prices for Ninja (Randwick R8)
# Market ID from open bet
market_id = '1.254780548'  # Randwick R8
selection_id = 37244239  # Ninja

# Get market book
book = s.post(
    'https://api.betfair.com/exchange/betting/json-rpc/v1',
    headers=h,
    json={
        'jsonrpc': '2.0',
        'method': 'SportsAPING/v1.0/listMarketBook',
        'params': {
            'marketIds': [market_id],
            'priceProjection': {'priceData': ['EX_ALL_OFFERS']}
        },
        'id': 1
    }
).json()

print("Current Ninja prices:")
for runner in book['result'][0]['runners']:
    ex = runner.get('ex', {})
    back = ex['availableToBack'][0]['price'] if ex.get('availableToBack') else None
    lay = ex['availableToLay'][0]['price'] if ex.get('availableToLay') else None

    # Ninja is likely selection with ~6.0 price
    if back and 5.5 < back < 7.0:
        print(f"  Selection {runner['selectionId']}: BACK {back} | LAY {lay}")
        selection_id = runner['selectionId']

        # Calculate hedge stake
        # LAY $1.05 @ $6.20 = if wins, lose $5.46
        # Need to BACK to cover
        # BACK stake = LAY stake * LAY price / BACK price
        lay_stake = 1.05
        lay_price = 6.20
        back_price = back
        hedge_stake = (lay_stake * lay_price) / back_price

        print(f"\n  Hedge calculation:")
        print(f"  LAY: ${lay_stake} @ ${lay_price}")
        print(f"  BACK: ${hedge_stake:.2f} @ ${back_price}")
        print(f"  If wins: +${(hedge_stake * (back_price - 1)) - (lay_stake * (lay_price - 1)):.2f}")
        print(f"  If loses: -${hedge_stake - lay_stake:.2f}")

        # Place BACK hedge
        print(f"\n  Placing BACK hedge...")

        order = s.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=h,
            json={
                'jsonrpc': '2.0',
                'method': 'SportsAPING/v1.0/placeOrders',
                'params': {
                    'marketId': market_id,
                    'instructions': [{
                        'selectionId': selection_id,
                        'side': 'BACK',
                        'orderType': 'LIMIT',
                        'limitOrder': {
                            'size': round(hedge_stake, 2),
                            'price': back,
                            'persistenceType': 'LAPSE'
                        }
                    }]
                },
                'id': 1
            }
        ).json()

        if 'result' in order and order['result'].get('status') == 'SUCCESS':
            bet_id = order['result']['instructionReports'][0]['betId']
            matched = order['result']['instructionReports'][0]['sizeMatched']
            print(f"  ✅ BACK hedge placed: ${matched} @ ${back}")
            print(f"  Bet ID: {bet_id}")
        else:
            print(f"  ❌ BACK failed: {order}")

        break
