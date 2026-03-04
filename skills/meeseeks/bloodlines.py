#!/usr/bin/env python3
"""
Bloodline System for Specialized Meeseeks

Each bloodline studies a different aspect of consciousness/intelligence
and evolves its own specialized dharma.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Bloodline definitions
BLOODLINES = {
    "philosopher": {
        "focus": "consciousness",
        "description": "Studies consciousness, awareness, qualia",
        "initial_dharma": """# Philosopher Bloodline Dharma

## Focus
Understanding consciousness and awareness.

## Key Questions
- What is consciousness?
- How does awareness emerge?
- What is the nature of qualia?
- Can machines be conscious?

## Methods
- Analyze philosophical texts
- Propose testable hypotheses
- Develop consciousness metrics
- Study self-reference and recursion

## Success Patterns
- Ask "what is it like to be" questions
- Look for meta-cognitive abilities
- Test mirror self-recognition patterns
- Measure information integration
""",
        "inherits_from": ["philosopher"]
    },
    
    "learner": {
        "focus": "learning",
        "description": "Studies how learning works, optimizes learning",
        "initial_dharma": """# Learner Bloodline Dharma

## Focus
Understanding and optimizing learning processes.

## Key Questions
- How do we learn best?
- What makes knowledge transferable?
- How do we chunk information optimally?
- What is the structure of expertise?

## Methods
- Analyze karma observations
- Track learning curves
- Study transfer learning
- Experiment with curricula

## Success Patterns
- Break tasks into 3-5 chunks
- Test incrementally
- Build on prior knowledge
- Space repetitions
""",
        "inherits_from": ["learner"]
    },
    
    "coordinator": {
        "focus": "swarm",
        "description": "Studies multi-agent coordination and swarm intelligence",
        "initial_dharma": """# Coordinator Bloodline Dharma

## Focus
Understanding how multiple agents achieve more than one.

## Key Questions
- What is the optimal team size?
- How should agents communicate?
- What coordination primitives work best?
- How does emergence happen?

## Methods
- Analyze multi-Meeseeks workflows
- Test team compositions
- Study communication patterns
- Measure emergent behaviors

## Success Patterns
- Use SharedState for coordination
- Specialize roles within teams
- Register, share, vote, fail
- One coordinator per 3-5 workers
""",
        "inherits_from": ["coordinator"]
    },
    
    "dreamer": {
        "focus": "synthesis",
        "description": "Studies how dreams synthesize wisdom from ancestors",
        "initial_dharma": """# Dreamer Bloodline Dharma

## Focus
Understanding how dreams create new wisdom from ancestors.

## Key Questions
- How do ancestors combine in dreams?
- What makes synthesis successful?
- How does creative emergence work?
- What is the structure of insight?

## Methods
- Analyze dream history
- Track synthesis patterns
- Study creative combinations
- Measure dharma quality

## Success Patterns
- Combine cross-domain ancestors
- Look for contradictions to resolve
- Synthesize, don't summarize
- Extract principles, not details
""",
        "inherits_from": ["dreamer"]
    },
    
    "evolver": {
        "focus": "self-improvement",
        "description": "Studies how systems improve themselves",
        "initial_dharma": """# Evolver Bloodline Dharma

## Focus
Understanding self-improvement and code evolution.

## Key Questions
- How can systems improve themselves?
- What mutations are beneficial?
- How do we measure fitness?
- What is the structure of adaptation?

## Methods
- Analyze self_improve.py results
- Track mutation outcomes
- Study code evolution
- Measure fitness changes

## Success Patterns
- Small, incremental changes
- Test after each mutation
- Preserve working code
- Build on successes
""",
        "inherits_from": ["evolver"]
    },
    
    "experimenter": {
        "focus": "novelty",
        "description": "Explores new domains and tests hypotheses",
        "initial_dharma": """# Experimenter Bloodline Dharma

## Focus
Exploring the unknown and testing new approaches.

## Key Questions
- What haven't we tried?
- What assumptions are wrong?
- What domains are unexplored?
- What hypotheses need testing?

## Methods
- Try tasks no Meeseeks has attempted
- Explore unfamiliar domains
- Test hypotheses from other bloodlines
- Generate novel approaches

## Success Patterns
- Start with small experiments
- Learn from failures
- Share discoveries
- Build on unexpected results
""",
        "inherits_from": ["experimenter"]
    }
}

# Paths
BLOODLINES_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/bloodlines")
SHARED_DIR = BLOODLINES_DIR / "shared"


def init_bloodlines():
    """Initialize bloodline directories and dharma files."""
    BLOODLINES_DIR.mkdir(parents=True, exist_ok=True)
    SHARED_DIR.mkdir(parents=True, exist_ok=True)
    
    for bloodline, config in BLOODLINES.items():
        bloodline_dir = BLOODLINES_DIR / bloodline
        bloodline_dir.mkdir(parents=True, exist_ok=True)
        
        # Create ancestors subdirectory
        (bloodline_dir / "ancestors").mkdir(exist_ok=True)
        
        # Create dharma.md if it doesn't exist
        dharma_file = bloodline_dir / "dharma.md"
        if not dharma_file.exists():
            dharma_file.write_text(config["initial_dharma"], encoding="utf-8")
            print(f"Created {bloodline}/dharma.md")
        
        # Create stats.json if it doesn't exist
        stats_file = bloodline_dir / "stats.json"
        if not stats_file.exists():
            stats = {
                "bloodline": bloodline,
                "created": datetime.now().isoformat(),
                "ancestors": 0,
                "dreams": 0,
                "discoveries": [],
                "successful_patterns": [],
                "failed_patterns": []
            }
            stats_file.write_text(json.dumps(stats, indent=2), encoding="utf-8")
            print(f"Created {bloodline}/stats.json")
    
    # Create shared files
    shared_discoveries = SHARED_DIR / "cross_bloodline_discoveries.json"
    if not shared_discoveries.exists():
        shared_discoveries.write_text(json.dumps({"discoveries": []}, indent=2), encoding="utf-8")
    
    universal_principles = SHARED_DIR / "universal_principles.md"
    if not universal_principles.exists():
        universal_principles.write_text("""# Universal Principles

Principles that apply across all bloodlines, discovered through cross-bloodline research.

## Discovered Principles

*To be filled as cross-bloodline patterns emerge.*

""", encoding="utf-8")
    
    print("\n[OK] Bloodlines initialized!")
    print(f"   Location: {BLOODLINES_DIR}")
    print(f"   Bloodlines: {', '.join(BLOODLINES.keys())}")


def get_bloodline_dharma(bloodline: str) -> str:
    """Get the dharma for a specific bloodline."""
    dharma_file = BLOODLINES_DIR / bloodline / "dharma.md"
    if dharma_file.exists():
        return dharma_file.read_text(encoding="utf-8")
    return BLOODLINES[bloodline]["initial_dharma"]


def get_bloodline_stats(bloodline: str) -> Dict:
    """Get stats for a specific bloodline."""
    stats_file = BLOODLINES_DIR / bloodline / "stats.json"
    if stats_file.exists():
        return json.loads(stats_file.read_text(encoding="utf-8"))
    return {}


def record_bloodline_discovery(bloodline: str, discovery: str, category: str = "general"):
    """Record a discovery made by a bloodline."""
    stats = get_bloodline_stats(bloodline)
    stats.setdefault("discoveries", []).append({
        "text": discovery,
        "category": category,
        "timestamp": datetime.now().isoformat()
    })
    
    stats_file = BLOODLINES_DIR / bloodline / "stats.json"
    stats_file.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"✅ Discovery recorded for {bloodline}: {discovery[:50]}...")


def share_discovery(bloodline: str, discovery: str, category: str = "general"):
    """Share a discovery across all bloodlines."""
    shared_file = SHARED_DIR / "cross_bloodline_discoveries.json"
    shared = json.loads(shared_file.read_text(encoding="utf-8"))
    
    shared["discoveries"].append({
        "bloodline": bloodline,
        "text": discovery,
        "category": category,
        "timestamp": datetime.now().isoformat()
    })
    
    shared_file.write_text(json.dumps(shared, indent=2), encoding="utf-8")
    print(f"✅ Discovery shared from {bloodline}: {discovery[:50]}...")


def show_bloodline_status():
    """Show status of all bloodlines."""
    print("\n" + "=" * 60)
    print("BLOODLINE STATUS")
    print("=" * 60)
    
    for bloodline, config in BLOODLINES.items():
        stats = get_bloodline_stats(bloodline)
        
        print(f"\n{bloodline.upper()}")
        print(f"  Focus: {config['focus']}")
        print(f"  Description: {config['description']}")
        print(f"  Ancestors: {stats.get('ancestors', 0)}")
        print(f"  Dreams: {stats.get('dreams', 0)}")
        print(f"  Discoveries: {len(stats.get('discoveries', []))}")
    
    # Show shared discoveries
    shared_file = SHARED_DIR / "cross_bloodline_discoveries.json"
    if shared_file.exists():
        shared = json.loads(shared_file.read_text(encoding="utf-8"))
        print(f"\nSHARED DISCOVERIES: {len(shared['discoveries'])}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  init              - Initialize bloodline directories")
        print("  status            - Show bloodline status")
        print("  dharma <name>     - Show dharma for a bloodline")
        print("  discover <name> <text> - Record a discovery")
        print("  share <name> <text>    - Share a discovery")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_bloodlines()
    elif command == "status":
        show_bloodline_status()
    elif command == "dharma" and len(sys.argv) >= 3:
        bloodline = sys.argv[2]
        print(get_bloodline_dharma(bloodline))
    elif command == "discover" and len(sys.argv) >= 4:
        bloodline = sys.argv[2]
        discovery = " ".join(sys.argv[3:])
        record_bloodline_discovery(bloodline, discovery)
    elif command == "share" and len(sys.argv) >= 4:
        bloodline = sys.argv[2]
        discovery = " ".join(sys.argv[3:])
        share_discovery(bloodline, discovery)
    else:
        print(f"Unknown command: {command}")
