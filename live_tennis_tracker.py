#!/usr/bin/env python3
"""
LIVE Tennis Steam Tracker

Tracks tennis markets overnight (11PM-7AM Brisbane time) when 
Australian horse racing is closed.

Strategy:
- Monitor pre-match tennis odds
- Detect steam moves (odds compression)
- Paper trade for validation

Usage:
    python live_tennis_tracker.py --duration 5
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import urllib3

urllib3.disable_warnings()

USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Strategy params
MIN_BACK_ODDS = 1.5
MAX_BACK_ODDS = 5.0
MIN_ODDS_DROP = 0.05
STAKE_1R = 1.00
COMMISSION = 0.05


class LiveTennisTracker:
    def __init__(self):
        self.token = None
        self.price_history = {}  # {market_runner: [(time, back, lay)]}
        self.trades = []
        
    def login(self):
        payload = f"username={USERNAME}&password={PASSWORD}"
        headers = {'X-Application': APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post('https://identitysso-cert.betfair.com/api/certlogin', 
                         data=payload, cert=CERT_FILE, headers=headers, timeout=15, verify=False)
        if r.status_code == 200:
            data = r.json()
            if data.get('loginStatus') == 'SUCCESS':
                self.token = data.get('sessionToken')
                return True
        return False
    
    def api(self, method, params):
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.token,
            'Content-Type': 'application/json'
        }
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        r = requests.post('https://api.betfair.com/exchange/betting/json-rpc/v1',
                         headers=headers, json=payload, timeout=10)
        return r.json().get('result') if r.status_code == 200 else None
    
    def get_tennis_markets(self, hours=6):
        """Get tennis markets starting soon"""
        now = datetime.now()
        later = now + timedelta(hours=hours)
        
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["2"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {
                    "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": later.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            },
            "maxResults": 50,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        })
        
        return result or []
    
    def get_prices(self, market_id):
        """Get current prices"""
        result = self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        return result[0] if result else None
    
    def track_price(self, key, back, lay):
        """Track price history"""
        now = datetime.now()
        if key not in self.price_history:
            self.price_history[key] = []
        
        self.price_history[key].append({
            'time': now,
            'back': back,
            'lay': lay
        })
        
        # Keep 10 minutes
        cutoff = now - timedelta(minutes=10)
        self.price_history[key] = [
            p for p in self.price_history[key]
            if p['time'] > cutoff
        ]
    
    def get_momentum(self, key):
        """Calculate price momentum"""
        history = self.price_history.get(key, [])
        if len(history) < 2:
            return 0
        
        first = history[0]['back']
        last = history[-1]['back']
        
        if first > 0:
            return (first - last) / first
        return 0
    
    def calc_r_value(self, back_odds, lay_odds):
        """Calculate R-value for BACK @ back_odds, LAY @ lay_odds"""
        if lay_odds >= back_odds:
            return None
        
        odds_drop = back_odds - lay_odds
        if odds_drop < MIN_ODDS_DROP:
            return None
        
        back_stake = STAKE_1R
        lay_stake = (back_stake * back_odds) / lay_odds
        
        back_profit = back_stake * (back_odds - 1)
        lay_liability = lay_stake * (lay_odds - 1)
        net_if_wins = back_profit - lay_liability
        net_if_loses = lay_stake - back_stake
        
        green_profit = min(net_if_wins, net_if_loses) * (1 - COMMISSION)
        r_value = green_profit / STAKE_1R
        
        return {
            'green_profit': green_profit,
            'r_value': r_value,
            'odds_drop': odds_drop
        }
    
    def run(self, duration_min=10):
        """Run tracking session"""
        print("="*70)
        print("LIVE TENNIS STEAM TRACKER")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Duration: {duration_min} min")
        print(f"Strategy: Detect odds compression, paper trade steam")
        print()
        
        if not self.login():
            print("Login failed")
            return
        
        end_time = datetime.now() + timedelta(minutes=duration_min)
        scan_count = 0
        trade_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            
            markets = self.get_tennis_markets(hours=3)
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{scan_count}: {len(markets)} markets")
            
            steam_detected = []
            
            for m in markets:
                mid = m.get('marketId')
                event = m.get('event', {}).get('eventName', 'Unknown')
                start = m.get('marketStartTime')
                
                # Time to start
                if start:
                    try:
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_to_start = (start_dt - datetime.now(start_dt.tzinfo)).total_seconds() / 60
                    except:
                        time_to_start = 999
                else:
                    time_to_start = 999
                
                # Only 2-30 min out
                if time_to_start < 2 or time_to_start > 30:
                    continue
                
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
                    bs = back[0]['size']
                    ls = lay[0]['size']
                    
                    # Filter odds
                    if not (MIN_BACK_ODDS <= bp <= MAX_BACK_ODDS):
                        continue
                    
                    # Track
                    self.track_price(key, bp, lp)
                    
                    # Get momentum
                    mom = self.get_momentum(key)
                    
                    # Display
                    spread = lp - bp
                    print(f"  {rname}: {bp:.2f}/{lp:.2f} Spr:{spread:.2f} Mom:{mom*100:.1f}% T:{time_to_start:.0f}min")
                    
                    # Steam detection
                    if mom > 0.02:  # 2%+ odds compression
                        trade = self.calc_r_value(self.price_history[key][0]['back'], lp)
                        if trade:
                            steam_detected.append({
                                'event': event,
                                'runner': rname,
                                'entry': self.price_history[key][0]['back'],
                                'exit': lp,
                                'momentum': mom,
                                'r_value': trade['r_value'],
                                'profit': trade['green_profit']
                            })
            
            # Trade on steam
            if steam_detected:
                steam_detected.sort(key=lambda x: x['momentum'], reverse=True)
                best = steam_detected[0]
                
                trade_count += 1
                print(f"\n  *** STEAM DETECTED ***")
                print(f"  {best['event']} - {best['runner']}")
                print(f"  BACK @ {best['entry']:.2f} → LAY @ {best['exit']:.2f}")
                print(f"  Momentum: {best['momentum']*100:.1f}%")
                print(f"  R-value: +{best['r_value']:.4f}R")
                print(f"  Profit: +${best['profit']:.4f}")
                
                self.trades.append({
                    'time': datetime.now().isoformat(),
                    'event': best['event'],
                    'runner': best['runner'],
                    'entry': best['entry'],
                    'exit': best['exit'],
                    'r_value': best['r_value']
                })
            
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining > 20:
                print(f"\n  Waiting 20s... ({remaining:.0f}s left)")
                time.sleep(20)
        
        # Summary
        print("\n" + "="*70)
        print("SESSION COMPLETE")
        print("="*70)
        print(f"Scans: {scan_count}")
        print(f"Steam trades: {trade_count}")
        
        if self.trades:
            total_r = sum(t['r_value'] for t in self.trades)
            print(f"Total R: +{total_r:.4f}R")
            print(f"Paper profit: +${total_r * STAKE_1R:.4f}")
            
            # Save
            with open('tennis_trades.json', 'w') as f:
                json.dump(self.trades, f, indent=2)
            print(f"\n[OK] Trades saved to tennis_trades.json")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=10)
    args = parser.parse_args()
    
    tracker = LiveTennisTracker()
    tracker.run(duration_min=args.duration)
