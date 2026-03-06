#!/usr/bin/env python3
"""Quick Betfair balance check using betfairlightweight"""
import betfairlightweight

# Credentials - try alternate
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Lachlan64!"
APP_KEY = "XmZEwtLsIRkf5lQ3"

print("="*60)
print("BETFAIR INTERACTIVE LOGIN")
print("="*60)

try:
    # Create client
    trading = betfairlightweight.APIClient(
        username=USERNAME,
        password=PASSWORD,
        app_key=APP_KEY
    )
    
    # Interactive login (no cert needed)
    print("\nAttempting interactive login...")
    trading.login_interactive()
    
    print("SUCCESS! Logged in.")
    print(f"Session token: {trading.session_token[:30]}...")
    
    # Get balance
    print("\nChecking account funds...")
    funds = trading.account.get_account_funds()
    
    print("\n" + "="*60)
    print("ACCOUNT BALANCE")
    print("="*60)
    print(f"Available: ${funds.available_to_bet_balance}")
    print(f"Exposure: ${funds.exposure}")
    print(f"Wallet: {funds.wallet if hasattr(funds, 'wallet') else 'N/A'}")
    print("="*60)
    
    # Save session
    import json
    config = {
        "app_key": APP_KEY,
        "session_token": trading.session_token,
        "username": USERNAME,
        "balance": funds.available_to_bet_balance,
        "extracted_at": "2026-03-06 22:57"
    }
    with open("betfair_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("\nConfig saved!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
