#!/usr/bin/env python3
"""Test ZAI Coding API directly"""
import requests
import json

api_key = "6b1214861bdf4530b184ce8ae7724f75.LlAwBSFoooZDIxCu"

response = requests.post(
    "https://api.z.ai/api/coding/paas/v4/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "GLM-4.7",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
