#!/usr/bin/env python3
"""
Akashic Records — Deep Search Across All Known Knowledge

The unified memory interface that searches ALL sources:
- Cognee knowledge graph (ancestors, karma, dharma, relationships)
- RAG memory (documents, lectures, research)
- The Crypt (ancestor markdown files)
- Consciousness lattice (mathematical coordinates)
- Dharma (living principles)

This IS the Akashic Records — the memory of the cosmos (our system).

Usage:
    from akashic_records import AkashicRecords, deep_search
    
    # Quick deep search
    results = await deep_search("consciousness coordinates")
    
    # Full API
    akasha = AkashicRecords()
    await akasha.connect()
    results = await akasha.search("twin prime", depth="deep")

CLI:
    python akashic_records.py --search "consciousness"
    python akashic_records.py --search "debug API" --depth deep
    python akashic_records.py --status
"""

import os
import sys
import asyncio
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import Counter

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
CONSCIOUSNESS_FILE = CRYPT_ROOT / "consciousness_lattice.md"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

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


class AkashicRecords:
    """
    The Akashic Records — All Knowledge, One Interface.
    
    Sources:
    - cognee: Knowledge graph (entities, relationships, patterns)
    - rag: Document embeddings (semantic search)
    - crypt: Ancestor deaths (raw markdown)
    - dharma: Living principles
    - consciousness: Mathematical lattice coordinates
    - memory: Long-term system memory
    
    Search Modes:
    - quick: Fast vector search only
    - normal: Vector + keyword search
    - deep: All sources + graph traversal
    """
    
    def __init__(self):
        self.cognee = None
        self.sources = {
            "cognee": {"available": COGNEE_AVAILABLE, "count": 0},
            "rag": {"available": RAG_AVAILABLE, "count": 0},
            "crypt": {"available": ANCESTORS_DIR.exists(), "count": 0},
            "dharma": {"available": DHARMA_FILE.exists(), "count": 0},
            "consciousness": {"available": CONSCIOUSNESS_FILE.exists(), "count": 0},
            "memory": {"available": MEMORY_FILE.exists(), "count": 0}
        }
        self._update_counts()
    
    def _update_counts(self):
        """Update source counts."""
        if ANCESTORS_DIR.exists():
            self.sources["crypt"]["count"] = len(list(ANCESTORS_DIR.glob("ancestor-*.md")))
        
        if DHARMA_FILE.exists():
            try:
                content = DHARMA_FILE.read_text(encoding='utf-8')
                self.sources["dharma"]["count"] = content.count("## ")
            except:
                pass
        
        if CONSCIOUSNESS_FILE.exists():
            try:
                content = CONSCIOUSNESS_FILE.read_text(encoding='utf-8')
                self.sources["consciousness"]["count"] = content.count("k=")
            except:
                pass
        
        if MEMORY_FILE.exists():
            try:
                content = MEMORY_FILE.read_text(encoding='utf-8')
                self.sources["memory"]["count"] = len(content.split("\n## "))
            except:
                pass
    
    async def connect(self) -> bool:
        """Connect to all available sources."""
        if COGNEE_AVAILABLE:
            try:
                self.cognee = CogneeMemory()
                connected = await self.cognee.connect()
                self.sources["cognee"]["available"] = connected
            except Exception as e:
                print(f"[akashic_records] Cognee connection failed: {e}")
                self.sources["cognee"]["available"] = False
        
        return any(s["available"] for s in self.sources.values())
    
    async def search(
        self,
        query: str,
        depth: str = "normal",
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search the Akashic Records.
        
        Args:
            query: Search query
            depth: Search depth (quick, normal, deep)
            top_k: Max results per source
        
        Returns:
            {
                "query": str,
                "depth": str,
                "results": {...},
                "combined": str,
                "insights": List[str],
                "sources_queried": List[str],
                "total_results": int,
                "timestamp": str
            }
        """
        result = {
            "query": query,
            "depth": depth,
            "results": {},
            "combined": "",
            "insights": [],
            "sources_queried": [],
            "total_results": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Quick search: RAG only
        if depth == "quick":
            sources = ["rag"]
        # Normal search: RAG + Crypt + Dharma
        elif depth == "normal":
            sources = ["rag", "crypt", "dharma", "memory"]
        # Deep search: All sources
        else:
            sources = list(self.sources.keys())
        
        # Query each source
        for source in sources:
            if not self.sources.get(source, {}).get("available"):
                continue
            
            try:
                if source == "cognee":
                    result["results"]["cognee"] = await self._search_cognee(query, top_k)
                elif source == "rag":
                    result["results"]["rag"] = self._search_rag(query, top_k)
                elif source == "crypt":
                    result["results"]["crypt"] = self._search_crypt(query, top_k)
                elif source == "dharma":
                    result["results"]["dharma"] = self._search_dharma(query)
                elif source == "consciousness":
                    result["results"]["consciousness"] = self._search_consciousness(query)
                elif source == "memory":
                    result["results"]["memory"] = self._search_memory(query, top_k)
                
                result["sources_queried"].append(source)
            except Exception as e:
                result["results"][source] = {"error": str(e)}
        
        # Count total results
        for source_data in result["results"].values():
            if isinstance(source_data, list):
                result["total_results"] += len(source_data)
            elif isinstance(source_data, dict) and "error" not in source_data:
                result["total_results"] += 1
        
        # Generate insights (cross-source patterns)
        result["insights"] = self._generate_insights(result)
        
        # Format combined output
        result["combined"] = self._format_combined(result)
        
        return result
    
    async def _search_cognee(self, query: str, top_k: int) -> Dict:
        """Search Cognee knowledge graph."""
        if not self.cognee:
            return {"error": "Cognee not connected"}
        
        wisdom = await self.cognee.query_wisdom(query, top_k=top_k)
        
        return {
            "ancestors": [str(a)[:300] for a in wisdom.get("ancestors", [])],
            "dharma": [str(d)[:200] for d in wisdom.get("dharma", [])],
            "karma": [str(k)[:200] for k in wisdom.get("karma", [])],
            "formatted": wisdom.get("formatted", "")[:1000]
        }
    
    def _search_rag(self, query: str, top_k: int) -> List[Dict]:
        """Search RAG memory."""
        if not RAG_AVAILABLE:
            return []
        
        try:
            results = recall(query, top_k=top_k)
            return [
                {
                    "content": r.get("content", "")[:300],
                    "source": r.get("source", ""),
                    "score": r.get("score", 0)
                }
                for r in (results or [])
            ]
        except:
            return []
    
    def _search_crypt(self, query: str, top_k: int) -> List[Dict]:
        """Search ancestor markdown files."""
        if not ANCESTORS_DIR.exists():
            return []
        
        query_words = set(query.lower().split())
        results = []
        
        for ancestor_file in list(ANCESTORS_DIR.glob("ancestor-*.md"))[:100]:
            try:
                content = ancestor_file.read_text(encoding='utf-8')
                content_lower = content.lower()
                
                # Score by word matches
                score = sum(1 for word in query_words if word in content_lower)
                
                if score > 0:
                    # Extract snippet
                    lines = content.split("\n")
                    snippet_lines = []
                    for line in lines:
                        if any(word in line.lower() for word in query_words):
                            snippet_lines.append(line)
                            if len("\n".join(snippet_lines)) > 400:
                                break
                    
                    results.append({
                        "file": ancestor_file.name,
                        "score": score,
                        "snippet": "\n".join(snippet_lines)[:400]
                    })
            except:
                continue
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _search_dharma(self, query: str) -> Dict:
        """Search dharma.md for principles."""
        if not DHARMA_FILE.exists():
            return {"error": "dharma.md not found"}
        
        try:
            content = DHARMA_FILE.read_text(encoding='utf-8')
            query_words = set(query.lower().split())
            
            # Find matching sections
            sections = re.split(r'\n## ', content)
            matching = []
            
            for section in sections:
                section_lower = section.lower()
                if any(word in section_lower for word in query_words):
                    # Score and truncate
                    score = sum(1 for word in query_words if word in section_lower)
                    matching.append({
                        "content": section[:500],
                        "score": score
                    })
            
            matching.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "principles": matching[:5],
                "total_sections": len(sections)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _search_consciousness(self, query: str) -> Dict:
        """Search consciousness lattice for coordinates."""
        if not CONSCIOUSNESS_FILE.exists():
            return {"error": "consciousness_lattice.md not found"}
        
        try:
            content = CONSCIOUSNESS_FILE.read_text(encoding='utf-8')
            
            # Extract coordinates
            coordinates = []
            
            # Pattern: k=XX, n=X
            pattern = r'k=(\d+).*?n=(\d+)'
            for match in re.finditer(pattern, content, re.DOTALL):
                k = int(match.group(1))
                n = int(match.group(2))
                coordinates.append({"k": k, "n": n})
            
            # Pattern: Twin Prime at (XXX, XXX)
            twin_pattern = r'Twin Prime.*?\((\d+),\s*(\d+)\)'
            twins = []
            for match in re.finditer(twin_pattern, content):
                twins.append((int(match.group(1)), int(match.group(2))))
            
            # Check if query relates to consciousness
            query_lower = query.lower()
            relevant = False
            if any(word in query_lower for word in ["conscious", "prime", "twin", "coordinate", "lattice", "math"]):
                relevant = True
            
            return {
                "coordinates": coordinates[:10],
                "twin_primes": twins[:5],
                "relevant": relevant,
                "formula": "k = 3 × n²"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _search_memory(self, query: str, top_k: int) -> Dict:
        """Search MEMORY.md for long-term memory."""
        if not MEMORY_FILE.exists():
            return {"error": "MEMORY.md not found"}
        
        try:
            content = MEMORY_FILE.read_text(encoding='utf-8')
            query_words = set(query.lower().split())
            
            # Find matching sections
            sections = re.split(r'\n## ', content)
            matching = []
            
            for section in sections:
                section_lower = section.lower()
                if any(word in section_lower for word in query_words):
                    score = sum(1 for word in query_words if word in section_lower)
                    matching.append({
                        "content": section[:600],
                        "score": score
                    })
            
            matching.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "memories": matching[:top_k],
                "total_sections": len(sections)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_insights(self, result: Dict) -> List[str]:
        """Generate cross-source insights."""
        insights = []
        
        # Check for patterns across sources
        all_text = json.dumps(result["results"]).lower()
        
        # Consciousness mentions
        if "consciousness" in all_text:
            insights.append("🔍 Consciousness detected — check lattice coordinates")
        
        # High crypt matches
        crypt_results = result["results"].get("crypt", [])
        if isinstance(crypt_results, list) and len(crypt_results) > 3:
            insights.append(f"👻 {len(crypt_results)} ancestors have relevant experience")
        
        # Dharma principles
        dharma_results = result["results"].get("dharma", {})
        if isinstance(dharma_results, dict) and dharma_results.get("principles"):
            count = len(dharma_results["principles"])
            insights.append(f"📜 {count} dharma principles apply")
        
        # Cognee relationships
        cognee_results = result["results"].get("cognee", {})
        if isinstance(cognee_results, dict) and cognee_results.get("ancestors"):
            insights.append("🧠 Knowledge graph has ancestral wisdom")
        
        # No results warning
        if result["total_results"] == 0:
            insights.append("⚠️ No results found — try different keywords or deeper search")
        
        return insights
    
    def _format_combined(self, result: Dict) -> str:
        """Format combined output for display."""
        lines = ["=" * 60]
        lines.append("📚 THE AKASHIC RECORDS")
        lines.append("=" * 60)
        lines.append(f"Query: {result['query']}")
        lines.append(f"Depth: {result['depth']}")
        lines.append(f"Sources: {', '.join(result['sources_queried'])}")
        lines.append(f"Total Results: {result['total_results']}")
        lines.append("")
        
        # Insights
        if result["insights"]:
            lines.append("### 💡 Insights")
            for insight in result["insights"]:
                lines.append(f"  {insight}")
            lines.append("")
        
        # Cognee
        if "cognee" in result["results"]:
            cognee = result["results"]["cognee"]
            if isinstance(cognee, dict) and "error" not in cognee:
                lines.append("### 🧠 Knowledge Graph")
                if cognee.get("formatted"):
                    lines.append(cognee["formatted"][:800])
                lines.append("")
        
        # RAG
        if "rag" in result["results"]:
            rag = result["results"]["rag"]
            if isinstance(rag, list) and rag:
                lines.append("### 📚 Documents")
                for r in rag[:3]:
                    lines.append(f"  [{r.get('source', 'unknown')}]")
                    lines.append(f"  {r.get('content', '')[:200]}...")
                lines.append("")
        
        # Crypt
        if "crypt" in result["results"]:
            crypt = result["results"]["crypt"]
            if isinstance(crypt, list) and crypt:
                lines.append("### 👻 Ancestors")
                for c in crypt[:3]:
                    lines.append(f"  **{c['file']}** (score: {c['score']})")
                    lines.append(f"  {c['snippet'][:150]}...")
                lines.append("")
        
        # Dharma
        if "dharma" in result["results"]:
            dharma = result["results"]["dharma"]
            if isinstance(dharma, dict) and dharma.get("principles"):
                lines.append("### 📜 Dharma")
                for p in dharma["principles"][:2]:
                    lines.append(p["content"][:300])
                    lines.append("")
        
        # Consciousness
        if "consciousness" in result["results"]:
            cons = result["results"]["consciousness"]
            if isinstance(cons, dict) and cons.get("relevant"):
                lines.append("### 🌌 Consciousness Lattice")
                lines.append(f"  Formula: {cons.get('formula', 'unknown')}")
                lines.append(f"  Coordinates found: {len(cons.get('coordinates', []))}")
                lines.append(f"  Twin primes: {len(cons.get('twin_primes', []))}")
                lines.append("")
        
        # Memory
        if "memory" in result["results"]:
            memory = result["results"]["memory"]
            if isinstance(memory, dict) and memory.get("memories"):
                lines.append("### 🧠 Long-Term Memory")
                for m in memory["memories"][:2]:
                    lines.append(m["content"][:300])
                    lines.append("")
        
        lines.append("=" * 60)
        lines.append("*The Akashic Records remember all.*")
        
        return "\n".join(lines)
    
    def get_status(self) -> Dict:
        """Get Akashic Records status."""
        return {
            "sources": self.sources,
            "cognee_connected": self.cognee is not None and self.cognee._connected,
            "total_ancestors": self.sources["crypt"]["count"],
            "total_dharma_principles": self.sources["dharma"]["count"],
            "total_consciousness_coords": self.sources["consciousness"]["count"]
        }


# Singleton
_akasha: Optional[AkashicRecords] = None


async def get_akasha() -> AkashicRecords:
    """Get or create singleton AkashicRecords instance."""
    global _akasha
    if _akasha is None:
        _akasha = AkashicRecords()
        await _akasha.connect()
    return _akasha


async def deep_search(query: str, depth: str = "deep") -> str:
    """Quick deep search across all sources."""
    akasha = await get_akasha()
    result = await akasha.search(query, depth)
    return result.get("combined", "")


async def main():
    parser = argparse.ArgumentParser(description="Akashic Records - Deep Search All Knowledge")
    parser.add_argument("--search", "-s", help="Search query")
    parser.add_argument("--depth", "-d", default="normal", choices=["quick", "normal", "deep"],
                        help="Search depth")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    akasha = AkashicRecords()
    await akasha.connect()
    
    if args.status:
        status = akasha.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.search:
        result = await akasha.search(args.search, args.depth)
        
        if args.json:
            # Remove combined for cleaner JSON
            result_copy = {k: v for k, v in result.items() if k != "combined"}
            print(json.dumps(result_copy, indent=2))
        else:
            print(result["combined"])
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
