"""Test cognee 0.4.1 - clean version"""
import asyncio
import os

os.environ["COGNEE_DATABASE_PATH"] = r"C:\Users\aaron\.openclaw\workspace\the-crypt\cognee\databases"

from cognee import add, cognify, search

async def test():
    print("Testing cognee 0.4.1...")
    
    text = "Sloth_rog is an AI assistant running on the ROG Ally."
    
    try:
        print("Step 1: Adding data...")
        await add(text, dataset_id="test_v041")
        print("Add succeeded")
        
        print("Step 2: Cognifying...")
        await cognify(dataset_id="test_v041")
        print("Cognify succeeded")
        
        print("Step 3: Searching...")
        results = await search(query_text="What is Sloth_rog?")
        print(f"Search returned: {results}")
        
        print("\nSUCCESS!")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
