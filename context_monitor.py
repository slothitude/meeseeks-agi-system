#!/usr/bin/env python3
"""
Context Monitor - Auto-trigger compact at 127k/205k tokens
==========================================================

Usage:
    python context_monitor.py --check
    python context_monitor.py --force-compact
"""

import os
from pathlib import Path

WORKSPACE = Path(__file__).parent
MEMORY_FILE = WORKSPACE / "MEMORY.md"
TRIGGER_THRESHOLD = 127000  # 127k tokens
MAX_TOKENS = 205000

def estimate_tokens(text):
    """Rough estimate: 1 token ≈ 4 chars"""
    return len(text) // 4

def check_context():
    """Check current context size"""
    total_chars = 0
    
    # Check MEMORY.md
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            total_chars += len(content)
    
    # Estimate tokens
    estimated_tokens = estimate_tokens(" " * total_chars)
    pct = (estimated_tokens / MAX_TOKENS) * 100
    
    status = "ok"
    recommendation = "continue"
    
    if estimated_tokens >= TRIGGER_THRESHOLD:
        status = "compact_needed"
        recommendation = "run_compact_now"
    
    return {
        "status": status,
        "tokens": estimated_tokens,
        "pct": round(pct, 1),
        "recommendation": recommendation
    }

def trigger_compact():
    """Trigger auto-compact"""
    print("Triggering auto-compact...")
    print("This would call the auto_compact module")
    print("For now, manually trim MEMORY.md to <10KB")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check context size')
    parser.add_argument('--force-compact', action='store_true', help='Force compact')
    args = parser.parse_args()
    
    if args.check or (not args.check and not args.force_compact):
        result = check_context()
        print(f"Context: {result['tokens']:,} tokens ({result['pct']}%)")
        print(f"Status: {result['status']}")
        
        if result['recommendation'] == 'run_compact_now':
            print("\n*** COMPACT NEEDED ***")
            print("Run: python context_monitor.py --force-compact")
    
    if args.force_compact:
        trigger_compact()

if __name__ == "__main__":
    main()
