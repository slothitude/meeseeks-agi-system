#!/usr/bin/env python3
"""
Auto-Hedge System
=================
Places LAY bets immediately after BACK bets to lock in profit.
Greens the book for guaranteed returns.

Uses requests directly with certificate (same as live_trading_integrated.py)
"""

import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
R_UNIT = 1.00
TARGET_PRICE_DROP = 0.95  # Target 5% price drop
MAX_WAIT_SECONDS = 300  # 5 minutes max wait
CHECK_INTERVAL = 2  # Check every 2 seconds
BETFAIR_COMMISSION = 0.05
MIN_TIME_TO_RACE = 120  # 2 minutes - force hedge if less than this

# Paths
WORKSPACE = Path(__file__).parent
OPEN_POSITIONS_FILE = WORKSPACE / "open_positions.json"
LIVE_TRADES_LOG = WORKSPACE / "live_trades_log.json"
BANKROLL_FILE = WORKSPACE / "bankroll.json"

# Betfair credentials (same as live_trading_integrated.py)
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"


class AutoHedge:
    """Auto-hedge system for green booking trades."""
    
    def __init__(self):
        self.session_token = None
        self.connected = False
        
    def connect(self):
        """Connect to Betfair API."""
        try:
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
                    self.session_token = result.get('sessionToken')
                    self.connected = True
                    print("[AUTO-HEDGE] Connected to Betfair")
                    return True
            
            print(f"[AUTO-HEDGE] Login failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"[AUTO-HEDGE] Connection failed: {e}")
            return False
    
    def load_open_positions(self):
        """Load open positions from file."""
        if not OPEN_POSITIONS_FILE.exists():
            return []
        try:
            with open(OPEN_POSITIONS_FILE) as f:
                data = json.load(f)
                # Handle both {"positions": [...]} and [...] formats
                if isinstance(data, dict) and "positions" in data:
                    return data["positions"]
                return data
        except:
            return []
    
    def save_open_positions(self, positions):
        """Save open positions to file."""
        with open(OPEN_POSITIONS_FILE, "w") as f:
            json.dump({"positions": positions}, f, indent=2)
    
    def get_current_price(self, market_id, selection_id):
        """Get current BACK and LAY prices for a selection."""
        if not self.connected:
            return None, None
            
        try:
            headers = {
                'X-Application': APP_KEY,
                'X-Authentication': self.session_token,
                'Content-Type': 'application/json'
            }
            
            data = {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/listMarketBook",
                "params": {
                    "marketIds": [market_id],
                    "priceProjection": {
                        "priceData": ["EX_ALL_OFFERS"]
                    }
                },
                "id": 1
            }
            
            response = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code != 200:
                return None, None
                
            result = response.json()
            
            if 'result' not in result or not result['result']:
                return None, None
                
            market_book = result['result'][0]
            
            for runner in market_book.get('runners', []):
                if runner.get('selectionId') == selection_id:
                    ex = runner.get('ex', {})
                    
                    back_price = None
                    lay_price = None
                    
                    if ex.get('availableToBack'):
                        back_price = ex['availableToBack'][0]['price']
                    if ex.get('availableToLay'):
                        lay_price = ex['availableToLay'][0]['price']
                        
                    return back_price, lay_price
                    
            return None, None
            
        except Exception as e:
            print(f"[AUTO-HEDGE] Error getting price: {e}")
            return None, None
    
    def place_lay_bet(self, market_id, selection_id, price, stake):
        """Place a LAY bet to hedge a BACK position."""
        if not self.connected:
            print("[AUTO-HEDGE] Not connected")
            return None
            
        try:
            headers = {
                'X-Application': APP_KEY,
                'X-Authentication': self.session_token,
                'Content-Type': 'application/json'
            }
            
            data = {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/placeOrders",
                "params": {
                    "marketId": market_id,
                    "instructions": [{
                        "selectionId": selection_id,
                        "side": "LAY",
                        "orderType": "LIMIT",
                        "limitOrder": {
                            "size": stake,
                            "price": price,
                            "persistenceType": "LAPSE"
                        }
                    }]
                },
                "id": 1
            }
            
            response = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"[AUTO-HEDGE] LAY failed: HTTP {response.status_code}")
                return None
                
            result = response.json()
            
            if 'result' in result and result['result'].get('status') == 'SUCCESS':
                instruction = result['result'].get('instructionReports', [{}])[0]
                bet_id = instruction.get('betId')
                print(f"[AUTO-HEDGE] LAY placed: ${stake:.2f} @ ${price:.2f} (bet_id: {bet_id})")
                return bet_id
            else:
                error = result.get('error', {}).get('message', 'Unknown error')
                print(f"[AUTO-HEDGE] LAY failed: {error}")
                return None
                
        except Exception as e:
            print(f"[AUTO-HEDGE] Error placing LAY: {e}")
            return None
    
    def calculate_green_book(self, back_price, back_stake, lay_price, lay_stake):
        """Calculate profit/loss for both outcomes after hedging."""
        # If runner WINS
        # BACK wins: back_stake * (back_price - 1)
        # LAY loses: -(lay_stake * (lay_price - 1))
        win_profit = (back_stake * (back_price - 1)) - (lay_stake * (lay_price - 1))
        
        # If runner LOSES
        # BACK loses: -back_stake
        # LAY wins: +lay_stake
        lose_profit = lay_stake - back_stake
        
        return win_profit, lose_profit
    
    def calculate_optimal_lay(self, back_price, back_stake, target_lay_price):
        """Calculate optimal LAY stake for equal profit either way."""
        # For green book: profit if wins = profit if loses
        # back_stake * (back_price - 1) - lay_stake * (lay_price - 1) = lay_stake - back_stake
        # Solving for lay_stake:
        # lay_stake = back_stake * back_price / lay_price
        
        lay_stake = (back_stake * back_price) / target_lay_price
        return lay_stake
    
    def get_market_start_time(self, market_id):
        """Get market start time."""
        if not self.connected:
            return None
            
        try:
            headers = {
                'X-Application': APP_KEY,
                'X-Authentication': self.session_token,
                'Content-Type': 'application/json'
            }
            
            data = {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/listMarketCatalogue",
                "params": {
                    "filter": {"marketIds": [market_id]},
                    "maxResults": 1,
                    "marketProjection": ["MARKET_START_TIME"]
                },
                "id": 1
            }
            
            response = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
                
            result = response.json()
            
            if 'result' in result and result['result']:
                start_time_str = result['result'][0].get('marketStartTime')
                if start_time_str:
                    # Parse ISO format time
                    from datetime import datetime, timezone
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    return start_time
            
            return None
            
        except Exception as e:
            print(f"[AUTO-HEDGE] Error getting market start time: {e}")
            return None

    def hedge_position(self, position):
        """Hedge a single open BACK position."""
        market_id = position.get("market_id")
        selection_id = position.get("selection_id")
        entry_price = position.get("entry_price")
        entry_stake = position.get("entry_stake", position.get("stake", R_UNIT))
        target_price = entry_price * TARGET_PRICE_DROP
        
        runner_name = position.get("runner", position.get("runner_name", "Unknown"))
        
        print(f"\n[AUTO-HEDGE] Monitoring: {runner_name}")
        print(f"  Entry: ${entry_stake:.2f} @ ${entry_price:.2f}")
        print(f"  Target: ${target_price:.2f} (5% drop)")
        
        # Get market start time
        market_start = self.get_market_start_time(market_id)
        if market_start:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            secs_to_start = (market_start - now).total_seconds()
            print(f"  Race starts in: {secs_to_start:.0f} seconds")
        else:
            secs_to_start = 9999  # Unknown, don't force
        
        start_time = time.time()
        max_loss_ratio = 0.50  # Accept up to 50% loss on hedge
        
        while time.time() - start_time < MAX_WAIT_SECONDS:
            # Check if we need to force hedge due to time
            if market_start:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                secs_remaining = (market_start - now).total_seconds()
                
                if secs_remaining < MIN_TIME_TO_RACE:
                    print(f"\n[AUTO-HEDGE] RACE STARTING SOON - forcing hedge at current price")
                    # Force hedge at current price to minimize loss
                    back_price, lay_price = self.get_current_price(market_id, selection_id)
                    if lay_price:
                        lay_stake = self.calculate_optimal_lay(entry_price, entry_stake, lay_price)
                        
                        # Ensure minimum stake of $1.00 for Betfair
                        if lay_stake < 1.00:
                            lay_stake = 1.00
                            print(f"[AUTO-HEDGE] Adjusted stake to minimum: $1.00")
                        
                        win_profit, lose_profit = self.calculate_green_book(
                            entry_price, entry_stake, lay_price, lay_stake
                        )
                        print(f"[AUTO-HEDGE] Forced LAY: ${lay_stake:.2f} @ ${lay_price:.2f}")
                        print(f"[AUTO-HEDGE] If wins: ${win_profit:.2f} | If loses: ${lose_profit:.2f}")
                        
                        bet_id = self.place_lay_bet(market_id, selection_id, lay_price, lay_stake)
                        if bet_id:
                            self.log_hedge(position, lay_price, lay_stake, bet_id, win_profit, lose_profit)
                            return True
                        else:
                            print("[AUTO-HEDGE] Failed to force hedge!")
                            return False
            
            # Check current price
            back_price, lay_price = self.get_current_price(market_id, selection_id)
            
            if back_price is None or lay_price is None:
                print("[AUTO-HEDGE] Could not get price, retrying...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            print(f"  Current: BACK ${back_price:.2f} | LAY ${lay_price:.2f}", end="\r")
            
            # Check if target reached
            if lay_price <= target_price:
                print(f"\n[AUTO-HEDGE] Target reached! LAY price ${lay_price:.2f} <= ${target_price:.2f}")
                
                # Calculate optimal LAY stake
                lay_stake = self.calculate_optimal_lay(entry_price, entry_stake, lay_price)
                
                # Ensure minimum stake of $1.00 for Betfair
                if lay_stake < 1.00:
                    lay_stake = 1.00
                    print(f"[AUTO-HEDGE] Adjusted stake to minimum: $1.00")
                
                # Calculate green book profit
                win_profit, lose_profit = self.calculate_green_book(
                    entry_price, entry_stake, lay_price, lay_stake
                )
                
                print(f"[AUTO-HEDGE] Optimal LAY: ${lay_stake:.2f} @ ${lay_price:.2f}")
                print(f"[AUTO-HEDGE] If wins: ${win_profit:.2f} | If loses: ${lose_profit:.2f}")
                
                # Place LAY bet
                bet_id = self.place_lay_bet(market_id, selection_id, lay_price, lay_stake)
                
                if bet_id:
                    # Log the hedge
                    self.log_hedge(position, lay_price, lay_stake, bet_id, win_profit, lose_profit)
                    return True
                else:
                    print("[AUTO-HEDGE] Failed to place LAY, will retry...")
            
            time.sleep(CHECK_INTERVAL)
        
        print(f"\n[AUTO-HEDGE] Timeout after {MAX_WAIT_SECONDS}s, price never reached target")
        return False
    
    def log_hedge(self, position, lay_price, lay_stake, bet_id, win_profit, lose_profit):
        """Log the completed hedge."""
        runner_name = position.get("runner", position.get("runner_name", "Unknown"))
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "HEDGE",
            "runner_name": runner_name,
            "market_id": position["market_id"],
            "selection_id": position["selection_id"],
            "back": {
                "price": position["entry_price"],
                "stake": position.get("entry_stake", position.get("stake", R_UNIT)),
                "bet_id": position.get("bet_id")
            },
            "lay": {
                "price": lay_price,
                "stake": lay_stake,
                "bet_id": bet_id
            },
            "green_book": {
                "if_wins": round(win_profit, 2),
                "if_loses": round(lose_profit, 2)
            }
        }
        
        # Append to log
        logs = []
        if LIVE_TRADES_LOG.exists():
            try:
                with open(LIVE_TRADES_LOG) as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(LIVE_TRADES_LOG, "w") as f:
            json.dump(logs, f, indent=2)
        
        print(f"[AUTO-HEDGE] Hedge logged")
    
    def run(self):
        """Run auto-hedge on all open positions."""
        print("[AUTO-HEDGE] Starting auto-hedge system...")
        
        if not self.connect():
            return
        
        positions = self.load_open_positions()
        
        if not positions:
            print("[AUTO-HEDGE] No open positions to hedge")
            return
        
        print(f"[AUTO-HEDGE] Found {len(positions)} open positions")
        
        hedged = 0
        remaining_positions = []
        
        for position in positions:
            # Check if already hedged
            if position.get("hedged"):
                print(f"[AUTO-HEDGE] Skipping already hedged: {position.get('runner', position.get('runner_name'))}")
                remaining_positions.append(position)
                continue
            
            # Try to hedge
            success = self.hedge_position(position)
            
            if success:
                position["hedged"] = True
                position["hedge_time"] = datetime.now().isoformat()
                hedged += 1
                remaining_positions.append(position)
            else:
                # Keep position for next attempt
                remaining_positions.append(position)
        
        # Save updated positions
        self.save_open_positions(remaining_positions)
        
        print(f"\n[AUTO-HEDGE] Complete: {hedged}/{len(positions)} positions hedged")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Hedge System")
    parser.add_argument("--watch", action="store_true", help="Watch mode - continuously monitor")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    args = parser.parse_args()
    
    hedge = AutoHedge()
    
    if args.watch:
        print(f"[AUTO-HEDGE] Watch mode - checking every {args.interval}s")
        while True:
            try:
                hedge.run()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n[AUTO-HEDGE] Stopped")
                break
    else:
        hedge.run()


if __name__ == "__main__":
    main()
