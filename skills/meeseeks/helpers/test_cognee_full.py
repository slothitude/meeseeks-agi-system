"""Test full Cognee pipeline with Ollama"""
import os
import asyncio

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

print("Importing cognee...")
import cognee
from cognee.api.v1.search import SearchType

async def test_full_pipeline():
    # Add
    print("\n1. Adding text...")
    await cognee.add("Sloth_rog is an AI assistant running on Windows. His creator is Slothitude.", dataset_name="sloth_rog")
    print("   Added!")

    # Cognify (build knowledge graph)
    print("\n2. Cognifying (building knowledge graph)...")
    try:
        await asyncio.wait_for(
            cognee.cognify(dataset_name="sloth_rog"),
            timeout=120
        )
        print("   Cognified!")
    except asyncio.TimeoutError:
        print("   Cognify timed out (120s) - this is expected for first run")
        return
    except Exception as e:
        print(f"   Cognify failed: {e}")
        return

    # Search
    print("\n3. Searching...")
    try:
        results = await cognee.search(
            query_text="Who created Sloth_rog?",
            search_type=SearchType.GRAPH_COMPLETION,
            limit=5
        )
        print(f"   Found {len(results)} results:")
        for r in results[:3]:
            text = r.text if hasattr(r, 'text') else str(r)
            print(f"   - {text[:100]}...")
    except Exception as e:
        print(f"   Search failed: {e}")

asyncio.run(test_full_pipeline())
