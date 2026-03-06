"""Test cognee 0.4.1"""
import asyncio
import os

# Set env before import
os.environ["COGNEE_DATABASE_PATH"] = r"C:\Users\aaron\.openclaw\workspace\the-crypt\cognee\databases"

from cognee import add, cognify, search

async def test():
    print("Testing cognee 0.4.1...")
    
    text = "Sloth_rog is an AI assistant running on the ROG Ally."
    
    try:
        # Add
        print("Adding data...")
        await add(text, dataset_id="test_v041")
        print("✓ Add succeeded")
        
        # Cognify
        print("Processing...")
        await cognify(dataset_id="test_v041")
        print("✓ Cognify succeeded")
        
        # Search
        print("Searching...")
        results = await search(query_text="What is Sloth_rog?")
        print(f"✓ Search: {results}")
        
        print("\n✅ SUCCESS!")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
