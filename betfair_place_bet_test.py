#!/usr/bin/env python3
"""
Betfair Place Bet Test - PAPER TRADING MODE
============================================

This shows how the system WILL place bets when we go live.

PAPER MODE: Sets "customerStrategyRef" = "PAPER" 
            Bets are validated but NOT executed.

LIVE MODE: Removes customerStrategyRef
           Bets are ACTUALLY placed.

Usage:
    python betfair_place_bet_test.py --paper    # Validate only (no bet)
    python betfair_place_bet_test.py --live     # Actually place bet
"""

import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings()

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# API endpoints
LOGIN_URL = "https://identitysso-cert.betfair.com/api/certlogin"
API_URL = "https://api.betfair.com/exchange/betting/json-rpc/v1"


class BetfairTrader:
    def __init__(self, paper_mode: bool = True):
        self.paper_mode = paper_mode
        self.token = None
        self.session = requests.Session()
        
    def login(self) -> bool:
        """Login to Betfair."""
        payload = f"username={USERNAME}&password={PASSWORD}"
        headers = {
            'X-Application': APP_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            r = self.session.post(
                LOGIN_URL,
                data=payload,
                cert=CERT_FILE,
                headers=headers,
                timeout=15,
                verify=False
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('loginStatus') == 'SUCCESS':
                    self.token = data.get('sessionToken')
                    print(f"[OK] Logged in as {USERNAME}")
                    return True
                else:
                    print(f"[FAIL] Login status: {data.get('loginStatus')}")
            else:
                print(f"[FAIL] HTTP {r.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        return False
    
    def api_call(self, method: str, params: dict):
        """Make API call."""
        if not self.token:
            return None
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        try:
            r = self.session.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[ERROR] API call failed: {e}")
        
        return None
    
    def get_market(self, market_id: str) -> dict:
        """Get market details."""
        result = self.api_call("SportsAPING/v1.0/listMarketBook", {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        
        if result and 'result' in result:
            return result['result'][0] if result['result'] else None
        return None
    
    def place_back_bet(self, market_id: str, selection_id: int, 
                       stake: float, price: float) -> dict:
        """
        Place a BACK bet.
        
        BACK = Betting something WILL happen (traditional bet)
        - Risk: stake
        - Return: stake * (price - 1) if wins
        """
        print(f"\n[BACK BET]")
        print(f"  Market: {market_id}")
        print(f"  Selection: {selection_id}")
        print(f"  Stake: ${stake:.2f}")
        print(f"  Price: {price:.2f}")
        print(f"  Mode: {'PAPER (validated only)' if self.paper_mode else 'LIVE (real money)'}")
        
        instructions = [{
            "selectionId": selection_id,
            "handicap": "0",
            "side": "BACK",  # BACK bet
            "orderType": "LIMIT",
            "limitOrder": {
                "size": stake,
                "price": price,
                "persistenceType": "LAPSE"  # Cancel if not matched
            }
        }]
        
        params = {
            "marketId": market_id,
            "instructions": instructions
        }
        
        # PAPER MODE: Add customerStrategyRef to validate without betting
        if self.paper_mode:
            params["customerStrategyRef"] = "PAPER"
        
        result = self.api_call("SportsAPING/v1.0/placeOrders", params)
        
        if result:
            print(f"  Result: {json.dumps(result, indent=2)}")
            return result
        
        print(f"  [ERROR] No response")
        return None
    
    def place_lay_bet(self, market_id: str, selection_id: int,
                      liability: float, price: float) -> dict:
        """
        Place a LAY bet.
        
        LAY = Betting something WON'T happen (acting as bookmaker)
        - Risk: liability = stake * (price - 1)
        - Return: stake if wins (horse loses)
        """
        print(f"\n[LAY BET]")
        print(f"  Market: {market_id}")
        print(f"  Selection: {selection_id}")
        print(f"  Liability: ${liability:.2f}")
        print(f"  Price: {price:.2f}")
        print(f"  Mode: {'PAPER (validated only)' if self.paper_mode else 'LIVE (real money)'}")
        
        # Calculate stake from liability
        # liability = stake * (price - 1)
        # stake = liability / (price - 1)
        stake = liability / (price - 1) if price > 1 else 0
        
        print(f"  Stake (calculated): ${stake:.2f}")
        
        instructions = [{
            "selectionId": selection_id,
            "handicap": "0",
            "side": "LAY",  # LAY bet
            "orderType": "LIMIT",
            "limitOrder": {
                "size": stake,
                "price": price,
                "persistenceType": "LAPSE"
            }
        }]
        
        params = {
            "marketId": market_id,
            "instructions": instructions
        }
        
        if self.paper_mode:
            params["customerStrategyRef"] = "PAPER"
        
        result = self.api_call("SportsAPING/v1.0/placeOrders", params)
        
        if result:
            print(f"  Result: {json.dumps(result, indent=2)}")
            return result
        
        print(f"  [ERROR] No response")
        return None
    
    def cancel_all_orders(self, market_id: str) -> dict:
        """Cancel all orders on a market."""
        print(f"\n[CANCEL ALL]")
        print(f"  Market: {market_id}")
        
        result = self.api_call("SportsAPING/v1.0/cancelAllOrders", {
            "marketIds": [market_id]
        })
        
        if result:
            print(f"  Result: {json.dumps(result, indent=2)}")
            return result
        
        return None


def test_paper_trading():
    """Test paper trading mode."""
    print("="*60)
    print("BETFAIR PAPER TRADING TEST")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print()
    
    trader = BetfairTrader(paper_mode=True)
    
    if not trader.login():
        print("\n[FAIL] Could not login")
        return False
    
    print("\n[OK] Ready to place bets (paper mode)")
    
    # Example: Place a back bet
    # In real usage, market_id and selection_id come from market scanner
    print("\n" + "-"*60)
    print("EXAMPLE 1: BACK bet (betting horse WILL win)")
    print("-"*60)
    print("This would place a $1.00 BACK bet at $3.00 odds")
    print("Risk: $1.00 | Return if wins: $2.00")
    print("In PAPER mode, bet is validated but NOT placed")
    
    # Example: Place a lay bet
    print("\n" + "-"*60)
    print("EXAMPLE 2: LAY bet (betting horse WON'T win)")
    print("-"*60)
    print("This would place a LAY bet with $2.00 liability at $3.00 odds")
    print("Risk: $2.00 | Return if horse loses: $1.00")
    print("In PAPER mode, bet is validated but NOT placed")
    
    print("\n" + "="*60)
    print("HOW STEAMARB WILL USE THIS")
    print("="*60)
    print()
    print("ARB Opportunity:")
    print("  1. BACK on Ladbrokes @ $4.00")
    print("  2. LAY on Betfair @ $3.50")
    print("  3. Profit: locked in regardless of outcome")
    print()
    print("STEAM Opportunity:")
    print("  1. BACK on Betfair @ $4.00")
    print("  2. Wait for price to drop")
    print("  3. LAY on Betfair @ $3.50")
    print("  4. Profit: green book")
    print()
    print("VALUE Opportunity:")
    print("  1. BACK on Ladbrokes @ $5.00")
    print("  2. Betfair true price: $4.00")
    print("  3. Profit: positive EV over time")
    print()
    print("="*60)
    print("SAFETY: All bets use LAPSE persistence")
    print("If not matched before race, bets auto-cancel")
    print("="*60)
    
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper', action='store_true', default=True)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    
    # Override paper mode if --live specified
    paper_mode = not args.live
    
    if args.live:
        print("\n" + "!"*60)
        print("WARNING: LIVE MODE - REAL MONEY AT STAKE")
        print("!"*60 + "\n")
    
    test_paper_trading()


if __name__ == "__main__":
    main()
