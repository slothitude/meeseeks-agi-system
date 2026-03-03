#!/usr/bin/env python3
"""
Reminder Handler - Called by agent when reminder fires.

Parses the reminder format:
- Extracts EXTERNAL MESSAGE for user
- Keeps context for agent

Usage (by agent):
    python handle_reminder.py "⏰ REMINDER: Call Dave\n\nEXTERNAL MESSAGE: \"📞 Call Dave\"\n\nCONTEXT: ..."
"""

import sys
import re

def parse_reminder(full_text: str) -> dict:
    """
    Parse reminder text into components.
    
    Returns:
        {
            "title": "Call Dave",
            "external": "📞 Call Dave",
            "context": "Dave approved the project..."
        }
    """
    lines = full_text.strip().split("\n")
    
    # Extract title (first line after ⏰ REMINDER:)
    title = ""
    for line in lines:
        if line.startswith("⏰ REMINDER:"):
            title = line.replace("⏰ REMINDER:", "").strip()
            break
    
    # Extract external message
    external = title  # default to title
    external_match = re.search(r'EXTERNAL MESSAGE:\s*"([^"]+)"', full_text)
    if external_match:
        external = external_match.group(1)
    
    # Extract context
    context = ""
    context_match = re.search(r'CONTEXT:\s*(.+?)(?:\n\n|$)', full_text, re.DOTALL)
    if context_match:
        context = context_match.group(1).strip()
    
    return {
        "title": title,
        "external": external,
        "context": context
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: handle_reminder.py <reminder_text>")
        return
    
    full_text = sys.argv[1]
    parsed = parse_reminder(full_text)
    
    print(f"EXTERNAL: {parsed['external']}")
    print(f"CONTEXT: {parsed['context']}")

if __name__ == "__main__":
    main()
