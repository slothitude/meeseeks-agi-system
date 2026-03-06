#!/usr/bin/env python3.13
"""
Cognee Worker - Runs under Python 3.13

This script is called by cognee_bridge.py to perform actual Cognee operations.
Must run under Python 3.13 (or 3.10-3.13) where Cognee is installed.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Configure Cognee BEFORE importing
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# Use Ollama for LLM (local, free)
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"  # Cognee requires this even for Ollama

# Use FastEmbed for embeddings (local, fast)
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"

# Cognee data in The Crypt
COGNEE_DATA_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/cognee")
COGNEE_DATA_DIR.mkdir(parents=True, exist_ok=True)
os.environ["COGNEE_DATA_DIR"] = str(COGNEE_DATA_DIR)

# Now import Cognee
try:
    import cognee
    from cognee.api.v1.search import SearchType
    COGNEE_AVAILABLE = True
except ImportError as e:
    COGNEE_AVAILABLE = False
    IMPORT_ERROR = str(e)


async def ingest_file(file_path: str) -> dict:
    """Ingest a file into Cognee knowledge graph."""
    if not COGNEE_AVAILABLE:
        return {"success": False, "error": f"Cognee not available: {IMPORT_ERROR}"}
    
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        # Read file content
        content = file_path.read_text(encoding="utf-8")
        
        # Ingest into Cognee with dataset name
        dataset_name = file_path.stem
        await cognee.add([content], dataset_name)
        
        # Process (build graph)
        await cognee.cognify(dataset_name)
        
        return {
            "success": True,
            "file": str(file_path),
            "dataset": dataset_name,
            "chars": len(content)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def query_wisdom(query: str) -> dict:
    """Query Cognee for wisdom using fast CHUNKS search."""
    if not COGNEE_AVAILABLE:
        return {"success": False, "error": f"Cognee not available: {IMPORT_ERROR}"}
    
    try:
        # Use CHUNKS search (fast, vector similarity)
        results = await cognee.search(
            query_text=query,
            search_type=SearchType.CHUNKS
        )
        
        # Extract relevant content
        wisdom = []
        for result in results[:5]:  # Top 5 results
            if hasattr(result, 'chunk_data'):
                wisdom.append(result.chunk_data)
            elif hasattr(result, 'text'):
                wisdom.append(result.text)
            elif isinstance(result, dict):
                wisdom.append(result.get('text', str(result)))
        
        return {
            "success": True,
            "query": query,
            "results": wisdom,
            "count": len(wisdom)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_status() -> dict:
    """Get Cognee status."""
    return {
        "success": True,
        "cognee_available": COGNEE_AVAILABLE,
        "python_version": sys.version,
        "data_dir": str(COGNEE_DATA_DIR),
        "timestamp": datetime.now().isoformat()
    }


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "ingest":
        if len(sys.argv) < 3:
            result = {"success": False, "error": "No file path provided"}
        else:
            result = await ingest_file(sys.argv[2])
    
    elif action == "query":
        if len(sys.argv) < 3:
            result = {"success": False, "error": "No query provided"}
        else:
            result = await query_wisdom(sys.argv[2])
    
    elif action == "status":
        result = await get_status()
    
    else:
        result = {"success": False, "error": f"Unknown action: {action}"}
    
    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
