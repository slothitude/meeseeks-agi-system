"""
Cognee with Ollama fallback configuration.
Use when z.ai rate limits hit.
"""

import os

# Ollama local configuration (no rate limits!)
def configure_ollama():
    """Configure Cognee to use local Ollama."""
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "ollama/phi3:mini"  # LiteLLM needs ollama/ prefix
    os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
    # No API key needed for Ollama
    
    # Keep fastembed for embeddings (works great)
    os.environ["EMBEDDING_PROVIDER"] = "fastembed"
    os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
    os.environ["EMBEDDING_DIMENSIONS"] = "384"
    
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
    
    print("[OK] Configured for Ollama local (no rate limits)")

def configure_zai():
    """Configure Cognee to use z.ai API (faster but rate limited)."""
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
    os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
    os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
    
    os.environ["EMBEDDING_PROVIDER"] = "fastembed"
    os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
    os.environ["EMBEDDING_DIMENSIONS"] = "384"
    
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
    
    print("[OK] Configured for z.ai API (fast but rate limited)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "ollama":
        configure_ollama()
    else:
        configure_zai()
