#!/usr/bin/env python3
"""Test cognee with ZAI Coding API"""
import asyncio
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["ZAI_API_KEY"] = "6b1214861bdf4530b184ce8ae7724f75.LlAwBSFoooZDIxCu"

async def main():
    print("Importing cognee...")
    import cognee
    print("[OK] Import OK")
    
    print("\nAdding test memory...")
    try:
        await cognee.add(
            data="Sloth_rog is an AI assistant. Ultimate goal: Make Meeseeks AGI. Uses GLM-5 model.",
            dataset_id="sloth-rog-memory"
        )
        print("[OK] Memory added!")
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\nCognee working with ZAI Coding API!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
