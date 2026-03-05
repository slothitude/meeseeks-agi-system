"""Test Ollama embedding endpoint"""
import urllib.request
import json

# Test embedding endpoint
req = urllib.request.Request(
    "http://localhost:11434/v1/embeddings",
    data=json.dumps({
        "model": "nomic-embed-text:latest",
        "input": "test"
    }).encode(),
    headers={"Content-Type": "application/json"}
)

print("Testing Ollama embeddings endpoint...")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
        print(f"Success! Embedding length: {len(result['data'][0]['embedding'])}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")
