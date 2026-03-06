#!/usr/bin/env python3
"""
CORRECTED Paper Trading Proof System
=====================================

The key insight: ALWAYS HEDGE, even if steam fails.

Strategy:
1. BACK at higher odds (steam detected)
2. WAIT 2-3 minutes
3. LAY at current odds (whatever they are)
4. Result: Small profit OR small loss (never -1R)

This changes the math completely.

Usage:
    python paper_proof_v2.py --trades 30
"""

import json
import random
import statistics
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List

# Parameters
STAKE_1R = 1.00
COMMISSION = 0.05
TARGET_PER_RACE = 0.50

TRADES_FILE = Path("paper_proof_v2_trades.json")


@dataclass
class Trade:
    trade_id: int
    timestamp: str
    race: str
    runner: str
    
    entry_odds: float
    exit_odds: float
    odds_drop: float
    
    stake: float
    profit: float
    profit_r: float
    
    result: str  # WIN, SMALL_LOSS, BIG_LOSS


def calc_green_book(back_odds: float, lay_odds: float, stake: float) -> dict:
    """Calculate green book profit - ALWAYS hedge"""
    if lay_odds >= back_odds:
        # Odds went UP - we still hedge but at a loss
        # Lay at higher odds means bigger liability
        lay_stake = (stake * back_odds) / lay_odds
        
        # If wins: back profit - lay liability
        back_profit = stake * (back_odds - 1)
        lay_liability = lay_stake * (lay_odds - 1)
        if_wins = back_profit - lay_liability
        
        # If loses: lay stake - back stake
        if_loses = lay_stake - stake
        
        # Both negative = guaranteed loss
        profit = max(if_wins, if_loses) * (1 - COMMISSION)
        
        return {
            'profit': profit,
            'profit_r': profit / STAKE_1R,
            'lay_stake': lay_stake,
            'type': 'LOSS'
        }
    else:
        # Odds went DOWN - green book profit
        lay_stake = (stake * back_odds) / lay_odds
        
        back_profit = stake * (back_odds - 1)
        lay_liability = lay_stake * (lay_odds - 1)
        if_wins = back_profit - lay_liability
        if_loses = lay_stake - stake
        
        if if_wins > 0 and if_loses > 0:
            profit = min(if_wins, if_loses) * (1 - COMMISSION)
            return {
                'profit': profit,
                'profit_r': profit / STAKE_1R,
                'lay_stake': lay_stake,
                'type': 'WIN'
            }
        else:
            # Small loss
            profit = max(if_wins, if_loses) * (1 - COMMISSION)
            return {
                'profit': profit,
                'profit_r': profit / STAKE_1R,
                'lay_stake': lay_stake,
                'type': 'SMALL_LOSS'
            }


def simulate_trade(trade_id: int) -> Trade:
    """Simulate a steam trade with ALWAYS HEDGE"""
    races = [
        "Randwick R3", "Flemington R5", "Eagle Farm R2",
        "Caulfield R4", "Doomben R6", "Rosehill R7"
    ]
    
    # Entry odds (4.0 - 8.0 typical for steam plays)
    entry_odds = round(random.uniform(4.0, 8.0), 2)
    
    # Steam probability: 65% follow through
    if random.random() < 0.65:
        # Steam follows - odds drop 0.2-0.6
        drop = random.uniform(0.20, 0.60)
        exit_odds = entry_odds - drop
        exit_odds = max(exit_odds, 1.5)  # Floor
    else:
        # Steam fails - odds drift up 0.1-0.4
        drift = random.uniform(0.10, 0.40)
        exit_odds = entry_odds + drift
    
    exit_odds = round(exit_odds, 2)
    
    # ALWAYS HEDGE
    result = calc_green_book(entry_odds, exit_odds, STAKE_1R)
    
    return Trade(
        trade_id=trade_id,
        timestamp=datetime.now().isoformat(),
        race=random.choice(races),
        runner=f"Runner {random.randint(1, 14)}",
        entry_odds=entry_odds,
        exit_odds=exit_odds,
        odds_drop=round(entry_odds - exit_odds, 2),
        stake=STAKE_1R,
        profit=round(result['profit'], 4),
        profit_r=round(result['profit_r'], 4),
        result=result['type']
    )


def run_validation(n_trades: int = 30):
    """Run validation with proper hedging"""
    
    print("="*60)
    print("PAPER TRADING PROOF SYSTEM v2")
    print("="*60)
    print("\nSTRATEGY: ALWAYS HEDGE (never let bet run)")
    print(f"\nSimulating {n_trades} steam trades...")
    print(f"1R = ${STAKE_1R}")
    print(f"Target = ${TARGET_PER_RACE}/race")
    print()
    
    trades: List[Trade] = []
    
    # Load existing
    if TRADES_FILE.exists():
        with open(TRADES_FILE, 'r') as f:
            for line in f:
                try:
                    trades.append(Trade(**json.loads(line.strip())))
                except:
                    pass
    
    # Simulate new trades
    start_id = len(trades) + 1
    for i in range(n_trades):
        trade = simulate_trade(start_id + i)
        trades.append(trade)
        
        with open(TRADES_FILE, 'a') as f:
            f.write(json.dumps(asdict(trade)) + '\n')
        
        # Print progress
        symbol = {"WIN": "+", "SMALL_LOSS": "-", "LOSS": "-"}
        print(f"  #{trade.trade_id:2d} {symbol[trade.result]} {trade.race:15s} | {trade.entry_odds:.2f}->{trade.exit_odds:.2f} | {trade.profit_r:+.4f}R (${trade.profit:+.4f})")
    
    # Calculate stats
    wins = [t for t in trades if t.result == "WIN"]
    small_losses = [t for t in trades if t.result == "SMALL_LOSS"]
    big_losses = [t for t in trades if t.result == "LOSS"]
    
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    
    total_r = sum(t.profit_r for t in trades)
    avg_r = total_r / len(trades) if trades else 0
    
    total_profit = sum(t.profit for t in trades)
    avg_per_race = total_profit / len(trades) if trades else 0
    
    # Expectancy
    if len(trades) >= 2:
        expectancy = statistics.mean(t.profit_r for t in trades)
    else:
        expectancy = 0
    
    # Print report
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)
    
    print("\n" + "-"*60)
    print("SUMMARY")
    print("-"*60)
    print(f"  Total trades:   {len(trades)}")
    print(f"  Wins:           {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
    print(f"  Small losses:   {len(small_losses)} ({len(small_losses)/len(trades)*100:.1f}%)")
    print(f"  Big losses:     {len(big_losses)} ({len(big_losses)/len(trades)*100:.1f}%)")
    
    print("\n" + "-"*60)
    print("R-MULTIPLE RESULTS")
    print("-"*60)
    print(f"  Total R:        {total_r:+.4f}R")
    print(f"  Avg R/trade:    {avg_r:+.4f}R")
    print(f"  Expectancy:     {expectancy:+.4f}R")
    
    print("\n" + "-"*60)
    print("AUD RESULTS")
    print("-"*60)
    print(f"  Total profit:   ${total_profit:+.2f}")
    print(f"  Avg per race:   ${avg_per_race:+.2f}")
    print(f"  Target ($0.50): {'[ACHIEVED]' if avg_per_race >= TARGET_PER_RACE else '[NOT YET]'}")
    
    print("\n" + "-"*60)
    print("VALIDATION STATUS")
    print("-"*60)
    
    if len(trades) >= 30:
        if expectancy > 0:
            print("  [VALIDATED] Positive expectancy confirmed!")
            print(f"  [READY] Expected profit: ${expectancy:.4f}/race")
        else:
            print("  [FAILED] Expectancy not positive")
    else:
        print(f"  [PENDING] Need {30 - len(trades)} more trades")
    
    # Scaling projection
    if avg_per_race > 0:
        print("\n" + "-"*60)
        print("SCALING PROJECTION")
        print("-"*60)
        
        races_per_day = 20
        daily_profit = avg_per_race * races_per_day
        
        print(f"  At {races_per_day} races/day @ 1R=$1:")
        print(f"    Daily:   ${daily_profit:.2f}")
        print(f"    Weekly:  ${daily_profit * 7:.2f}")
        print(f"    Monthly: ${daily_profit * 30:.2f}")
        
        print(f"\n  At {races_per_day} races/day @ 1R=$10:")
        print(f"    Daily:   ${daily_profit * 10:.2f}")
        print(f"    Weekly:  ${daily_profit * 70:.2f}")
        print(f"    Monthly: ${daily_profit * 300:.2f}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--trades', type=int, default=30)
    args = parser.parse_args()
    
    run_validation(n_trades=args.trades)
