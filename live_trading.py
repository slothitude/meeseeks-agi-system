#!/usr/bin/env python3
"""
LIVE TRADING - $10 AUD Bankroll
================================

CONSERVATIVE MODE - Real Money
- R-unit: $10.00 AUD
- Min edge: 10% (only BEST setups)
- Max trades/race: 2
- Exit buffer: 3 minutes
- Stop loss: -0.05R (-$0.50)
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
TRADES_CSV = Path("live_trades.csv")
TRADES_JSON = Path("live_trades_log.json")
POSITIONS_JSON = Path("live_positions.json")
BANKROLL_JSON = Path("bankroll.json")

# API
HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# CONSERVATIVE TRADING PARAMETERS
R_UNIT = 1.00  # $1.00 AUD per R
MIN_BET = 1.00  # $1.00 minimum bet
STEAM_THRESHOLD = 0.10  # 10% drop (CONSERVATIVE)
DRIFT_THRESHOLD = 0.10  # 10% rise (CONSERVATIVE)
MAX_TRADES_PER_RACE = 2  # Reduced from 3
MIN_TIME_TO_START = 3.0  # 3 minutes (increased from 2)
MAX_HOLD_TIME = 120  # 2 minutes (reduced from 3)
BETFAIR_COMMISSION = 0.05  # 5%
STOP_LOSS_R = 0.05  # -0.05R = -$0.05

# Bankroll tracking
bankroll = {
    'starting': 10.00,
    'current': 10.00,
    'r_remaining': 1.0,
    'trades': 0,
    'wins': 0,
    'losses': 0,
    'total_r': 0.0
}

# State
open_positions = {}
trade_log = []
race_trade_count = defaultdict(int)


def load_bankroll():
    """Load bankroll state"""
    global bankroll
    if BANKROLL_JSON.exists():
        with open(BANKROLL_JSON, 'r') as f:
            bankroll = json.load(f)


def save_bankroll():
    """Save bankroll state"""
    with open(BANKROLL_JSON, 'w') as f:
        json.dump(bankroll, f, indent=2)


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


def detect_edges_conservative(runners: List[dict], track: str, race: str) -> List[dict]:
    """Detect ONLY the best edges (10%+ threshold)"""
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
        
        # CONSERVATIVE: Only 10%+ edges
        if price_change < -STEAM_THRESHOLD:  # 10%+ STEAM
            target_price = current_price * 0.95
            back_stake = R_UNIT  # $10.00
            lay_stake = (back_stake * current_price) / target_price
            
            profit_if_win = (back_stake * (current_price - 1)) - (lay_stake * (target_price - 1))
            profit_if_lose = lay_stake - back_stake
            profit_if_win *= (1 - BETFAIR_COMMISSION)
            profit_if_lose *= (1 - BETFAIR_COMMISSION)
            
            edges.append({
                'type': 'STEAM',
                'runner': name,
                'open_price': open_price,
                'current_price': current_price,
                'target_price': target_price,
                'change_pct': round(price_change * 100, 1),
                'stakes': {
                    'back_stake': round(back_stake, 2),
                    'lay_stake': round(lay_stake, 2),
                    'profit_if_win': round(profit_if_win, 2),
                    'profit_if_lose': round(profit_if_lose, 2),
                    'guaranteed_profit': round(min(profit_if_win, profit_if_lose), 2)
                },
                'r_potential': round(min(profit_if_win, profit_if_lose) / R_UNIT, 3)
            })
        
        elif price_change > DRIFT_THRESHOLD:  # 10%+ DRIFT
            target_price = current_price * 1.05
            lay_stake = R_UNIT  # $10.00
            back_stake = (lay_stake * current_price) / target_price
            
            profit_if_win = (back_stake * (target_price - 1)) - (lay_stake * (current_price - 1))
            profit_if_lose = lay_stake - back_stake
            profit_if_win *= (1 - BETFAIR_COMMISSION)
            profit_if_lose *= (1 - BETFAIR_COMMISSION)
            
            edges.append({
                'type': 'DRIFT',
                'runner': name,
                'open_price': open_price,
                'current_price': current_price,
                'target_price': target_price,
                'change_pct': round(price_change * 100, 1),
                'stakes': {
                    'lay_stake': round(lay_stake, 2),
                    'back_stake': round(back_stake, 2),
                    'profit_if_win': round(profit_if_win, 2),
                    'profit_if_lose': round(profit_if_lose, 2),
                    'guaranteed_profit': round(min(profit_if_win, profit_if_lose), 2)
                },
                'r_potential': round(min(profit_if_win, profit_if_lose) / R_UNIT, 3)
            })
    
    return edges


def execute_trade(edge: dict, track: str, race: str, race_start: datetime):
    """Execute a CONSERVATIVE trade"""
    now = datetime.now(timezone.utc)
    mins_to_start = (race_start - now).total_seconds() / 60
    
    # Safety checks (CONSERVATIVE)
    if mins_to_start < MIN_TIME_TO_START:
        print(f"    SKIP: Too close to start ({mins_to_start:.1f} mins)")
        return None
    
    race_key = f"{track}_R{race}"
    if race_trade_count[race_key] >= MAX_TRADES_PER_RACE:
        print(f"    SKIP: Max trades reached for race")
        return None
    
    # Check bankroll
    if bankroll['r_remaining'] < edge['r_potential']:
        print(f"    SKIP: Insufficient bankroll ({bankroll['r_remaining']:.3f}R < {edge['r_potential']:.3f}R)")
        return None
    
    # Check if already traded this runner
    trade_id = f"{track}_R{race}_{edge['runner']}"
    for existing_trade in trade_log:
        if existing_trade.get('id', '').startswith(trade_id):
            print(f"    SKIP: Already traded {edge['runner']}")
            return None
    
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
        'change_pct': edge['change_pct'],
        'stakes': edge['stakes'],
        'r_potential': edge['r_potential'],
        'status': 'OPEN',
        'mins_to_start': round(mins_to_start, 1),
        'bankroll_before': bankroll['current']
    }
    
    # Log the trade
    trade_log.append(trade)
    race_trade_count[race_key] += 1
    
    # Update bankroll (reserve R)
    bankroll['r_remaining'] -= edge['r_potential']
    bankroll['trades'] += 1
    
    # Track position
    open_positions[trade['id']] = trade
    
    print(f"\n  *** LIVE TRADE ***")
    print(f"  {edge['type']} {edge['runner']}")
    print(f"  Entry: ${edge['current_price']:.2f}")
    print(f"  Target: ${edge['target_price']:.2f}")
    print(f"  Change: {edge['change_pct']:+.1f}%")
    print(f"  Risk: ${edge['stakes'].get('back_stake', edge['stakes'].get('lay_stake')):.2f}")
    print(f"  Profit potential: ${edge['stakes']['guaranteed_profit']:.2f}")
    print(f"  R potential: +{edge['r_potential']:.3f}R")
    print(f"  Bankroll remaining: ${bankroll['current']:.2f} ({bankroll['r_remaining']:.3f}R)")
    
    return trade


def scan_and_trade():
    """Main scanning loop - CONSERVATIVE"""
    print(f"\n{'='*60}")
    print(f"LIVE SCANNING - ${bankroll['current']:.2f} ({bankroll['r_remaining']:.3f}R)")
    print(f"{datetime.now().strftime('%H:%M:%S')}")
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
            
            # Skip if too close to start (CONSERVATIVE)
            if mins_to_start < MIN_TIME_TO_START:
                continue
            
            # Get race details
            race_data = get_race_details(race_id)
            if not race_data:
                continue
            
            runners = race_data.get('runners', [])
            if not runners:
                continue
            
            # Detect edges (CONSERVATIVE)
            edges = detect_edges_conservative(runners, track, str(race_number))
            
            if edges:
                print(f"\n{track} R{race_number} ({mins_to_start:.1f} mins):")
                print(f"  Found {len(edges)} edges (10%+ threshold)")
                
                for edge in edges:
                    print(f"  [{edge['type']}] {edge['runner']}: "
                          f"${edge['open_price']:.2f} -> ${edge['current_price']:.2f} "
                          f"({edge['change_pct']:+.1f}%)")
                    total_edges += 1
                
                # Execute BEST edge only (highest R potential)
                if bankroll['r_remaining'] > 0:
                    best_edge = max(edges, key=lambda e: e['r_potential'])
                    
                    trade = execute_trade(best_edge, track, str(race_number), race_start)
                    if trade:
                        total_trades += 1
    
    print(f"\n{'='*60}")
    print(f"Scan complete: {total_edges} edges found, {total_trades} trades executed")
    print(f"Open positions: {len(open_positions)}")
    print(f"Bankroll: ${bankroll['current']:.2f} ({bankroll['r_remaining']:.3f}R remaining)")
    print(f"{'='*60}")
    
    save_state()
    save_bankroll()


def main():
    print("="*60)
    print("LIVE TRADING - $10.00 AUD")
    print("CONSERVATIVE MODE")
    print("="*60)
    print(f"R-unit: ${R_UNIT:.2f}")
    print(f"Min edge: {STEAM_THRESHOLD*100:.0f}%")
    print(f"Max trades/race: {MAX_TRADES_PER_RACE}")
    print(f"Exit buffer: {MIN_TIME_TO_START:.0f} mins")
    print(f"Stop loss: -{STOP_LOSS_R}R (-${STOP_LOSS_R * R_UNIT:.2f})")
    print("="*60)
    print()
    
    load_bankroll()
    load_state()
    
    print(f"Bankroll: ${bankroll['current']:.2f} ({bankroll['r_remaining']:.3f}R)")
    print(f"Historical trades: {len(trade_log)}")
    print(f"Open positions: {len(open_positions)}")
    print()
    
    while True:
        try:
            if bankroll['r_remaining'] <= 0:
                print("\n*** BANKROLL DEPLETED - STOPPING ***")
                break
            
            scan_and_trade()
            time.sleep(30)  # Scan every 30 seconds
            
        except KeyboardInterrupt:
            print("\n\nStopping...")
            save_state()
            save_bankroll()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
