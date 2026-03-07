#!/usr/bin/env python3
"""
Result Tracker - Automatic Learning System
===========================================

Checks race results after completion and learns from outcomes.

This is the FEEDBACK LOOP that makes the system improve.
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Files
TRADES_LOG = Path("live_trades_log.json")
RESULTS_LOG = Path("race_results_log.json")
LEARNING_LOG = Path("learning_log.json")

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Ladbrokes headers
HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

session_token = None


def login_betfair():
    """Login to Betfair"""
    global session_token
    
    payload = f'username={USERNAME}&password={PASSWORD}'
    headers = {
        'X-Application': APP_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(
        'https://identitysso-cert.betfair.com/api/certlogin',
        data=payload,
        cert=CERT_FILE,
        headers=headers,
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('loginStatus') == 'SUCCESS':
            session_token = result.get('sessionToken')
            return True
    
    return False


def get_race_result(track: str, race_num: int) -> Optional[Dict]:
    """Get race result from Ladbrokes"""
    r = requests.get(
        'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
        headers=HEADERS,
        timeout=15
    )
    
    if r.status_code != 200:
        return None
    
    data = r.json()
    meetings = data.get('data', {}).get('meetings', [])
    
    for m in meetings:
        if m.get('name') == track:
            for race in m.get('races', []):
                if race.get('race_number') == race_num:
                    race_id = race.get('id')
                    
                    # Get race details
                    r2 = requests.get(
                        f'https://api.ladbrokes.com.au/affiliates/v1/racing/events/{race_id}',
                        headers=HEADERS,
                        timeout=15
                    )
                    
                    if r2.status_code == 200:
                        rd = r2.json().get('data', {})
                        runners = rd.get('runners', [])
                        
                        # Find winner and placings
                        results = []
                        for runner in runners:
                            result = runner.get('result')
                            if result:
                                results.append({
                                    'position': result,
                                    'name': runner.get('name'),
                                    'number': runner.get('number'),
                                    'price': runner.get('odds', {}).get('fixed_win', 0)
                                })
                        
                        if results:
                            return {
                                'track': track,
                                'race': race_num,
                                'results': sorted(results, key=lambda x: x['position'])
                            }
    
    return None


def check_bet_result(bet: Dict, race_result: Dict) -> Dict:
    """Check if bet won or lost"""
    runner_name = bet.get('runner')
    action = bet.get('action')
    entry_price = bet.get('entry_price')
    stake = bet.get('stake', 1.0)
    
    # Find our runner in results
    for result in race_result.get('results', []):
        if result['name'] == runner_name:
            position = result['position']
            
            if position == 1:
                # Winner
                if action == 'BACK':
                    profit = stake * (entry_price - 1)
                    r_mult = profit / stake
                    return {
                        'bet_id': bet.get('bet_id'),
                        'runner': runner_name,
                        'result': 'WIN',
                        'position': position,
                        'profit': profit,
                        'r_multiple': r_mult,
                        'notes': f"Backed at ${entry_price:.2f}, won at {result['price']:.2f}"
                    }
                else:  # LAY
                    loss = stake * (entry_price - 1)
                    r_mult = -loss / stake
                    return {
                        'bet_id': bet.get('bet_id'),
                        'runner': runner_name,
                        'result': 'LOSS',
                        'position': position,
                        'profit': -loss,
                        'r_multiple': r_mult,
                        'notes': f"Laid at ${entry_price:.2f}, won"
                    }
            else:
                # Lost
                if action == 'BACK':
                    return {
                        'bet_id': bet.get('bet_id'),
                        'runner': runner_name,
                        'result': 'LOSS',
                        'position': position,
                        'profit': -stake,
                        'r_multiple': -1.0,
                        'notes': f"Backed at ${entry_price:.2f}, finished {position}"
                    }
                else:  # LAY
                    return {
                        'bet_id': bet.get('bet_id'),
                        'runner': runner_name,
                        'result': 'WIN',
                        'position': position,
                        'profit': stake,
                        'r_multiple': 1.0,
                        'notes': f"Laid at ${entry_price:.2f}, finished {position}"
                    }
    
    # Runner not found in results
    return {
        'bet_id': bet.get('bet_id'),
        'runner': runner_name,
        'result': 'UNKNOWN',
        'position': None,
        'profit': 0,
        'r_multiple': 0,
        'notes': 'Runner not found in results'
    }


def learn_from_result(bet_result: Dict):
    """Extract lessons from bet result"""
    lessons = []
    
    edge_type = bet_result.get('edge_type')
    result = bet_result.get('result')
    r_mult = bet_result.get('r_multiple')
    notes = bet_result.get('notes')
    
    # Lesson 1: Edge type performance
    if result == 'WIN':
        lessons.append(f"{edge_type} edge +{r_mult:.3f}R: {notes}")
    else:
        lessons.append(f"{edge_type} edge {r_mult:.3f}R: {notes}")
    
    # Lesson 2: Price analysis
    entry_price = bet_result.get('entry_price')
    if result == 'WIN' and entry_price < 5.0:
        lessons.append(f"Short prices ({entry_price:.2f}) working well")
    elif result == 'LOSS' and entry_price > 10.0:
        lessons.append(f"Long prices ({entry_price:.2f}) risky")
    
    return lessons


def track_results():
    """Main tracking loop"""
    print("="*60)
    print("RESULT TRACKER - LEARNING SYSTEM")
    print("="*60)
    
    # Load trades
    if not TRADES_LOG.exists():
        print("No trades to track")
        return
    
    with open(TRADES_LOG, 'r') as f:
        trades = json.load(f)
    
    # Filter for completed races
    now = datetime.now(timezone.utc)
    completed = []
    
    for trade in trades:
        track = trade.get('track')
        race = trade.get('race')
        bet_id = trade.get('bet_id')
        
        # Check if race has completed
        result = get_race_result(track, int(race))
        
        if result:
            print(f"\n{track} R{race}:")
            print(f"  Winner: {result['results'][0]['name'] if result['results'] else 'N/A'}")
            
            # Check our bet
            bet_result = check_bet_result(trade, result)
            bet_result['edge_type'] = trade.get('edge_type')
            bet_result['entry_price'] = trade.get('entry_price')
            
            print(f"  Our bet: {bet_result['runner']}")
            print(f"  Result: {bet_result['result']}")
            print(f"  R: {bet_result['r_multiple']:+.3f}R")
            print(f"  Notes: {bet_result['notes']}")
            
            completed.append(bet_result)
            
            # Learn from it
            lessons = learn_from_result(bet_result)
            for lesson in lessons:
                print(f"  Lesson: {lesson}")
    
    # Calculate total R
    if completed:
        total_r = sum(b['r_multiple'] for b in completed)
        print(f"\n{'='*60}")
        print(f"TOTAL R: {total_r:+.3f}R from {len(completed)} bets")
        print(f"{'='*60}")
        
        # Save results
        with open(RESULTS_LOG, 'w') as f:
            json.dump(completed, f, indent=2)
    
    print("\nResult tracking complete")


if __name__ == "__main__":
    track_results()
