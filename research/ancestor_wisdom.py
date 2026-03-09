#!/usr/bin/env python3
"""
Ancestor Wisdom Search

Search the wisdom from the entombed ancestors.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ANCESTORS_DIR = Path(__file__).parent.parent / "the-crypt" / "ancestors"

def search_ancestors(query: str, limit: int = 10) -> list:
    """Search ancestor files for patterns matching query."""
    results = []
    
    for ancestor_file in ANCESTORS_DIR.glob("*.md"):
        try:
            content = ancestor_file.read_text()
            
            # Simple search in content
            if query.lower() in content.lower():
                # Extract relevant sections
                lines = content.split('\n')
                context_lines = []
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        # Get surrounding context
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        context_lines.extend(lines[start:end])
                
                if context_lines:
                    results.append({
                        "file": ancestor_file.name,
                        "lines": context_lines
                    })
        except:
            continue
    
    return results[:limit]

def get_successful_patterns(limit: int = 20) -> list:
    """Get patterns from successful ancestors only."""
    patterns = []
    
    for ancestor_file in ANCESTORS_DIR.glob("*.md"):
        try:
            content = ancestor_file.read_text()
            
            if "Outcome" in content and "Success" in content:
                # Extract the Patterns Discovered section
                if "## Patterns Discovered" in content:
                    lines = content.split('\n')
                    in_patterns = False
                    pattern_lines = []
                    
                    for line in lines:
                        if "## Patterns Discovered" in line:
                            in_patterns = True
                            continue
                        if in_patterns and line.startswith("##"):
                            break
                        if in_patterns and line.strip().startswith("-"):
                            pattern_lines.append(line)
                    
                    if pattern_lines:
                        patterns.append({
                            "file": ancestor_file.name,
                            "patterns": pattern_lines
                        })
        except:
            continue
    
    return patterns[:limit]

def get_failure_patterns(limit: int = 20) -> list:
    """Get patterns from failed ancestors."""
    patterns = []
    
    for ancestor_file in ANCESTORS_DIR.glob("*.md"):
        try:
            content = ancestor_file.read_text()
            
            if "Outcome" in content and "Failure" in content:
                # Extract the Patterns Discovered section
                if "## Patterns Discovered" in content:
                    lines = content.split('\n')
                    in_patterns = False
                    pattern_lines = []
                    
                    for line in lines:
                        if "## Patterns Discovered" in line:
                        in_patterns = True
                            continue
                        if in_patterns and line.startswith("##"):
                            break
                        if in_patterns and line.strip().startswith("-"):
                            pattern_lines.append(line)
                    
                    if pattern_lines:
                        patterns.append({
                            "file": ancestor_file.name,
                            "patterns": pattern_lines
                        })
        except:
            continue
    
    return patterns[:limit]

if __name__ == "__main__":
    print("=" * 70)
    print("ANCESTOR WISDOM SEARCH")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python ancestor_wisdom.py search <query>")
        print("  python ancestor_wisdom.py success")
        print("  python ancestor_wisdom.py failure")
        print("\nExamples:")
        print("  python ancestor_wisdom.py search 'consciousness'")
        print("  python ancestor_wisdom.py success")
        print("  python ancestor_wisdom.py failure")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        if len(sys.argv) < 3:
            print("Please provide a search query")
            sys.exit(1)
        
        query = sys.argv[2]
        results = search_ancestors(query)
        
        print(f"\nFound {len(results)} matches for '{query}':")
        for result in results:
            print(f"\n{result['file']}:")
            for line in result['lines']:
                print(f"  {line}")
    
    elif cmd == "success":
        patterns = get_successful_patterns()
        
        print(f"\nFound {len(patterns)} successful ancestors with patterns:")
        for pattern in patterns:
            print(f"\n{pattern['file']}:")
            for p in pattern['patterns']:
                print(f"  {p}")
    
    elif cmd == "failure":
        patterns = get_failure_patterns()
        
        print(f"\nFound {len(patterns)} failed ancestors with patterns:")
        for pattern in patterns:
            print(f"\n{pattern['file']}:")
            for p in pattern['patterns']:
                print(f"  {p}")
