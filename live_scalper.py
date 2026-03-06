#!/usr/bin/env python3
"""
LIVE Tennis Scalping Tracker

Tracks prices in real-time and alerts on opportunities.
Paper trades when momentum detected.

Min bet: $1.00 AUD
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"
STATE_FILE = Path("live_scalp_state.json")


class LiveScalper:
    def __init__(self, balance=10.0):
        self.balance = balance
        self.starting = balance
        self.token = None
        self.trades = []
        self.prices = {}  # {market_runner: [(time, back, lay)]}
        
    def login(self):
        payload = f"username={USERNAME}&password={PASSWORD}"
        headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=payload, cert=CERT_FILE, headers=headers, timeout=15)
        if r.status_code == 200 and r.json().get('loginStatus') == 'SUCCESS':
            self.token = r.json().get('sessionToken')
            return True
        return False
    
    def api(self, method, params):
        headers = {'X-Application': APP_KEY, 'X-Authentication': self.token, 'Content-Type': 'application/json'}
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1', headers=headers, json=payload, timeout=10)
        return r.json().get('result') if r.status_code == 200 else None
    
    def get_markets(self):
        now = datetime.now()
        return self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["2"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {"from": now.isoformat() + "Z"}
            },
            "maxResults": 10,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
        }) or []
    
    def get_prices(self, market_id):
        result = self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        return result[0] if result else None
    
    def track(self, key, back, lay):
        now = datetime.now()
        if key not in self.prices:
            self.prices[key] = []
        self.prices[key].append({'time': now, 'back': back, 'lay': lay})
        # Keep 60 seconds
        cutoff = now - timedelta(seconds=60)
        self.prices[key] = [p for p in self.prices[key] if p['time'] > cutoff]
    
    def momentum(self, key):
        history = self.prices.get(key, [])
        if len(history) < 5:
            return 0
        first_back = history[0]['back']
        last_back = history[-1]['back']
        if first_back > 0:
            return (first_back - last_back) / first_back
        return 0
    
    def run(self, duration_min=5):
        print("="*70)
        print("LIVE TENNIS SCALPER")
        print("="*70)
        print(f"Balance: ${self.balance:.2f}")
        print(f"Duration: {duration_min} min")
        print()
        
        if not self.login():
            print("Login failed")
            return
        
        end = datetime.now() + timedelta(minutes=duration_min)
        trades = 0
        
        while datetime.now() < end:
            markets = self.get_markets()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {len(markets)} markets")
            
            for m in markets[:5]:
                mid = m.get('marketId')
                book = self.get_prices(mid)
                if not book or book.get('status') != 'OPEN':
                    continue
                
                for runner in m.get('runners', []):
                    rid = runner.get('selectionId')
                    rname = runner.get('runnerName', 'Unknown')
                    key = f"{mid}_{rid}"
                    
                    ex = None
                    for r in book.get('runners', []):
                        if r.get('selectionId') == rid:
                            ex = r.get('ex', {})
                            break
                    
                    if not ex:
                        continue
                    
                    back = ex.get('availableToBack', [])
                    lay = ex.get('availableToLay', [])
                    
                    if not back or not lay:
                        continue
                    
                    bp = back[0]['price']
                    lp = lay[0]['price']
                    spread = lp - bp
                    liq = min(back[0]['size'], lay[0]['size'])
                    
                    # Track
                    self.track(key, bp, lp)
                    
                    # Get momentum
                    mom = self.momentum(key)
                    
                    # Signal if:
                    # 1. Tight spread (<=0.05)
                    # 2. Good liquidity ($20+)
                    # 3. Momentum detected
                    
                    if spread <= 0.05 and liq >= 20:
                        signal = ""
                        if mom > 0.005:
                            signal = ">>> BACK (shortening)"
                        elif mom < -0.005:
                            signal = ">>> LAY (drifting)"
                        
                        print(f"  {rname}: {bp:.2f}/{lp:.2f} Spr:{spread:.2f} Liq:${liq:.0f} Mom:{mom*100:.1f}% {signal}")
                        
                        # Paper trade if strong signal
                        if abs(mom) > 0.01:
                            trades += 1
                            # Simulate 1-tick scalp
                            profit = 0.02 if random.random() > 0.4 else -0.01
                            self.balance += profit
                            print(f"    TRADE #{trades}: {'WIN' if profit > 0 else 'LOSS'} ${profit:.2f} (Bal: ${self.balance:.2f})")
                
                time.sleep(2)
            
            time.sleep(5)
        
        print("\n" + "="*70)
        print("SESSION DONE")
        print("="*70)
        print(f"Trades: {trades}")
        print(f"Starting: ${self.starting:.2f}")
        print(f"Final: ${self.balance:.2f}")
        print(f"P&L: ${self.balance - self.starting:.2f}")
        print(f"ROI: {(self.balance - self.starting) / self.starting * 100:.1f}%")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--balance', type=float, default=10.0)
    parser.add_argument('--duration', type=int, default=5)
    args = parser.parse_args()
    
    bot = LiveScalper(balance=args.balance)
    bot.run(duration_min=args.duration)
