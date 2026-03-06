"""Test cognee with fresh database"""
import os
import sys

# Set env vars BEFORE importing cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
os.environ["COGNEE_DATABASE_PATH"] = r"C:\Users\aaron\.openclaw\workspace\the-crypt\cognee\databases"

# Cognee imports
sys.path.insert(0, r"C:\Users\aaron\.openclaw\workspace\skills\cognee-integration\venv-cognee\Lib\site-packages")
import cognee
from cognee.api.v1.cognify.code_graph import code_graph
from cognee.infrastructure.databases.vector import get_vector_engine
from cognee.modules.retrieval.brute_force_triplet_search import brute_force_triplet_search

async def test():
    print("Creating new dataset...")
    
    # Try with a simple dataset name (no special chars)
    dataset_name = "test123"
    
    try:
        # Add data
        print(f"Adding text to dataset '{dataset_name}'...")
        await cognee.add(
            data="Sloth_rog is an AI assistant running on the ROG Ally. It helps with coding, file operations, and system administration.",
            dataset_id=dataset_name
        )
        print("✓ Add succeeded!")
        
        # Cognify
        print("Running cognify...")
        await cognee.cognify(dataset_id=dataset_name)
        print("✓ Cognify succeeded!")
        
        # Search
        print("Searching...")
        results = await brute_force_triplet_search(
            query_text="What is Sloth_rog?",
            datasets=[dataset_name]
        )
        print(f"✓ Search returned {len(results)} results")
        for r in results[:3]:
            print(f"  - {r}")
            
        print("\n✅ ALL TESTS PASSED!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
