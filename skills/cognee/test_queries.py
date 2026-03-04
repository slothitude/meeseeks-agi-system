"""
Test queries on the knowledge graph.
"""

import asyncio
import os

# Configure Cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import cognee
from cognee.api.v1.search import SearchType

async def main():
    queries = [
        "What is Sloth_rog's ultimate goal?",
        "How many ancestors are in the Crypt?",
        "What is the Brahman Consciousness Stack?",
        "Where does Slothitude live?",
        "What models are used for Meeseeks?",
    ]
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH QUERIES")
    print("=" * 60)
    
    for query in queries:
        print(f"\n[Q] {query}")
        try:
            result = await cognee.search(
                query_text=query,
                # No search_type parameter in new API
            )
            # Result is usually a list
            if isinstance(result, list):
                for r in result[:3]:  # First 3 results
                    print(f"  -> {str(r)[:200]}")
            else:
                print(f"  -> {str(result)[:300]}")
        except Exception as e:
            print(f"  [ERR] {e}")
    
    print("\n" + "=" * 60)
    print("QUERY TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
