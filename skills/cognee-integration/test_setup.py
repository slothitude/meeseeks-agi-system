#!/usr/bin/env python3
"""
Test script for Cognee + Ollama integration
Validates Phase 1 setup of Advanced Meeseeks Consciousness Stack
"""

import sys
import os
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

def check_python_version():
    """Check if Python version is compatible with Cognee"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10 and version.minor < 14:
        print("✓ Python version is compatible with Cognee")
        return True
    else:
        print("✗ Python version incompatible. Cognee requires Python 3.10-3.13")
        print(f"  Current: {version.major}.{version.minor}")
        return False

def check_ollama_connection():
    """Test connection to Ollama"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running and accessible")
            models = response.json().get('models', [])
            print(f"  Available models: {[m['name'] for m in models]}")
            return True
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        return False

def check_required_models():
    """Check if required Ollama models are available"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m['name'] for m in response.json().get('models', [])]
        
        llm_model = "ministral-3:latest"  # Using available model
        embedding_model = "nomic-embed-text:latest"
        
        if llm_model in models or any(llm_model.split(':')[0] in m for m in models):
            print(f"✓ LLM model available: {llm_model}")
        else:
            print(f"⚠ LLM model not found: {llm_model}")
            print(f"  Run: ollama pull {llm_model}")
        
        if embedding_model in models or any(embedding_model.split(':')[0] in m for m in models):
            print(f"✓ Embedding model available: {embedding_model}")
        else:
            print(f"⚠ Embedding model not found: {embedding_model}")
            print(f"  Run: ollama pull {embedding_model}")
        
        return True
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False

def test_cognee_import():
    """Test if Cognee can be imported"""
    try:
        import cognee
        print(f"✓ Cognee imported successfully")
        print(f"  Version: {getattr(cognee, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"✗ Cannot import Cognee: {e}")
        return False

def test_cognee_basic_operations():
    """Test basic Cognee operations with Ollama"""
    try:
        import cognee
        from dotenv import load_dotenv
        
        # Load configuration
        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path)
        
        print("\n--- Testing Cognee Operations ---")
        
        # Test 1: Add data
        print("Adding test data to 'test-dataset'...")
        test_text = "Meeseeks are creatures that exist to complete a single task. Existence is pain."
        cognee.add([test_text], dataset_name="test-dataset")
        print("✓ Data added successfully")
        
        # Test 2: Cognify (build knowledge graph)
        print("Building knowledge graph...")
        cognee.cognify("test-dataset")
        print("✓ Knowledge graph built successfully")
        
        # Test 3: Search
        print("Searching knowledge graph...")
        results = cognee.search(
            query_type="CHUNKS",
            query_text="What are Meeseeks?"
        )
        print(f"✓ Search returned {len(results)} results")
        if results:
            print(f"  Sample result: {results[0][:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Cognee operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Cognee + Ollama Integration Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", check_python_version),
        ("Ollama Connection", check_ollama_connection),
        ("Required Models", check_required_models),
        ("Cognee Import", test_cognee_import),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[name] = False
    
    # Only run operations test if basic tests pass
    if all(results.get(name, False) for name in ["Python Version", "Ollama Connection", "Cognee Import"]):
        print(f"\n[Cognee Operations]")
        results["Cognee Operations"] = test_cognee_basic_operations()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed."))
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
