#!/usr/bin/env python3
"""
SteamArb Backtester
===================

Tests the 3 engines (ARB, STEAM, VALUE) against simulated data.

Usage:
    python steam_arb_backtester.py --demo --races 500
"""

import random
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import argparse

# Parameters
STAKE_1R = 1.00
COMMISSION = 0.05
MIN_ARB_PROFIT_PCT = 0.5
MIN_STEAM_DROP_PCT = 5.0
MIN_VALUE_EDGE_PCT = 10.0

OUTPUT_FILE = Path("steamarb_backtest_results.json")


@dataclass
class Trade:
    engine: str
    runner_name: str
    back_price: float
    lay_price: float
    profit_r: float
    won: bool


def generate_race(race_num: int) -> List[Dict]:
    """Generate simulated runners for a race."""
    runners = []
    num_runners = random.randint(6, 14)

    for i in range(num_runners):
        # Generate realistic odds (favorites to longshots)
        if i == 0:
            base_odds = random.uniform(2.0, 4.0)
        elif i < 3:
            base_odds = random.uniform(3.0, 8.0)
        else:
            base_odds = random.uniform(8.0, 30.0)

        # Ladbrokes price (slightly different from true)
        lad_price = base_odds * random.uniform(0.95, 1.15)

        # Betfair back/lay (spread around true)
        bf_back = base_odds * random.uniform(0.98, 1.02)
        bf_lay = base_odds * random.uniform(1.02, 1.08)

        # Steam flucs (sometimes)
        flucs = []
        if random.random() < 0.3:  # 30% chance of steam
            old_price = lad_price * random.uniform(1.05, 1.20)
            for _ in range(random.randint(2, 6)):
                flucs.append({"fluc": old_price})
                old_price = old_price * random.uniform(0.97, 0.99)
            flucs.append({"fluc": lad_price})

        runners.append({
            "name": f"Horse_{i+1}",
            "lad_price": lad_price,
            "bf_back": bf_back,
            "bf_lay": bf_lay,
            "flucs": flucs,
            "true_prob": 1 / base_odds
        })

    return runners


def detect_arb(lad_price: float, bf_lay: float) -> Optional[float]:
    """Check for ARB opportunity."""
    if lad_price <= bf_lay:
        return None

    back_stake = STAKE_1R
    lay_stake = back_stake * lad_price / bf_lay

    net_wins = back_stake * (lad_price - 1) - lay_stake * (bf_lay - 1)
    net_loses = lay_stake - back_stake

    if net_wins <= 0 or net_loses <= 0:
        return None

    profit = min(net_wins, net_loses) * (1 - COMMISSION)
    profit_pct = (profit / back_stake) * 100

    if profit_pct < MIN_ARB_PROFIT_PCT:
        return None

    return profit / STAKE_1R


def detect_steam(flucs: List, bf_back: float, lad_price: float) -> Optional[float]:
    """Check for STEAM opportunity."""
    if not flucs or len(flucs) < 2:
        return None

    prices = [f["fluc"] for f in flucs]
    old_price = prices[0]
    new_price = prices[-1]

    if old_price <= new_price:
        return None

    drop_pct = ((old_price - new_price) / old_price) * 100

    if drop_pct < MIN_STEAM_DROP_PCT:
        return None

    if bf_back <= lad_price:
        return None

    gap_pct = ((bf_back - lad_price) / bf_back) * 100

    expected_lay = lad_price * 1.03

    if expected_lay >= bf_back:
        return None

    back_stake = STAKE_1R
    lay_stake = (back_stake * bf_back) / expected_lay

    net_wins = back_stake * (bf_back - 1) - lay_stake * (expected_lay - 1)
    net_loses = lay_stake - back_stake

    profit = min(net_wins, net_loses) * (1 - COMMISSION)

    if profit <= 0:
        return None

    # Simulate win/loss (60% win rate for steam)
    won = random.random() < 0.6

    if won:
        return profit / STAKE_1R
    else:
        # Lose 1-2 ticks on average
        return -0.03


def detect_value(bf_back: float, lad_price: float, true_prob: float) -> Optional[float]:
    """Check for VALUE opportunity."""
    if lad_price < 2.0 or lad_price > 15.0:
        return None

    bf_prob = 1 / bf_back
    lad_prob = 1 / lad_price

    if bf_prob <= lad_prob:
        return None

    edge_pct = ((bf_prob - lad_prob) / lad_prob) * 100

    if edge_pct < MIN_VALUE_EDGE_PCT:
        return None

    ev_r = (true_prob * (lad_price - 1)) - ((1 - true_prob) * 1)

    if ev_r <= 0:
        return None

    # Simulate win/loss based on true probability
    won = random.random() < true_prob

    if won:
        return (lad_price - 1) * STAKE_1R / STAKE_1R
    else:
        return -1.0


def run_backtest(num_races: int = 500) -> Dict:
    """Run backtest simulation."""
    print("="*60)
    print("STEAMARB BACKTESTER")
    print("="*60)
    print(f"Races: {num_races}")
    print(f"Time: {datetime.now()}")
    print()

    trades = []
    stats = {"ARB": {"count": 0, "wins": 0, "total_r": 0},
             "STEAM": {"count": 0, "wins": 0, "total_r": 0},
             "VALUE": {"count": 0, "wins": 0, "total_r": 0}}

    for race_num in range(1, num_races + 1):
        runners = generate_race(race_num)

        for runner in runners:
            # ARB
            arb_r = detect_arb(runner["lad_price"], runner["bf_lay"])
            if arb_r:
                trades.append(Trade(
                    engine="ARB",
                    runner_name=runner["name"],
                    back_price=runner["lad_price"],
                    lay_price=runner["bf_lay"],
                    profit_r=arb_r,
                    won=True
                ))
                stats["ARB"]["count"] += 1
                stats["ARB"]["wins"] += 1
                stats["ARB"]["total_r"] += arb_r

            # STEAM
            steam_r = detect_steam(runner["flucs"], runner["bf_back"], runner["lad_price"])
            if steam_r:
                won = steam_r > 0
                trades.append(Trade(
                    engine="STEAM",
                    runner_name=runner["name"],
                    back_price=runner["bf_back"],
                    lay_price=runner["lad_price"],
                    profit_r=steam_r,
                    won=won
                ))
                stats["STEAM"]["count"] += 1
                if won:
                    stats["STEAM"]["wins"] += 1
                stats["STEAM"]["total_r"] += steam_r

            # VALUE
            value_r = detect_value(runner["bf_back"], runner["lad_price"], runner["true_prob"])
            if value_r:
                won = value_r > 0
                trades.append(Trade(
                    engine="VALUE",
                    runner_name=runner["name"],
                    back_price=runner["lad_price"],
                    lay_price=0,
                    profit_r=value_r,
                    won=won
                ))
                stats["VALUE"]["count"] += 1
                if won:
                    stats["VALUE"]["wins"] += 1
                stats["VALUE"]["total_r"] += value_r

        if race_num % 100 == 0:
            print(f"  Processed {race_num}/{num_races} races...")

    # Results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    for engine, s in stats.items():
        if s["count"] > 0:
            win_rate = (s["wins"] / s["count"]) * 100
            avg_r = s["total_r"] / s["count"]
            print(f"\n{engine}:")
            print(f"  Trades: {s['count']}")
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  Total R: {s['total_r']:+.4f}")
            print(f"  Avg R/trade: {avg_r:+.4f}")

    total_trades = sum(s["count"] for s in stats.values())
    total_r = sum(s["total_r"] for s in stats.values())
    avg_r = total_r / total_trades if total_trades > 0 else 0

    print("\n" + "-"*60)
    print(f"TOTAL:")
    print(f"  Trades: {total_trades}")
    print(f"  Total R: {total_r:+.4f}")
    print(f"  Avg R/trade: {avg_r:+.4f}")
    print(f"  Total AUD: ${total_r:.2f}")
    print("="*60)

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "races": num_races,
        "stats": stats,
        "total_trades": total_trades,
        "total_r": total_r,
        "avg_r_per_trade": avg_r
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_FILE}")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use simulated data")
    parser.add_argument("--races", type=int, default=500, help="Number of races to simulate")
    args = parser.parse_args()

    if args.demo:
        run_backtest(args.races)
    else:
        print("Use --demo flag for simulated backtest")


if __name__ == "__main__":
    main()
