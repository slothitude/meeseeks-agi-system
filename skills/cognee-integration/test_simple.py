#!/usr/bin/env python3
"""Simple cognee test"""
import asyncio
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("Importing cognee...")
    import cognee
    print("[OK] Import OK")
    
    print("\nTesting simple add...")
    try:
        await cognee.add(
            data="Test memory entry",
            dataset_id="test-dataset"
        )
        print("[OK] Add OK")
    except Exception as e:
        print(f"[FAIL] Add failed: {e}")
        return 1
    
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
