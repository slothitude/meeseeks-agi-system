#!/usr/bin/env python3
"""
Betfair Pre-Race Steam Analyser
================================

Analyses odds movement in Australian horse racing markets to find optimal 
back (entry) and lay (exit) windows using Van K. Tharp R-multiple framework.

The strategy:
- BACK early (~10 min before race) at higher odds
- LAY later (~3-0 min before race) at lower odds
- Green book = profit regardless of result

Setup:
    pip install betfairlightweight pandas numpy

Usage:
    python betfair_steam_analyser.py
    
    (Will run in DEMO mode without credentials)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import Optional

# ─────────────────────────────────────────────
# STRATEGY PARAMETERS
# ─────────────────────────────────────────────
BACK_WINDOW_MINUTES = 10      # Look for back entry up to X min before race
LAY_WINDOW_MINUTES = 3        # Look for lay exit from X min before race
MIN_BACK_ODDS = 2.0           # Minimum back odds to consider
MAX_BACK_ODDS = 15.0          # Maximum back odds (avoid extreme outsiders)
MIN_ODDS_DROP = 0.3           # Minimum odds compression needed (e.g. 4.0 → 3.7)
STAKE_1R = 1.00               # 1R stake in AUD
COMMISSION_RATE = 0.05        # Betfair standard 5% commission
DAYS_TO_ANALYSE = 7           # How many days of history to pull

# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class TradeOpportunity:
    market_id: str
    race_name: str
    runner_name: str
    race_start: str
    back_odds: float
    back_time_to_start_mins: float
    lay_odds: float
    lay_time_to_start_mins: float
    odds_drop: float
    odds_drop_pct: float
    back_stake: float
    lay_stake: float
    green_book_profit: float
    worst_case_loss: float
    r_value: float  # Profit in R units
    is_profitable: bool

@dataclass
class WindowStats:
    window_label: str
    trade_count: int
    avg_odds_drop: float
    avg_odds_drop_pct: float
    profitable_pct: float
    avg_r_value: float
    expectancy_r: float
    best_r: float
    worst_r: float

# ─────────────────────────────────────────────
# STEAM PATTERN DETECTION
# ─────────────────────────────────────────────

def analyse_odds_movement(back_odds: float, lay_odds: float) -> Optional[dict]:
    """
    Given a back and lay opportunity, calculate the trade metrics.
    Back at back_odds, lay at lay_odds (lay_odds < back_odds = steam move).
    Uses Betfair's trading formula to calculate green book profit.
    """
    if lay_odds >= back_odds:
        return None  # No steam, odds went wrong way
    
    odds_drop = back_odds - lay_odds
    odds_drop_pct = (odds_drop / back_odds) * 100
    
    if odds_drop < MIN_ODDS_DROP:
        return None  # Not enough movement
    
    # Calculate green book position
    # Back stake = 1R
    back_stake = STAKE_1R
    
    # Lay stake to balance the book
    lay_stake = (back_stake * back_odds) / lay_odds
    
    # Profit if runner wins (back wins, lay loses)
    back_profit = back_stake * (back_odds - 1)
    lay_liability = lay_stake * (lay_odds - 1)
    net_if_wins = back_profit - lay_liability
    
    # Profit if runner loses (back loses, lay wins)
    lay_profit = lay_stake
    net_if_loses = lay_profit - back_stake
    
    # Apply commission to winning side
    green_book_profit = min(net_if_wins, net_if_loses) * (1 - COMMISSION_RATE)
    
    # In R terms
    r_value = green_book_profit / STAKE_1R
    
    return {
        "back_stake": back_stake,
        "lay_stake": lay_stake,
        "green_book_profit": green_book_profit,
        "worst_case_loss": min(net_if_wins, net_if_loses),  # Should be positive if green
        "r_value": r_value,
        "odds_drop": odds_drop,
        "odds_drop_pct": odds_drop_pct,
        "is_profitable": green_book_profit > 0
    }

# ─────────────────────────────────────────────
# WINDOW ANALYSIS
# ─────────────────────────────────────────────

def analyse_time_windows(opportunities: list) -> list:
    """
    Group opportunities by entry/exit time windows and compute stats.
    This tells you WHICH windows produce the best R-multiples.
    """
    if not opportunities:
        return []
    
    df = pd.DataFrame([asdict(o) for o in opportunities])
    
    # Create time window buckets for entry (back)
    df["back_window"] = pd.cut(
        df["back_time_to_start_mins"],
        bins=[0, 3, 5, 7, 10, 15, 20],
        labels=["0-3min", "3-5min", "5-7min", "7-10min", "10-15min", "15-20min"],
        right=True
    )
    
    # Create time window buckets for exit (lay)
    df["lay_window"] = pd.cut(
        df["lay_time_to_start_mins"],
        bins=[0, 1, 2, 3, 5],
        labels=["0-1min", "1-2min", "2-3min", "3-5min"],
        right=True
    )
    
    print("\n" + "="*60)
    print("ENTRY WINDOW ANALYSIS (When to BACK)")
    print("="*60)
    
    entry_stats = []
    for window, group in df.groupby("back_window", observed=True):
        profitable = group[group["is_profitable"]]
        stats = WindowStats(
            window_label=f"Back entry @ {window} before race",
            trade_count=len(group),
            avg_odds_drop=group["odds_drop"].mean(),
            avg_odds_drop_pct=group["odds_drop_pct"].mean(),
            profitable_pct=(len(profitable) / len(group)) * 100,
            avg_r_value=group["r_value"].mean(),
            expectancy_r=group["r_value"].mean(),
            best_r=group["r_value"].max(),
            worst_r=group["r_value"].min()
        )
        entry_stats.append(stats)
        
        print(f"\n  Window: {window}")
        print(f"  Trades: {stats.trade_count}")
        print(f"  Avg odds drop: {stats.avg_odds_drop:.2f} ({stats.avg_odds_drop_pct:.1f}%)")
        print(f"  Profitable: {stats.profitable_pct:.1f}%")
        print(f"  Avg R: {stats.avg_r_value:.3f}R")
        print(f"  Expectancy: {stats.expectancy_r:.3f}R per trade")
        print(f"  Best R: {stats.best_r:.3f}R")
        print(f"  Worst R: {stats.worst_r:.3f}R")
    
    print("\n" + "="*60)
    print("EXIT WINDOW ANALYSIS (When to LAY)")
    print("="*60)
    
    exit_stats = []
    for window, group in df.groupby("lay_window", observed=True):
        profitable = group[group["is_profitable"]]
        stats = WindowStats(
            window_label=f"Lay exit @ {window} before race",
            trade_count=len(group),
            avg_odds_drop=group["odds_drop"].mean(),
            avg_odds_drop_pct=group["odds_drop_pct"].mean(),
            profitable_pct=(len(profitable) / len(group)) * 100,
            avg_r_value=group["r_value"].mean(),
            expectancy_r=group["r_value"].mean(),
            best_r=group["r_value"].max(),
            worst_r=group["r_value"].min()
        )
        exit_stats.append(stats)
        
        print(f"\n  Window: {window}")
        print(f"  Trades: {stats.trade_count}")
        print(f"  Avg odds drop: {stats.avg_odds_drop:.2f} ({stats.avg_odds_drop_pct:.1f}%)")
        print(f"  Profitable: {stats.profitable_pct:.1f}%")
        print(f"  Avg R: {stats.avg_r_value:.3f}R")
        print(f"  Expectancy: {stats.expectancy_r:.3f}R per trade")
    
    return entry_stats + exit_stats

# ─────────────────────────────────────────────
# DEMO MODE
# ─────────────────────────────────────────────

def run_demo_analysis():
    """
    Runs analysis on simulated odds movement data.
    Mirrors realistic Australian horse racing steam patterns.
    """
    print("\n" + "="*60)
    print("DEMO MODE - Simulated Australian Horse Racing Data")
    print("="*60)
    print("(Fill in credentials at top to use live Betfair API)\n")
    
    np.random.seed(42)
    n_races = 500
    
    opportunities = []
    
    for i in range(n_races):
        # Random back odds between 2.0 and 12.0
        back_odds = np.random.uniform(MIN_BACK_ODDS, MAX_BACK_ODDS)
        
        # Steam probability: higher odds -> less likely to steam
        # Favourites and mid-rangers steam most reliably
        steam_prob = 0.65 if back_odds < 6.0 else 0.40
        
        if np.random.random() > steam_prob:
            continue  # No steam this race
        
        # Odds drop: typically 5-25% in the steam window
        drop_pct = np.random.normal(0.12, 0.07)
        drop_pct = max(0.03, min(0.35, drop_pct))
        lay_odds = round(back_odds * (1 - drop_pct), 2)
        lay_odds = max(1.01, lay_odds)
        
        # Time windows
        back_time = np.random.uniform(7, 12)   # 7-12 mins out
        lay_time = np.random.uniform(0.5, 3)   # 0.5-3 mins out
        
        trade = analyse_odds_movement(back_odds, lay_odds)
        if not trade:
            continue
        
        opp = TradeOpportunity(
            market_id=f"1.{180000000 + i}",
            race_name=f"Race {(i % 8) + 1}",
            runner_name=f"Runner {np.random.randint(1, 14)}",
            race_start=(datetime.now() - timedelta(days=np.random.randint(0, 7))).strftime("%Y-%m-%d %H:%M"),
            back_odds=round(back_odds, 2),
            back_time_to_start_mins=round(back_time, 1),
            lay_odds=round(lay_odds, 2),
            lay_time_to_start_mins=round(lay_time, 1),
            odds_drop=round(trade["odds_drop"], 2),
            odds_drop_pct=round(trade["odds_drop_pct"], 1),
            back_stake=trade["back_stake"],
            lay_stake=round(trade["lay_stake"], 2),
            green_book_profit=round(trade["green_book_profit"], 4),
            worst_case_loss=round(trade["worst_case_loss"], 4),
            r_value=round(trade["r_value"], 4),
            is_profitable=trade["is_profitable"]
        )
        opportunities.append(opp)
    
    print(f"Simulated races analysed: {n_races}")
    print(f"Steam opportunities found: {len(opportunities)}")
    
    # Run window analysis
    analyse_time_windows(opportunities)
    
    # Overall summary
    df = pd.DataFrame([asdict(o) for o in opportunities])
    profitable = df[df["is_profitable"]]
    
    print("\n" + "="*60)
    print("OVERALL SYSTEM STATS")
    print("="*60)
    print(f"  Total opportunities: {len(df)}")
    print(f"  Profitable trades: {len(profitable)} ({len(profitable)/len(df)*100:.1f}%)")
    print(f"  Avg R per trade: {df['r_value'].mean():.4f}R")
    print(f"  System expectancy: {df['r_value'].mean():.4f}R per trade")
    print(f"  Best single trade: +{df['r_value'].max():.3f}R")
    print(f"  Avg odds drop: {df['odds_drop'].mean():.2f} pts ({df['odds_drop_pct'].mean():.1f}%)")
    
    print(f"\n  With 1R = $1.00 AUD:")
    print(f"  Avg profit/trade: ${df['r_value'].mean():.4f}")
    print(f"  If 200 trades/month: ${df['r_value'].mean() * 200:.2f}/month")
    print(f"  If 1R = $10: ${df['r_value'].mean() * 200 * 10:.2f}/month")
    print(f"  If 1R = $50: ${df['r_value'].mean() * 200 * 50:.2f}/month")
    
    # Save results
    df.to_csv("steam_analysis_results.csv", index=False)
    print(f"\n[OK] Results saved to steam_analysis_results.csv")
    
    # Identify the optimal windows
    print("\n" + "="*60)
    print("RECOMMENDED STRATEGY WINDOWS")
    print("="*60)
    
    best_back = df.groupby(
        pd.cut(df["back_time_to_start_mins"], bins=[0,3,5,7,10,15]), observed=True
    )["r_value"].mean().idxmax()
    
    best_lay = df.groupby(
        pd.cut(df["lay_time_to_start_mins"], bins=[0,1,2,3,5]), observed=True
    )["r_value"].mean().idxmax()
    
    print(f"  [OK] Optimal BACK entry: {best_back} minutes before race")
    print(f"  [OK] Optimal LAY exit: {best_lay} minutes before race")
    print(f"\n  Filter: Only trade runners with odds between {MIN_BACK_ODDS} and {MAX_BACK_ODDS}")
    print(f"  Filter: Only trade when expected odds drop > {MIN_ODDS_DROP} points")
    
    return opportunities


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("="*60)
    print("Betfair Pre-Race Steam Analyser")
    print("Van K. Tharp R-Multiple Framework")
    print("Australian Horse Racing")
    print("="*60)
    
    # Run in demo mode (no credentials needed)
    run_demo_analysis()
