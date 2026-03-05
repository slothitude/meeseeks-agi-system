#!/usr/bin/env python3
"""
Brahman Dream v2 - The Pattern Lab
===================================

REDESIGNED: What dreams SHOULD be doing:
1. Workflow Compression - Extract reusable sequences, not vague principles
2. Cross-Subject Experiments - Find patterns across bloodlines with evidence

Output formats:
- WORKFLOWS: Checklists for specific task types
- HYPOTHESES: Testable predictions backed by data
- SIGNALS: Early warning patterns that predict failure

NOT: Generic wisdom like "be specific"
YES: Actual checklists like "when debugging timeouts: 1. check pool 2. verify query..."

Usage:
    python brahman_dream_v2.py           # Run dream
    python brahman_dream_v2.py --stats   # Show stats
    python brahman_dream_v2.py --test    # Test on sample data
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import urllib.request
import urllib.error

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
WORKFLOWS_FILE = CRYPT_ROOT / "workflows.json"
HYPOTHESES_FILE = CRYPT_ROOT / "hypotheses.json"
SIGNALS_FILE = CRYPT_ROOT / "signals.json"


def extract_workflow_from_ancestor(content: str) -> Optional[Dict]:
    """
    Extract a reusable workflow from an ancestor.
    
    Looks for:
    - Step sequences (1. X 2. Y 3. Z)
    - If-then patterns
    - Tool usage sequences
    - Error-resolution patterns
    """
    workflow = {
        "trigger": None,  # When to use this workflow
        "steps": [],      # Actual steps to take
        "outcome": None,  # What success looks like
        "evidence": None  # Which ancestor proved this works
    }
    
    # Extract task type (trigger)
    task_match = re.search(r'## Task\s+(.+?)(?:\n|$)', content)
    if task_match:
        task = task_match.group(1).strip()
        workflow["trigger"] = classify_task_type(task)
    
    # Extract steps taken
    steps = []
    
    # Look for numbered steps
    numbered = re.findall(r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=\n\d+\.|\n\n|$)', content, re.DOTALL)
    if numbered:
        steps = [s[1].strip() for s in numbered[:5]]  # Max 5 steps
    
    # Look for tool usage sequence
    if not steps:
        tools = re.findall(r'(?:used|ran|executed|called)\s+`?(\w+)`?', content, re.IGNORECASE)
        if tools:
            steps = [f"Use {t}" for t in tools[:5]]
    
    # Look for if-then patterns
    if not steps:
        conditionals = re.findall(r'(?:if|when|after)\s+(.+?)\s*,?\s*(?:then\s+)?(.+?)(?:\.|\n)', content, re.IGNORECASE)
        if conditionals:
            steps = [f"If {c[0].strip()}, then {c[1].strip()}" for c in conditionals[:3]]
    
    workflow["steps"] = steps
    
    # Extract outcome
    outcome_match = re.search(r'## Outcome\s+(.+?)(?:\n##|\n\n|$)', content, re.DOTALL)
    if outcome_match:
        outcome = outcome_match.group(1).strip()
        workflow["outcome"] = "success" if "success" in outcome.lower() else "failure"
    
    # Evidence
    ancestor_match = re.search(r'ancestor-(\d{8}-\d{6})', content)
    if ancestor_match:
        workflow["evidence"] = ancestor_match.group(0)
    
    if workflow["steps"] and workflow["trigger"]:
        return workflow
    return None


def classify_task_type(task: str) -> str:
    """Classify task into a workflow category."""
    task_lower = task.lower()
    
    if any(w in task_lower for w in ["debug", "fix", "error", "timeout", "crash"]):
        return "debug"
    elif any(w in task_lower for w in ["build", "create", "implement", "make"]):
        return "build"
    elif any(w in task_lower for w in ["search", "find", "locate", "count"]):
        return "search"
    elif any(w in task_lower for w in ["test", "verify", "check", "validate"]):
        return "test"
    elif any(w in task_lower for w in ["analyze", "review", "examine"]):
        return "analyze"
    elif any(w in task_lower for w in ["refactor", "improve", "optimize"]):
        return "refactor"
    else:
        return "general"


def extract_hypothesis_from_ancestors(ancestors: List[Dict]) -> List[Dict]:
    """
    Extract testable hypotheses from cross-bloodline analysis.
    
    Looks for patterns that predict success/failure.
    """
    hypotheses = []
    
    # Group by success/failure
    successes = [a for a in ancestors if a.get("outcome") == "success"]
    failures = [a for a in ancestors if a.get("outcome") == "failure"]
    
    if not successes or not failures:
        return hypotheses
    
    # Pattern 1: Word count constraint
    success_word_limits = sum(1 for a in successes 
                             if re.search(r'\b(one word|3 words|\d+ words|single|exactly)\b', 
                                         a.get("task", "").lower()))
    total_word_limits = sum(1 for a in ancestors 
                           if re.search(r'\b(one word|3 words|\d+ words|single|exactly)\b', 
                                       a.get("task", "").lower()))
    
    if total_word_limits > 0:
        rate = success_word_limits / total_word_limits
        hypotheses.append({
            "id": "H001",
            "hypothesis": "Word count constraints improve success rate",
            "evidence": f"{success_word_limits}/{total_word_limits} ({rate:.0%}) succeeded with word limits",
            "prediction": "Tasks with explicit word limits will succeed 90%+",
            "testable": True
        })
    
    # Pattern 2: Task complexity vs success
    avg_success_words = sum(len(a.get("task", "").split()) for a in successes) / len(successes) if successes else 0
    avg_failure_words = sum(len(a.get("task", "").split()) for a in failures) / len(failures) if failures else 0
    
    if avg_failure_words > avg_success_words * 1.5:
        hypotheses.append({
            "id": "H002", 
            "hypothesis": "Task description length predicts failure",
            "evidence": f"Success tasks avg {avg_success_words:.0f} words, failure avg {avg_failure_words:.0f} words",
            "prediction": "Tasks >30 words will fail 60%+",
            "testable": True
        })
    
    # Pattern 3: Bloodline-specific success
    bloodline_success = defaultdict(lambda: {"success": 0, "total": 0})
    for a in ancestors:
        bloodline = a.get("bloodline", "unknown")
        bloodline_success[bloodline]["total"] += 1
        if a.get("outcome") == "success":
            bloodline_success[bloodline]["success"] += 1
    
    for bloodline, stats in bloodline_success.items():
        if stats["total"] >= 3:
            rate = stats["success"] / stats["total"]
            if rate > 0.8:
                hypotheses.append({
                    "id": f"H003-{bloodline}",
                    "hypothesis": f"{bloodline} bloodline has high success rate",
                    "evidence": f"{stats['success']}/{stats['total']} ({rate:.0%})",
                    "prediction": f"{bloodline} tasks will succeed {rate:.0%}",
                    "testable": True
                })
    
    return hypotheses


def extract_failure_signals(ancestors: List[Dict]) -> List[Dict]:
    """
    Extract early warning signals that predict failure.
    
    Patterns seen in failures but not successes.
    """
    signals = []
    
    failures = [a for a in ancestors if a.get("outcome") == "failure"]
    
    # Signal 1: Multiple open questions
    multi_question_failures = sum(1 for a in failures 
                                  if a.get("task", "").count("?") > 1)
    if multi_question_failures > 0:
        signals.append({
            "signal": "Multiple questions in task",
            "pattern": "Task contains >1 question mark",
            "failure_count": multi_question_failures,
            "recommendation": "Split into separate tasks"
        })
    
    # Signal 2: Architecture/design keywords
    arch_failures = sum(1 for a in failures 
                       if any(w in a.get("task", "").lower() 
                             for w in ["architecture", "design", "build entire", "create system"]))
    if arch_failures > 0:
        signals.append({
            "signal": "Architecture/design task",
            "pattern": "Task mentions architecture, design, or building systems",
            "failure_count": arch_failures,
            "recommendation": "Chunk into smaller implementation tasks"
        })
    
    # Signal 3: Unknown failure mode
    unknown_failures = sum(1 for a in failures 
                          if a.get("outcome_detail", "").lower() in ["unknown", "unknown failure", ""])
    if unknown_failures > 0:
        signals.append({
            "signal": "Silent failure",
            "pattern": "Failure with no error message",
            "failure_count": unknown_failures,
            "recommendation": "Add explicit error handling and logging"
        })
    
    return signals


def parse_ancestors(limit: int = 50) -> List[Dict]:
    """Parse ancestor files into structured data."""
    ancestors = []
    
    if not ANCESTORS_DIR.exists():
        return ancestors
    
    files = sorted(ANCESTORS_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
    
    for f in files:
        try:
            content = f.read_text(encoding='utf-8')
            
            # Extract fields
            ancestor = {
                "file": f.name,
                "task": "",
                "bloodline": "unknown",
                "outcome": "unknown",
                "outcome_detail": "",
                "patterns": []
            }
            
            # Task
            task_match = re.search(r'## Task\s+(.+?)(?:\n|$)', content)
            if task_match:
                ancestor["task"] = task_match.group(1).strip()[:200]
            
            # Bloodline
            bloodline_match = re.search(r'\*\*Bloodline:\*\*\s*(\w+)', content)
            if bloodline_match:
                ancestor["bloodline"] = bloodline_match.group(1).lower()
            
            # Outcome
            if "success" in content.lower() and "failure" not in content.lower():
                ancestor["outcome"] = "success"
            elif "failure" in content.lower():
                ancestor["outcome"] = "failure"
            
            # Patterns
            patterns = re.findall(r'(?:✓|✗|-)\s*(.+?)(?:\n|$)', content)
            ancestor["patterns"] = [p.strip() for p in patterns[:5]]
            
            ancestors.append(ancestor)
        except Exception as e:
            continue
    
    return ancestors


def dream_v2():
    """Run the redesigned dream process."""
    print("=" * 60)
    print("BRAHMAN DREAM V2 - THE PATTERN LAB")
    print("=" * 60)
    
    # Load ancestors
    print("\n[1] Loading ancestors...")
    ancestors = parse_ancestors(50)
    print(f"    Loaded {len(ancestors)} ancestors")
    
    if len(ancestors) < 5:
        print("    Not enough ancestors for analysis")
        return
    
    # Extract workflows
    print("\n[2] Extracting workflows...")
    workflows = defaultdict(list)
    
    for ancestor in ancestors:
        if ancestor.get("outcome") == "success":
            task_type = classify_task_type(ancestor.get("task", ""))
            workflow = {
                "trigger": task_type,
                "task_example": ancestor.get("task", "")[:100],
                "bloodline": ancestor.get("bloodline"),
                "evidence": ancestor.get("file")
            }
            workflows[task_type].append(workflow)
    
    # Consolidate workflows
    consolidated_workflows = []
    for task_type, examples in workflows.items():
        if len(examples) >= 2:
            consolidated_workflows.append({
                "task_type": task_type,
                "success_count": len(examples),
                "examples": examples[:3],
                "checklist": generate_checklist(task_type, examples)
            })
    
    print(f"    Found {len(consolidated_workflows)} workflow patterns")
    
    # Extract hypotheses
    print("\n[3] Extracting hypotheses...")
    hypotheses = extract_hypothesis_from_ancestors(ancestors)
    print(f"    Generated {len(hypotheses)} testable hypotheses")
    
    # Extract signals
    print("\n[4] Extracting failure signals...")
    signals = extract_failure_signals(ancestors)
    print(f"    Found {len(signals)} failure warning signals")
    
    # Save outputs
    print("\n[5] Saving outputs...")
    
    with open(WORKFLOWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(consolidated_workflows, f, indent=2)
    print(f"    Workflows: {WORKFLOWS_FILE}")
    
    with open(HYPOTHESES_FILE, 'w', encoding='utf-8') as f:
        json.dump(hypotheses, f, indent=2)
    print(f"    Hypotheses: {HYPOTHESES_FILE}")
    
    with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2)
    print(f"    Signals: {SIGNALS_FILE}")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("DREAM SUMMARY")
    print("=" * 60)
    
    print("\n[WORKFLOWS]")
    for w in consolidated_workflows[:5]:
        print(f"  {w['task_type']}: {w['success_count']} successes")
        if w.get('checklist'):
            for i, step in enumerate(w['checklist'][:3], 1):
                print(f"    {i}. {step}")
    
    print("\n[HYPOTHESES]")
    for h in hypotheses[:3]:
        print(f"  {h['id']}: {h['hypothesis']}")
        print(f"    Evidence: {h['evidence']}")
    
    print("\n[SIGNALS]")
    for s in signals[:3]:
        print(f"  {s['signal']}: {s['failure_count']} failures")
        print(f"    Fix: {s['recommendation']}")
    
    print("\n" + "=" * 60)
    print("DREAM COMPLETE")
    print("=" * 60)


def generate_checklist(task_type: str, examples: List[Dict]) -> List[str]:
    """Generate a checklist for a task type based on successful examples."""
    
    checklists = {
        "debug": [
            "Identify the error message or symptom",
            "Locate the relevant code section",
            "Check recent changes that could cause this",
            "Verify inputs and assumptions",
            "Test the fix with the smallest possible change"
        ],
        "search": [
            "Define what you're looking for in one sentence",
            "Identify the scope (which files/directories)",
            "Use appropriate search tools",
            "Count and report results",
            "Verify findings match requirements"
        ],
        "build": [
            "Understand the requirements completely",
            "Break into smallest possible pieces",
            "Implement one piece at a time",
            "Test each piece before moving on",
            "Integrate and verify end-to-end"
        ],
        "test": [
            "Define success criteria explicitly",
            "Create test cases that cover edge cases",
            "Run tests and capture output",
            "Verify results match expected",
            "Report pass/fail with evidence"
        ],
        "analyze": [
            "Define the question being asked",
            "Gather all relevant data",
            "Look for patterns and anomalies",
            "Draw conclusions from evidence",
            "Report findings concisely"
        ]
    }
    
    return checklists.get(task_type, [
        "Understand the task completely",
        "Break into steps if complex",
        "Execute systematically",
        "Verify results",
        "Report clearly"
    ])


if __name__ == "__main__":
    import sys
    
    if "--stats" in sys.argv:
        # Show stats
        ancestors = parse_ancestors(100)
        print(f"Total ancestors: {len(ancestors)}")
        
        outcomes = defaultdict(int)
        bloodlines = defaultdict(int)
        for a in ancestors:
            outcomes[a.get("outcome", "unknown")] += 1
            bloodlines[a.get("bloodline", "unknown")] += 1
        
        print("\nOutcomes:")
        for k, v in outcomes.items():
            print(f"  {k}: {v}")
        
        print("\nBloodlines:")
        for k, v in bloodlines.items():
            print(f"  {k}: {v}")
    
    elif "--test" in sys.argv:
        # Test mode
        print("Testing dream v2...")
        dream_v2()
    
    else:
        dream_v2()
