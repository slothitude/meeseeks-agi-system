"""
Batch Cognee Ingestion with Rate Limit Handling
Processes chunks one at a time with delays to avoid rate limits.
"""

import os
import asyncio
import time
import cognee
from cognee.api.v1.search import SearchType

# Configure Cognee
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

DELAY_SECONDS = 30  # Wait between chunks
CHUNK_SIZE = 1500   # Smaller chunks
MAX_RETRIES = 3
RETRY_DELAY = 60    # Wait on rate limit


async def batch_add(text_chunks: list[str], delay: float = DELAY_SECONDS):
    """Add chunks one at a time with delays."""
    results = []
    for i, chunk in enumerate(text_chunks):
        print(f"\n[CHUNK {i+1}/{len(text_chunks)}] Adding {len(chunk)} chars...")
        
        for attempt in range(MAX_RETRIES):
            try:
                await cognee.add(chunk)
                print(f"  [OK] Added successfully")
                results.append(True)
                break
            except Exception as e:
                if "Rate limit" in str(e):
                    print(f"  [RETRY {attempt+1}/{MAX_RETRIES}] Rate limited, waiting {RETRY_DELAY}s...")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    print(f"  [ERR] {e}")
                    results.append(False)
                    break
        
        # Delay between chunks
        if i < len(text_chunks) - 1:
            print(f"  Waiting {delay}s before next chunk...")
            await asyncio.sleep(delay)
    
    return results


async def batch_cognify(delay: float = DELAY_SECONDS):
    """Run cognify with retry on rate limits."""
    print("\n[COGNIFY] Building knowledge graph...")
    
    for attempt in range(MAX_RETRIES):
        try:
            await cognee.cognify()
            print("[OK] Graph built successfully!")
            return True
        except Exception as e:
            if "Rate limit" in str(e):
                print(f"[RETRY {attempt+1}/{MAX_RETRIES}] Rate limited, waiting {RETRY_DELAY}s...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"[ERR] {e}")
                return False
    
    return False


async def main():
    print("=" * 60)
    print("BATCH COGNEE INGESTION")
    print("=" * 60)
    
    # Read MEMORY.md
    memory_path = r"C:\Users\aaron\.openclaw\workspace\MEMORY.md"
    print(f"\n[READ] {memory_path}")
    
    with open(memory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"  {len(content)} chars total")
    
    # Split into chunks
    chunks = []
    for i in range(0, len(content), CHUNK_SIZE):
        chunks.append(content[i:i+CHUNK_SIZE])
    
    print(f"  {len(chunks)} chunks of {CHUNK_SIZE} chars")
    
    # Add chunks with delays
    add_results = await batch_add(chunks)
    successful = sum(add_results)
    print(f"\n[ADD] {successful}/{len(chunks)} chunks added")
    
    if successful == 0:
        print("[ABORT] No chunks added, skipping cognify")
        return
    
    # Build graph with retry
    cognify_ok = await batch_cognify()
    
    if not cognify_ok:
        print("\n[PARTIAL] Graph may be incomplete due to rate limits")
        return
    
    # Test query
    print("\n[QUERY] Testing search...")
    try:
        result = await cognee.search(
            query_text="What is Sloth_rog's ultimate goal?",
            search_type=SearchType.GRAPH_COMPLETION
        )
        print(f"  [OK] Got response")
        print(f"  {result[:500]}..." if len(str(result)) > 500 else f"  {result}")
    except Exception as e:
        print(f"  [ERR] {e}")
    
    print("\n" + "=" * 60)
    print("BATCH INGESTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
