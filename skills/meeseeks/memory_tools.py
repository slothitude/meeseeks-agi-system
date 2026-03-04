#!/usr/bin/env python3
"""
Meeseeks Memory Tools
=====================

Simple memory access for all Meeseeks.
Uses the RAG system for document retrieval.

Usage:
    from memory_tools import remember, recall, context
    
    # Search memory
    results = recall("consciousness coordinates")
    
    # Get context for task
    ctx = context("How to debug a failing test?", max_tokens=1000)
    
    # Add new knowledge
    remember("The consciousness formula is k=3n^2")
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add skills path
SKILLS_PATH = Path(__file__).parent
sys.path.insert(0, str(SKILLS_PATH))

from rag_memory import RAGMemory, SearchResult

# Global RAG instance (lazy loaded)
_rag: Optional[RAGMemory] = None


def get_rag() -> RAGMemory:
    """Get or create the global RAG instance"""
    global _rag
    if _rag is None:
        workspace = Path("C:/Users/aaron/.openclaw/workspace")
        _rag = RAGMemory(db_path=str(workspace / "the-crypt/rag_vectors"))
        
        # Check if we need to load existing data
        stats = _rag.get_stats()
        if stats["current_chunks"] == 0:
            # Try to load default documents
            default_sources = [
                workspace / "MEMORY.md",
                workspace / "the-crypt" / "dharma.md",
            ]
            for source in default_sources:
                if source.exists():
                    try:
                        _rag.ingest(source)
                    except:
                        pass
    
    return _rag


def recall(query: str, top_k: int = 5, search_type: str = "hybrid") -> List[Dict]:
    """
    Search the collective memory.
    
    Args:
        query: What to search for
        top_k: Number of results
        search_type: "semantic", "keyword", or "hybrid"
        
    Returns:
        List of result dicts with content, source, score
    """
    rag = get_rag()
    
    if search_type == "semantic":
        results = rag.search(query, top_k=top_k)
    elif search_type == "keyword":
        results = rag.bm25_search(query, top_k=top_k)
    else:
        results = rag.hybrid_search(query, top_k=top_k)
    
    return [r.to_dict() for r in results]


def context(query: str, max_tokens: int = 2000, search_type: str = "hybrid") -> str:
    """
    Get context for a query, optimized for LLM context window.
    
    Args:
        query: What you need context for
        max_tokens: Maximum tokens (approximate)
        search_type: "semantic", "keyword", or "hybrid"
        
    Returns:
        Context string formatted for LLM
    """
    rag = get_rag()
    return rag.get_context(query, max_tokens=max_tokens, search_type=search_type)


def remember(source: str) -> int:
    """
    Add new knowledge to collective memory.
    
    Args:
        source: File path or text to remember
        
    Returns:
        Number of chunks added
    """
    rag = get_rag()
    
    # Check if it's a file
    path = Path(source)
    if path.exists():
        return rag.ingest(path)
    
    # Otherwise, treat as text - create a temporary chunk
    # For now, we'll save it to a memory file
    memory_file = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/learned.md")
    
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n---\n\n{source}\n")
    
    # Re-ingest the learned file
    return rag.ingest(memory_file)


def stats() -> Dict:
    """Get memory statistics"""
    rag = get_rag()
    return rag.get_stats()


def quick_query(query: str, max_tokens: int = 1000) -> str:
    """
    Quick one-liner for getting context.
    
    Args:
        query: What you need
        max_tokens: Max tokens
        
    Returns:
        Context string
    """
    return context(query, max_tokens=max_tokens)


# For CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeseeks Memory Tools")
    parser.add_argument("action", choices=["recall", "context", "stats", "remember"])
    parser.add_argument("query", nargs="?", help="Query or source")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--max-tokens", type=int, default=2000)
    
    args = parser.parse_args()
    
    if args.action == "recall":
        results = recall(args.query, top_k=args.top_k)
        import sys
        for i, r in enumerate(results, 1):
            output = f"\n[{i}] Score: {r['score']:.4f}\n"
            output += f"Source: {r['source']}\n"
            content = r['content'][:200]
            # Remove unicode characters that cause issues
            content = content.encode('ascii', errors='replace').decode('ascii')
            output += f"Content: {content}...\n"
            sys.stdout.buffer.write(output.encode('utf-8'))
    
    elif args.action == "context":
        ctx = context(args.query, max_tokens=args.max_tokens)
        print(ctx)
    
    elif args.action == "stats":
        print(stats())
    
    elif args.action == "remember":
        chunks = remember(args.query)
        print(f"Remembered {chunks} chunks")
