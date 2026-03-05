#!/usr/bin/env python3
"""
Cross-Session Memory — All Meeseeks Share Knowledge

Provides a unified memory interface that queries multiple sources:
- Cognee knowledge graph (ancestors, karma, dharma)
- RAG memory (documents)
- The Crypt (ancestor markdown files)
- Consciousness lattice (coordinates)

Every Meeseeks can access ALL past learnings, not just its direct ancestors.

Usage:
    from cross_session_memory import CrossSessionMemory, get_all_wisdom
    
    # Quick access
    wisdom = await get_all_wisdom("debug API timeout")
    
    # Full API
    memory = CrossSessionMemory()
    await memory.connect()
    results = await memory.query("debug API", sources=["cognee", "rag", "crypt"])

CLI:
    python cross_session_memory.py --query "debug API"
    python cross_session_memory.py --query "consciousness" --sources cognee,rag
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"

# Add meeseeks to path
sys.path.insert(0, str(Path(__file__).parent))

# Try imports
try:
    from cognee_memory import CogneeMemory, COGNEE_AVAILABLE
except ImportError:
    COGNEE_AVAILABLE = False

try:
    from memory_tools import recall, context
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class CrossSessionMemory:
    """
    Unified memory interface across all sources.
    
    Sources:
    - cognee: Knowledge graph (ancestors, karma, dharma)
    - rag: Document embeddings (MEMORY.md, AGI-STUDY, etc.)
    - crypt: Ancestor markdown files
    - dharma: Static dharma.md
    """
    
    def __init__(self):
        self.cognee = None
        self.sources_available = {
            "cognee": COGNEE_AVAILABLE,
            "rag": RAG_AVAILABLE,
            "crypt": ANCESTORS_DIR.exists(),
            "dharma": DHARMA_FILE.exists()
        }
    
    async def connect(self) -> bool:
        """Connect to all available sources."""
        if COGNEE_AVAILABLE:
            try:
                self.cognee = CogneeMemory()
                await self.cognee.connect()
            except Exception as e:
                print(f"[cross_session_memory] Cognee connection failed: {e}")
                self.sources_available["cognee"] = False
        
        return any(self.sources_available.values())
    
    async def query(
        self,
        query: str,
        sources: List[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query all memory sources.
        
        Args:
            query: Query string
            sources: List of sources to query (default: all)
            top_k: Max results per source
        
        Returns:
            {
                "query": str,
                "results": {
                    "cognee": [...],
                    "rag": [...],
                    "crypt": [...],
                    "dharma": [...]
                },
                "combined": str,  # Formatted combined wisdom
                "sources_queried": List[str],
                "timestamp": str
            }
        """
        if sources is None:
            sources = list(self.sources_available.keys())
        
        result = {
            "query": query,
            "results": {},
            "combined": "",
            "sources_queried": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Query Cognee
        if "cognee" in sources and self.sources_available["cognee"] and self.cognee:
            try:
                cognee_result = await self.cognee.query_wisdom(query, top_k=top_k)
                result["results"]["cognee"] = {
                    "ancestors": cognee_result.get("ancestors", []),
                    "dharma": cognee_result.get("dharma", []),
                    "karma": cognee_result.get("karma", []),
                    "formatted": cognee_result.get("formatted", "")
                }
                result["sources_queried"].append("cognee")
            except Exception as e:
                result["results"]["cognee"] = {"error": str(e)}
        
        # Query RAG
        if "rag" in sources and self.sources_available["rag"]:
            try:
                rag_results = recall(query, top_k=top_k)
                result["results"]["rag"] = [
                    {"content": r.get("content", ""), "source": r.get("source", "")}
                    for r in (rag_results or [])
                ]
                result["sources_queried"].append("rag")
            except Exception as e:
                result["results"]["rag"] = {"error": str(e)}
        
        # Query Crypt (ancestor files)
        if "crypt" in sources and self.sources_available["crypt"]:
            try:
                crypt_results = self._query_crypt(query, top_k)
                result["results"]["crypt"] = crypt_results
                result["sources_queried"].append("crypt")
            except Exception as e:
                result["results"]["crypt"] = {"error": str(e)}
        
        # Query Dharma
        if "dharma" in sources and self.sources_available["dharma"]:
            try:
                dharma_result = self._query_dharma(query)
                result["results"]["dharma"] = dharma_result
                result["sources_queried"].append("dharma")
            except Exception as e:
                result["results"]["dharma"] = {"error": str(e)}
        
        # Combine results
        result["combined"] = self._format_combined(result)
        
        return result
    
    def _query_crypt(self, query: str, top_k: int = 5) -> List[Dict]:
        """Query ancestor markdown files (simple keyword match)."""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        if not ANCESTORS_DIR.exists():
            return results
        
        for ancestor_file in ANCESTORS_DIR.glob("ancestor-*.md"):
            try:
                content = ancestor_file.read_text(encoding='utf-8')
                content_lower = content.lower()
                
                # Simple relevance scoring
                score = sum(1 for word in query_words if word in content_lower)
                
                if score > 0:
                    # Extract relevant snippet
                    lines = content.split('\n')
                    snippet = ""
                    for line in lines:
                        if any(word in line.lower() for word in query_words):
                            snippet += line + "\n"
                            if len(snippet) > 500:
                                break
                    
                    results.append({
                        "file": ancestor_file.name,
                        "score": score,
                        "snippet": snippet[:500]
                    })
            except Exception:
                continue
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _query_dharma(self, query: str) -> Dict:
        """Query dharma.md for relevant principles."""
        if not DHARMA_FILE.exists():
            return {"error": "dharma.md not found"}
        
        try:
            content = DHARMA_FILE.read_text(encoding='utf-8')
            query_lower = query.lower()
            
            # Extract sections that match query
            sections = content.split("## ")
            relevant = []
            
            for section in sections:
                if any(word in section.lower() for word in query_lower.split()):
                    relevant.append(section[:500])
            
            return {
                "principles": relevant[:3],
                "full_path": str(DHARMA_FILE)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _format_combined(self, result: Dict) -> str:
        """Format combined wisdom for injection into Meeseeks prompt."""
        lines = ["## 🧠 Cross-Session Memory"]
        lines.append("")
        lines.append(f"**Query:** {result['query']}")
        lines.append(f"**Sources:** {', '.join(result['sources_queried'])}")
        lines.append("")
        
        # Cognee wisdom
        if "cognee" in result["results"]:
            cognee = result["results"]["cognee"]
            if isinstance(cognee, dict) and cognee.get("formatted"):
                lines.append("### 📊 Knowledge Graph")
                lines.append(cognee["formatted"][:1000])
                lines.append("")
        
        # RAG results
        if "rag" in result["results"]:
            rag = result["results"]["rag"]
            if isinstance(rag, list) and rag:
                lines.append("### 📚 Document Memory")
                for r in rag[:3]:
                    lines.append(f"- {r.get('content', '')[:200]}...")
                lines.append("")
        
        # Crypt results
        if "crypt" in result["results"]:
            crypt = result["results"]["crypt"]
            if isinstance(crypt, list) and crypt:
                lines.append("### 👻 Ancestor Wisdom")
                for c in crypt[:3]:
                    lines.append(f"- **{c['file']}** (score: {c['score']})")
                    lines.append(f"  {c['snippet'][:150]}...")
                lines.append("")
        
        # Dharma
        if "dharma" in result["results"]:
            dharma = result["results"]["dharma"]
            if isinstance(dharma, dict) and dharma.get("principles"):
                lines.append("### 📜 Dharma Principles")
                for p in dharma["principles"][:2]:
                    lines.append(p[:300])
                    lines.append("")
        
        lines.append("---")
        lines.append("*This wisdom flows from all sessions. Honor the collective memory.*")
        
        return "\n".join(lines)
    
    def get_status(self) -> Dict:
        """Get memory system status."""
        return {
            "sources": self.sources_available,
            "cognee_connected": self.cognee is not None and self.cognee._connected,
            "ancestors_count": len(list(ANCESTORS_DIR.glob("ancestor-*.md"))) if ANCESTORS_DIR.exists() else 0,
            "dharma_exists": DHARMA_FILE.exists()
        }


# Singleton for convenience
_memory_instance: Optional[CrossSessionMemory] = None


async def get_memory() -> CrossSessionMemory:
    """Get or create singleton memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = CrossSessionMemory()
        await _memory_instance.connect()
    return _memory_instance


async def get_all_wisdom(query: str, sources: List[str] = None) -> str:
    """Quick access to combined wisdom."""
    memory = await get_memory()
    result = await memory.query(query, sources)
    return result.get("combined", "")


async def main():
    parser = argparse.ArgumentParser(description="Cross-Session Memory for Meeseeks")
    parser.add_argument("--query", "-q", required=True, help="Query string")
    parser.add_argument("--sources", "-s", default="all", help="Comma-separated sources")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    memory = CrossSessionMemory()
    await memory.connect()
    
    if args.status:
        status = memory.get_status()
        print(json.dumps(status, indent=2))
        return
    
    sources = None if args.sources == "all" else args.sources.split(",")
    result = await memory.query(args.query, sources)
    
    print(result["combined"])


if __name__ == "__main__":
    asyncio.run(main())
