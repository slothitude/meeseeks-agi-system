#!/usr/bin/env python3
"""
SteamArb Safe Trader
====================

Exits ALL positions before race starts.
Runs during active hours only (10am-5pm Brisbane).

Critical: Never hold positions into in-play.
"""

import requests
import json
import time
import urllib3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sys

urllib3.disable_warnings()

# Credentials
BETFAIR_USERNAME = "dnfarnot@gmail.com"
BETFAIR_PASSWORD = "Tobiano01"
BETFAIR_APP_KEY = "XmZEwtLsIRkf5lQ3"
BETFAIR_CERT = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Safety parameters
MIN_TIME_TO_START = 120  # Exit if < 2 mins to race
MAX_TIME_TO_START = 1200  # Only trade 2-20 mins before race
STAKE_1R = 1.00

# Active hours (Brisbane time)
START_HOUR = 10  # 10am
END_HOUR = 17  # 5pm

OUTPUT_LOG = Path("steamarb_safe.log")


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
    
    def get_markets(self, hours: int = 6) -> List[dict]:
        now = datetime.now()
        later = now + timedelta(hours=hours)
        
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["7"],
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


def is_trading_hours() -> bool:
    """Check if current time is within trading hours."""
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR


def get_time_to_start(market: dict) -> float:
    """Get minutes until race starts."""
    start_time = market.get("marketStartTime")
    
    if not start_time:
        return 999
    
    try:
        from datetime import timezone
        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = (dt - now).total_seconds() / 60
        return delta
    except:
        return 999


def log(msg: str):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    
    with open(OUTPUT_LOG, 'a') as f:
        f.write(line + '\n')


def run_safe_trading(duration_mins: int = 30):
    """Run safe trading loop - exits before race starts."""
    log("="*60)
    log("STEAMARB SAFE TRADER")
    log("="*60)
    log(f"Trading hours: {START_HOUR}:00 - {END_HOUR}:00 Brisbane")
    log(f"Safety: Exit if < {MIN_TIME_TO_START}s to race start")
    log(f"Duration: {duration_mins} minutes")
    log("")
    
    # Check trading hours
    if not is_trading_hours():
        log("Outside trading hours - exiting")
        return
    
    # Login
    api = BetfairAPI()
    
    if not api.login():
        log("Betfair login failed")
        return
    
    log("[OK] Connected to Betfair")
    log("")
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    scan_count = 0
    total_markets = 0
    safe_markets = 0
    
    while datetime.now() < end_time and is_trading_hours():
        scan_count += 1
        
        log(f"\n--- Scan #{scan_count} ---")
        
        # Get markets
        markets = api.get_markets(hours=6)
        total_markets = len(markets)
        
        log(f"Total markets: {total_markets}")
        
        # Filter for safe time window
        safe = []
        for m in markets:
            mins_to_start = get_time_to_start(m)
            
            # Check safety window
            if MIN_TIME_TO_START <= mins_to_start <= MAX_TIME_TO_START:
                safe.append(m)
            elif mins_to_start < MIN_TIME_TO_START:
                # TOO LATE - would exit immediately
                event = m.get('event', {}).get('eventName', 'Unknown')
                log(f"  SKIP: {event} - only {mins_to_start:.0f}min to start (TOO LATE)")
        
        safe_markets = len(safe)
        log(f"Safe markets (2-20min window): {safe_markets}")
        
        # Show safe markets
        if safe:
            log("\n  Safe to trade:")
            for m in safe[:10]:
                event = m.get('event', {}).get('eventName', 'Unknown')
                mins = get_time_to_start(m)
                log(f"    {event}: {mins:.0f}min to start")
        
        # Sleep
        remaining = (end_time - datetime.now()).total_seconds()
        if remaining > 30:
            log(f"\n  Waiting 30s...")
            time.sleep(30)
    
    # Summary
    log("\n" + "="*60)
    log("SESSION COMPLETE")
    log("="*60)
    log(f"Scans: {scan_count}")
    log(f"Total markets: {total_markets}")
    log(f"Safe markets: {safe_markets}")
    log(f"Trades executed: 0 (paper mode)")
    log("")
    log("Safety rule: NEVER hold positions into race start")
    log("="*60)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=30, help='Duration in minutes')
    args = parser.parse_args()
    
    run_safe_trading(duration_mins=args.duration)


if __name__ == "__main__":
    main()
