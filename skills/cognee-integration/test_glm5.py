#!/usr/bin/env python3
"""Simple cognee test with GLM-5"""
import asyncio
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Set API key
os.environ["ZAI_API_KEY"] = "6b1214861bdf4530b184ce8ae7724f75.LlAwBSFoooZDIxCu"

async def main():
    print("Importing cognee...")
    import cognee
    print("[OK] Import OK")
    
    print("\nTesting simple add...")
    try:
        await cognee.add(
            data="Test memory entry from Sloth_rog",
            dataset_id="test-dataset"
        )
        print("[OK] Add OK - memory stored")
    except Exception as e:
        print(f"[FAIL] Add failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\nDone! Cognee working with GLM-5")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
