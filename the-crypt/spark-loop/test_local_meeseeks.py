#!/usr/bin/env python3
"""
Local Meeseeks Tester - Test Meeseeks with Ollama models

Usage:
    python test_local_meeseeks.py "fix this bug" --model tinyllama
    python test_local_meeseeks.py "optimize this code" --model ministral-3
"""

import sys
import requests
import json
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "meeseeks"))
from spawn_meeseeks import spawn_prompt

OLLAMA_API = "http://localhost:11434/api"

def get_available_models():
    """Get list of available Ollama models."""
    try:
        response = requests.get(f"{OLLAMA_API}/tags", timeout=5)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])]
    except:
        pass
    return []

def ollama_generate(model: str, prompt: str, max_tokens: int = 500) -> str:
    """Generate response from Ollama model."""
    try:
        response = requests.post(
            f"{OLLAMA_API}/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"
    return "Error: No response"

def test_meeseeks(task: str, model: str, meeseeks_type: str = "mini"):
    """Test a Meeseeks task with a local model."""
    
    print(f"\n{'='*60}")
    print(f"TESTING: {task}")
    print(f"Model: {model}")
    print(f"Type: {meeseeks_type}")
    print('='*60)
    
    # Generate prompt
    prompt = spawn_prompt(
        purpose=task,
        meeseeks_type=meeseeks_type,
        atman=False  # Keep it simple for small models
    )
    
    # Count tokens (rough estimate)
    prompt_tokens = len(prompt.split())
    print(f"\nPrompt tokens (estimate): {prompt_tokens}")
    
    # Generate
    print("\nGenerating response...")
    start = time.time()
    response = ollama_generate(model, prompt)
    elapsed = time.time() - start
    
    print(f"\nResponse ({elapsed:.1f}s):")
    print("-" * 40)
    print(response[:2000])  # Limit output
    print("-" * 40)
    
    return response

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Meeseeks with local models")
    parser.add_argument("task", nargs="?", default="", help="Task for Meeseeks")
    parser.add_argument("--model", default="tinyllama", help="Ollama model to use")
    parser.add_argument("--type", default="mini", help="Meeseeks type")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        models = get_available_models()
        print("Available models:")
        for m in models:
            print(f"  - {m}")
        return
    
    test_meeseeks(args.task, args.model, args.type)

if __name__ == "__main__":
    main()
