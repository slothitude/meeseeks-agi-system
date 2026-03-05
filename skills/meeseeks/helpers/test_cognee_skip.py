"""Test Cognee add with skip connection test"""
import os
import asyncio

# Set env vars BEFORE importing
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

print("Importing cognee...")
import cognee

async def test_add():
    print("Adding text to dataset...")
    try:
        result = await asyncio.wait_for(
            cognee.add("Sloth_rog runs on Windows Rog machine", dataset_name="sloth_rog"),
            timeout=30
        )
        print(f"Add succeeded! Result: {result}")
    except asyncio.TimeoutError:
        print("Add timed out after 30s")
    except Exception as e:
        print(f"Add failed: {type(e).__name__}: {e}")

asyncio.run(test_add())
