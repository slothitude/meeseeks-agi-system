#!/usr/bin/env python3
"""
Betfair Live Steam Analyser
============================

Connects to real Betfair API and analyses Australian horse racing markets.

Usage:
    python live_steam_analyser.py
"""

import requests
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Strategy params
MIN_BACK_ODDS = 2.0
MAX_BACK_ODDS = 15.0
MIN_ODDS_DROP = 0.2
STAKE_1R = 1.00
COMMISSION = 0.05

STATE_FILE = Path("live_steam_results.json")


class LiveSteamAnalyser:
    def __init__(self):
        self.token = None
        self.opportunities = []
        
    def login(self):
        """Login to Betfair API"""
        print("Connecting to Betfair API...")
        
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
                timeout=15
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('loginStatus') == 'SUCCESS':
                    self.token = data.get('sessionToken')
                    print(f"[OK] Logged in")
                    return True
                else:
                    print(f"[FAIL] {data.get('loginStatus')}")
            else:
                print(f"[FAIL] HTTP {r.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        return False
    
    def api(self, method, params):
        """Make API request"""
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
    
    def get_au_horse_markets(self, hours_ahead=24):
        """Get Australian horse racing markets"""
        print(f"\nFetching AU horse racing markets (next {hours_ahead}h)...")
        
        now = datetime.now()
        later = now + timedelta(hours=hours_ahead)
        
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["2996873"],  # Australian horse racing
                "marketTypeCodes": ["WIN"],
                "marketStartTime": {
                    "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": later.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            },
            "maxResults": 100,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        })
        
        if result:
            print(f"[OK] Found {len(result)} markets")
            return result
        
        # Try without country filter
        result = self.api("SportsAPING/v1.0/listMarketCatalogue", {
            "filter": {
                "eventTypeIds": ["1"],  # All horse racing
                "marketTypeCodes": ["WIN"],
                "marketStartTime": {
                    "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": later.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            },
            "maxResults": 100,
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]
        })
        
        if result:
            print(f"[OK] Found {len(result)} markets (all regions)")
            return result
        
        print("[WARN] No markets found")
        return []
    
    def get_prices(self, market_id):
        """Get current prices"""
        result = self.api("SportsAPING/v1.0/listMarketBook", {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_ALL_OFFERS"]}
        })
        
        return result[0] if result else None
    
    def analyse_trade(self, back_odds, lay_odds):
        """Calculate R-value for trade"""
        if lay_odds >= back_odds:
            return None
        
        odds_drop = back_odds - lay_odds
        if odds_drop < MIN_ODDS_DROP:
            return None
        
        back_stake = STAKE_1R
        lay_stake = (back_stake * back_odds) / lay_odds
        
        # Green book
        back_profit = back_stake * (back_odds - 1)
        lay_liability = lay_stake * (lay_odds - 1)
        net_if_wins = back_profit - lay_liability
        net_if_loses = lay_stake - back_stake
        
        green_profit = min(net_if_wins, net_if_loses) * (1 - COMMISSION)
        r_value = green_profit / STAKE_1R
        
        return {
            'back_stake': back_stake,
            'lay_stake': round(lay_stake, 2),
            'green_profit': round(green_profit, 4),
            'r_value': round(r_value, 4),
            'odds_drop': round(odds_drop, 2),
            'odds_drop_pct': round((odds_drop / back_odds) * 100, 1)
        }
    
    def scan_markets(self):
        """Scan all markets for current opportunities"""
        markets = self.get_au_horse_markets(hours_ahead=6)
        
        if not markets:
            return []
        
        opportunities = []
        
        print(f"\n{'='*60}")
        print("SCANNING MARKETS FOR STEAM OPPORTUNITIES")
        print(f"{'='*60}")
        
        for m in markets:
            market_id = m.get('marketId')
            event_name = m.get('event', {}).get('eventName', 'Unknown')
            market_name = m.get('marketName', 'Unknown')
            start_time = m.get('marketStartTime')
            
            # Get prices
            book = self.get_prices(market_id)
            
            if not book or book.get('status') != 'OPEN':
                continue
            
            # Time to start
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_to_start = (start_dt - datetime.now(start_dt.tzinfo)).total_seconds() / 60
                except:
                    time_to_start = 999
            else:
                time_to_start = 999
            
            # Only scan markets 2-15 mins out
            if time_to_start < 2 or time_to_start > 15:
                continue
            
            for runner in m.get('runners', []):
                rid = runner.get('selectionId')
                rname = runner.get('runnerName', 'Unknown')
                
                # Get prices
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
                back_size = back[0]['size']
                lay_size = lay[0]['size']
                
                # Filter odds
                if not (MIN_BACK_ODDS <= back_price <= MAX_BACK_ODDS):
                    continue
                
                # Check liquidity
                if back_size < 20 or lay_size < 20:
                    continue
                
                spread = lay_price - back_price
                
                # Record snapshot
                opp = {
                    'time': datetime.now().isoformat(),
                    'market_id': market_id,
                    'event': event_name,
                    'market': market_name,
                    'runner': rname,
                    'back_price': back_price,
                    'lay_price': lay_price,
                    'spread': round(spread, 2),
                    'back_size': back_size,
                    'lay_size': lay_size,
                    'time_to_start': round(time_to_start, 1)
                }
                
                opportunities.append(opp)
                
                # Display
                print(f"\n{event_name} - {rname}")
                print(f"  BACK {back_price:.2f} (${back_size:.0f}) | LAY {lay_price:.2f} (${lay_size:.0f})")
                print(f"  Spread: {spread:.2f} | Time: {time_to_start:.1f}min")
            
            time.sleep(0.3)  # Rate limit
        
        return opportunities
    
    def run_tracking_session(self, duration_minutes=10):
        """Track markets over time to detect steam"""
        print(f"\n{'='*60}")
        print("LIVE STEAM TRACKING SESSION")
        print(f"{'='*60}")
        print(f"Duration: {duration_minutes} min")
        print(f"Looking for: Odds compression (steam moves)")
        print()
        
        if not self.login():
            return
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        all_snapshots = []
        scan_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{scan_count}")
            
            opps = self.scan_markets()
            all_snapshots.extend(opps)
            
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining > 30:
                print(f"\nWaiting 30s... ({remaining:.0f}s remaining)")
                time.sleep(30)
        
        # Analyse results
        self.analyse_session(all_snapshots)
        
        return all_snapshots
    
    def analyse_session(self, snapshots):
        """Analyse all snapshots for steam patterns"""
        if not snapshots:
            print("\nNo data collected")
            return
        
        print(f"\n{'='*60}")
        print("SESSION ANALYSIS")
        print(f"{'='*60}")
        
        df = pd.DataFrame(snapshots)
        
        print(f"\nTotal snapshots: {len(df)}")
        print(f"Unique markets: {df['market_id'].nunique()}")
        print(f"Unique runners: {len(df.groupby(['market_id', 'runner']))}")
        
        # Find steam patterns (same runner, odds dropping over time)
        print(f"\n{'='*60}")
        print("STEAM DETECTION (Odds Compression)")
        print(f"{'='*60}")
        
        steam_found = 0
        
        for (market_id, runner_id), group in df.groupby(['market_id', 'runner']):
            if len(group) < 2:
                continue
            
            group = group.sort_values('time')
            first_back = group.iloc[0]['back_price']
            last_back = group.iloc[-1]['back_price']
            first_lay = group.iloc[0]['lay_price']
            last_lay = group.iloc[-1]['lay_price']
            
            back_drop = first_back - last_back
            lay_drop = first_lay - last_lay
            
            # Steam = odds compressing
            if back_drop >= MIN_ODDS_DROP:
                steam_found += 1
                runner = group.iloc[0]['runner']
                event = group.iloc[0]['event']
                
                # Calculate R-value
                trade = self.analyse_trade(first_back, last_lay)
                
                if trade:
                    print(f"\n{event} - {runner}")
                    print(f"  BACK: {first_back:.2f} → {last_back:.2f} (drop {back_drop:.2f})")
                    print(f"  LAY:  {first_lay:.2f} → {last_lay:.2f} (drop {lay_drop:.2f})")
                    print(f"  Trade: BACK @ {first_back:.2f}, LAY @ {last_lay:.2f}")
                    print(f"  R-value: +{trade['r_value']:.4f}R")
                    print(f"  Profit: +${trade['green_profit']:.2f} (green book)")
        
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Steam moves detected: {steam_found}")
        
        if steam_found > 0:
            print(f"\nIf all traded @ 1R = $1:")
            print(f"  Potential profit: ${steam_found * 0.16:.2f}")
            print(f"If 1R = $10:")
            print(f"  Potential profit: ${steam_found * 1.60:.2f}")
        
        # Save results
        df.to_csv("live_steam_session.csv", index=False)
        print(f"\n[OK] Session data saved to live_steam_session.csv")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=10, help='Tracking duration in minutes')
    args = parser.parse_args()
    
    analyser = LiveSteamAnalyser()
    analyser.run_tracking_session(duration_minutes=args.duration)


if __name__ == "__main__":
    main()
