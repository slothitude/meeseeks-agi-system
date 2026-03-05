"""Test Cognee with ALL required env vars"""
import os
import asyncio

# LLM config
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["LLM_API_KEY"] = "ollama"

# Embedding config
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["EMBEDDING_API_KEY"] = "ollama"
os.environ["EMBEDDING_DIMENSIONS"] = "768"  # Required for nomic-embed-text

print("Importing Cognee...")
import cognee
from cognee.infrastructure.llm.utils import test_llm_connection, test_embedding_connection

async def test():
    print("Testing LLM connection...")
    await test_llm_connection()
    print("LLM OK!")

    print("Testing embedding connection...")
    await test_embedding_connection()
    print("Embedding OK!")

    print("\nAll tests passed!")

asyncio.run(test())
