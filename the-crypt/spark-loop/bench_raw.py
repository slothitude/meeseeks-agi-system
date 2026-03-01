#!/usr/bin/env python3
"""
Quick benchmark of ULTRA CRYPT raw search speed (no embedding call)
"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ultra_crypt import UltraCrypt

crypt = UltraCrypt()

# Pre-compute a query embedding
query_emb = np.random.randn(768).astype(np.float16)
query_emb = query_emb / (np.linalg.norm(query_emb) + 1e-8)

# Benchmark raw search (no Ollama call)
n = 10000

start = time.time()
for _ in range(n):
    # Simulate the search computation
    similarities = np.dot(crypt.embeddings, query_emb)
    top_indices = np.argsort(similarities)[-5:][::-1]
elapsed = time.time() - start

print(f"\nRAW SEARCH BENCHMARK (no Ollama)")
print("=" * 50)
print(f"Queries: {n}")
print(f"Total time: {elapsed*1000:.1f}ms")
print(f"Average: {elapsed*1000/n:.4f}ms per query")
print(f"Rate: {n/elapsed:.0f} queries/second")
print(f"\nWith {len(crypt.index)} ancestors:")
print(f"  - Per-query similarity computation: {elapsed*1000/n:.4f}ms")
print(f"  - Memory usage: {crypt.embeddings.nbytes / 1024:.2f} KB")
