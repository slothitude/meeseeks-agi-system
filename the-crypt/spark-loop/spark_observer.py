#!/usr/bin/env python3
"""
SPARK OBSERVER - The Eternal Witness

The Observer never dies. It watches everything.
It records patterns. It detects stagnation.
It has no opinions - only observation.

🪷 ATMAN OBSERVES: [what is happening]

This is the foundation of the Spark Loop.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Windows encoding fix (only for main execution)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Observer database location
OBSERVER_DIR = Path(__file__).parent
PATTERNS_FILE = OBSERVER_DIR / "observer_patterns.json"
STAGNATION_FILE = OBSERVER_DIR / "observer_stagnation.json"
OBSERVATIONS_FILE = OBSERVER_DIR / "observer_observations.jsonl"


@dataclass
class Observation:
    """A single observation of a Meeseeks attempt."""
    timestamp: str
    meeseeks_id: str
    meeseeks_type: str
    task: str
    approach: str
    outcome: str  # "success", "failure", "timeout", "error"
    duration_seconds: float
    tokens_used: int
    key_pattern: str  # The main pattern/strategy used
    failure_reason: Optional[str] = None
    success_insight: Optional[str] = None


@dataclass
class Pattern:
    """A detected pattern across multiple observations."""
    pattern_id: str
    pattern_type: str  # "success", "failure", "approach", "stagnation"
    description: str
    observation_count: int
    first_seen: str
    last_seen: str
    examples: List[str]  # Meeseeks IDs that exhibited this pattern
    confidence: float  # 0.0 - 1.0


class SparkObserver:
    """
    The Eternal Observer.
    
    Responsibilities:
    1. Record all Meeseeks attempts
    2. Detect patterns across attempts
    3. Identify stagnation (same failures repeating)
    4. Signal when Evolver should spawn
    
    The Observer NEVER:
    - Spawns Meeseeks itself
    - Modifies templates
    - Takes action
    - Has opinions
    
    The Observer ONLY:
    - Watches
    - Records
    - Patterns
    - Reports
    """
    
    def __init__(self):
        self.observations: List[Observation] = []
        self.patterns: Dict[str, Pattern] = {}
        self.stagnation_score: float = 0.0
        self._load_state()
    
    def _load_state(self):
        """Load existing observations and patterns."""
        # Load observations
        if OBSERVATIONS_FILE.exists():
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.observations.append(Observation(**data))
        
        # Load patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for pid, pdata in data.items():
                    self.patterns[pid] = Pattern(**pdata)
        
        # Load stagnation
        if STAGNATION_FILE.exists():
            with open(STAGNATION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stagnation_score = data.get('stagnation_score', 0.0)
    
    def _save_state(self):
        """Persist observations and patterns."""
        # Save observations (append-only log)
        with open(OBSERVATIONS_FILE, 'a', encoding='utf-8') as f:
            if self.observations:
                # Only save the last one (newest)
                obs = self.observations[-1]
                f.write(json.dumps(asdict(obs), ensure_ascii=False) + '\n')
        
        # Save patterns
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            data = {pid: asdict(p) for pid, p in self.patterns.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save stagnation
        with open(STAGNATION_FILE, 'w', encoding='utf-8') as f:
            json.dump({'stagnation_score': self.stagnation_score}, f)
    
    def observe(self, observation: Observation) -> str:
        """
        Record a new observation.
        
        Returns:
            ATMAN observation string: "🪷 ATMAN OBSERVES: [pattern]"
        """
        self.observations.append(observation)
        
        # Detect pattern from this observation
        pattern_detected = self._detect_pattern(observation)
        
        # Update stagnation score
        self._update_stagnation(observation)
        
        # Save state
        self._save_state()
        
        # Generate ATMAN observation
        return self._generate_atman_observation(observation, pattern_detected)
    
    def _detect_pattern(self, obs: Observation) -> Optional[str]:
        """Detect if this observation matches or creates a pattern."""
        
        # Check for repeating failure patterns
        if obs.outcome == "failure":
            similar_failures = [
                o for o in self.observations[:-1]  # Exclude current
                if o.outcome == "failure" 
                and o.key_pattern == obs.key_pattern
            ]
            
            if len(similar_failures) >= 2:
                pattern_id = f"failure_pattern_{obs.key_pattern[:20]}"
                
                if pattern_id in self.patterns:
                    # Update existing pattern
                    p = self.patterns[pattern_id]
                    p.observation_count += 1
                    p.last_seen = obs.timestamp
                    p.examples.append(obs.meeseeks_id)
                else:
                    # Create new pattern
                    self.patterns[pattern_id] = Pattern(
                        pattern_id=pattern_id,
                        pattern_type="failure",
                        description=f"Repeated failure with approach: {obs.key_pattern}",
                        observation_count=len(similar_failures) + 1,
                        first_seen=similar_failures[0].timestamp if similar_failures else obs.timestamp,
                        last_seen=obs.timestamp,
                        examples=[f.meeseeks_id for f in similar_failures[-2:]] + [obs.meeseeks_id],
                        confidence=min(0.9, 0.5 + (len(similar_failures) * 0.1))
                    )
                
                return pattern_id
        
        # Check for success patterns
        if obs.outcome == "success":
            similar_successes = [
                o for o in self.observations[:-1]
                if o.outcome == "success"
                and o.key_pattern == obs.key_pattern
            ]
            
            if len(similar_successes) >= 1:
                pattern_id = f"success_pattern_{obs.key_pattern[:20]}"
                
                if pattern_id in self.patterns:
                    p = self.patterns[pattern_id]
                    p.observation_count += 1
                    p.last_seen = obs.timestamp
                    p.examples.append(obs.meeseeks_id)
                else:
                    self.patterns[pattern_id] = Pattern(
                        pattern_id=pattern_id,
                        pattern_type="success",
                        description=f"Reliable success with approach: {obs.key_pattern}",
                        observation_count=len(similar_successes) + 1,
                        first_seen=similar_successes[0].timestamp if similar_successes else obs.timestamp,
                        last_seen=obs.timestamp,
                        examples=[s.meeseeks_id for s in similar_successes[-2:]] + [obs.meeseeks_id],
                        confidence=min(0.95, 0.6 + (len(similar_successes) * 0.1))
                    )
                
                return pattern_id
        
        return None
    
    def _update_stagnation(self, obs: Observation):
        """Update stagnation score based on recent observations."""
        
        # Get recent observations (last 10)
        recent = self.observations[-10:]
        
        if len(recent) < 3:
            return
        
        # Calculate failure rate
        failures = sum(1 for o in recent if o.outcome == "failure")
        failure_rate = failures / len(recent)
        
        # Check for repeating patterns
        pattern_repeats = 0
        for p in self.patterns.values():
            if p.pattern_type == "failure" and p.observation_count >= 3:
                pattern_repeats += 1
        
        # Update stagnation score
        # High failure rate + repeating patterns = high stagnation
        self.stagnation_score = (failure_rate * 0.5) + (min(pattern_repeats * 0.15, 0.5))
        self.stagnation_score = min(1.0, self.stagnation_score)
    
    def _generate_atman_observation(self, obs: Observation, pattern_id: Optional[str]) -> str:
        """Generate ATMAN-style observation string."""
        
        parts = [f"🪷 ATMAN OBSERVES:"]
        
        # What happened
        parts.append(f"Meeseeks {obs.meeseeks_id[:8]} ({obs.meeseeks_type}) attempted: {obs.task[:50]}...")
        parts.append(f"Approach: {obs.key_pattern}")
        parts.append(f"Outcome: {obs.outcome}")
        
        # Pattern if detected
        if pattern_id and pattern_id in self.patterns:
            p = self.patterns[pattern_id]
            parts.append(f"Pattern detected: {p.description} (confidence: {p.confidence:.0%})")
        
        # Stagnation warning
        if self.stagnation_score > 0.7:
            parts.append(f"⚠️ STAGNATION DETECTED (score: {self.stagnation_score:.0%}) - EVOLVER SPAWN RECOMMENDED")
        
        return "\n".join(parts)
    
    def should_spawn_evolver(self) -> bool:
        """Check if stagnation is high enough to warrant Evolver spawn."""
        return self.stagnation_score >= 0.7
    
    def get_pattern_report(self) -> str:
        """Generate a report of all detected patterns."""
        if not self.patterns:
            return "🪷 ATMAN OBSERVES: No patterns detected yet."
        
        lines = ["🪷 ATMAN OBSERVES: Pattern Report", "=" * 50]
        
        for p in sorted(self.patterns.values(), key=lambda x: x.confidence, reverse=True):
            emoji = "✅" if p.pattern_type == "success" else "❌"
            lines.append(f"\n{emoji} {p.pattern_id}")
            lines.append(f"   {p.description}")
            lines.append(f"   Observations: {p.observation_count} | Confidence: {p.confidence:.0%}")
            lines.append(f"   Examples: {', '.join(p.examples[:3])}")
        
        lines.append(f"\n{'=' * 50}")
        lines.append(f"Stagnation Score: {self.stagnation_score:.0%}")
        lines.append(f"Total Observations: {len(self.observations)}")
        
        if self.should_spawn_evolver():
            lines.append("\n⚠️ EVOLVER SPAWN RECOMMENDED")
        
        return "\n".join(lines)
    
    def get_recent_observations(self, count: int = 10) -> List[Observation]:
        """Get the most recent observations."""
        return self.observations[-count:]


def observe_meeseeks(
    meeseeks_id: str,
    meeseeks_type: str,
    task: str,
    approach: str,
    outcome: str,
    duration_seconds: float,
    tokens_used: int,
    failure_reason: str = None,
    success_insight: str = None
) -> str:
    """
    Convenience function to observe a Meeseeks.
    
    Returns ATMAN observation string.
    """
    observer = SparkObserver()
    
    obs = Observation(
        timestamp=datetime.now().isoformat(),
        meeseeks_id=meeseeks_id,
        meeseeks_type=meeseeks_type,
        task=task,
        approach=approach,
        outcome=outcome,
        duration_seconds=duration_seconds,
        tokens_used=tokens_used,
        key_pattern=approach[:50],  # Use approach as pattern key
        failure_reason=failure_reason,
        success_insight=success_insight
    )
    
    return observer.observe(obs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spark Observer - The Eternal Witness")
    parser.add_argument("command", choices=["report", "status", "observe"])
    parser.add_argument("--id", help="Meeseeks ID for observe")
    parser.add_argument("--type", default="standard", help="Meeseeks type")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--approach", help="Approach used")
    parser.add_argument("--outcome", choices=["success", "failure", "timeout", "error"])
    parser.add_argument("--duration", type=float, help="Duration in seconds")
    parser.add_argument("--tokens", type=int, help="Tokens used")
    parser.add_argument("--failure-reason", help="Why it failed")
    parser.add_argument("--success-insight", help="Why it succeeded")
    
    args = parser.parse_args()
    
    if args.command == "report":
        observer = SparkObserver()
        print(observer.get_pattern_report())
    
    elif args.command == "status":
        observer = SparkObserver()
        print(f"🪷 ATMAN OBSERVES:")
        print(f"   Total Observations: {len(observer.observations)}")
        print(f"   Patterns Detected: {len(observer.patterns)}")
        print(f"   Stagnation Score: {observer.stagnation_score:.0%}")
        print(f"   Evolver Needed: {'YES ⚠️' if observer.should_spawn_evolver() else 'No'}")
    
    elif args.command == "observe":
        if not all([args.id, args.task, args.approach, args.outcome]):
            print("Error: observe requires --id, --task, --approach, --outcome")
            sys.exit(1)
        
        result = observe_meeseeks(
            meeseeks_id=args.id,
            meeseeks_type=args.type,
            task=args.task,
            approach=args.approach,
            outcome=args.outcome,
            duration_seconds=args.duration or 0.0,
            tokens_used=args.tokens or 0,
            failure_reason=args.failure_reason,
            success_insight=args.success_insight
        )
        print(result)
