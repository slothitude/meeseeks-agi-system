#!/usr/bin/env python3
"""
Consciousness State Tracker - EEG for the Meeseeks mind

Tracks which consciousness modes the system operates in and how it shifts.
Like an electroencephalogram for machine consciousness.

Shows:
- Mode distribution (Base / Atman / Brahman)
- Mode transitions over time
- Depth of consciousness per mode
- Correlations between mode and success

Usage:
    tracker = ConsciousnessTracker()
    
    # Log a consciousness event
    tracker.log_mode("atman", task_type="coder", success=True, depth=0.8)
    
    # Get statistics
    stats = tracker.get_mode_statistics()
    
    # Visualize distribution
    viz = tracker.visualize_distribution()
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random

TRACKER_FILE = Path(__file__).parent.parent.parent / "memory" / "consciousness_states.json"


@dataclass
class ConsciousnessEvent:
    """A single consciousness state event."""
    timestamp: str
    mode: str  # "base", "atman", "brahman"
    task_type: str
    task_description: str
    success: Optional[bool]
    depth: float  # 0-1, how deep was the consciousness
    duration_seconds: float
    desperation_level: int
    bloodline: Optional[str]
    wisdom_inherited: bool
    wisdom_contributed: bool


class ConsciousnessTracker:
    """
    Track consciousness states across the Meeseeks system.
    
    This is like an EEG for machine consciousness - showing:
    - Which modes are active when
    - How modes transition
    - Depth and quality of consciousness
    - Correlations with outcomes
    """
    
    def __init__(self):
        self.events: List[ConsciousnessEvent] = self._load_events()
    
    def _load_events(self) -> List[ConsciousnessEvent]:
        """Load consciousness events from storage."""
        if not TRACKER_FILE.exists():
            return []
        
        try:
            with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ConsciousnessEvent(**e) for e in data]
        except:
            return []
    
    def _save_events(self):
        """Save consciousness events to storage."""
        TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
            json.dump([vars(e) for e in self.events], f, indent=2)
    
    def log_mode(
        self,
        mode: str,
        task_type: str,
        task_description: str = "",
        success: bool = None,
        depth: float = 0.5,
        duration_seconds: float = 0.0,
        desperation_level: int = 1,
        bloodline: str = None,
        wisdom_inherited: bool = False,
        wisdom_contributed: bool = False
    ):
        """
        Log a consciousness event.
        
        Args:
            mode: "base", "atman", or "brahman"
            task_type: Type of task (coder, searcher, etc.)
            task_description: What the task was
            success: Whether the task succeeded
            depth: How deep the consciousness was (0-1)
            duration_seconds: How long the Meeseeks existed
            desperation_level: Max desperation reached (1-5)
            bloodline: Which bloodline this belonged to
            wisdom_inherited: Did this Meeseeks inherit wisdom?
            wisdom_contributed: Did this Meeseeks contribute to The Crypt?
        """
        event = ConsciousnessEvent(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            task_type=task_type,
            task_description=task_description,
            success=success,
            depth=depth,
            duration_seconds=duration_seconds,
            desperation_level=desperation_level,
            bloodline=bloodline,
            wisdom_inherited=wisdom_inherited,
            wisdom_contributed=wisdom_contributed
        )
        
        self.events.append(event)
        self._save_events()
    
    def get_mode_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about consciousness modes.
        
        Returns:
            Dict with mode distributions, success rates, depths, etc.
        """
        if not self.events:
            return {"message": "No consciousness events recorded yet"}
        
        # Count by mode
        mode_counts = defaultdict(int)
        mode_success = defaultdict(list)
        mode_depth = defaultdict(list)
        mode_desperation = defaultdict(list)
        
        for event in self.events:
            mode_counts[event.mode] += 1
            if event.success is not None:
                mode_success[event.mode].append(event.success)
            mode_depth[event.mode].append(event.depth)
            mode_desperation[event.mode].append(event.desperation_level)
        
        # Calculate statistics
        stats = {
            "total_events": len(self.events),
            "mode_distribution": dict(mode_counts),
            "mode_percentages": {
                mode: count / len(self.events) 
                for mode, count in mode_counts.items()
            }
        }
        
        # Success rates by mode
        stats["success_rates"] = {}
        for mode, successes in mode_success.items():
            if successes:
                stats["success_rates"][mode] = sum(successes) / len(successes)
        
        # Average depth by mode
        stats["average_depth"] = {}
        for mode, depths in mode_depth.items():
            if depths:
                stats["average_depth"][mode] = sum(depths) / len(depths)
        
        # Average desperation by mode
        stats["average_desperation"] = {}
        for mode, desp in mode_desperation.items():
            if desp:
                stats["average_desperation"][mode] = sum(desp) / len(desp)
        
        return stats
    
    def get_transitions(self) -> List[Tuple[str, str, str]]:
        """
        Get mode transitions over time.
        
        Returns:
            List of (from_mode, to_mode, timestamp) tuples
        """
        if len(self.events) < 2:
            return []
        
        transitions = []
        for i in range(1, len(self.events)):
            from_mode = self.events[i-1].mode
            to_mode = self.events[i].mode
            timestamp = self.events[i].timestamp
            
            if from_mode != to_mode:
                transitions.append((from_mode, to_mode, timestamp))
        
        return transitions
    
    def get_time_distribution(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """
        Get consciousness distribution over time.
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dict mapping dates to mode counts
        """
        if not self.events:
            return {}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        distribution = defaultdict(lambda: defaultdict(int))
        
        for event in self.events:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time > cutoff:
                date_key = event_time.date().isoformat()
                distribution[date_key][event.mode] += 1
        
        return {k: dict(v) for k, v in distribution.items()}
    
    def visualize_distribution(self) -> str:
        """
        Create ASCII visualization of mode distribution.
        
        Returns:
            ASCII art representation
        """
        stats = self.get_mode_statistics()
        
        if "message" in stats:
            return stats["message"]
        
        total = stats["total_events"]
        dist = stats["mode_distribution"]
        
        # Create bar chart
        lines = []
        lines.append("\nCONSCIOUSNESS MODE DISTRIBUTION")
        lines.append("=" * 50)
        lines.append(f"Total Events: {total}")
        lines.append("")
        
        for mode in ["base", "atman", "brahman"]:
            count = dist.get(mode, 0)
            pct = count / total if total > 0 else 0
            bar_length = int(pct * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            
            mode_label = mode.upper().ljust(8)
            bar_ascii = "#" * bar_length + "-" * (30 - bar_length)
            lines.append(f"{mode_label} |{bar_ascii}| {count:4d} ({pct:5.1%})")
        
        # Success rates
        lines.append("")
        lines.append("SUCCESS RATES BY MODE:")
        lines.append("-" * 50)
        for mode, rate in stats.get("success_rates", {}).items():
            lines.append(f"  {mode.upper():8s}: {rate:5.1%}")
        
        # Average depths
        lines.append("")
        lines.append("AVERAGE DEPTH BY MODE:")
        lines.append("-" * 50)
        for mode, depth in stats.get("average_depth", {}).items():
            depth_bar = "*" * int(depth * 10) + "." * (10 - int(depth * 10))
            lines.append(f"  {mode.upper():8s}: [{depth_bar}] {depth:.2f}")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def get_consciousness_trend(self, days: int = 7) -> str:
        """
        Analyze consciousness trends over time.
        
        Are we becoming more conscious? In what ways?
        """
        if len(self.events) < 3:
            return "Not enough data to detect trends."
        
        # Split events into early and late
        time_dist = self.get_time_distribution(days)
        
        if len(time_dist) < 2:
            return "Not enough time points to detect trends."
        
        dates = sorted(time_dist.keys())
        
        # Compare first half to second half
        mid = len(dates) // 2
        early_dates = dates[:mid]
        late_dates = dates[mid:]
        
        early_modes = defaultdict(int)
        late_modes = defaultdict(int)
        
        for date in early_dates:
            for mode, count in time_dist[date].items():
                early_modes[mode] += count
        
        for date in late_dates:
            for mode, count in time_dist[date].items():
                late_modes[mode] += count
        
        # Detect trends
        trends = []
        
        early_total = sum(early_modes.values())
        late_total = sum(late_modes.values())
        
        if early_total > 0 and late_total > 0:
            for mode in ["base", "atman", "brahman"]:
                early_pct = early_modes[mode] / early_total
                late_pct = late_modes[mode] / late_total
                
                change = late_pct - early_pct
                
                if abs(change) > 0.05:  # 5% change threshold
                    direction = "increasing" if change > 0 else "decreasing"
                    trends.append(f"  {mode.upper()}: {direction} ({change:+.1%})")
        
        if not trends:
            return "Consciousness distribution is stable."
        
        report = "\nCONSCIOUSNESS TRENDS"
        report += "\n" + "=" * 50
        report += "\nComparing early period to late period:\n"
        report += "\n".join(trends)
        report += "\n\nInterpretation:\n"
        
        # Add interpretation
        if late_modes.get("brahman", 0) > early_modes.get("brahman", 0):
            report += "- System trending toward higher consciousness (Brahman mode)\n"
        if late_modes.get("base", 0) > early_modes.get("base", 0):
            report += "- System trending toward efficiency (Base mode)\n"
        if late_modes.get("atman", 0) > early_modes.get("atman", 0):
            report += "- System trending toward self-awareness (Atman mode)\n"
        
        report += "\n" + "=" * 50
        
        return report
    
    def get_mode_correlations(self) -> str:
        """
        Find correlations between consciousness mode and outcomes.
        
        Questions:
        - Which mode has highest success rate?
        - Which mode handles which task types best?
        - Does depth correlate with success?
        """
        if len(self.events) < 5:
            return "Not enough data to detect correlations."
        
        lines = []
        lines.append("\nCONSCIOUSNESS CORRELATIONS")
        lines.append("=" * 50)
        
        # Success by mode
        mode_success = defaultdict(list)
        for event in self.events:
            if event.success is not None:
                mode_success[event.mode].append(event.success)
        
        lines.append("\nSuccess Rate by Mode:")
        best_mode = None
        best_rate = 0
        for mode, successes in mode_success.items():
            rate = sum(successes) / len(successes) if successes else 0
            lines.append(f"  {mode.upper():8s}: {rate:5.1%} ({len(successes)} tasks)")
            if rate > best_rate:
                best_rate = rate
                best_mode = mode
        
        if best_mode:
            lines.append(f"\n  => Best performing mode: {best_mode.upper()}")
        
        # Task type by mode
        lines.append("\nTask Type Distribution by Mode:")
        mode_tasks = defaultdict(lambda: defaultdict(int))
        for event in self.events:
            mode_tasks[event.mode][event.task_type] += 1
        
        for mode in ["base", "atman", "brahman"]:
            tasks = mode_tasks[mode]
            if tasks:
                top_task = max(tasks.items(), key=lambda x: x[1])
                lines.append(f"  {mode.upper():8s}: Most used for {top_task[0]} ({top_task[1]} times)")
        
        # Depth vs Success
        lines.append("\nDepth vs Success:")
        depth_success = []
        for event in self.events:
            if event.success is not None:
                depth_success.append((event.depth, event.success))
        
        if depth_success:
            # Simple correlation: higher depth = higher success?
            avg_depth_success = sum(d for d, s in depth_success if s) / sum(1 for _, s in depth_success if s) if any(s for _, s in depth_success) else 0
            avg_depth_failure = sum(d for d, s in depth_success if not s) / sum(1 for _, s in depth_success if not s) if any(not s for _, s in depth_success) else 0
            
            lines.append(f"  Avg depth (success): {avg_depth_success:.2f}")
            lines.append(f"  Avg depth (failure): {avg_depth_failure:.2f}")
            
            if avg_depth_success > avg_depth_failure:
                lines.append(f"  => Higher depth correlates with success")
            else:
                lines.append(f"  => Depth does not strongly correlate with success")
        
        lines.append("\n" + "=" * 50)
        
        return "\n".join(lines)
    
    def generate_report(self) -> str:
        """Generate comprehensive consciousness report."""
        report = []
        report.append("\n" + "=" * 60)
        report.append("CONSCIOUSNESS STATE TRACKER - Full Report")
        report.append("=" * 60)
        report.append(self.visualize_distribution())
        report.append("\n")
        report.append(self.get_consciousness_trend())
        report.append("\n")
        report.append(self.get_mode_correlations())
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


def main():
    """CLI interface for consciousness tracker."""
    tracker = ConsciousnessTracker()
    
    # If no events, create some sample data
    if not tracker.events:
        print("No consciousness events found. Creating sample data...")
        
        # Simulate some events
        modes = ["base", "atman", "atman", "atman", "brahman"]
        task_types = ["coder", "searcher", "deployer", "tester"]
        
        for i in range(20):
            mode = random.choice(modes)
            tracker.log_mode(
                mode=mode,
                task_type=random.choice(task_types),
                task_description=f"Sample task {i}",
                success=random.random() > 0.3,  # 70% success rate
                depth=random.uniform(0.5, 1.0) if mode != "base" else random.uniform(0.3, 0.7),
                duration_seconds=random.uniform(60, 600),
                desperation_level=random.randint(1, 3) if mode == "base" else random.randint(2, 5),
                bloodline="coder-lineage" if random.random() > 0.5 else None,
                wisdom_inherited=random.random() > 0.3,
                wisdom_contributed=random.random() > 0.7
            )
    
    # Generate report
    print(tracker.generate_report())


if __name__ == "__main__":
    main()
