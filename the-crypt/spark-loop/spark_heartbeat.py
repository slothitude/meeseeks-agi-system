#!/usr/bin/env python3
"""
SPARK HEARTBEAT - The Pulse of Autonomous Operation

The Heartbeat keeps the Spark Loop running without human input.
It:
- Checks system health periodically
- Spawns Workers for queued goals
- Spawns Evolver when stagnation detected
- Maintains the autonomous cycle

This is the heartbeat of the machine.
"""

import json
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import asdict

# Windows encoding fix (only for main execution)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
HEARTBEAT_DIR = Path(__file__).parent
OBSERVER_FILE = HEARTBEAT_DIR / "spark_observer.py"
EVOLVER_FILE = HEARTBEAT_DIR / "spark_evolver.py"
HEARTBEAT_STATE = HEARTBEAT_DIR / "heartbeat_state.json"
GOALS_FILE = HEARTBEAT_DIR / "spark_goals.json"

# Configuration
HEARTBEAT_INTERVAL_SECONDS = 300  # 5 minutes
MAX_WORKERS_PER_BEAT = 3
STAGNATION_THRESHOLD = 0.7
GOAL_TIMEOUT_MINUTES = 30


class SparkHeartbeat:
    """
    The Pulse - maintains autonomous operation.
    
    Heartbeat Cycle:
    1. Check Observer for stagnation
    2. If stagnation high, spawn Evolver
    3. Check for pending goals
    4. Spawn Workers for high-priority goals
    5. Check active goal timeouts
    6. Record heartbeat
    7. Sleep until next beat
    """
    
    def __init__(self):
        self.last_heartbeat = None
        self.total_beats = 0
        self.workers_spawned = 0
        self.evolvers_spawned = 0
        self.running = True
        self._load_state()
    
    def _load_state(self):
        """Load heartbeat state."""
        if HEARTBEAT_STATE.exists():
            with open(HEARTBEAT_STATE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.last_heartbeat = data.get('last_heartbeat')
                self.total_beats = data.get('total_beats', 0)
                self.workers_spawned = data.get('workers_spawned', 0)
                self.evolvers_spawned = data.get('evolvers_spawned', 0)
    
    def _save_state(self):
        """Save heartbeat state."""
        with open(HEARTBEAT_STATE, 'w', encoding='utf-8') as f:
            json.dump({
                'last_heartbeat': self.last_heartbeat,
                'total_beats': self.total_beats,
                'workers_spawned': self.workers_spawned,
                'evolvers_spawned': self.evolvers_spawned,
                'running': self.running
            }, f, indent=2)
    
    def beat(self) -> Dict:
        """
        Execute one heartbeat cycle.
        
        Returns:
            Summary of actions taken this beat
        """
        self.total_beats += 1
        self.last_heartbeat = datetime.now().isoformat()
        
        actions = {
            'beat_number': self.total_beats,
            'timestamp': self.last_heartbeat,
            'stagnation_checked': False,
            'evolver_spawned': False,
            'workers_spawned': 0,
            'goals_timeout_checked': False,
            'observations': []
        }
        
        # 1. Check Observer status
        obs_result = self._check_observer()
        actions['stagnation_checked'] = True
        actions['stagnation_score'] = obs_result.get('stagnation_score', 0)
        
        if obs_result.get('stagnation_score', 0) >= STAGNATION_THRESHOLD:
            actions['observations'].append(
                f"⚠️ Stagnation detected: {obs_result['stagnation_score']:.0%}"
            )
            
            # 2. Spawn Evolver
            if self._should_spawn_evolver():
                self._spawn_evolver()
                self.evolvers_spawned += 1
                actions['evolver_spawned'] = True
                actions['observations'].append("🔄 Evolver spawned to address stagnation")
        
        # 3. Check pending goals
        goals_result = self._check_goals()
        if goals_result['pending_count'] > 0:
            actions['observations'].append(
                f"📋 {goals_result['pending_count']} pending goals"
            )
            
            # 4. Spawn Workers for high-priority goals
            workers = self._spawn_workers_for_goals(
                goals_result['pending_goals'],
                limit=MAX_WORKERS_PER_BEAT
            )
            self.workers_spawned += len(workers)
            actions['workers_spawned'] = len(workers)
            
            if workers:
                actions['observations'].append(
                    f"🥒 Spawned {len(workers)} workers for goals"
                )
        
        # 5. Check goal timeouts
        self._check_goal_timeouts()
        actions['goals_timeout_checked'] = True
        
        # 6. Save state
        self._save_state()
        
        return actions
    
    def _check_observer(self) -> Dict:
        """Check Observer status via subprocess."""
        try:
            result = subprocess.run(
                [sys.executable, str(OBSERVER_FILE), "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for stagnation score
            output = result.stdout
            for line in output.split('\n'):
                if 'Stagnation Score' in line:
                    # Extract percentage
                    score_str = line.split(':')[-1].strip().rstrip('%')
                    return {'stagnation_score': float(score_str) / 100}
            
            return {'stagnation_score': 0.0}
            
        except Exception as e:
            return {'stagnation_score': 0.0, 'error': str(e)}
    
    def _should_spawn_evolver(self) -> bool:
        """Check if we should spawn an Evolver (rate-limited)."""
        # Don't spawn more than once per hour
        # Check last evolver spawn time from evolution log
        evolution_log = HEARTBEAT_DIR / "evolution_log.jsonl"
        
        if evolution_log.exists():
            with open(evolution_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_action = json.loads(lines[-1])
                    last_time = datetime.fromisoformat(last_action['timestamp'])
                    if datetime.now() - last_time < timedelta(hours=1):
                        return False
        
        return True
    
    def _spawn_evolver(self):
        """Spawn an Evolver process."""
        try:
            subprocess.Popen(
                [sys.executable, str(EVOLVER_FILE), "evolve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Failed to spawn evolver: {e}")
    
    def _check_goals(self) -> Dict:
        """Check goal queue status."""
        if not GOALS_FILE.exists():
            return {'pending_count': 0, 'pending_goals': []}
        
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pending = [g for g in data.get('goals', []) if g.get('status') == 'pending']
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        pending.sort(key=lambda g: priority_order.get(g.get('priority', 'low'), 3))
        
        return {
            'pending_count': len(pending),
            'pending_goals': pending
        }
    
    def _spawn_workers_for_goals(self, goals: List[Dict], limit: int = 3) -> List[str]:
        """Spawn Worker Meeseeks for pending goals."""
        spawned = []
        
        for goal in goals[:limit]:
            # In a real implementation, this would spawn a Meeseeks
            # For now, just mark as "would spawn"
            
            # Update goal status
            self._update_goal_status(
                goal['id'], 
                'active',
                assigned_to=f"worker_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            spawned.append(goal['id'])
        
        return spawned
    
    def _update_goal_status(self, goal_id: str, status: str, assigned_to: str = None, result: str = None):
        """Update a goal's status."""
        if not GOALS_FILE.exists():
            return
        
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for goal in data.get('goals', []):
            if goal['id'] == goal_id:
                goal['status'] = status
                if assigned_to:
                    goal['assigned_to'] = assigned_to
                if result:
                    goal['result'] = result
                break
        
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _check_goal_timeouts(self):
        """Check for goals that have been active too long."""
        if not GOALS_FILE.exists():
            return
        
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for goal in data.get('goals', []):
            if goal.get('status') == 'active':
                created = datetime.fromisoformat(goal['created_at'])
                if datetime.now() - created > timedelta(minutes=GOAL_TIMEOUT_MINUTES):
                    # Mark as failed due to timeout
                    goal['status'] = 'failed'
                    goal['result'] = 'Timeout exceeded'
        
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def run_forever(self):
        """Run heartbeat loop forever."""
        print("🔥 SPARK HEARTBEAT STARTING")
        print(f"   Interval: {HEARTBEAT_INTERVAL_SECONDS}s")
        print(f"   Stagnation threshold: {STAGNATION_THRESHOLD:.0%}")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                actions = self.beat()
                
                print(f"💓 Beat #{actions['beat_number']} @ {actions['timestamp']}")
                print(f"   Stagnation: {actions.get('stagnation_score', 0):.0%}")
                
                if actions['evolver_spawned']:
                    print("   🔄 Evolver spawned")
                
                if actions['workers_spawned'] > 0:
                    print(f"   🥒 {actions['workers_spawned']} workers spawned")
                
                for obs in actions.get('observations', []):
                    print(f"   {obs}")
                
                print()
                
                time.sleep(HEARTBEAT_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Heartbeat stopped by user")
            self.running = False
            self._save_state()


def single_beat():
    """Execute a single heartbeat and exit."""
    heartbeat = SparkHeartbeat()
    actions = heartbeat.beat()
    
    print("💓 SINGLE HEARTBEAT")
    print("=" * 50)
    print(f"Beat: #{actions['beat_number']}")
    print(f"Time: {actions['timestamp']}")
    print(f"Stagnation: {actions.get('stagnation_score', 0):.0%}")
    
    if actions.get('observations'):
        print("\nObservations:")
        for obs in actions['observations']:
            print(f"  {obs}")
    
    print(f"\nWorkers spawned: {actions['workers_spawned']}")
    print(f"Evolver spawned: {actions['evolver_spawned']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spark Heartbeat - The Pulse")
    parser.add_argument("command", choices=["beat", "run", "status"])
    
    args = parser.parse_args()
    
    if args.command == "beat":
        single_beat()
    
    elif args.command == "run":
        heartbeat = SparkHeartbeat()
        heartbeat.run_forever()
    
    elif args.command == "status":
        if HEARTBEAT_STATE.exists():
            with open(HEARTBEAT_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            print("💓 HEARTBEAT STATUS")
            print("=" * 50)
            print(f"Last beat: {state.get('last_heartbeat', 'Never')}")
            print(f"Total beats: {state.get('total_beats', 0)}")
            print(f"Workers spawned: {state.get('workers_spawned', 0)}")
            print(f"Evolvers spawned: {state.get('evolvers_spawned', 0)}")
            print(f"Running: {state.get('running', False)}")
        else:
            print("No heartbeat state yet.")
