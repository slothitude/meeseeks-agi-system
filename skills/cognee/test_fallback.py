#!/usr/bin/env python3
"""Test Cognee fallback speed - Ollama llama3.2 vs z.ai"""

import os
import asyncio
import time

# Configure BEFORE importing cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# Fallback LLM - Ollama llama3.2 (local, no rate limits)
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/llama3.2"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["LLM_API_KEY"] = "ollama"

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
    print("COGNEE FALLBACK SPEED TEST (Ollama llama3.2)")
    print("=" * 60)
    
    # Clear old data
    print("\n[0] Clearing old data...")
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("    Cleared!")
    except Exception as e:
        print(f"    Clear skipped: {e}")
    
    # Step 1: Add text
    print("\n[1] Adding text...")
    text = "Sloth_rog is an AI assistant. His ultimate goal is to make Meeseeks AGI. He coordinates with sloth_pibot on the Raspberry Pi."
    start = time.time()
    await cognee.add(text, dataset_name="fallback_test")
    add_time = time.time() - start
    print(f"    Added in {add_time:.2f}s")
    
    # Step 2: Process into graph (LLM-heavy - this is where speed matters)
    print("\n[2] Processing into knowledge graph (LLM-heavy)...")
    start = time.time()
    await cognee.cognify(dataset_name="fallback_test")
    cognify_time = time.time() - start
    print(f"    Processed in {cognify_time:.2f}s")
    
    # Step 3: Search (fast vector search)
    print("\n[3] Searching...")
    start = time.time()
    results = await cognee.search(
        query_text="What is Sloth_rog's ultimate goal?",
        query_type=SearchType.CHUNKS,
        top_k=3
    )
    search_time = time.time() - start
    print(f"    Search in {search_time:.2f}s")
    print(f"    Found {len(results) if results else 0} results")
    
    print("\n" + "=" * 60)
    print("TIMING SUMMARY")
    print("=" * 60)
    print(f"  Add:      {add_time:.2f}s")
    print(f"  Cognify:  {cognify_time:.2f}s  <-- LLM speed test")
    print(f"  Search:   {search_time:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test())
