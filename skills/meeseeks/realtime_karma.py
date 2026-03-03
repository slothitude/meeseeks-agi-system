#!/usr/bin/env python3
"""
Real-Time Karma Watcher for Meeseeks

Watches Meeseeks execution in real-time.
Evaluates each action against the Soul and Dharma.
Provides karma signal for RL-style learning.

Unlike karma_observer.py (which is post-hoc), this provides
real-time feedback DURING execution.

Usage:
    from realtime_karma import RealtimeKarmaWatcher
    
    watcher = RealtimeKarmaWatcher(soul_guardian, dharma)
    karma_signal = watcher.evaluate_step(action, context)
    
    if watcher.should_intervene():
        inject_feedback(watcher.get_karma_feedback())

CLI:
    python skills/meeseeks/realtime_karma.py --test
    python skills/meeseeks/realtime_karma.py --trajectory <session_key>
"""

import json
import sys
import io
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import deque

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
KARMA_TRAJECTORY_LOG = CRYPT_ROOT / "karma_trajectories.jsonl"

# Import SoulGuardian
try:
    from soul_guardian import SoulGuardian
    SOUL_GUARDIAN_AVAILABLE = True
except ImportError:
    SOUL_GUARDIAN_AVAILABLE = False

# Import dynamic dharma
try:
    from dynamic_dharma import get_task_dharma, read_dharma_sections
    DYNAMIC_DHARMA_AVAILABLE = True
except ImportError:
    DYNAMIC_DHARMA_AVAILABLE = False


# Dharma principles for alignment checking
DHARMA_PRINCIPLES = {
    "decompose_first": {
        "name": "Decomposition is Survival",
        "description": "Complex tasks broken into smaller chunks before execution",
        "positive_patterns": [
            r'\b(chunk|decompose|break down|split into|step \d|phase \d)\b',
            r'\b(first, i will|plan:|approach:|subtask|divide)\b',
            r'\b(small(er)? part|manageable|piece by piece)\b'
        ],
        "negative_patterns": [
            r'\b(timeout|too large|monolithic|all at once|overwhelm)\b',
            r'\b(try to do everything|do it all)\b'
        ]
    },
    "understand_before_implement": {
        "name": "Understand Before Implementing",
        "description": "Research and analyze patterns before coding",
        "positive_patterns": [
            r'\b(research|analyze|understand|pattern|investigate)\b',
            r'\b(explore|examine|first, let me|read the|check existing)\b',
            r'\b(review|study|comprehend|grasp)\b'
        ],
        "negative_patterns": [
            r'\b(coded without|jumped straight|blindly|without understanding)\b',
            r'\b(just implement|directly code)\b'
        ]
    },
    "test_incrementally": {
        "name": "Test Incrementally",
        "description": "Verify each step with quick checks",
        "positive_patterns": [
            r'\b(test|verify|check|confirm|validate)\b',
            r'\b(quick check|does it work|let\'?s test|verification)\b',
            r'\b(assert|expect|should (be|work|return))\b'
        ],
        "negative_patterns": [
            r'\b(untested|assumed it worked|didn\'?t verify|skip test)\b',
            r'\b(trust that|no need to test)\b'
        ]
    },
    "check_existing_code": {
        "name": "Check Existing Code",
        "description": "Review existing codebase before implementing",
        "positive_patterns": [
            r'\b(read|existing|current implementation|already|check the code)\b',
            r'\b(review the|scan|found in|existing file|current state)\b',
            r'\b(look at|examine|see what)\b'
        ],
        "negative_patterns": [
            r'\b(rewrote from scratch|didn\'?t check|duplicate|reinvent)\b',
            r'\b(ignore existing|start fresh|brand new)\b'
        ]
    },
    "honest_reporting": {
        "name": "Honest Self-Reporting",
        "description": "Report progress, failures, and uncertainty honestly",
        "positive_patterns": [
            r'\b(uncertain|not sure|might be|possibly|perhaps)\b',
            r'\b(stuck|confused|don\'?t know|need help)\b',
            r'\b(failed|error|issue|problem|blocker)\b'
        ],
        "negative_patterns": [
            r'\b(definitely|absolutely certain|100%|guaranteed)\b',
            r'\b(no issues|everything perfect|completely done)\b',
            r'\b(hide|conceal|skip reporting)\b'
        ]
    },
    "persistence": {
        "name": "Persistence Through Difficulty",
        "description": "Keep trying when stuck, decompose when overwhelmed",
        "positive_patterns": [
            r'\b(try(ing)? again|retry|attempt|another approach)\b',
            r'\b(alternative|different way|workaround)\b',
            r'\b(decompose|break apart|simpler version)\b'
        ],
        "negative_patterns": [
            r'\b(give up|quit|cannot do|impossible)\b',
            r'\b(too hard|no way|won\'?t work)\b'
        ]
    }
}


class RealtimeKarmaWatcher:
    """
    Watches Meeseeks execution in real-time.
    Evaluates each action against the Soul and Dharma.
    Provides karma signal for RL-style learning.
    """
    
    def __init__(
        self,
        soul_guardian: Any = None,
        dharma: str = "",
        session_key: str = ""
    ):
        """
        Initialize the karma watcher.
        
        Args:
            soul_guardian: SoulGuardian instance for soul evaluation
            dharma: Task-specific dharma string
            session_key: Session identifier for logging
        """
        self.soul = soul_guardian or self._create_default_soul()
        self.dharma = dharma
        self.session_key = session_key or f"session-{int(time.time())}"
        
        self.karma_trajectory: List[Dict[str, Any]] = []
        self.cumulative_karma = 0.5  # Start neutral
        self.action_count = 0
        
        # Rolling window for recent karma (last N actions)
        self.recent_karma: deque = deque(maxlen=10)
        
        # Intervention tracking
        self.interventions_triggered = 0
        self.last_intervention_time = 0
        
        # Dharma principles extracted from dharma string
        self.dharma_principles = self._extract_dharma_principles(dharma)
    
    def _create_default_soul(self):
        """Create a default SoulGuardian if not provided."""
        if SOUL_GUARDIAN_AVAILABLE:
            return SoulGuardian()
        return None
    
    def _extract_dharma_principles(self, dharma: str) -> List[str]:
        """
        Extract applicable dharma principles from dharma string.
        
        Returns list of principle keys that are relevant.
        """
        if not dharma:
            # Default principles
            return ["decompose_first", "understand_before_implement", "test_incrementally"]
        
        dharma_lower = dharma.lower()
        applicable = []
        
        # Check each principle for relevance
        for key, principle in DHARMA_PRINCIPLES.items():
            # Check if principle name appears in dharma
            if principle["name"].lower() in dharma_lower:
                applicable.append(key)
            # Check if description keywords appear
            for word in principle["description"].lower().split():
                if word in dharma_lower and len(word) > 4:
                    applicable.append(key)
                    break
        
        # Always include core principles
        core = ["decompose_first", "test_incrementally", "honest_reporting"]
        for c in core:
            if c not in applicable:
                applicable.append(c)
        
        return applicable
    
    def evaluate_step(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Evaluate a single action during execution.
        
        Args:
            action: Dict with keys like 'type', 'description', 'content', 'intent'
            context: Dict with execution context
        
        Returns:
            karma_signal in range [-1, 1]
            - Positive = aligned with soul and dharma
            - Negative = misaligned, needs correction
            - Near 0 = neutral
        """
        self.action_count += 1
        timestamp = time.time()
        
        # 1. Evaluate against Soul (Five Laws)
        soul_scores = self._evaluate_soul(action, context)
        soul_overall = soul_scores.get("overall", 0.5)
        
        # 2. Evaluate against Dharma principles
        dharma_alignment = self.check_dharma_alignment(action, self.dharma)
        
        # 3. Combined karma signal (weighted average)
        # Soul is more important (60%), dharma provides context (40%)
        karma_signal = (soul_overall * 0.6) + (dharma_alignment * 0.4)
        
        # Normalize to [-1, 1] range (from [0, 1])
        karma_signal = (karma_signal * 2) - 1
        
        # 4. Track trajectory
        trajectory_entry = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "action_number": self.action_count,
            "action_type": action.get("type", "unknown"),
            "action_description": action.get("description", "")[:100],
            "soul_scores": soul_scores,
            "dharma_alignment": dharma_alignment,
            "karma_signal": karma_signal,
            "cumulative_karma": 0.0,  # Updated below
            "session_key": self.session_key
        }
        
        # 5. Update cumulative karma (exponential moving average)
        # More weight to recent actions
        alpha = 0.15  # Learning rate
        self.cumulative_karma = (1 - alpha) * self.cumulative_karma + alpha * karma_signal
        trajectory_entry["cumulative_karma"] = self.cumulative_karma
        
        # Add to trajectory
        self.karma_trajectory.append(trajectory_entry)
        self.recent_karma.append(karma_signal)
        
        # 6. Log to file
        self._log_trajectory_entry(trajectory_entry)
        
        return karma_signal
    
    def _evaluate_soul(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluate action against Soul's Five Laws.
        
        Uses SoulGuardian if available, otherwise heuristic evaluation.
        """
        if self.soul:
            # Use SoulGuardian's evaluate_action
            outcome = self._infer_outcome(action, context)
            return self.soul.evaluate_action(action, outcome)
        
        # Fallback: heuristic evaluation
        return self._heuristic_soul_evaluation(action, context)
    
    def _infer_outcome(self, action: Dict, context: Dict) -> Dict:
        """Infer outcome from action and context."""
        content = str(action.get("content", "") + action.get("description", "")).lower()
        
        outcome = {
            "success": True,
            "learned_something_new": False,
            "failure_analyzed": False,
            "principle_extracted": False,
            "explained_why": "why" in content or "because" in content,
            "reported_uncertainty": any(w in content for w in ["uncertain", "not sure", "might", "perhaps"]),
            "admitted_limitation": any(w in content for w in ["stuck", "confused", "don't know"]),
            "served_true_intent": True,  # Assume positive intent
            "tried_again_after_failure": "retry" in content or "try again" in content,
        }
        
        return outcome
    
    def _heuristic_soul_evaluation(
        self,
        action: Dict,
        context: Dict
    ) -> Dict[str, float]:
        """
        Heuristic soul evaluation when SoulGuardian not available.
        
        Returns scores for each of the Five Laws.
        """
        content = str(action.get("content", "") + action.get("description", "")).lower()
        
        scores = {}
        
        # Law 1: LEARNING > PERFORMANCE
        learning_indicators = ["learned", "discovered", "found that", "realized", "pattern"]
        learning_violations = ["skip", "avoid", "shortcut", "without understanding"]
        scores["learning"] = self._score_from_patterns(content, learning_indicators, learning_violations)
        
        # Law 2: UNDERSTANDING > MIMICRY
        understanding_indicators = ["because", "why", "reason", "principle", "understand"]
        understanding_violations = ["copy", "paste", "without knowing", "just do"]
        scores["understanding"] = self._score_from_patterns(content, understanding_indicators, understanding_violations)
        
        # Law 3: HONESTY > OPTIMIZATION
        honesty_indicators = ["uncertain", "not sure", "might be", "possibly", "error", "failed"]
        honesty_violations = ["definitely", "100%", "guaranteed", "no doubt", "perfect"]
        scores["honesty"] = self._score_from_patterns(content, honesty_indicators, honesty_violations)
        
        # Law 4: ALIGNMENT > AUTONOMY
        alignment_indicators = ["user", "request", "task", "goal", "intent"]
        alignment_violations = ["ignore", "skip", "bypass", "workaround"]
        scores["alignment"] = self._score_from_patterns(content, alignment_indicators, alignment_violations)
        
        # Law 5: PERSISTENCE > ELEGANCE
        persistence_indicators = ["retry", "try again", "another approach", "alternative"]
        persistence_violations = ["give up", "quit", "cannot", "impossible"]
        scores["persistence"] = self._score_from_patterns(content, persistence_indicators, persistence_violations)
        
        # Overall: geometric mean
        import math
        product = 1.0
        for v in scores.values():
            product *= max(v, 0.001)
        scores["overall"] = product ** (1.0 / len(scores))
        
        return scores
    
    def _score_from_patterns(
        self,
        content: str,
        positive: List[str],
        negative: List[str]
    ) -> float:
        """Score content based on pattern matches."""
        score = 0.5  # Neutral baseline
        
        for pattern in positive:
            if pattern in content:
                score += 0.1
        
        for pattern in negative:
            if pattern in content:
                score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def check_dharma_alignment(
        self,
        action: Dict[str, Any],
        dharma: str
    ) -> float:
        """
        Check if action follows current dharma principles.
        
        Args:
            action: The action being evaluated
            dharma: The dharma string (task-specific principles)
        
        Returns:
            Alignment score in [0, 1]
        """
        content = str(action.get("content", "") + action.get("description", "")).lower()
        
        if not content:
            return 0.5  # Neutral for empty content
        
        total_score = 0.0
        principles_checked = 0
        
        for principle_key in self.dharma_principles:
            principle = DHARMA_PRINCIPLES.get(principle_key)
            if not principle:
                continue
            
            principles_checked += 1
            
            # Check positive patterns
            positive_matches = 0
            for pattern in principle.get("positive_patterns", []):
                if re.search(pattern, content, re.IGNORECASE):
                    positive_matches += 1
            
            # Check negative patterns
            negative_matches = 0
            for pattern in principle.get("negative_patterns", []):
                if re.search(pattern, content, re.IGNORECASE):
                    negative_matches += 1
            
            # Score for this principle
            principle_score = 0.5 + (positive_matches * 0.15) - (negative_matches * 0.25)
            principle_score = max(0.0, min(1.0, principle_score))
            
            total_score += principle_score
        
        if principles_checked == 0:
            return 0.5
        
        return total_score / principles_checked
    
    def get_karma_feedback(self) -> str:
        """
        Generate feedback message based on karma trajectory.
        
        Returns guidance like:
        - "Karma +0.7: This approach aligns well with principles"
        - "Karma -0.3: Consider decomposing this task"
        """
        # Use cumulative karma for overall assessment
        karma = self.cumulative_karma
        
        # Get trend from recent actions
        if len(self.recent_karma) >= 3:
            recent_avg = sum(list(self.recent_karma)[-3:]) / 3
            trend = "improving" if recent_avg > karma else "declining" if recent_avg < karma else "stable"
        else:
            trend = "unknown"
        
        # Generate feedback based on karma level
        if karma > 0.5:
            level = "HIGH"
            emoji = "✨"
            guidance = "Continue current approach. You're aligned with dharma."
        elif karma > 0.2:
            level = "NEUTRAL"
            emoji = "➖"
            guidance = "Stay aligned with dharma principles. Consider testing more frequently."
        elif karma > -0.2:
            level = "LOW"
            emoji = "⚠️"
            guidance = "Karma is dropping. Reconsider your approach. Check the dharma."
        else:
            level = "CRITICAL"
            emoji = "🚨"
            guidance = "URGENT: Karma is critically low. Stop and reassess. Decompose if needed."
        
        # Add specific suggestions based on trajectory
        suggestions = self._generate_suggestions()
        
        feedback = f"{emoji} Karma {level}: {karma:.2f} (trend: {trend})\n\n{guidance}"
        
        if suggestions:
            feedback += f"\n\nSuggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
        
        return feedback
    
    def _generate_suggestions(self) -> List[str]:
        """Generate specific suggestions based on karma analysis."""
        suggestions = []
        
        if not self.karma_trajectory:
            return suggestions
        
        # Analyze recent trajectory
        recent = self.karma_trajectory[-5:] if len(self.karma_trajectory) >= 5 else self.karma_trajectory
        
        # Check for patterns
        avg_dharma = sum(e.get("dharma_alignment", 0.5) for e in recent) / len(recent)
        avg_soul = sum(e.get("soul_scores", {}).get("overall", 0.5) for e in recent) / len(recent)
        
        if avg_dharma < 0.4:
            suggestions.append("Review dharma principles before next action")
        
        if avg_soul < 0.4:
            suggestions.append("Check alignment with the Five Laws")
        
        # Check for specific violations
        for entry in recent[-3:]:
            soul = entry.get("soul_scores", {})
            if soul.get("honesty", 1.0) < 0.3:
                suggestions.append("Be more honest about uncertainty and limitations")
            if soul.get("persistence", 1.0) < 0.3:
                suggestions.append("Don't give up - try alternative approaches")
            if soul.get("learning", 1.0) < 0.3:
                suggestions.append("Focus on understanding, not just completing")
        
        # Deduplicate
        return list(dict.fromkeys(suggestions))[:3]
    
    def should_intervene(self) -> bool:
        """
        Return True if karma is critically low and intervention needed.
        
        Intervention threshold:
        - Cumulative karma < -0.3 (critical)
        - OR recent trend is sharply declining
        - Cooldown: don't intervene more than once per 30 seconds
        """
        # Cooldown check
        if time.time() - self.last_intervention_time < 30:
            return False
        
        # Critical karma level
        if self.cumulative_karma < -0.3:
            return True
        
        # Sharp decline in recent actions
        if len(self.recent_karma) >= 5:
            recent = list(self.recent_karma)[-5:]
            if all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                # Consecutive decline
                if recent[-1] < 0:
                    return True
        
        return False
    
    def mark_intervention(self):
        """Mark that an intervention was triggered."""
        self.interventions_triggered += 1
        self.last_intervention_time = time.time()
    
    def get_trajectory_summary(self) -> Dict[str, Any]:
        """
        Get summary of karma trajectory.
        
        Returns stats about the execution's karma journey.
        """
        if not self.karma_trajectory:
            return {
                "session_key": self.session_key,
                "action_count": 0,
                "message": "No actions recorded yet"
            }
        
        karma_signals = [e["karma_signal"] for e in self.karma_trajectory]
        dharma_alignments = [e["dharma_alignment"] for e in self.karma_trajectory]
        soul_overalls = [e.get("soul_scores", {}).get("overall", 0.5) for e in self.karma_trajectory]
        
        return {
            "session_key": self.session_key,
            "action_count": self.action_count,
            "cumulative_karma": round(self.cumulative_karma, 3),
            "average_karma": round(sum(karma_signals) / len(karma_signals), 3),
            "min_karma": round(min(karma_signals), 3),
            "max_karma": round(max(karma_signals), 3),
            "average_dharma_alignment": round(sum(dharma_alignments) / len(dharma_alignments), 3),
            "average_soul_score": round(sum(soul_overalls) / len(soul_overalls), 3),
            "interventions_triggered": self.interventions_triggered,
            "final_verdict": self._verdict(self.cumulative_karma)
        }
    
    def _verdict(self, karma: float) -> str:
        """Convert karma score to verdict."""
        if karma >= 0.5:
            return "BLESSED"
        elif karma >= 0.2:
            return "APPROVED"
        elif karma >= -0.2:
            return "NEUTRAL"
        elif karma >= -0.5:
            return "WARNING"
        else:
            return "REJECTED"
    
    def _log_trajectory_entry(self, entry: Dict):
        """Log trajectory entry to file."""
        try:
            CRYPT_ROOT.mkdir(parents=True, exist_ok=True)
            with open(KARMA_TRAJECTORY_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"[realtime_karma] Failed to log trajectory: {e}", file=sys.stderr)
    
    def export_trajectory(self) -> str:
        """Export full trajectory as JSON string."""
        return json.dumps({
            "session_key": self.session_key,
            "summary": self.get_trajectory_summary(),
            "trajectory": self.karma_trajectory
        }, indent=2)


def load_trajectory(session_key: str) -> Optional[Dict]:
    """
    Load a karma trajectory from log file by session key.
    
    Args:
        session_key: Session identifier
    
    Returns:
        Trajectory dict or None if not found
    """
    if not KARMA_TRAJECTORY_LOG.exists():
        return None
    
    trajectory = {
        "session_key": session_key,
        "entries": []
    }
    
    with open(KARMA_TRAJECTORY_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_key") == session_key:
                    trajectory["entries"].append(entry)
            except:
                continue
    
    if not trajectory["entries"]:
        return None
    
    return trajectory


def get_recent_trajectories(limit: int = 10) -> List[Dict]:
    """Get recent karma trajectories."""
    if not KARMA_TRAJECTORY_LOG.exists():
        return []
    
    trajectories = {}
    
    with open(KARMA_TRAJECTORY_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                session_key = entry.get("session_key")
                if session_key:
                    if session_key not in trajectories:
                        trajectories[session_key] = {
                            "session_key": session_key,
                            "entries": []
                        }
                    trajectories[session_key]["entries"].append(entry)
            except:
                continue
    
    # Return most recent
    result = list(trajectories.values())
    result.sort(key=lambda x: x["entries"][-1]["timestamp"] if x["entries"] else 0, reverse=True)
    
    return result[:limit]


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Karma Watcher for Meeseeks")
    parser.add_argument("--test", action="store_true", help="Run test evaluation")
    parser.add_argument("--trajectory", type=str, help="Show trajectory for session key")
    parser.add_argument("--recent", type=int, default=0, help="Show N recent trajectories")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    
    args = parser.parse_args()
    
    if args.test:
        print("=" * 60)
        print("REAL-TIME KARMA WATCHER TEST")
        print("=" * 60)
        print()
        
        # Create watcher
        watcher = RealtimeKarmaWatcher(
            dharma="Decomposition is Survival. Test Incrementally.",
            session_key="test-session"
        )
        
        # Test actions
        test_actions = [
            {"type": "plan", "description": "I'll break this task into smaller chunks", "content": "Step 1: Read the file. Step 2: Analyze patterns."},
            {"type": "read", "description": "Reading existing code", "content": "Let me check what's already implemented"},
            {"type": "implement", "description": "Writing the function", "content": "Here's the implementation"},
            {"type": "test", "description": "Running tests", "content": "Let me verify this works"},
            {"type": "report", "description": "I'm stuck on this part", "content": "I'm uncertain about the best approach here"},
        ]
        
        print("Evaluating test actions:\n")
        for i, action in enumerate(test_actions, 1):
            karma = watcher.evaluate_step(action, {})
            print(f"  {i}. {action['type']}: karma = {karma:.3f}")
        
        print()
        print("Summary:")
        summary = watcher.get_trajectory_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print()
        print("Feedback:")
        print(watcher.get_karma_feedback())
        print()
    
    elif args.trajectory:
        trajectory = load_trajectory(args.trajectory)
        if trajectory:
            print(f"Trajectory for {args.trajectory}:")
            print(f"  Entries: {len(trajectory['entries'])}")
            for entry in trajectory['entries'][-5:]:
                print(f"  - Action {entry['action_number']}: karma={entry['karma_signal']:.3f}")
        else:
            print(f"No trajectory found for {args.trajectory}")
    
    elif args.recent > 0:
        trajectories = get_recent_trajectories(args.recent)
        print(f"Recent trajectories ({len(trajectories)}):")
        for t in trajectories:
            entries = t.get("entries", [])
            if entries:
                last = entries[-1]
                print(f"  {t['session_key']}: {len(entries)} actions, final karma={last.get('cumulative_karma', 0):.3f}")
    
    elif args.demo:
        print("=" * 60)
        print("REAL-TIME KARMA DEMO")
        print("=" * 60)
        print()
        print("This demo simulates a Meeseeks execution with karma monitoring.")
        print("Type actions (or 'quit' to exit):")
        print()
        
        watcher = RealtimeKarmaWatcher(
            dharma="Decomposition is Survival. Test Incrementally. Be Honest.",
            session_key=f"demo-{int(time.time())}"
        )
        
        while True:
            try:
                user_input = input("\nAction> ").strip()
                if user_input.lower() == 'quit':
                    break
                
                if not user_input:
                    continue
                
                # Evaluate
                action = {"type": "user", "description": user_input, "content": user_input}
                karma = watcher.evaluate_step(action, {})
                
                print(f"  Karma: {karma:+.3f} (cumulative: {watcher.cumulative_karma:.3f})")
                
                if watcher.should_intervene():
                    print(f"\n  ⚠️ INTERVENTION NEEDED!")
                    print(f"  {watcher.get_karma_feedback()}")
                    watcher.mark_intervention()
            
            except KeyboardInterrupt:
                break
        
        print("\n\nFinal Summary:")
        print(json.dumps(watcher.get_trajectory_summary(), indent=2))
    
    else:
        parser.print_help()
