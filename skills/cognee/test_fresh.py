#!/usr/bin/env python3
"""Fresh Cognee test with z.ai endpoint."""

import os
import asyncio

# Configure BEFORE importing cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# z.ai Coding endpoint
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Ollama local embeddings
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"

async def test():
    import cognee
    from cognee.api.v1.search import SearchType
    
    print("=" * 60)
    print("COGNEE FRESH TEST")
    print("=" * 60)
    
    # Step 1: Add simple text
    print("\n[1] Adding text to cognee...")
    text = "Sloth_rog is an AI assistant. His ultimate goal is to make Meeseeks AGI."
    await cognee.add(text, dataset_name="test_dataset")
    print("    Added!")
    
    # Step 2: Process into graph
    print("\n[2] Processing into knowledge graph...")
    await cognee.cognify(dataset_name="test_dataset")
    print("    Processed!")
    
    # Step 3: Search
    print("\n[3] Searching for 'ultimate goal'...")
    results = await cognee.search(
        query_text="What is Sloth_rog's ultimate goal?",
        query_type=SearchType.CHUNKS,
        top_k=3
    )
    
    print(f"    Found {len(results) if results else 0} results:")
    if results:
        for i, r in enumerate(results[:3]):
            print(f"    [{i}] {str(r)[:200]}...")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test())
