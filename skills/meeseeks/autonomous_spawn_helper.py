#!/usr/bin/env python3
"""
Autonomous Spawn Helper - Reads pending spawns and executes them

This script is meant to be called by the main agent session to process
autonomous spawn requests logged by autonomous_research.py

Usage:
    python skills/meeseeks/autonomous_spawn_helper.py --check
    python skills/meeseeks/autonomous_spawn_helper.py --clear
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

META_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/meta")
PENDING_FILE = META_DIR / "pending_autonomous_spawns.jsonl"


def check_pending():
    """Check for pending autonomous spawns."""
    if not PENDING_FILE.exists():
        print("No pending spawns file found")
        return []
    
    pending = []
    with open(PENDING_FILE, 'r') as f:
        for line in f:
            if line.strip():
                pending.append(json.loads(line))
    
    if pending:
        print(f"\n{'='*60}")
        print(f"PENDING AUTONOMOUS SPAWNS: {len(pending)}")
        print(f"{'='*60}\n")
        
        for i, spawn in enumerate(pending, 1):
            print(f"{i}. [{spawn.get('bloodline', 'STANDARD')}] {spawn.get('task', 'No task')[:60]}...")
            print(f"   Logged: {spawn.get('timestamp', 'unknown')}")
            print()
    else:
        print("No pending spawns")
    
    return pending


def clear_processed():
    """Clear the pending file after processing."""
    if PENDING_FILE.exists():
        PENDING_FILE.unlink()
        print("Cleared pending spawns file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check pending spawns")
    parser.add_argument("--clear", action="store_true", help="Clear pending file")
    
    args = parser.parse_args()
    
    if args.check:
        check_pending()
    elif args.clear:
        clear_processed()
    else:
        check_pending()
