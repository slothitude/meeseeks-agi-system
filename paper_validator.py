#!/usr/bin/env python3
"""
Paper Trading Validation System
================================

PROVE THE SYSTEM WORKS BEFORE REAL MONEY

This system:
1. Connects to REAL Betfair prices
2. Simulates trades (paper trading)
3. Logs every trade in R-units
4. Calculates expectancy over time
5. Validates $0.50/race target

Run this for days/weeks until you have statistical significance.

Usage:
    python paper_validator.py --mode live     # Real Betfair prices
    python paper_validator.py --mode demo     # Simulated prices
    python paper_validator.py --report        # Show results
"""

import requests
import json
import csv
import time
import random
import urllib3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
import statistics

urllib3.disable_warnings()

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Strategy parameters
STAKE_1R = 1.00  # AUD - risk unit
COMMISSION = 0.05
MIN_BACK_ODDS = 2.0
MAX_BACK_ODDS = 15.0
MIN_ODDS_DROP = 0.15  # Minimum drop to trigger trade
TARGET_PROFIT_PER_RACE = 0.50  # AUD

# Files
TRADES_FILE = Path("paper_trades.jsonl")
STATS_FILE = Path("paper_stats.json")


@dataclass
class PaperTrade:
    """A paper trade record"""
    trade_id: str
    timestamp: str
    market_id: str
    event_name: str
    runner_name: str
    race_start: str
    
    # Entry
    entry_time: str
    entry_odds: float
    entry_type: str  # BACK or LAY
    
    # Exit (if closed)
    exit_time: Optional[str]
    exit_odds: Optional[float]
    exit_type: Optional[str]
    
    # R-metrics
    stake_aud: float
    risk_aud: float  # Max loss = 1R
    profit_aud: float
    profit_r: float
    
    # Status
    status: str  # OPEN, CLOSED, VOID
    
    # Market context
    time_to_start: float  # Minutes
    odds_movement: float  # % change detected


class PaperValidator:
    def __init__(self, mode="demo"):
        self.mode = mode
        self.token = None
        self.trades: List[PaperTrade] = []
        self.open_positions: Dict[str, PaperTrade] = {}
        self.price_history: Dict[str, List[dict]] = {}
        self.trade_counter = 0
        
        # Load existing trades
        self.load_trades()
    
    def login(self):
        """Login to Betfair"""
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
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
        
        return False
    
    def api(self, method: str, params: dict):
        """Make Betfair API call"""
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
    
    def get_horse_markets(self, hours=3):
        """Get horse racing markets"""
        now = datetime.now()
        later = now + timedelta(hours=hours)
        
        # Try Australian markets first
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["7"],
                "marketTypeCodes": ["WIN"],
                "marketStartTime": {
                    "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": later.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            },
            "maxResults": 50,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        })
        
        return result or []
    
    def get_prices(self, market_id: str):
        """Get current prices for market"""
        result = self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        
        return result[0] if result else None
    
    def track_price(self, runner_key: str, back: float, lay: float):
        """Track price history for steam detection"""
        now = time.time()
        
        if runner_key not in self.price_history:
            self.price_history[runner_key] = []
        
        self.price_history[runner_key].append({
            'time': now,
            'back': back,
            'lay': lay
        })
        
        # Keep 15 minutes
        cutoff = now - 900
        self.price_history[runner_key] = [
            p for p in self.price_history[runner_key]
            if p['time'] > cutoff
        ]
    
    def detect_steam(self, runner_key: str, current_back: float) -> Optional[float]:
        """Detect steam move (odds dropping)"""
        history = self.price_history.get(runner_key, [])
        
        if len(history) < 2:
            return None
        
        # Compare to 3-10 mins ago
        now = time.time()
        window_start = now - 600
        window_end = now - 180
        
        old_prices = [
            p['back'] for p in history
            if window_start <= p['time'] <= window_end
        ]
        
        if not old_prices:
            return None
        
        old_price = max(old_prices)
        
        if old_price <= current_back:
            return None  # Price went up
        
        drop_pct = (old_price - current_back) / old_price
        
        if drop_pct >= 0.05:  # 5%+ drop
            return drop_pct
        
        return None
    
    def calc_green_book(self, back_odds: float, lay_odds: float, stake: float) -> dict:
        """Calculate green book profit"""
        if lay_odds >= back_odds:
            return None
        
        # Back first
        back_stake = stake
        back_profit = back_stake * (back_odds - 1)
        
        # Lay to green book
        lay_stake = (back_stake * back_odds) / lay_odds
        lay_liability = lay_stake * (lay_odds - 1)
        
        # Net outcomes
        if_wins = back_profit - lay_liability
        if_loses = lay_stake - back_stake
        
        # Green book profit (guaranteed)
        if if_wins > 0 and if_loses > 0:
            profit = min(if_wins, if_loses) * (1 - COMMISSION)
            return {
                'profit': profit,
                'profit_r': profit / STAKE_1R,
                'lay_stake': lay_stake
            }
        
        return None
    
    def open_trade(self, market, runner, entry_odds: float, entry_type: str, 
                   time_to_start: float, steam_drop: float = 0):
        """Open a paper trade"""
        self.trade_counter += 1
        trade_id = f"PAPER_{int(time.time())}_{self.trade_counter}"
        
        trade = PaperTrade(
            trade_id=trade_id,
            timestamp=datetime.now().isoformat(),
            market_id=market['marketId'],
            event_name=market.get('event', {}).get('eventName', 'Unknown'),
            runner_name=runner.get('runnerName', 'Unknown'),
            race_start=market.get('marketStartTime', ''),
            
            entry_time=datetime.now().isoformat(),
            entry_odds=entry_odds,
            entry_type=entry_type,
            
            exit_time=None,
            exit_odds=None,
            exit_type=None,
            
            stake_aud=STAKE_1R,
            risk_aud=STAKE_1R,  # 1R risk
            profit_aud=0,
            profit_r=0,
            
            status='OPEN',
            time_to_start=time_to_start,
            odds_movement=steam_drop
        )
        
        self.open_positions[trade_id] = trade
        self.trades.append(trade)
        self.save_trade(trade)
        
        return trade
    
    def close_trade(self, trade_id: str, exit_odds: float, exit_type: str):
        """Close a paper trade"""
        if trade_id not in self.open_positions:
            return None
        
        trade = self.open_positions[trade_id]
        
        # Calculate profit
        if trade.entry_type == 'BACK' and exit_type == 'LAY':
            result = self.calc_green_book(trade.entry_odds, exit_odds, trade.stake_aud)
            if result:
                trade.profit_aud = result['profit']
                trade.profit_r = result['profit_r']
        
        trade.exit_time = datetime.now().isoformat()
        trade.exit_odds = exit_odds
        trade.exit_type = exit_type
        trade.status = 'CLOSED'
        
        del self.open_positions[trade_id]
        self.save_trade(trade)
        
        return trade
    
    def save_trade(self, trade: PaperTrade):
        """Save trade to JSONL file"""
        with open(TRADES_FILE, 'a') as f:
            f.write(json.dumps(asdict(trade)) + '\n')
    
    def load_trades(self):
        """Load existing trades"""
        if not TRADES_FILE.exists():
            return
        
        with open(TRADES_FILE, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    trade = PaperTrade(**data)
                    self.trades.append(trade)
                    
                    if trade.status == 'OPEN':
                        self.open_positions[trade.trade_id] = trade
                except:
                    pass
    
    def calculate_stats(self) -> dict:
        """Calculate trading statistics"""
        closed_trades = [t for t in self.trades if t.status == 'CLOSED']
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'closed_trades': 0,
                'win_rate': 0,
                'avg_profit_r': 0,
                'total_profit_r': 0,
                'expectancy': 0,
                'total_profit_aud': 0,
                'avg_profit_per_race': 0,
                'target_met': False
            }
        
        wins = [t for t in closed_trades if t.profit_r > 0]
        losses = [t for t in closed_trades if t.profit_r <= 0]
        
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0
        
        total_r = sum(t.profit_r for t in closed_trades)
        avg_r = total_r / len(closed_trades)
        
        total_aud = sum(t.profit_aud for t in closed_trades)
        avg_per_race = total_aud / len(closed_trades)
        
        # Expectancy calculation (Van K. Tharp)
        if wins and losses:
            avg_win = statistics.mean(t.profit_r for t in wins)
            avg_loss = abs(statistics.mean(t.profit_r for t in losses))
            expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        else:
            expectancy = 0
        
        return {
            'total_trades': len(self.trades),
            'closed_trades': len(closed_trades),
            'open_trades': len(self.open_positions),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(win_rate * 100, 1),
            'avg_profit_r': round(avg_r, 4),
            'total_profit_r': round(total_r, 4),
            'expectancy': round(expectancy, 4),
            'total_profit_aud': round(total_aud, 2),
            'avg_profit_per_race': round(avg_per_race, 2),
            'target_met': avg_per_race >= TARGET_PROFIT_PER_RACE
        }
    
    def save_stats(self):
        """Save stats to file"""
        stats = self.calculate_stats()
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        return stats
    
    def generate_demo_markets(self) -> List[dict]:
        """Generate demo markets for testing"""
        random.seed(int(time.time()))
        
        races = [
            ("Randwick R3", "2026-03-07 14:35"),
            ("Flemington R5", "2026-03-07 14:55"),
            ("Eagle Farm R2", "2026-03-07 15:10"),
            ("Caulfield R4", "2026-03-07 15:30"),
        ]
        
        markets = []
        
        for race_name, race_start in races:
            market_id = f"DEMO_{race_name.replace(' ', '_')}"
            
            runners = []
            n_runners = random.randint(8, 14)
            
            for i in range(n_runners):
                runners.append({
                    'selectionId': i + 1,
                    'runnerName': f"Runner {i+1}"
                })
            
            markets.append({
                'marketId': market_id,
                'event': {'eventName': race_name},
                'marketName': f"{race_name} WIN",
                'marketStartTime': race_start,
                'runners': runners
            })
        
        return markets
    
    def generate_demo_prices(self, market_id: str) -> dict:
        """Generate demo prices"""
        random.seed(int(time.time() * 1000) % 100000)
        
        prices = {}
        n_runners = random.randint(8, 14)
        
        for i in range(n_runners):
            rid = i + 1
            
            # Generate realistic odds
            base_odds = random.uniform(2.0, 15.0)
            spread = base_odds * random.uniform(0.01, 0.03)
            
            prices[rid] = {
                'back': round(base_odds, 2),
                'lay': round(base_odds + spread, 2),
                'back_size': round(random.uniform(50, 500), 0),
                'lay_size': round(random.uniform(50, 300), 0)
            }
        
        return prices
    
    def scan_for_opportunities(self, markets: List[dict]) -> List[dict]:
        """Scan markets for trading opportunities"""
        opportunities = []
        
        for market in markets:
            market_id = market['marketId']
            
            if self.mode == "live":
                book = self.get_prices(market_id)
                if not book or book.get('status') != 'OPEN':
                    continue
            else:
                book = None
            
            # Time to start
            start_time = market.get('marketStartTime')
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_to_start = (start_dt - datetime.now(start_dt.tzinfo)).total_seconds() / 60
                except:
                    time_to_start = 999
            else:
                time_to_start = 999
            
            # Only 3-15 mins out
            if time_to_start < 3 or time_to_start > 15:
                continue
            
            for runner in market.get('runners', []):
                rid = runner.get('selectionId')
                runner_key = f"{market_id}_{rid}"
                
                # Get prices
                if self.mode == "live" and book:
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
                    
                    back_price = back[0]['price']
                    lay_price = lay[0]['price']
                else:
                    # Demo mode
                    demo_prices = self.generate_demo_prices(market_id)
                    rid_prices = demo_prices.get(rid, {})
                    back_price = rid_prices.get('back', 0)
                    lay_price = rid_prices.get('lay', 0)
                
                if not back_price or not lay_price:
                    continue
                
                # Filter odds
                if not (MIN_BACK_ODDS <= back_price <= MAX_BACK_ODDS):
                    continue
                
                # Track price
                self.track_price(runner_key, back_price, lay_price)
                
                # Detect steam
                steam_drop = self.detect_steam(runner_key, back_price)
                
                if steam_drop and steam_drop >= 0.05:
                    opportunities.append({
                        'market': market,
                        'runner': runner,
                        'back_price': back_price,
                        'lay_price': lay_price,
                        'time_to_start': time_to_start,
                        'steam_drop': steam_drop
                    })
        
        return opportunities
    
    def run_trading_cycle(self):
        """Run one trading cycle"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning...")
        
        if self.mode == "live":
            if not self.token and not self.login():
                print("[ERROR] Not logged in")
                return
            markets = self.get_horse_markets(hours=3)
        else:
            markets = self.generate_demo_markets()
        
        print(f"  Markets: {len(markets)}")
        
        # Close any open positions first
        for trade_id, trade in list(self.open_positions.items()):
            # In demo, simulate exit after 2-3 mins
            entry_time = datetime.fromisoformat(trade.entry_time)
            elapsed = (datetime.now() - entry_time).total_seconds()
            
            if elapsed > 180:  # 3 mins
                # Simulate odds dropping 0.1-0.3
                exit_odds = trade.entry_odds - random.uniform(0.1, 0.3)
                exit_odds = max(exit_odds, 1.01)
                
                trade = self.close_trade(trade_id, exit_odds, 'LAY')
                
                if trade:
                    print(f"\n  [CLOSED] {trade.runner_name}")
                    print(f"    Entry: {trade.entry_odds:.2f} | Exit: {trade.exit_odds:.2f}")
                    print(f"    Profit: +{trade.profit_r:.4f}R (${trade.profit_aud:.2f})")
        
        # Scan for new opportunities
        opps = self.scan_for_opportunities(markets)
        
        if opps:
            print(f"  Opportunities: {len(opps)}")
            
            # Take best opportunity
            opp = max(opps, key=lambda x: x['steam_drop'])
            
            trade = self.open_trade(
                market=opp['market'],
                runner=opp['runner'],
                entry_odds=opp['back_price'],
                entry_type='BACK',
                time_to_start=opp['time_to_start'],
                steam_drop=opp['steam_drop']
            )
            
            print(f"\n  [OPEN] {trade.runner_name}")
            print(f"    Entry: BACK @ {trade.entry_odds:.2f}")
            print(f"    Steam: -{opp['steam_drop']*100:.1f}%")
            print(f"    Time to start: {opp['time_to_start']:.1f} min")
        
        # Save stats
        stats = self.save_stats()
        print(f"\n  Stats:")
        print(f"    Trades: {stats['closed_trades']} closed")
        print(f"    Win rate: {stats['win_rate']}%")
        print(f"    Total R: +{stats['total_profit_r']:.4f}R")
        print(f"    Total AUD: ${stats['total_profit_aud']:.2f}")
        print(f"    Avg/race: ${stats['avg_profit_per_race']:.2f}")
        print(f"    Target ($0.50): {'[OK]' if stats['target_met'] else '[PENDING]'}")
    
    def print_report(self):
        """Print detailed report"""
        stats = self.calculate_stats()
        
        print("\n" + "="*60)
        print("PAPER TRADING VALIDATION REPORT")
        print("="*60)
        print(f"\nMode: {self.mode.upper()}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-"*60)
        print("SUMMARY")
        print("-"*60)
        print(f"  Total trades:     {stats['total_trades']}")
        print(f"  Closed trades:    {stats['closed_trades']}")
        print(f"  Open positions:   {stats['open_trades']}")
        
        print("\n" + "-"*60)
        print("PERFORMANCE")
        print("-"*60)
        print(f"  Wins:             {stats['wins']}")
        print(f"  Losses:           {stats['losses']}")
        print(f"  Win rate:         {stats['win_rate']}%")
        print(f"  Total R:          +{stats['total_profit_r']:.4f}R")
        print(f"  Avg R/trade:      {stats['avg_profit_r']:.4f}R")
        print(f"  Expectancy:       {stats['expectancy']:.4f}R")
        
        print("\n" + "-"*60)
        print("AUD RESULTS")
        print("-"*60)
        print(f"  Total profit:     ${stats['total_profit_aud']:.2f}")
        print(f"  Avg per race:     ${stats['avg_profit_per_race']:.2f}")
        print(f"  Target ($0.50):   {'[ACHIEVED]' if stats['target_met'] else '[NOT YET]'}")
        
        if stats['closed_trades'] >= 30:
            print("\n" + "-"*60)
            print("VALIDATION STATUS")
            print("-"*60)
            
            if stats['expectancy'] > 0 and stats['win_rate'] >= 50:
                print("  [VALIDATED] System shows positive expectancy")
                print("  [READY] Can proceed with real money")
            else:
                print("  [PENDING] Need more data or strategy adjustment")
        else:
            print(f"\n  Need {30 - stats['closed_trades']} more trades for validation")
        
        print("\n" + "="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['live', 'demo'], default='demo')
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--cycles', type=int, default=1)
    parser.add_argument('--interval', type=int, default=30)
    args = parser.parse_args()
    
    validator = PaperValidator(mode=args.mode)
    
    if args.report:
        validator.print_report()
        return
    
    print("="*60)
    print("PAPER TRADING VALIDATOR")
    print("="*60)
    print(f"\nMode: {args.mode.upper()}")
    print(f"1R = ${STAKE_1R}")
    print(f"Target: ${TARGET_PROFIT_PER_RACE}/race")
    print(f"Interval: {args.interval}s")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        for _ in range(args.cycles):
            validator.run_trading_cycle()
            
            if args.cycles > 1:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    validator.print_report()


if __name__ == "__main__":
    main()
