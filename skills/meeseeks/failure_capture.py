#!/usr/bin/env python3
"""
Failure Pattern Capture for Meeseeks

Captures and analyzes failure patterns from timed-out/failed Meeseeks runs.
This addresses the "0% failures recorded" gap.

Records:
- Why tasks failed (timeout, error, stuck)
- What approaches were tried
- What could be done differently
- Failure patterns by bloodline
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field

FAILURE_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "failure_patterns.json"


@dataclass
class FailurePattern:
    """A captured failure pattern."""
    session_key: str
    task_type: str
    failure_mode: str  # timeout, error, stuck, incomplete
    task_summary: str
    runtime_ms: int
    model: str
    chunked: bool = False
    retry_count: int = 0
    patterns: List[str] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FailureCapture:
    """
    Captures and analyzes failure patterns.
    
    Usage:
        capture = FailureCapture()
        
        # Record a failure
        capture.record_failure(
            session_key="agent:main:subagent:xxx",
            task="Fix the bug...",
            failure_mode="timeout",
            runtime_ms=300000,
            model="zai/glm-5"
        )
        
        # Get patterns
        patterns = capture.get_patterns_by_bloodline("coder")
    """
    
    def __init__(self):
        self.failures: List[Dict] = []
        self._load()
    
    def _load(self):
        """Load existing failure patterns."""
        if FAILURE_FILE.exists():
            try:
                data = json.loads(FAILURE_FILE.read_text(encoding="utf-8"))
                self.failures = data.get("failures", [])
            except:
                self.failures = []
    
    def _save(self):
        """Save failure patterns."""
        FAILURE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "failures": self.failures,
            "stats": self._calculate_stats(),
            "updated": datetime.now().isoformat()
        }
        FAILURE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def _calculate_stats(self) -> Dict:
        """Calculate failure statistics."""
        if not self.failures:
            return {"total": 0, "failure_rate": "0%"}
        
        # Count by failure mode
        modes = {}
        for f in self.failures:
            mode = f.get("failure_mode", "unknown")
            modes[mode] = modes.get(mode, 0) + 1
        
        # Count by task type
        types = {}
        for f in self.failures:
            ttype = f.get("task_type", "unknown")
            types[ttype] = types.get(ttype, 0) + 1
        
        return {
            "total": len(self.failures),
            "by_mode": modes,
            "by_type": types,
            "recent_count": len([f for f in self.failures if self._is_recent(f)])
        }
    
    def _is_recent(self, failure: Dict, hours: int = 24) -> bool:
        """Check if failure is recent."""
        try:
            ts = datetime.fromisoformat(failure.get("timestamp", ""))
            return (datetime.now() - ts).total_seconds() < hours * 3600
        except:
            return False
    
    def infer_task_type(self, task: str) -> str:
        """Infer task type from task description."""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ["evolve", "dna", "bloodline", "evolution"]):
            return "evolver"
        elif any(kw in task_lower for kw in ["arc-agi", "puzzle", "solve"]):
            return "puzzle-solver"
        elif any(kw in task_lower for kw in ["template", "improve"]):
            return "template-evolver"
        elif any(kw in task_lower for kw in ["code", "fix", "implement", "bug"]):
            return "coder"
        elif any(kw in task_lower for kw in ["search", "find", "analyze"]):
            return "searcher"
        else:
            return "standard"
    
    def extract_patterns(self, task: str) -> List[str]:
        """Extract patterns that might have contributed to failure."""
        patterns = []
        task_lower = task.lower()
        
        # Detect complexity indicators
        if len(task) > 2000:
            patterns.append("very_long_task")
        if task.count("\n") > 50:
            patterns.append("many_steps")
        if "all" in task_lower and ("evolve" in task_lower or "analyze" in task_lower):
            patterns.append("broad_scope")
        if "parallel" in task_lower:
            patterns.append("parallel_execution")
        if "recursive" in task_lower or "repeat" in task_lower:
            patterns.append("iterative")
        
        return patterns
    
    def suggest_fixes(self, failure_mode: str, patterns: List[str]) -> List[str]:
        """Suggest fixes based on failure mode and patterns."""
        fixes = []
        
        if failure_mode == "timeout":
            fixes.append("break_into_smaller_chunks")
            fixes.append("reduce_scope")
            if "very_long_task" in patterns:
                fixes.append("simplify_prompt")
            if "many_steps" in patterns:
                fixes.append("parallelize_steps")
        
        elif failure_mode == "error":
            fixes.append("add_error_handling")
            fixes.append("verify_prerequisites")
        
        elif failure_mode == "stuck":
            fixes.append("add_progress_checkpoints")
            fixes.append("enable_early_termination")
        
        return fixes
    
    def record_failure(
        self,
        session_key: str,
        task: str,
        failure_mode: str,
        runtime_ms: int,
        model: str,
        chunked: bool = False,
        retry_count: int = 0
    ):
        """
        Record a failure pattern.
        
        Args:
            session_key: Session identifier
            task: Task description
            failure_mode: timeout, error, stuck, incomplete
            runtime_ms: Runtime in milliseconds
            model: Model used
            chunked: Whether task was chunked for retry
            retry_count: Number of retry attempts
        """
        # Check if already recorded
        existing = [f for f in self.failures if f.get("session_key") == session_key]
        if existing:
            return  # Already captured
        
        task_type = self.infer_task_type(task)
        patterns = self.extract_patterns(task)
        fixes = self.suggest_fixes(failure_mode, patterns)
        
        failure = {
            "session_key": session_key,
            "task_type": task_type,
            "failure_mode": failure_mode,
            "task_summary": task[:200] + "..." if len(task) > 200 else task,
            "runtime_ms": runtime_ms,
            "model": model,
            "chunked": chunked,
            "retry_count": retry_count,
            "patterns": patterns,
            "suggested_fixes": fixes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.failures.append(failure)
        self._save()
        
        print(f"[failure_capture] Recorded: {session_key[:30]}... ({failure_mode})")
    
    def get_patterns_by_type(self, task_type: str) -> List[Dict]:
        """Get failure patterns for a task type."""
        return [f for f in self.failures if f.get("task_type") == task_type]
    
    def get_patterns_by_mode(self, mode: str) -> List[Dict]:
        """Get failure patterns by failure mode."""
        return [f for f in self.failures if f.get("failure_mode") == mode]
    
    def get_common_patterns(self, limit: int = 10) -> List[Dict]:
        """Get most common failure patterns."""
        from collections import Counter
        
        pattern_counts = Counter()
        for f in self.failures:
            for p in f.get("patterns", []):
                pattern_counts[p] += 1
        
        return [{"pattern": p, "count": c} for p, c in pattern_counts.most_common(limit)]
    
    def get_suggested_fixes(self, task: str) -> List[str]:
        """Get suggested fixes for a new task based on past failures."""
        task_type = self.infer_task_type(task)
        patterns = self.extract_patterns(task)
        
        # Find similar past failures
        similar = [f for f in self.failures 
                   if f.get("task_type") == task_type 
                   or any(p in f.get("patterns", []) for p in patterns)]
        
        # Aggregate suggested fixes
        all_fixes = []
        for f in similar:
            all_fixes.extend(f.get("suggested_fixes", []))
        
        # Return unique fixes, prioritized by frequency
        from collections import Counter
        fix_counts = Counter(all_fixes)
        return [f for f, _ in fix_counts.most_common(5)]
    
    def get_stats(self) -> Dict:
        """Get failure statistics."""
        return self._calculate_stats()
    
    def to_prompt_block(self) -> str:
        """Generate failure patterns block for prompt injection."""
        stats = self.get_stats()
        common = self.get_common_patterns(5)
        
        lines = [
            "## ⚠️ Failure Pattern Awareness",
            "",
            f"**Total Failures Captured:** {stats.get('total', 0)}",
            ""
        ]
        
        if common:
            lines.append("### Common Failure Patterns:")
            for item in common:
                lines.append(f"- {item['pattern']} ({item['count']} times)")
            lines.append("")
        
        if stats.get("by_mode"):
            lines.append("### Failures by Mode:")
            for mode, count in stats["by_mode"].items():
                lines.append(f"- {mode}: {count}")
            lines.append("")
        
        lines.append("### Prevention Tips:")
        lines.append("- Break large tasks into smaller chunks")
        lines.append("- Set clear scope limits")
        lines.append("- Use progress checkpoints")
        lines.append("- Enable early termination on stuck detection")
        
        return "\n".join(lines)


# Singleton instance
_capture = None

def get_failure_capture() -> FailureCapture:
    """Get the singleton failure capture instance."""
    global _capture
    if _capture is None:
        _capture = FailureCapture()
    return _capture


def record_failure(session_key: str, task: str, failure_mode: str, 
                   runtime_ms: int, model: str, **kwargs):
    """Convenience function to record a failure."""
    capture = get_failure_capture()
    capture.record_failure(session_key, task, failure_mode, runtime_ms, model, **kwargs)


if __name__ == "__main__":
    # Test failure capture
    capture = FailureCapture()
    
    print("Failure Pattern Capture Test")
    print("=" * 50)
    print(f"Total failures: {len(capture.failures)}")
    print(f"Stats: {capture.get_stats()}")
    print(f"Common patterns: {capture.get_common_patterns()}")
    print()
    print(capture.to_prompt_block())
