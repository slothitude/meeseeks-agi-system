#!/usr/bin/env python3
"""
BDI Model (Beliefs-Desires-Intentions) for Meeseeks

Implements the Beliefs-Desires-Intentions cognitive architecture.

Beliefs: What the Meeseeks knows about the world
Desires: Goals and desired outcomes
Intentions: Committed plans of action
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

BDI_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "bdi_state.json"


class BeliefSystem:
    """Manages beliefs - what the Meeseeks knows."""
    
    def __init__(self):
        self.beliefs = {}
        self.confidence = {}  # 0.0 to 1.0
        self.sources = {}  # Where belief came from
    
    def add_belief(self, key: str, value: Any, confidence: float = 0.8, source: str = "unknown"):
        """Add or update a belief."""
        self.beliefs[key] = value
        self.confidence[key] = confidence
        self.sources[key] = source
    
    def get_belief(self, key: str) -> Optional[Any]:
        """Get a belief by key."""
        return self.beliefs.get(key)
    
    def get_confidence(self, key: str) -> float:
        """Get confidence level for a belief."""
        return self.confidence.get(key, 0.0)
    
    def update_confidence(self, key: str, delta: float):
        """Update confidence based on evidence."""
        if key in self.confidence:
            self.confidence[key] = max(0.0, min(1.0, self.confidence[key] + delta))
    
    def to_prompt_block(self) -> str:
        """Format beliefs for prompt injection."""
        if not self.beliefs:
            return ""
        
        lines = ["### My Beliefs", ""]
        for key, value in self.beliefs.items():
            conf = self.confidence.get(key, 0.5)
            conf_str = "high" if conf > 0.7 else "medium" if conf > 0.4 else "low"
            lines.append(f"- **{key}** ({conf_str} confidence): {value}")
        lines.append("")
        return "\n".join(lines)


class DesireSystem:
    """Manages desires - goals and desired outcomes."""
    
    def __init__(self):
        self.desires = {}  # Goal -> priority (0-1)
        self.deadlines = {}  # Goal -> optional deadline
        self.constraints = {}  # Goal -> list of constraints
    
    def add_desire(self, goal: str, priority: float = 0.5, deadline: str = None, constraints: List[str] = None):
        """Add a desire/goal."""
        self.desires[goal] = priority
        if deadline:
            self.deadlines[goal] = deadline
        if constraints:
            self.constraints[goal] = constraints
    
    def get_top_desire(self) -> Optional[str]:
        """Get highest priority desire."""
        if not self.desires:
            return None
        return max(self.desires.keys(), key=lambda k: self.desires[k])
    
    def get_priority(self, goal: str) -> float:
        """Get priority of a goal."""
        return self.desires.get(goal, 0.0)
    
    def to_prompt_block(self) -> str:
        """Format desires for prompt injection."""
        if not self.desires:
            return ""
        
        lines = ["### My Desires (Goals)", ""]
        sorted_desires = sorted(self.desires.items(), key=lambda x: -x[1])
        
        for goal, priority in sorted_desires:
            priority_str = "CRITICAL" if priority > 0.9 else "HIGH" if priority > 0.7 else "MEDIUM" if priority > 0.4 else "LOW"
            lines.append(f"- [{priority_str}] {goal}")
            if goal in self.constraints:
                for c in self.constraints[goal]:
                    lines.append(f"  - Constraint: {c}")
        lines.append("")
        return "\n".join(lines)


class IntentionSystem:
    """Manages intentions - committed plans of action."""
    
    def __init__(self):
        self.intentions = []  # List of (action, status, result)
        self.current_intention = None
        self.committed = False
    
    def add_intention(self, action: str, rationale: str = ""):
        """Add an intended action."""
        self.intentions.append({
            "action": action,
            "rationale": rationale,
            "status": "pending",
            "result": None,
            "timestamp": datetime.now().isoformat()
        })
    
    def commit(self, intention_idx: int = None):
        """Commit to an intention."""
        if intention_idx is None:
            intention_idx = len(self.intentions) - 1
        
        if 0 <= intention_idx < len(self.intentions):
            self.current_intention = intention_idx
            self.committed = True
            self.intentions[intention_idx]["status"] = "committed"
    
    def complete_current(self, result: str, success: bool = True):
        """Mark current intention as complete."""
        if self.current_intention is not None:
            self.intentions[self.current_intention]["status"] = "completed" if success else "failed"
            self.intentions[self.current_intention]["result"] = result
            self.committed = False
    
    def get_plan(self) -> List[str]:
        """Get remaining actions."""
        return [i["action"] for i in self.intentions if i["status"] == "pending"]
    
    def to_prompt_block(self) -> str:
        """Format intentions for prompt injection."""
        if not self.intentions:
            return ""
        
        lines = ["### My Intentions (Plan)", ""]
        for i, intent in enumerate(self.intentions):
            status_emoji = {
                "pending": "⏳",
                "committed": "🎯",
                "completed": "✅",
                "failed": "❌"
            }.get(intent["status"], "❓")
            
            current = " (CURRENT)" if i == self.current_intention and self.committed else ""
            lines.append(f"{i+1}. {status_emoji} {intent['action']}{current}")
            if intent.get("rationale"):
                lines.append(f"   Rationale: {intent['rationale']}")
        
        lines.append("")
        return "\n".join(lines)


class BDIModel:
    """
    Complete BDI (Beliefs-Desires-Intentions) cognitive model.
    
    Usage:
        bdi = BDIModel()
        
        # Set beliefs
        bdi.believe("file_location", "src/auth.py", confidence=0.9, source="read")
        
        # Set desires
        bdi.desire("Fix authentication bug", priority=0.9)
        bdi.desire("Add error handling", priority=0.6)
        
        # Plan intentions
        bdi.intend("Read auth.py", rationale="Understand current code")
        bdi.intend("Identify bug", rationale="Find root cause")
        bdi.intend("Fix bug", rationale="Implement solution")
        
        # Commit and execute
        bdi.commit(0)  # Commit to first intention
        
        # Generate prompt block
        prompt = bdi.to_prompt()
    """
    
    def __init__(self, session_key: str = None):
        self.session_key = session_key
        self.beliefs = BeliefSystem()
        self.desires = DesireSystem()
        self.intentions = IntentionSystem()
    
    def believe(self, key: str, value: Any, confidence: float = 0.8, source: str = "unknown"):
        """Add a belief."""
        self.beliefs.add_belief(key, value, confidence, source)
    
    def desire(self, goal: str, priority: float = 0.5, deadline: str = None, constraints: List[str] = None):
        """Add a desire."""
        self.desires.add_desire(goal, priority, deadline, constraints)
    
    def intend(self, action: str, rationale: str = ""):
        """Add an intention."""
        self.intentions.add_intention(action, rationale)
    
    def commit(self, intention_idx: int = None):
        """Commit to an intention."""
        self.intentions.commit(intention_idx)
    
    def complete(self, result: str, success: bool = True):
        """Complete current intention."""
        self.intentions.complete_current(result, success)
    
    def to_prompt(self) -> str:
        """Generate BDI block for prompt injection."""
        lines = [
            "## 🧠 BDI Cognitive State",
            "",
            self.beliefs.to_prompt_block(),
            self.desires.to_prompt_block(),
            self.intentions.to_prompt_block(),
        ]
        return "\n".join([l for l in lines if l])
    
    def save(self):
        """Save BDI state to file."""
        if not self.session_key:
            return
        
        BDI_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "session_key": self.session_key,
            "beliefs": self.beliefs.beliefs,
            "confidence": self.beliefs.confidence,
            "desires": self.desires.desires,
            "intentions": self.intentions.intentions,
            "updated": datetime.now().isoformat()
        }
        
        # Load existing or create new
        all_states = {}
        if BDI_FILE.exists():
            try:
                all_states = json.loads(BDI_FILE.read_text(encoding="utf-8"))
            except:
                pass
        
        all_states[self.session_key] = data
        BDI_FILE.write_text(json.dumps(all_states, indent=2), encoding="utf-8")
    
    @classmethod
    def load(cls, session_key: str) -> Optional['BDIModel']:
        """Load BDI state from file."""
        if not BDI_FILE.exists():
            return None
        
        try:
            all_states = json.loads(BDI_FILE.read_text(encoding="utf-8"))
            data = all_states.get(session_key)
            
            if not data:
                return None
            
            bdi = cls(session_key)
            bdi.beliefs.beliefs = data.get("beliefs", {})
            bdi.beliefs.confidence = data.get("confidence", {})
            bdi.desires.desires = data.get("desires", {})
            bdi.intentions.intentions = data.get("intentions", [])
            
            return bdi
        except:
            return None


# Convenience function for quick BDI setup
def create_bdi_for_task(task: str, context: Dict = None) -> BDIModel:
    """Create a BDI model pre-populated for a task."""
    bdi = BDIModel()
    
    # Add context as beliefs
    if context:
        for key, value in context.items():
            bdi.believe(key, value, confidence=0.9, source="provided")
    
    # Main task as top desire
    bdi.desire(task, priority=1.0)
    
    # Default intentions based on task type
    task_lower = task.lower()
    
    if "fix" in task_lower or "bug" in task_lower:
        bdi.intend("Understand the problem", "Read relevant code")
        bdi.intend("Identify root cause", "Debug/analyze")
        bdi.intend("Implement fix", "Make changes")
        bdi.intend("Verify fix works", "Test solution")
    elif "create" in task_lower or "build" in task_lower:
        bdi.intend("Understand requirements", "Clarify what to build")
        bdi.intend("Design approach", "Plan implementation")
        bdi.intend("Implement", "Write code")
        bdi.intend("Test", "Verify works")
    elif "search" in task_lower or "find" in task_lower:
        bdi.intend("Clarify search", "What exactly to find")
        bdi.intend("Search", "Execute search")
        bdi.intend("Analyze results", "Review findings")
        bdi.intend("Report", "Summarize results")
    else:
        bdi.intend("Understand task", "Read and analyze")
        bdi.intend("Execute", "Do the work")
        bdi.intend("Verify", "Check completion")
    
    return bdi


if __name__ == "__main__":
    # Test BDI model
    print("Testing BDI Model")
    print("=" * 50)
    
    bdi = create_bdi_for_task(
        "Fix the authentication bug in login.py",
        context={
            "file": "login.py",
            "error": "401 Unauthorized on valid credentials"
        }
    )
    
    print(bdi.to_prompt())
    
    # Commit to first intention
    bdi.commit(0)
    print("\nCommitted to first intention")
    print(bdi.intentions.to_prompt_block())
    
    # Complete it
    bdi.complete("Read login.py - found auth logic", success=True)
    print("\nCompleted first intention")
    print(bdi.intentions.to_prompt_block())
