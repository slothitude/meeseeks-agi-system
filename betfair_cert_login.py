#!/usr/bin/env python3
"""Betfair cert login with proper credentials"""
import requests
import json
import urllib3

urllib3.disable_warnings()

# From aus_cert_login.py
USERNAME = "aaron Adsit"
PASSWORD = "Lachlan64!"
APP_KEY = "XmZEwtLsIRkf5lQ3"

# Try Australian cert endpoint
LOGIN_URL = "https://identitysso-cert.betfair.com.au/api/certlogin"
BALANCE_URL = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"

# Certificate files to try
CERT_FILES = [
    r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem",
    r"C:\Users\aaron\Desktop\008\betfair_combined.pem",
    r"C:\Users\aaron\Desktop\008\betfair_new_combined_20260225_152100.pem",
]

print("="*60)
print("BETFAIR CERTIFICATE LOGIN")
print("="*60)
print(f"Username: {USERNAME}")
print(f"App Key: {APP_KEY}")
print()

headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = f"username={USERNAME}&password={PASSWORD}"

for cert_file in CERT_FILES:
    print(f"\nTrying: {cert_file.split('\\')[-1]}")
    
    try:
        response = requests.post(
            LOGIN_URL,
            data=data,
            cert=cert_file,
            headers=headers,
            timeout=15,
            verify=False
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('loginStatus', 'Unknown')
            print(f"Login status: {status}")
            
            if status == 'SUCCESS':
                token = result.get('sessionToken')
                print(f"\n✓ SUCCESS! Token: {token[:40]}...")
                
                # Check balance
                bal_headers = {
                    'X-Application': APP_KEY,
                    'X-Authentication': token,
                    'Accept': 'application/json'
                }
                
                bal_resp = requests.get(BALANCE_URL, headers=bal_headers, timeout=10)
                
                if bal_resp.status_code == 200:
                    bal = bal_resp.json()
                    print("\n" + "="*60)
                    print("ACCOUNT BALANCE")
                    print("="*60)
                    print(f"Available: ${bal.get('availableToBetBalance', 'N/A')}")
                    print(f"Exposure: ${bal.get('exposure', 'N/A')}")
                    print("="*60)
                    
                    # Save
                    config = {
                        "app_key": APP_KEY,
                        "session_token": token,
                        "balance": bal.get('availableToBetBalance', 0),
                        "extracted_at": "2026-03-06 22:58"
                    }
                    with open(r"C:\Users\aaron\Desktop\008\betfair_config.json", "w") as f:
                        json.dump(config, f, indent=2)
                    print("\n✓ Config saved!")
                else:
                    print(f"Balance error: {bal_resp.text}")
                    
                break
            else:
                print(f"Failed: {status}")
        else:
            print(f"Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"Error: {e}")
