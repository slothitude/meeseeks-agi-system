"""Test Cognee add operation"""
import os
import asyncio

# Set env vars BEFORE importing cognee
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"

print("Importing cognee...")
import cognee

async def test_add():
    print("Adding text to dataset...")
    try:
        await asyncio.wait_for(
            cognee.add("Test memory from Sloth_rog", dataset_name="sloth_rog"),
            timeout=30
        )
        print("Add succeeded!")
    except asyncio.TimeoutError:
        print("Add timed out after 30s")
    except Exception as e:
        print(f"Add failed: {e}")

asyncio.run(test_add())
