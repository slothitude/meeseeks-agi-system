"""Test litellm + Ollama (what Cognee uses internally)"""
import os

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"

print("Testing litellm with Ollama...")
import litellm

try:
    response = litellm.completion(
        model="ollama/llama3.2:latest",
        messages=[{"role": "user", "content": "Say hi"}],
        api_base="http://localhost:11434",
        timeout=10
    )
    print(f"litellm OK: {response.choices[0].message.content[:50]}...")
except Exception as e:
    print(f"litellm FAILED: {type(e).__name__}: {e}")
