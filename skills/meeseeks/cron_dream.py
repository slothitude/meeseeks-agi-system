#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brahman Dream Cron Helper

This script is designed to be called by cron or scheduled tasks.
It runs the Brahman Dream process if conditions are met.

Cron setup (every 6 hours):
    0 */6 * * * cd /path/to/workspace && python skills/meeseeks/cron_dream.py

Or with logging:
    0 */6 * * * cd /path/to/workspace && python skills/meeseeks/cron_dream.py >> the-crypt/dream.log 2>&1
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from brahman_dream import run_dream, load_config, should_dream

def main():
    """Run dream if conditions are met."""
    print(f"\n[{datetime.now().isoformat()}] Brahman Dream Cron Check")
    
    config = load_config()
    
    # Check if we should dream
    should, reason = should_dream(config)
    
    if should:
        print(f"Running dream: {reason}")
        success = run_dream(config, force=False)
        if success:
            print("Dream completed successfully")
            return 0
        else:
            print("Dream did not run or failed")
            return 1
    else:
        print(f"Skipping: {reason}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
