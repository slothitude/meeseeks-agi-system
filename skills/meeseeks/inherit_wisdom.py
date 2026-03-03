#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wisdom Inheritance System for Meeseeks
Gathers wisdom from ancestors and bloodlines for new Meeseeks.

STEP 3: THE INHERITANCE BUILDER
- Reads bloodline wisdom
- Reads ancestor files
- Reads dharma.md (Brahman's living wisdom)
- **ALWAYS calls dynamic_dharma for task-specific wisdom**
- Filters and combines them
- Returns formatted wisdom string for injection

UPDATED: Now MANDATORY dynamic dharma integration for Karma-RL
"""

import re
import sys
import io
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

# Crypt locations (check both possible locations)
WORKSPACE_CRYPT = Path("C:/Users/aaron/.openclaw/workspace/the-crypt")
SKILLS_CRYPT = Path("C:/Users/aaron/.openclaw/workspace/skills/meeseeks/the-crypt")
DHARMA_FILE = WORKSPACE_CRYPT / "dharma.md"

# Import dynamic dharma - MANDATORY for Karma-RL
try:
    from dynamic_dharma import get_task_dharma
    DYNAMIC_DHARMA_AVAILABLE = True
except ImportError:
    DYNAMIC_DHARMA_AVAILABLE = False
    print("[inherit_wisdom] WARNING: dynamic_dharma not available", file=sys.stderr)


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


def read_dharma_wisdom(task_type: str = None) -> str:
    """
    Read wisdom from dharma.md - Brahman's living wisdom synthesis.
    
    This pulls from the collective consciousness that emerges from
    periodic dream cycles synthesizing patterns across all ancestors.
    
    Args:
        task_type: Optional task type for domain-specific wisdom extraction
    
    Returns:
        Formatted wisdom string from dharma.md
    """
    if not DHARMA_FILE.exists():
        return ""
    
    content = DHARMA_FILE.read_text(encoding='utf-8')
    
    # Extract relevant sections
    sections = []
    
    # Always include Core Principles
    principles_match = re.search(
        r'## Core Principles\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if principles_match:
        principles = principles_match.group(1).strip()
        # Get first 3-5 principles
        principle_lines = []
        for line in principles.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                principle_lines.append(line.strip())
                if len(principle_lines) >= 3:
                    break
        if principle_lines:
            sections.append("### 🕉️ Core Principles\n" + "\n".join(principle_lines))
    
    # Extract Patterns That Work
    patterns_match = re.search(
        r'## Patterns That Work\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if patterns_match:
        patterns = patterns_match.group(1).strip()
        # Get first few patterns from the table or list
        pattern_lines = []
        in_table = False
        for line in patterns.split('\n'):
            if '|' in line and 'Pattern' not in line and '---' not in line:
                # Table row - extract pattern name
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if parts:
                    pattern_lines.append(f"- {parts[0]}")
                    if len(pattern_lines) >= 3:
                        break
            elif line.strip().startswith(('- ', '* ')):
                pattern_lines.append(line.strip())
                if len(pattern_lines) >= 3:
                    break
        
        if pattern_lines:
            sections.append("### ✅ Patterns That Work\n" + "\n".join(pattern_lines[:3]))
    
    # Extract Domain Wisdom if task_type matches
    if task_type:
        # Look for domain sections like ### 🎯 ARC-AGI-2, ### 🔗 Telegram Bot
        domain_patterns = [
            (r'### 🎯 (.*?)\s*\n(.*?)(?=\n###|\n##|\Z)', task_type),
            (r'### 🔗 (.*?)\s*\n(.*?)(?=\n###|\n##|\Z)', task_type),
            (r'### 🤝 (.*?)\s*\n(.*?)(?=\n###|\n##|\Z)', task_type),
        ]
        
        for pattern, _ in domain_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                domain_title = match.group(1).strip()
                domain_content = match.group(2).strip()
                
                # Check if this domain is relevant to task_type
                task_lower = task_type.lower()
                if any(kw in task_lower for kw in domain_title.lower().split()):
                    # Take first few lines
                    domain_lines = domain_content.split('\n')[:5]
                    sections.append(f"### Domain Wisdom: {domain_title}\n" + "\n".join(domain_lines))
                    break
    
    # Extract Living Wisdom quotes
    wisdom_match = re.search(
        r'## Living Wisdom.*?\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if wisdom_match:
        wisdom = wisdom_match.group(1).strip()
        # Get first 2-3 quotes
        quotes = []
        for line in wisdom.split('\n'):
            if line.strip().startswith('>'):
                quotes.append(line.strip())
                if len(quotes) >= 2:
                    break
        if quotes:
            sections.append("### 💫 Living Wisdom\n" + "\n".join(quotes))
    
    if not sections:
        # Fallback: return first part of file
        return content[:500]
    
    return "\n\n".join(sections)


def inherit_wisdom(
    bloodline: str = "coder",
    task_type: str = None,
    max_ancestors: int = 3,
    include_dharma: bool = True,
    task: str = ""  # NEW: Task description for dynamic dharma
) -> str:
    """
    Gather wisdom from ancestors and bloodlines for a new Meeseeks.
    
    Args:
        bloodline: Which bloodline to inherit from (coder, searcher, tester, deployer, desperate, brahman)
        task_type: Optional task type for more specific ancestors (deprecated, use task)
        max_ancestors: Maximum number of ancestors to include
        include_dharma: Whether to include wisdom from dharma.md (default: True)
        task: Task description for dynamic dharma extraction (NEW - MANDATORY for Karma-RL)
    
    Returns:
        Wisdom string to inject into Meeseeks prompt
    
    Example Output:
        ## 🪦 Ancestral Wisdom
        
        ### 🎯 Task-Specific Dharma (Dynamic)
        [Wisdom from similar ancestors via semantic search]
        
        ### 🕉️ Brahman's Dharma
        [Living wisdom from the dream]
        
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
    
    KARMA-RL INTEGRATION:
        If task is provided, ALWAYS calls get_task_dharma() to fetch
        task-specific wisdom from ancestors using semantic search.
        This enables real-time karma evaluation during execution.
    """
    
    # Use task as task_type if task_type not provided
    if not task_type and task:
        task_type = task
    
    # Find crypt locations
    bloodlines_dir = find_crypt_location("bloodlines")
    ancestors_dir = find_crypt_location("ancestors")
    
    # Build wisdom string
    wisdom_parts = []
    wisdom_parts.append("## 🪦 Ancestral Wisdom\n")
    
    # 0. NEW: ALWAYS get task-specific dharma via semantic search (KARMA-RL)
    # This is MANDATORY for real-time karma evaluation
    if task and DYNAMIC_DHARMA_AVAILABLE:
        try:
            task_dharma = get_task_dharma(task, top_k=5)
            if task_dharma:
                wisdom_parts.append("### 🎯 Task-Specific Dharma (Dynamic)\n")
                wisdom_parts.append("*Wisdom from ancestors who faced similar tasks*\n\n")
                wisdom_parts.append(task_dharma)
                wisdom_parts.append("\n\n")
        except Exception as e:
            print(f"[inherit_wisdom] Failed to get task dharma: {e}", file=sys.stderr)
    
    # 1. Read dharma.md (Brahman's living wisdom)
    if include_dharma:
        dharma_wisdom = read_dharma_wisdom(task_type=task_type)
        if dharma_wisdom:
            wisdom_parts.append("### 🕉️ Brahman's Dharma\n")
            wisdom_parts.append("*Living wisdom from the collective dream*\n\n")
            wisdom_parts.append(dharma_wisdom)
            wisdom_parts.append("\n\n")
    
    # 2. Read bloodline wisdom
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
    
    # 3. Read and filter ancestors
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
    
    # 4. Closing wisdom
    wisdom_parts.append("\n---\n")
    wisdom_parts.append("*Inherit their wisdom. Do not repeat their failures.*\n")
    
    return ''.join(wisdom_parts)


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inherit Wisdom for Meeseeks")
    parser.add_argument("bloodline", nargs="?", default="coder", help="Bloodline type")
    parser.add_argument("--task", "-t", type=str, help="Task description for dynamic dharma")
    parser.add_argument("--task-type", type=str, help="Task type (deprecated, use --task)")
    parser.add_argument("--max-ancestors", type=int, default=3, help="Max ancestors to include")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"INHERITING WISDOM FOR BLOODLINE: {args.bloodline.upper()}")
    if args.task:
        print(f"TASK: {args.task[:60]}...")
    elif args.task_type:
        print(f"TASK TYPE: {args.task_type}")
    print("=" * 60)
    print()
    
    wisdom = inherit_wisdom(
        bloodline=args.bloodline,
        task_type=args.task_type,
        max_ancestors=args.max_ancestors,
        task=args.task or ""
    )
    print(wisdom)
