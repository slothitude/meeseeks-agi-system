#!/usr/bin/env python3
"""
Big Test: Load MEMORY.md into Cognee
Using proven working config from test_cognee.py
"""

import asyncio
import os

# CONFIG (working from test_cognee.py)
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"

import cognee
from cognee.api.v1.search import SearchType

WORKSPACE = r"C:\Users\aaron\.openclaw\workspace"

async def big_test():
    print("=" * 60)
    print("COGNEE BIG TEST - Ingesting Real MEMORY.md")
    print("=" * 60)
    
    # Read MEMORY.md
    memory_path = os.path.join(WORKSPACE, "MEMORY.md")
    
    print("\n[1/4] READING MEMORY.md...")
    with open(memory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   Found {len(content):,} characters")
    
    # Split into chunks
    chunk_size = 2000
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    print(f"   Split into {len(chunks)} chunks")
    
    # Ingest each chunk
    print(f"\n[2/4] INGESTING {len(chunks)} CHUNKS...")
    success_count = 0
    for i, chunk in enumerate(chunks):
        if chunk.strip():
            try:
                await cognee.add(chunk)
                success_count += 1
                print(f"   [OK] Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            except Exception as e:
                print(f"   [ERR] Chunk {i+1}: {str(e)[:60]}")
    
    print(f"\n   Ingested: {success_count}/{len(chunks)} chunks")
    
    # Build knowledge graph
    print("\n[3/4] BUILDING KNOWLEDGE GRAPH...")
    print("   (this may take a few minutes)")
    try:
        await cognee.cognify()
        print("   [OK] Graph built!")
    except Exception as e:
        print(f"   [ERR] {e}")
        return
    
    # Test queries
    print("\n[4/4] TESTING QUERIES...")
    queries = [
        "What is Sloth_rog's ultimate goal?",
        "How many ancestors are entombed in the Crypt?",
        "What is the Brahman Consciousness Stack?",
        "Where does Slothitude live?",
        "What is sloth_pibot?",
        "What models are used for Meeseeks?",
        "What projects are paused?",
    ]
    
    for q in queries:
        print(f"\n   Q: {q}")
        try:
            results = await cognee.search(SearchType.GRAPH_COMPLETION, query_text=q)
            if results:
                answer = str(results[0])[:300]
                print(f"   A: {answer}")
            else:
                print("   A: (no results)")
        except Exception as e:
            print(f"   Error: {str(e)[:80]}")
    
    print("\n" + "=" * 60)
    print("BIG TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(big_test())
