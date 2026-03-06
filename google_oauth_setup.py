#!/usr/bin/env python3
"""
Google OAuth Setup for Sloth_rog
Initial authentication to get access token
"""

import json
import webbrowser
from urllib.parse import urlencode
import urllib.request

# Load credentials
with open('google_credentials.json', 'r') as f:
    creds = json.load(f)

installed = creds['installed']

# Build auth URL
auth_url = (
    f"{installed['auth_uri']}?"
    f"client_id={installed['client_id']}&"
    f"redirect_uri={installed['redirect_uris'][1]}&"
    f"response_type=code&"
    f"scope={' '.join(creds['scope'])}&"
    f"access_type=offline"
)

print("=" * 60)
print("GOOGLE OAUTH SETUP")
print("=" * 60)
print("\n1. Opening browser for authentication...")
print("2. Log in as: slothitudegames@gmail.com")
print("3. Approve the access request")
print("4. You'll get a code - paste it here")
print("\n" + "=" * 60)

# Open browser
webbrowser.open(auth_url)

# Wait for code
print("\nPaste the authorization code here: ")
auth_code = input().strip()

# Exchange code for token
token_url = installed['token_uri']
data = urlencode({
    'code': auth_code,
    'client_id': installed['client_id'],
    'client_secret': installed['client_secret'],
    'redirect_uri': installed['redirect_uris'][1],
    'grant_type': 'authorization_code'
})

req = urllib.request.Request(token_url, data.encode())
with urllib.request.urlopen(req) as response:
    token_data = json.loads(response.read())

# Save token
with open('google_token.json', 'w') as f:
    json.dump(token_data, f, indent=2)

print("\n" + "=" * 60)
print("SUCCESS! Token saved to google_token.json")
print("=" * 60)
print(f"\nAccess Token: {token_data['access_token'][:50]}...")
print(f"Refresh Token: {token_data['refresh_token'][:50]}...")
print(f"Expires in: {token_data['expires_in']} seconds")
