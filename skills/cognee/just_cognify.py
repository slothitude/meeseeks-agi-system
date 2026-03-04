"""
Just run cognify on existing data.
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

async def main():
    print("[COGNIFY] Building knowledge graph...")
    try:
        await cognee.cognify()
        print("[OK] Graph built!")
    except Exception as e:
        print(f"[ERR] {e}")
        # Try to get more details
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
