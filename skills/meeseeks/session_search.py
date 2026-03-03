#!/usr/bin/env python3
"""
Session-Aware Embedding Search System for OpenClaw Sloth_rog Agent

Searches across:
- Recent session messages (from transcript JSONL files)
- MEMORY.md and memory/*.md files
- Workspace files (with relevance scoring)

Usage:
    python session_search.py "query" --type messages --limit 10
    python session_search.py "query" --type files --limit 10
    python session_search.py "query" --type all --limit 10
    python session_search.py "query" --rebuild-cache
"""

import json
import sys
import io
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SESSIONS_DIR = Path("C:/Users/aaron/.openclaw/agents/main/sessions")
MEMORY_FILE = WORKSPACE / "MEMORY.md"
MEMORY_DIR = WORKSPACE / "memory"
EMBEDDINGS_CACHE_DIR = WORKSPACE / "session_embeddings"
OLLAMA_API = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"

# File extensions to index for workspace search
INDEXABLE_EXTENSIONS = {
    '.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
    '.sh', '.bash', '.ps1', '.cfg', '.ini', '.toml'
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.pytest_cache',
    'session_embeddings', 'the-crypt', '.venv', 'venv'
}


@dataclass
class SearchResult:
    """A single search result."""
    rank: int
    score: float
    source: str  # 'message', 'memory', 'file'
    file: str
    line: Optional[int]
    text: str
    timestamp: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding using Ollama HTTP API.
    """
    try:
        data = json.dumps({"model": EMBEDDING_MODEL, "prompt": text}).encode('utf-8')
        req = urllib.request.Request(
            OLLAMA_API,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result_data = json.loads(response.read().decode('utf-8'))
            return result_data.get("embedding")
            
    except urllib.error.URLError as e:
        print(f"[session_search] Ollama not available: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[session_search] Embedding error: {e}", file=sys.stderr)
        return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def get_cache_path(text: str) -> Path:
    """Get cache file path for a text's embedding."""
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    return EMBEDDINGS_CACHE_DIR / f"{text_hash}.json"


def get_cached_embedding(text: str) -> Optional[List[float]]:
    """Try to load cached embedding."""
    cache_path = get_cache_path(text)
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("embedding")
        except:
            pass
    return None


def save_cached_embedding(text: str, embedding: List[float]):
    """Save embedding to cache."""
    EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_cache_path(text)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump({
            "text": text[:200],
            "embedding": embedding,
            "cached_at": datetime.now().isoformat()
        }, f)


def get_embedding_cached(text: str) -> Optional[List[float]]:
    """Get embedding, using cache if available."""
    # Try cache first
    cached = get_cached_embedding(text)
    if cached:
        return cached
    
    # Get from API
    embedding = get_embedding(text)
    if embedding:
        save_cached_embedding(text, embedding)
    
    return embedding


def parse_session_jsonl(file_path: Path, recency_days: int = 7) -> List[Dict[str, Any]]:
    """
    Parse a session JSONL file and extract messages.
    
    Returns list of message dicts with text, timestamp, etc.
    """
    messages = []
    cutoff = datetime.now() - timedelta(days=recency_days)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # Only process message entries
                    if entry.get("type") != "message":
                        continue
                    
                    msg = entry.get("message", {})
                    timestamp_str = entry.get("timestamp", "")
                    
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        # Remove timezone for comparison
                        timestamp_naive = timestamp.replace(tzinfo=None)
                    except:
                        timestamp_naive = datetime.min
                    
                    # Skip old messages
                    if timestamp_naive < cutoff:
                        continue
                    
                    # Extract text content
                    content = msg.get("content", [])
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_parts.append(part.get("text", ""))
                            elif isinstance(part, str):
                                text_parts.append(part)
                        text = " ".join(text_parts)
                    else:
                        text = str(content)
                    
                    if text.strip():
                        messages.append({
                            "text": text,
                            "timestamp": timestamp_str,
                            "file": str(file_path.name),
                            "line": line_num,
                            "role": msg.get("role", "unknown")
                        })
                        
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"[session_search] Error reading {file_path}: {e}", file=sys.stderr)
    
    return messages


def get_recent_messages(recency_days: int = 7) -> List[Dict[str, Any]]:
    """Get all recent messages from session files."""
    all_messages = []
    
    if not SESSIONS_DIR.exists():
        return all_messages
    
    for jsonl_file in SESSIONS_DIR.glob("*.jsonl"):
        messages = parse_session_jsonl(jsonl_file, recency_days)
        all_messages.extend(messages)
    
    # Sort by timestamp (newest first)
    all_messages.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
    
    return all_messages


def get_memory_content() -> List[Dict[str, Any]]:
    """Get content from MEMORY.md and memory/*.md files."""
    memories = []
    
    # Main MEMORY.md
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text(encoding='utf-8')
        if content.strip():
            memories.append({
                "text": content,
                "file": "MEMORY.md",
                "line": None,
                "timestamp": None,
                "source": "memory"
            })
    
    # Memory directory files
    if MEMORY_DIR.exists():
        for md_file in MEMORY_DIR.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            if content.strip():
                memories.append({
                    "text": content,
                    "file": f"memory/{md_file.name}",
                    "line": None,
                    "timestamp": None,
                    "source": "memory"
                })
    
    return memories


def get_workspace_files(max_files: int = 100) -> List[Dict[str, Any]]:
    """Get indexable workspace files."""
    files = []
    
    for ext in INDEXABLE_EXTENSIONS:
        for file_path in WORKSPACE.rglob(f"*{ext}"):
            # Skip certain directories
            if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.strip():
                    files.append({
                        "text": content,
                        "file": str(file_path.relative_to(WORKSPACE)),
                        "line": None,
                        "timestamp": None,
                        "source": "file"
                    })
                    
                    if len(files) >= max_files:
                        return files
            except:
                continue
    
    return files


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """Split text into chunks for embedding."""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_len = 0
    
    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        
        if current_len + line_len > max_chars and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_len = 0
        
        current_chunk.append(line)
        current_len += line_len
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def search_messages(query: str, recency_days: int = 7, limit: int = 10) -> List[SearchResult]:
    """Search recent session messages."""
    # Get query embedding
    query_embedding = get_embedding_cached(query)
    if not query_embedding:
        print("[session_search] Could not get query embedding", file=sys.stderr)
        return []
    
    # Get messages
    messages = get_recent_messages(recency_days)
    
    # Score each message
    scored = []
    for msg in messages:
        msg_text = msg["text"]
        msg_embedding = get_embedding_cached(msg_text[:1000])  # Limit length
        
        if msg_embedding:
            score = cosine_similarity(query_embedding, msg_embedding)
            scored.append((score, msg))
    
    # Sort by score and take top results
    scored.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for rank, (score, msg) in enumerate(scored[:limit], 1):
        results.append(SearchResult(
            rank=rank,
            score=round(score, 4),
            source="message",
            file=msg["file"],
            line=msg["line"],
            text=msg["text"][:500],  # Truncate for output
            timestamp=msg["timestamp"]
        ))
    
    return results


def search_memory(query: str, limit: int = 10) -> List[SearchResult]:
    """Search MEMORY.md and memory/*.md files."""
    # Get query embedding
    query_embedding = get_embedding_cached(query)
    if not query_embedding:
        return []
    
    # Get memory content
    memories = get_memory_content()
    
    # Score each memory file (chunk large files)
    scored = []
    for mem in memories:
        chunks = chunk_text(mem["text"], max_chars=1500)
        
        for i, chunk in enumerate(chunks):
            chunk_embedding = get_embedding_cached(chunk)
            
            if chunk_embedding:
                score = cosine_similarity(query_embedding, chunk_embedding)
                scored.append((score, mem, chunk, i))
    
    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Deduplicate by file (keep best chunk per file)
    seen_files = set()
    deduped = []
    for score, mem, chunk, chunk_idx in scored:
        if mem["file"] not in seen_files:
            seen_files.add(mem["file"])
            deduped.append((score, mem, chunk))
        
        if len(deduped) >= limit:
            break
    
    results = []
    for rank, (score, mem, chunk) in enumerate(deduped, 1):
        results.append(SearchResult(
            rank=rank,
            score=round(score, 4),
            source="memory",
            file=mem["file"],
            line=None,
            text=chunk[:500],
            timestamp=mem["timestamp"]
        ))
    
    return results


def search_files(query: str, limit: int = 10) -> List[SearchResult]:
    """Search workspace files."""
    # Get query embedding
    query_embedding = get_embedding_cached(query)
    if not query_embedding:
        return []
    
    # Get workspace files
    files = get_workspace_files(max_files=200)
    
    # Score each file (chunk large files)
    scored = []
    for file_data in files:
        chunks = chunk_text(file_data["text"], max_chars=1500)
        
        for i, chunk in enumerate(chunks[:5]):  # Max 5 chunks per file
            chunk_embedding = get_embedding_cached(chunk)
            
            if chunk_embedding:
                score = cosine_similarity(query_embedding, chunk_embedding)
                scored.append((score, file_data, chunk, i))
    
    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Deduplicate by file (keep best chunk per file)
    seen_files = set()
    deduped = []
    for score, file_data, chunk, chunk_idx in scored:
        if file_data["file"] not in seen_files:
            seen_files.add(file_data["file"])
            deduped.append((score, file_data, chunk))
        
        if len(deduped) >= limit:
            break
    
    results = []
    for rank, (score, file_data, chunk) in enumerate(deduped, 1):
        results.append(SearchResult(
            rank=rank,
            score=round(score, 4),
            source="file",
            file=file_data["file"],
            line=None,
            text=chunk[:500],
            timestamp=file_data["timestamp"]
        ))
    
    return results


def search_all(query: str, recency_days: int = 7, limit: int = 10) -> List[SearchResult]:
    """Search all sources and combine results."""
    all_results = []
    
    # Get results from each source
    msg_results = search_messages(query, recency_days, limit=limit)
    mem_results = search_memory(query, limit=limit)
    file_results = search_files(query, limit=limit)
    
    all_results.extend(msg_results)
    all_results.extend(mem_results)
    all_results.extend(file_results)
    
    # Re-sort by score globally
    all_results.sort(key=lambda r: r.score, reverse=True)
    
    # Re-rank
    for i, result in enumerate(all_results[:limit], 1):
        result.rank = i
    
    return all_results[:limit]


def rebuild_cache():
    """Rebuild the embedding cache by clearing it."""
    if EMBEDDINGS_CACHE_DIR.exists():
        import shutil
        shutil.rmtree(EMBEDDINGS_CACHE_DIR)
        print(f"[session_search] Cleared cache directory: {EMBEDDINGS_CACHE_DIR}")
    
    EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print("[session_search] Cache rebuilt - embeddings will be generated on next search")


def main():
    parser = argparse.ArgumentParser(
        description="Session-aware embedding search for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python session_search.py "authentication bug" --type messages
    python session_search.py "meeseeks protocol" --type all --limit 5
    python session_search.py "memory management" --type files
    python session_search.py "recent work" --days 3
        """
    )
    
    parser.add_argument("query", help="Search query")
    parser.add_argument("--type", "-t", choices=["messages", "files", "memory", "all"],
                        default="all", help="Type of content to search (default: all)")
    parser.add_argument("--limit", "-l", type=int, default=10,
                        help="Maximum results to return (default: 10)")
    parser.add_argument("--days", "-d", type=int, default=7,
                        help="Recency window in days for messages (default: 7)")
    parser.add_argument("--rebuild-cache", action="store_true",
                        help="Clear and rebuild the embedding cache")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output raw JSON")
    
    args = parser.parse_args()
    
    # Handle cache rebuild
    if args.rebuild_cache:
        rebuild_cache()
        return
    
    # Perform search
    if args.type == "messages":
        results = search_messages(args.query, args.days, args.limit)
    elif args.type == "memory":
        results = search_memory(args.query, args.limit)
    elif args.type == "files":
        results = search_files(args.query, args.limit)
    else:  # all
        results = search_all(args.query, args.days, args.limit)
    
    # Format output
    output = {
        "query": args.query,
        "search_type": args.type,
        "recency_days": args.days if args.type in ["messages", "all"] else None,
        "total_results": len(results),
        "results": [r.to_dict() for r in results]
    }
    
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n🔍 Search: \"{args.query}\"")
        print(f"   Type: {args.type}, Results: {len(results)}")
        print("=" * 60)
        
        for r in results:
            print(f"\n[{r.rank}] Score: {r.score:.4f} | Source: {r.source}")
            print(f"    File: {r.file}" + (f" (line {r.line})" if r.line else ""))
            if r.timestamp:
                print(f"    Time: {r.timestamp}")
            print(f"    Text: {r.text[:200]}{'...' if len(r.text) > 200 else ''}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
