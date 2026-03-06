"""
Test Gemini API with key parameter
"""

import urllib.request
import json

api_key = "AQ.Ab8RN6LwoqXVTaraDl5WeLEMByg4W7Sk3rV41Y3-IEQJtBbGQw"

# Test Gemini API - list models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read())
        print("SUCCESS - API Key is valid!")
        print(f"Available models: {len(data.get('models', []))}")
        for model in data.get('models', [])[:5]:
            print(f"  - {model.get('name', 'unknown')}")
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying to access a shared Gemini conversation...")
    
    # Try accessing shared content
    share_id = "9700cf948bc5"
    url2 = f"https://generativelanguage.googleapis.com/v1beta/shared/{share_id}?key={api_key}"
    try:
        req2 = urllib.request.Request(url2)
        with urllib.request.urlopen(req2, timeout=10) as response2:
            data2 = json.loads(response2.read())
            print("SUCCESS - Can access shared content!")
            print(json.dumps(data2, indent=2)[:500])
    except Exception as e2:
        print(f"Also failed: {e2}")
