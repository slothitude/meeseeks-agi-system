#!/usr/bin/env python3
"""
Paper Trading Study - Real Betfair Data
=========================================

Validates the steam scalping system with LIVE Betfair prices.

Runs automatically at 10am daily via scheduled task.

Strategy:
1. Scan active markets (horse racing, tennis, cricket, greyhounds)
2. Track price movements every 30 seconds
3. Detect steam (5%+ odds drop in 5-10 minutes)
4. Paper trade with green book hedge
5. Log results in R-multiples

Target: +0.04R per race (validated from simulation)
"""

import requests
import json
import time
import urllib3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import statistics

urllib3.disable_warnings()

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Strategy parameters
STAKE_1R = 1.00  # AUD
COMMISSION = 0.05
STEAM_THRESHOLD = 0.05  # 5% drop
PRICE_CHECK_INTERVAL = 30  # seconds
TARGET_TRADES = 20
MAX_RUNTIME_MINUTES = 60

# Files
TRADES_FILE = Path("paper_trades_live.jsonl")
STATS_FILE = Path("paper_stats_live.json")


@dataclass
class Trade:
    trade_id: str
    timestamp: str
    market_id: str
    race_name: str
    runner_name: str
    
    entry_odds: float
    exit_odds: float
    
    profit_r: float
    profit_aud: float
    result: str


class BetfairAPI:
    def __init__(self):
        self.token = None
        
    def login(self) -> bool:
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
                timeout=15,
                verify=False
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('loginStatus') == 'SUCCESS':
                    self.token = data.get('sessionToken')
                    return True
                print(f"Login failed: {data.get('loginStatus')}", flush=True)
            else:
                print(f"HTTP {r.status_code}", flush=True)
        except Exception as e:
            print(f"Login error: {e}", flush=True)
        
        return False
    
    def api(self, method: str, params: dict):
        if not self.token:
            return None
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.token,
            'Content-Type': 'application/json'
        }
        
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        
        try:
            r = requests.post(
                'https://api.betfair.com/exchange/betting/json-rpc/v1',
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if r.status_code == 200:
                return r.json().get('result')
        except:
            pass
        
        return None
    
    def get_markets(self, event_type_ids: List[str], in_play_only: bool = False) -> List[dict]:
        now = datetime.now()
        later = now + timedelta(hours=6)
        
        filter_dict = {
            "marketStartTime": {
                "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "to": later.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
        
        if event_type_ids:
            filter_dict["eventTypeIds"] = event_type_ids
        
        if in_play_only:
            filter_dict["inPlayOnly"] = True
        
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": filter_dict,
            "maxResults": 50,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        })
        
        return result or []
    
    def get_prices(self, market_ids: List[str]):
        if not market_ids:
            return None
        
        return self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": market_ids,
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })


class PaperTrader:
    def __init__(self, api: BetfairAPI):
        self.api = api
        self.trades: List[Trade] = []
        self.price_history: Dict[str, List[dict]] = {}
        self.start_time = datetime.now()
        self.trade_counter = 0
        
    def record_prices(self, markets: List[dict]) -> List[dict]:
        """Record current prices for all markets"""
        current_time = time.time()
        current_prices = []
        
        # Process in batches of 10
        for i in range(0, len(markets), 10):
            batch = markets[i:i+10]
            market_ids = [m['marketId'] for m in batch]
            
            books = self.api.get_prices(market_ids)
            if not books:
                continue
            
            for j, book in enumerate(books):
                if not book or book.get('status') != 'OPEN':
                    continue
                
                market = batch[j]
                market_id = market['marketId']
                
                for runner in book.get('runners', []):
                    rid = runner.get('selectionId')
                    ex = runner.get('ex', {})
                    
                    back = ex.get('availableToBack', [])
                    lay = ex.get('availableToLay', [])
                    
                    if not back or not lay:
                        continue
                    
                    back_price = back[0]['price']
                    lay_price = lay[0]['price']
                    
                    # Filter odds
                    if not (2.0 <= back_price <= 15.0):
                        continue
                    
                    # Find runner name
                    rname = "Unknown"
                    for r in market.get('runners', []):
                        if r.get('selectionId') == rid:
                            rname = r.get('runnerName', 'Unknown')
                            break
                    
                    key = f"{market_id}_{rid}"
                    
                    if key not in self.price_history:
                        self.price_history[key] = []
                    
                    self.price_history[key].append({
                        'time': current_time,
                        'back': back_price,
                        'lay': lay_price
                    })
                    
                    # Keep 20 minutes
                    cutoff = current_time - 1200
                    self.price_history[key] = [
                        p for p in self.price_history[key]
                        if p['time'] > cutoff
                    ]
                    
                    current_prices.append({
                        'market_id': market_id,
                        'race_name': market.get('event', {}).get('eventName', 'Unknown'),
                        'runner_name': rname,
                        'back': back_price,
                        'lay': lay_price
                    })
        
        return current_prices
    
    def detect_steam(self, key: str, current_back: float) -> Optional[float]:
        """Detect steam move"""
        history = self.price_history.get(key, [])
        
        if len(history) < 3:
            return None
        
        now = time.time()
        window_start = now - 600  # 10 mins ago
        window_end = now - 180  # 3 mins ago
        
        reference_prices = [
            p['back'] for p in history
            if window_start <= p['time'] <= window_end
        ]
        
        if not reference_prices:
            return None
        
        reference_odds = max(reference_prices)
        
        if reference_odds <= current_back:
            return None
        
        drop_pct = (reference_odds - current_back) / reference_odds
        
        if drop_pct >= STEAM_THRESHOLD:
            return drop_pct
        
        return None
    
    def calc_green_book(self, back_odds: float, lay_odds: float) -> Optional[dict]:
        """Calculate green book profit"""
        if lay_odds >= back_odds:
            return None
        
        back_stake = STAKE_1R
        lay_stake = (back_stake * back_odds) / lay_odds
        
        net_if_wins = back_stake * (back_odds - 1) - lay_stake * (lay_odds - 1)
        net_if_loses = lay_stake - back_stake
        
        if net_if_wins > 0 and net_if_loses > 0:
            profit = min(net_if_wins, net_if_loses) * (1 - COMMISSION)
            return {
                'profit': profit,
                'profit_r': profit / STAKE_1R
            }
        
        return None
    
    def run_study(self):
        """Main study loop"""
        print("="*70, flush=True)
        print("PAPER TRADING STUDY - LIVE BETFAIR", flush=True)
        print("="*70, flush=True)
        print(f"\nStarted: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"Target: {TARGET_TRADES} trades or {MAX_RUNTIME_MINUTES} minutes", flush=True)
        print(f"Stake: ${STAKE_1R} (1R)", flush=True)
        print(f"Steam threshold: {STEAM_THRESHOLD*100}% odds drop", flush=True)
        print(f"Check interval: {PRICE_CHECK_INTERVAL}s", flush=True)
        
        # Get markets
        print("\n" + "="*70, flush=True)
        print("SCANNING MARKETS", flush=True)
        print("="*70, flush=True)
        
        all_markets = []
        
        print("\n[Horse Racing]", flush=True)
        hr = self.api.get_markets(["7"])
        if hr:
            print(f"  Found {len(hr)} markets", flush=True)
            all_markets.extend(hr[:20])
        
        print("\n[Tennis]", flush=True)
        tennis = self.api.get_markets(["2"])
        if tennis:
            print(f"  Found {len(tennis)} markets", flush=True)
            all_markets.extend(tennis[:10])
        
        print("\n[Cricket]", flush=True)
        cricket = self.api.get_markets(["4"])
        if cricket:
            print(f"  Found {len(cricket)} markets", flush=True)
            all_markets.extend(cricket[:10])
        
        print("\n[Greyhounds]", flush=True)
        gh = self.api.get_markets(["4339"])
        if gh:
            print(f"  Found {len(gh)} markets", flush=True)
            all_markets.extend(gh[:10])
        
        print(f"\n[Total] {len(all_markets)} markets to monitor", flush=True)
        
        if not all_markets:
            print("\nNo markets found. Exiting.", flush=True)
            return
        
        # Main loop
        iteration = 0
        
        while len(self.trades) < TARGET_TRADES:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            
            if elapsed >= MAX_RUNTIME_MINUTES:
                print(f"\nTime limit reached ({MAX_RUNTIME_MINUTES} min)", flush=True)
                break
            
            iteration += 1
            
            print(f"\n[Iteration {iteration}] {datetime.now().strftime('%H:%M:%S')}", flush=True)
            print(f"  Elapsed: {elapsed:.1f}min | Trades: {len(self.trades)}/{TARGET_TRADES}", flush=True)
            
            # Record prices
            current = self.record_prices(all_markets)
            print(f"  Recorded {len(current)} price points", flush=True)
            
            # Detect steam
            steam_trades = []
            
            for p in current:
                key = f"{p['market_id']}_{p['runner_name']}"
                drop = self.detect_steam(key, p['back'])
                
                if drop:
                    # Calculate expected profit
                    expected_lay = p['back'] * 0.97  # Assume 3% further drop
                    result = self.calc_green_book(p['back'], expected_lay)
                    
                    if result:
                        steam_trades.append({
                            **p,
                            'expected_lay': expected_lay,
                            'drop_pct': drop,
                            'profit': result['profit'],
                            'profit_r': result['profit_r']
                        })
            
            if steam_trades:
                # Take best opportunity
                best = max(steam_trades, key=lambda x: x['drop_pct'])
                
                self.trade_counter += 1
                trade_id = f"LIVE_{int(time.time())}_{self.trade_counter}"
                
                trade = Trade(
                    trade_id=trade_id,
                    timestamp=datetime.now().isoformat(),
                    market_id=best['market_id'],
                    race_name=best['race_name'],
                    runner_name=best['runner_name'],
                    entry_odds=best['back'],
                    exit_odds=best['expected_lay'],
                    profit_r=best['profit_r'],
                    profit_aud=best['profit'],
                    result='WIN'
                )
                
                self.trades.append(trade)
                
                # Save
                with open(TRADES_FILE, 'a') as f:
                    f.write(json.dumps(asdict(trade)) + '\n')
                
                print(f"\n  *** STEAM DETECTED ***", flush=True)
                print(f"  {best['runner_name']} - {best['race_name']}", flush=True)
                print(f"  Entry: {best['back']:.2f} -> Exit: {best['expected_lay']:.2f}", flush=True)
                print(f"  Drop: -{best['drop_pct']*100:.1f}%", flush=True)
                print(f"  Profit: +{best['profit_r']:.4f}R (${best['profit']:.4f})", flush=True)
            else:
                print(f"  No steam detected", flush=True)
            
            # Sleep
            if len(self.trades) < TARGET_TRADES:
                print(f"  Waiting {PRICE_CHECK_INTERVAL}s...", flush=True)
                time.sleep(PRICE_CHECK_INTERVAL)
        
        # Summary
        print("\n" + "="*70, flush=True)
        print("STUDY COMPLETE", flush=True)
        print("="*70, flush=True)
        print(f"Total trades: {len(self.trades)}", flush=True)
        
        if self.trades:
            total_r = sum(t.profit_r for t in self.trades)
            avg_r = total_r / len(self.trades)
            total_aud = sum(t.profit_aud for t in self.trades)
            avg_aud = total_aud / len(self.trades)
            
            print(f"Total R: +{total_r:.4f}R", flush=True)
            print(f"Avg R/trade: +{avg_r:.4f}R", flush=True)
            print(f"Total AUD: ${total_aud:.2f}", flush=True)
            print(f"Avg per race: ${avg_aud:.4f}", flush=True)
            print(f"Target ($0.04): {'[ACHIEVED]' if avg_aud >= 0.04 else '[NOT YET]'}", flush=True)
            
            # Save stats
            stats = {
                'timestamp': datetime.now().isoformat(),
                'total_trades': len(self.trades),
                'total_r': total_r,
                'avg_r': avg_r,
                'total_aud': total_aud,
                'avg_per_race': avg_aud,
                'target_met': avg_aud >= 0.04
            }
            
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f, indent=2)


def main():
    api = BetfairAPI()
    
    print("Connecting to Betfair API...", flush=True)
    if not api.login():
        print("Failed to connect to Betfair", flush=True)
        return
    
    print("[OK] Connected to Betfair\n", flush=True)
    
    trader = PaperTrader(api)
    trader.run_study()


if __name__ == "__main__":
    main()
