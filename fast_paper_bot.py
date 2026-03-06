#!/usr/bin/env python3
"""
FAST Betfair Paper Trading Bot

Min bet: $1.00 AUD
Strategy: Pre-race tick scalping with ladders

Usage:
    python fast_paper_bot.py --balance 10 --duration 5
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

STATE_FILE = Path("fast_paper_state.json")


class FastPaperBot:
    """Fast paper trading with real market data"""
    
    def __init__(self, balance=10.00):
        self.balance = balance
        self.starting_balance = balance
        self.session_token = None
        self.trades = []
        self.positions = []
        self.price_history = {}  # {market_runner: [(time, price)]}
        
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
            'positions': self.positions,
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
    
    def get_markets(self):
        """Get live horse racing markets"""
        if not self.session_token:
            return []
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        now = datetime.now()
        soon = now + timedelta(hours=1)
        
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketCatalogue",
            "params": {
                "filter": {
                    "eventTypeIds": ["1"],  # Horse racing
                    "marketTypeCodes": ["WIN"],
                    "marketStartTime": {
                        "from": now.isoformat() + "Z",
                        "to": soon.isoformat() + "Z"
                    }
                },
                "maxResults": 20,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            },
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
                return r.json().get('result', [])
        except:
            pass
        return []
    
    def get_prices(self, market_id):
        """Get current prices for market"""
        if not self.session_token:
            return None
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketBook",
            "params": {
                "marketIds": [market_id],
                "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
            },
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
                result = r.json().get('result', [])
                if result:
                    return result[0]
        except:
            pass
        return None
    
    def track_price(self, market_id, runner_id, price, size):
        """Track price for momentum analysis"""
        key = f"{market_id}_{runner_id}"
        now = datetime.now()
        
        if key not in self.price_history:
            self.price_history[key] = []
        
        self.price_history[key].append({
            'time': now,
            'price': price,
            'size': size
        })
        
        # Keep last 30 seconds only
        cutoff = now - timedelta(seconds=30)
        self.price_history[key] = [
            p for p in self.price_history[key] 
            if p['time'] > cutoff
        ]
    
    def get_momentum(self, market_id, runner_id):
        """Calculate price momentum (-1 to +1)"""
        key = f"{market_id}_{runner_id}"
        history = self.price_history.get(key, [])
        
        if len(history) < 3:
            return 0
        
        prices = [p['price'] for p in history]
        if len(prices) < 2:
            return 0
        
        # Simple momentum: (first - last) / first
        first = prices[0]
        last = prices[-1]
        
        if first > 0:
            return (first - last) / first
        return 0
    
    def find_opportunity(self, market_id, runner_id, back_price, back_size, lay_price, lay_size):
        """Find scalping opportunity"""
        # Track price
        self.track_price(market_id, runner_id, back_price, back_size)
        self.track_price(market_id, runner_id, lay_price, lay_size)
        
        # Calculate spread in ticks
        spread = lay_price - back_price
        
        # Tick sizes vary by price range
        if back_price < 2.0:
            tick_size = 0.01
        elif back_price < 3.0:
            tick_size = 0.02
        elif back_price < 4.0:
            tick_size = 0.05
        elif back_price < 6.0:
            tick_size = 0.1
        elif back_price < 10.0:
            tick_size = 0.2
        elif back_price < 20.0:
            tick_size = 0.5
        else:
            tick_size = 1.0
        
        spread_ticks = spread / tick_size
        
        # Get momentum
        momentum = self.get_momentum(market_id, runner_id)
        
        # Opportunity criteria:
        # 1. Tight spread (1-2 ticks)
        # 2. Good liquidity ($100+)
        # 3. Momentum in one direction
        
        if spread_ticks <= 2 and back_size >= 100 and lay_size >= 100:
            # Direction based on momentum
            if momentum > 0.005:
                direction = "BACK"  # Price shortening
                confidence = min(abs(momentum) * 100, 50)
            elif momentum < -0.005:
                direction = "LAY"  # Price drifting
                confidence = min(abs(momentum) * 100, 50)
            else:
                direction = "WAIT"
                confidence = 0
            
            return {
                'spread_ticks': spread_ticks,
                'direction': direction,
                'confidence': confidence,
                'momentum': momentum,
                'liquidity': min(back_size, lay_size)
            }
        
        return None
    
    def paper_trade(self, opp, market, runner, stake=1.0):
        """Execute paper trade"""
        direction = opp['direction']
        confidence = opp['confidence']
        
        if direction == "WAIT":
            return None
        
        # Get current prices
        book = self.get_prices(market['marketId'])
        if not book:
            return None
        
        for r in book.get('runners', []):
            if r.get('selectionId') == runner['selectionId']:
                ex = r.get('ex', {})
                back = ex.get('availableToBack', [])
                lay = ex.get('availableToLay', [])
                
                if not back or not lay:
                    return None
                
                back_price = back[0]['price']
                lay_price = lay[0]['price']
                
                # Calculate P&L
                if direction == "BACK":
                    # BACK now, expect to LAY lower
                    entry_price = back_price
                    exit_price = back_price - 0.02  # Target 1 tick profit
                    if exit_price < lay_price:
                        # Can't exit at profit
                        return None
                    
                    # Simulate: if we BACK $1 @ entry_price
                    # And LAY $1 @ exit_price
                    # Win: +$1 * (entry_price - 1) - $1 * (exit_price - 1) = +$(entry - exit)
                    # Lose: -$1 + $1 = $0
                    profit_if_win = entry_price - exit_price
                    profit_if_lose = 0
                    
                else:  # LAY
                    # LAY now, expect to BACK higher
                    entry_price = lay_price
                    exit_price = lay_price + 0.02  # Target 1 tick profit
                    if exit_price > back_price:
                        return None
                    
                    # LAY $1 @ entry_price, BACK $1 @ exit_price
                    # Win: +$1 - $1 * (entry_price - 1) = +$(2 - entry_price)
                    # Lose: -$1 * (exit_price - 1) + $1 = +$(2 - exit_price)
                    profit_if_win = 2 - entry_price
                    profit_if_lose = 2 - exit_price
                
                # Record trade
                trade = {
                    'time': datetime.now().isoformat(),
                    'market': market.get('event', {}).get('eventName', 'Unknown'),
                    'runner': runner.get('runnerName', 'Unknown'),
                    'direction': direction,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'stake': stake,
                    'confidence': confidence,
                    'profit_if_win': profit_if_win,
                    'profit_if_lose': profit_if_lose,
                    'status': 'PAPER'
                }
                
                self.trades.append(trade)
                
                # Simulate outcome (50/50 for paper trading)
                import random
                if random.random() > 0.5:
                    profit = profit_if_win
                    outcome = "WIN"
                else:
                    profit = profit_if_lose
                    outcome = "LOSE"
                
                self.balance += profit
                
                return {
                    'trade': trade,
                    'outcome': outcome,
                    'profit': profit,
                    'new_balance': self.balance
                }
        
        return None
    
    def run(self, duration_minutes=5):
        """Run paper trading session"""
        print("="*70)
        print("FAST PAPER TRADING BOT")
        print("="*70)
        print(f"Balance: ${self.balance:.2f}")
        print(f"Duration: {duration_minutes} min")
        print(f"Strategy: Tick scalping with momentum")
        print()
        
        if not self.login():
            print("Login failed")
            return
        
        print("Logged in successfully")
        print()
        
        start = datetime.now()
        end_time = start + timedelta(minutes=duration_minutes)
        scan_count = 0
        trade_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            
            # Get markets
            markets = self.get_markets()
            
            if not markets:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No markets found")
                time.sleep(5)
                continue
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{scan_count}: {len(markets)} markets")
            
            # Check each market
            for market in markets[:5]:  # Top 5 markets
                market_id = market.get('marketId')
                event_name = market.get('event', {}).get('eventName', 'Unknown')
                
                # Get prices
                book = self.get_prices(market_id)
                
                if not book:
                    continue
                
                # Check each runner
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
                    
                    # Find opportunity
                    opp = self.find_opportunity(
                        market_id, runner_id,
                        back_price, back_size,
                        lay_price, lay_size
                    )
                    
                    if opp and opp['direction'] != "WAIT":
                        print(f"\n  OPPORTUNITY: {runner_name}")
                        print(f"    {opp['direction']} @ {back_price if opp['direction']=='BACK' else lay_price:.2f}")
                        print(f"    Spread: {opp['spread_ticks']:.1f} ticks")
                        print(f"    Momentum: {opp['momentum']*100:.1f}%")
                        print(f"    Confidence: {opp['confidence']}%")
                        
                        # Execute paper trade
                        result = self.paper_trade(opp, market, runner)
                        
                        if result:
                            trade_count += 1
                            print(f"\n  TRADE #{trade_count}: {result['outcome']}")
                            print(f"    Profit: ${result['profit']:.3f}")
                            print(f"    Balance: ${result['new_balance']:.2f}")
                            
                            self.save_state()
                
                # Brief pause
                time.sleep(2)
        
        print("\n" + "="*70)
        print("SESSION COMPLETE")
        print("="*70)
        print(f"Scans: {scan_count}")
        print(f"Trades: {trade_count}")
        print(f"Starting Balance: {self.starting_balance:.2f}")
        print(f"Final Balance: {self.balance:.2f}")
        print(f"P&L: {self.balance - self.starting_balance:.2f}")
        print(f"ROI: {(self.balance - self.starting_balance) / self.starting_balance * 100:.1f}%")
        
        self.save_state()


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--balance', type=float, default=10.0)
    parser.add_argument('--duration', type=int, default=5)
    
    args = parser.parse_args()
    
    bot = FastPaperBot(balance=args.balance)
    bot.run(duration_minutes=args.duration)


if __name__ == "__main__":
    main()
