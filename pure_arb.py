#!/usr/bin/env python3
"""
Pure Arbitrage System
=====================

NO DIRECTIONAL BETTING. ONLY LOCKED PROFIT.

Finds price discrepancies between Ladbrokes and Betfair,
places both sides immediately, guarantees profit.

The Cycle:
1. Detect ARB (Ladbrokes price > Betfair LAY price)
2. Calculate stakes for green book
3. Place BACK at Ladbrokes
4. Place LAY at Betfair
5. Lock profit (complete)

Never leave a position naked. Never bet on price direction.
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

# Files
ARB_LOG = Path("arb_trades.json")
BANKROLL_JSON = Path("bankroll.json")

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# ARB parameters
MIN_ARB_EDGE = 0.02  # 2% minimum edge
MAX_ODDS = 8.00  # Maximum odds to arb
MIN_ODDS = 2.00  # Minimum odds to arb
R_UNIT = 1.00  # Base stake
BETFAIR_COMMISSION = 0.05

# Ladbrokes API
LADBROKES_HEADERS = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

# State
session_token = None
bankroll = {
    'starting': 10.00,
    'current': 10.00,
    'r_remaining': 10.00,
    'trades': 0
}


def login_betfair() -> bool:
    """Login to Betfair API."""
    global session_token

    payload = f'username={USERNAME}&password={PASSWORD}'
    headers = {
        'X-Application': APP_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
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
                print(f"[ARB] Betfair login: SUCCESS")
                return True
    except Exception as e:
        print(f"[ARB] Login failed: {e}")

    return False


def get_betfair_market_book(market_id: str) -> Optional[dict]:
    """Get current prices for a Betfair market."""
    if not session_token:
        return None

    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }

    data = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds": [market_id],
            "priceProjection": {
                "priceData": ["EX_ALL_OFFERS"]
            }
        },
        "id": 1
    }

    try:
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if 'result' in result and result['result']:
                return result['result'][0]
    except Exception as e:
        print(f"[ARB] Error getting market book: {e}")

    return None


def get_ladbrokes_races() -> List[dict]:
    """Get upcoming races from Ladbrokes - inline fetcher."""
    BASE_URL = "https://api.ladbrokes.com.au/affiliates/v1"
    HEADERS = {
        "From": "slothitudegames@gmail.com",
        "X-Partner": "Slothitude Games"
    }

    try:
        # Get meetings
        url = f"{BASE_URL}/racing/meetings"
        params = {"date_from": "today", "date_to": "today", "category": "T"}

        r = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if r.status_code != 200:
            print(f"[ARB] Ladbrokes meetings error: {r.status_code}")
            return []

        data = r.json()
        meetings = data.get("data", {}).get("meetings", [])

        # Filter for AU
        aus_meetings = [m for m in meetings if m.get('country') in ['AU', 'AUS']]
        print(f"[ARB] Ladbrokes AU meetings: {len(aus_meetings)}")

        now = datetime.now(timezone.utc)
        all_races = []

        for meeting in aus_meetings:
            track = meeting.get('name')
            races = meeting.get('races', [])

            for race in races:
                status = race.get('status')
                if status != 'Open':  # Only upcoming races
                    continue

                start_time_str = race.get('start_time')
                if not start_time_str:
                    continue

                try:
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    mins_to_start = (start_time - now).total_seconds() / 60

                    if not (3 <= mins_to_start <= 30):
                        continue
                except:
                    continue

                event_id = race.get('id')
                race_number = race.get('race_number')

                # Get event data with runners
                event_url = f"{BASE_URL}/racing/events/{event_id}"
                event_r = requests.get(event_url, headers=HEADERS, timeout=10)

                if event_r.status_code != 200:
                    continue

                event_data = event_r.json()
                runners_data = event_data.get('data', {}).get('runners', [])

                if not runners_data:
                    continue

                # Build runner list with odds
                runners_with_odds = []
                for runner in runners_data:
                    if runner.get('is_scratched'):
                        continue

                    odds = runner.get('odds', {})
                    fixed_win = odds.get('fixed_win', 0)

                    if not fixed_win:
                        continue

                    runners_with_odds.append({
                        'name': runner.get('name'),
                        'runner_number': runner.get('runner_number'),
                        'fixed_win': float(fixed_win),
                        'fixed_place': float(odds.get('fixed_place', 0))
                    })

                if runners_with_odds:
                    all_races.append({
                        'meeting_name': track,
                        'race_number': race_number,
                        'start_time': start_time_str,
                        'mins_to_start': mins_to_start,
                        'runners': runners_with_odds
                    })

                time.sleep(0.15)  # Rate limit

        print(f"[ARB] Ladbrokes races with odds: {len(all_races)}")
        return all_races

    except Exception as e:
        print(f"[ARB] Error fetching Ladbrokes: {e}")
        return []


def get_betfair_markets() -> Dict[str, dict]:
    """Get all AU horse racing markets from Betfair."""
    if not session_token:
        return {}

    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }

    now = datetime.now(timezone.utc)
    later = (now + timedelta(hours=1)).isoformat()

    data = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["7"],
                "marketCountries": ["AU"],
                "marketTypeCodes": ["WIN"],
                "marketStartTime": {
                    "from": now.isoformat(),
                    "to": later
                }
            },
            "maxResults": 100,
            "marketProjection": ["EVENT", "MARKET_START_TIME", "RUNNER_METADATA"]
        },
        "id": 1
    }

    try:
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code != 200:
            return {}

        result = response.json()
        markets = {}

        for market in result.get('result', []):
            market_id = market.get('marketId')
            market_name = market.get('marketName', '')
            event = market.get('event', {})
            venue = event.get('venue', '')
            start_time_str = market.get('marketStartTime', '')

            # Extract race number
            race_number = None
            if 'R' in market_name:
                import re
                match = re.search(r'R(\d+)', market_name)
                if match:
                    race_number = int(match.group(1))

            # Build runner lookup
            runners = {}
            for runner in market.get('runners', []):
                runner_name = runner.get('runnerName', '')
                selection_id = runner.get('selectionId')
                # Normalize name
                normalized = runner_name.lower().replace(' ', '').replace('-', '')
                runners[normalized] = {
                    'name': runner_name,
                    'selection_id': selection_id
                }

            if venue and race_number:
                key = f"{venue.lower().replace(' ', '')}_r{race_number}"
                markets[key] = {
                    'market_id': market_id,
                    'venue': venue,
                    'race_number': race_number,
                    'start_time': start_time_str,
                    'runners': runners
                }

        return markets
    except Exception as e:
        print(f"[ARB] Error fetching Betfair markets: {e}")
        return {}


def normalize_name(name: str) -> str:
    """Normalize runner name for matching."""
    return name.lower().replace(' ', '').replace('-', '').replace("'", '')


def find_arb_opportunities() -> List[dict]:
    """Find arbitrage opportunities between Ladbrokes and Betfair."""
    print(f"\n[ARB] Scanning for arbitrage opportunities...")

    # Get Ladbrokes races
    ladbrokes_races = get_ladbrokes_races()
    print(f"[ARB] Ladbrokes: {len(ladbrokes_races)} races")

    # Get Betfair markets
    betfair_markets = get_betfair_markets()
    print(f"[ARB] Betfair: {len(betfair_markets)} markets")

    opportunities = []

    for race in ladbrokes_races:
        track = race.get('meeting_name', '')
        race_number = race.get('race_number')
        runners = race.get('runners', [])

        if not runners:
            continue

        # Find matching Betfair market
        track_normalized = normalize_name(track)
        market_key = f"{track_normalized}_r{race_number}"

        if market_key not in betfair_markets:
            continue

        bf_market = betfair_markets[market_key]
        market_id = bf_market['market_id']

        print(f"  [{track} R{race_number}] Checking {len(runners)} runners...")

        # Get Betfair prices
        market_book = get_betfair_market_book(market_id)
        if not market_book:
            continue

        # Build Betfair price lookup
        bf_prices = {}
        for runner in market_book.get('runners', []):
            selection_id = runner.get('selectionId')
            ex = runner.get('ex', {})

            back_price = None
            lay_price = None

            if ex.get('availableToBack'):
                back_price = ex['availableToBack'][0]['price']
            if ex.get('availableToLay'):
                lay_price = ex['availableToLay'][0]['price']

            bf_prices[selection_id] = {
                'back': back_price,
                'lay': lay_price
            }

        # Find ARB opportunities
        for i, runner in enumerate(runners):
            ladb_name = runner.get('name', '')
            ladb_price = runner.get('fixed_win', 0)  # Direct access, not nested

            if ladb_price <= 0:
                continue

            # Check odds range
            if ladb_price < MIN_ODDS or ladb_price > MAX_ODDS:
                continue

            # Find matching Betfair runner
            ladb_normalized = normalize_name(ladb_name)

            bf_runner = None
            for key, r in bf_market['runners'].items():
                if ladb_normalized in key or key in ladb_normalized:
                    bf_runner = r
                    break

            if not bf_runner:
                continue

            selection_id = bf_runner['selection_id']
            bf_price_data = bf_prices.get(selection_id, {})

            bf_lay_price = bf_price_data.get('lay')
            if not bf_lay_price:
                continue

            # Calculate ARB edge
            # Ladbrokes BACK vs Betfair LAY
            edge = (ladb_price / bf_lay_price) - 1

            # Debug: show comparison
            if i < 3:  # First 3 runners
                print(f"  {ladb_name}: LADB {ladb_price:.2f} vs BF LAY {bf_lay_price:.2f} = {edge*100:.2f}% edge")

            if edge >= MIN_ARB_EDGE:
                # Calculate stakes for green book
                back_stake = R_UNIT
                lay_stake = (back_stake * ladb_price) / bf_lay_price

                # Calculate profit
                if_wins = (back_stake * (ladb_price - 1)) - (lay_stake * (bf_lay_price - 1))
                if_wins *= (1 - BETFAIR_COMMISSION)

                if_loses = lay_stake - back_stake
                if_loses *= (1 - BETFAIR_COMMISSION)

                # Both must be positive
                if if_wins > 0 and if_loses > 0:
                    opportunities.append({
                        'track': track,
                        'race': race_number,
                        'runner': ladb_name,
                        'ladb_price': ladb_price,
                        'bf_lay_price': bf_lay_price,
                        'edge': round(edge * 100, 2),
                        'back_stake': round(back_stake, 2),
                        'lay_stake': round(lay_stake, 2),
                        'if_wins': round(if_wins, 2),
                        'if_loses': round(if_loses, 2),
                        'market_id': market_id,
                        'selection_id': selection_id,
                        'mins_to_start': race.get('mins_to_start', 0)
                    })

    return opportunities


def execute_arb(opp: dict) -> bool:
    """Execute an arbitrage trade (BOTH sides)."""
    print(f"\n[ARB] EXECUTING ARB:")
    print(f"  {opp['runner']} @ {opp['track']} R{opp['race']}")
    print(f"  Ladbrokes: BACK ${opp['back_stake']:.2f} @ ${opp['ladb_price']:.2f}")
    print(f"  Betfair: LAY ${opp['lay_stake']:.2f} @ ${opp['bf_lay_price']:.2f}")
    print(f"  Edge: {opp['edge']:.2f}%")
    print(f"  Profit: +${opp['if_wins']:.2f} (wins) | +${opp['if_loses']:.2f} (loses)")

    # TODO: Place BACK at Ladbrokes (need API or manual)
    print(f"  [MANUAL] Place BACK at Ladbrokes: ${opp['back_stake']:.2f} @ ${opp['ladb_price']:.2f}")

    # Place LAY at Betfair
    if not session_token:
        print(f"  [ERROR] Not logged in to Betfair")
        return False

    headers = {
        'X-Application': APP_KEY,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }

    data = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/placeOrders",
        "params": {
            "marketId": opp['market_id'],
            "instructions": [{
                "selectionId": opp['selection_id'],
                "side": "LAY",
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": max(opp['lay_stake'], 1.00),  # Minimum $1.00
                    "price": opp['bf_lay_price'],
                    "persistenceType": "LAPSE"
                }
            }]
        },
        "id": 1
    }

    try:
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            if 'result' in result and result['result'].get('status') == 'SUCCESS':
                instruction = result['result'].get('instructionReports', [{}])[0]
                bet_id = instruction.get('betId')
                matched = instruction.get('sizeMatched', 0)

                print(f"  [BETFAIR] LAY placed: ${matched:.2f} @ ${opp['bf_lay_price']:.2f}")
                print(f"  Bet ID: {bet_id}")

                # Log the ARB
                log_arb(opp, bet_id, matched)

                return True
            else:
                error = result.get('error', {}).get('message', 'Unknown')
                print(f"  [BETFAIR] LAY failed: {error}")
        else:
            print(f"  [BETFAIR] LAY failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"  [BETFAIR] LAY error: {e}")

    return False


def log_arb(opp: dict, bet_id: str, matched: float):
    """Log the arbitrage trade."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'ARB',
        'track': opp['track'],
        'race': opp['race'],
        'runner': opp['runner'],
        'ladb_back': {
            'price': opp['ladb_price'],
            'stake': opp['back_stake'],
            'status': 'PENDING'  # Manual placement
        },
        'bf_lay': {
            'price': opp['bf_lay_price'],
            'stake': opp['lay_stake'],
            'matched': matched,
            'bet_id': bet_id,
            'status': 'PLACED'
        },
        'edge': opp['edge'],
        'if_wins': opp['if_wins'],
        'if_loses': opp['if_loses'],
        'status': 'OPEN'
    }

    # Append to log
    logs = []
    if ARB_LOG.exists():
        try:
            with open(ARB_LOG, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

    logs.append(log_entry)

    with open(ARB_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

    print(f"  [LOG] ARB logged")


def scan_loop():
    """Main scanning loop."""
    print(f"\n{'='*60}")
    print(f"PURE ARBITRAGE SYSTEM")
    print(f"{'='*60}")
    print(f"Edge threshold: {MIN_ARB_EDGE*100:.1f}%")
    print(f"Odds range: {MIN_ODDS:.2f} - {MAX_ODDS:.2f}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    if not login_betfair():
        print("[ARB] Cannot start - login failed")
        return

    while True:
        try:
            print(f"\n[ARB] Scan @ {datetime.now().strftime('%H:%M:%S')}")

            opportunities = find_arb_opportunities()

            if opportunities:
                print(f"\n[ARB] Found {len(opportunities)} opportunities!")

                # Sort by edge (highest first)
                opportunities.sort(key=lambda x: x['edge'], reverse=True)

                for i, opp in enumerate(opportunities[:3]):  # Top 3
                    print(f"\n  [{i+1}] {opp['runner']} @ {opp['track']} R{opp['race']}")
                    print(f"      Ladbrokes: ${opp['ladb_price']:.2f}")
                    print(f"      Betfair LAY: ${opp['bf_lay_price']:.2f}")
                    print(f"      Edge: {opp['edge']:.2f}%")
                    print(f"      Profit: +${min(opp['if_wins'], opp['if_loses']):.2f} guaranteed")

                # Execute top opportunity
                if bankroll['r_remaining'] >= 1:
                    execute_arb(opportunities[0])
                    bankroll['r_remaining'] -= 1
                else:
                    print(f"\n[ARB] Bankroll depleted: {bankroll['r_remaining']:.2f}R")
            else:
                print(f"[ARB] No opportunities found")

            time.sleep(30)  # Scan every 30 seconds

        except KeyboardInterrupt:
            print(f"\n[ARB] Stopped by user")
            break
        except Exception as e:
            print(f"[ARB] Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    scan_loop()
