"""Test endpoint URL with and without /v1"""
import urllib.request
import json

# Test without /v1 (Cognee's current approach)
print("Testing http://localhost:11434/v1/chat/completions...")
try:
    req = urllib.request.Request(
        "http://localhost:11434/v1/chat/completions",
        data=json.dumps({
            "model": "llama3.2:latest",
            "messages": [{"role": "user", "content": "hi"}]
        }).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"OK with /v1")
except Exception as e:
    print(f"Failed with /v1: {e}")

# Test with /v1
print("\nTesting http://localhost:11434/chat/completions (no /v1)...")
try:
    req = urllib.request.Request(
        "http://localhost:11434/chat/completions",
        data=json.dumps({
            "model": "llama3.2:latest",
            "messages": [{"role": "user", "content": "hi"}]
        }).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"OK without /v1")
except Exception as e:
    print(f"Failed without /v1: {e}")
