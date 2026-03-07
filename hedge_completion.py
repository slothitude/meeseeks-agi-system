#!/usr/bin/env python3
"""
Hedge Completion System
=======================

Monitors open BACK positions and places LAY bets to complete hedge.

CRITICAL: This completes the green book.
"""

import requests
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Files
POSITIONS_FILE = Path("open_positions.json")
HEDGE_LOG = Path("hedge_log.json")

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

session_token = None


def login_betfair():
    """Login to Betfair"""
    global session_token
    
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
            print("Betfair login: SUCCESS")
            return True
    
    return False


def get_current_prices(market_id: str, selection_id: int):
    """Get current BACK and LAY prices"""
    if not session_token:
        return None
    
    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }
    
    payload = {
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
    
    response = requests.post(
        'https://api.betfair.com/exchange/betting/json-rpc/v1',
        headers=headers,
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json().get('result', [])
        if result:
            book = result[0]
            ex = book.get('ex', {})
            
            back_offers = ex.get('availableToBack', [])
            lay_offers = ex.get('availableToLay', [])
            
            if back_offers and lay_offers:
                return {
                    'back_price': back_offers[0].get('price', 0),
                    'back_size': back_offers[0].get('size', 0),
                    'lay_price': lay_offers[0].get('price', 0),
                    'lay_size': lay_offers[0].get('size', 0)
                }
    
    return None


def place_lay_bet(market_id: str, selection_id: int, price: float, stake: float):
    """Place LAY bet to complete hedge"""
    if not session_token:
        return None
    
    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }
    
    payload = {
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
                    'size': stake,
                    'price': price,
                    'persistenceType': 'LAPSE'
                }
            }],
            'customerRef': f'hedge_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        },
        'id': 1
    }
    
    response = requests.post(
        'https://api.betfair.com/exchange/betting/json-rpc/v1',
        headers=headers,
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    
    return None


def complete_hedge(position: dict):
    """Complete hedge for an open BACK position"""
    market_id = position.get('market_id')
    selection_id = position.get('selection_id')
    entry_price = position.get('entry_price')
    stake = position.get('stake', 1.0)
    target_lay_price = position.get('target_price')
    runner_name = position.get('runner', 'Unknown')
    
    print(f"\nChecking {runner_name}:")
    print(f"  BACK @ ${entry_price:.2f}")
    print(f"  Target LAY @ ${target_lay_price:.2f}")
    
    # Get current prices
    prices = get_current_prices(market_id, selection_id)
    
    if not prices:
        print(f"  ERROR: Cannot get prices")
        return None
    
    current_lay = prices['lay_price']
    current_lay_size = prices['lay_size']
    
    print(f"  Current LAY: ${current_lay:.2f} (liquidity: ${current_lay_size:.2f})")
    
    # Check if we can hedge
    if current_lay <= target_lay_price:
        # Calculate lay stake
        lay_stake = (stake * entry_price) / current_lay
        
        print(f"  HEDGE OPPORTUNITY!")
        print(f"  Placing LAY ${lay_stake:.2f} @ ${current_lay:.2f}")
        
        # Place LAY bet
        result = place_lay_bet(market_id, selection_id, current_lay, lay_stake)
        
        if result:
            status = result.get('result', {}).get('status')
            
            if status == 'SUCCESS':
                instructions = result.get('result', {}).get('instructionReports', [])
                if instructions:
                    bet_id = instructions[0].get('betId')
                    matched = instructions[0].get('sizeMatched', 0)
                    
                    # Calculate guaranteed profit
                    if_matched = (stake * (entry_price - 1)) - (lay_stake * (current_lay - 1))
                    if_loses = lay_stake - stake
                    guaranteed = min(if_matched, if_loses)
                    
                    print(f"  SUCCESS! Bet ID: {bet_id}")
                    print(f"  Matched: ${matched:.2f}")
                    print(f"  GREEN BOOK: +${guaranteed:.2f} guaranteed profit!")
                    
                    return {
                        'success': True,
                        'lay_bet_id': bet_id,
                        'lay_price': current_lay,
                        'lay_stake': lay_stake,
                        'guaranteed_profit': guaranteed
                    }
            else:
                print(f"  FAILED: {status}")
        else:
            print(f"  FAILED: No response")
    else:
        print(f"  Waiting for price to drop (need ${target_lay_price:.2f}, current ${current_lay:.2f})")
    
    return None


def monitor_and_hedge():
    """Main monitoring loop"""
    print("="*60)
    print("HEDGE COMPLETION SYSTEM")
    print("="*60)
    print()
    
    if not login_betfair():
        print("FATAL: Could not login")
        return
    
    # Load open positions
    if not POSITIONS_FILE.exists():
        print("No open positions to hedge")
        return
    
    with open(POSITIONS_FILE, 'r') as f:
        positions = json.load(f)
    
    print(f"Monitoring {len(positions)} open positions...\n")
    
    # Check each position
    for position in positions:
        if position.get('side') == 'BACK' and not position.get('hedged'):
            result = complete_hedge(position)
            
            if result and result.get('success'):
                position['hedged'] = True
                position['lay_bet_id'] = result['lay_bet_id']
                position['lay_price'] = result['lay_price']
                position['lay_stake'] = result['lay_stake']
                position['guaranteed_profit'] = result['guaranteed_profit']
    
    # Save updated positions
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)
    
    print("\nHedge monitoring complete")


if __name__ == "__main__":
    monitor_and_hedge()
