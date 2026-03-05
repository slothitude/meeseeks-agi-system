"""Test Cognee's test_llm_connection directly"""
import os
import asyncio

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"
# Don't skip - we're testing the test itself

print("Importing Cognee...")
import cognee
from cognee.infrastructure.llm.utils import test_llm_connection

async def test():
    print("Running test_llm_connection...")
    try:
        await asyncio.wait_for(
            test_llm_connection(),
            timeout=30
        )
        print("Test passed!")
    except asyncio.TimeoutError:
        print("Test TIMED OUT after 30s")
    except Exception as e:
        print(f"Test failed: {type(e).__name__}: {e}")

asyncio.run(test())
