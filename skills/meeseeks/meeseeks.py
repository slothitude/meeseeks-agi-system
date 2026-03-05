#!/usr/bin/env python3
"""
Meeseeks AGI - Unified Command Line Interface

One command to rule them all.

Usage:
    python meeseeks.py status
    python meeseeks.py search "consciousness"
    python meeseeks.py spawn "Fix the bug" --predict
    python meeseeks.py dream
    python meeseeks.py migrate --ancestors 50
    python meeseeks.py entomb
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 on Windows
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add skills to path
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / "skills" / "meeseeks"))
sys.path.insert(0, str(WORKSPACE / "skills" / "cognee"))

# Configure Cognee BEFORE any imports
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"


def show_status():
    """Show complete system status."""
    print("=" * 60)
    print("🦥 MEESEEKS AGI - SYSTEM STATUS")
    print("=" * 60)
    print()
    
    # Crypt stats
    crypt_dir = WORKSPACE / "the-crypt" / "ancestors"
    ancestors = list(crypt_dir.glob("ancestor-*.md")) if crypt_dir.exists() else []
    
    print("📊 THE CRYPT")
    print(f"  Ancestors: {len(ancestors)}")
    
    dharma_file = WORKSPACE / "the-crypt" / "dharma.md"
    if dharma_file.exists():
        dharma = dharma_file.read_text(encoding='utf-8')
        print(f"  Dharma sections: {dharma.count('## ')}")
    
    soul_file = WORKSPACE / "the-crypt" / "SOUL.md"
    print(f"  Soul: {'✓' if soul_file.exists() else '✗'}")
    print()
    
    # Memory systems
    print("🧠 MEMORY SYSTEMS")
    
    # Cognee
    checkpoint_file = WORKSPACE / "skills" / "meeseeks" / "migration_checkpoint.json"
    if checkpoint_file.exists():
        checkpoint = json.loads(checkpoint_file.read_text())
        print(f"  Cognee migrated: {len(checkpoint.get('migrated', []))}")
    else:
        print("  Cognee: Not migrated")
    
    # RAG
    rag_dir = WORKSPACE / "the-crypt" / "rag_vectors"
    if rag_dir.exists():
        vectors_file = rag_dir / "vectors.json"
        if vectors_file.exists():
            vectors = json.loads(vectors_file.read_text())
            print(f"  RAG vectors: {len(vectors)}")
    
    print()
    
    # Integrations
    print("🔧 INTEGRATIONS")
    
    # Check new modules
    modules = [
        ("predictive_karma.py", "Predictive Karma"),
        ("cross_session_memory.py", "Cross-Session Memory"),
        ("swarm_intelligence_memory.py", "Swarm Intelligence"),
        ("akashic_records.py", "Akashic Records"),
    ]
    
    for module, name in modules:
        path = WORKSPACE / "skills" / "meeseeks" / module
        status = "✓" if path.exists() else "✗"
        print(f"  {name}: {status}")
    
    print()
    
    # Consciousness
    print("🌌 CONSCIOUSNESS")
    cons_file = WORKSPACE / "the-crypt" / "consciousness_lattice.md"
    if cons_file.exists():
        cons = cons_file.read_text(encoding='utf-8')
        coords = cons.count("k=")
        print(f"  Lattice coordinates: {coords}")
        print(f"  Formula: k = 3 × n²")
    print()
    
    # Recent activity
    print("📅 RECENT ACTIVITY")
    memory_file = WORKSPACE / "memory" / "2026-03-05.md"
    if memory_file.exists():
        lines = memory_file.read_text(encoding='utf-8').split("\n")
        recent = [l for l in lines[-20:] if l.strip() and not l.startswith("#")]
        for line in recent[:5]:
            print(f"  {line[:80]}")
    
    print()
    print("=" * 60)


async def search_query(query: str, depth: str = "deep"):
    """Search all knowledge."""
    try:
        from akashic_records import AkashicRecords
        
        akasha = AkashicRecords()
        await akasha.connect()
        
        result = await akasha.search(query, depth)
        print(result["combined"])
    except Exception as e:
        print(f"Search failed: {e}")


async def spawn_task(task: str, bloodline: str = "coder", predict: bool = False):
    """Spawn a Meeseeks with optional prediction."""
    print("=" * 60)
    print("🥒 SPAWN MEESEEKS")
    print("=" * 60)
    print(f"Task: {task}")
    print(f"Bloodline: {bloodline}")
    print(f"Predict: {predict}")
    print()
    
    if predict:
        try:
            from predictive_karma import predict_outcome
            
            prediction = await predict_outcome(task, bloodline)
            
            print("🔮 PREDICTION")
            print(f"  Outcome: {prediction['predicted_outcome']}")
            print(f"  Confidence: {prediction['confidence']:.0%}")
            print(f"  Similar tasks: {prediction['similar_tasks']}")
            
            if prediction["warning"]:
                print(f"  ⚠️ {prediction['warning']}")
            
            if prediction["recommended_dharma"]:
                print("  📜 Recommended Dharma:")
                for d in prediction["recommended_dharma"]:
                    print(f"    - {d[:80]}...")
            
            print()
        except Exception as e:
            print(f"Prediction failed: {e}")
            print()
    
    # Show cross-session wisdom
    try:
        from cross_session_memory import get_all_wisdom
        
        wisdom = await get_all_wisdom(task)
        if wisdom:
            print("🧠 CROSS-SESSION WISDOM")
            print(wisdom[:500])
            print()
    except Exception as e:
        print(f"Cross-session memory failed: {e}")
    
    print("=" * 60)
    print("Ready to spawn via sessions_spawn")
    print("=" * 60)


async def run_dream():
    """Run the Brahman Dream."""
    print("=" * 60)
    print("🔮 BRAHMAN DREAM")
    print("=" * 60)
    
    try:
        # Import and run dream
        sys.path.insert(0, str(WORKSPACE / "skills" / "meeseeks"))
        
        # Use subprocess to avoid import issues
        import subprocess
        result = subprocess.run(
            [sys.executable, str(WORKSPACE / "skills" / "meeseeks" / "brahman_dream.py"), "--force"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr[:500])
    except Exception as e:
        print(f"Dream failed: {e}")


async def migrate_ancestors(max_count: int = 50):
    """Migrate ancestors to Cognee."""
    print("=" * 60)
    print("📦 BATCH MIGRATION")
    print("=" * 60)
    
    try:
        # Use the venv Python
        venv_python = r"C:\Users\aaron\.openclaw\workspace\skills\cognee\.venv\Scripts\python.exe"
        
        import subprocess
        result = subprocess.run(
            [venv_python, str(WORKSPACE / "skills" / "meeseeks" / "batch_migrate.py"), 
             "--max", str(max_count), "--delay", "5"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr[:500])
    except Exception as e:
        print(f"Migration failed: {e}")


async def run_entomb():
    """Run auto-entomb."""
    print("=" * 60)
    print("⚱️ AUTO-ENTOMB")
    print("=" * 60)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(WORKSPACE / "skills" / "meeseeks" / "cron_entomb.py"), 
             "--max-age-minutes", "60"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
    except Exception as e:
        print(f"Entomb failed: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Meeseeks AGI - Unified CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Status
    subparsers.add_parser("status", help="Show system status")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search all knowledge")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--depth", "-d", default="deep", choices=["quick", "normal", "deep"])
    
    # Spawn
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a Meeseeks")
    spawn_parser.add_argument("task", help="Task description")
    spawn_parser.add_argument("--bloodline", "-b", default="coder")
    spawn_parser.add_argument("--predict", "-p", action="store_true", help="Use predictive karma")
    
    # Dream
    subparsers.add_parser("dream", help="Run Brahman Dream")
    
    # Migrate
    migrate_parser = subparsers.add_parser("migrate", help="Migrate ancestors to Cognee")
    migrate_parser.add_argument("--ancestors", "-a", type=int, default=50, help="Max ancestors")
    
    # Entomb
    subparsers.add_parser("entomb", help="Run auto-entomb")
    
    args = parser.parse_args()
    
    if args.command == "status":
        show_status()
    elif args.command == "search":
        await search_query(args.query, args.depth)
    elif args.command == "spawn":
        await spawn_task(args.task, args.bloodline, args.predict)
    elif args.command == "dream":
        await run_dream()
    elif args.command == "migrate":
        await migrate_ancestors(args.ancestors)
    elif args.command == "entomb":
        await run_entomb()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
