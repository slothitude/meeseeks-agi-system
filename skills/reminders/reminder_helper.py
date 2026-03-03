#!/usr/bin/env python3
"""
Reminder Helper for OpenClaw

Creates reminders that work with the current setup:
- System event goes to main session (agent gets context)
- Agent relays to Telegram via message tool

This is a workaround for isolated session delivery not working.
"""

import json
from datetime import datetime, timedelta

def create_reminder_config(text: str, local_time: datetime, job_name: str = None) -> dict:
    """
    Create a cron job config for a reminder.
    
    Args:
        text: Reminder message text
        local_time: Local time (Brisbane, UTC+10)
        job_name: Optional custom job name
    
    Returns:
        Cron job config dict ready for cron tool
    """
    # Convert local time to UTC
    utc_time = local_time - timedelta(hours=10)
    utc_iso = utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    if not job_name:
        job_name = f"reminder-{local_time.strftime('%Y%m%d-%H%M')}"
    
    return {
        "name": job_name,
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
            "text": f"⏰ REMINDER: {text}"
        }
    }


def create_dual_reminder(text: str, local_time: datetime, job_name: str = None) -> tuple:
    """
    Create TWO reminder jobs:
    1. System event to main session (agent context)
    2. Isolated agent that uses message tool directly
    
    Args:
        text: Reminder message text
        local_time: Local time (Brisbane, UTC+10)
        job_name: Optional custom job name
    
    Returns:
        Tuple of (main_session_job, isolated_job)
    """
    utc_time = local_time - timedelta(hours=10)
    utc_iso = utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    if not job_name:
        job_name = f"reminder-{local_time.strftime('%Y%m%d-%H%M')}"
    
    # Job 1: System event to main session
    main_job = {
        "name": f"{job_name}-internal",
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
            "text": f"⏰ REMINDER: {text}\n\n[Relay this to Telegram via message tool]"
        }
    }
    
    # Job 2: Isolated agent that tries to send message
    # (This may fail, but main session job will work)
    isolated_job = {
        "name": f"{job_name}-ping",
        "enabled": True,
        "deleteAfterRun": True,
        "schedule": {
            "kind": "at",
            "at": utc_iso
        },
        "sessionTarget": "isolated",
        "payload": {
            "kind": "agentTurn",
            "message": f"Send this exact message to Telegram chat 5597932516: '⏰ {text}'",
            "model": "GLM-4.7-Flash"
        },
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "5597932516"
        }
    }
    
    return (main_job, isolated_job)


# Example usage:
if __name__ == "__main__":
    # Test: Reminder in 1 minute
    test_time = datetime.now() + timedelta(minutes=1)
    
    main, isolated = create_dual_reminder(
        text="Test reminder from helper script!",
        local_time=test_time,
        job_name="test-reminder-helper"
    )
    
    print("Main session job:")
    print(json.dumps(main, indent=2))
    print("\nIsolated job:")
    print(json.dumps(isolated, indent=2))
