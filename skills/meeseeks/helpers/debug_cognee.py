"""Debug Cognee + Ollama connection"""
import os
import asyncio

# Set env vars BEFORE importing
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"
os.environ["LOG_LEVEL"] = "DEBUG"

print("Testing Ollama directly first...")
import urllib.request
import json

# Test Ollama generate endpoint
req = urllib.request.Request(
    "http://localhost:11434/api/generate",
    data=json.dumps({"model": "llama3.2:latest", "prompt": "Hi", "stream": False}).encode(),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
        print(f"Ollama direct test OK: {result.get('response', '')[:50]}...")
except Exception as e:
    print(f"Ollama direct test FAILED: {e}")

print("\nNow testing Cognee's LLM config...")
import cognee
from cognee.infrastructure.llm.config import get_llm_config

config = get_llm_config()
print(f"LLM Provider: {config.llm_provider}")
print(f"LLM Model: {config.llm_model}")
print(f"LLM Endpoint: {config.llm_endpoint}")
print(f"LLM API Key: {config.llm_api_key[:10]}..." if config.llm_api_key else "No API key")
