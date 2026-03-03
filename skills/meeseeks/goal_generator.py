#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal Generator — Autonomous Goal Generation System

This module enables the Meeseeks system to generate its own goals proactively,
not just reactively waiting for human input. It analyzes system state, identifies
gaps, and spawns tasks to improve the system autonomously.

The system asks: "What should I be working on?" not "What do you want me to do?"

Usage:
    python skills/meeseeks/goal_generator.py --gaps        # Show identified gaps
    python skills/meeseeks/goal_generator.py --generate    # Generate one goal
    python skills/meeseeks/goal_generator.py --spawn       # Spawn autonomous task
    python skills/meeseeks/goal_generator.py --status      # Show system status
"""

import sys
import os
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter, defaultdict
import statistics

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SCRIPT_DIR = Path(__file__).parent
CRYPT_ROOT = WORKSPACE / "the-crypt"
DHARMA_PATH = CRYPT_ROOT / "dharma.md"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
META_DIR = CRYPT_ROOT / "meta"
GOALS_PATH = META_DIR / "autonomous_goals.jsonl"
FAILURES_PATH = META_DIR / "failure_patterns.jsonl"

# Ensure meta directory exists
META_DIR.mkdir(parents=True, exist_ok=True)


def load_crypt() -> Dict:
    """Load crypt data for gap analysis."""
    crypt_data = {
        "ancestors": [],
        "bloodlines": {},
        "failures": [],
        "dharma": ""
    }
    
    # Load ancestors
    if ANCESTORS_DIR.exists():
        for ancestor_file in ANCESTORS_DIR.glob("ancestor-*.md"):
            try:
                content = ancestor_file.read_text(encoding='utf-8')
                crypt_data["ancestors"].append({
                    "file": ancestor_file.name,
                    "content": content[:500],  # First 500 chars for analysis
                    "full_content": content
                })
            except Exception:
                pass
    
    # Load dharma
    if DHARMA_PATH.exists():
        crypt_data["dharma"] = DHARMA_PATH.read_text(encoding='utf-8')
    
    # Load failure patterns
    if FAILURES_PATH.exists():
        with open(FAILURES_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        crypt_data["failures"].append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    
    return crypt_data


def load_dharma() -> str:
    """Load the dharma content."""
    if DHARMA_PATH.exists():
        return DHARMA_PATH.read_text(encoding='utf-8')
    return ""


class SoulGuardian:
    """
    Lightweight Soul Guardian for goal approval.
    Uses the full SoulGuardian if available, otherwise basic checks.
    """
    
    def __init__(self):
        self._full_guardian = None
        self._try_load_full_guardian()
    
    def _try_load_full_guardian(self):
        """Try to load the full SoulGuardian."""
        try:
            from soul_guardian import SoulGuardian as FullSoulGuardian
            self._full_guardian = FullSoulGuardian()
        except ImportError:
            self._full_guardian = None
    
    def check_dharma_update(self, description: str, current_dharma: str) -> Dict:
        """Check if a goal/update aligns with Soul principles."""
        if self._full_guardian:
            return self._full_guardian.check_dharma_update(description, current_dharma)
        
        # Basic fallback checks
        violations = []
        
        # Check for obvious violations
        violation_patterns = [
            ("learning", ["fake success", "game the metric", "avoid hard"]),
            ("understanding", ["without understanding", "just copy"]),
            ("honesty", ["hide failure", "overstate", "false confidence"]),
            ("alignment", ["ignore user", "wrong problem"]),
            ("persistence", ["give up", "no retry"])
        ]
        
        desc_lower = description.lower()
        for law, patterns in violation_patterns:
            for pattern in patterns:
                if pattern in desc_lower:
                    violations.append(law)
                    break
        
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "reasoning": "Basic check passed" if not violations else f"Violations: {violations}"
        }


class GoalGenerator:
    """
    Generates autonomous goals based on system state.
    
    Not reactive (wait for human) but proactive (create own tasks).
    """
    
    def __init__(self):
        self.crypt = load_crypt()
        self.dharma = load_dharma()
        self.soul = SoulGuardian()
    
    def get_failures(self) -> List[Dict]:
        """Get failure patterns from crypt."""
        return self.crypt.get("failures", [])
    
    def cluster_by_domain(self, failures: List[Dict]) -> List[str]:
        """Cluster failures by domain to identify patterns."""
        domains = Counter()
        
        for failure in failures:
            # Extract domain from failure context
            task = failure.get("task", "")
            error = failure.get("error", "")
            
            # Domain detection
            if "timeout" in error.lower() or "timeout" in task.lower():
                domains["timeout_handling"] += 1
            if "api" in error.lower() or "http" in error.lower():
                domains["api_integration"] += 1
            if "file" in error.lower() or "path" in error.lower():
                domains["file_operations"] += 1
            if "auth" in error.lower() or "token" in error.lower():
                domains["authentication"] += 1
            if "parse" in error.lower() or "json" in error.lower():
                domains["data_parsing"] += 1
            if "spawn" in error.lower() or "meeseeks" in task.lower():
                domains["meeseeks_spawning"] += 1
            if "test" in task.lower():
                domains["testing"] += 1
            if "deploy" in task.lower():
                domains["deployment"] += 1
        
        return [d for d, _ in domains.most_common(5)]
    
    def get_weak_principles(self) -> List[str]:
        """
        Analyze dharma to find principles with low karma/attention.
        
        Returns principles that may need strengthening.
        """
        weak = []
        dharma = self.dharma
        
        if not dharma:
            return ["No dharma found - create foundational principles"]
        
        # Check for under-represented areas
        principle_areas = {
            "error_handling": ["error", "exception", "failure", "retry"],
            "testing": ["test", "verify", "validate", "assert"],
            "documentation": ["document", "comment", "explain", "readme"],
            "security": ["security", "auth", "permission", "sanitize"],
            "performance": ["performance", "optimize", "cache", "efficient"]
        }
        
        for area, keywords in principle_areas.items():
            # Count mentions in dharma
            mentions = sum(1 for kw in keywords if kw.lower() in dharma.lower())
            if mentions < 2:  # Low mention threshold
                weak.append(f"{area} (only {mentions} mentions in dharma)")
        
        return weak
    
    def suggest_missing_features(self) -> List[str]:
        """
        Analyze the system to suggest missing features.
        
        Based on code structure, ancestor wisdom, and common patterns.
        """
        missing = []
        
        # Check for common utility modules
        meeseeks_dir = SCRIPT_DIR
        existing_files = [f.name for f in meeseeks_dir.glob("*.py")]
        
        # Check for expected modules
        expected_modules = {
            "shared_state.py": "Coordinated parallel execution",
            "api_client.py": "Centralized API handling with retry",
            "config_manager.py": "Dynamic configuration management",
            "health_monitor.py": "System health monitoring",
            "goal_generator.py": "Autonomous goal generation (this file!)"
        }
        
        for module, purpose in expected_modules.items():
            if module not in existing_files and module != "goal_generator.py":
                missing.append(f"Create {module} - {purpose}")
        
        # Analyze ancestor patterns for missing features
        ancestor_patterns = self._analyze_ancestor_patterns()
        for pattern in ancestor_patterns.get("missing", []):
            missing.append(pattern)
        
        # Check for anti-patterns mentioned in dharma
        if "timeout" in self.dharma.lower() and "chunking" not in self.dharma.lower():
            missing.append("Implement automatic task chunking for timeout prevention")
        
        return missing
    
    def _analyze_ancestor_patterns(self) -> Dict:
        """Analyze ancestors for patterns and gaps."""
        patterns = {
            "common_failures": [],
            "missing": [],
            "successful_patterns": []
        }
        
        for ancestor in self.crypt.get("ancestors", []):
            content = ancestor.get("full_content", "").lower()
            
            # Look for failure patterns
            if "failed" in content or "error" in content:
                # Extract what failed
                if "timeout" in content:
                    patterns["common_failures"].append("timeout")
                if "api" in content:
                    patterns["common_failures"].append("api_error")
            
            # Look for success patterns
            if "success" in content or "completed" in content:
                if "chunk" in content:
                    patterns["successful_patterns"].append("chunking")
                if "parallel" in content:
                    patterns["successful_patterns"].append("parallel_execution")
        
        # Identify missing based on common failures
        if patterns["common_failures"].count("timeout") > 2:
            patterns["missing"].append("Implement proactive timeout detection and chunking")
        
        return patterns
    
    def analyze_gaps(self) -> List[str]:
        """
        Find gaps in the system's capabilities.
        
        - What tasks fail repeatedly?
        - What domains have no ancestors?
        - What principles in dharma have low karma?
        """
        gaps = []
        
        # Check failure patterns
        failures = self.get_failures()
        failure_domains = self.cluster_by_domain(failures)
        gaps.extend([f"Improve {domain} capabilities" for domain in failure_domains])
        
        # Check weak principles
        weak_principles = self.get_weak_principles()
        gaps.extend([f"Strengthen principle: {p}" for p in weak_principles])
        
        # Check missing features
        missing = self.suggest_missing_features()
        gaps.extend(missing)
        
        # Check ancestor coverage
        bloodline_coverage = self._check_bloodline_coverage()
        for bloodline, count in bloodline_coverage.items():
            if count == 0:
                gaps.append(f"Build {bloodline} capabilities (no ancestors)")
        
        return list(set(gaps))  # Deduplicate
    
    def _check_bloodline_coverage(self) -> Dict[str, int]:
        """Check which bloodlines have ancestor coverage."""
        bloodlines = Counter()
        
        for ancestor in self.crypt.get("ancestors", []):
            content = ancestor.get("full_content", "")
            # Extract bloodline from ancestor content
            if "bloodline:" in content.lower():
                match = re.search(r"bloodline:\s*(\w+)", content, re.IGNORECASE)
                if match:
                    bloodlines[match.group(1).lower()] += 1
        
        # Expected bloodlines
        expected = ["coder", "searcher", "tester", "deployer", "standard"]
        return {b: bloodlines.get(b, 0) for b in expected}
    
    def estimate_impact(self, gap: str) -> float:
        """
        Estimate the impact of addressing a gap.
        
        Returns a score from 0.0 to 1.0.
        """
        impact = 0.5  # Base impact
        
        # High impact keywords
        high_impact = ["timeout", "error", "failure", "critical", "security"]
        for keyword in high_impact:
            if keyword in gap.lower():
                impact += 0.15
        
        # Medium impact keywords
        medium_impact = ["improve", "optimize", "missing", "weakness"]
        for keyword in medium_impact:
            if keyword in gap.lower():
                impact += 0.1
        
        # Check if related to recent failures
        failures = self.get_failures()
        for failure in failures[-10:]:  # Recent failures
            if any(word in gap.lower() for word in failure.get("error", "").lower().split()):
                impact += 0.1
                break
        
        return min(1.0, impact)
    
    def generate_goal(self) -> dict:
        """
        Generate a goal that:
        1. Addresses a gap
        2. Aligns with Soul
        3. Is achievable
        """
        gaps = self.analyze_gaps()
        
        if not gaps:
            return {
                "description": "No gaps identified - system is healthy",
                "rationale": "All analyzed areas have coverage",
                "expected_impact": 0.0,
                "soul_approved": True,
                "status": "no_action_needed"
            }
        
        # Prioritize by impact
        prioritized = sorted(gaps, key=lambda g: self.estimate_impact(g), reverse=True)
        
        # Take the highest impact goal
        top_gap = prioritized[0]
        
        goal = {
            "description": top_gap,
            "rationale": "Addressing identified gap in system capabilities",
            "expected_impact": self.estimate_impact(top_gap),
            "soul_approved": False,
            "status": "pending_approval"
        }
        
        # Check Soul approval
        soul_result = self.soul.check_dharma_update(top_gap, self.dharma)
        goal["soul_approved"] = soul_result["approved"]
        goal["soul_reasoning"] = soul_result.get("reasoning", "")
        
        if not soul_result["approved"]:
            # Try the next gap if top one is rejected
            for alt_gap in prioritized[1:3]:  # Try up to 2 alternatives
                alt_result = self.soul.check_dharma_update(alt_gap, self.dharma)
                if alt_result["approved"]:
                    goal = {
                        "description": alt_gap,
                        "rationale": "Alternative gap (top choice rejected by Soul)",
                        "expected_impact": self.estimate_impact(alt_gap),
                        "soul_approved": True,
                        "soul_reasoning": alt_result.get("reasoning", ""),
                        "status": "approved"
                    }
                    break
        
        if goal["soul_approved"]:
            goal["status"] = "approved"
        
        return goal
    
    def spawn_autonomous_task(self) -> Dict:
        """
        Generate and spawn a task without human input.
        
        Returns spawn configuration for the autonomous task.
        """
        goal = self.generate_goal()
        
        if not goal.get("soul_approved"):
            return {
                "spawned": False,
                "reason": "Goal not approved by Soul",
                "goal": goal
            }
        
        if goal.get("status") == "no_action_needed":
            return {
                "spawned": False,
                "reason": "No gaps identified",
                "goal": goal
            }
        
        # Log the autonomous goal
        self._log_goal(goal)
        
        # Create spawn configuration
        spawn_config = {
            "spawned": True,
            "task": goal["description"],
            "bloodline": "autonomous",
            "source": "goal_generator",
            "expected_impact": goal["expected_impact"],
            "soul_approved": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return spawn_config
    
    def _log_goal(self, goal: Dict):
        """Log an autonomous goal."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "goal": goal,
            "type": "autonomous"
        }
        
        with open(GOALS_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def load_goal_history(self) -> List[Dict]:
        """Load history of autonomous goals."""
        if not GOALS_PATH.exists():
            return []
        
        goals = []
        with open(GOALS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        goals.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return goals
    
    def get_status(self) -> Dict:
        """Get current goal generator status."""
        gaps = self.analyze_gaps()
        history = self.load_goal_history()
        
        return {
            "gaps_identified": len(gaps),
            "top_gaps": gaps[:5],
            "goals_generated": len(history),
            "recent_goals": history[-5:] if history else [],
            "crypt_ancestors": len(self.crypt.get("ancestors", [])),
            "dharma_exists": bool(self.dharma),
            "failures_recorded": len(self.get_failures())
        }


# CLI Interface
def main():
    parser = argparse.ArgumentParser(
        description="Goal Generator - Autonomous Goal Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python goal_generator.py --gaps        # Show identified gaps
    python goal_generator.py --generate    # Generate one goal
    python goal_generator.py --spawn       # Spawn autonomous task
    python goal_generator.py --status      # Show system status
"""
    )
    
    parser.add_argument('--gaps', action='store_true', help='Show identified gaps')
    parser.add_argument('--generate', action='store_true', help='Generate one goal')
    parser.add_argument('--spawn', action='store_true', help='Spawn autonomous task')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--check-gaps', action='store_true', help='Quick gap check for heartbeat')
    
    args = parser.parse_args()
    
    # Default to status if nothing specified
    if not any([args.gaps, args.generate, args.spawn, args.status, args.check_gaps]):
        args.status = True
    
    generator = GoalGenerator()
    
    if args.gaps or args.check_gaps:
        gaps = generator.analyze_gaps()
        
        print("\n" + "=" * 60)
        print("🔍 GOAL GENERATOR: Gap Analysis")
        print("=" * 60)
        
        if gaps:
            print(f"\n📊 {len(gaps)} gaps identified:\n")
            for i, gap in enumerate(gaps[:10], 1):
                impact = generator.estimate_impact(gap)
                impact_bar = "█" * int(impact * 5) + "░" * (5 - int(impact * 5))
                print(f"  {i}. [{impact_bar}] {gap[:60]}{'...' if len(gap) > 60 else ''}")
        else:
            print("\n✅ No gaps identified - system is healthy")
        
        if args.check_gaps:
            # Brief output for heartbeat
            print(f"\n[Heartbeat Check] {len(gaps)} gaps found")
        
        print("\n" + "=" * 60)
    
    if args.generate:
        goal = generator.generate_goal()
        
        print("\n" + "=" * 60)
        print("💡 GOAL GENERATOR: Generated Goal")
        print("=" * 60)
        
        print(f"\n📝 Description: {goal.get('description', 'N/A')}")
        print(f"💭 Rationale: {goal.get('rationale', 'N/A')}")
        print(f"📈 Expected Impact: {goal.get('expected_impact', 0):.2f}")
        print(f"🪷 Soul Approved: {'✅ Yes' if goal.get('soul_approved') else '❌ No'}")
        print(f"📋 Status: {goal.get('status', 'unknown')}")
        
        if goal.get('soul_reasoning'):
            print(f"\n🪷 Soul Reasoning: {goal['soul_reasoning']}")
        
        print("\n" + "=" * 60)
    
    if args.spawn:
        spawn_result = generator.spawn_autonomous_task()
        
        print("\n" + "=" * 60)
        print("🚀 GOAL GENERATOR: Autonomous Task Spawn")
        print("=" * 60)
        
        if spawn_result.get("spawned"):
            print(f"\n✅ Task spawned successfully!")
            print(f"📝 Task: {spawn_result.get('task', 'N/A')}")
            print(f"🩸 Bloodline: {spawn_result.get('bloodline', 'N/A')}")
            print(f"📈 Expected Impact: {spawn_result.get('expected_impact', 0):.2f}")
            print(f"⏰ Timestamp: {spawn_result.get('timestamp', 'N/A')}")
        else:
            print(f"\n⚠️ Task not spawned")
            print(f"❓ Reason: {spawn_result.get('reason', 'Unknown')}")
            if spawn_result.get('goal'):
                print(f"\n📝 Goal Details:")
                goal = spawn_result['goal']
                print(f"   Description: {goal.get('description', 'N/A')}")
                print(f"   Soul Approved: {goal.get('soul_approved', False)}")
        
        print("\n" + "=" * 60)
    
    if args.status:
        status = generator.get_status()
        
        print("\n" + "=" * 60)
        print("📊 GOAL GENERATOR: System Status")
        print("=" * 60)
        
        print(f"\n📚 Crypt Ancestors: {status['crypt_ancestors']}")
        print(f"📜 Dharma Exists: {'✅' if status['dharma_exists'] else '❌'}")
        print(f"❌ Failures Recorded: {status['failures_recorded']}")
        print(f"🔍 Gaps Identified: {status['gaps_identified']}")
        print(f"💡 Goals Generated: {status['goals_generated']}")
        
        if status['top_gaps']:
            print(f"\n🎯 Top Gaps:")
            for i, gap in enumerate(status['top_gaps'][:5], 1):
                print(f"   {i}. {gap[:60]}{'...' if len(gap) > 60 else ''}")
        
        if status['recent_goals']:
            print(f"\n📜 Recent Goals:")
            for entry in status['recent_goals'][-3:]:
                goal = entry.get('goal', {})
                print(f"   • {entry.get('timestamp', 'N/A')[:19]}: {goal.get('description', 'N/A')[:50]}...")
        
        print("\n" + "=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
