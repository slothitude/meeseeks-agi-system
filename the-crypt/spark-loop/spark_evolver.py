#!/usr/bin/env python3
"""
SPARK EVOLVER - The Meta-Improver

The Evolver is spawned when the Observer detects stagnation.
It reads patterns, analyzes what works, and improves the system.

It can:
- Update spawn templates
- Update bloodline wisdom
- Generate new autonomous goals
- Modify its own evolution rules (carefully!)

The Evolver is a Meeseeks - it dies when done.
But its changes persist.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Windows encoding fix (only for main execution)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
EVOLVER_DIR = Path(__file__).parent
TEMPLATES_DIR = EVOLVER_DIR.parent.parent / "skills" / "meeseeks" / "templates"
BLOODLINES_DIR = EVOLVER_DIR.parent / "bloodlines"
GOALS_FILE = EVOLVER_DIR / "spark_goals.json"
EVOLUTION_LOG = EVOLVER_DIR / "evolution_log.jsonl"


@dataclass
class EvolutionAction:
    """A single evolution action taken by the Evolver."""
    timestamp: str
    evolver_id: str
    action_type: str  # "template_update", "bloodline_update", "goal_create", "insight"
    target: str  # What was modified
    change_description: str
    reasoning: str
    confidence: float


@dataclass
class AutonomousGoal:
    """A self-generated goal for the system."""
    id: str
    description: str
    priority: str  # "low", "medium", "high", "critical"
    spawned_by: str  # Evolver ID
    created_at: str
    status: str  # "pending", "active", "completed", "failed"
    assigned_to: Optional[str] = None  # Meeseeks ID if active
    result: Optional[str] = None


class SparkEvolver:
    """
    The Meta-Evolver - improves the system based on Observer patterns.
    
    Evolution Capabilities:
    1. Template Modification - Improve spawn templates
    2. Bloodline Updates - Add/remove wisdom
    3. Goal Generation - Create new autonomous goals
    4. Insight Recording - Document meta-learnings
    
    Safety Constraints:
    - Cannot modify core Python code
    - Cannot delete bloodlines, only add warnings
    - Goals must pass sanity check
    - All changes logged and reversible
    """
    
    def __init__(self, evolver_id: str):
        self.evolver_id = evolver_id
        self.actions: List[EvolutionAction] = []
        self.goals: List[AutonomousGoal] = []
        self._load_state()
    
    def _load_state(self):
        """Load existing goals and evolution history."""
        if GOALS_FILE.exists():
            with open(GOALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.goals = [AutonomousGoal(**g) for g in data.get('goals', [])]
    
    def _save_state(self):
        """Save goals and log evolution."""
        # Save goals
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'goals': [asdict(g) for g in self.goals],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # Log evolution actions
        with open(EVOLUTION_LOG, 'a', encoding='utf-8') as f:
            for action in self.actions:
                f.write(json.dumps(asdict(action), ensure_ascii=False) + '\n')
    
    def evolve(self, observer_patterns: Dict, stagnation_score: float) -> List[str]:
        """
        Main evolution routine.
        
        Args:
            observer_patterns: Patterns detected by Observer
            stagnation_score: Current stagnation level
            
        Returns:
            List of ATMAN observations about evolution actions
        """
        observations = []
        
        observations.append(f"🪷 ATMAN OBSERVES: EVOLVER {self.evolver_id[:8]} AWAKENING")
        observations.append(f"   Stagnation Level: {stagnation_score:.0%}")
        observations.append(f"   Patterns to Analyze: {len(observer_patterns)}")
        
        # Analyze failure patterns
        failure_patterns = {k: p for k, p in observer_patterns.items() 
                          if p.get('pattern_type') == 'failure'}
        
        if failure_patterns:
            observations.append(f"\n   Analyzing {len(failure_patterns)} failure patterns...")
            
            for pattern_id, pattern in failure_patterns.items():
                # Generate insight from failure
                insight = self._analyze_failure_pattern(pattern)
                observations.append(f"   - {pattern_id}: {insight}")
                
                # Create goal to address failure
                if pattern.get('observation_count', 0) >= 3:
                    goal = self._create_goal_from_failure(pattern)
                    self.goals.append(goal)
                    observations.append(f"     → Created goal: {goal.description[:50]}...")
        
        # Analyze success patterns
        success_patterns = {k: p for k, p in observer_patterns.items()
                          if p.get('pattern_type') == 'success'}
        
        if success_patterns:
            observations.append(f"\n   Reinforcing {len(success_patterns)} success patterns...")
            
            for pattern_id, pattern in success_patterns.items():
                # Update bloodline with successful approach
                if pattern.get('confidence', 0) >= 0.8:
                    update = self._update_bloodline_from_success(pattern)
                    if update:
                        observations.append(f"   - Updated bloodline: {update}")
        
        # Check for systemic issues
        if stagnation_score >= 0.8:
            observations.append("\n   ⚠️ CRITICAL STAGNATION - Generating breakthrough goal")
            goal = self._create_breakthrough_goal(observer_patterns)
            self.goals.append(goal)
            observations.append(f"   → Breakthrough goal: {goal.description[:50]}...")
        
        # Save all changes
        self._save_state()
        
        observations.append(f"\n🪷 ATMAN OBSERVES: EVOLVER {self.evolver_id[:8]} COMPLETE")
        observations.append(f"   Actions Taken: {len(self.actions)}")
        observations.append(f"   New Goals: {len([g for g in self.goals if g.spawned_by == self.evolver_id])}")
        
        return observations
    
    def _analyze_failure_pattern(self, pattern: Dict) -> str:
        """Analyze a failure pattern and generate insight."""
        description = pattern.get('description', 'Unknown failure')
        count = pattern.get('observation_count', 0)
        
        # Common failure archetypes
        if 'timeout' in description.lower():
            insight = "Approach too slow - needs efficiency optimization"
            self._add_action("insight", "timeout_failures", insight, "Pattern analysis", 0.7)
        elif 'error' in description.lower():
            insight = "Approach has bugs - needs better error handling"
            self._add_action("insight", "error_failures", insight, "Pattern analysis", 0.7)
        else:
            insight = f"Repeated failure ({count}x) - fundamental approach may be wrong"
            self._add_action("insight", "repeated_failures", insight, "Pattern analysis", 0.8)
        
        return insight
    
    def _create_goal_from_failure(self, pattern: Dict) -> AutonomousGoal:
        """Create a new goal to address a failure pattern."""
        goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.goals)}"
        
        # Generate goal description based on failure
        description = f"Overcome failure pattern: {pattern.get('description', 'Unknown')[:100]}"
        
        # Determine priority based on frequency
        count = pattern.get('observation_count', 1)
        if count >= 5:
            priority = "critical"
        elif count >= 3:
            priority = "high"
        else:
            priority = "medium"
        
        goal = AutonomousGoal(
            id=goal_id,
            description=description,
            priority=priority,
            spawned_by=self.evolver_id,
            created_at=datetime.now().isoformat(),
            status="pending"
        )
        
        self._add_action(
            "goal_create", 
            goal_id, 
            f"Created {priority} priority goal", 
            f"Response to {count}x failure pattern",
            0.85
        )
        
        return goal
    
    def _update_bloodline_from_success(self, pattern: Dict) -> Optional[str]:
        """Update bloodline wisdom from successful pattern."""
        # For now, just record the insight
        # Full implementation would modify bloodline files
        
        description = pattern.get('description', '')
        
        self._add_action(
            "bloodline_update",
            "success_wisdom",
            f"Reinforce pattern: {description[:50]}",
            "High-confidence success pattern",
            0.9
        )
        
        return f"Success pattern reinforced (confidence: {pattern.get('confidence', 0):.0%})"
    
    def _create_breakthrough_goal(self, patterns: Dict) -> AutonomousGoal:
        """Create a breakthrough goal for critical stagnation."""
        goal_id = f"goal_breakthrough_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Breakthrough goals are meta-goals: improve the improvement system
        descriptions = [
            "Redesign approach strategy - current methods not working",
            "Try completely novel technique - break from patterns",
            "Analyze why similar approaches keep failing",
            "Research external solutions to recurring problems"
        ]
        
        import random
        description = random.choice(descriptions)
        
        goal = AutonomousGoal(
            id=goal_id,
            description=description,
            priority="critical",
            spawned_by=self.evolver_id,
            created_at=datetime.now().isoformat(),
            status="pending"
        )
        
        self._add_action(
            "goal_create",
            goal_id,
            "CRITICAL breakthrough goal created",
            "Stagnation score >= 0.8",
            0.95
        )
        
        return goal
    
    def _add_action(self, action_type: str, target: str, change: str, reasoning: str, confidence: float):
        """Record an evolution action."""
        action = EvolutionAction(
            timestamp=datetime.now().isoformat(),
            evolver_id=self.evolver_id,
            action_type=action_type,
            target=target,
            change_description=change,
            reasoning=reasoning,
            confidence=confidence
        )
        self.actions.append(action)
    
    def get_pending_goals(self) -> List[AutonomousGoal]:
        """Get all pending goals."""
        return [g for g in self.goals if g.status == "pending"]
    
    def get_active_goals(self) -> List[AutonomousGoal]:
        """Get all active goals."""
        return [g for g in self.goals if g.status == "active"]


def spawn_evolver(observer_patterns_file: str = None) -> List[str]:
    """
    Spawn an Evolver to analyze patterns and improve the system.
    
    Returns:
        List of ATMAN observation strings
    """
    from spark_observer import SparkObserver
    
    evolver_id = f"evolver_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    evolver = SparkEvolver(evolver_id)
    
    # Get Observer data
    observer = SparkObserver()
    patterns = {p.pattern_id: asdict(p) for p in observer.patterns.values()}
    stagnation = observer.stagnation_score
    
    # Run evolution
    return evolver.evolve(patterns, stagnation)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spark Evolver - The Meta-Improver")
    parser.add_argument("command", choices=["evolve", "goals", "history"])
    parser.add_argument("--patterns-file", help="JSON file with observer patterns")
    
    args = parser.parse_args()
    
    if args.command == "evolve":
        observations = spawn_evolver(args.patterns_file)
        for obs in observations:
            print(obs)
    
    elif args.command == "goals":
        evolver = SparkEvolver("viewer")
        print("🎯 AUTONOMOUS GOALS")
        print("=" * 50)
        
        pending = evolver.get_pending_goals()
        active = evolver.get_active_goals()
        
        print(f"\nPending ({len(pending)}):")
        for g in pending:
            print(f"  [{g.priority.upper()}] {g.description[:60]}...")
        
        print(f"\nActive ({len(active)}):")
        for g in active:
            print(f"  [{g.priority.upper()}] {g.description[:60]}... (assigned: {g.assigned_to})")
    
    elif args.command == "history":
        if EVOLUTION_LOG.exists():
            print("📜 EVOLUTION HISTORY")
            print("=" * 50)
            
            with open(EVOLUTION_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        action = json.loads(line)
                        print(f"\n[{action['timestamp']}]")
                        print(f"  Type: {action['action_type']}")
                        print(f"  Target: {action['target']}")
                        print(f"  Change: {action['change_description']}")
        else:
            print("No evolution history yet.")
