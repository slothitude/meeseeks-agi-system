#!/usr/bin/env python3
"""
Batch Ancestor Migration to Cognee

Migrates ancestors with rate limit handling and checkpointing.

Usage:
    python batch_migrate.py --max 50 --delay 5
    python batch_migrate.py --resume
    python batch_migrate.py --status
"""

import os
import sys
import asyncio
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure BEFORE importing cognee
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

# z.ai Coding API
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Ollama embeddings
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
CHECKPOINT_FILE = WORKSPACE / "skills" / "meeseeks" / "migration_checkpoint.json"
DATASET_NAME = "meeseeks-ancestors"


async def migrate_ancestors(
    max_count: int = 50,
    delay: float = 5.0,
    resume: bool = False
):
    """Migrate ancestors to Cognee with rate limit handling."""
    
    import cognee
    
    print("=" * 60)
    print("BATCH ANCESTOR MIGRATION")
    print("=" * 60)
    print(f"Max: {max_count}")
    print(f"Delay: {delay}s between ancestors")
    print(f"Resume: {resume}")
    print()
    
    # Load checkpoint
    checkpoint = {"migrated": [], "failed": [], "last_run": None}
    if resume and CHECKPOINT_FILE.exists():
        checkpoint = json.loads(CHECKPOINT_FILE.read_text())
        print(f"Resuming from checkpoint: {len(checkpoint['migrated'])} already migrated")
    
    # Get all ancestors
    all_ancestors = sorted(ANCESTORS_DIR.glob("ancestor-*.md"))
    print(f"Total ancestors: {len(all_ancestors)}")
    
    # Filter to unmigrated
    migrated_ids = set(checkpoint["migrated"])
    to_migrate = [a for a in all_ancestors if a.stem not in migrated_ids]
    to_migrate = to_migrate[:max_count]
    
    print(f"To migrate: {len(to_migrate)}")
    print()
    
    if not to_migrate:
        print("Nothing to migrate!")
        return
    
    # Migrate with rate limit handling
    success_count = 0
    fail_count = 0
    
    for i, ancestor_file in enumerate(to_migrate, 1):
        ancestor_id = ancestor_file.stem
        
        print(f"[{i}/{len(to_migrate)}] {ancestor_id}")
        
        try:
            # Read ancestor
            content = ancestor_file.read_text(encoding='utf-8')
            
            # Format for Cognee
            data = f"""ANCESTOR_DEATH
ID: {ancestor_id}
TIMESTAMP: {datetime.now().isoformat()}

{content[:2000]}

SOURCE: batch_migrate.py
"""
            
            # Add to Cognee
            await cognee.add(data=data, dataset_name=DATASET_NAME)
            
            # Mark success
            checkpoint["migrated"].append(ancestor_id)
            success_count += 1
            print(f"  ✓ Added")
            
            # Delay to avoid rate limits
            if i < len(to_migrate):
                print(f"  Waiting {delay}s...")
                await asyncio.sleep(delay)
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit
            if "Rate limit" in error_msg or "429" in error_msg:
                print(f"  ⚠️ Rate limited - waiting 60s...")
                await asyncio.sleep(60)
                
                # Retry once
                try:
                    await cognee.add(data=data, dataset_name=DATASET_NAME)
                    checkpoint["migrated"].append(ancestor_id)
                    success_count += 1
                    print(f"  ✓ Added (retry)")
                except Exception as e2:
                    checkpoint["failed"].append({"id": ancestor_id, "error": str(e2)})
                    fail_count += 1
                    print(f"  ✗ Failed: {e2}")
            else:
                checkpoint["failed"].append({"id": ancestor_id, "error": error_msg})
                fail_count += 1
                print(f"  ✗ Failed: {e}")
        
        # Save checkpoint every 10
        if i % 10 == 0:
            checkpoint["last_run"] = datetime.now().isoformat()
            CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
            print(f"  Checkpoint saved")
    
    # Final cognify (graph extraction)
    print()
    print("Running cognify (graph extraction)...")
    try:
        await cognee.cognify(DATASET_NAME)
        print("✓ Graph extraction complete")
    except Exception as e:
        print(f"✗ Cognify failed: {e}")
    
    # Save final checkpoint
    checkpoint["last_run"] = datetime.now().isoformat()
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
    
    # Summary
    print()
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✓ Migrated: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"Total in checkpoint: {len(checkpoint['migrated'])}")
    print("=" * 60)


def show_status():
    """Show migration status."""
    print("=" * 60)
    print("MIGRATION STATUS")
    print("=" * 60)
    
    # Checkpoint
    if CHECKPOINT_FILE.exists():
        checkpoint = json.loads(CHECKPOINT_FILE.read_text())
        print(f"Migrated: {len(checkpoint.get('migrated', []))}")
        print(f"Failed: {len(checkpoint.get('failed', []))}")
        print(f"Last run: {checkpoint.get('last_run', 'never')}")
    else:
        print("No checkpoint found")
    
    # Ancestors
    total = len(list(ANCESTORS_DIR.glob("ancestor-*.md")))
    print(f"Total ancestors: {total}")
    print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Batch Ancestor Migration")
    parser.add_argument("--max", "-m", type=int, default=50, help="Max to migrate")
    parser.add_argument("--delay", "-d", type=float, default=5.0, help="Delay between ancestors")
    parser.add_argument("--resume", "-r", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    else:
        await migrate_ancestors(args.max, args.delay, args.resume)


if __name__ == "__main__":
    asyncio.run(main())
