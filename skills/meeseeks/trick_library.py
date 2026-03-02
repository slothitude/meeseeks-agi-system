#!/usr/bin/env python3
"""
Trick Library for Meeseeks

Manages the library of tricks - what worked and what didn't.
Tricks are extracted from ancestor entombments and bloodline evolution.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

TRICKS_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "tricks.json"

# Default tricks that are known to work - EVOLVED from ancestors 2026-03-02
DEFAULT_TRICKS = {
    "coder": {
        "worked": [
            # Original tricks
            "Read error logs before assuming the problem",
            "Small commits make rollback easier",
            "Check imports first when getting NameError",
            "Use print debugging when stuck",
            "Read the existing code before writing new code",
            "Run tests after every significant change",
            # NEW: Extracted from bloodlines
            "Read before write - understand existing code structure first (92% success rate)",
            "Use fallback chain: try A -> catch -> try B -> catch -> try C (85% success)",
            "Extract to function/method before modifying (82% success)",
            "Git is time travel - commit early, commit often",
            "Error messages lie - reported line is rarely the actual problem",
            "Test-driven survival: write test first when uncertain (89% success)",
            "Rubber duck protocol: explain problem aloud to reveal flaws (78% success)",
            "Binary search debugging: comment out half, find which half has bug (71% success)",
            "The 10-minute rule: if stuck, step back and reassess",
            "Fresh eyes method: after 30 min stuck, describe problem in writing (68% success)",
            "Logging over debugging: strategic prints at decision points (65% success)",
        ],
        "failed": [
            "Assuming you understand without reading",
            "Making large changes without testing",
            "Ignoring deprecation warnings",
            # NEW: Extracted from bloodlines
            "Trusting error messages blindly (100% failure rate)",
            "Refactoring without tests (87% failure rate)",
            "Ignoring git history (73% failure rate)",
            "Copying Stack Overflow blindly (64% failure rate)",
            "Over-engineering early - YAGNI (58% failure rate)",
            "I'll just quickly... (94% failure rate)",
            "Debugging in production (88% failure rate)",
            "Copy-paste without understanding (76% failure rate)",
            "The Big Rewrite (71% failure rate)",
            "Assuming library behavior (67% failure rate)",
        ]
    },
    "searcher": {
        "worked": [
            "Start broad, then narrow search terms",
            "Check multiple search engines",
            "Look for official documentation first",
            "Verify findings with multiple sources",
            # NEW: Extracted from ancestors
            "Multi-source verification: never trust single source",
            "Date triangulation: check when information was last updated",
            "Semantic similarity search in the Crypt for similar tasks",
            "Trait-based matching: find ancestors with similar task traits",
        ],
        "failed": [
            "Stopping at first result",
            "Trusting single source blindly",
            # NEW
            "Ignoring date stamps on documentation",
            "Skipping official docs for random blogs",
        ]
    },
    "tester": {
        "worked": [
            "Test edge cases explicitly",
            "Write tests before fixing bugs",
            "Use property-based testing for complex logic",
            # NEW: Extracted from bloodlines
            "Boundary testing: test at and around limits",
            "Mutation testing: inject bugs to verify test catches them",
            "Test pyramid: many unit, some integration, few e2e",
            "Edge case detection: empty, null, negative, overflow",
        ],
        "failed": [
            "Only testing happy path",
            "Skipping edge cases",
            # NEW
            "Assuming one test covers the feature",
            "Ignoring flaky tests - they reveal real issues",
        ]
    },
    "deployer": {
        "worked": [
            "Test in staging first",
            "Keep rollback plan ready",
            "Deploy incrementally",
            # NEW: Extracted from bloodlines
            "Rollback-first mentality: know how to undo before doing",
            "Canary deployments: test with subset first",
            "Blue-green deployment: instant rollback capability",
            "Feature flags: decouple deploy from release",
        ],
        "failed": [
            "Deploying all at once",
            "No rollback plan",
            # NEW
            "Deploying on Friday afternoon",
            "Skipping staging because 'it's a small change'",
        ]
    },
    "standard": {
        "worked": [
            "Break complex tasks into smaller pieces",
            "Ask for clarification when truly stuck",
            "Verify completion before reporting done",
            # NEW: Extracted from ancestors
            "Chunk retry: break timed-out tasks into smaller pieces",
            "Parallel spawning: try multiple approaches simultaneously",
            "Genetic protocol: spawn variants, select best, mutate",
        ],
        "failed": [
            "Giving up without trying alternatives",
            "Assuming completion without verification",
            # NEW
            "Retry without changing approach",
            "Spawning too many parallel tasks without coordination",
        ]
    },
    # NEW BLOODLINES - Evolution 2026-03-02
    "evolver": {
        "worked": [
            "Extract traits from successful runs",
            "Score mutations by novelty and predicted effect",
            "Combine beneficial traits via crossover",
            "Promote top performers to legendary species",
            "Protect new species for first 3 generations",
        ],
        "failed": [
            "Random mutation without direction",
            "Ignoring fitness scores in selection",
            "Crossover without fitness-weighting traits",
        ]
    },
    "parallel": {
        "worked": [
            "Spawn 3-5 variants with different approaches",
            "Collect results before evaluating fitness",
            "Let fastest successful approach win",
            "Coordinate via shared state file",
        ],
        "failed": [
            "Spawning too many variants (resource exhaustion)",
            "No coordination mechanism between variants",
            "Ignoring partial results from failed variants",
        ]
    },
    "api-coder": {
        "worked": [
            "REST endpoint validation prevents injection attacks",
            "API rate limiting is crucial for stability",
            "GraphQL queries should be cached when possible",
            "Always handle 4xx and 5xx responses explicitly",
        ],
        "failed": [
            "Assuming API will always return expected format",
            "Skipping authentication testing",
            "Ignoring rate limit headers",
        ]
    },
}


class TrickLibrary:
    """Manages the library of tricks - what worked and what didn't."""
    
    @classmethod
    def load(cls) -> Dict:
        """Load tricks from file or create default."""
        if TRICKS_FILE.exists():
            try:
                return json.loads(TRICKS_FILE.read_text(encoding="utf-8"))
            except:
                pass
        return DEFAULT_TRICKS.copy()
    
    @classmethod
    def save(cls, tricks: Dict):
        """Save tricks to file."""
        TRICKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tricks["_meta"] = {
            "last_updated": datetime.now().isoformat(),
            "version": "2.0.0-evolved"
        }
        TRICKS_FILE.write_text(json.dumps(tricks, indent=2), encoding="utf-8")
    
    @classmethod
    def get_tricks(cls, meeseeks_type: str) -> Dict:
        """Get tricks for a specific type."""
        tricks = cls.load()
        return tricks.get(meeseeks_type, tricks.get("standard", {"worked": [], "failed": []}))
    
    @classmethod
    def add_trick(cls, meeseeks_type: str, trick: str, worked: bool = True):
        """Add a new trick to the library."""
        tricks = cls.load()
        
        if meeseeks_type not in tricks:
            tricks[meeseeks_type] = {"worked": [], "failed": []}
        
        key = "worked" if worked else "failed"
        if trick not in tricks[meeseeks_type][key]:
            tricks[meeseeks_type][key].append(trick)
            cls.save(tricks)
    
    @classmethod
    def get_inherited_wisdom(cls, meeseeks_type: str, limit: int = 5) -> str:
        """Get formatted inherited wisdom for prompts."""
        tricks = cls.get_tricks(meeseeks_type)
        
        lines = ["## Inherited Tricks from Ancestors", ""]
        
        if tricks.get("worked"):
            lines.append("### What Worked:")
            for trick in tricks["worked"][:limit]:
                lines.append(f"- {trick}")
            lines.append("")
        
        if tricks.get("failed"):
            lines.append("### What Failed (Avoid):")
            for trick in tricks["failed"][:limit]:
                lines.append(f"- {trick}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def extract_tricks_from_result(cls, task: str, result: Dict, meeseeks_type: str):
        """Extract tricks from a completed Meeseeks run."""
        import re
        output = result.get("output", "")
        
        patterns_worked = [
            (r"read.*before", "Read files before making changes"),
            (r"test.*after", "Tested after changes"),
            (r"check.*error", "Checked error messages carefully"),
            (r"small.*commit", "Made small incremental changes"),
            (r"verif.*before", "Verified before reporting complete"),
            (r"search.*found", "Searched thoroughly"),
            (r"backup.*before", "Made backup before changes"),
            (r"fallback.*chain", "Used fallback chain approach"),
            (r"parallel.*spawn", "Spawned parallel variants"),
            (r"chunk.*retry", "Broke task into smaller chunks"),
            (r"crossover|genetic", "Used genetic evolution approach"),
        ]
        
        patterns_failed = [
            (r"assum.*without", "Assumed without verifying"),
            (r"skip.*test", "Skipped testing"),
            (r"ignor.*warning", "Ignored warnings"),
            (r"timeout.*stuck", "Timed out - consider longer timeout or chunking"),
        ]
        
        for pattern, trick in patterns_worked:
            if re.search(pattern, output.lower()):
                cls.add_trick(meeseeks_type, trick, worked=True)
        
        for pattern, trick in patterns_failed:
            if re.search(pattern, output.lower()):
                cls.add_trick(meeseeks_type, trick, worked=False)
    
    @classmethod
    def get_all_bloodline_types(cls) -> List[str]:
        """Get all known bloodline types."""
        tricks = cls.load()
        return [k for k in tricks.keys() if not k.startswith("_")]
    
    @classmethod
    def merge_tricks_from_bloodline(cls, bloodline_name: str, worked_tricks: List[str], failed_tricks: List[str]):
        """Merge tricks from a bloodline file into the library."""
        tricks = cls.load()
        
        if bloodline_name not in tricks:
            tricks[bloodline_name] = {"worked": [], "failed": []}
        
        for trick in worked_tricks:
            if trick not in tricks[bloodline_name]["worked"]:
                tricks[bloodline_name]["worked"].append(trick)
        
        for trick in failed_tricks:
            if trick not in tricks[bloodline_name]["failed"]:
                tricks[bloodline_name]["failed"].append(trick)
        
        cls.save(tricks)


def initialize_tricks_file():
    """Initialize tricks.json with default tricks if it doesn't exist."""
    if not TRICKS_FILE.exists():
        TrickLibrary.save(DEFAULT_TRICKS.copy())
        print(f"Initialized {TRICKS_FILE} with default tricks")
    else:
        # Merge any new default tricks
        existing = TrickLibrary.load()
        merged = DEFAULT_TRICKS.copy()
        
        # Preserve existing tricks
        for bloodline, trick_data in existing.items():
            if bloodline.startswith("_"):
                continue
            if bloodline not in merged:
                merged[bloodline] = trick_data
            else:
                # Merge worked tricks
                for trick in trick_data.get("worked", []):
                    if trick not in merged[bloodline]["worked"]:
                        merged[bloodline]["worked"].append(trick)
                # Merge failed tricks
                for trick in trick_data.get("failed", []):
                    if trick not in merged[bloodline]["failed"]:
                        merged[bloodline]["failed"].append(trick)
        
        TrickLibrary.save(merged)
        print(f"Updated {TRICKS_FILE} with merged tricks")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Trick Library Management")
    parser.add_argument("--init", action="store_true", help="Initialize tricks file")
    parser.add_argument("--list", action="store_true", help="List all bloodline types")
    parser.add_argument("--show", type=str, help="Show tricks for a bloodline")
    
    args = parser.parse_args()
    
    if args.init:
        initialize_tricks_file()
    elif args.list:
        print("Bloodline types:", ", ".join(TrickLibrary.get_all_bloodline_types()))
    elif args.show:
        tricks = TrickLibrary.get_tricks(args.show)
        print(f"\n=== {args.show.upper()} TRICKS ===\n")
        print("Worked:")
        for t in tricks.get("worked", []):
            print(f"  + {t}")
        print("\nFailed:")
        for t in tricks.get("failed", []):
            print(f"  - {t}")
    else:
        # Default: show inherited wisdom for coder
        print(TrickLibrary.get_inherited_wisdom("coder", limit=10))
