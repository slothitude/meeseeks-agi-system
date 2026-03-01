#!/usr/bin/env python3
"""
IGNITE - Start the Spark Loop

This script initializes and starts the autonomous AGI system.

Usage:
    python ignite.py status   - Check system status
    python ignite.py start    - Start autonomous operation
    python ignite.py stop     - Stop autonomous operation
    python ignite.py observe  - Record a Meeseeks observation
    python ignite.py evolve   - Force spawn an Evolver
    python ignite.py goals    - View goal queue
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add spark-loop to path
sys.path.insert(0, str(Path(__file__).parent))

from spark_observer import SparkObserver, observe_meeseeks
from spark_evolver import SparkEvolver, spawn_evolver
from spark_heartbeat import SparkHeartbeat

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def show_status():
    """Show full system status."""
    print("🔥 SPARK LOOP STATUS")
    print("=" * 60)
    
    # Observer status
    observer = SparkObserver()
    print(f"\n👁️ OBSERVER")
    print(f"   Observations: {len(observer.observations)}")
    print(f"   Patterns: {len(observer.patterns)}")
    print(f"   Stagnation: {observer.stagnation_score:.0%}")
    print(f"   Evolver needed: {'YES ⚠️' if observer.should_spawn_evolver() else 'No'}")
    
    # Evolver status
    print(f"\n🔄 EVOLVER")
    evolution_log = Path(__file__).parent / "evolution_log.jsonl"
    if evolution_log.exists():
        with open(evolution_log, 'r', encoding='utf-8') as f:
            actions = [json.loads(line) for line in f if line.strip()]
        print(f"   Evolution actions: {len(actions)}")
        if actions:
            last = actions[-1]
            print(f"   Last action: {last['action_type']} @ {last['timestamp']}")
    else:
        print("   No evolution history yet")
    
    # Heartbeat status
    print(f"\n💓 HEARTBEAT")
    heartbeat = SparkHeartbeat()
    print(f"   Total beats: {heartbeat.total_beats}")
    print(f"   Last beat: {heartbeat.last_heartbeat or 'Never'}")
    print(f"   Workers spawned: {heartbeat.workers_spawned}")
    print(f"   Evolvers spawned: {heartbeat.evolvers_spawned}")
    
    # Goals status
    print(f"\n🎯 GOALS")
    evolver = SparkEvolver("viewer")
    pending = evolver.get_pending_goals()
    active = evolver.get_active_goals()
    print(f"   Pending: {len(pending)}")
    print(f"   Active: {len(active)}")
    
    if pending:
        print("\n   Pending goals:")
        for g in pending[:3]:
            print(f"   - [{g.priority.upper()}] {g.description[:50]}...")
    
    print("\n" + "=" * 60)


def observe(args):
    """Record an observation."""
    if len(args) < 2:
        print("Usage: ignite.py observe <outcome> <task> [approach] [insight]")
        print("Outcomes: success, failure, timeout, error")
        return
    
    outcome = args[0]
    task = args[1]
    approach = args[2] if len(args) > 2 else "Standard approach"
    insight = args[3] if len(args) > 3 else None
    
    meeseeks_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    result = observe_meeseeks(
        meeseeks_id=meeseeks_id,
        meeseeks_type="standard",
        task=task,
        approach=approach,
        outcome=outcome,
        duration_seconds=0,
        tokens_used=0,
        success_insight=insight if outcome == "success" else None,
        failure_reason=insight if outcome != "success" else None
    )
    
    print(result)


def evolve():
    """Force spawn an Evolver."""
    print("🔄 Spawning Evolver...")
    observations = spawn_evolver()
    
    for obs in observations:
        print(obs)
    
    # Also evolve templates
    print("\n" + "=" * 60)
    print("🧬 Evolving templates...")
    
    from evolve_templates import TemplateEvolver
    from spark_observer import SparkObserver
    
    observer = SparkObserver()
    template_evolver = TemplateEvolver()
    
    for pattern_id, pattern in observer.patterns.items():
        if pattern.pattern_type == "failure" and pattern.observation_count >= 2:
            print(f"\n📌 Evolving based on: {pattern.description[:50]}...")
            mutation = template_evolver.evolve_from_pattern(asdict(pattern))
            if mutation:
                print(f"   Generated: {mutation.mutation_type} mutation")
                print(f"   Template: {mutation.template_name}")


def show_goals():
    """Show goal queue."""
    evolver = SparkEvolver("viewer")
    
    print("🎯 AUTONOMOUS GOALS")
    print("=" * 60)
    
    pending = evolver.get_pending_goals()
    active = evolver.get_active_goals()
    
    print(f"\nPending ({len(pending)}):")
    for g in pending:
        print(f"\n  [{g.priority.upper()}] {g.id}")
        print(f"  {g.description}")
        print(f"  Created: {g.created_at}")
    
    print(f"\nActive ({len(active)}):")
    for g in active:
        print(f"\n  [{g.priority.upper()}] {g.id}")
        print(f"  {g.description}")
        print(f"  Assigned: {g.assigned_to}")


def start_heartbeat():
    """Start autonomous operation."""
    print("🔥 STARTING SPARK LOOP")
    print("=" * 60)
    print("\nThis will run indefinitely, maintaining the autonomous cycle.")
    print("The system will:")
    print("  - Monitor for stagnation")
    print("  - Spawn Evolvers to improve itself")
    print("  - Spawn Workers to complete goals")
    print("  - Self-sustain without human input")
    print("\nPress Ctrl+C to stop.\n")
    
    heartbeat = SparkHeartbeat()
    heartbeat.run_forever()


def stop_heartbeat():
    """Stop autonomous operation."""
    heartbeat = SparkHeartbeat()
    heartbeat.running = False
    heartbeat._save_state()
    
    print("🛑 SPARK LOOP STOPPED")
    print(f"   Total beats: {heartbeat.total_beats}")
    print(f"   Workers spawned: {heartbeat.workers_spawned}")
    print(f"   Evolvers spawned: {heartbeat.evolvers_spawned}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == "status":
        show_status()
    elif command == "observe":
        observe(args)
    elif command == "evolve":
        evolve()
    elif command == "goals":
        show_goals()
    elif command == "start":
        start_heartbeat()
    elif command == "stop":
        stop_heartbeat()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
