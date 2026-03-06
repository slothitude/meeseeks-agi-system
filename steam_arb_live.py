#!/usr/bin/env python3
"""
SteamArb Live Engine - PRODUCTION
==================================

Combines Betfair + Ladbrokes prices in real-time.
Runs all three engines (ARB, STEAM, VALUE).
Logs opportunities to JSON for dashboard.

Usage:
    python steam_arb_live.py --paper          # Paper trading (log only)
    python steam_arb_live.py --paper --test   # Test with demo prices
"""

import requests
import json
import time
import urllib3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

urllib3.disable_warnings()

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
BETFAIR_USERNAME = "dnfarnot@gmail.com"
BETFAIR_PASSWORD = "Tobiano01"
BETFAIR_APP_KEY = "XmZEwtLsIRkf5lQ3"
BETFAIR_CERT = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

LADBROKES_EMAIL = "slothitudegames@gmail.com"
LADBROKES_PARTNER = "Slothitude Games"

# ─────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────
STAKE_1R = 1.00  # AUD
COMMISSION = 0.05
MIN_ARB_PROFIT_PCT = 0.5
MIN_STEAM_DROP_PCT = 5.0
MIN_VALUE_EDGE_PCT = 10.0
POLL_INTERVAL = 30  # seconds
MIN_BACK_ODDS = 2.0
MAX_BACK_ODDS = 15.0

OUTPUT_JSON = Path("steamarb_opportunities.json")
OUTPUT_CSV = Path("steamarb_log.csv")

# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class Opportunity:
    engine: str
    priority: str
    timestamp: str
    runner_name: str
    meeting_name: str
    race_number: int
    betfair_back: float
    betfair_lay: float
    ladbrokes_back: float
    action: str
    back_at: str
    lay_at: str
    profit_r: float
    profit_aud: float
    edge_pct: float
    status: str = "OPEN"


# ─────────────────────────────────────────────
# BETFAIR API
# ─────────────────────────────────────────────

class BetfairAPI:
    def __init__(self):
        self.token = None
        
    def login(self) -> bool:
        payload = f"username={BETFAIR_USERNAME}&password={BETFAIR_PASSWORD}"
        headers = {
            'X-Application': BETFAIR_APP_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            r = requests.post(
                'https://identitysso-cert.betfair.com/api/certlogin',
                data=payload,
                cert=BETFAIR_CERT,
                headers=headers,
                timeout=15,
                verify=False
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('loginStatus') == 'SUCCESS':
                    self.token = data.get('sessionToken')
                    return True
        except:
            pass
        
        return False
    
    def api(self, method: str, params: dict):
        if not self.token:
            return None
        
        headers = {
            'X-Application': BETFAIR_APP_KEY,
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
    
    def get_au_markets(self, hours: int = 6) -> List[dict]:
        now = datetime.now()
        later = now + timedelta(hours=hours)
        
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["7"],  # Horse racing
                "marketCountries": ["AU"],
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
    
    def get_prices(self, market_ids: List[str]) -> List[dict]:
        if not market_ids:
            return []
        
        result = self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": market_ids,
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        
        return result or []


# ─────────────────────────────────────────────
# LADBROKES API
# ─────────────────────────────────────────────

class LadbrokesAPI:
    def __init__(self):
        self.headers = {
            "From": LADBROKES_EMAIL,
            "X-Partner": LADBROKES_PARTNER,
            "User-Agent": "SteamArb/1.0"
        }
        self.base_url = "https://api.ladbrokes.com.au/affiliates/v1"
    
    def get_meetings(self, category: str = "H") -> List[dict]:
        try:
            r = requests.get(
                f"{self.base_url}/racing/meetings",
                headers=self.headers,
                params={"date_from": "today", "category": category},
                timeout=10
            )
            
            if r.status_code == 200:
                return r.json().get("data", {}).get("meetings", [])
        except:
            pass
        
        return []
    
    def get_event_odds(self, event_id: str) -> Optional[dict]:
        try:
            r = requests.get(
                f"{self.base_url}/racing/events/{event_id}",
                headers=self.headers,
                timeout=10
            )
            
            if r.status_code == 200:
                return r.json()
        except:
            pass
        
        return None
    
    def fetch_au_prices(self) -> List[Dict]:
        """Fetch all AU horse racing prices."""
        all_runners = []
        
        meetings = self.get_meetings("H")
        
        for meeting in meetings:
            if meeting.get("country") != "AU":
                continue
            
            meeting_name = meeting.get("name", "Unknown")
            
            for race in meeting.get("races", []):
                event_id = race.get("id")
                race_number = race.get("race_number", 0)
                status = race.get("status", "")
                
                # Skip finished
                if status == "Final":
                    continue
                
                event_data = self.get_event_odds(event_id)
                
                if not event_data:
                    continue
                
                runners = event_data.get("data", {}).get("runners", [])
                
                for runner in runners:
                    if runner.get("is_scratched"):
                        continue
                    
                    name = runner.get("name", "")
                    odds = runner.get("odds", {})
                    fixed_win = odds.get("fixed_win", 0)
                    
                    if not fixed_win or fixed_win <= 1.01:
                        continue
                    
                    # Get flucs
                    flucs_data = runner.get("flucs_with_timestamp", {})
                    flucs = flucs_data.get("last_six", [])
                    
                    all_runners.append({
                        "runner_name": name,
                        "meeting_name": meeting_name,
                        "race_number": race_number,
                        "fixed_win": float(fixed_win),
                        "flucs": flucs
                    })
                
                # Rate limit
                time.sleep(0.1)
        
        return all_runners


# ─────────────────────────────────────────────
# NAME MATCHER
# ─────────────────────────────────────────────

def normalize_name(name: str) -> str:
    """Normalize runner name for matching."""
    return (
        name.lower()
        .replace("'", "")
        .replace("-", "")
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )


def match_runners(lad_runners: List[dict], bf_market: dict, bf_book: dict) -> List[Tuple[dict, dict]]:
    """Match Ladbrokes runners to Betfair runners."""
    matches = []
    
    for bf_runner in bf_market.get("runners", []):
        bf_name = normalize_name(bf_runner.get("runnerName", ""))
        bf_id = bf_runner.get("selectionId")
        
        # Get BF prices
        bf_back = None
        bf_lay = None
        
        for rbook in bf_book.get("runners", []):
            if rbook.get("selectionId") == bf_id:
                ex = rbook.get("ex", {})
                back_list = ex.get("availableToBack", [])
                lay_list = ex.get("availableToLay", [])
                
                if back_list:
                    bf_back = back_list[0]["price"]
                if lay_list:
                    bf_lay = lay_list[0]["price"]
                break
        
        if not bf_back or not bf_lay:
            continue
        
        # Find matching Ladbrokes runner
        for lad in lad_runners:
            lad_name = normalize_name(lad["runner_name"])
            
            # Exact match
            if bf_name == lad_name:
                matches.append((lad, {
                    "name": bf_runner.get("runnerName"),
                    "back": bf_back,
                    "lay": bf_lay,
                    "selection_id": bf_id
                }))
                break
            
            # Partial match (one contains the other)
            if len(bf_name) > 5 and (bf_name in lad_name or lad_name in bf_name):
                matches.append((lad, {
                    "name": bf_runner.get("runnerName"),
                    "back": bf_back,
                    "lay": bf_lay,
                    "selection_id": bf_id
                }))
                break
    
    return matches


# ─────────────────────────────────────────────
# ENGINES
# ─────────────────────────────────────────────

def detect_arb(lad_back: float, bf_lay: float) -> Optional[dict]:
    """ENGINE 1: Arbitrage"""
    if lad_back <= bf_lay:
        return None
    
    back_stake = STAKE_1R
    lay_stake = back_stake * lad_back / bf_lay
    
    net_wins = back_stake * (lad_back - 1) - lay_stake * (bf_lay - 1)
    net_loses = lay_stake - back_stake
    
    if net_wins <= 0 or net_loses <= 0:
        return None
    
    profit = min(net_wins, net_loses) * (1 - COMMISSION)
    profit_pct = (profit / back_stake) * 100
    
    if profit_pct < MIN_ARB_PROFIT_PCT:
        return None
    
    return {
        "profit": profit,
        "profit_r": profit / STAKE_1R,
        "edge_pct": profit_pct
    }


def detect_steam(flucs: List[dict], bf_back: float, lad_back: float) -> Optional[dict]:
    """ENGINE 2: Steam moves"""
    if not flucs or len(flucs) < 2:
        return None
    
    # Get price movement
    prices = [f["fluc"] for f in flucs]
    
    if len(prices) < 2:
        return None
    
    # Check for drop
    old_price = prices[0]  # Earliest
    new_price = prices[-1]  # Latest
    
    if old_price <= new_price:
        return None  # Price went up, not steam
    
    drop_pct = ((old_price - new_price) / old_price) * 100
    
    if drop_pct < MIN_STEAM_DROP_PCT:
        return None
    
    # Betfair should still be higher (hasn't caught up)
    if bf_back <= lad_back:
        return None
    
    gap_pct = ((bf_back - lad_back) / bf_back) * 100
    
    # Expected lay price (where market is heading)
    expected_lay = lad_back * 1.03
    
    if expected_lay >= bf_back:
        return None
    
    # Calculate green book
    back_stake = STAKE_1R
    lay_stake = (back_stake * bf_back) / expected_lay
    
    net_wins = back_stake * (bf_back - 1) - lay_stake * (expected_lay - 1)
    net_loses = lay_stake - back_stake
    
    profit = min(net_wins, net_loses) * (1 - COMMISSION)
    
    if profit <= 0:
        return None
    
    return {
        "profit": profit,
        "profit_r": profit / STAKE_1R,
        "drop_pct": drop_pct,
        "expected_lay": expected_lay,
        "edge_pct": gap_pct
    }


def detect_value(bf_back: float, lad_back: float) -> Optional[dict]:
    """ENGINE 3: Value betting"""
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
        "profit": ev_r * STAKE_1R,
        "profit_r": ev_r,
        "edge_pct": edge_pct
    }


# ─────────────────────────────────────────────
# OPPORTUNITY LOGGER
# ─────────────────────────────────────────────

opportunities_log: List[dict] = []

def log_opportunity(opp: Opportunity):
    opportunities_log.insert(0, asdict(opp))
    
    if len(opportunities_log) > 200:
        opportunities_log.pop()
    
    # Write JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(opportunities_log, f, indent=2, default=str)
    
    # Append CSV
    file_exists = OUTPUT_CSV.exists()
    with open(OUTPUT_CSV, "a", newline="") as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=asdict(opp).keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(asdict(opp))
    
    # Print
    symbol = {"ARB": "⚡️", "STEAM": "🔥", "VALUE": "💎"}.get(opp.engine, "•")
    print(f"\n{symbol} [{opp.engine}] {opp.priority}")
    print(f"  {opp.runner_name} - {opp.meeting_name} R{opp.race_number}")
    print(f"  {opp.action}")
    print(f"  Profit: +{opp.profit_r:.4f}R (${opp.profit_aud:.4f})")


# ─────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────

class SteamArbEngine:
    def __init__(self, paper_mode: bool = True):
        self.paper_mode = paper_mode
        self.betfair = BetfairAPI()
        self.ladbrokes = LadbrokesAPI()
        self.scan_count = 0
        self.total_opps = 0
    
    def run_cycle(self):
        """Run one scan cycle."""
        self.scan_count += 1
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{self.scan_count}", flush=True)
        
        # Get Ladbrokes AU prices
        print("  Fetching Ladbrokes AU...", flush=True)
        lad_runners = self.ladbrokes.fetch_au_prices()
        print(f"  Found {len(lad_runners)} Ladbrokes runners", flush=True)
        
        if not lad_runners:
            print("  No Ladbrokes data", flush=True)
            return
        
        # Get Betfair AU markets
        print("  Fetching Betfair AU...", flush=True)
        bf_markets = self.betfair.get_au_markets(hours=6)
        print(f"  Found {len(bf_markets)} Betfair markets", flush=True)
        
        if not bf_markets:
            print("  No Betfair data", flush=True)
            return
        
        # Get Betfair prices (batch)
        market_ids = [m["marketId"] for m in bf_markets[:20]]
        bf_books = self.betfair.get_prices(market_ids)
        
        if not bf_books:
            print("  No Betfair prices", flush=True)
            return
        
        # Create price lookup
        bf_by_id = {b["marketId"]: b for b in bf_books}
        
        # Process each market
        found = 0
        
        for market in bf_markets:
            market_id = market["marketId"]
            event_name = market.get("event", {}).get("eventName", "Unknown")
            
            if market_id not in bf_by_id:
                continue
            
            book = bf_by_id[market_id]
            
            if book.get("status") != "OPEN":
                continue
            
            # Match runners
            matches = match_runners(lad_runners, market, book)
            
            for lad, bf in matches:
                lad_back = lad["fixed_win"]
                bf_back = bf["back"]
                bf_lay = bf["lay"]
                flucs = lad.get("flucs", [])
                
                # ENGINE 1: ARB
                arb = detect_arb(lad_back, bf_lay)
                if arb:
                    priority = "HIGH" if arb["edge_pct"] > 3 else ("MEDIUM" if arb["edge_pct"] > 1.5 else "LOW")
                    
                    opp = Opportunity(
                        engine="ARB",
                        priority=priority,
                        timestamp=datetime.now().isoformat(),
                        runner_name=bf["name"],
                        meeting_name=event_name,
                        race_number=lad["race_number"],
                        betfair_back=bf_back,
                        betfair_lay=bf_lay,
                        ladbrokes_back=lad_back,
                        action=f"BACK Ladbrokes @{lad_back:.2f} | LAY Betfair @{bf_lay:.2f}",
                        back_at="Ladbrokes",
                        lay_at="Betfair",
                        profit_r=round(arb["profit_r"], 4),
                        profit_aud=round(arb["profit"], 4),
                        edge_pct=round(arb["edge_pct"], 2)
                    )
                    log_opportunity(opp)
                    found += 1
                
                # ENGINE 2: STEAM
                steam = detect_steam(flucs, bf_back, lad_back)
                if steam:
                    priority = "HIGH" if steam["drop_pct"] > 15 else ("MEDIUM" if steam["drop_pct"] > 10 else "LOW")
                    
                    opp = Opportunity(
                        engine="STEAM",
                        priority=priority,
                        timestamp=datetime.now().isoformat(),
                        runner_name=bf["name"],
                        meeting_name=event_name,
                        race_number=lad["race_number"],
                        betfair_back=bf_back,
                        betfair_lay=bf_lay,
                        ladbrokes_back=lad_back,
                        action=f"BACK Betfair @{bf_back:.2f} | LAY @{steam['expected_lay']:.2f} | Steam -{steam['drop_pct']:.1f}%",
                        back_at="Betfair",
                        lay_at="Betfair",
                        profit_r=round(steam["profit_r"], 4),
                        profit_aud=round(steam["profit"], 4),
                        edge_pct=round(steam["edge_pct"], 2)
                    )
                    log_opportunity(opp)
                    found += 1
                
                # ENGINE 3: VALUE
                value = detect_value(bf_back, lad_back)
                if value:
                    priority = "HIGH" if value["edge_pct"] > 20 else ("MEDIUM" if value["edge_pct"] > 15 else "LOW")
                    
                    opp = Opportunity(
                        engine="VALUE",
                        priority=priority,
                        timestamp=datetime.now().isoformat(),
                        runner_name=bf["name"],
                        meeting_name=event_name,
                        race_number=lad["race_number"],
                        betfair_back=bf_back,
                        betfair_lay=bf_lay,
                        ladbrokes_back=lad_back,
                        action=f"BACK Ladbrokes @{lad_back:.2f} | Edge +{value['edge_pct']:.1f}%",
                        back_at="Ladbrokes",
                        lay_at="hold",
                        profit_r=round(value["profit_r"], 4),
                        profit_aud=round(value["profit"], 4),
                        edge_pct=round(value["edge_pct"], 2)
                    )
                    log_opportunity(opp)
                    found += 1
        
        self.total_opps += found
        print(f"  Found: {found} | Total: {self.total_opps}", flush=True)
        
        if opportunities_log:
            total_r = sum(o["profit_r"] for o in opportunities_log)
            print(f"  Total R: +{total_r:.4f}R", flush=True)
    
    def run(self, duration_mins: int = 30):
        """Run engine for specified duration."""
        print("="*60)
        print("STEAMARB LIVE ENGINE")
        print("="*60)
        print(f"Mode: {'PAPER TRADING' if self.paper_mode else 'LIVE'}")
        print(f"Duration: {duration_mins} minutes")
        print(f"1R = ${STAKE_1R}")
        print(f"Interval: {POLL_INTERVAL}s")
        print()
        
        if not self.betfair.login():
            print("Betfair login failed")
            return
        
        print("[OK] Connected to Betfair")
        print("[OK] Ladbrokes API ready")
        print()
        
        end_time = datetime.now() + timedelta(minutes=duration_mins)
        
        while datetime.now() < end_time:
            try:
                self.run_cycle()
                
                remaining = (end_time - datetime.now()).total_seconds()
                if remaining > POLL_INTERVAL:
                    time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                print("\n\nStopped by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
                time.sleep(5)
        
        # Summary
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        print(f"Scans: {self.scan_count}")
        print(f"Opportunities: {self.total_opps}")
        
        if opportunities_log:
            total_r = sum(o["profit_r"] for o in opportunities_log)
            arbs = [o for o in opportunities_log if o["engine"] == "ARB"]
            steams = [o for o in opportunities_log if o["engine"] == "STEAM"]
            values = [o for o in opportunities_log if o["engine"] == "VALUE"]
            
            print(f"\nBy Engine:")
            print(f"  ⚡️ ARB: {len(arbs)}")
            print(f"  🔥 STEAM: {len(steams)}")
            print(f"  💎 VALUE: {len(values)}")
            print(f"\nTotal R: +{total_r:.4f}R")
            print(f"Total AUD: ${total_r * STAKE_1R:.2f}")
        
        print("="*60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", action="store_true", default=True)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()
    
    engine = SteamArbEngine(paper_mode=args.paper)
    engine.run(duration_mins=args.duration)


if __name__ == "__main__":
    main()
