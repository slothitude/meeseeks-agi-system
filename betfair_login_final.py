#!/usr/bin/env python3
"""Betfair login - try all combined PEM files from 008"""
import requests
import json
import urllib3
import os

urllib3.disable_warnings()

USERNAME = "aaron Adsit"
PASSWORD = "Lachlan64!"
APP_KEY = "XmZEwtLsIRkf5lQ3"

LOGIN_URL = "https://identitysso-cert.betfair.com/api/certlogin"
BALANCE_URL = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"

# All combined PEM files to try
CERT_FILES = [
    r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem",
    r"C:\Users\aaron\Desktop\008\betfair_combined.pem",
    r"C:\Users\aaron\Desktop\008\betfair_new_combined_20260225_152100.pem",
]

headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = f"username={USERNAME}&password={PASSWORD}"

print("="*60)
print("BETFAIR CERT LOGIN")
print("="*60)

for cert_file in CERT_FILES:
    name = os.path.basename(cert_file)
    print(f"\nTrying: {name}")
    
    if not os.path.exists(cert_file):
        print("  File not found")
        continue
        
    try:
        response = requests.post(
            LOGIN_URL,
            data=data,
            cert=cert_file,
            headers=headers,
            timeout=15,
            verify=False
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('loginStatus', 'Unknown')
            print(f"  Login: {status}")
            
            if status == 'SUCCESS':
                token = result.get('sessionToken')
                print(f"\n{'='*60}")
                print("SUCCESS!")
                print(f"{'='*60}")
                print(f"Token: {token[:40]}...")
                
                # Get balance
                bal_headers = {
                    'X-Application': APP_KEY,
                    'X-Authentication': token,
                    'Accept': 'application/json'
                }
                
                bal_resp = requests.get(BALANCE_URL, headers=bal_headers, timeout=10)
                
                if bal_resp.status_code == 200:
                    bal = bal_resp.json()
                    print(f"\n{'='*60}")
                    print("ACCOUNT BALANCE")
                    print(f"{'='*60}")
                    print(f"Available: ${bal.get('availableToBetBalance', 'N/A')}")
                    print(f"Exposure: ${bal.get('exposure', 'N/A')}")
                    print(f"{'='*60}")
                    
                    # Save
                    with open(r"C:\Users\aaron\Desktop\008\betfair_config.json", "w") as f:
                        json.dump({
                            "app_key": APP_KEY,
                            "session_token": token,
                            "balance": bal.get('availableToBetBalance', 0),
                            "extracted_at": "2026-03-06 23:04",
                            "cert_used": name
                        }, f, indent=2)
                    print("\nConfig saved!")
                else:
                    print(f"Balance error: {bal_resp.status_code}")
                break
        else:
            print(f"Error: {response.text[:80]}")
            
    except Exception as e:
        print(f"Error: {str(e)[:80]}")

print("\nDone.")
