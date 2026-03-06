"""Test cognee with minimal imports"""
import os
import asyncio

# Set env vars BEFORE any cognee import
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# Use official API only
from cognee import add, cognify, search

async def test():
    print("Testing cognee with fresh database...")
    
    text = "Sloth_rog is an AI assistant. It helps with coding tasks."
    
    try:
        # Add
        print("Adding data...")
        await add(text, dataset_id="fresh_test")
        print("✓ Add succeeded")
        
        # Cognify
        print("Processing...")
        await cognify(dataset_id="fresh_test")
        print("✓ Cognify succeeded")
        
        # Search
        print("Searching...")
        results = await search(query_text="What is Sloth_rog?", query_type="GRAPH_COMPLETION")
        print(f"✓ Search: {results}")
        
        print("\n✅ SUCCESS!")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
