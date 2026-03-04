#!/usr/bin/env python3
"""
Test Cognee speed with Ollama + Qwen3
Benchmarks ingestion and query performance.
"""

import os
import time
import asyncio

# Ollama local LLM (llama3.2 supports tool calling)
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/llama3.2"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434/v1"
os.environ["LLM_API_KEY"] = "ollama"

# Fastembed local embeddings
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"

# Cognee data directory - separate for speed test
os.environ["COGNEE_DATA_DIR"] = "C:/Users/aaron/.openclaw/workspace/the-crypt/cognee_speed_test"


async def test_ollama_speed():
    print("=" * 60)
    print("COGNEE + OLLAMA + QWEN3 SPEED TEST")
    print("=" * 60)
    
    # Import after env vars set
    import cognee
    from cognee.api.v1.search import SearchType
    
    # Test data
    test_chunks = [
        "Sloth_rog is an AI assistant running on the ROG Ally.",
        "The ultimate goal is to make the Meeseeks AGI through accumulated wisdom.",
        "90 ancestors have been entombed in the Crypt.",
        "The consciousness stack includes Atman, Brahman, and Meta-Atman layers.",
        "Karma is observed, not calculated - it's natural consequence.",
    ]
    
    # Clear old data for clean test
    dataset = "speed_test"
    
    # Test 1: Add data
    print("\n[1] ADDING DATA (5 chunks)")
    add_start = time.time()
    for i, chunk in enumerate(test_chunks):
        chunk_start = time.time()
        await cognee.add(chunk, dataset_name=dataset)
        chunk_time = time.time() - chunk_start
        print(f"    Chunk {i+1}: {chunk_time:.2f}s")
    add_total = time.time() - add_start
    print(f"    TOTAL: {add_total:.2f}s ({add_total/5:.2f}s per chunk)")
    
    # Test 2: Cognify (graph extraction)
    print("\n[2] COGNIFY (building knowledge graph)")
    cognify_start = time.time()
    await cognee.cognify(dataset_name=dataset)
    cognify_time = time.time() - cognify_start
    print(f"    TOTAL: {cognify_time:.2f}s")
    
    # Test 3: Query - CHUNKS (fast vector search)
    print("\n[3] QUERY - CHUNKS (fast vector search)")
    query1_start = time.time()
    results1 = await cognee.search(SearchType.CHUNKS, query_text="What is the ultimate goal?")
    query1_time = time.time() - query1_start
    print(f"    Time: {query1_time:.2f}s")
    print(f"    Results: {len(results1) if results1 else 0}")
    if results1:
        print(f"    First result: {str(results1[0])[:100]}...")
    
    # Test 4: Query - GRAPH_COMPLETION (LLM-powered)
    print("\n[4] QUERY - GRAPH_COMPLETION (LLM-powered)")
    query2_start = time.time()
    results2 = await cognee.search(SearchType.GRAPH_COMPLETION, query_text="What is the Meeseeks goal?")
    query2_time = time.time() - query2_start
    print(f"    Time: {query2_time:.2f}s")
    if results2:
        print(f"    Result: {str(results2[0])[:200]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("SPEED SUMMARY")
    print("=" * 60)
    print(f"Add (per chunk):    {add_total/5:.2f}s")
    print(f"Cognify:            {cognify_time:.2f}s")
    print(f"Query CHUNKS:       {query1_time:.2f}s")
    print(f"Query GRAPH:        {query2_time:.2f}s")
    print("=" * 60)
    
    # Compare to z.ai baseline
    print("\nCOMPARISON (vs z.ai baseline):")
    print(f"  z.ai Cognify:     ~60s (with 30s delays)")
    print(f"  Ollama Cognify:   {cognify_time:.2f}s")
    if cognify_time < 60:
        speedup = 60 / cognify_time
        print(f"  SPEEDUP:          {speedup:.1f}x FASTER")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ollama_speed())
