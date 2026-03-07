#!/usr/bin/env python3
"""
Complete System Test
====================

Tests ALL components to make sure everything works.
"""

import requests
import json
import sys
from pathlib import Path

print("="*60)
print("COMPLETE SYSTEM TEST")
print("="*60)
print()

# Test results
tests_passed = 0
tests_failed = 0

def test(name, condition, details=""):
    global tests_passed, tests_failed
    if condition:
        print(f"[PASS] {name}")
        if details:
            print(f"   {details}")
        tests_passed += 1
        return True
    else:
        print(f"[FAIL] {name}")
        if details:
            print(f"   {details}")
        tests_failed += 1
        return False

# Test 1: Files exist
print("TEST 1: Required Files")
print("-" * 60)

required_files = [
    'live_trading_integrated.py',
    'betfair_market_matcher.py',
    'hedge_completion.py',
    'result_tracker.py',
    'bankroll.json',
    'HANDOFF.md'
]

for f in required_files:
    path = Path(f)
    test(f"File exists: {f}", path.exists())

print()

# Test 2: Betfair Login
print("TEST 2: Betfair API")
print("-" * 60)

USERNAME = 'dnfarnot@gmail.com'
PASSWORD = 'Tobiano01'
APP_KEY = 'XmZEwtLsIRkf5lQ3'
CERT_FILE = r'C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem'

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
            test("Betfair login", True, "Logged in successfully")

            # Test get balance
            headers = {
                'X-Application': APP_KEY,
                'X-Authentication': session_token,
                'Content-Type': 'application/json'
            }

            payload = {
                'jsonrpc': '2.0',
                'method': 'AccountAPING/v1.0/getAccountFunds',
                'params': {},
                'id': 1
            }

            response = requests.post(
                'https://api.betfair.com/exchange/account/json-rpc/v1',
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json().get('result', {})
                balance = result.get('availableToBetBalance', 0)
                test("Get balance", True, f"Balance: ${balance:.2f}")
            else:
                test("Get balance", False, f"Error: {response.status_code}")
        else:
            test("Betfair login", False, result.get('loginStatus'))
    else:
        test("Betfair login", False, f"HTTP {response.status_code}")
except Exception as e:
    test("Betfair login", False, str(e))

print()

# Test 3: Ladbrokes API
print("TEST 3: Ladbrokes API")
print("-" * 60)

headers = {
    'From': 'slothitudegames@gmail.com',
    'X-Partner': 'Slothitude Games'
}

try:
    response = requests.get(
        'https://api.ladbrokes.com.au/affiliates/v1/racing/meetings',
        headers=headers,
        timeout=15
    )

    if response.status_code == 200:
        data = response.json()
        meetings = data.get('data', {}).get('meetings', [])
        au_meetings = [m for m in meetings if m.get('country') == 'AUS']

        test("Ladbrokes API", True, f"Found {len(au_meetings)} AU meetings")
    else:
        test("Ladbrokes API", False, f"HTTP {response.status_code}")
except Exception as e:
    test("Ladbrokes API", False, str(e))

print()

# Test 4: Bankroll State
print("TEST 4: System State")
print("-" * 60)

try:
    with open('bankroll.json', 'r') as f:
        bankroll = json.load(f)

    test("Bankroll file", True,
         f"${bankroll.get('current', 0):.2f} ({bankroll.get('r_remaining', 0)}R remaining)")
except Exception as e:
    test("Bankroll file", False, str(e))

print()

# Test 5: Summary
print("="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Passed: {tests_passed}")
print(f"Failed: {tests_failed}")
print(f"Total:  {tests_passed + tests_failed}")
print()

if tests_failed == 0:
    print("[OK] ALL TESTS PASSED - SYSTEM READY")
    sys.exit(0)
else:
    print("[WARN] SOME TESTS FAILED - FIX BEFORE TRADING")
    sys.exit(1)
