#!/usr/bin/env python3
"""
Ancestor Embedding Index Builder

Builds and maintains the ancestor_index.json file with embeddings for
semantic search. Uses nomic-embed-text via Ollama.

Usage:
    python build_ancestor_index.py --rebuild  # Full rebuild
    python build_ancestor_index.py --update   # Add new only
    python build_ancestor_index.py --stats    # Show stats
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
AUTO_ENTOMBED_DIR = CRYPT_ROOT / "auto-entombed"
ANCESTOR_INDEX = CRYPT_ROOT / "ancestor_index.json"
EMBEDDINGS_DIR = CRYPT_ROOT / "embeddings"
OLD_EMBEDDINGS = EMBEDDINGS_DIR / "ancestor_embeddings.json"


def get_embedding_api(text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
    """
    Generate embedding using Ollama HTTP API.
    """
    import urllib.request
    import urllib.error
    
    try:
        data = json.dumps({"model": model, "prompt": text}).encode('utf-8')
        req = urllib.request.Request(
            "http://localhost:11434/api/embeddings",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result_data = json.loads(response.read().decode('utf-8'))
            return result_data.get("embedding")
            
    except urllib.error.URLError:
        print("[build_index] Ollama not available - skipping embeddings", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[build_index] Embedding error: {e}", file=sys.stderr)
        return None


def extract_ancestor_data(ancestor_path: Path) -> Dict[str, Any]:
    """
    Extract key data from an ancestor file.
    
    Returns dict with:
        - id
        - task_summary
        - patterns
        - outcome
        - success
        - bloodline
        - embedded_text (for embedding generation)
    """
    if not ancestor_path.exists():
        return {}
    
    content = ancestor_path.read_text(encoding='utf-8')
    
    data = {
        "id": ancestor_path.stem,
        "ancestor_file": str(ancestor_path),
        "task_summary": "",
        "key_traits": [],
        "outcome": "",
        "success": False,
        "bloodline": "unknown",
        "embedded_at": datetime.now().isoformat()
    }
    
    # Extract task
    lines = content.split("\n")
    in_task = False
    task_lines = []
    
    for i, line in enumerate(lines):
        if line.startswith("## Task"):
            in_task = True
            continue
        if in_task:
            if line.startswith("## "):
                break
            if line.strip():
                task_lines.append(line.strip())
    
    data["task_summary"] = " ".join(task_lines)[:500]
    
    # Extract patterns
    in_patterns = False
    for line in lines:
        if line.startswith("## Patterns Discovered"):
            in_patterns = True
            continue
        if in_patterns:
            if line.startswith("## "):
                break
            if line.strip().startswith("- ") or "✓" in line or "✗" in line:
                pattern = line.lstrip("- ").strip()
                if pattern:
                    data["key_traits"].append(pattern)
    
    # Extract outcome
    in_outcome = False
    for line in lines:
        if line.startswith("## Outcome"):
            in_outcome = True
            continue
        if in_outcome:
            if line.startswith("## "):
                break
            if line.strip():
                data["outcome"] = line.strip()
                data["success"] = "success" in line.lower()
                break
    
    # Extract bloodline
    for line in lines:
        if line.startswith("## Bloodline"):
            idx = lines.index(line)
            if idx + 1 < len(lines):
                data["bloodline"] = lines[idx + 1].strip().lower()
            break
    
    # Create text for embedding (task + patterns combined)
    embed_text = data["task_summary"]
    if data["key_traits"]:
        embed_text += " " + " ".join(data["key_traits"][:3])
    
    data["embedded_text"] = embed_text[:1000]  # Limit length
    
    return data


def get_all_ancestor_files() -> List[Path]:
    """Get all ancestor files from both directories."""
    files = []
    
    # Main ancestors directory
    if ANCESTORS_DIR.exists():
        files.extend(ANCESTORS_DIR.glob("ancestor-*.md"))
    
    # Auto-entombed directory
    if AUTO_ENTOMBED_DIR.exists():
        files.extend(AUTO_ENTOMBED_DIR.glob("auto-*.md"))
    
    return sorted(files, key=lambda x: x.stem, reverse=True)


def load_existing_index() -> Dict[str, Any]:
    """Load existing index or return empty."""
    if ANCESTOR_INDEX.exists():
        with open(ANCESTOR_INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_old_embeddings() -> Dict[str, Any]:
    """Load old embeddings file if exists."""
    if OLD_EMBEDDINGS.exists():
        with open(OLD_EMBEDDINGS, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("embeddings", {})
    return {}


def build_index(rebuild: bool = False, verbose: bool = True) -> Dict[str, Any]:
    """
    Build or update the ancestor embedding index.
    
    Args:
        rebuild: If True, rebuild all embeddings. If False, only add new.
        verbose: Print progress
    
    Returns:
        The built/updated index
    """
    # Load existing index
    if rebuild:
        index = {}
        # But keep old embeddings as fallback
        old_embeddings = load_old_embeddings()
    else:
        index = load_existing_index()
        old_embeddings = {}
    
    # Get all ancestor files
    all_files = get_all_ancestor_files()
    
    if verbose:
        print(f"[build_index] Found {len(all_files)} ancestor files")
    
    # Check which need embedding
    new_count = 0
    skipped_count = 0
    error_count = 0
    
    for ancestor_file in all_files:
        ancestor_id = ancestor_file.stem
        
        # Skip if already indexed (unless rebuild)
        if not rebuild and ancestor_id in index:
            skipped_count += 1
            continue
        
        # Extract data
        data = extract_ancestor_data(ancestor_file)
        
        if not data.get("task_summary"):
            if verbose:
                print(f"[build_index] Skipping {ancestor_id} - no task data")
            continue
        
        # Try to get embedding
        embed_text = data.pop("embedded_text", "")
        
        embedding = get_embedding_api(embed_text)
        
        if embedding:
            data["embedding"] = embedding
            new_count += 1
            if verbose:
                print(f"[build_index] Embedded: {ancestor_id}")
        else:
            # Check old embeddings for fallback
            if ancestor_id in old_embeddings:
                data["embedding"] = old_embeddings[ancestor_id].get("embedding", [])
                if verbose:
                    print(f"[build_index] Using cached embedding: {ancestor_id}")
            else:
                # Store without embedding - can be embedded later
                data["embedding"] = []
                error_count += 1
                if verbose:
                    print(f"[build_index] No embedding for: {ancestor_id}")
        
        index[ancestor_id] = data
    
    # Add metadata
    index["_meta"] = {
        "last_updated": datetime.now().isoformat(),
        "total_ancestors": len([k for k in index.keys() if k != "_meta"]),
        "with_embeddings": len([k for k, v in index.items() if k != "_meta" and v.get("embedding")]),
        "rebuild": rebuild
    }
    
    # Save index
    ANCESTOR_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(ANCESTOR_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    if verbose:
        print(f"\n[build_index] Complete!")
        print(f"  - New embeddings: {new_count}")
        print(f"  - Skipped (existing): {skipped_count}")
        print(f"  - Without embeddings: {error_count}")
        print(f"  - Total in index: {index['_meta']['total_ancestors']}")
        print(f"  - Saved to: {ANCESTOR_INDEX}")
    
    return index


def show_stats():
    """Show index statistics."""
    index = load_existing_index()
    
    if not index:
        print("No index found. Run with --rebuild to create.")
        return
    
    meta = index.get("_meta", {})
    
    print("=" * 60)
    print("ANCESTOR INDEX STATISTICS")
    print("=" * 60)
    print(f"Last updated: {meta.get('last_updated', 'Unknown')}")
    print(f"Total ancestors: {meta.get('total_ancestors', 0)}")
    print(f"With embeddings: {meta.get('with_embeddings', 0)}")
    print()
    
    # Count by bloodline
    bloodlines = {}
    successes = 0
    failures = 0
    
    for key, data in index.items():
        if key == "_meta":
            continue
        
        bl = data.get("bloodline", "unknown")
        bloodlines[bl] = bloodlines.get(bl, 0) + 1
        
        if data.get("success"):
            successes += 1
        else:
            failures += 1
    
    print("By Bloodline:")
    for bl, count in sorted(bloodlines.items(), key=lambda x: -x[1]):
        print(f"  - {bl}: {count}")
    
    print()
    print(f"Success rate: {successes}/{successes + failures} ({100 * successes / max(successes + failures, 1):.1f}%)")


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Ancestor Embedding Index")
    parser.add_argument("--rebuild", action="store_true", help="Full rebuild of all embeddings")
    parser.add_argument("--update", action="store_true", help="Only add new ancestors")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
        sys.exit(0)
    
    if args.rebuild:
        build_index(rebuild=True, verbose=not args.quiet)
    elif args.update:
        build_index(rebuild=False, verbose=not args.quiet)
    else:
        # Default: update
        build_index(rebuild=False, verbose=not args.quiet)
