#!/usr/bin/env python3
"""Test Cognee search on migrated ancestors."""

import os
import asyncio

# Configure Cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"

async def main():
    import cognee
    from cognee.api.v1.search import SearchType
    
    print("Searching Cognee for 'debug API'...")
    
    try:
        results = await cognee.search(
            query_text="debug API",
            query_type=SearchType.CHUNKS,
            datasets=["meeseeks-ancestors"],
            top_k=5
        )
        
        print(f"Found {len(results) if results else 0} results")
        
        if results:
            for i, r in enumerate(results[:3]):
                print(f"\n[{i+1}] {str(r)[:300]}...")
    except Exception as e:
        print(f"Search error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
