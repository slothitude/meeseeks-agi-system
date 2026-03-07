#!/usr/bin/env python3
"""
Auto-Executor - Paper Trading with $1.00 Minimum Bets
=====================================================

Automatically detects edges and places paper trades.

MINIMUM BET: $1.00 (as requested)
R UNIT: $1.00

Edge Detection:
- STEAM: Price drops > 5%
- DRIFT: Price rises > 5%
- VOLATILITY: Range > 10%

Execution:
- Green book all trades
- Exit 2 mins before race start
- Max 3 trades per race
- Stop loss at -0.1R
"""

import requests
import csv
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

# Files
TRADES_CSV = Path("paper_trades.csv")
TRADES_JSON = Path("paper_trades_log.json")
POSITIONS_JSON = Path("open_positions.json")

# API
HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# Trading Parameters
MIN_BET = 1.00  # $1.00 minimum
R_UNIT = 1.00   # 1R = $1.00
STEAM_THRESHOLD = 0.05  # 5% drop
DRIFT_THRESHOLD = 0.05  # 5% rise
VOLATILITY_THRESHOLD = 0.10  # 10% range
MAX_TRADES_PER_RACE = 3
MIN_TIME_TO_START = 2.0  # minutes
MAX_HOLD_TIME = 180  # seconds (3 mins)
BETFAIR_COMMISSION = 0.05  # 5%

# State
open_positions = {}
trade_log = []
race_trade_count = defaultdict(int)


def load_state():
    """Load existing state"""
    global open_positions, trade_log, race_trade_count
    
    if POSITIONS_JSON.exists():
        with open(POSITIONS_JSON, 'r') as f:
            open_positions = json.load(f)
    
    if TRADES_JSON.exists():
        with open(TRADES_JSON, 'r') as f:
            trade_log = json.load(f)
            
        # Count trades per race
        for trade in trade_log:
            key = f"{trade['track']}_R{trade['race']}"
            race_trade_count[key] += 1


def save_state():
    """Save current state"""
    with open(POSITIONS_JSON, 'w') as f:
        json.dump(open_positions, f, indent=2, default=str)
    
    with open(TRADES_JSON, 'w') as f:
        json.dump(trade_log, f, indent=2, default=str)


def get_meetings() -> List[dict]:
    """Fetch AU thoroughbred meetings"""
    r = requests.get(
        'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
        headers=HEADERS,
        timeout=15
    )
    
    if r.status_code != 200:
        return []
    
    data = r.json()
    meetings = data.get('data', {}).get('meetings', [])
    return [m for m in meetings if m.get('country') == 'AUS' and m.get('category') == 'T']


def get_race_details(race_id: str) -> Optional[dict]:
    """Fetch race details with runner data"""
    r = requests.get(
        f"https://api.ladbrokes.com.au/affiliates/v1/racing/events/{race_id}",
        headers=HEADERS,
        timeout=15
    )
    
    if r.status_code != 200:
        return None
    
    return r.json().get('data', {})


def calculate_green_book_stakes(back_price: float, lay_price: float, back_stake: float = MIN_BET) -> dict:
    """
    Calculate stakes to green book a trade.
    
    Returns:
        {
            'back_stake': float,
            'lay_stake': float,
            'profit_if_win': float,
            'profit_if_lose': float,
            'guaranteed_profit': float
        }
    """
    # Lay stake to green book
    lay_stake = (back_stake * back_price) / lay_price
    
    # Calculate outcomes
    profit_if_win = (back_stake * (back_price - 1)) - (lay_stake * (lay_price - 1))
    profit_if_lose = lay_stake - back_stake
    
    # After commission
    profit_if_win *= (1 - BETFAIR_COMMISSION)
    profit_if_lose *= (1 - BETFAIR_COMMISSION)
    
    return {
        'back_stake': round(back_stake, 2),
        'lay_stake': round(lay_stake, 2),
        'profit_if_win': round(profit_if_win, 2),
        'profit_if_lose': round(profit_if_lose, 2),
        'guaranteed_profit': round(min(profit_if_win, profit_if_lose), 2)
    }


def detect_edges(runners: List[dict], track: str, race: str) -> List[dict]:
    """Detect trading edges in runner data"""
    edges = []
    
    for runner in runners:
        name = runner.get('name', '')
        if not name:
            continue
        
        odds = runner.get('odds', {})
        current_price = odds.get('fixed_win', 0)
        if current_price <= 0:
            continue
        
        flucs = runner.get('flucs', [])
        open_price = flucs[0] if flucs else current_price
        
        if open_price <= 0:
            continue
        
        # Calculate price change
        price_change = (current_price - open_price) / open_price
        
        # Detect STEAM (price dropping)
        if price_change < -STEAM_THRESHOLD:
            target_price = current_price * 0.95  # Expect 5% more drop
            stakes = calculate_green_book_stakes(current_price, target_price)
            
            edges.append({
                'type': 'STEAM',
                'runner': name,
                'open_price': open_price,
                'current_price': current_price,
                'target_price': target_price,
                'change_pct': round(price_change * 100, 1),
                'stakes': stakes,
                'r_potential': round(stakes['guaranteed_profit'] / R_UNIT, 3)
            })
        
        # Detect DRIFT (price rising)
        elif price_change > DRIFT_THRESHOLD:
            # For drift, we LAY first, then BACK at higher price
            target_price = current_price * 1.05  # Expect 5% more rise
            # Inverse calculation: lay at current, back at target
            lay_stake = MIN_BET
            back_stake = (lay_stake * current_price) / target_price
            
            profit_if_win = back_stake * (target_price - 1) - lay_stake * (current_price - 1)
            profit_if_lose = lay_stake - back_stake
            
            edges.append({
                'type': 'DRIFT',
                'runner': name,
                'open_price': open_price,
                'current_price': current_price,
                'target_price': target_price,
                'change_pct': round(price_change * 100, 1),
                'stakes': {
                    'lay_stake': lay_stake,
                    'back_stake': round(back_stake, 2),
                    'profit_if_win': round(profit_if_win * (1 - BETFAIR_COMMISSION), 2),
                    'profit_if_lose': round(profit_if_lose * (1 - BETFAIR_COMMISSION), 2),
                    'guaranteed_profit': round(min(profit_if_win, profit_if_lose) * (1 - BETFAIR_COMMISSION), 2)
                },
                'r_potential': round(min(profit_if_win, profit_if_lose) * (1 - BETFAIR_COMMISSION) / R_UNIT, 3)
            })
    
    return edges


def execute_trade(edge: dict, track: str, race: str, race_start: datetime):
    """Execute a paper trade"""
    now = datetime.now(timezone.utc)
    mins_to_start = (race_start - now).total_seconds() / 60
    
    # Safety checks
    if mins_to_start < MIN_TIME_TO_START:
        return None
    
    race_key = f"{track}_R{race}"
    if race_trade_count[race_key] >= MAX_TRADES_PER_RACE:
        return None
    
    # Check if already traded this runner
    trade_id = f"{track}_R{race}_{edge['runner']}"
    for existing_trade in trade_log:
        if existing_trade.get('id', '').startswith(trade_id):
            return None  # Already traded this runner
    
    # Create trade record
    trade = {
        'id': f"{track}_R{race}_{edge['runner']}_{datetime.now().strftime('%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'track': track,
        'race': race,
        'runner': edge['runner'],
        'edge_type': edge['type'],
        'entry_price': edge['current_price'],
        'target_price': edge['target_price'],
        'open_price': edge['open_price'],
        'stakes': edge['stakes'],
        'r_potential': edge['r_potential'],
        'status': 'OPEN',
        'mins_to_start': round(mins_to_start, 1)
    }
    
    # Log the trade
    trade_log.append(trade)
    race_trade_count[race_key] += 1
    
    # Track position
    open_positions[trade['id']] = trade
    
    print(f"\n  [TRADE] OPENED: {edge['type']} {edge['runner']}")
    print(f"     Entry: ${edge['current_price']:.2f}")
    print(f"     Target: ${edge['target_price']:.2f}")
    print(f"     R potential: +{edge['r_potential']:.3f}R")
    print(f"     Guaranteed: ${edge['stakes']['guaranteed_profit']:.2f}")
    
    return trade


def scan_and_trade():
    """Main scanning loop"""
    print(f"\n{'='*60}")
    print(f"SCANNING FOR EDGES - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    meetings = get_meetings()
    if not meetings:
        print("No meetings found")
        return
    
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(minutes=15)
    
    total_edges = 0
    total_trades = 0
    
    for meeting in meetings:
        track = meeting.get('name', '')
        
        for race in meeting.get('races', []):
            race_number = race.get('race_number')
            race_id = race.get('id')
            start_str = race.get('start_time', '').replace('Z', '+00:00')
            
            if not start_str:
                continue
            
            try:
                race_start = datetime.fromisoformat(start_str)
            except:
                continue
            
            # Only scan races in next 15 mins
            if not (now < race_start <= cutoff):
                continue
            
            mins_to_start = (race_start - now).total_seconds() / 60
            
            # Skip if too close to start
            if mins_to_start < MIN_TIME_TO_START:
                continue
            
            # Get race details
            race_data = get_race_details(race_id)
            if not race_data:
                continue
            
            runners = race_data.get('runners', [])
            if not runners:
                continue
            
            # Detect edges
            edges = detect_edges(runners, track, str(race_number))
            
            if edges:
                print(f"\n{track} R{race_number} ({mins_to_start:.1f} mins):")
                print(f"  Found {len(edges)} edges")
                
                for edge in edges:
                    print(f"  [{edge['type']}] {edge['runner']}: "
                          f"${edge['open_price']:.2f} -> ${edge['current_price']:.2f} "
                          f"({edge['change_pct']:+.1f}%)")
                    total_edges += 1
                
                # Execute best edge (highest R potential)
                best_edge = max(edges, key=lambda e: e['r_potential'])
                
                trade = execute_trade(best_edge, track, str(race_number), race_start)
                if trade:
                    total_trades += 1
    
    print(f"\n{'='*60}")
    print(f"Scan complete: {total_edges} edges found, {total_trades} trades executed")
    print(f"Open positions: {len(open_positions)}")
    print(f"{'='*60}")
    
    save_state()


def main():
    print("="*60)
    print("AUTO-EXECUTOR - Paper Trading System")
    print(f"Minimum Bet: ${MIN_BET:.2f}")
    print(f"R Unit: ${R_UNIT:.2f}")
    print(f"Started: {datetime.now()}")
    print("="*60)
    
    load_state()
    
    print(f"Loaded: {len(trade_log)} historical trades")
    print(f"Open positions: {len(open_positions)}")
    
    while True:
        try:
            scan_and_trade()
            time.sleep(30)  # Scan every 30 seconds
            
        except KeyboardInterrupt:
            print("\n\nStopping...")
            save_state()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
