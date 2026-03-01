#!/usr/bin/env python3
"""
MEESERE ULTRA CRYPT - Maximum Performance Vector Memory

No external dependencies beyond NumPy. Pure optimization.

Optimizations:
1. Pre-normalized embeddings (no division at query time)
2. Float16 storage (2x smaller, 2x faster)
3. Batch matrix multiplication
4. Memory-mapped for instant load
5. Inverted index for bloodline filtering
6. Query caching with TTL

Performance targets:
- Load: < 1ms
- Search: < 0.5ms
- Memory: ~2MB per 1000 ancestors
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
import requests
import hashlib

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
CRYPT_DIR = Path(__file__).parent.parent
ANCESTORS_DIR = CRYPT_DIR / "ancestors"
ULTRA_CRYPT_DIR = CRYPT_DIR / "ultra-crypt"

# Ensure directory exists
ULTRA_CRYPT_DIR.mkdir(parents=True, exist_ok=True)

# Binary files
EMBEDDINGS_NPY = ULTRA_CRYPT_DIR / "embeddings.npy"       # (N, 768) float16 - PRE-NORMALIZED
METADATA_MSGPACK = ULTRA_CRYPT_DIR / "metadata.bin"       # Msgpack compressed
INDEX_JSON = ULTRA_CRYPT_DIR / "index.json"               # ancestor_id -> row
BLOODLINE_INDEX_JSON = ULTRA_CRYPT_DIR / "bloodline_index.json"  # bloodline -> [row indices]
META_JSON = ULTRA_CRYPT_DIR / "meta.json"

# Ollama config
OLLAMA_API = "http://localhost:11434/api"
EMBEDDING_DIM = 768


class UltraCrypt:
    """
    Maximum performance ancestor memory.

    Key optimizations:
    1. Pre-normalized float16 embeddings
    2. Bloodline inverted index
    3. Zero-copy memory mapping
    4. Cached query embeddings
    """

    def __init__(self):
        self.embeddings: Optional[np.ndarray] = None  # (N, 768) float16, PRE-NORMALIZED
        self.index: Dict[str, int] = {}                # ancestor_id -> row
        self.bloodline_index: Dict[str, List[int]] = {}  # bloodline -> [rows]
        self.metadata: List[Dict] = []                 # List of metadata dicts
        self._mmap = None
        self._load()

    def _load(self):
        """Load from disk with memory mapping."""
        if EMBEDDINGS_NPY.exists():
            # Memory map for zero-copy load
            self._mmap = np.load(str(EMBEDDINGS_NPY), mmap_mode='r')
            self.embeddings = self._mmap

        if INDEX_JSON.exists():
            with open(INDEX_JSON, 'r', encoding='utf-8') as f:
                self.index = json.load(f)

        if BLOODLINE_INDEX_JSON.exists():
            with open(BLOODLINE_INDEX_JSON, 'r', encoding='utf-8') as f:
                self.bloodline_index = json.load(f)

        if METADATA_MSGPACK.exists():
            # Try msgpack, fallback to JSON
            try:
                import msgpack
                with open(METADATA_MSGPACK, 'rb') as f:
                    self.metadata = msgpack.unpack(f, raw=False)
            except:
                # Fallback to JSON
                with open(ULTRA_CRYPT_DIR / "metadata.json", 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
        elif (ULTRA_CRYPT_DIR / "metadata.json").exists():
            with open(ULTRA_CRYPT_DIR / "metadata.json", 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

    def _save(self):
        """Save to disk."""
        if self.embeddings is not None:
            np.save(str(EMBEDDINGS_NPY), self.embeddings)

        with open(INDEX_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.index, f)

        with open(BLOODLINE_INDEX_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.bloodline_index, f)

        # Try msgpack for smaller size
        try:
            import msgpack
            with open(METADATA_MSGPACK, 'wb') as f:
                msgpack.pack(self.metadata, f)
        except:
            # Fallback to JSON
            with open(ULTRA_CRYPT_DIR / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f)

        with open(META_JSON, 'w', encoding='utf-8') as f:
            json.dump({
                "total_ancestors": len(self.index),
                "embedding_dim": EMBEDDING_DIM,
                "storage_type": "float16_normalized",
                "last_updated": datetime.now().isoformat()
            }, f)

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Ollama."""
        try:
            response = requests.post(
                f"{OLLAMA_API}/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30
            )
            if response.status_code == 200:
                emb = np.array(response.json().get("embedding", []), dtype=np.float32)
                # Normalize immediately
                norm = np.linalg.norm(emb) + 1e-8
                return (emb / norm).astype(np.float16)
        except Exception as e:
            print(f"Embedding error: {e}")
        return np.zeros(EMBEDDING_DIM, dtype=np.float16)

    def parse_ancestor(self, filepath: Path) -> Tuple[str, str, List[str], str, bool]:
        """Parse ancestor file."""
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

    def embed_all(self) -> int:
        """Embed all ancestors with optimizations."""
        ancestor_files = list(ANCESTORS_DIR.glob("*.md"))

        # Filter already embedded
        new_files = [f for f in ancestor_files if f.stem not in self.index]

        if not new_files:
            print("No new ancestors to embed.")
            return 0

        print(f"Embedding {len(new_files)} ancestors...")

        # Parse all
        parsed = []
        for f in new_files:
            aid, task, traits, bloodline, success = self.parse_ancestor(f)
            embed_text = f"Task: {task}\nPatterns: {'. '.join(traits[:5])}\nBloodline: {bloodline}"
            parsed.append((aid, embed_text, task, traits, bloodline, success))

        # Batch embed with progress
        embeddings = []
        for i, (aid, text, task, traits, bloodline, success) in enumerate(parsed):
            emb = self.get_embedding(text)
            embeddings.append(emb)
            print(f"  [{i+1}/{len(parsed)}] {aid[:30]}...")

        embeddings = np.array(embeddings, dtype=np.float16)

        # Build metadata
        new_metadata = [
            {
                "id": p[0],
                "task": p[2],
                "traits": p[3],
                "bloodline": p[4],
                "success": p[5]
            }
            for p in parsed
        ]

        # Append to existing
        if self.embeddings is not None and len(self.embeddings) > 0:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        else:
            self.embeddings = embeddings

        self.metadata.extend(new_metadata)

        # Update indices
        start_idx = len(self.index)
        for i, p in enumerate(parsed):
            self.index[p[0]] = start_idx + i

            # Bloodline index
            bl = p[4]
            if bl not in self.bloodline_index:
                self.bloodline_index[bl] = []
            self.bloodline_index[bl].append(start_idx + i)

        self._save()

        print(f"✓ Embedded {len(parsed)} ancestors")
        print(f"✓ Total: {len(self.index)} ancestors")

        return len(parsed)

    def search(self, query: str, top_k: int = 5, bloodline: str = None) -> List[Tuple[str, float, str, List[str]]]:
        """
        Ultra-fast similarity search.

        Since embeddings are pre-normalized, cosine = dot product.
        Single matrix multiplication for all similarities.
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Get query embedding (normalized)
        query_emb = self.get_embedding(query)

        # Filter by bloodline if specified
        if bloodline and bloodline in self.bloodline_index:
            indices = np.array(self.bloodline_index[bloodline])
            search_embeddings = self.embeddings[indices]
        else:
            indices = np.arange(len(self.embeddings))
            search_embeddings = self.embeddings

        # Dot product = cosine similarity (pre-normalized)
        similarities = np.dot(search_embeddings, query_emb)

        # Top-k
        top_local_indices = np.argsort(similarities)[-top_k:][::-1]
        top_indices = indices[top_local_indices]

        results = []
        for idx in top_indices:
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append((
                    meta["id"],
                    float(similarities[top_local_indices[np.where(indices == idx)[0][0]]]) if bloodline else float(similarities[np.where(top_indices == idx)[0][0]]),
                    meta["task"],
                    meta["traits"]
                ))

        return results

    @lru_cache(maxsize=500)
    def get_inheritance(self, task_hash: str, task: str, bloodline: str = None) -> str:
        """Get inherited wisdom (cached by task hash)."""
        similar = self.search(task, top_k=3, bloodline=bloodline)

        if not similar:
            return ""

        all_traits = []
        ancestor_ids = []
        for aid, sim, task_text, traits in similar:
            all_traits.extend(traits[:2])
            ancestor_ids.append(aid[:12])

        unique_traits = list(set(all_traits))[:5]
        ancestors_str = ", ".join(ancestor_ids)

        return f"""
## 🧬 Ancestral Inheritance

Similar ancestors ({ancestors_str}) suggest:

{chr(10).join([f"- {t}" for t in unique_traits])}

🪷 ATMAN OBSERVES: This Meeseeks stands on the shoulders of ancestors.
"""

    def get_inheritance_for_task(self, task: str, bloodline: str = None) -> str:
        """Get inheritance (computes hash for caching)."""
        task_hash = hashlib.md5((task + (bloodline or "")).encode()).hexdigest()
        return self.get_inheritance(task_hash, task, bloodline)

    def get_status(self) -> Dict:
        """Get system status."""
        return {
            "total_ancestors": len(self.index),
            "embedding_dim": EMBEDDING_DIM,
            "memory_mb": self.embeddings.nbytes / (1024 * 1024) if self.embeddings is not None else 0,
            "storage_type": "float16_normalized",
            "bloodlines": list(self.bloodline_index.keys()),
            "cache_info": str(self.get_inheritance.cache_info()) if hasattr(self.get_inheritance, 'cache_info') else "N/A",
            "ollama_available": self._check_ollama()
        }

    def _check_ollama(self) -> bool:
        """Check Ollama availability."""
        try:
            response = requests.get(f"{OLLAMA_API}/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def benchmark(self, n_queries: int = 1000):
        """Benchmark search performance."""
        import random
        import string

        queries = [
            ''.join(random.choices(string.ascii_letters + ' ', k=50))
            for _ in range(n_queries)
        ]

        # Warm up
        self.search(queries[0])

        # Benchmark
        start = time.time()
        for q in queries:
            self.search(q)
        elapsed = time.time() - start

        print(f"\n⚡ BENCHMARK RESULTS")
        print("=" * 50)
        print(f"Queries: {n_queries}")
        print(f"Total time: {elapsed*1000:.1f}ms")
        print(f"Average: {elapsed*1000/n_queries:.3f}ms per query")
        print(f"Rate: {n_queries/elapsed:.0f} queries/second")

    def migrate_from_fast_crypt(self):
        """Migrate from fast-crypt format."""
        old_embeddings = CRYPT_DIR / "fast-crypt" / "embeddings.npy"
        old_metadata = CRYPT_DIR / "fast-crypt" / "metadata.npy"
        old_index = CRYPT_DIR / "fast-crypt" / "index.npy"

        if not old_embeddings.exists():
            print("No fast-crypt data to migrate.")
            return

        print("Migrating from fast-crypt...")

        # Load old data
        old_emb = np.load(str(old_embeddings))
        old_meta = np.load(str(old_metadata), allow_pickle=True)
        old_idx = dict(np.load(str(old_index), allow_pickle=True))

        # Convert to float16 and normalize
        norms = np.linalg.norm(old_emb, axis=1, keepdims=True) + 1e-8
        self.embeddings = (old_emb / norms).astype(np.float16)

        # Convert metadata
        self.metadata = []
        for m in old_meta:
            self.metadata.append({
                "id": str(m['ancestor_id']),
                "task": str(m['task']),
                "traits": json.loads(str(m['traits'])),
                "bloodline": str(m['bloodline']),
                "success": bool(m['success'])
            })

        # Copy index
        self.index = old_idx

        # Build bloodline index
        self.bloodline_index = {}
        for i, m in enumerate(self.metadata):
            bl = m['bloodline']
            if bl not in self.bloodline_index:
                self.bloodline_index[bl] = []
            self.bloodline_index[bl].append(i)

        self._save()
        print(f"✓ Migrated {len(self.index)} ancestors")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ultra Crypt - Maximum Performance")
    parser.add_argument("command", choices=["embed", "search", "inherit", "status", "benchmark", "migrate"])
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--bloodline", help="Bloodline filter")
    parser.add_argument("--task", help="Task for inheritance")
    parser.add_argument("--n-queries", type=int, default=1000, help="Benchmark queries")

    args = parser.parse_args()

    crypt = UltraCrypt()

    if args.command == "embed":
        crypt.embed_all()

    elif args.command == "search":
        if not args.query:
            print("Error: --query required")
            sys.exit(1)

        start = time.time()
        results = crypt.search(args.query, bloodline=args.bloodline)
        elapsed = (time.time() - start) * 1000

        print(f"🔍 Results ({elapsed:.2f}ms):")
        for aid, sim, task, traits in results:
            print(f"\n{sim:.1%} similar: {aid}")
            print(f"  Task: {task[:60]}...")
            print(f"  Traits: {', '.join(traits[:3])}")

    elif args.command == "inherit":
        if not args.task:
            print("Error: --task required")
            sys.exit(1)
        print(crypt.get_inheritance_for_task(args.task, args.bloodline))

    elif args.command == "status":
        status = crypt.get_status()
        print("⚡ ULTRA CRYPT STATUS")
        print("=" * 50)
        for k, v in status.items():
            print(f"{k}: {v}")

    elif args.command == "benchmark":
        crypt.benchmark(n_queries=args.n_queries)

    elif args.command == "migrate":
        crypt.migrate_from_fast_crypt()


if __name__ == "__main__":
    main()
