"""Test Cognee with valid HuggingFace tokenizer"""
import os
import asyncio

# LLM config
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["LLM_API_KEY"] = "ollama"

# Embedding config - must use valid HuggingFace tokenizer for chunking
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["EMBEDDING_API_KEY"] = "ollama"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "bert-base-uncased"  # Valid tokenizer for chunking

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

    print("\n✓ All Cognee tests passed with Ollama!")

asyncio.run(test())
