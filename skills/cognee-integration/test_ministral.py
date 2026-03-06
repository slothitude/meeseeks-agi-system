#!/usr/bin/env python3
"""Test cognee with ministral-3"""
import asyncio
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("Importing cognee...")
    import cognee
    print("[OK] Import OK")
    
    print("\nAdding test memory...")
    try:
        await cognee.add(
            data="Sloth_rog is an AI assistant running on Windows. Ultimate goal: Make Meeseeks AGI.",
            dataset_id="sloth-rog-memory"
        )
        print("[OK] Memory added to knowledge graph!")
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\nSUCCESS - Cognee working!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
