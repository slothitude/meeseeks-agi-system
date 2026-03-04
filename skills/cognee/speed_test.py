"""
Cognee Speed Test: z.ai API vs Ollama Local
Compare query speeds for the knowledge graph.
"""

import os
import asyncio
import time

# Test queries
QUERIES = [
    "What is Sloth_rog's ultimate goal?",
    "How many ancestors are in the Crypt?",
    "What is the Brahman Consciousness Stack?",
]

def configure_zai():
    """Configure for z.ai API (fast but rate limited)."""
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
    os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
    os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
    os.environ["EMBEDDING_PROVIDER"] = "fastembed"
    os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
    os.environ["EMBEDDING_DIMENSIONS"] = "384"
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
    print("[CONFIG] z.ai API (glm-4.7-flash)")

def configure_ollama():
    """Configure for Ollama local (no rate limits)."""
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "ollama/phi3:mini"
    os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
    os.environ["EMBEDDING_PROVIDER"] = "fastembed"
    os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
    os.environ["EMBEDDING_DIMENSIONS"] = "384"
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
    print("[CONFIG] Ollama local (phi3:mini)")

async def test_query_speed(config_name: str):
    """Test query speed with current config."""
    import cognee
    
    print(f"\n{'='*60}")
    print(f"TESTING: {config_name}")
    print('='*60)
    
    results = []
    for query in QUERIES:
        print(f"\n[Q] {query}")
        start = time.time()
        try:
            result = await cognee.search(query_text=query)
            elapsed = time.time() - start
            print(f"  [OK] {elapsed:.2f}s")
            if result:
                # Show first 100 chars of result
                r_str = str(result[0])[:100] if isinstance(result, list) else str(result)[:100]
                print(f"  -> {r_str}...")
            results.append(elapsed)
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [ERR] {elapsed:.2f}s - {e}")
            results.append(elapsed)
    
    avg = sum(results) / len(results) if results else 0
    print(f"\n[AVG] {avg:.2f}s per query")
    return avg

async def main():
    print("="*60)
    print("COGNEE SPEED TEST")
    print("="*60)
    
    # Test 1: z.ai API
    configure_zai()
    zai_avg = await test_query_speed("z.ai API")
    
    # Wait a bit
    print("\n[PAUSE] Waiting 5s before Ollama test...")
    await asyncio.sleep(5)
    
    # Test 2: Ollama local
    configure_ollama()
    ollama_avg = await test_query_speed("Ollama Local")
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"z.ai API:    {zai_avg:.2f}s average")
    print(f"Ollama:      {ollama_avg:.2f}s average")
    
    if zai_avg < ollama_avg:
        print(f"\n[WINNER] z.ai API is {ollama_avg/zai_avg:.1f}x faster")
    else:
        print(f"\n[WINNER] Ollama is {zai_avg/ollama_avg:.1f}x faster")
    
    print("\nNOTE: Ollama has no rate limits, z.ai does.")

if __name__ == "__main__":
    asyncio.run(main())
