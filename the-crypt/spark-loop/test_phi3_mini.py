#!/usr/bin/env python3
"""Test phi3:mini speed for Mini Meeseeks tasks"""

import requests
import time

OLLAMA_API = "http://localhost:11434/api"

def test_classify():
    """Test classify speed"""
    prompt = """# CLASSIFY (1 word each)
Task: Fix authentication bug in login.py
COMPLEXITY/CATEGORY/CONFIDENCE:"""
    
    start = time.time()
    r = requests.post(f"{OLLAMA_API}/generate", json={
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 20, "temperature": 0.3}
    }, timeout=30)
    elapsed = (time.time() - start) * 1000
    
    print(f"phi3:mini CLASSIFY test:")
    print(f"Response: {r.json().get('response', '')}")
    print(f"Time: {elapsed:.0f}ms")
    print()

def test_fitness():
    """Test fitness evaluation speed"""
    prompt = """# SCORE (0-100)
Task: Fix authentication bug
Result: Added validation and rate limiting
FITNESS/VERDICT:"""
    
    start = time.time()
    r = requests.post(f"{OLLAMA_API}/generate", json={
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 30, "temperature": 0.3}
    }, timeout=30)
    elapsed = (time.time() - start) * 1000
    
    print(f"phi3:mini FITNESS test:")
    print(f"Response: {r.json().get('response', '')}")
    print(f"Time: {elapsed:.0f}ms")
    print()

def test_patterns():
    """Test pattern spotting speed"""
    prompt = """# PATTERNS
Result: Fixed bug by adding validation
PATTERNS/TRAITS:"""
    
    start = time.time()
    r = requests.post(f"{OLLAMA_API}/generate", json={
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 30, "temperature": 0.3}
    }, timeout=30)
    elapsed = (time.time() - start) * 1000
    
    print(f"phi3:mini PATTERNS test:")
    print(f"Response: {r.json().get('response', '')}")
    print(f"Time: {elapsed:.0f}ms")
    print()

if __name__ == "__main__":
    print("Testing phi3:mini for Mini Meeseeks tasks...\n")
    test_classify()
    test_fitness()
    test_patterns()
    print("Done!")
