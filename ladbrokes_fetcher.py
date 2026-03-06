#!/usr/bin/env python3
"""
Ladbrokes/Neds Price Fetcher - PRODUCTION v2
=============================================

Fixed version - uses races embedded in meeting object.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

HEADERS = {
    "From": "slothitudegames@gmail.com",
    "X-Partner": "Slothitude Games",
    "User-Agent": "SteamArb/1.0"
}

BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"


def get_meetings(date: str = "today", category: str = "H") -> Optional[List[dict]]:
    """Get all racing meetings for a date."""
    url = f"{BASE_URL}/racing/meetings"
    params = {
        "date_from": date,
        "date_to": date,
        "category": category
    }
    
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            return data.get("data", {}).get("meetings", [])
    
    except Exception as e:
        print(f"Error fetching meetings: {e}")
    
    return None


def get_event_odds(event_id: str) -> Optional[dict]:
    """Get full odds for a specific race."""
    url = f"{BASE_URL}/racing/events/{event_id}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        
        if r.status_code == 200:
            return r.json()
    
    except Exception as e:
        pass
    
    return None


def fetch_all_prices(categories: List[str] = ["H", "G"], au_only: bool = True) -> List[Dict]:
    """
    Fetch all current prices.
    """
    all_runners = []
    
    for category in categories:
        print(f"\n[{category}] Fetching meetings...", flush=True)
        meetings = get_meetings(date="today", category=category)
        
        if not meetings:
            continue
        
        print(f"  Found {len(meetings)} meetings", flush=True)
        
        for meeting in meetings[:15]:
            meeting_name = meeting.get("name", "Unknown")
            country = meeting.get("country", "")
            
            # Filter for AU only if requested
            if au_only and country != "AU":
                continue
            
            print(f"\n  [{meeting_name}] ({country})", flush=True)
            
            # Get races from meeting object
            races = meeting.get("races", [])
            
            if not races:
                continue
            
            for race in races[:10]:
                event_id = race.get("id")
                race_number = race.get("race_number", 0)
                start_time = race.get("start_time", "")
                status = race.get("status", "")
                
                # Skip finished races during active trading
                # For testing at midnight, we allow Final races
                # if status == "Final":
                #     continue
                
                # Get full event details
                event_data = get_event_odds(event_id)
                
                if not event_data:
                    continue
                
                # Extract runners
                data = event_data.get("data", {})
                runners_data = data.get("runners", [])
                
                if not runners_data:
                    continue
                
                print(f"    R{race_number}: {len(runners_data)} runners", flush=True)
                
                for runner in runners_data:
                    name = runner.get("name", "Unknown")
                    runner_number = runner.get("runner_number", 0)
                    odds = runner.get("odds", {})
                    
                    fixed_win = odds.get("fixed_win", 0)
                    fixed_place = odds.get("fixed_place", 0)
                    
                    # Skip scratched or no odds
                    if runner.get("is_scratched") or not fixed_win:
                        continue
                    
                    # Get price fluctuations
                    flucs_data = runner.get("flucs_with_timestamp", {})
                    flucs = flucs_data.get("last_six", [])
                    
                    all_runners.append({
                        "runner_name": name,
                        "runner_number": runner_number,
                        "meeting_name": meeting_name,
                        "race_number": race_number,
                        "event_id": event_id,
                        "fixed_win": float(fixed_win),
                        "fixed_place": float(fixed_place),
                        "start_time": start_time,
                        "country": country,
                        "status": status,
                        "flucs": flucs
                    })
                
                # Rate limiting
                time.sleep(0.15)
    
    print(f"\n[Total] {len(all_runners)} runners with odds", flush=True)
    return all_runners


def test_fetch(au_only: bool = False):
    """Test the fetcher."""
    print("="*60)
    print("LADBROKES AU - PRICE FETCH TEST")
    print("="*60)
    print(f"Email: {HEADERS['From']}")
    print()
    
    runners = fetch_all_prices(["H", "G"], au_only=au_only)
    
    if runners:
        print("\n" + "="*60)
        print("SAMPLE PRICES")
        print("="*60)
        
        for r in runners[:15]:
            country_tag = f"({r['country']})" if r['country'] != "AU" else ""
            flucs_str = ""
            if r['flucs']:
                changes = [f"{f['fluc']:.1f}" for f in r['flucs'][-3:]]
                flucs_str = f" | Flucs: {' → '.join(changes)}"
            
            print(f"  {r['meeting_name']:15s} R{r['race_number']} | #{r['runner_number']:2d} {r['runner_name'][:20]:20s} | {r['fixed_win']:6.2f}{flucs_str}")
        
        au_count = sum(1 for r in runners if r['country'] == 'AU')
        print(f"\n[OK] {len(runners)} total runners ({au_count} AU)")
        return True
    else:
        print("\n[FAIL] No runners found")
        if au_only:
            print("Note: It's currently midnight - AU markets start 10am")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--all-countries', action='store_true', help='Fetch all countries, not just AU')
    args = parser.parse_args()
    
    test_fetch(au_only=not args.all_countries)
