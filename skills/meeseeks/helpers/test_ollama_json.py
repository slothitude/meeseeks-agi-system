"""Test Ollama's JSON mode support"""
import urllib.request
import json

# Test with response_format
req = urllib.request.Request(
    "http://localhost:11434/v1/chat/completions",
    data=json.dumps({
        "model": "llama3.2:latest",
        "messages": [{"role": "user", "content": "Say test"}],
        "response_format": {"type": "json_object"}
    }).encode(),
    headers={"Content-Type": "application/json"}
)

print("Testing Ollama OpenAI-compatible endpoint with JSON mode...")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
        print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")
