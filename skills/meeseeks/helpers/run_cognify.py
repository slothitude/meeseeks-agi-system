"""Run Cognee cognify in background"""
import os
import asyncio

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "llama3.2:latest"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDER_PROVIDER"] = "ollama"
os.environ["EMBEDDER_MODEL"] = "nomic-embed-text:latest"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

print("Importing cognee...")
import cognee

async def run_cognify():
    print("Starting cognify (this may take several minutes)...")
    try:
        await cognee.cognify(dataset_name="sloth_rog")
        print("Cognify completed!")
    except Exception as e:
        print(f"Cognify failed: {e}")

asyncio.run(run_cognify())
