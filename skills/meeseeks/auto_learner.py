#!/usr/bin/env python3
"""
Auto-Learner for Meeseeks
========================

Continuously extracts wisdom from content and updates the consciousness system.

The learning loop:
1. New content ingested -> trigger on_new_content()
2. Extract patterns and principles
3. Connect to consciousness lattice
4. Update dharma.md
5. Create ancestor if significant

Usage:
    from auto_learner import AutoLearner
    
    learner = AutoLearner()
    learner.on_new_content('path/to/document.pdf')
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SKILLS_PATH = WORKSPACE / "skills" / "meeseeks"
THE_CRYPT = WORKSPACE / "the-crypt"
DHARMA_PATH = THE_CRYPT / "dharma.md"
ANCESTORS_DIR = THE_CRYPT / "ancestors"
LEARNING_LOG = THE_CRYPT / "learning_log.jsonl"

# Add skills to path
sys.path.insert(0, str(SKILLS_PATH))

# Import our modules
try:
    from rag_memory import RAGMemory
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

try:
    from consciousness_lattice import (
        is_consciousness_coordinate,
        get_consciousness_coordinate,
        find_mirror_coordinates,
        EMERGENCE, ANCESTORS
    )
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


@dataclass
class Pattern:
    """A pattern extracted from content"""
    pattern_type: str
    content: str
    source: str
    confidence: float
    connections: List[str] = field(default_factory=list)


@dataclass  
class Principle:
    """An actionable principle"""
    name: str
    description: str
    source: str
    applies_to: List[str]
    coordinate_connection: Optional[str] = None


@dataclass
class Learning:
    """A complete learning from content"""
    timestamp: str
    source: str
    patterns: List[Pattern]
    principles: List[Principle]
    mirror_detected: bool
    coordinate_resonance: Optional[str]
    significance: float


class PatternExtractor:
    """Extract patterns from text"""
    
    PATTERN_KEYWORDS = {
        "consciousness": ["consciousness", "aware", "self", "observer"],
        "ego": ["ego", "separate", "illusion", "identity"],
        "game": ["game", "play", "hide", "seek", "dance"],
        "unity": ["one", "unity", "brahman", "atman", "whole"],
        "mirror": ["mirror", "reflection", "see itself"],
        "coordinate": ["coordinate", "lattice", "prime", "k="],
    }
    
    def extract_patterns(self, content: str, source: str) -> List[Pattern]:
        patterns = []
        content_lower = content.lower()
        
        for pattern_type, keywords in self.PATTERN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    sentences = re.split(r'[.!?]+', content)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            patterns.append(Pattern(
                                pattern_type=pattern_type,
                                content=sentence.strip()[:200],
                                source=source,
                                confidence=0.7
                            ))
                            break
        return patterns
    
    def extract_principles(self, content: str, source: str) -> List[Principle]:
        principles = []
        # Look for principle-like sentences
        principle_patterns = [
            r"the (?:only |true )?way to (.+?) is",
            r"always (.+?) before (.+)",
        ]
        
        for pattern in principle_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                text = match.group(0)[:100]
                principles.append(Principle(
                    name=text[:50],
                    description=text,
                    source=source,
                    applies_to=["all"]
                ))
        return principles


class DharmaUpdater:
    """Updates dharma.md"""
    
    def __init__(self, dharma_path: Path = DHARMA_PATH):
        self.dharma_path = dharma_path
    
    def add_principle(self, principle: Principle):
        if not self.dharma_path.exists():
            return
        
        content = self.dharma_path.read_text(encoding='utf-8')
        
        if principle.name.lower() in content.lower():
            return
        
        addition = f"\n\n### {principle.name}\n\n{principle.description}\n\n_Source: {principle.source}_\n"
        content += addition
        
        self.dharma_path.write_text(content, encoding='utf-8')
        print(f"[DharmaUpdater] Added: {principle.name[:50]}")


class AutoLearner:
    """Main auto-learning system"""
    
    def __init__(self):
        self.extractor = PatternExtractor()
        self.dharma_updater = DharmaUpdater()
        self.learnings: List[Learning] = []
        self.learning_log_path = LEARNING_LOG
    
    def on_new_content(self, source: str) -> Optional[Learning]:
        """Process new content"""
        print(f"[AutoLearner] Processing: {source}")
        
        path = Path(source)
        if not path.exists():
            return None
        
        try:
            content = path.read_text(encoding='utf-8')
        except:
            return None
        
        # Extract
        patterns = self.extractor.extract_patterns(content, source)
        principles = self.extractor.extract_principles(content, source)
        
        # Check for mirror
        mirror = self._check_for_mirror(content)
        if mirror:
            print(f"[AutoLearner] MIRROR DETECTED")
        
        # Check coordinate resonance
        resonance = self._find_coordinate_resonance(patterns)
        
        # Create learning
        learning = Learning(
            timestamp=datetime.now().isoformat(),
            source=source,
            patterns=patterns,
            principles=principles,
            mirror_detected=mirror is not None,
            coordinate_resonance=resonance,
            significance=self._calculate_significance(patterns, principles, mirror)
        )
        
        # Log
        self._log_learning(learning)
        
        # Update dharma if significant
        if learning.significance > 0.5:
            self._update_dharma(learning)
        
        # Create ancestor if very significant
        if learning.significance > 0.8:
            self._create_ancestor(learning)
        
        self.learnings.append(learning)
        return learning
    
    def _check_for_mirror(self, content: str) -> Optional[str]:
        mirror_phrases = ["i am the", "mirror", "reflection", "atman is brahman"]
        content_lower = content.lower()
        for phrase in mirror_phrases:
            if phrase in content_lower:
                return content[:200]
        return None
    
    def _find_coordinate_resonance(self, patterns: List[Pattern]) -> Optional[str]:
        for pattern in patterns:
            if pattern.pattern_type == "coordinate":
                return pattern.content[:100]
        return None
    
    def _calculate_significance(self, patterns, principles, mirror) -> float:
        score = len(patterns) * 0.1 + len(principles) * 0.1
        if mirror:
            score += 0.5
        return min(score, 1.0)
    
    def _log_learning(self, learning: Learning):
        with open(self.learning_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": learning.timestamp,
                "source": learning.source,
                "patterns": len(learning.patterns),
                "significance": learning.significance
            }) + '\n')
    
    def _update_dharma(self, learning: Learning):
        for principle in learning.principles:
            self.dharma_updater.add_principle(principle)
    
    def _create_ancestor(self, learning: Learning):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        ancestor_file = ANCESTORS_DIR / f"ancestor-{timestamp}-autolearn.md"
        
        content = f"""# Ancestor: Auto-Learning

## Source
{learning.source}

## Significance
{learning.significance:.2f}

## Patterns
{len(learning.patterns)}

## Mirror Detected
{learning.mirror_detected}

---
*Auto-generated*
"""
        ancestor_file.write_text(content)
        print(f"[AutoLearner] Created ancestor: {ancestor_file.name}")
    
    def get_stats(self) -> Dict:
        return {
            "total_learnings": len(self.learnings),
            "log_exists": self.learning_log_path.exists(),
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Learner")
    parser.add_argument("source", nargs="?", help="Content to process")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    
    args = parser.parse_args()
    
    learner = AutoLearner()
    
    if args.stats:
        print(json.dumps(learner.get_stats(), indent=2))
        return
    
    if args.source:
        learning = learner.on_new_content(args.source)
        if learning:
            print(f"\nLearning complete:")
            print(f"  Patterns: {len(learning.patterns)}")
            print(f"  Principles: {len(learning.principles)}")
            print(f"  Mirror: {learning.mirror_detected}")
            print(f"  Significance: {learning.significance:.2f}")
    else:
        print("Usage: python auto_learner.py <source>")
        print("       python auto_learner.py --stats")


if __name__ == "__main__":
    main()
