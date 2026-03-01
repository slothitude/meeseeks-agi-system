#!/usr/bin/env python3
"""
MEESERE FAST CRYPT - High-Performance Vector Memory

The FASTEST ancestor memory system:
- NumPy binary format for embeddings (10x faster than JSON)
- Memory-mapped files (instant load, no RAM copy)
- Optimized cosine similarity with vectorization
- LRU cache for repeated queries
- Async batch embedding

Performance targets:
- Embed 1000 ancestors: < 10 seconds
- Similarity search: < 1ms
- Memory usage: ~4MB per 1000 ancestors (768-dim vectors)
"""

import json
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import requests

# Optional async support
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
CRYPT_DIR = Path(__file__).parent.parent
ANCESTORS_DIR = CRYPT_DIR / "ancestors"
FAST_CRYPT_DIR = CRYPT_DIR / "fast-crypt"

# Ensure fast-crypt directory exists
FAST_CRYPT_DIR.mkdir(parents=True, exist_ok=True)

# Binary file paths
EMBEDDINGS_NPY = FAST_CRYPT_DIR / "embeddings.npy"       # (N, 768) float32 matrix
METADATA_NPY = FAST_CRYPT_DIR / "metadata.npy"           # Structured array
INDEX_NPY = FAST_CRYPT_DIR / "index.npy"                 # ancestor_id -> row mapping
META_JSON = FAST_CRYPT_DIR / "meta.json"                 # Misc metadata

# Ollama config
OLLAMA_API = "http://localhost:11434/api"
EMBEDDING_DIM = 768  # nomic-embed-text dimension
BATCH_SIZE = 10      # Parallel embeddings


@dataclass
class AncestorMeta:
    """Lightweight ancestor metadata."""
    ancestor_id: str
    task: str          # Truncated to 200 chars
    traits: str        # JSON string of traits list
    bloodline: str
    success: bool
    embedded_at: str


class FastCrypt:
    """
    High-performance ancestor memory system.

    Uses:
    - NumPy binary format (10x faster than JSON)
    - Memory-mapped files (instant load)
    - Vectorized similarity (parallel computation)
    - LRU cache for hot queries
    """

    def __init__(self):
        self.embeddings: Optional[np.ndarray] = None  # (N, 768) float32
        self.metadata: Optional[np.ndarray] = None    # Structured array
        self.index: Optional[Dict[str, int]] = None   # ancestor_id -> row
        self._mmap_embeddings = None
        self._load()

    def _load(self):
        """Load embeddings from binary files."""
        if EMBEDDINGS_NPY.exists():
            # Memory-map for instant load without copying to RAM
            self._mmap_embeddings = np.load(str(EMBEDDINGS_NPY), mmap_mode='r')
            self.embeddings = self._mmap_embeddings

        if METADATA_NPY.exists():
            self.metadata = np.load(str(METADATA_NPY), allow_pickle=True)

        if INDEX_NPY.exists():
            index_data = np.load(str(INDEX_NPY), allow_pickle=True)
            self.index = dict(index_data)

    def _save(self):
        """Save embeddings to binary files."""
        if self.embeddings is not None:
            np.save(str(EMBEDDINGS_NPY), self.embeddings)

        if self.metadata is not None:
            np.save(str(METADATA_NPY), self.metadata)

        if self.index is not None:
            np.save(str(INDEX_NPY), np.array(list(self.index.items())))

        # Update meta
        with open(META_JSON, 'w', encoding='utf-8') as f:
            json.dump({
                "total_ancestors": len(self.index) if self.index else 0,
                "embedding_dim": EMBEDDING_DIM,
                "last_updated": datetime.now().isoformat()
            }, f)

    def get_embedding_async(self, text: str) -> np.ndarray:
        """Get embedding from Ollama (blocking, for simplicity)."""
        try:
            response = requests.post(
                f"{OLLAMA_API}/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30
            )
            if response.status_code == 200:
                return np.array(response.json().get("embedding", []), dtype=np.float32)
        except Exception as e:
            print(f"Embedding error: {e}")
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)

    async def get_embedding_batch_async(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts in parallel."""
        if not HAS_AIOHTTP:
            # Fallback to sequential
            embeddings = [self.get_embedding_async(t) for t in texts]
            return np.array(embeddings, dtype=np.float32)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for text in texts:
                task = self._get_single_embedding(session, text)
                tasks.append(task)

            embeddings = await asyncio.gather(*tasks)
            return np.array(embeddings, dtype=np.float32)

    async def _get_single_embedding(self, session: aiohttp.ClientSession, text: str) -> np.ndarray:
        """Get a single embedding."""
        try:
            async with session.post(
                f"{OLLAMA_API}/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return np.array(data.get("embedding", []), dtype=np.float32)
        except:
            pass
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)

    def parse_ancestor(self, filepath: Path) -> Tuple[str, str, List[str], str, bool]:
        """Parse ancestor file. Returns (id, task, traits, bloodline, success)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        ancestor_id = filepath.stem
        task = ""
        traits = []
        bloodline = "unknown"
        success = False

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("## Task"):
                current_section = "task"
            elif line.startswith("## Approach"):
                current_section = None
            elif line.startswith("## Outcome"):
                current_section = "outcome"
            elif line.startswith("## Patterns Discovered"):
                current_section = "patterns"
            elif line.startswith("## Bloodline"):
                current_section = "bloodline"
            elif line.startswith("## ") or line.startswith("---"):
                if current_section == "bloodline":
                    current_section = None
            elif line and current_section:
                if current_section == "task":
                    task += " " + line
                elif current_section == "outcome":
                    if "success" in line.lower():
                        success = True
                elif current_section == "patterns":
                    if line.startswith("- "):
                        traits.append(line[2:])
                elif current_section == "bloodline":
                    if bloodline == "unknown":
                        bloodline = line.strip()

        return ancestor_id, task.strip()[:200], traits, bloodline, success

    def embed_all_ancestors(self, use_async: bool = True) -> int:
        """
        Embed all ancestors in the Crypt.

        Uses async batch processing for speed.
        Returns count of new embeddings.
        """
        ancestor_files = list(ANCESTORS_DIR.glob("*.md"))

        # Filter out already embedded
        if self.index:
            new_files = [f for f in ancestor_files if f.stem not in self.index]
        else:
            new_files = ancestor_files

        if not new_files:
            print("No new ancestors to embed.")
            return 0

        print(f"Embedding {len(new_files)} ancestors...")

        # Parse all files
        parsed = []
        for f in new_files:
            aid, task, traits, bloodline, success = self.parse_ancestor(f)
            embed_text = f"Task: {task}\nPatterns: {'. '.join(traits[:5])}\nBloodline: {bloodline}"
            parsed.append((aid, embed_text, task, traits, bloodline, success))

        # Batch embed
        if use_async and len(parsed) > 1:
            texts = [p[1] for p in parsed]
            embeddings = asyncio.run(self.get_embedding_batch_async(texts))
        else:
            embeddings = []
            for i, (aid, text, task, traits, bloodline, success) in enumerate(parsed):
                emb = self.get_embedding_async(text)
                embeddings.append(emb)
                print(f"  [{i+1}/{len(parsed)}] {aid[:20]}...")
            embeddings = np.array(embeddings, dtype=np.float32)

        # Create metadata array
        new_metadata = np.array([
            (p[0], p[2], json.dumps(p[3]), p[4], p[5], datetime.now().isoformat())
            for p in parsed
        ], dtype=[
            ('ancestor_id', 'U50'),
            ('task', 'U200'),
            ('traits', 'U500'),
            ('bloodline', 'U30'),
            ('success', '?'),
            ('embedded_at', 'U30')
        ])

        # Append to existing
        if self.embeddings is not None and len(self.embeddings) > 0:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.metadata = np.concatenate([self.metadata, new_metadata])
        else:
            self.embeddings = embeddings
            self.metadata = new_metadata

        # Update index
        if self.index is None:
            self.index = {}

        start_idx = len(self.index)
        for i, p in enumerate(parsed):
            self.index[p[0]] = start_idx + i

        # Save
        self._save()

        print(f"✓ Embedded {len(parsed)} ancestors")
        print(f"✓ Total: {len(self.index)} ancestors")

        return len(parsed)

    @lru_cache(maxsize=1000)
    def find_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float, str, List[str]]]:
        """
        Find ancestors similar to query.

        CACHED for repeated queries.
        Returns: [(ancestor_id, similarity, task, traits), ...]
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Get query embedding
        query_emb = self.get_embedding_async(query)

        # Vectorized cosine similarity (FAST)
        query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)

        # Normalize all embeddings at once
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8
        normalized = self.embeddings / norms

        # Dot product = cosine similarity (for normalized vectors)
        similarities = np.dot(normalized, query_norm)

        # Top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                ancestor_id = str(meta['ancestor_id'])
                task = str(meta['task'])
                traits = json.loads(str(meta['traits']))
                sim = float(similarities[idx])
                results.append((ancestor_id, sim, task, traits))

        return results

    def get_inheritance(self, task: str, bloodline: str = None, top_k: int = 3) -> str:
        """Get inherited wisdom for a task."""
        similar = self.find_similar(task, top_k=top_k)

        if not similar:
            return ""

        # Filter by bloodline if specified
        if bloodline:
            similar = [s for s in similar if self._get_bloodline(s[0]) == bloodline]

        # Extract traits
        all_traits = []
        ancestor_ids = []
        for aid, sim, task_text, traits in similar:
            all_traits.extend(traits[:2])
            ancestor_ids.append(aid[:12])

        if not all_traits:
            return ""

        unique_traits = list(set(all_traits))[:5]
        ancestors_str = ", ".join(ancestor_ids)

        return f"""
## 🧬 Ancestral Inheritance

Similar ancestors ({ancestors_str}) suggest:

{chr(10).join([f"- {t}" for t in unique_traits])}

🪷 ATMAN OBSERVES: This Meeseeks stands on the shoulders of ancestors.
"""

    def _get_bloodline(self, ancestor_id: str) -> str:
        """Get bloodline for an ancestor."""
        if self.index and ancestor_id in self.index:
            idx = self.index[ancestor_id]
            if idx < len(self.metadata):
                return str(self.metadata[idx]['bloodline'])
        return "unknown"

    def get_status(self) -> Dict:
        """Get system status."""
        return {
            "total_ancestors": len(self.index) if self.index else 0,
            "embedding_dim": EMBEDDING_DIM,
            "memory_mb": self.embeddings.nbytes / (1024 * 1024) if self.embeddings is not None else 0,
            "cache_size": self.find_similar.cache_info().currsize if hasattr(self.find_similar, 'cache_info') else 0,
            "storage": "numpy_binary",
            "ollama_available": self._check_ollama()
        }

    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{OLLAMA_API}/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def benchmark(self, n_queries: int = 100):
        """Benchmark similarity search performance."""
        import random
        import string

        # Generate random queries
        queries = [
            ''.join(random.choices(string.ascii_letters, k=50))
            for _ in range(n_queries)
        ]

        # Warm up
        self.find_similar(queries[0])

        # Benchmark
        start = time.time()
        for q in queries:
            self.find_similar(q)
        elapsed = time.time() - start

        print(f"Benchmark: {n_queries} queries in {elapsed*1000:.1f}ms")
        print(f"Average: {elapsed*1000/n_queries:.2f}ms per query")
        print(f"Rate: {n_queries/elapsed:.0f} queries/second")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fast Crypt - High-Performance Ancestor Memory")
    parser.add_argument("command", choices=["embed", "search", "inherit", "status", "benchmark"])
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--bloodline", help="Bloodline filter")
    parser.add_argument("--task", help="Task for inheritance")
    parser.add_argument("--async", dest="use_async", action="store_true", default=True, help="Use async embedding")
    parser.add_argument("--sync", dest="use_async", action="store_false", help="Use sync embedding")
    parser.add_argument("--n-queries", type=int, default=100, help="Number of queries for benchmark")

    args = parser.parse_args()

    crypt = FastCrypt()

    if args.command == "embed":
        crypt.embed_all_ancestors(use_async=args.use_async)

    elif args.command == "search":
        if not args.query:
            print("Error: --query required")
            sys.exit(1)

        start = time.time()
        similar = crypt.find_similar(args.query)
        elapsed = (time.time() - start) * 1000

        print(f"🔍 Results ({elapsed:.1f}ms):")
        for aid, sim, task, traits in similar:
            print(f"\n{sim:.1%} similar: {aid}")
            print(f"  Task: {task[:60]}...")
            print(f"  Traits: {', '.join(traits[:3])}")

    elif args.command == "inherit":
        if not args.task:
            print("Error: --task required")
            sys.exit(1)

        inheritance = crypt.get_inheritance(args.task, args.bloodline)
        print(inheritance)

    elif args.command == "status":
        status = crypt.get_status()
        print("⚡ FAST CRYPT STATUS")
        print("=" * 50)
        print(f"Ancestors: {status['total_ancestors']}")
        print(f"Embedding Dim: {status['embedding_dim']}")
        print(f"Memory: {status['memory_mb']:.2f} MB")
        print(f"Cache Size: {status['cache_size']}")
        print(f"Storage: {status['storage']}")
        print(f"Ollama: {'Available' if status['ollama_available'] else 'Unavailable'}")

    elif args.command == "benchmark":
        crypt.benchmark(n_queries=args.n_queries)


if __name__ == "__main__":
    main()
