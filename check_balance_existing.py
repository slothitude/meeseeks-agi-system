#!/usr/bin/env python3
"""Check Betfair balance using existing session token"""
import requests
import json

# Load config
with open(r"C:\Users\aaron\Desktop\008\betfair_config.json") as f:
    config = json.load(f)

APP_KEY = config.get("app_key")
SESSION_TOKEN = config.get("session_token")

print("="*60)
print("BETFAIR BALANCE CHECK")
print("="*60)
print(f"App Key: {APP_KEY}")
print(f"Session Token: {SESSION_TOKEN[:30]}...")
print(f"Extracted: {config.get('extracted_at')}")
print()

# Check balance
BALANCE_URL = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"

headers = {
    'X-Application': APP_KEY,
    'X-Authentication': SESSION_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

print("Checking balance...")

try:
    response = requests.get(BALANCE_URL, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "="*60)
        print("ACCOUNT BALANCE")
        print("="*60)
        print(f"Available: ${data.get('availableToBetBalance', 'N/A')}")
        print(f"Exposure: ${data.get('exposure', 'N/A')}")
        print(f"Exposure Limit: ${data.get('exposureLimit', 'N/A')}")
        print(f"Discount Rate: {data.get('discountRate', 'N/A')}")
        print(f"Points Balance: {data.get('pointsBalance', 'N/A')}")
        print("="*60)
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
