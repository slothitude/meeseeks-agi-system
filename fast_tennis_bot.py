#!/usr/bin/env python3
"""
FAST Tennis Paper Trading Bot

Tennis is ideal for overnight trading - matches happening globally.
Min bet: $1.00 AUD

Usage:
    python fast_tennis_bot.py --balance 10 --duration 5
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

STATE_FILE = Path("tennis_paper_state.json")


class FastTennisBot:
    """Fast paper trading for tennis matches"""
    
    def __init__(self, balance=10.00):
        self.balance = balance
        self.starting_balance = balance
        self.session_token = None
        self.trades = []
        self.price_history = {}
        self.load_state()
    
    def load_state(self):
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
                self.balance = state.get('balance', self.starting_balance)
                self.trades = state.get('trades', [])
    
    def save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'balance': self.balance,
                'starting_balance': self.starting_balance,
                'trades': self.trades,
                'updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def login(self):
        payload = f"username={USERNAME}&password={PASSWORD}"
        headers = {
            'X-Application': APP_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            r = requests.post(
                'https://identitysso-cert.betfair.com/api/certlogin',
                data=payload,
                cert=CERT_FILE,
                headers=headers,
                timeout=10
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('loginStatus') == 'SUCCESS':
                    self.session_token = data.get('sessionToken')
                    return True
        except:
            pass
        return False
    
    def api_request(self, method, params):
        """Make API request"""
        if not self.session_token:
            return None
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        try:
            r = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if r.status_code == 200:
                return r.json().get('result')
        except:
            pass
        return None
    
    def get_tennis_markets(self):
        """Get tennis match odds markets"""
        now = datetime.now()
        soon = now + timedelta(hours=3)
        
        result = self.api_request(
            "SportsAPING/v1.0/listMarketCatalogue",
            {
                "filter": {
                    "eventTypeIds": ["2"],  # Tennis
                    "marketTypeCodes": ["MATCH_ODDS"],
                    "marketStartTime": {
                        "from": now.isoformat() + "Z",
                        "to": soon.isoformat() + "Z"
                    }
                },
                "maxResults": 20,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            }
        )
        
        return result or []
    
    def get_prices(self, market_id):
        """Get prices for market"""
        result = self.api_request(
            "SportsAPING/v1.0/listMarketBook",
            {
                "marketIds": [market_id],
                "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
            }
        )
        
        if result:
            return result[0]
        return None
    
    def track_price(self, key, price):
        """Track price history"""
        now = datetime.now()
        
        if key not in self.price_history:
            self.price_history[key] = []
        
        self.price_history[key].append({
            'time': now,
            'price': price
        })
        
        # Keep last 30 seconds
        cutoff = now - timedelta(seconds=30)
        self.price_history[key] = [
            p for p in self.price_history[key] 
            if p['time'] > cutoff
        ]
    
    def get_momentum(self, key):
        """Get price momentum"""
        history = self.price_history.get(key, [])
        
        if len(history) < 3:
            return 0
        
        prices = [p['price'] for p in history]
        first = prices[0]
        last = prices[-1]
        
        if first > 0:
            return (first - last) / first
        return 0
    
    def analyze_opportunity(self, market_id, runner_id, back_price, back_size, lay_price, lay_size):
        """Analyze if there's a trading opportunity"""
        key = f"{market_id}_{runner_id}"
        
        # Track both sides
        self.track_price(key, back_price)
        
        # Calculate spread
        spread = lay_price - back_price
        
        # Tick size
        if back_price < 2.0:
            tick_size = 0.01
        elif back_price < 3.0:
            tick_size = 0.02
        else:
            tick_size = 0.05
        
        spread_ticks = spread / tick_size
        
        # Get momentum
        momentum = self.get_momentum(key)
        
        # Criteria for entry:
        # 1. Tight spread (1-3 ticks)
        # 2. Some liquidity ($20+)
        # 3. Any momentum direction
        
        if spread_ticks <= 3 and back_size >= 20 and lay_size >= 20:
            if momentum > 0.001:
                return "BACK", abs(momentum)
            elif momentum < -0.001:
                return "LAY", abs(momentum)
            elif spread_ticks <= 1:
                # No momentum but tight spread - market make
                return "BACK", 0.01
        
        return None, 0
    
    def run(self, duration_minutes=5):
        """Run trading session"""
        print("="*70)
        print("FAST TENNIS PAPER TRADING BOT")
        print("="*70)
        print(f"Balance: ${self.balance:.2f}")
        print(f"Duration: {duration_minutes} min")
        print(f"Strategy: Tick scalping with momentum")
        print()
        
        if not self.login():
            print("Login failed")
            return
        
        print("Logged in")
        print()
        
        start = datetime.now()
        end_time = start + timedelta(minutes=duration_minutes)
        scan_count = 0
        trade_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            
            # Get markets
            markets = self.get_tennis_markets()
            
            if not markets:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No tennis markets")
                time.sleep(10)
                continue
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan {scan_count}: {len(markets)} markets")
            
            # Show sample prices for debugging
            for market in markets[:2]:
                book = self.get_prices(market.get('marketId'))
                if book and book.get('status') == 'OPEN':
                    for r in book.get('runners', [])[:1]:
                        ex = r.get('ex', {})
                        back = ex.get('availableToBack', [])
                        lay = ex.get('availableToLay', [])
                        if back and lay:
                            print(f"  Sample: BACK {back[0]['price']:.2f} ({back[0]['size']:.0f}) | LAY {lay[0]['price']:.2f} ({lay[0]['size']:.0f})")
                            break
                    break
            
            opportunities = []
            
            for market in markets[:10]:
                market_id = market.get('marketId')
                event_name = market.get('event', {}).get('eventName', 'Unknown')
                
                book = self.get_prices(market_id)
                if not book:
                    continue
                
                status = book.get('status')
                if status != 'OPEN':
                    continue
                
                for runner in market.get('runners', []):
                    runner_id = runner.get('selectionId')
                    runner_name = runner.get('runnerName', 'Unknown')
                    
                    ex = None
                    for r in book.get('runners', []):
                        if r.get('selectionId') == runner_id:
                            ex = r.get('ex', {})
                            break
                    
                    if not ex:
                        continue
                    
                    back = ex.get('availableToBack', [])
                    lay = ex.get('availableToLay', [])
                    
                    if not back or not lay:
                        continue
                    
                    back_price = back[0]['price']
                    back_size = back[0]['size']
                    lay_price = lay[0]['price']
                    lay_size = lay[0]['size']
                    
                    direction, strength = self.analyze_opportunity(
                        market_id, runner_id,
                        back_price, back_size,
                        lay_price, lay_size
                    )
                    
                    if direction:
                        opportunities.append({
                            'market': market,
                            'runner': runner,
                            'direction': direction,
                            'strength': strength,
                            'back_price': back_price,
                            'lay_price': lay_price,
                            'event_name': event_name,
                            'runner_name': runner_name
                        })
            
            # Sort by strength
            opportunities.sort(key=lambda x: x['strength'], reverse=True)
            
            # Take best opportunity
            if opportunities:
                opp = opportunities[0]
                
                print(f"\n  *** SIGNAL: {opp['direction']} {opp['runner_name']}")
                print(f"      Event: {opp['event_name']}")
                print(f"      Price: {opp['back_price']:.2f} / {opp['lay_price']:.2f}")
                print(f"      Strength: {opp['strength']*100:.1f}%")
                
                # Paper trade
                direction = opp['direction']
                stake = 1.0
                
                if direction == "BACK":
                    entry = opp['back_price']
                    # Target 1 tick profit
                    if entry < 2.0:
                        exit_price = entry - 0.01
                    elif entry < 3.0:
                        exit_price = entry - 0.02
                    else:
                        exit_price = entry - 0.05
                    
                    # P&L if exit filled
                    profit = entry - exit_price
                else:  # LAY
                    entry = opp['lay_price']
                    # Target 1 tick profit
                    if entry < 2.0:
                        exit_price = entry + 0.01
                    elif entry < 3.0:
                        exit_price = entry + 0.02
                    else:
                        exit_price = entry + 0.05
                    
                    # LAY P&L
                    profit = exit_price - entry
                
                # Simulate outcome (real would wait for fill)
                # For paper: 60% success rate (momentum following)
                if random.random() < 0.6:
                    outcome = "WIN"
                    self.balance += profit
                else:
                    outcome = "LOSS"
                    self.balance -= 0.02  # Small loss on exit
                    profit = -0.02
                
                trade_count += 1
                
                print(f"\n  >>> TRADE #{trade_count}: {outcome}")
                print(f"      P&L: ${profit:.3f}")
                print(f"      Balance: ${self.balance:.2f}")
                
                self.trades.append({
                    'time': datetime.now().isoformat(),
                    'runner': opp['runner_name'],
                    'direction': direction,
                    'entry': entry,
                    'exit': exit_price,
                    'profit': profit,
                    'outcome': outcome
                })
                
                self.save_state()
                
                # Wait after trade
                time.sleep(5)
            
            # Scan interval
            time.sleep(3)
        
        print("\n" + "="*70)
        print("SESSION COMPLETE")
        print("="*70)
        print(f"Scans: {scan_count}")
        print(f"Trades: {trade_count}")
        print(f"Starting: ${self.starting_balance:.2f}")
        print(f"Final: ${self.balance:.2f}")
        print(f"P&L: ${self.balance - self.starting_balance:.2f}")
        print(f"ROI: {(self.balance - self.starting_balance) / self.starting_balance * 100:.1f}%")
        
        self.save_state()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--balance', type=float, default=10.0)
    parser.add_argument('--duration', type=int, default=5)
    args = parser.parse_args()
    
    bot = FastTennisBot(balance=args.balance)
    bot.run(duration_minutes=args.duration)


if __name__ == "__main__":
    main()
