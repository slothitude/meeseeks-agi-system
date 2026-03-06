#!/usr/bin/env python3
"""Betfair balance check with new password"""
import requests
import json

# New credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

print("="*60)
print("BETFAIR LOGIN - NEW PASSWORD")
print("="*60)
print(f"Username: {USERNAME}")
print(f"App Key: {APP_KEY}")
print()

# Login with certificate
payload = f"username={USERNAME}&password={PASSWORD}"
headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

print("Logging in...")

try:
    response = requests.post(
        'https://identitysso-cert.betfair.com/api/certlogin',
        data=payload,
        cert=CERT_FILE,
        headers=headers,
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        status = result.get('loginStatus', 'Unknown')
        print(f"Login: {status}")
        
        if status == 'SUCCESS':
            session_token = result.get('sessionToken')
            print(f"\n[OK] SUCCESS! Token: {session_token[:40]}...")
            
            # Get balance
            headers = {
                'X-Application': APP_KEY,
                'X-Authentication': session_token,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "jsonrpc": "2.0",
                "method": "AccountAPING/v1.0/getAccountFunds",
                "params": {},
                "id": 1
            }
            
            print("\nChecking balance...")
            response = requests.post(
                'https://api.betfair.com/exchange/account/json-rpc/v1',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json().get('result', {})
                
                print("\n" + "="*60)
                print("BETFAIR ACCOUNT BALANCE")
                print("="*60)
                print(f"Available: ${result.get('availableToBetBalance', 0):.2f}")
                print(f"Exposure: ${result.get('exposure', 0):.2f}")
                print(f"Discount Rate: {result.get('discountRate', 0)}")
                print(f"Points: {result.get('pointsBalance', 0)}")
                print("="*60)
                
                # Save config
                config = {
                    "app_key": APP_KEY,
                    "session_token": session_token,
                    "username": USERNAME,
                    "password": PASSWORD,
                    "balance": result.get('availableToBetBalance', 0),
                    "exposure": result.get('exposure', 0),
                    "extracted_at": "2026-03-06 23:11",
                    "cert_file": CERT_FILE
                }
                
                with open(r"C:\Users\aaron\Desktop\008\betfair_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                print("\n[OK] Config saved to 008/betfair_config.json")
                
            else:
                print(f"Balance error: {response.status_code} - {response.text}")
        else:
            print(f"\n[FAIL] Login failed: {status}")
            print(f"Response: {result}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
