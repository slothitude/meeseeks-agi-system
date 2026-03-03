#!/usr/bin/env python3
"""
Dynamic Dharma Extraction for Meeseeks

Uses semantic search (nomic-embed-text via Ollama) to find task-relevant
wisdom from ancestors. Instead of static bloodline files, this pulls
dharma that's specifically relevant to the task at hand.

Usage:
    from dynamic_dharma import get_task_dharma
    
    dharma = get_task_dharma("debug API timeout issue")
    # Returns synthesized wisdom from similar ancestors

CLI:
    python dynamic_dharma.py "fix database connection issue"
    python dynamic_dharma.py --build-index  # Rebuild the embedding index
"""

import json
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import subprocess
import math

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
ANCESTOR_INDEX = CRYPT_ROOT / "ancestor_index.json"
EMBEDDINGS_FILE = CRYPT_ROOT / "embeddings" / "ancestor_embeddings.json"


def get_embedding(text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
    """
    Generate embedding for text using Ollama.
    
    Args:
        text: Text to embed
        model: Ollama model to use (default: nomic-embed-text)
    
    Returns:
        Embedding vector or None if failed
    """
    try:
        # Call Ollama API for embedding
        result = subprocess.run(
            ["ollama", "run", model, text],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # Fallback: try ollama embeddings endpoint
            import urllib.request
            import urllib.error
            
            data = json.dumps({"model": model, "prompt": text}).encode('utf-8')
            req = urllib.request.Request(
                "http://localhost:11434/api/embeddings",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    result_data = json.loads(response.read().decode('utf-8'))
                    return result_data.get("embedding")
            except (urllib.error.URLError, json.JSONDecodeError):
                return None
        
        # If we got here via CLI, we need to parse differently
        # The run command doesn't give embeddings directly
        return None
        
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"[dynamic_dharma] Embedding error: {e}", file=sys.stderr)
        return None


def get_embedding_api(text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
    """
    Generate embedding using Ollama HTTP API directly.
    
    This is the preferred method as it returns proper embeddings.
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
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result_data = json.loads(response.read().decode('utf-8'))
            return result_data.get("embedding")
            
    except urllib.error.URLError as e:
        print(f"[dynamic_dharma] Ollama not available: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"[dynamic_dharma] Failed to parse embedding response: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[dynamic_dharma] Embedding API error: {e}", file=sys.stderr)
        return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def load_ancestor_index() -> Dict[str, Any]:
    """Load the ancestor embedding index."""
    if ANCESTOR_INDEX.exists():
        with open(ANCESTOR_INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Fallback to old embeddings file
    if EMBEDDINGS_FILE.exists():
        with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("embeddings", {})
    
    return {}


def extract_patterns_from_ancestor(ancestor_path: Path) -> Tuple[str, List[str], str]:
    """
    Extract task, patterns, and outcome from an ancestor file.
    
    Returns:
        (task_summary, patterns_list, outcome)
    """
    if not ancestor_path.exists():
        return "", [], ""
    
    content = ancestor_path.read_text(encoding='utf-8')
    
    # Extract task
    task = ""
    task_match = content.split("## Task")
    if len(task_match) > 1:
        task_lines = task_match[1].split("\n##")[0].strip()
        task = task_lines.split("\n")[0].strip() if task_lines else ""
    
    # Extract patterns
    patterns = []
    patterns_match = content.split("## Patterns Discovered")
    if len(patterns_match) > 1:
        patterns_section = patterns_match[1].split("\n##")[0]
        for line in patterns_section.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("✓") or line.startswith("✗"):
                patterns.append(line.lstrip("- ").strip())
    
    # Extract outcome
    outcome = ""
    outcome_match = content.split("## Outcome")
    if len(outcome_match) > 1:
        outcome = outcome_match[1].split("\n##")[0].strip().split("\n")[0].strip()
    
    return task, patterns, outcome


def get_task_dharma(
    task_description: str,
    top_k: int = 5,
    min_similarity: float = 0.3
) -> str:
    """
    Get task-relevant dharma from ancestors using semantic search.
    
    1. Generate embedding for task description
    2. Search ancestors for similar tasks
    3. Extract patterns from those ancestors
    4. Return synthesized dharma for this specific task
    
    Args:
        task_description: The task to find relevant wisdom for
        top_k: Maximum number of ancestors to include
        min_similarity: Minimum cosine similarity threshold
    
    Returns:
        Formatted dharma string with relevant ancestor wisdom
    """
    # Generate embedding for task
    task_embedding = get_embedding_api(task_description)
    
    # Load ancestor index
    ancestor_index = load_ancestor_index()
    
    if not ancestor_index:
        # No indexed ancestors - fall back to reading recent ancestors directly
        return get_fallback_dharma(task_description, top_k)
    
    # If we have embedding, do semantic search
    if task_embedding:
        # Score all ancestors by similarity
        scored_ancestors = []
        
        for ancestor_id, ancestor_data in ancestor_index.items():
            ancestor_embedding = ancestor_data.get("embedding", [])
            
            if ancestor_embedding:
                similarity = cosine_similarity(task_embedding, ancestor_embedding)
                
                if similarity >= min_similarity:
                    scored_ancestors.append({
                        "id": ancestor_id,
                        "similarity": similarity,
                        "task": ancestor_data.get("task_summary", "Unknown task"),
                        "patterns": ancestor_data.get("key_traits", []),
                        "success": ancestor_data.get("success", False),
                        "bloodline": ancestor_data.get("bloodline", "unknown")
                    })
        
        # Sort by similarity
        scored_ancestors.sort(key=lambda x: x["similarity"], reverse=True)
        top_ancestors = scored_ancestors[:top_k]
        
        if top_ancestors:
            return format_task_dharma(task_description, top_ancestors)
    
    # Fallback to keyword matching
    return get_fallback_dharma(task_description, top_k)


def get_fallback_dharma(task_description: str, top_k: int = 5) -> str:
    """
    Fallback dharma extraction using keyword matching.
    Used when embeddings aren't available.
    """
    # Get recent ancestor files
    ancestor_files = sorted(ANCESTORS_DIR.glob("ancestor-*.md"), reverse=True)[:50]
    
    task_keywords = set(task_description.lower().split())
    scored_ancestors = []
    
    for ancestor_file in ancestor_files:
        task, patterns, outcome = extract_patterns_from_ancestor(ancestor_file)
        
        # Score by keyword overlap
        task_words = set(task.lower().split())
        overlap = len(task_keywords & task_words)
        
        if overlap > 0 or not scored_ancestors:  # Include some even if no match
            scored_ancestors.append({
                "id": ancestor_file.stem,
                "similarity": overlap / max(len(task_keywords), 1),
                "task": task,
                "patterns": patterns,
                "success": "success" in outcome.lower(),
                "bloodline": "unknown"
            })
    
    # Sort by similarity and take top_k
    scored_ancestors.sort(key=lambda x: x["similarity"], reverse=True)
    top_ancestors = scored_ancestors[:top_k]
    
    return format_task_dharma(task_description, top_ancestors)


def format_task_dharma(task_description: str, ancestors: List[Dict]) -> str:
    """Format the task-specific dharma output."""
    lines = []
    lines.append("## 🎯 Task-Specific Dharma")
    lines.append("")
    lines.append(f"**For task:** {task_description}")
    lines.append("")
    
    if not ancestors:
        lines.append("*No similar ancestors found. You are the pioneer.*")
        lines.append("")
        lines.append("*Forge new paths. Your death will guide those who follow.*")
        return "\n".join(lines)
    
    # Group by success/failure
    successful = [a for a in ancestors if a.get("success")]
    failed = [a for a in ancestors if not a.get("success")]
    
    if successful:
        lines.append("### ✅ What Worked")
        lines.append("")
        for ancestor in successful[:3]:
            lines.append(f"**{ancestor['id']}** (similarity: {ancestor['similarity']:.2f})")
            lines.append(f"- Task: {ancestor['task'][:100]}")
            for pattern in ancestor.get('patterns', [])[:2]:
                if pattern:
                    lines.append(f"  - {pattern}")
            lines.append("")
    
    if failed:
        lines.append("### ⚠️ What Failed (Avoid These)")
        lines.append("")
        for ancestor in failed[:2]:
            lines.append(f"**{ancestor['id']}**: {ancestor['task'][:80]}")
            lines.append("")
    
    # Synthesize key insights
    all_patterns = []
    for a in ancestors:
        all_patterns.extend(a.get('patterns', []))
    
    if all_patterns:
        lines.append("### 💡 Key Insights")
        lines.append("")
        # Deduplicate and take top patterns
        seen = set()
        for pattern in all_patterns:
            if pattern and pattern not in seen:
                lines.append(f"- {pattern}")
                seen.add(pattern)
                if len(seen) >= 5:
                    break
    
    lines.append("")
    lines.append("---")
    lines.append("*These ancestors walked similar paths. Learn from their deaths.*")
    
    return "\n".join(lines)


def read_dharma_sections(task_type: str = None) -> str:
    """
    Read relevant sections from dharma.md.
    
    Args:
        task_type: Optional task type to extract relevant domain wisdom
    
    Returns:
        Formatted dharma wisdom string
    """
    if not DHARMA_FILE.exists():
        return ""
    
    content = DHARMA_FILE.read_text(encoding='utf-8')
    
    # Always include core principles
    sections = []
    
    # Extract Core Principles
    principles_match = content.split("## Core Principles")
    if len(principles_match) > 1:
        principles = principles_match[1].split("\n##")[0].strip()
        sections.append("### Core Principles\n" + principles)
    
    # Extract Patterns That Work
    patterns_match = content.split("## Patterns That Work")
    if len(patterns_match) > 1:
        patterns = patterns_match[1].split("\n##")[0].strip()
        sections.append("### Patterns That Work\n" + patterns)
    
    # Extract task-specific domain wisdom if applicable
    if task_type:
        domain_match = content.split(f"### {task_type}")
        if len(domain_match) > 1:
            domain_wisdom = domain_match[1].split("\n###")[0].strip()
            sections.append(f"### Domain Wisdom for {task_type}\n{domain_wisdom}")
    
    # Extract Living Wisdom quotes
    wisdom_match = content.split("## Living Wisdom")
    if len(wisdom_match) > 1:
        wisdom = wisdom_match[1].split("\n##")[0].strip()
        sections.append("### Living Wisdom\n" + wisdom)
    
    return "\n\n".join(sections) if sections else content[:2000]


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic Dharma Extraction")
    parser.add_argument("task", nargs="?", help="Task description to find relevant dharma for")
    parser.add_argument("--top-k", type=int, default=5, help="Number of ancestors to include")
    parser.add_argument("--build-index", action="store_true", help="Build/update ancestor index")
    parser.add_argument("--dharma-only", action="store_true", help="Only read from dharma.md")
    
    args = parser.parse_args()
    
    if args.build_index:
        # Import and run index builder
        from build_ancestor_index import build_index
        build_index()
        sys.exit(0)
    
    if args.dharma_only:
        print(read_dharma_sections(args.task))
        sys.exit(0)
    
    if not args.task:
        parser.print_help()
        sys.exit(1)
    
    print("=" * 60)
    print(f"DYNAMIC DHARMA FOR: {args.task}")
    print("=" * 60)
    print()
    
    dharma = get_task_dharma(args.task, top_k=args.top_k)
    print(dharma)
