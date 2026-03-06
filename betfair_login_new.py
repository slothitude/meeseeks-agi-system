#!/usr/bin/env python3
"""Betfair login with new certificates"""
import requests
import json
import urllib3
import ssl

urllib3.disable_warnings()

# Credentials
USERNAME = "aaron Adsit"
PASSWORD = "Lachlan64!"
APP_KEY = "XmZEwtLsIRkf5lQ3"

# Login endpoint (try both AU and UK)
LOGIN_URLS = [
    "https://identitysso-cert.betfair.com.au/api/certlogin",
    "https://identitysso-cert.betfair.com/api/certlogin"
]
BALANCE_URL = "https://api.betfair.com/exchange/account/rest/v1.0/getAccountFunds/"

# Certificate file (the combined one sent)
CERT_FILE = r"C:\Users\aaron\.openclaw\workspace\betfair_combined.p12"

print("="*60)
print("BETFAIR CERTIFICATE LOGIN - NEW CERT")
print("="*60)
print(f"Username: {USERNAME}")
print(f"App Key: {APP_KEY}")
print(f"Cert: {CERT_FILE}")
print()

headers = {
    'X-Application': APP_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = f"username={USERNAME}&password={PASSWORD}"

for login_url in LOGIN_URLS:
    print(f"\nTrying: {login_url.split('//')[1].split('/')[0]}")
    
    try:
        # Try with p12 file
        response = requests.post(
            login_url,
            data=data,
            cert=CERT_FILE,
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
                print(f"\n✓ SUCCESS!")
                print(f"Token: {token[:40]}...")
                
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
                    print("💰 ACCOUNT BALANCE")
                    print("="*60)
                    print(f"Available: ${bal.get('availableToBetBalance', 'N/A')}")
                    print(f"Exposure: ${bal.get('exposure', 'N/A')}")
                    print("="*60)
                    
                    # Save config
                    config = {
                        "app_key": APP_KEY,
                        "session_token": token,
                        "balance": bal.get('availableToBetBalance', 0),
                        "extracted_at": "2026-03-06 23:02"
                    }
                    with open(r"C:\Users\aaron\Desktop\008\betfair_config.json", "w") as f:
                        json.dump(config, f, indent=2)
                    print("\n✓ Config saved to 008/betfair_config.json")
                else:
                    print(f"Balance error: {bal_resp.text[:200]}")
                    
                exit(0)
            else:
                print(f"❌ {status}")
        else:
            print(f"Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"Error: {str(e)[:100]}")

print("\n" + "="*60)
print("All attempts failed")
print("="*60)
