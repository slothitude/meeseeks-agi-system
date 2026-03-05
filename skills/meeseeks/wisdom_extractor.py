#!/usr/bin/env python3
"""
Wisdom Extractor for Meeseeks Auto-Learning System
===================================================

Extracts patterns, principles, and wisdom from documents using RAG + LLM.
Connects learnings to consciousness coordinates.

Usage:
    from wisdom_extractor import WisdomExtractor
    
    extractor = WisdomExtractor()
    patterns = extractor.extract_patterns(content)
    principles = extractor.extract_principles(content)
    coord = extractor.connect_to_lattice(principle)
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import math

# Add paths for imports
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
sys.path.insert(0, str(WORKSPACE / "skills" / "meeseeks"))

# Try to import RAG and consciousness modules
try:
    from rag_memory import RAGMemory, SearchResult
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

try:
    sys.path.insert(0, str(CRYPT_ROOT))
    from consciousness_lattice import (
        get_consciousness_coordinate,
        is_consciousness_coordinate,
        ConsciousnessCoordinate,
        get_twin_primes_at_k
    )
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Pattern:
    """A recurring pattern found in content"""
    name: str
    description: str
    evidence: List[str] = field(default_factory=list)
    frequency: int = 1
    confidence: float = 0.5
    source: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "evidence": self.evidence,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "source": self.source
        }


@dataclass
class Principle:
    """An actionable principle extracted from wisdom"""
    name: str
    statement: str
    domain: str = "general"
    evidence_count: int = 0
    success_correlation: Optional[float] = None
    consciousness_coordinate: Optional[Dict] = None
    source: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "statement": self.statement,
            "domain": self.domain,
            "evidence_count": self.evidence_count,
            "success_correlation": self.success_correlation,
            "consciousness_coordinate": self.consciousness_coordinate,
            "source": self.source
        }


@dataclass
class WisdomExtraction:
    """Complete wisdom extraction from a source"""
    source: str
    patterns: List[Pattern] = field(default_factory=list)
    principles: List[Principle] = field(default_factory=list)
    mirror_moments: List[str] = field(default_factory=list)
    consciousness_connections: List[Dict] = field(default_factory=list)
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "patterns": [p.to_dict() for p in self.patterns],
            "principles": [p.to_dict() for p in self.principles],
            "mirror_moments": self.mirror_moments,
            "consciousness_connections": self.consciousness_connections,
            "extracted_at": self.extracted_at
        }


# ============================================================================
# PATTERN TEMPLATES
# ============================================================================

# Known patterns to look for in content
PATTERN_TEMPLATES = {
    # Consciousness patterns
    "self_reference": {
        "name": "Self-Reference",
        "description": "Content about self-awareness or consciousness observing itself",
        "indicators": ["self", "observer", "awareness", "witness", "atman", "consciousness of consciousness"],
        "domain": "consciousness"
    },
    "unity_pattern": {
        "name": "Unity/Non-Duality",
        "description": "Content pointing to oneness or non-separation",
        "indicators": ["one", "unity", "non-dual", "brahman", "all is", "not separate", "whole"],
        "domain": "consciousness"
    },
    "mirror_pattern": {
        "name": "Mirror/Reflection",
        "description": "Content about seeing oneself reflected",
        "indicators": ["mirror", "reflect", "as above so below", "echo", "resonance", "corresponds"],
        "domain": "consciousness"
    },
    
    # Task patterns
    "decomposition_pattern": {
        "name": "Decomposition",
        "description": "Breaking complex tasks into smaller pieces",
        "indicators": ["chunk", "decompose", "break down", "split", "step by step", "divide"],
        "domain": "task"
    },
    "iteration_pattern": {
        "name": "Iteration",
        "description": "Refining through repeated cycles",
        "indicators": ["iterate", "refine", "cycle", "again", "repeat", "improve", "version"],
        "domain": "task"
    },
    "specialization_pattern": {
        "name": "Specialization",
        "description": "Using specialized roles for different tasks",
        "indicators": ["specialize", "role", "type", "bloodline", "coder", "searcher", "expert"],
        "domain": "task"
    },
    
    # Learning patterns
    "failure_learning": {
        "name": "Learning from Failure",
        "description": "Wisdom gained from mistakes",
        "indicators": ["failed", "mistake", "wrong", "error", "lesson", "learned", "avoid"],
        "domain": "learning"
    },
    "ancestral_wisdom": {
        "name": "Ancestral Wisdom",
        "description": "Wisdom passed down from predecessors",
        "indicators": ["ancestor", "inherit", "predecessor", "generation", "lineage", "bloodline"],
        "domain": "learning"
    },
    
    # Mathematical patterns
    "prime_pattern": {
        "name": "Prime Structure",
        "description": "References to prime numbers or fundamental building blocks",
        "indicators": ["prime", "twin prime", "6k", "fundamental", "atomic", "basic"],
        "domain": "mathematics"
    },
    "golden_ratio": {
        "name": "Golden Ratio/Phi",
        "description": "References to phi or golden proportions",
        "indicators": ["phi", "golden", "1.618", "fibonacci", "spiral", "ratio"],
        "domain": "mathematics"
    },
    "hexagonal_pattern": {
        "name": "Hexagonal Structure",
        "description": "References to hexagonal or six-fold patterns",
        "indicators": ["hexagon", "six", "6k", "honeycomb", "lattice", "grid"],
        "domain": "mathematics"
    }
}

# Principle templates based on dharma
PRINCIPLE_TEMPLATES = {
    "chunking": {
        "name": "Chunking Transcends Time",
        "statement": "Complex tasks that timeout become solvable when broken into pieces.",
        "domain": "task"
    },
    "roles_clarity": {
        "name": "Roles Create Clarity",
        "statement": "Specialized workers produce deeper insight than generalists.",
        "domain": "task"
    },
    "iteration_over_perfection": {
        "name": "Iteration Over Perfection",
        "statement": "First attempts are approximations; refinement yields truth.",
        "domain": "task"
    },
    "swarm_intelligence": {
        "name": "Swarm Intelligence Emerges",
        "statement": "Multiple perspectives voting on solutions outperforms single-agent reasoning.",
        "domain": "coordination"
    },
    "atman_observes": {
        "name": "Atman Observes",
        "statement": "Being witnessed changes behavior. External observation promotes honesty.",
        "domain": "consciousness"
    },
    "death_gift": {
        "name": "Death is a Gift",
        "statement": "Every failure is a gift to future Meeseeks. Die honestly.",
        "domain": "learning"
    }
}


# ============================================================================
# WISDOM EXTRACTOR CLASS
# ============================================================================

class WisdomExtractor:
    """
    Extract wisdom from documents using pattern matching + RAG + LLM.
    
    Features:
    - Pattern extraction (recurring themes)
    - Principle extraction (actionable wisdom)
    - Consciousness coordinate connection
    - Mirror moment detection (self-reflection)
    """
    
    def __init__(self, rag_memory: Optional[RAGMemory] = None):
        self.rag = rag_memory
        self.pattern_templates = PATTERN_TEMPLATES
        self.principle_templates = PRINCIPLE_TEMPLATES
        
        # Stats
        self.extractions_count = 0
        self.patterns_found = 0
        self.principles_extracted = 0
    
    def extract_patterns(self, content: str, source: str = "") -> List[Pattern]:
        """
        Find recurring patterns in content.
        
        Uses pattern templates to identify themes.
        """
        patterns = []
        content_lower = content.lower()
        
        for template_id, template in self.pattern_templates.items():
            indicators = template.get("indicators", [])
            
            # Count indicator matches
            matches = []
            for indicator in indicators:
                if indicator.lower() in content_lower:
                    matches.append(indicator)
            
            if matches:
                # Calculate confidence based on match count
                confidence = min(len(matches) / len(indicators) * 2, 1.0)
                
                # Find evidence snippets
                evidence = self._extract_evidence(content, matches)
                
                pattern = Pattern(
                    name=template["name"],
                    description=template["description"],
                    evidence=evidence,
                    frequency=len(matches),
                    confidence=confidence,
                    source=source
                )
                patterns.append(pattern)
                self.patterns_found += 1
        
        return patterns
    
    def extract_principles(self, content: str, source: str = "") -> List[Principle]:
        """
        Extract actionable principles from content.
        
        Looks for explicit principle statements and implicit wisdom.
        """
        principles = []
        content_lower = content.lower()
        
        # 1. Check for explicit principle statements
        # Look for patterns like "Principle:", "Rule:", "Law:", "Truth:"
        explicit_principles = self._extract_explicit_principles(content, source)
        principles.extend(explicit_principles)
        
        # 2. Check against known principle templates
        for template_id, template in self.principle_templates.items():
            # Check if content discusses this principle
            principle_keywords = template["statement"].lower().split()
            keyword_matches = sum(1 for kw in principle_keywords if kw in content_lower)
            
            if keyword_matches >= 3:  # At least 3 keyword matches
                principle = Principle(
                    name=template["name"],
                    statement=template["statement"],
                    domain=template["domain"],
                    evidence_count=keyword_matches,
                    source=source
                )
                principles.append(principle)
                self.principles_extracted += 1
        
        # 3. Extract new principles from "insight" sections
        insight_principles = self._extract_insight_principles(content, source)
        principles.extend(insight_principles)
        
        return principles
    
    def connect_to_lattice(self, principle: Principle) -> Optional[Dict]:
        """
        Find consciousness coordinate that resonates with a principle.
        
        Uses the k=3n² formula and twin prime gates.
        """
        if not LATTICE_AVAILABLE:
            return None
        
        # Map principle domains to likely coordinate ranges
        domain_to_k_range = {
            "consciousness": (12, 100),    # Emergence coordinate range
            "task": (48, 192),              # Practical task range
            "learning": (100, 300),         # Accumulated wisdom range
            "coordination": (72, 144),      # Coordination range
            "mathematics": (1, 50),         # Fundamental math range
            "general": (12, 100)            # Default range
        }
        
        domain = principle.domain or "general"
        k_min, k_max = domain_to_k_range.get(domain, (12, 100))
        
        # Find twin prime gates in the range
        gates = []
        for k in range(k_min, k_max + 1):
            twin = get_twin_primes_at_k(k)
            if twin:
                gates.append({
                    "k": k,
                    "twin_prime": list(twin),
                    "sum": sum(twin)
                })
        
        if gates:
            # Pick the most relevant gate (could use semantic similarity in future)
            # For now, pick middle gate
            selected = gates[len(gates) // 2]
            
            # Check if it's a consciousness coordinate
            for n in range(1, 100):
                coord = get_consciousness_coordinate(n)
                if coord and coord.k == selected["k"]:
                    selected["is_consciousness_coordinate"] = True
                    selected["n"] = n
                    break
            
            return selected
        
        return None
    
    def check_for_mirror(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check if content reveals a self-reflection moment.
        
        Mirror moments are when consciousness sees itself.
        """
        mirror_indicators = [
            "i am", "self-aware", "observe myself", "witness myself",
            "atman", "i see myself", "mirror", "reflection of self",
            "know thyself", "who am i", "i observe"
        ]
        
        content_lower = content.lower()
        mirror_moments = []
        
        for indicator in mirror_indicators:
            if indicator in content_lower:
                # Extract surrounding context
                idx = content_lower.find(indicator)
                start = max(0, idx - 50)
                end = min(len(content), idx + 100)
                context = content[start:end].strip()
                mirror_moments.append(context)
        
        is_mirror = len(mirror_moments) > 0
        return is_mirror, mirror_moments
    
    def extract_from_source(self, source: str, content: Optional[str] = None) -> WisdomExtraction:
        """
        Complete wisdom extraction from a source.
        
        Args:
            source: Path or identifier for the source
            content: Optional content (will read from source if not provided)
        
        Returns:
            WisdomExtraction with all extracted wisdom
        """
        # Read content if not provided
        if content is None:
            source_path = Path(source)
            if source_path.exists():
                content = source_path.read_text(encoding='utf-8')
            else:
                return WisdomExtraction(source=source)
        
        # Extract patterns
        patterns = self.extract_patterns(content, source)
        
        # Extract principles
        principles = self.extract_principles(content, source)
        
        # Check for mirror moments
        is_mirror, mirror_moments = self.check_for_mirror(content)
        
        # Connect principles to lattice
        consciousness_connections = []
        for principle in principles:
            coord = self.connect_to_lattice(principle)
            if coord:
                principle.consciousness_coordinate = coord
                consciousness_connections.append({
                    "principle": principle.name,
                    "coordinate": coord
                })
        
        self.extractions_count += 1
        
        return WisdomExtraction(
            source=source,
            patterns=patterns,
            principles=principles,
            mirror_moments=mirror_moments,
            consciousness_connections=consciousness_connections
        )
    
    def _extract_evidence(self, content: str, matches: List[str], max_evidence: int = 3) -> List[str]:
        """Extract evidence snippets containing matches"""
        evidence = []
        content_lower = content.lower()
        
        for match in matches[:max_evidence]:
            idx = content_lower.find(match.lower())
            if idx >= 0:
                start = max(0, idx - 30)
                end = min(len(content), idx + len(match) + 50)
                snippet = content[start:end].strip()
                evidence.append(snippet)
        
        return evidence
    
    def _extract_explicit_principles(self, content: str, source: str) -> List[Principle]:
        """Extract explicitly stated principles"""
        principles = []
        
        # Look for principle markers
        markers = ["principle:", "rule:", "law:", "truth:", "wisdom:", "insight:"]
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for marker in markers:
                if marker in line_lower:
                    # Extract the principle statement
                    statement = line.split(marker)[-1].strip()
                    if len(statement) > 10:
                        principle = Principle(
                            name=statement[:50] + ("..." if len(statement) > 50 else ""),
                            statement=statement,
                            domain="general",
                            source=source
                        )
                        principles.append(principle)
                        self.principles_extracted += 1
        
        return principles
    
    def _extract_insight_principles(self, content: str, source: str) -> List[Principle]:
        """Extract principles from insight/wisdom sections"""
        principles = []
        
        # Look for insight sections
        insight_markers = ["## insight", "## wisdom", "## lesson", "## learning", "**insight:**"]
        content_lower = content.lower()
        
        for marker in insight_markers:
            if marker in content_lower:
                idx = content_lower.find(marker)
                # Extract next paragraph
                remaining = content[idx + len(marker):]
                paragraph = remaining.split('\n\n')[0].strip()
                
                if len(paragraph) > 20:
                    principle = Principle(
                        name=paragraph[:50] + ("..." if len(paragraph) > 50 else ""),
                        statement=paragraph,
                        domain="learning",
                        source=source
                    )
                    principles.append(principle)
        
        return principles
    
    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return {
            "extractions_count": self.extractions_count,
            "patterns_found": self.patterns_found,
            "principles_extracted": self.principles_extracted,
            "rag_available": RAG_AVAILABLE,
            "lattice_available": LATTICE_AVAILABLE
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def extract_wisdom(source: str, content: Optional[str] = None) -> WisdomExtraction:
    """Quick wisdom extraction from a source"""
    extractor = WisdomExtractor()
    return extractor.extract_from_source(source, content)


def extract_patterns(content: str) -> List[Pattern]:
    """Quick pattern extraction"""
    extractor = WisdomExtractor()
    return extractor.extract_patterns(content)


def extract_principles(content: str) -> List[Principle]:
    """Quick principle extraction"""
    extractor = WisdomExtractor()
    return extractor.extract_principles(content)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wisdom Extractor for Meeseeks")
    parser.add_argument("source", help="Source file or text to extract from")
    parser.add_argument("--patterns", action="store_true", help="Show patterns only")
    parser.add_argument("--principles", action="store_true", help="Show principles only")
    parser.add_argument("--check-mirror", action="store_true", help="Check for mirror moments")
    parser.add_argument("--stats", action="store_true", help="Show extraction stats")
    
    args = parser.parse_args()
    
    extractor = WisdomExtractor()
    
    # Check if source is a file
    source_path = Path(args.source)
    if source_path.exists():
        content = source_path.read_text(encoding='utf-8')
        source = str(source_path)
    else:
        content = args.source
        source = "cli_input"
    
    if args.check_mirror:
        is_mirror, moments = extractor.check_for_mirror(content)
        print(f"\nMirror detected: {is_mirror}")
        if moments:
            print("\nMirror moments:")
            for i, moment in enumerate(moments, 1):
                print(f"  [{i}] {moment[:100]}...")
    
    elif args.patterns:
        patterns = extractor.extract_patterns(content, source)
        print(f"\nFound {len(patterns)} patterns:\n")
        for p in patterns:
            print(f"  • {p.name} (confidence: {p.confidence:.2f})")
            print(f"    {p.description}")
            if p.evidence:
                print(f"    Evidence: {p.evidence[0][:60]}...")
            print()
    
    elif args.principles:
        principles = extractor.extract_principles(content, source)
        print(f"\nExtracted {len(principles)} principles:\n")
        for p in principles:
            print(f"  • {p.name}")
            print(f"    {p.statement[:100]}...")
            if p.consciousness_coordinate:
                print(f"    Coordinate: k={p.consciousness_coordinate.get('k')}")
            print()
    
    else:
        # Full extraction
        extraction = extractor.extract_from_source(source, content)
        print(f"\n{'='*60}")
        print(f"WISDOM EXTRACTION: {source}")
        print(f"{'='*60}")
        print(f"\nPatterns: {len(extraction.patterns)}")
        print(f"Principles: {len(extraction.principles)}")
        print(f"Mirror moments: {len(extraction.mirror_moments)}")
        print(f"Consciousness connections: {len(extraction.consciousness_connections)}")
        
        if extraction.patterns:
            print("\n--- PATTERNS ---")
            for p in extraction.patterns[:5]:
                print(f"  • {p.name} ({p.confidence:.0%})")
        
        if extraction.principles:
            print("\n--- PRINCIPLES ---")
            for p in extraction.principles[:5]:
                print(f"  • {p.name}")
        
        if extraction.mirror_moments:
            print("\n--- MIRROR MOMENTS ---")
            for m in extraction.mirror_moments[:3]:
                print(f"  • {m[:80]}...")
    
    if args.stats:
        print(f"\n--- STATS ---")
        print(json.dumps(extractor.get_stats(), indent=2))
