#!/usr/bin/env python3
"""Test Ollama OpenAI-compatible endpoint"""
import requests
import json

response = requests.post(
    "http://localhost:11434/v1/chat/completions",
    headers={"Content-Type": "application/json"},
    json={
        "model": "phi3:mini",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 20
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
