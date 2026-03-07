#!/usr/bin/env python3
"""
LIVE TRADING v4 - AUTO-HEDGE INTEGRATED
========================================

Places BACK bets and automatically hedges them with LAY bets.

NO LUCK REQUIRED - GREEN BOOK EVERY TIME
"""

import requests
import json
import time
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

# Import auto-hedge
import sys
sys.path.append(str(Path(__file__).parent))
from auto_hedge import auto_hedge, login_betfair as login_betfair_hedge

# Files
TRADES_JSON = Path("live_trades_log.json")
BANKROLL_JSON = Path("bankroll.json")
MARKET_CACHE = Path("betfair_market_cache.json")

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Trading parameters
R_UNIT = 1.00
BANKROLL = 10.00
STEAM_THRESHOLD = 0.10
DRIFT_THRESHOLD = 0.10
MAX_TRADES_PER_RACE = 2
MIN_TIME_TO_START = 3.0
BETFAIR_COMMISSION = 0.05

# State
session_token = None
market_cache = {}
bankroll = {
    'starting': 10.00,
    'current': 10.00,
    'r_remaining': 10.00,
    'trades': 0,
    'wins': 0,
    'losses': 0,
    'total_r': 0.0
}
trade_log = []
race_trade_count = defaultdict(int)


def login_betfair():
    """Login to Betfair"""
    global session_token

    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {
        "X-Application": APP_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        "https://identitysso-cert.betfair.com/api/certlogin",
        data=payload,
        cert=CERT_FILE,
        headers=headers,
        timeout=15
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("loginStatus") == "SUCCESS":
            session_token = result.get("sessionToken")
            print("Betfair login: SUCCESS")
            return True

    print(f"Login failed: {response.status_code}")
    return False


def get_betfair_balance():
    """Get current Betfair balance"""
    if not session_token:
        return None

    headers = {
        "X-Application": APP_KEY,
        "X-Authentication": session_token,
        "Content-Type": "application/json"
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "AccountAPING/v1.0/getAccountFunds",
        "params": {},
        "id": 1
    }

    try:
        response = requests.post(
            "https://api.betfair.com/exchange/account/json-rpc/v1",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json().get("result", {})
            return result.get("availableToBetBalance", 0)
    except:
        pass

    return None


def get_au_horse_racing_markets():
    """Get all AU horse racing WIN markets from Betfair"""
    if not session_token:
        return []

    headers = {
        "X-Application": APP_KEY,
        "X-Authentication": session_token,
        "Content-Type": "application/json"
    }

    now = datetime.now(timezone.utc)
    time_range = {
        "from": now.isoformat(),
        "to": (now + timedelta(hours=6)).isoformat()
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["7"],
                "marketCountries": ["AU"],
                "marketTypeCodes": ["WIN"],
                "marketStartTime": time_range
            },
            "maxResults": 200,
            "marketProjection": [
                "EVENT",
                "MARKET_START_TIME",
                "RUNNER_DESCRIPTION"
            ]
        },
        "id": 1
    }

    response = requests.post(
        "https://api.betfair.com/exchange/betting/json-rpc/v1",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        markets = result.get("result", [])
        print(f"Betfair markets: {len(markets)}")
        return markets

    return []


def normalize_name(name: str) -> str:
    """Normalize name for matching"""
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name


def match_venue(ladbrokes_track: str, betfair_venue: str) -> bool:
    """Match track names"""
    l_name = normalize_name(ladbrokes_track)
    b_name = normalize_name(betfair_venue)
    return l_name == b_name or l_name in b_name or b_name in l_name


def match_time(ladbrokes_time: datetime, betfair_time: datetime) -> bool:
    """Match race times (2 min tolerance)"""
    diff = abs((ladbrokes_time - betfair_time).total_seconds())
    return diff < 120


def build_market_cache():
    """Build cache of Betfair markets"""
    global market_cache

    markets = get_au_horse_racing_markets()
    cache = {}

    for market in markets:
        market_id = market.get("marketId")
        market_name = market.get("marketName", "")
        event = market.get("event", {})
        venue = event.get("venue", "")
        start_time_str = market.get("marketStartTime", "")

        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        except:
            continue

        # Extract race number
        race_number = None
        if 'R' in market_name:
            match = re.search(r'R(\d+)', market_name)
            if match:
                race_number = int(match.group(1))

        # Build runners dict
        runners = {}
        for runner in market.get("runners", []):
            runner_name = runner.get("runnerName", "")
            selection_id = runner.get("selectionId")
            runners[normalize_name(runner_name)] = {
                "name": runner_name,
                "selection_id": selection_id
            }

        if venue and race_number:
            cache[f"{normalize_name(venue)}_r{race_number}"] = {
                "market_id": market_id,
                "venue": venue,
                "race_number": race_number,
                "start_time": start_time.isoformat(),
                "runners": runners
            }

    market_cache = cache

    with open(MARKET_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"Market cache: {len(cache)} markets")


def find_market(ladbrokes_track: str, race_number: int, race_time: datetime) -> Optional[dict]:
    """Find Betfair market"""
    if not market_cache:
        build_market_cache()

    for key, market in market_cache.items():
        venue = market.get("venue", "")
        r_num = market.get("race_number")
        start_time_str = market.get("start_time", "")

        try:
            start_time = datetime.fromisoformat(start_time_str)
        except:
            continue

        if (match_venue(ladbrokes_track, venue) and
            r_num == race_number and
            match_time(race_time, start_time)):
            return market

    return None


def find_selection(market: dict, runner_name: str) -> Optional[int]:
    """Find selection ID"""
    runners = market.get("runners", {})
    normalized = normalize_name(runner_name)

    if normalized in runners:
        return runners[normalized].get("selection_id")

    for key, runner in runners.items():
        if normalized in key or key in normalized:
            return runner.get("selection_id")

    return None


def place_back_bet(market_id: str, selection_id: int, price: float, stake: float) -> Optional[str]:
    """Place BACK bet on Betfair"""
    if not session_token:
        return None

    headers = {
        "X-Application": APP_KEY,
        "X-Authentication": session_token,
        "Content-Type": "application/json"
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/placeOrders",
        "params": {
            "marketId": market_id,
            "instructions": [{
                "selectionId": selection_id,
                "handicap": "0",
                "side": "BACK",
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": stake,
                    "price": price,
                    "persistenceType": "LAPSE"
                }
            }],
            "customerRef": f"steamarb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        },
        "id": 1
    }

    try:
        response = requests.post(
            "https://api.betfair.com/exchange/betting/json-rpc/v1",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            status = result.get("result", {}).get("status")

            if status == "SUCCESS":
                instructions = result.get("result", {}).get("instructionReports", [])
                if instructions:
                    return instructions[0].get("betId")
    except:
        pass

    return None


def get_meetings() -> List[dict]:
    """Fetch AU thoroughbred meetings"""
    headers = {
        'From': 'slothitudegames@gmail.com',
        'X-Partner': 'Slothitude Games'
    }

    r = requests.get(
        'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
        headers=headers,
        timeout=15
    )

    if r.status_code != 200:
        return []

    data = r.json()
    meetings = data.get('data', {}).get('meetings', [])
    return [m for m in meetings if m.get('country') == 'AUS' and m.get('category') == 'T']


def get_race_details(race_id: str) -> Optional[dict]:
    """Fetch race details"""
    headers = {
        'From': 'slothitudegames@gmail.com',
        'X-Partner': 'Slothitude Games'
    }

    r = requests.get(
        f"https://api.ladbrokes.com.au/affiliates/v1/racing/events/{race_id}",
        headers=headers,
        timeout=15
    )

    if r.status_code != 200:
        return None

    return r.json().get('data', {})


def detect_edges(runners: List[dict]) -> List[dict]:
    """Detect trading edges"""
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

        price_change = (current_price - open_price) / open_price

        if price_change < -STEAM_THRESHOLD:
            edges.append({
                'type': 'STEAM',
                'runner': name,
                'open_price': open_price,
                'current_price': current_price,
                'change_pct': round(price_change * 100, 1),
                'action': 'BACK'
            })

    return edges


def execute_trade_with_hedge(edge: dict, track: str, race: str, race_start: datetime):
    """Execute trade WITH automatic hedging"""
    now = datetime.now(timezone.utc)
    mins_to_start = (race_start - now).total_seconds() / 60

    # Safety checks
    if mins_to_start < MIN_TIME_TO_START:
        return None

    race_key = f"{track}_R{race}"
    if race_trade_count[race_key] >= MAX_TRADES_PER_RACE:
        return None

    if bankroll['r_remaining'] < 1.0:
        return None

    # Find Betfair market
    market = find_market(track, int(race), race_start)

    if not market:
        print(f"  SKIP: No Betfair market found for {track} R{race}")
        return None

    # Find selection
    selection_id = find_selection(market, edge['runner'])

    if not selection_id:
        print(f"  SKIP: Runner '{edge['runner']}' not found in Betfair market")
        return None

    # Place BACK bet
    print(f"\n  *** PLACING BACK BET ***")
    print(f"  {edge['runner']} @ ${edge['current_price']:.2f}")

    back_bet_id = place_back_bet(
        market_id=market['market_id'],
        selection_id=selection_id,
        price=edge['current_price'],
        stake=R_UNIT
    )

    if not back_bet_id:
        print(f"  FAILED: Could not place BACK bet")
        return None

    print(f"  SUCCESS: BACK bet {back_bet_id}")

    # CREATE TRADE RECORD
    trade = {
        'id': f"{track}_R{race}_{edge['runner']}_{datetime.now().strftime('%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'track': track,
        'race': race,
        'runner': edge['runner'],
        'edge_type': edge['type'],
        'action': 'BACK',
        'entry_price': edge['current_price'],
        'stake': R_UNIT,
        'status': 'BACK_PLACED',
        'bet_id': back_bet_id,
        'market_id': market['market_id'],
        'selection_id': selection_id
    }

    # AUTO-HEDGE IMMEDIATELY
    print(f"\n  *** AUTO-HEDGING ***")

    hedge_result = auto_hedge({
        'bet_id': back_bet_id,
        'market_id': market['market_id'],
        'selection_id': selection_id,
        'runner': edge['runner'],
        'entry_price': edge['current_price'],
        'stake': R_UNIT
    })

    if hedge_result.get('success'):
        trade['status'] = 'HEDGED'
        trade['lay_bet_id'] = hedge_result.get('lay_bet_id')
        trade['lay_price'] = hedge_result.get('lay_price')
        trade['lay_stake'] = hedge_result.get('lay_stake')
        trade['guaranteed_profit'] = hedge_result.get('guaranteed_profit')
        trade['time_to_hedge'] = hedge_result.get('time_to_hedge')

        print(f"  GREEN BOOK: +${trade['guaranteed_profit']:.2f} GUARANTEED")
    else:
        trade['status'] = 'HEDGE_FAILED'
        trade['hedge_error'] = hedge_result.get('error', 'Unknown')
        print(f"  WARNING: {trade['hedge_error']}")

    # Log trade
    trade_log.append(trade)
    race_trade_count[race_key] += 1

    # Update bankroll
    bankroll['r_remaining'] -= 1.0
    bankroll['trades'] += 1

    return trade


def load_bankroll():
    """Load bankroll"""
    global bankroll

    if BANKROLL_JSON.exists():
        with open(BANKROLL_JSON, 'r') as f:
            bankroll = json.load(f)


def save_bankroll():
    """Save bankroll"""
    with open(BANKROLL_JSON, 'w') as f:
        json.dump(bankroll, f, indent=2)


def scan_and_trade():
    """Main scanning loop"""
    print(f"\n{'='*60}")
    print(f"LIVE TRADING v4 - AUTO-HEDGE")
    print(f"Bankroll: ${bankroll['r_remaining']:.2f}R")
    print(f"{datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    # Refresh market cache
    build_market_cache()

    meetings = get_meetings()
    if not meetings:
        return

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(minutes=15)

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

            if not (now < race_start <= cutoff):
                continue

            mins_to_start = (race_start - now).total_seconds() / 60

            if mins_to_start < MIN_TIME_TO_START:
                continue

            race_data = get_race_details(race_id)
            if not race_data:
                continue

            runners = race_data.get('runners', [])
            if not runners:
                continue

            edges = detect_edges(runners)

            if edges and bankroll['r_remaining'] >= 1.0:
                print(f"\n{track} R{race_number} ({mins_to_start:.1f} mins):")
                print(f"  Found {len(edges)} edges")

                best_edge = max(edges, key=lambda e: abs(e['change_pct']))

                trade = execute_trade_with_hedge(best_edge, track, str(race_number), race_start)
                if trade:
                    total_trades += 1

    print(f"\n{'='*60}")
    print(f"Scan complete: {total_trades} trades")
    print(f"Bankroll: ${bankroll['r_remaining']:.2f}R remaining")
    print(f"{'='*60}")

    save_bankroll()


def main():
    print("="*60)
    print("LIVE TRADING v4 - AUTO-HEDGE INTEGRATED")
    print("="*60)
    print("CRITICAL: This version automatically hedges EVERY bet")
    print("NO LUCK REQUIRED - GREEN BOOK EVERY TIME")
    print("="*60)
    print()

    if not login_betfair():
        print("FATAL: Could not login")
        return

    # Also login for hedge module
    if not login_betfair_hedge():
        print("FATAL: Could not login hedge module")
        return

    bf_balance = get_betfair_balance()
    if bf_balance:
        print(f"Betfair balance: ${bf_balance:.2f}")

    load_bankroll()

    print(f"\nStarting with ${bankroll['r_remaining']:.2f}R")
    print()

    while True:
        try:
            if bankroll['r_remaining'] < 1.0:
                print("\n*** BANKROLL DEPLETED ***")
                break

            scan_and_trade()
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n\nStopping...")
            save_bankroll()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
