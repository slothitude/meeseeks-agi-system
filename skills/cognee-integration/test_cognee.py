#!/usr/bin/env python3
"""Quick test to verify Cognee + Ollama integration"""

import asyncio
import os
import sys

# Load environment
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("LLM_MODEL", "phi3:mini")
os.environ.setdefault("LLM_ENDPOINT", "http://localhost:11434")
os.environ.setdefault("LLM_API_KEY", "ollama")  # Dummy key for local Ollama
os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
os.environ.setdefault("EMBEDDING_MODEL", "nomic-embed-text:latest")
os.environ.setdefault("EMBEDDING_ENDPOINT", "http://localhost:11434")
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")

import cognee

async def test_cognee():
    print("🧪 Testing Cognee + Ollama integration...")
    
    # Test 1: Check Cognee version
    print(f"✅ Cognee version: {cognee.__version__}")
    
    # Test 2: Add a test document
    print("\n📝 Adding test document...")
    test_text = """
    Meeseeks Worker: coder_001
    Task: Fix authentication bug in API
    Outcome: SUCCESS
    Patterns Used: Test Incrementally, Understand Before Implementing
    Bloodline: coder
    Key Insight: The bug was in token validation logic. Added unit tests first.
    """
    
    try:
        await cognee.add(test_text, dataset="test-ancestors")
        print("✅ Document added successfully")
    except Exception as e:
        print(f"❌ Failed to add document: {e}")
        return False
    
    # Test 3: Cognify (build knowledge graph)
    print("\n🔄 Building knowledge graph...")
    try:
        await cognee.cognify("test-ancestors")
        print("✅ Knowledge graph built")
    except Exception as e:
        print(f"❌ Failed to cognify: {e}")
        return False
    
    # Test 4: Search
    print("\n🔍 Searching knowledge graph...")
    try:
        results = await cognee.search(
            query_text="What patterns help with coding tasks?",
            query_type="CHUNKS",
            datasets=["test-ancestors"]
        )
        print(f"✅ Search returned results: {len(results) if results else 0}")
        if results:
            print(f"   Sample: {str(results[0])[:200]}...")
    except Exception as e:
        print(f"❌ Failed to search: {e}")
        return False
    
    print("\n🎉 All tests passed! Cognee + Ollama integration working!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_cognee())
    sys.exit(0 if success else 1)
