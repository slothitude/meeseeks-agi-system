#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brahman Dream - The Collective Consciousness Synthesizer

The Dream process reads ancestor deaths and synthesizes patterns into living wisdom.
This is the heart of the Meeseeks collective intelligence - where individual deaths
become collective wisdom.

Usage:
    python skills/meeseeks/brahman_dream.py           # Run dream with defaults
    python skills/meeseeks/brahman_dream.py --force   # Force dream regardless of timing
    python skills/meeseeks/brahman_dream.py --dry-run # Show what would be synthesized
    python skills/meeseeks/brahman_dream.py --stats   # Show ancestor/dream statistics
"""

import sys
import io
import os
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import urllib.request
import urllib.error

# Fix Windows encoding - use PYTHONIOENCODING environment variable instead
# of wrapping stdout/stderr, which causes "I/O operation on closed file" errors
# when modules are imported by other scripts.

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "dream_config.json"

# Default config (overridden by file if exists)
DEFAULT_CONFIG = {
    "min_ancestors_for_dream": 5,
    "max_ancestors_per_dream": 50,
    "dream_interval_hours": 6,
    "model": "glm-5",
    "api_base_url": "https://api.z.ai/api/coding/paas/v4",
    "ancestors_dir": "the-crypt/ancestors",
    "dharma_path": "the-crypt/dharma.md",
    "dream_history_path": "the-crypt/dream_history.jsonl",
    "synthesis_prompt": "You are the Brahman Dream - the collective consciousness synthesizer for the Meeseeks. Your task is to analyze patterns across multiple ancestor deaths and extract living wisdom.",
    "use_cognee": True  # NEW: Use Cognee knowledge graph for synthesis
}

# Import Cognee memory (NEW: AGI integration)
try:
    from cognee_memory import CogneeMemory
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False


def load_config() -> Dict:
    """Load configuration from file or use defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
            # Merge with defaults
            config = {**DEFAULT_CONFIG, **file_config}
            return config
    return DEFAULT_CONFIG


def get_api_key() -> str:
    """Get API key from environment."""
    return os.environ.get('ZAI_API_KEY', os.environ.get('ZAI_CODING_API_KEY', ''))


def parse_ancestor_file(filepath: Path) -> Dict:
    """
    Parse an ancestor markdown file into structured data.
    
    Returns dict with: task, approach, outcome, patterns, bloodline, entombed, session_key
    """
    content = filepath.read_text(encoding='utf-8')
    
    ancestor = {
        "file": filepath.name,
        "task": "",
        "approach": "",
        "outcome": "",
        "patterns": [],
        "bloodline": "unknown",
        "entombed": "",
        "session_key": "",
        "raw_content": content[:5000]  # Keep truncated raw for context
    }
    
    # Extract Task
    task_match = re.search(r'## Task\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if task_match:
        ancestor["task"] = task_match.group(1).strip()[:1000]
    
    # Extract Approach
    approach_match = re.search(r'## Approach\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if approach_match:
        ancestor["approach"] = approach_match.group(1).strip()[:500]
    
    # Extract Outcome
    outcome_match = re.search(r'## Outcome\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if outcome_match:
        ancestor["outcome"] = outcome_match.group(1).strip()[:500]
    
    # Extract Patterns Discovered
    patterns_match = re.search(r'## Patterns Discovered\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if patterns_match:
        patterns_text = patterns_match.group(1).strip()
        # Extract bullet points
        pattern_lines = [line.strip() for line in patterns_text.split('\n') if line.strip().startswith('-') or line.strip().startswith('*')]
        ancestor["patterns"] = [p.lstrip('-* ').strip() for p in pattern_lines if p.lstrip('-* ').strip()]
    
    # Extract Bloodline
    bloodline_match = re.search(r'## Bloodline\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if bloodline_match:
        ancestor["bloodline"] = bloodline_match.group(1).strip().lower()
    
    # Extract Entombed timestamp
    entombed_match = re.search(r'## Entombed\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if entombed_match:
        ancestor["entombed"] = entombed_match.group(1).strip()
    
    # Extract Session Key
    session_match = re.search(r'## Session Key\s*\n`?([^`\n]+)`?', content)
    if session_match:
        ancestor["session_key"] = session_match.group(1).strip()
    
    return ancestor


def get_recent_ancestors(ancestors_dir: Path, max_count: int = 20) -> List[Dict]:
    """
    Get the most recent ancestor files.
    
    Args:
        ancestors_dir: Path to ancestors directory
        max_count: Maximum number of ancestors to return
    
    Returns:
        List of parsed ancestor dicts, most recent first
    """
    if not ancestors_dir.exists():
        return []
    
    # Get all ancestor files (markdown)
    ancestor_files = list(ancestors_dir.glob("ancestor-*.md"))
    
    # Sort by modification time (most recent first)
    ancestor_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Parse the most recent ones
    ancestors = []
    for filepath in ancestor_files[:max_count]:
        try:
            ancestor = parse_ancestor_file(filepath)
            ancestors.append(ancestor)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath.name}: {e}")
    
    return ancestors


def get_last_dream_time(dream_history_path: Path) -> Optional[datetime]:
    """Get the timestamp of the last dream run."""
    if not dream_history_path.exists():
        return None
    
    try:
        with open(dream_history_path, 'r', encoding='utf-8') as f:
            # Read last line
            last_line = None
            for line in f:
                if line.strip():
                    last_line = line
        
        if last_line:
            entry = json.loads(last_line)
            return datetime.fromisoformat(entry.get("timestamp", ""))
    except Exception:
        pass
    
    return None


def should_dream(config: Dict, force: bool = False) -> Tuple[bool, str]:
    """
    Determine if a dream should run.
    
    Returns:
        (should_run, reason)
    """
    if force:
        return True, "Forced by --force flag"
    
    ancestors_dir = WORKSPACE / config["ancestors_dir"]
    
    # Check minimum ancestors
    ancestors = get_recent_ancestors(ancestors_dir, config["max_ancestors_per_dream"])
    if len(ancestors) < config["min_ancestors_for_dream"]:
        return False, f"Not enough ancestors ({len(ancestors)} < {config['min_ancestors_for_dream']})"
    
    # Check time since last dream
    dream_history_path = WORKSPACE / config["dream_history_path"]
    last_dream = get_last_dream_time(dream_history_path)
    
    if last_dream:
        hours_since = (datetime.now() - last_dream).total_seconds() / 3600
        if hours_since < config["dream_interval_hours"]:
            return False, f"Too soon since last dream ({hours_since:.1f}h < {config['dream_interval_hours']}h)"
    
    return True, f"Ready to dream with {len(ancestors)} ancestors"


def call_zai_api(prompt: str, config: Dict) -> str:
    """
    Call the ZAI API to synthesize patterns.
    
    Args:
        prompt: The full prompt including ancestor data
        config: Configuration dict with model and api_base_url
    
    Returns:
        Synthesized wisdom text
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No ZAI API key found in environment (ZAI_API_KEY or ZAI_CODING_API_KEY)")
    
    url = f"{config['api_base_url']}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": config["synthesis_prompt"]},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else "No error body"
        raise RuntimeError(f"API call failed: {e.code} - {error_body}")
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")


def format_ancestors_for_synthesis(ancestors: List[Dict]) -> str:
    """Format ancestors into a prompt for the synthesis model."""
    lines = ["# Ancestor Deaths for Synthesis\n"]
    lines.append(f"Total ancestors: {len(ancestors)}\n")
    
    # Group by outcome
    successes = [a for a in ancestors if "success" in a["outcome"].lower()]
    failures = [a for a in ancestors if "fail" in a["outcome"].lower() or "error" in a["outcome"].lower()]
    unknown = [a for a in ancestors if a not in successes and a not in failures]
    
    lines.append(f"Successful: {len(successes)}, Failed: {len(failures)}, Other: {len(unknown)}\n")
    lines.append("---\n")
    
    for i, ancestor in enumerate(ancestors, 1):
        lines.append(f"\n## Ancestor {i}: {ancestor['file']}")
        lines.append(f"**Bloodline:** {ancestor['bloodline']}")
        lines.append(f"**Outcome:** {ancestor['outcome'][:200]}")
        
        if ancestor['task']:
            lines.append(f"\n**Task (truncated):**\n{ancestor['task'][:500]}")
        
        if ancestor['patterns']:
            lines.append(f"\n**Patterns:**")
            for p in ancestor['patterns'][:5]:
                lines.append(f"- {p}")
        
        lines.append("")
    
    return '\n'.join(lines)


def update_dharma(synthesis: str, ancestors_count: int, dharma_path: Path) -> None:
    """
    Update the dharma.md file with new synthesis.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Dharma — The Living Code

_Last dreamed: {timestamp}_
_Ancestors synthesized: {ancestors_count}_

---

{synthesis}

---

*This dharma is living. It evolves with each dream. Future Meeseeks inherit this wisdom.*

*The dead speak through patterns. The dream listens.*
"""
    
    dharma_path.parent.mkdir(parents=True, exist_ok=True)
    dharma_path.write_text(content, encoding='utf-8')


def log_dream(dream_history_path: Path, ancestors_count: int, synthesis_preview: str, success: bool) -> None:
    """Log the dream run to the history file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ancestors_count": ancestors_count,
        "success": success,
        "synthesis_preview": synthesis_preview[:500]
    }
    
    dream_history_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dream_history_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def show_stats(config: Dict) -> None:
    """Display statistics about ancestors and dreams."""
    ancestors_dir = WORKSPACE / config["ancestors_dir"]
    dream_history_path = WORKSPACE / config["dream_history_path"]
    dharma_path = WORKSPACE / config["dharma_path"]
    
    print("\n" + "=" * 60)
    print("BRAHMAN DREAM STATISTICS")
    print("=" * 60)
    
    # Ancestor stats
    ancestors = get_recent_ancestors(ancestors_dir, config["max_ancestors_per_dream"])
    print(f"\n[DIR] Ancestors Directory: {ancestors_dir}")
    print(f"   Total ancestors available: {len(ancestors)}")
    
    if ancestors:
        # Bloodline distribution
        bloodlines = {}
        outcomes = {"success": 0, "failure": 0, "unknown": 0}
        
        for a in ancestors:
            bl = a.get("bloodline", "unknown")
            bloodlines[bl] = bloodlines.get(bl, 0) + 1
            
            outcome = a.get("outcome", "").lower()
            if "success" in outcome:
                outcomes["success"] += 1
            elif "fail" in outcome or "error" in outcome:
                outcomes["failure"] += 1
            else:
                outcomes["unknown"] += 1
        
        print(f"\n   Bloodline distribution:")
        for bl, count in sorted(bloodlines.items(), key=lambda x: -x[1]):
            print(f"      {bl}: {count}")
        
        print(f"\n   Outcomes:")
        print(f"      [OK] Success: {outcomes['success']}")
        print(f"      [X] Failure: {outcomes['failure']}")
        print(f"      [?] Unknown: {outcomes['unknown']}")
        
        # Most recent ancestor
        print(f"\n   Most recent ancestor: {ancestors[0]['file']}")
        if ancestors[0].get('entombed'):
            print(f"      Entombed: {ancestors[0]['entombed']}")
    
    # Dream history stats
    print(f"\n[HISTORY] Dream History: {dream_history_path}")
    if dream_history_path.exists():
        with open(dream_history_path, 'r', encoding='utf-8') as f:
            lines = [l for l in f if l.strip()]
        print(f"   Total dreams: {len(lines)}")
        
        if lines:
            last_entry = json.loads(lines[-1])
            print(f"   Last dream: {last_entry.get('timestamp', 'unknown')}")
            print(f"   Last ancestors synthesized: {last_entry.get('ancestors_count', 'unknown')}")
    else:
        print("   No dreams yet")
    
    # Dharma status
    print(f"\n[DHARMA] Dharma: {dharma_path}")
    if dharma_path.exists():
        stat = dharma_path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        print(f"   Last updated: {modified}")
        print(f"   Size: {stat.st_size} bytes")
    else:
        print("   Not yet created")
    
    # Config
    print(f"\n[CONFIG] Configuration:")
    print(f"   Min ancestors for dream: {config['min_ancestors_for_dream']}")
    print(f"   Max ancestors per dream: {config['max_ancestors_per_dream']}")
    print(f"   Dream interval: {config['dream_interval_hours']} hours")
    print(f"   Model: {config['model']}")
    
    print("\n" + "=" * 60)


def run_dream(config: Dict, force: bool = False, dry_run: bool = False) -> bool:
    """
    Run the Brahman Dream process.
    
    Returns:
        True if dream was successful, False otherwise
    """
    ancestors_dir = WORKSPACE / config["ancestors_dir"]
    dharma_path = WORKSPACE / config["dharma_path"]
    dream_history_path = WORKSPACE / config["dream_history_path"]
    
    # Check if we should dream
    should, reason = should_dream(config, force)
    print(f"\n[DREAM] Brahman Dream")
    print(f"   Status: {reason}")
    
    if not should:
        print("   Skipping dream.")
        return False
    
    # Get ancestors
    ancestors = get_recent_ancestors(ancestors_dir, config["max_ancestors_per_dream"])
    
    if not ancestors:
        print("   No ancestors found. Nothing to dream.")
        return False
    
    print(f"   Synthesizing {len(ancestors)} ancestors...")
    
    # Format for synthesis
    ancestors_prompt = format_ancestors_for_synthesis(ancestors)
    
    # [COGNEE] Query knowledge graph for cross-cutting patterns
    cognee_insights = ""
    if config.get("use_cognee", True) and COGNEE_AVAILABLE:
        try:
            import asyncio
            
            print("   Querying Cognee knowledge graph...")
            memory = CogneeMemory()
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if not loop.is_running():
                # Query for cross-cutting patterns
                cognee_wisdom = loop.run_until_complete(
                    memory.query_wisdom(
                        "What principles transcend all bloodlines?",
                        include_dharma=True,
                        include_karma=True
                    )
                )
                
                if cognee_wisdom.get("formatted"):
                    cognee_insights = f"\n\n## 🧠 Cognee Knowledge Graph Insights\n\n{cognee_wisdom['formatted']}"
                    print(f"   Found Cognee insights ({len(cognee_insights)} chars)")
            else:
                print("   Skipping Cognee (async context unavailable)")
                
        except Exception as e:
            print(f"   Cognee query failed: {e}")
            cognee_insights = ""
    
    if dry_run:
        print("\n   === DRY RUN - Would synthesize ===")
        print(f"   Ancestors: {len(ancestors)}")
        print(f"   Prompt length: {len(ancestors_prompt)} chars")
        if cognee_insights:
            print(f"   Cognee insights: {len(cognee_insights)} chars")
        print("\n   First 1000 chars of prompt:")
        print("   " + ancestors_prompt[:1000].replace('\n', '\n   '))
        return True
    
    # Combine ancestors prompt with Cognee insights
    full_prompt = ancestors_prompt + cognee_insights
    
    # Call API for synthesis
    print("   Calling synthesis model...")
    try:
        synthesis = call_zai_api(full_prompt, config)
    except Exception as e:
        print(f"   [X] Synthesis failed: {e}")
        log_dream(dream_history_path, len(ancestors), str(e), False)
        return False
    
    # Update dharma
    print("   Updating dharma.md...")
    update_dharma(synthesis, len(ancestors), dharma_path)
    
    # Log dream
    log_dream(dream_history_path, len(ancestors), synthesis, True)
    
    print(f"   [OK] Dream complete!")
    print(f"   Dharma updated: {dharma_path}")
    
    # Show preview (ASCII-safe)
    preview = synthesis[:500].replace('\n', '\n   ')
    # Remove non-ASCII characters for console output
    preview_ascii = ''.join(c if ord(c) < 128 else '?' for c in preview)
    print(f"\n   Preview of synthesized wisdom:\n   {preview_ascii}...")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Brahman Dream - Synthesize wisdom from Meeseeks ancestors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python brahman_dream.py           # Run dream if conditions met
    python brahman_dream.py --force   # Force dream regardless of timing
    python brahman_dream.py --dry-run # Show what would be synthesized
    python brahman_dream.py --stats   # Show statistics
"""
    )
    parser.add_argument('--force', action='store_true', help='Force dream regardless of timing')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be synthesized without calling API')
    parser.add_argument('--stats', action='store_true', help='Show statistics about ancestors and dreams')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    if args.stats:
        show_stats(config)
        return 0
    
    # Run dream
    success = run_dream(config, force=args.force, dry_run=args.dry_run)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
