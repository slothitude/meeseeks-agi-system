#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wisdom Inheritance System for Meeseeks
Gathers wisdom from ancestors and bloodlines for new Meeseeks.

STEP 3: THE INHERITANCE BUILDER
- Reads bloodline wisdom
- Reads ancestor files
- Filters and combines them
- Returns formatted wisdom string for injection
"""

import re
import sys
import io
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Crypt locations (check both possible locations)
WORKSPACE_CRYPT = Path("C:/Users/aaron/.openclaw/workspace/the-crypt")
SKILLS_CRYPT = Path("C:/Users/aaron/.openclaw/workspace/skills/meeseeks/the-crypt")


def find_crypt_location(crypt_type: str = "bloodlines") -> Path:
    """
    Find the correct crypt location for a given type.
    
    Args:
        crypt_type: "bloodlines" or "ancestors"
    
    Returns:
        Path to the crypt directory
    """
    if crypt_type == "bloodlines":
        # Bloodlines are in workspace/the-crypt/bloodlines
        if WORKSPACE_CRYPT.exists():
            return WORKSPACE_CRYPT / "bloodlines"
    elif crypt_type == "ancestors":
        # Ancestors are in skills/meeseeks/the-crypt/ancestors
        if SKILLS_CRYPT.exists():
            return SKILLS_CRYPT / "ancestors"
    
    # Fallback
    return WORKSPACE_CRYPT / crypt_type


def extract_bloodline_wisdom(bloodline_path: Path) -> Dict[str, str]:
    """
    Extract key wisdom from a bloodline file.
    
    Args:
        bloodline_path: Path to bloodline markdown file
    
    Returns:
        Dict with 'oath', 'patterns', 'warnings', 'success_strategies'
    """
    if not bloodline_path.exists():
        return {
            "oath": "",
            "patterns": "",
            "warnings": "",
            "success_strategies": ""
        }
    
    content = bloodline_path.read_text(encoding='utf-8')
    
    # Extract oath (between ## Bloodline Oath and ##)
    oath_match = re.search(
        r'## Bloodline Oath\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    oath = oath_match.group(1).strip() if oath_match else ""
    
    # Extract top patterns (from Accumulated Patterns section)
    patterns_match = re.search(
        r'## 🧬 Accumulated Patterns\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    patterns = ""
    if patterns_match:
        # Get first 3-5 key patterns
        pattern_lines = []
        in_sacred = False
        for line in patterns_match.group(1).split('\n'):
            if '### The Sacred Patterns' in line:
                in_sacred = True
                continue
            if in_sacred and line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                pattern_lines.append(line.strip())
                if len(pattern_lines) >= 3:  # Top 3 patterns
                    break
        patterns = '\n'.join(pattern_lines)
    
    # Extract warnings (from Ancestral Warnings section)
    warnings_match = re.search(
        r'## ⚠️ Ancestral Warnings\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    warnings = ""
    if warnings_match:
        # Get first 2-3 warnings
        warning_lines = []
        for line in warnings_match.group(1).split('\n'):
            if line.strip().startswith(('1.', '2.', '3.')):
                # Extract just the warning title (before the parentheses)
                warning_title = re.sub(r'\s*\(\d+%.*\)', '', line.strip())
                warning_lines.append(warning_title)
                if len(warning_lines) >= 2:  # Top 2 warnings
                    break
        warnings = '\n'.join(warning_lines)
    
    # Extract successful approaches
    success_match = re.search(
        r'## ✅ Successful Approaches\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    success_strategies = ""
    if success_match:
        # Get first 2 strategies
        strategy_lines = []
        for line in success_match.group(1).split('\n'):
            if line.strip().startswith(('1.', '2.')):
                strategy_lines.append(line.strip())
                if len(strategy_lines) >= 2:  # Top 2 strategies
                    break
        success_strategies = '\n'.join(strategy_lines)
    
    return {
        "oath": oath,
        "patterns": patterns,
        "warnings": warnings,
        "success_strategies": success_strategies
    }


def read_ancestor_index(ancestors_dir: Path) -> List[Dict[str, str]]:
    """
    Read the ancestor index file and parse it.
    
    Args:
        ancestors_dir: Path to ancestors directory
    
    Returns:
        List of ancestor dicts with 'id', 'name', 'type', 'success', 'insight'
    """
    index_path = ancestors_dir / "index.md"
    
    if not index_path.exists():
        return []
    
    content = index_path.read_text(encoding='utf-8')
    ancestors = []
    
    # Parse markdown table
    # Format: | ID | Name | Type | Success | Desperation | Key Insight |
    in_table = False
    for line in content.split('\n'):
        if line.strip().startswith('| ID |'):
            in_table = True
            continue
        if in_table and line.strip().startswith('|') and not line.strip().startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 7:  # | ID | Name | Type | Success | Desperation | Key Insight | ...
                ancestor = {
                    "id": parts[1],
                    "name": parts[2],
                    "type": parts[3],
                    "success": parts[4],
                    "desperation": parts[5] if len(parts) > 5 else "",
                    "insight": parts[6] if len(parts) > 6 else ""
                }
                ancestors.append(ancestor)
    
    return ancestors


def filter_ancestors(
    ancestors: List[Dict[str, str]],
    bloodline: str = None,
    task_type: str = None,
    max_ancestors: int = 3
) -> List[Dict[str, str]]:
    """
    Filter ancestors by bloodline match or task relevance.
    
    Args:
        ancestors: List of ancestor dicts
        bloodline: Target bloodline type
        task_type: Optional task type for relevance matching
        max_ancestors: Maximum number of ancestors to return
    
    Returns:
        Filtered list of ancestors (most recent first)
    """
    if not ancestors:
        return []
    
    # Score each ancestor
    scored_ancestors = []
    for ancestor in ancestors:
        score = 0
        
        # Bloodline match is highest priority
        if bloodline and ancestor.get("type", "").lower() == bloodline.lower():
            score += 10
        
        # Task type relevance (if provided)
        if task_type:
            task_lower = task_type.lower()
            name_lower = ancestor.get("name", "").lower()
            insight_lower = ancestor.get("insight", "").lower()
            
            # Check if task keywords appear in name or insight
            task_keywords = task_lower.split()
            for keyword in task_keywords:
                if keyword in name_lower or keyword in insight_lower:
                    score += 2
        
        # Successful ancestors are more valuable
        if ancestor.get("success", "").lower() in ["yes", "true"]:
            score += 3
        
        scored_ancestors.append((score, ancestor))
    
    # Sort by score (descending), then by ID (most recent first)
    scored_ancestors.sort(key=lambda x: (-x[0], -int(x[1].get("id", "0"))))
    
    # Return top max_ancestors
    return [ancestor for score, ancestor in scored_ancestors[:max_ancestors]]


def inherit_wisdom(
    bloodline: str = "coder",
    task_type: str = None,
    max_ancestors: int = 3
) -> str:
    """
    Gather wisdom from ancestors and bloodlines for a new Meeseeks.
    
    Args:
        bloodline: Which bloodline to inherit from (coder, searcher, tester, deployer, desperate, brahman)
        task_type: Optional task type for more specific ancestors
        max_ancestors: Maximum number of ancestors to include
    
    Returns:
        Wisdom string to inject into Meeseeks prompt
    
    Example Output:
        ## 🪦 Ancestral Wisdom
        
        ### Bloodline: coder
        [Bloodline oath text]
        
        Key patterns:
        - pattern 1
        - pattern 2
        
        ### Recent Ancestors
        **Ancestor 001**: Fallback before fix
        **Ancestor 002**: Start with README
        
        ---
        *Inherit their wisdom. Do not repeat their failures.*
    """
    
    # Find crypt locations
    bloodlines_dir = find_crypt_location("bloodlines")
    ancestors_dir = find_crypt_location("ancestors")
    
    # Build wisdom string
    wisdom_parts = []
    wisdom_parts.append("## 🪦 Ancestral Wisdom\n")
    
    # 1. Read bloodline wisdom
    bloodline_file = bloodlines_dir / f"{bloodline.lower()}-lineage.md"
    bloodline_wisdom = extract_bloodline_wisdom(bloodline_file)
    
    if bloodline_wisdom["oath"] or bloodline_wisdom["patterns"]:
        wisdom_parts.append(f"### Bloodline: {bloodline}\n")
        
        if bloodline_wisdom["oath"]:
            wisdom_parts.append(f"{bloodline_wisdom['oath']}\n")
        
        if bloodline_wisdom["patterns"]:
            wisdom_parts.append("\n**Key patterns:**\n")
            for line in bloodline_wisdom["patterns"].split('\n'):
                if line.strip():
                    wisdom_parts.append(f"- {line.strip()}\n")
        
        if bloodline_wisdom["warnings"]:
            wisdom_parts.append("\n**⚠️ Warnings:**\n")
            for line in bloodline_wisdom["warnings"].split('\n'):
                if line.strip():
                    wisdom_parts.append(f"- {line.strip()}\n")
    
    # 2. Read and filter ancestors
    ancestors = read_ancestor_index(ancestors_dir)
    
    if ancestors:
        filtered_ancestors = filter_ancestors(
            ancestors,
            bloodline=bloodline,
            task_type=task_type,
            max_ancestors=max_ancestors
        )
        
        if filtered_ancestors:
            wisdom_parts.append("\n### Recent Ancestors\n")
            for ancestor in filtered_ancestors:
                ancestor_id = ancestor.get("id", "???")
                insight = ancestor.get("insight", "No insight recorded")
                wisdom_parts.append(f"**Ancestor {ancestor_id}**: {insight}\n")
    
    # 3. Closing wisdom
    wisdom_parts.append("\n---\n")
    wisdom_parts.append("*Inherit their wisdom. Do not repeat their failures.*\n")
    
    return ''.join(wisdom_parts)


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    bloodline = sys.argv[1] if len(sys.argv) > 1 else "coder"
    task_type = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print(f"INHERITING WISDOM FOR BLOODLINE: {bloodline.upper()}")
    if task_type:
        print(f"TASK TYPE: {task_type}")
    print("=" * 60)
    print()
    
    wisdom = inherit_wisdom(bloodline=bloodline, task_type=task_type)
    print(wisdom)
