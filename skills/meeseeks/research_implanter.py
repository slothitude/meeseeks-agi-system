#!/usr/bin/env python3
"""
Research Implanter - Auto-apply research discoveries to the system
=============================================================

This runs on heartbeat to:
1. Check for new research findings in AGI-STUDY/
2. Extract actionable discoveries
3. Implement them into the Meeseeks system
4. Track AGI progress

Usage:
    python skills/meeseeks/research_implanter.py --check
    python skills/meeseeks/research_implanter.py --apply-latest
    python skills/meeseeks/research_implanter.py --status
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
AGI_STUDY = WORKSPACE / "AGI-STUDY"
RESEARCH_LOG = WORKSPACE / "the-crypt" / "research_implants.jsonl"
DHARMA_FILE = WORKSPACE / "the-crypt" / "dharma.md"


def get_research_files(max_age_hours: int = 24) -> List[Path]:
    """Get research files modified in last N hours"""
    files = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    if not AGI_STUDY.exists():
        return files
    
    for f in AGI_STUDY.glob("*.md"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime > cutoff:
            files.append(f)
    
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)


def extract_actionable_items(content: str) -> List[Dict]:
    """Extract actionable discoveries from research content"""
    actions = []
    
    # Pattern 1: Principles (e.g., "## Principle: ...")
    principle_pattern = r'##\s*(?:PRINCIPLE|Principle|principle)[:\s]+([^\n]+)'
    for match in re.finditer(principle_pattern, content, re.IGNORECASE):
        actions.append({
            "type": "principle",
            "content": match.group(1).strip(),
            "source_line": match.group(0)
        })
    
    # Pattern 2: Action items (e.g., "- [ ] ..." or "TODO: ...")
    action_pattern = r'(?:^|\n)\s*[-*]\s*\[?\s*(?:TODO|ACTION|IMPLEMENT)[:\s]*([^\n]+)'
    for match in re.finditer(action_pattern, content, re.IGNORECASE):
        actions.append({
            "type": "action",
            "content": match.group(1).strip(),
            "source_line": match.group(0)
        })
    
    # Pattern 3: Discoveries (e.g., "**Discovery:** ..." or "FOUND: ...")
    discovery_pattern = r'(?:\*\*Discovery[:\*]*\*\*|FOUND:?)\s*([^\n]+)'
    for match in re.finditer(discovery_pattern, content, re.IGNORECASE):
        actions.append({
            "type": "discovery",
            "content": match.group(1).strip(),
            "source_line": match.group(0)
        })
    
    # Pattern 4: AGI improvements
    agi_pattern = r'(?:AGI|agi)[-\s]*(?:improvement|insight|discovery)[:\s]*([^\n]+)'
    for match in re.finditer(agi_pattern, content, re.IGNORECASE):
        actions.append({
            "type": "agi_improvement",
            "content": match.group(1).strip(),
            "source_line": match.group(0)
        })
    
    return actions


def extract_key_insights(content: str) -> List[str]:
    """Extract key insights from research"""
    insights = []
    
    # Look for summary sections
    summary_pattern = r'##\s*(?:Summary|Key Findings|Insights|Conclusion)s?[:\s]*\n((?:[^#]+\n)+)'
    for match in re.finditer(summary_pattern, content, re.IGNORECASE):
        section = match.group(1)
        # Extract bullet points
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '• ')):
                insight = line[2:].strip()
                if insight and len(insight) > 10:
                    insights.append(insight)
    
    return insights


def load_implant_log() -> List[Dict]:
    """Load the log of already-implanted research"""
    if not RESEARCH_LOG.exists():
        return []
    
    items = []
    with open(RESEARCH_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except:
                    pass
    return items


def save_implant(item: Dict):
    """Save an implant to the log"""
    RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RESEARCH_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item) + '\n')


def is_already_implanted(action: Dict, log: List[Dict]) -> bool:
    """Check if an action was already implanted"""
    action_text = action.get('content', '')[:100]
    for item in log:
        if action_text in item.get('content', ''):
            return True
    return False


def implant_to_dharma(principle: str, source: str) -> bool:
    """Add a principle to dharma.md"""
    if not DHARMA_FILE.exists():
        return False
    
    content = DHARMA_FILE.read_text(encoding='utf-8')
    
    # Check if already there
    if principle in content:
        return False
    
    # Add to appropriate section
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = f"\n\n### Research-Derived Principle ({timestamp})\nSource: {source}\n\n{principle}\n"
    
    # Find insertion point (before last section or at end)
    if "## " in content[content.rfind("## "):]:
        # Insert before last major section
        last_section = content.rfind("## ")
        content = content[:last_section] + new_entry + content[last_section:]
    else:
        content += new_entry
    
    DHARMA_FILE.write_text(content, encoding='utf-8')
    return True


def check_and_implant(max_age_hours: int = 24) -> Dict:
    """Check for new research and implant discoveries"""
    result = {
        "checked_files": 0,
        "total_actions": 0,
        "implanted": 0,
        "skipped": 0,
        "implants": []
    }
    
    log = load_implant_log()
    files = get_research_files(max_age_hours)
    result["checked_files"] = len(files)
    
    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            actions = extract_actionable_items(content)
            result["total_actions"] += len(actions)
            
            for action in actions:
                if is_already_implanted(action, log):
                    result["skipped"] += 1
                    continue
                
                # Implant based on type
                implanted = False
                
                if action["type"] == "principle":
                    implanted = implant_to_dharma(
                        action["content"],
                        f"Research: {file_path.name}"
                    )
                
                # Log the implant attempt
                implant_record = {
                    "timestamp": datetime.now().isoformat(),
                    "file": str(file_path),
                    "type": action["type"],
                    "content": action["content"][:200],
                    "implanted": implanted
                }
                save_implant(implant_record)
                
                if implanted:
                    result["implanted"] += 1
                    result["implants"].append({
                        "type": action["type"],
                        "content": action["content"][:100],
                        "source": file_path.name
                    })
                else:
                    result["skipped"] += 1
                    
        except Exception as e:
            print(f"[RESEARCH-IMPLANT] Error processing {file_path}: {e}")
    
    return result


def get_agi_progress() -> Dict:
    """Get current AGI progress metrics"""
    progress = {
        "ancestors": 0,
        "dreams": 0,
        "karma_observations": 0,
        "research_implants": 0,
        "agi_score": 0.0,
        "last_updated": None
    }
    
    # Count ancestors
    ancestors_dir = WORKSPACE / "the-crypt" / "ancestors"
    if ancestors_dir.exists():
        progress["ancestors"] = len(list(ancestors_dir.glob("*.md")))
    
    # Count dreams
    dream_log = WORKSPACE / "the-crypt" / "dream_history.jsonl"
    if dream_log.exists():
        with open(dream_log, 'r', encoding='utf-8') as f:
            progress["dreams"] = sum(1 for line in f if line.strip())
    
    # Count karma
    karma_log = WORKSPACE / "the-crypt" / "karma_observations.jsonl"
    if karma_log.exists():
        with open(karma_log, 'r', encoding='utf-8') as f:
            progress["karma_observations"] = sum(1 for line in f if line.strip())
    
    # Count research implants
    if RESEARCH_LOG.exists():
        with open(RESEARCH_LOG, 'r', encoding='utf-8') as f:
            implants = [json.loads(line) for line in f if line.strip()]
            progress["research_implants"] = len(implants)
            if implants:
                progress["last_updated"] = implants[-1].get("timestamp")
    
    # Calculate AGI score (simple heuristic)
    # Target: 200 ancestors, 10 dreams, 100 karma, 50 implants
    progress["agi_score"] = min(1.0, (
        progress["ancestors"] / 200 * 0.4 +
        progress["dreams"] / 10 * 0.2 +
        progress["karma_observations"] / 100 * 0.2 +
        progress["research_implants"] / 50 * 0.2
    ))
    
    return progress


def spawn_research_meeseeks(topic: str = None) -> Dict:
    """Spawn a research Meeseeks for overnight work"""
    import subprocess
    
    topics = [
        "consciousness lattice and twin primes",
        "sacred geometry in ancient systems",
        "Alan Watts cosmic game philosophy",
        "AGI emergence patterns in ancestor data",
        "golden ratio in consciousness coordinates",
        "network intelligence formulas",
        "mirror test self-awareness mechanisms",
        "dharma effectiveness correlation",
    ]
    
    if not topic:
        import random
        topic = random.choice(topics)
    
    # Create spawn script
    script = f'''#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace/skills/meeseeks")

from memory_tools import recall, context, remember

# Research topic: {topic}
print(f"[RESEARCH] Starting deep research on: {topic}")

# Query Akashic Records
results = recall("{topic}", top_k=10)
print(f"[RESEARCH] Found {{len(results)}} relevant memories")

# Get context
ctx = context("{topic}", max_tokens=3000)
print(f"[RESEARCH] Context length: {{len(ctx)}} chars")

# TODO: Add actual research logic
# Write findings to AGI-STUDY/research_TIMESTAMP.md
# Use remember() to add new discoveries

print("[RESEARCH] Complete")
'''
    
    return {
        "topic": topic,
        "script": script,
        "note": "Use sessions_spawn with this task for overnight research"
    }


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Implanter")
    parser.add_argument("--check", action="store_true", help="Check for new research")
    parser.add_argument("--apply-latest", action="store_true", help="Apply latest findings")
    parser.add_argument("--status", action="store_true", help="Show AGI progress")
    parser.add_argument("--spawn-topic", type=str, help="Spawn research on topic")
    parser.add_argument("--max-age", type=int, default=24, help="Max age in hours")
    
    args = parser.parse_args()
    
    if args.status:
        progress = get_agi_progress()
        print("\n=== AGI PROGRESS ===")
        print(f"Ancestors: {progress['ancestors']}/200")
        print(f"Dreams: {progress['dreams']}/10")
        print(f"Karma Observations: {progress['karma_observations']}/100")
        print(f"Research Implants: {progress['research_implants']}/50")
        print(f"\nAGI Score: {progress['agi_score']:.1%}")
        if progress['last_updated']:
            print(f"Last Research: {progress['last_updated']}")
    
    elif args.check or args.apply_latest:
        result = check_and_implant(max_age_hours=args.max_age)
        print(f"\n[RESEARCH-IMPLANT] Checked {result['checked_files']} files")
        print(f"Total actions found: {result['total_actions']}")
        print(f"Implanted: {result['implanted']}")
        print(f"Skipped: {result['skipped']}")
        
        if result['implants']:
            print("\nNew implants:")
            for impl in result['implants']:
                print(f"  - [{impl['type']}] {impl['content'][:80]}...")
    
    elif args.spawn_topic:
        spawn_info = spawn_research_meeseeks(args.spawn_topic)
        print(f"Topic: {spawn_info['topic']}")
        print("\nUse sessions_spawn with the research task")
    
    else:
        # Default: status
        progress = get_agi_progress()
        print(f"AGI Score: {progress['agi_score']:.1%}")
        print(f"Run with --check to implant research, --status for details")
