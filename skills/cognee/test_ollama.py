"""
Speed test: Cognee CHUNKS search with text extraction
"""

import os
import asyncio
import time

# Configure Cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# z.ai API for LLM
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Fastembed local embeddings
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"
os.environ["HUGGINGFACE_TOKENIZER"] = "BAAI/bge-small-en-v1.5"

import cognee
from cognee.modules.search.types.SearchType import SearchType

async def main():
    print("[TEST] Cognee CHUNKS Search - Text Content")
    print("="*50)
    
    query = "What is Sloth_rog's ultimate goal?"
    print(f"[Q] {query}")
    
    start = time.time()
    result = await cognee.search(
        query_text=query,
        query_type=SearchType.CHUNKS,
        top_k=3
    )
    elapsed = time.time() - start
    print(f"[OK] {elapsed:.2f}s - {len(result)} chunks\n")
    
    for i, chunk in enumerate(result):
        print(f"--- Chunk {i+1} ---")
        # Try to extract text from the chunk object
        if hasattr(chunk, 'text'):
            print(chunk.text[:500])
        elif isinstance(chunk, dict):
            # Print the dict keys to understand structure
            print(f"Keys: {list(chunk.keys())}")
            if 'text' in chunk:
                print(chunk['text'][:500])
            elif 'content' in chunk:
                print(chunk['content'][:500])
            else:
                print(f"Full chunk: {chunk}")
        else:
            print(f"Type: {type(chunk)}")
            print(str(chunk)[:500])
        print()

if __name__ == "__main__":
    asyncio.run(main())
