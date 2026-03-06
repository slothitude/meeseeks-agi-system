#!/usr/bin/env python3
"""Test Ollama embeddings via OpenAI-compatible API"""
import requests
import json

response = requests.post(
    "http://localhost:11434/v1/embeddings",
    headers={"Content-Type": "application/json"},
    json={
        "model": "nomic-embed-text",
        "input": "test text"
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
