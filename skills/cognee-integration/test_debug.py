"""Test cognee 0.4.1 with full error capture"""
import asyncio
import os
import traceback

os.environ["COGNEE_DATABASE_PATH"] = r"C:\Users\aaron\.openclaw\workspace\the-crypt\cognee\databases"

try:
    from cognee import add, cognify, search
    print("✓ Imports succeeded")
    
    async def test():
        print("Testing add...")
        try:
            result = await add("Sloth_rog is an AI assistant.", dataset_id="test")
            print(f"✓ Add result: {result}")
        except Exception as e:
            print(f"❌ Add failed: {e}")
            traceback.print_exc()
    
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    traceback.print_exc()
