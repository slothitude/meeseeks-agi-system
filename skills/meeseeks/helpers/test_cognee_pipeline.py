"""Test full Cognee pipeline with FIXED Ollama endpoint"""
import os
import asyncio

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"  # FIXED
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"

print("Importing cognee...")
import cognee
from cognee.api.v1.search import SearchType

async def test_full():
    # Add
    print("\n1. Adding text...")
    await cognee.add("Sloth_rog is an AI assistant created by Slothitude. Sloth_rog runs on Windows.", dataset_name="sloth_rog")
    print("   Added!")

    # Cognify
    print("\n2. Cognifying (building knowledge graph)...")
    try:
        await asyncio.wait_for(cognee.cognify(dataset_name="sloth_rog"), timeout=180)
        print("   Cognified!")
    except asyncio.TimeoutError:
        print("   Cognify timed out (180s)")
        return

    # Search
    print("\n3. Searching...")
    results = await cognee.search(
        query_text="Who created Sloth_rog?",
        search_type=SearchType.GRAPH_COMPLETION,
        limit=5
    )
    print(f"   Found {len(results)} results:")
    for r in results[:3]:
        text = r.text if hasattr(r, 'text') else str(r)
        print(f"   - {text[:100]}...")

asyncio.run(test_full())
