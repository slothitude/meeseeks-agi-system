#!/usr/bin/env python3
"""Quick balance check using interactive login"""
import requests
import json

# Credentials from 008 files
USERNAME = "aaronwashington8@gmail.com"
PASSWORD = "Melbourne22!"
APP_KEY = "XmZEwtLsIRkf5lQ3"

# Interactive login endpoint
LOGIN_URL = "https://identitysso.betfair.com/api/login"
BALANCE_URL = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"

headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

payload = f"username={USERNAME}&password={PASSWORD}"

print("Attempting interactive login...")

try:
    response = requests.post(LOGIN_URL, data=payload, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        status = data.get('status', 'Unknown')
        print(f"Login status: {status}")
        
        if status == 'SUCCESS':
            token = data.get('token')
            print(f"Token: {token[:30]}..." if token else "No token")
            
            # Check balance
            bal_headers = {
                'X-Application': APP_KEY,
                'X-Authentication': token,
                'Accept': 'application/json'
            }
            
            bal_response = requests.get(BALANCE_URL, headers=bal_headers, timeout=10)
            print(f"\nBalance check status: {bal_response.status_code}")
            
            if bal_response.status_code == 200:
                balance_data = bal_response.json()
                print("\n" + "="*50)
                print("ACCOUNT BALANCE")
                print("="*50)
                print(f"Available: ${balance_data.get('availableToBetBalance', 'N/A')}")
                print(f"Exposure: ${balance_data.get('exposure', 'N/A')}")
                print(f"Exposure Limit: ${balance_data.get('exposureLimit', 'N/A')}")
                print("="*50)
                
                # Save to config
                config = {
                    "app_key": APP_KEY,
                    "session_token": token,
                    "extracted_at": "2026-03-06 22:56",
                    "balance": balance_data.get('availableToBetBalance', 0)
                }
                with open("betfair_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                print("\nConfig saved to betfair_config.json")
            else:
                print(f"Balance error: {bal_response.text}")
        else:
            error = data.get('error', 'Unknown error')
            print(f"Login failed: {error}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
