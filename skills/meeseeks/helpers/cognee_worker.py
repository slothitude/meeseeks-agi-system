"""
Cognee Worker - Runs under Python 3.13
This script is called by cognee_bridge.py
"""

import sys
import json
import os

# Set Ollama as LLM provider (no API key needed)
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"  # Must include /v1 for OpenAI compatibility
os.environ["LLM_API_KEY"] = "ollama"

# Set Ollama as embedding provider
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/v1"  # Must include /v1
os.environ["EMBEDDING_API_KEY"] = "ollama"
os.environ["EMBEDDING_DIMENSIONS"] = "768"  # nomic-embed-text has 768 dimensions
os.environ["HUGGINGFACE_TOKENIZER"] = ""  # Not needed for Ollama, but Cognee requires it

import cognee
from cognee.api.v1.search import SearchType

async def handle_add(args):
    """Add text to dataset"""
    try:
        await cognee.add(args["text"], dataset_name=args.get("dataset", "default"))
        return {"success": True, "message": f"Added to {args.get('dataset', 'default')}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def handle_search(args):
    """Search knowledge graph"""
    try:
        results = await cognee.search(
            query_text=args["query"],
            search_type=SearchType.GRAPH_COMPLETION,
            limit=args.get("limit", 10)
        )
        return {
            "success": True,
            "results": [
                {"text": r.text if hasattr(r, 'text') else str(r)}
                for r in results
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def handle_cognify(args):
    """Process dataset into knowledge graph"""
    try:
        await cognee.cognify(dataset_name=args.get("dataset", "default"))
        return {"success": True, "message": f"Cognified {args.get('dataset', 'default')}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No args provided"}))
        sys.exit(1)
    
    try:
        args = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON: {e}"}))
        sys.exit(1)
    
    action = args.get("action")
    
    handlers = {
        "add": handle_add,
        "search": handle_search,
        "cognify": handle_cognify
    }
    
    if action not in handlers:
        print(json.dumps({"success": False, "error": f"Unknown action: {action}"}))
        sys.exit(1)
    
    result = await handlers[action](args)
    print(json.dumps(result))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
