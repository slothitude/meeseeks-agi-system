"""
Cognee Bridge for Sloth_rog
Uses Python 3.13 subprocess since Cognee requires <3.14
"""

import subprocess
import json
import sys
from pathlib import Path

# Python 3.13 executable
PY313 = "py -3.13"

def run_cognee_worker(args: dict) -> dict:
    """Run cognee operations via Python 3.13 subprocess"""
    worker_script = Path(__file__).parent / "cognee_worker.py"
    
    # Serialize args as JSON
    args_json = json.dumps(args)
    
    # Run via Python 3.13
    result = subprocess.run(
        [PY313, str(worker_script), args_json],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr or result.stdout
        }
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"Invalid JSON output: {result.stdout[:500]}"
        }


async def add_memory(text: str, dataset: str = "sloth_rog") -> dict:
    """Add text to Cognee knowledge graph"""
    return run_cognee_worker({
        "action": "add",
        "text": text,
        "dataset": dataset
    })


async def search_memory(query: str, limit: int = 10) -> dict:
    """Search Cognee knowledge graph"""
    return run_cognee_worker({
        "action": "search",
        "query": query,
        "limit": limit
    })


async def cognify(dataset: str = "sloth_rog") -> dict:
    """Process dataset into knowledge graph"""
    return run_cognee_worker({
        "action": "cognify",
        "dataset": dataset
    })


# CLI test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing Cognee bridge...")
        
        # Test add
        result = await add_memory("Sloth_rog runs on Windows Rog machine")
        print(f"Add: {result}")
        
        # Test cognify
        result = await cognify()
        print(f"Cognify: {result}")
        
        # Test search
        result = await search_memory("Sloth_rog")
        print(f"Search: {result}")
    
    asyncio.run(test())
