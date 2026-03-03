#!/usr/bin/env python3
"""
Create OpenClaw Reminders

Pattern:
- Internal: Full context for the agent
- External: Short message for user Telegram

Usage:
    python create_reminder.py "Call Dave about HHO" "2026-03-04 14:00"
    python create_reminder.py "Meeting with Zane" "in 2 hours" --context "Discuss Samsung cord BN39-03006A"
    python create_reminder.py --list
"""

import sys
import json
import re
from datetime import datetime, timedelta

TIMEZONE_OFFSET = 10  # Brisbane UTC+10

def parse_time(time_str: str) -> datetime:
    """Parse various time formats."""
    time_str = time_str.strip().lower()
    
    # "in X minutes/hours"
    if time_str.startswith("in "):
        match = re.match(r"in (\d+) (minute|hour)s?", time_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            delta = timedelta(minutes=amount) if unit == "minute" else timedelta(hours=amount)
            return datetime.now() + delta
    
    # "2026-03-04 14:00"
    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", time_str):
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    
    # "14:00" (today)
    if re.match(r"\d{1,2}:\d{2}", time_str):
        today = datetime.now().strftime("%Y-%m-%d")
        return datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")
    
    raise ValueError(f"Unknown time format: {time_str}")

def create_reminder(external_msg: str, local_time: datetime, internal_context: str = None) -> dict:
    """
    Create a reminder cron job.
    
    Args:
        external_msg: Short message to send to user Telegram
        local_time: When to fire (local time, Brisbane)
        internal_context: Optional context for agent (defaults to external_msg)
    
    Returns:
        Cron job config dict
    """
    if not internal_context:
        internal_context = external_msg
    
    # Convert to UTC
    utc_time = local_time - timedelta(hours=TIMEZONE_OFFSET)
    utc_iso = utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Build the full internal message
    full_text = f"""⏰ REMINDER: {external_msg}

EXTERNAL MESSAGE: "{external_msg}"

CONTEXT: {internal_context}"""
    
    return {
        "name": f"reminder-{local_time.strftime('%Y%m%d-%H%M')}",
        "enabled": True,
        "deleteAfterRun": True,
        "schedule": {
            "kind": "at",
            "at": utc_iso
        },
        "sessionTarget": "main",
        "wakeMode": "now",
        "payload": {
            "kind": "systemEvent",
            "text": full_text
        }
    }

def main():
    args = sys.argv[1:]
    
    if not args or args[0] == "--help":
        print(__doc__)
        return
    
    if args[0] == "--list":
        print("Use: openclaw cron list")
        return
    
    # Parse arguments
    external_msg = args[0]
    time_str = args[1] if len(args) > 1 else "in 1 minute"
    
    # Check for --context
    internal_context = None
    if "--context" in args:
        idx = args.index("--context")
        if idx + 1 < len(args):
            internal_context = args[idx + 1]
    
    try:
        local_time = parse_time(time_str)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    job = create_reminder(external_msg, local_time, internal_context)
    
    print(f"\n📋 Reminder for {local_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   External: {external_msg}")
    if internal_context:
        print(f"   Context:  {internal_context}")
    print(f"\nCron job config:")
    print(json.dumps(job, indent=2))
    print("\n---\n")
    print("To create this reminder, tell Sloth_rog:")
    print(f'  "Create a reminder for {time_str}: {external_msg}"')

if __name__ == "__main__":
    main()
