"""
Test Google API Key
Check if this is a Gemini API key
"""

import urllib.request
import json

api_key = "AQ.Ab8RN6LwoqXVTaraDl5WeLEMByg4W7Sk3rV41Y3-IEQJtBbGQw"

# Test Gemini API
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro?key={api_key}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read())
        print("✅ API Key is valid for Gemini!")
        print(f"\nAvailable models: {len(data.get('models', []))}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThis might be a different type of key")
