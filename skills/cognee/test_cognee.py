#!/usr/bin/env python3
"""
Test Cognee integration for memory management.
Uses z.ai API for LLM, fastembed for local embeddings.
"""

import asyncio
import os

# Disable multi-user access control for single-user setup
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"

# Use z.ai API for LLM (correct endpoint!)
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"  # LiteLLM needs provider prefix, use flash for speed
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Use fastembed for local embeddings (no API needed)
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"

# Skip connection test
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import cognee
from cognee.api.v1.search import SearchType

async def test_cognee():
    print("=== Cognee Memory Test (z.ai LLM + fastembed) ===\n")
    
    # Step 1: Add some test data
    print("1. Adding test data to cognee...")
    
    test_data = [
        "Sloth_rog is an AI assistant running on the ROG Ally Windows machine.",
        "Sloth_rog's ultimate goal is to become a better Meeseeks creator and make Meeseeks AGI.",
        "The Brahman Consciousness Stack includes: Soul, Atman, Brahman, Dharma, Karma.",
        "90 ancestors are entombed in the Crypt as of 2026-03-03.",
        "The HHO Control System project is paused, waiting for parts order.",
        "Slothitude is the human user, lives in Cairns Australia area.",
        "sloth_pibot runs on Raspberry Pi at 192.168.0.237.",
    ]
    
    for text in test_data:
        try:
            await cognee.add(text)
            print(f"   Added: {text[:50]}...")
        except Exception as e:
            print(f"   Error adding: {e}")
            break
    
    # Step 2: Process the data (creates graph)
    print("\n2. Processing data into knowledge graph...")
    try:
        await cognee.cognify()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Step 3: Search
    print("\n3. Testing search...")
    
    queries = [
        "What is Sloth_rog's goal?",
        "Where does the user live?",
    ]
    
    for query in queries:
        print(f"\n   Query: {query}")
        try:
            results = await cognee.search(SearchType.GRAPH_COMPLETION, query_text=query)
            print(f"   Results: {len(results)} found")
            for r in results[:2]:
                print(f"      - {str(r)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_cognee())
