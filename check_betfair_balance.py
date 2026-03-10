#!/usr/bin/env python3
"""Check actual Betfair account balance"""

import requests
import json
from pathlib import Path

# Betfair credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_PATH = Path("C:/Users/aaron/Desktop/008/betfair_api_combined_20260225_152452.pem")

# Login to Betfair
login_url = "https://identitysso.betfair.com/api/certlogin"
headers = {
    "X-Application": APP_KEY,
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    response = requests.post(
        login_url,
        data=f"username={USERNAME}&password={PASSWORD}",
        headers=headers,
        cert=str(CERT_PATH),
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        session_token = data.get("sessionToken")
        print("Login successful!")
        print(f"Session token: {session_token[:20]}...")

        # Get account balance
        balance_url = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"
        balance_headers = {
            "X-Application": APP_KEY,
            "X-Authentication": session_token,
            "Content-Type": "application/json"
        }

        balance_response = requests.post(
            balance_url,
            headers=balance_headers,
            json={},
            timeout=10
        )

        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            print("\n=== BETFAIR ACCOUNT BALANCE ===")
            print(f"Available: ${balance_data.get('availableToBetBalance', 0):.2f} AUD")
            print(f"Balance: ${balance_data.get('balance', 0):.2f} AUD")
            print(f"Exposure: ${balance_data.get('exposure', 0):.2f} AUD")
            print(f"Commission: ${balance_data.get('commissionBalance', 0):.2f} AUD")
            print("================================")
        else:
            print(f"Balance check failed: {balance_response.status_code}")
            print(balance_response.text[:200])
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text[:200])

except Exception as e:
    print(f"Error: {e}")
