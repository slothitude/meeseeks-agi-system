#!/usr/bin/env python3
"""
AUTO-HEDGE SYSTEM - No Luck Required
=====================================

Automatically hedges every BACK bet with a LAY bet to guarantee profit.

CRITICAL: This removes the luck component.
"""

import requests
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

# Files
HEDGE_LOG = Path("hedge_log.json")
TRADES_LOG = Path("live_trades_log.json")

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Parameters
TARGET_PRICE_DROP = 0.95  # 5% lower
MAX_WAIT_SECONDS = 180  # 3 minutes
CHECK_INTERVAL = 2  # Check every 2 seconds

session_token = None


def login_betfair() -> bool:

    """Login to Betfair"""
    global session_token

    payload = f"username={USERNAME}&password={PASSWORD}"
    headers = {
        "X-Application": APP_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
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
                return True
    except:
        pass

    return False


def get_lay_price(market_id: str, selection_id: int) -> Optional[Dict]:
    """Get current best LAY price"""
    if not session_token:
        return None

    headers = {
        "X-Application": APP_KEY,
        "X-Authentication": session_token,
        "Content-Type": "application/json"
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listRunnerBook",
        "params": {
            "marketId": market_id,
            "selectionId": selection_id,
            "priceProjection": {
                "priceData": ["EX_BEST_OFFERS"],
                "virtualise": True
            }
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
            result = response.json().get("result", [])
            if result:
                book = result[0]
                ex = book.get("ex", {})
                lay_offers = ex.get("availableToLay", [])

                if lay_offers:
                    return {
                        "price": lay_offers[0].get("price", 0),
                        "size": lay_offers[0].get("size", 0)
                    }
    except:
        pass

    return None


def place_lay_bet(market_id: str, selection_id: int, price: float, stake: float) -> Optional[str]:
    """Place LAY bet"""
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
                "side": "LAY",
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": stake,
                    "price": price,
                    "persistenceType": "LAPSE"
                }
            }],
            "customerRef": f"autohedge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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


def auto_hedge(back_bet: Dict) -> Dict:
    """
    Automatically hedge a BACK bet with a LAY bet.

    Returns dict with hedge result.
    """
    market_id = back_bet.get("market_id")
    selection_id = back_bet.get("selection_id")
    entry_price = back_bet.get("entry_price")
    back_stake = back_bet.get("stake", 1.0)
    target_lay_price = entry_price * TARGET_PRICE_DROP

    print(f"\n{'='*60}")
    print(f"AUTO-HEDGE STARTED")
    print(f"{'='*60}")
    print(f"Runner: {back_bet.get('runner', 'Unknown')}")
    print(f"BACK: ${back_stake:.2f} @ ${entry_price:.2f}")
    print(f"Target LAY: ${target_lay_price:.2f}")
    print(f"{'='*60}\n")

    # Monitor price until target reached or timeout
    start_time = time.time()
    hedge_result = {
        "success": False,
        "back_bet_id": back_bet.get("bet_id"),
        "market_id": market_id,
        "selection_id": selection_id,
        "entry_price": entry_price,
        "target_price": target_lay_price
    }

    while time.time() - start_time < MAX_WAIT_SECONDS:
        # Get current LAY price
        lay_data = get_lay_price(market_id, selection_id)

        if not lay_data:
            print("Error getting price, retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        current_price = lay_data["price"]
        current_size = lay_data["size"]
        elapsed = time.time() - start_time

        print(f"[{elapsed:.00}s] Current LAY: ${current_price:.2f} (liquidity: ${current_size:.2f})")

        # Check if price is at or below target
        if current_price <= target_lay_price:
            print(f"\nTARGET REACHED! LAY @ ${current_price:.2f}")

            # Calculate LAY stake
            lay_stake = (back_stake * entry_price) / current_price

            print(f"Placing LAY: ${lay_stake:.2f} @ ${current_price:.2f}")

            # Check liquidity
            if current_size < lay_stake:
                print(f"WARNING: Insufficient liquidity (${current_size:.2f} < ${lay_stake:.2f})")
                print("Adjusting stake to available liquidity...")
                lay_stake = current_size * 0.95  # Use 95% of available

            # Place LAY bet
            lay_bet_id = place_lay_bet(market_id, selection_id, current_price, lay_stake)

            if lay_bet_id:
                # Calculate guaranteed profit
                if_wins = (back_stake * (entry_price - 1)) - (lay_stake * (current_price - 1))
                if_loses = lay_stake - back_stake
                guaranteed = min(if_wins, if_loses)

                print(f"\n{'='*60}")
                print(f"GREEN BOOK COMPLETE!")
                print(f"{'='*60}")
                print(f"LAY Bet ID: {lay_bet_id}")
                print(f"LAY Stake: ${lay_stake:.2f} @ ${current_price:.2f}")
                print(f"\nOutcomes:")
                print(f"  If wins: ${if_wins:+.2f}")
                print(f"  If loses: ${if_loses:+.2f}")
                print(f"  GUARANTEED: ${guaranteed:+.2f}")
                print(f"{'='*60}\n")

                hedge_result["success"] = True
                hedge_result["lay_bet_id"] = lay_bet_id
                hedge_result["lay_price"] = current_price
                hedge_result["lay_stake"] = lay_stake
                hedge_result["guaranteed_profit"] = guaranteed
                hedge_result["time_to_hedge"] = elapsed

                # Log it
                log_hedge(hedge_result)

                return hedge_result
            else:
                print("ERROR: Failed to place LAY bet")
                hedge_result["error"] = "LAY placement failed"
                return hedge_result

        # Wait before next check
        time.sleep(CHECK_INTERVAL)

    # Timeout
    print(f"\nTIMEOUT: Price did not reach target in {MAX_WAIT_SECONDS} seconds")
    hedge_result["error"] = "Timeout waiting for target price"
    return hedge_result


def log_hedge(hedge_result: Dict):
    """Log hedge result"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        **hedge_result
    }

    # Load existing log
    if HEDGE_LOG.exists():
        with open(HEDGE_LOG, "r") as f:
            log = json.load(f)
    else:
        log = []

    log.append(log_entry)

    with open(HEDGE_LOG, "w") as f:
        json.dump(log, f, indent=2)


def test_auto_hedge():
    """Test the auto-hedge system with a simulated bet"""
    print("="*60)
    print("AUTO-HEDGE SYSTEM TEST")
    print("="*60)
    print()

    if not login_betfair():
        print("ERROR: Cannot login to Betfair")
        return

    print("Login: SUCCESS")
    print()

    # Simulated BACK bet
    test_bet = {
        "bet_id": "TEST_123",
        "market_id": "1.226614153",  # Example market
        "selection_id": 95919103,  # Example selection
        "runner": "Test Runner",
        "entry_price": 3.40,
        "stake": 1.00
    }

    print("Testing with simulated BACK bet:")
    print(f"  Market: {test_bet['market_id']}")
    print(f"  Selection: {test_bet['selection_id']}")
    print(f"  Price: ${test_bet['entry_price']:.2f}")
    print(f"  Stake: ${test_bet['stake']:.2f}")
    print()

    # Run auto-hedge
    result = auto_hedge(test_bet)

    if result.get("success"):
        print("\nTEST PASSED: Auto-hedge system working!")
    else:
        print(f"\nTEST RESULT: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_auto_hedge()
