#!/usr/bin/env python3
"""
Cognee Helper for Sloth_rog Memory System
Integrates graph-based memory with the existing file-based system.

REQUIRES: Python 3.10-3.12 (uses venv at skills/cognee/.venv)
RUN WITH: skills/cognee/.venv/Scripts/python.exe cognee_helper.py
OR USE: skills/cognee/run.bat <script.py>

Supports both:
- GRAPH_COMPLETION: Slow but comprehensive LLM-powered answers
- CHUNKS: Fast vector similarity search (no LLM, instant)

LLM: z.ai coding endpoint (glm-4.7-flash)
Embeddings: Fastembed local (BAAI/bge-small-en-v1.5)
"""

import os
import asyncio
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configure cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# z.ai Coding endpoint for LLM (graph extraction)
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Ollama local embeddings (nomic-embed-text)
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"

# Cognee data directory (in The Crypt)
COGNEE_DATA_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/cognee")
os.environ["COGNEE_DATA_DIR"] = str(COGNEE_DATA_DIR)

# Cache for fast repeated queries
QUERY_CACHE_FILE = COGNEE_DATA_DIR / "query_cache.json"
CACHE_TTL_SECONDS = 3600  # 1 hour cache

# Track Cognee availability
_cognee_available: Optional[bool] = None

# Lazy import of cognee (only when needed)
_cognee_module = None
_search_type_enum = None


def _ensure_cognee():
    """Lazy load cognee module."""
    global _cognee_module, _search_type_enum, _cognee_available
    
    if _cognee_module is not None:
        return _cognee_available
    
    try:
        import cognee
        from cognee.api.v1.search import SearchType
        _cognee_module = cognee
        _search_type_enum = SearchType
        _cognee_available = True
        return True
    except ImportError as e:
        print(f"[cognee_helper] Cognee not available: {e}")
        _cognee_available = False
        return False
    except Exception as e:
        print(f"[cognee_helper] Cognee init error: {e}")
        _cognee_available = False
        return False


@dataclass
class WisdomResult:
    """Result from wisdom query."""
    source: str  # "cognee" or "crypt"
    content: str
    relevance: float  # 0.0-1.0
    timestamp: str
    metadata: Dict[str, Any]


def _load_cache() -> Dict[str, Any]:
    """Load query cache from disk."""
    if QUERY_CACHE_FILE.exists():
        try:
            with open(QUERY_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"queries": {}}


def _save_cache(cache: Dict[str, Any]):
    """Save query cache to disk."""
    QUERY_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUERY_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def _get_cached_result(query: str) -> Optional[WisdomResult]:
    """Get cached result if still valid."""
    cache = _load_cache()
    query_key = query.lower().strip()[:100]  # Normalize key
    
    if query_key in cache["queries"]:
        entry = cache["queries"][query_key]
        cached_time = entry.get("timestamp", 0)
        
        if time.time() - cached_time < CACHE_TTL_SECONDS:
            return WisdomResult(
                source=entry.get("source", "cognee"),
                content=entry.get("content", ""),
                relevance=entry.get("relevance", 0.5),
                timestamp=datetime.fromtimestamp(cached_time).isoformat(),
                metadata=entry.get("metadata", {})
            )
    
    return None


def _cache_result(query: str, result: WisdomResult):
    """Cache a query result."""
    cache = _load_cache()
    query_key = query.lower().strip()[:100]
    
    cache["queries"][query_key] = {
        "source": result.source,
        "content": result.content,
        "relevance": result.relevance,
        "timestamp": time.time(),
        "metadata": result.metadata
    }
    
    # Keep cache size manageable
    if len(cache["queries"]) > 1000:
        # Remove oldest entries
        sorted_entries = sorted(
            cache["queries"].items(),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True
        )
        cache["queries"] = dict(sorted_entries[:500])
    
    _save_cache(cache)


async def query_wisdom_chunks(query: str, top_k: int = 3) -> List[WisdomResult]:
    """
    Fast chunk-based search using vector embeddings.
    
    This is the FAST search type - uses vector embeddings directly.
    Returns relevant chunks without LLM processing.
    """
    if not _ensure_cognee():
        return []
    
    try:
        # Cognee 0.5.x API - query_text and query_type
        results = await _cognee_module.search(
            query_text=query,
            query_type=_search_type_enum.CHUNKS,
            top_k=top_k
        )
        
        wisdom_results = []
        if results:
            for i, r in enumerate(results[:top_k]):
                wisdom_results.append(WisdomResult(
                    source="cognee",
                    content=str(r),
                    relevance=1.0 - (i * 0.1),  # Decreasing relevance
                    timestamp=datetime.now().isoformat(),
                    metadata={"search_type": "chunks", "rank": i}
                ))
        
        return wisdom_results
        
    except Exception as e:
        print(f"[cognee_helper] Chunk search error: {e}")
        return []


async def search_graph(query: str) -> Optional[WisdomResult]:
    """
    Slow but comprehensive LLM-powered search.
    
    Uses the full knowledge graph with LLM reasoning.
    Good for complex queries requiring synthesis.
    """
    if not _ensure_cognee():
        return None
    
    try:
        results = await _cognee_module.search(
            query_text=query,
            query_type=_search_type_enum.GRAPH_COMPLETION
        )
        
        if results:
            result = WisdomResult(
                source="cognee",
                content=str(results[0]),
                relevance=0.9,
                timestamp=datetime.now().isoformat(),
                metadata={"search_type": "graph_completion"}
            )
            _cache_result(query, result)
            return result
        
        return None
        
    except Exception as e:
        print(f"[cognee_helper] Graph search error: {e}")
        return None


async def add_memory(text: str, dataset_name: str = "sloth_rog_memory") -> bool:
    """Add a memory to the knowledge graph."""
    if not _ensure_cognee():
        return False
    
    try:
        await _cognee_module.add(text, dataset_name=dataset_name)
        return True
    except Exception as e:
        print(f"[cognee_helper] Error adding memory: {e}")
        return False


async def process_memories(dataset_name: str = "sloth_rog_memory") -> bool:
    """Process added memories into the knowledge graph."""
    if not _ensure_cognee():
        return False
    
    try:
        await _cognee_module.cognify(dataset_name=dataset_name)
        return True
    except Exception as e:
        print(f"[cognee_helper] Error processing memories: {e}")
        return False


async def search_chunks(query: str, top_k: int = 5) -> List[WisdomResult]:
    """
    Fast chunk-based search (no LLM, vector similarity only).
    
    This is the FAST search type - uses vector embeddings directly.
    Returns relevant chunks without LLM processing.
    """
    if not _ensure_cognee():
        return []


async def query_wisdom_fast(
    task_description: str,
    use_cache: bool = True,
    top_k: int = 3
) -> List[WisdomResult]:
    """
    Fast wisdom query for Meeseeks inheritance.
    
    Priority:
    1. Cache (if use_cache and valid)
    2. Cognee CHUNKS search (fast vector search)
    
    Args:
        task_description: Task to find relevant wisdom for
        use_cache: Whether to use cached results
        top_k: Max results to return
    
    Returns:
        List of WisdomResult objects from Cognee
    """
    # Check cache first
    if use_cache:
        cached = _get_cached_result(task_description)
        if cached:
            return [cached]
    
    # Query Cognee
    results = await query_wisdom_chunks(task_description, top_k=top_k)
    
    # Cache best result
    if results and use_cache:
        _cache_result(task_description, results[0])
    
    return results


async def add_meeseeks_wisdom(
    task: str,
    outcome: str,
    patterns: List[str],
    lessons: List[str]
) -> bool:
    """Add a Meeseeks completion to the wisdom graph."""
    memory_text = f"""
    Meeseeks Task: {task}
    Outcome: {outcome}
    Patterns Used: {', '.join(patterns)}
    Lessons Learned: {', '.join(lessons)}
    """
    return await add_memory(memory_text, dataset_name="meeseeks_wisdom")


async def get_relevant_wisdom(task_description: str) -> str:
    """Get relevant wisdom from past Meeseeks for a new task."""
    results = await query_wisdom_fast(task_description)
    if results:
        return results[0].content
    return ""


def is_cognee_available() -> bool:
    """Check if Cognee is available and configured."""
    return _ensure_cognee()


def get_graph_stats() -> Dict[str, Any]:
    """Get statistics about the knowledge graph."""
    stats = {
        "available": _ensure_cognee(),
        "data_dir": str(COGNEE_DATA_DIR),
        "cache_file": str(QUERY_CACHE_FILE),
        "cache_exists": QUERY_CACHE_FILE.exists()
    }
    
    # Check for database file
    db_file = COGNEE_DATA_DIR / "databases" / "cognee_db"
    stats["db_exists"] = db_file.exists()
    if db_file.exists():
        stats["db_size_mb"] = db_file.stat().st_size / (1024 * 1024)
    
    return stats


def run_async(coro):
    """Helper to run async functions from sync code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop if current is running
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# Synchronous wrappers for convenience
def query_wisdom_sync(task_description: str) -> List[WisdomResult]:
    """Synchronous wrapper for query_wisdom_fast."""
    return run_async(query_wisdom_fast(task_description))


def get_wisdom_text(task_description: str) -> str:
    """Get wisdom as plain text string."""
    results = query_wisdom_sync(task_description)
    if results:
        return "\n\n".join(r.content for r in results)
    return ""


if __name__ == "__main__":
    # Quick test
    async def test():
        print("=" * 60)
        print("COGNEE HELPER TEST")
        print("=" * 60)
        
        # Check availability
        print(f"\n[1] Cognee available: {is_cognee_available()}")
        
        # Get stats
        stats = get_graph_stats()
        print(f"\n[2] Graph stats:")
        for k, v in stats.items():
            print(f"    {k}: {v}")
        
        # Test fast query
        print("\n[3] Testing fast wisdom query...")
        results = await query_wisdom_fast("What is Sloth_rog's ultimate goal?")
        for r in results:
            print(f"    [{r.source}] (relevance: {r.relevance:.2f})")
            print(f"    {r.content[:200]}...")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
    
    run_async(test())
