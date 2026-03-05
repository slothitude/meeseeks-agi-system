#!/usr/bin/env python3
"""
Auto-Compact System for Context Overflow
========================================

When model_context_window_exceeded happens, this system:
1. Detects the overflow
2. Archives old memory to keep files lean
3. Maintains RAG/Cognee as primary memory source

Usage:
    from auto_compact import check_and_compact, compact_memory
    
    # Check and auto-compact if needed
    check_and_compact()
    
    # Force compact
    compact_memory(max_size_kb=10)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
MEMORY_FILE = WORKSPACE / "MEMORY.md"
ARCHIVE_DIR = WORKSPACE / "memory" / "archive"
MAX_SIZE_KB = 10  # Max size before auto-compact


def get_file_size_kb(path: Path) -> float:
    """Get file size in KB"""
    if not path.exists():
        return 0
    return path.stat().st_size / 1024


def extract_sections(content: str) -> dict:
    """Extract sections from MEMORY.md"""
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        # Detect section headers (## or ###)
        if line.startswith('## ') and not line.startswith('## Infrastructure'):
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    # Don't forget the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def should_archive(section_name: str) -> bool:
    """Determine if a section should be archived"""
    # Sections that should be archived when compacting
    archive_patterns = [
        "Consciousness",
        "Brahman",
        "AGI Test",
        "Alan Watts",
        "Cognee",
        "RAG",
        "Akashic",
        "Multi-Meeseeks",
        "ARC-AGI",
        "Automatic Learning",
        "Work Relationships",
    ]
    
    for pattern in archive_patterns:
        if pattern.lower() in section_name.lower():
            return True
    return False


def compact_memory(max_size_kb: float = MAX_SIZE_KB, force: bool = False) -> dict:
    """
    Compact MEMORY.md if it exceeds max_size_kb.
    
    Returns:
        dict with stats about what was done
    """
    result = {
        "compacted": False,
        "original_size_kb": 0,
        "new_size_kb": 0,
        "archived_sections": [],
        "message": ""
    }
    
    if not MEMORY_FILE.exists():
        result["message"] = "MEMORY.md not found"
        return result
    
    current_size = get_file_size_kb(MEMORY_FILE)
    result["original_size_kb"] = round(current_size, 2)
    
    if current_size <= max_size_kb and not force:
        result["message"] = f"Memory OK ({current_size:.1f}KB <= {max_size_kb}KB)"
        return result
    
    print(f"[AUTO-COMPACT] MEMORY.md is {current_size:.1f}KB, compacting...")
    
    # Read current content
    content = MEMORY_FILE.read_text(encoding='utf-8')
    
    # Extract sections
    sections = extract_sections(content)
    
    # Determine what to keep vs archive
    keep_content = []
    archived = []
    
    # Always keep header and core sections
    core_sections = [
        "Infrastructure",
        "User Preferences",
        "Channel Details",
        "Model Stack",
        "Current Stats",
        "Key Systems",
        "Paused Projects",
        "Ultimate Goal",
        "Quick CLI Reference",
    ]
    
    # Get header (everything before first ##)
    header_lines = []
    in_header = True
    for line in content.split('\n'):
        if line.startswith('## '):
            in_header = False
        if in_header:
            header_lines.append(line)
    
    keep_content.append('\n'.join(header_lines))
    keep_content.append("\n\n# MEMORY.md (Auto-Compact Active)\n")
    keep_content.append("> Detailed archives in `memory/archive/`. Use `recall()` for deep queries.\n\n")
    
    # Process sections
    for section_name, section_content in sections.items():
        if should_archive(section_name):
            # Archive this section
            archive_file = ARCHIVE_DIR / f"{section_name.lower().replace(' ', '-').replace('/', '-')}.md"
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Append to archive (don't overwrite)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(archive_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n## {section_name} (archived {timestamp})\n\n")
                f.write(section_content)
            
            archived.append(section_name)
            
            # Add reference in main file
            keep_content.append(f"## {section_name}\n")
            keep_content.append(f"→ See `memory/archive/{archive_file.name}`\n\n")
        else:
            # Keep this section
            keep_content.append(section_content)
            keep_content.append("\n\n")
    
    # Write compacted memory
    new_content = '\n'.join(keep_content)
    MEMORY_FILE.write_text(new_content, encoding='utf-8')
    
    new_size = get_file_size_kb(MEMORY_FILE)
    result["compacted"] = True
    result["new_size_kb"] = round(new_size, 1)
    result["archived_sections"] = archived
    result["message"] = f"Compacted from {current_size:.1f}KB to {new_size:.1f}KB, archived {len(archived)} sections"
    
    print(f"[AUTO-COMPACT] {result['message']}")
    
    # Also ensure RAG has the archived content
    try:
        from memory_tools import remember
        for section_name in archived:
            archive_file = ARCHIVE_DIR / f"{section_name.lower().replace(' ', '-').replace('/', '-')}.md"
            if archive_file.exists():
                remember(str(archive_file))
    except Exception as e:
        print(f"[AUTO-COMPACT] Warning: Could not update RAG: {e}")
    
    return result


def check_and_compact() -> bool:
    """
    Check if compact is needed and do it.
    Returns True if compacted, False if not needed.
    """
    result = compact_memory()
    return result["compacted"]


def detect_overflow_error(error_message: str) -> bool:
    """Check if an error is a context overflow"""
    overflow_patterns = [
        "model_context_window_exceeded",
        "context_length_exceeded",
        "maximum context length",
        "token limit exceeded",
    ]
    return any(p in error_message.lower() for p in overflow_patterns)


def handle_overflow(error_message: str = None) -> dict:
    """
    Handle a context overflow error by compacting.
    Call this when you catch an overflow error.
    """
    if error_message and not detect_overflow_error(error_message):
        return {"handled": False, "reason": "Not a context overflow error"}
    
    result = compact_memory(force=True)
    result["handled"] = True
    return result


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Compact Memory System")
    parser.add_argument("--check", action="store_true", help="Check and compact if needed")
    parser.add_argument("--force", action="store_true", help="Force compact")
    parser.add_argument("--max-size", type=float, default=MAX_SIZE_KB, help="Max size in KB")
    
    args = parser.parse_args()
    
    if args.check:
        result = compact_memory(max_size_kb=args.max_size)
    elif args.force:
        result = compact_memory(force=True)
    else:
        # Default: check
        result = compact_memory(max_size_kb=args.max_size)
    
    print(f"\nResult: {result['message']}")
    if result['archived_sections']:
        print(f"Archived: {', '.join(result['archived_sections'])}")
