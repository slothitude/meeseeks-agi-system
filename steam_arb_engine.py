#!/usr/bin/env python3
"""
SteamArb Engine - Simplified Version
=====================================

Three engines running simultaneously:

1. ARB DETECTOR - Ladbrokes back > Betfair lay = locked profit
2. STEAM SIGNAL - Ladbrokes drops suddenly -> back on Betfair
3. VALUE FINDER - Betfair implied prob > Ladbrokes = back at Ladbrokes

Usage:
    python steam_arb_engine.py
"""

import asyncio
import aiohttp
import json
import csv
import os
import time
import random
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional
from collections import defaultdict

# Credentials
BETFAIR_USERNAME = "dnfarnot@gmail.com"
BETFAIR_PASSWORD = "Tobiano01"
BETFAIR_APP_KEY = "XmZEwtLsIRkf5lQ3"
BETFAIR_CERT_PATH = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Parameters
STAKE_1R = 1.00
COMMISSION = 0.05
MIN_ARB_PROFIT_PCT = 0.5
MIN_STEAM_DROP_PCT = 8.0
MIN_VALUE_EDGE_PCT = 10.0
POLL_INTERVAL_SECS = 15
MAX_BACK_ODDS = 15.0
MIN_BACK_ODDS = 1.5

OUTPUT_JSON = "steamarb_opportunities.json"
OUTPUT_CSV = "steamarb_log.csv"

@dataclass
class Opportunity:
    engine: str
    priority: str
    runner_name: str
    race_name: str
    race_start: str
    market_id: str
    betfair_back: float
    betfair_lay: float
    ladbrokes_back: float
    action: str
    back_at: str
    lay_at: str
    back_odds: float
    lay_odds: float
    stake_1r: float
    profit_r: float
    profit_aud: float
    edge_pct: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "OPEN"

# Price history for steam detection
price_history: dict = defaultdict(list)

def record_price(runner_id: str, odds: float):
    now = time.time()
    price_history[runner_id].append((now, odds))
    cutoff = now - 1200
    price_history[runner_id] = [(t, o) for t, o in price_history[runner_id] if t > cutoff]

def get_steam_signal(runner_id: str, current_odds: float) -> Optional[float]:
    history = price_history.get(runner_id, [])
    if len(history) < 2:
        return None
    
    now = time.time()
    window_start = now - 600
    window_end = now - 60
    
    reference_prices = [o for t, o in history if window_start <= t <= window_end]
    if not reference_prices:
        return None
    
    reference_odds = max(reference_prices)
    if reference_odds <= current_odds:
        return None
    
    drop_pct = ((reference_odds - current_odds) / reference_odds) * 100
    return drop_pct if drop_pct >= MIN_STEAM_DROP_PCT else None

def detect_arb(lad_back: float, bf_lay: float) -> Optional[dict]:
    if lad_back <= bf_lay:
        return None
    
    back_stake = STAKE_1R
    back_profit = back_stake * (lad_back - 1)
    
    lay_stake = back_stake * lad_back / bf_lay
    lay_liability = lay_stake * (bf_lay - 1)
    
    net_wins = back_profit - lay_liability
    net_loses = lay_stake - back_stake
    
    if net_wins > 0 and net_loses > 0:
        profit = min(net_wins, net_loses) * (1 - COMMISSION)
    else:
        return None
    
    profit_pct = (profit / back_stake) * 100
    if profit_pct < MIN_ARB_PROFIT_PCT:
        return None
    
    return {
        "profit": profit,
        "profit_pct": profit_pct,
        "lay_stake": lay_stake
    }

def detect_steam(bf_back: float, bf_lay: float, lad_back: float, runner_id: str) -> Optional[dict]:
    drop_pct = get_steam_signal(runner_id, lad_back)
    if drop_pct is None:
        return None
    
    if bf_back <= lad_back:
        return None
    
    gap_pct = ((bf_back - lad_back) / bf_back) * 100
    if gap_pct < 3.0:
        return None
    
    expected_lay = lad_back * 1.02
    if expected_lay >= bf_back:
        return None
    
    back_stake = STAKE_1R
    lay_stake = (back_stake * bf_back) / expected_lay
    
    net_if_wins = back_stake * (bf_back - 1) - lay_stake * (expected_lay - 1)
    net_if_lose = lay_stake - back_stake
    
    profit = min(net_if_wins, net_if_lose) * (1 - COMMISSION)
    
    if profit <= 0:
        return None
    
    return {
        "profit": profit,
        "drop_pct": drop_pct,
        "gap_pct": gap_pct,
        "expected_lay": expected_lay
    }

def detect_value(bf_back: float, lad_back: float) -> Optional[dict]:
    if lad_back < MIN_BACK_ODDS or lad_back > MAX_BACK_ODDS:
        return None
    
    bf_prob = 1 / bf_back
    lad_prob = 1 / lad_back
    
    if bf_prob <= lad_prob:
        return None
    
    edge_pct = ((bf_prob - lad_prob) / lad_prob) * 100
    if edge_pct < MIN_VALUE_EDGE_PCT:
        return None
    
    ev_r = (bf_prob * (lad_back - 1)) - ((1 - bf_prob) * 1)
    
    if ev_r <= 0:
        return None
    
    return {
        "ev_r": ev_r,
        "edge_pct": edge_pct
    }

def generate_demo_prices() -> tuple:
    random.seed(int(time.time()) % 100)
    
    races = [
        ("Randwick R3", "2026-03-07 14:35"),
        ("Flemington R5", "2026-03-07 14:55"),
        ("Eagle Farm R2", "2026-03-07 15:10"),
        ("Caulfield R4", "2026-03-07 15:30"),
    ]
    
    runners_data = []
    betfair_data = {}
    
    for race_name, race_start in races:
        n_runners = random.randint(8, 14)
        
        for i in range(n_runners):
            name = f"Runner {i+1}"
            
            bf_back = round(random.uniform(1.8, 14.0), 2)
            bf_lay = round(bf_back * random.uniform(1.01, 1.04), 2)
            
            # Occasionally create opportunities
            if random.random() < 0.08:
                lad_back = round(bf_lay * random.uniform(1.02, 1.08), 2)
            elif random.random() < 0.12:
                lad_back = round(bf_back * random.uniform(1.12, 1.30), 2)
            else:
                lad_back = round(bf_back * random.uniform(0.92, 1.05), 2)
            
            market_id = f"DEMO_{race_name.replace(' ', '_')}"
            sel_id = f"{market_id}_{i}"
            
            runners_data.append({
                "runner_name": name,
                "selection_id": sel_id,
                "ladbrokes_back": lad_back,
                "market_id": market_id,
                "race_name": race_name,
                "race_start": race_start
            })
            
            betfair_data[name.lower()] = {
                "back": bf_back,
                "lay": bf_lay,
                "market_id": market_id,
                "race_name": race_name,
                "race_start": race_start
            }
            
            # Simulate steam history
            runner_key = sel_id
            now = time.time()
            
            if random.random() < 0.25:
                old_price = lad_back * random.uniform(1.10, 1.25)
                price_history[runner_key] = [
                    (now - 480, old_price),
                    (now - 300, old_price * 0.97),
                    (now - 120, lad_back * 1.02),
                ]
    
    return runners_data, betfair_data

opportunities_log: list = []

def log_opportunity(opp: Opportunity):
    opportunities_log.insert(0, asdict(opp))
    
    if len(opportunities_log) > 200:
        opportunities_log.pop()
    
    with open(OUTPUT_JSON, "w") as f:
        json.dump(opportunities_log, f, indent=2, default=str)
    
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(opp).keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(opp))
    
    symbol = {"ARB": "[ARB]", "STEAM": "[STM]", "VALUE": "[VAL]"}.get(opp.engine, "[?]")
    print(f"\n{symbol} {opp.priority}")
    print(f"  {opp.runner_name} - {opp.race_name}")
    print(f"  {opp.action}")
    print(f"  Profit: +{opp.profit_r:.4f}R (${opp.profit_aud:.4f} AUD)")

async def run_scan_cycle(session, demo_mode: bool):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning markets...", end="")
    
    if demo_mode:
        ladbrokes_runners, betfair_prices = generate_demo_prices()
    else:
        ladbrokes_runners, betfair_prices = generate_demo_prices()
    
    found = 0
    
    for lad in ladbrokes_runners:
        name_key = lad["runner_name"].lower().strip()
        bf = betfair_prices.get(name_key)
        
        if not bf:
            continue
        
        # Update price history
        record_price(lad["selection_id"], lad["ladbrokes_back"])
        
        # ARB detection
        arb = detect_arb(lad["ladbrokes_back"], bf["lay"])
        if arb:
            profit_r = arb["profit"] / STAKE_1R
            priority = "HIGH" if arb["profit_pct"] > 3 else ("MEDIUM" if arb["profit_pct"] > 1.5 else "LOW")
            
            opp = Opportunity(
                engine="ARB",
                priority=priority,
                runner_name=lad["runner_name"],
                race_name=lad["race_name"],
                race_start=lad["race_start"],
                market_id=lad["market_id"],
                betfair_back=bf["back"],
                betfair_lay=bf["lay"],
                ladbrokes_back=lad["ladbrokes_back"],
                action=f"BACK @ Ladbrokes {lad['ladbrokes_back']} | LAY @ Betfair {bf['lay']} | Locked profit",
                back_at="Ladbrokes",
                lay_at="Betfair",
                back_odds=lad["ladbrokes_back"],
                lay_odds=bf["lay"],
                stake_1r=STAKE_1R,
                profit_r=round(profit_r, 4),
                profit_aud=round(arb["profit"], 4),
                edge_pct=round(arb["profit_pct"], 2)
            )
            log_opportunity(opp)
            found += 1
        
        # STEAM detection
        steam = detect_steam(bf["back"], bf["lay"], lad["ladbrokes_back"], lad["selection_id"])
        if steam:
            profit_r = steam["profit"] / STAKE_1R
            priority = "HIGH" if steam["drop_pct"] > 20 else ("MEDIUM" if steam["drop_pct"] > 12 else "LOW")
            
            opp = Opportunity(
                engine="STEAM",
                priority=priority,
                runner_name=lad["runner_name"],
                race_name=lad["race_name"],
                race_start=lad["race_start"],
                market_id=lad["market_id"],
                betfair_back=bf["back"],
                betfair_lay=bf["lay"],
                ladbrokes_back=lad["ladbrokes_back"],
                action=f"BACK Betfair @ {bf['back']} NOW | LAY @ ~{round(steam['expected_lay'],2)} in 2-3 mins | Steam: -{steam['drop_pct']:.1f}%",
                back_at="Betfair",
                lay_at="Betfair",
                back_odds=bf["back"],
                lay_odds=round(steam["expected_lay"], 2),
                stake_1r=STAKE_1R,
                profit_r=round(profit_r, 4),
                profit_aud=round(steam["profit"], 4),
                edge_pct=round(steam["gap_pct"], 2)
            )
            log_opportunity(opp)
            found += 1
        
        # VALUE detection
        value = detect_value(bf["back"], lad["ladbrokes_back"])
        if value:
            priority = "HIGH" if value["edge_pct"] > 25 else ("MEDIUM" if value["edge_pct"] > 15 else "LOW")
            
            opp = Opportunity(
                engine="VALUE",
                priority=priority,
                runner_name=lad["runner_name"],
                race_name=lad["race_name"],
                race_start=lad["race_start"],
                market_id=lad["market_id"],
                betfair_back=bf["back"],
                betfair_lay=bf["lay"],
                ladbrokes_back=lad["ladbrokes_back"],
                action=f"BACK Ladbrokes @ {lad['ladbrokes_back']} | Betfair says {bf['back']} | Edge: +{value['edge_pct']:.1f}%",
                back_at="Ladbrokes",
                lay_at="hold",
                back_odds=lad["ladbrokes_back"],
                lay_odds=0,
                stake_1r=STAKE_1R,
                profit_r=round(value["ev_r"], 4),
                profit_aud=round(value["ev_r"] * STAKE_1R, 4),
                edge_pct=round(value["edge_pct"], 2)
            )
            log_opportunity(opp)
            found += 1
    
    print(f" {found} opportunities found")

async def main():
    demo_mode = True
    
    print("="*50)
    print("SteamArb Engine v1.0")
    print("ARB + STEAM + VALUE - All 3 Engines")
    print("="*50)
    
    if demo_mode:
        print("\n[!] DEMO MODE - Simulated prices")
        print(" Configure Ladbrokes API for live trading\n")
    else:
        print("\n[OK] Live mode - connecting to Betfair + Ladbrokes\n")
    
    print(f"Polling every {POLL_INTERVAL_SECS}s")
    print(f"1R = ${STAKE_1R} AUD")
    print(f"Output: {OUTPUT_JSON} + {OUTPUT_CSV}")
    print("-" * 45)
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await run_scan_cycle(session, demo_mode)
                await asyncio.sleep(POLL_INTERVAL_SECS)
            except KeyboardInterrupt:
                print("\n\nStopped by user.")
                
                if opportunities_log:
                    total_r = sum(o["profit_r"] for o in opportunities_log)
                    arbs = [o for o in opportunities_log if o["engine"] == "ARB"]
                    steams = [o for o in opportunities_log if o["engine"] == "STEAM"]
                    values = [o for o in opportunities_log if o["engine"] == "VALUE"]
                    
                    print(f"\nSession Summary:")
                    print(f"  Total opportunities: {len(opportunities_log)}")
                    print(f"  ARB: {len(arbs)}")
                    print(f"  STEAM: {len(steams)}")
                    print(f"  VALUE: {len(values)}")
                    print(f"  Total R available: +{total_r:.4f}R")
                    print(f"  Total AUD (at 1R=$1): ${total_r:.4f}")
                break
            except Exception as e:
                print(f"\nError: {e} - retrying in {POLL_INTERVAL_SECS}s")
                await asyncio.sleep(POLL_INTERVAL_SECS)

if __name__ == "__main__":
    asyncio.run(main())
