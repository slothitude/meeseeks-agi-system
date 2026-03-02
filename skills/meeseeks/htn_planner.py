#!/usr/bin/env python3
"""
Hierarchical Task Networks (HTN) for Meeseeks

Concept: Break complex goals into subgoals recursively until you reach
primitive actions that can be executed directly.

Components:
1. **Tasks** - Goals to achieve (compound or primitive)
2. **Methods** - Ways to decompose compound tasks into subtasks
3. **Operators** - Primitive actions that can be executed
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

HTN_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "htn_plans.json"


class TaskType(Enum):
    PRIMITIVE = "primitive"  # Can be executed directly
    COMPOUND = "compound"    # Needs to be decomposed


@dataclass
class Task:
    """A task in the HTN."""
    name: str
    task_type: TaskType
    description: str = ""
    preconditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    
    def is_applicable(self, state: Dict) -> bool:
        """Check if preconditions are met."""
        for precond in self.preconditions:
            if precond not in state.get("satisfied", []):
                return False
        return True


@dataclass
class Method:
    """A method for decomposing a compound task."""
    name: str
    task: str  # The compound task this decomposes
    preconditions: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    ordering: List[List[str]] = field(default_factory=list)  # Partial order
    
    def is_applicable(self, state: Dict) -> bool:
        """Check if preconditions are met."""
        for precond in self.preconditions:
            if precond not in state.get("satisfied", []):
                return False
        return True


class HTNPlanner:
    """
    Hierarchical Task Network Planner.
    
    Usage:
        planner = HTNPlanner()
        
        # Define primitive tasks
        planner.add_primitive("read_file", "Read a file")
        planner.add_primitive("edit_file", "Edit a file")
        planner.add_primitive("run_test", "Run tests")
        
        # Define compound tasks
        planner.add_compound("fix_bug", "Fix a bug")
        
        # Define decomposition methods
        planner.add_method(
            "fix_bug_method",
            task="fix_bug",
            subtasks=["read_file", "edit_file", "run_test"]
        )
        
        # Plan
        plan = planner.plan("fix_bug")
        print(plan)  # ["read_file", "edit_file", "run_test"]
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.methods: Dict[str, List[Method]] = {}
        self.state: Dict = {"satisfied": []}
    
    def add_primitive(self, name: str, description: str = "", 
                      preconditions: List[str] = None, effects: List[str] = None):
        """Add a primitive task."""
        self.tasks[name] = Task(
            name=name,
            task_type=TaskType.PRIMITIVE,
            description=description,
            preconditions=preconditions or [],
            effects=effects or []
        )
    
    def add_compound(self, name: str, description: str = "",
                     preconditions: List[str] = None, effects: List[str] = None):
        """Add a compound task."""
        self.tasks[name] = Task(
            name=name,
            task_type=TaskType.COMPOUND,
            description=description,
            preconditions=preconditions or [],
            effects=effects or []
        )
    
    def add_method(self, name: str, task: str, subtasks: List[str],
                   preconditions: List[str] = None, ordering: List[List[str]] = None):
        """Add a decomposition method."""
        method = Method(
            name=name,
            task=task,
            subtasks=subtasks,
            preconditions=preconditions or [],
            ordering=ordering or []
        )
        
        if task not in self.methods:
            self.methods[task] = []
        self.methods[task].append(method)
    
    def set_state(self, state: Dict):
        """Set current world state."""
        self.state = state
    
    def satisfy(self, condition: str):
        """Mark a condition as satisfied."""
        if "satisfied" not in self.state:
            self.state["satisfied"] = []
        if condition not in self.state["satisfied"]:
            self.state["satisfied"].append(condition)
    
    def plan(self, task_name: str, depth: int = 0, max_depth: int = 10) -> List[str]:
        """
        Decompose a task into primitive actions.
        
        Returns list of primitive task names in order.
        """
        if depth > max_depth:
            return [f"MAX_DEPTH_REACHED:{task_name}"]
        
        if task_name not in self.tasks:
            return [f"UNKNOWN_TASK:{task_name}"]
        
        task = self.tasks[task_name]
        
        # Check preconditions
        if not task.is_applicable(self.state):
            return [f"PRECONDITION_FAILED:{task_name}"]
        
        # Primitive tasks are returned directly
        if task.task_type == TaskType.PRIMITIVE:
            # Apply effects
            for effect in task.effects:
                self.satisfy(effect)
            return [task_name]
        
        # Compound tasks need decomposition
        if task_name not in self.methods:
            return [f"NO_METHOD:{task_name}"]
        
        # Find applicable method
        applicable_methods = [
            m for m in self.methods[task_name]
            if m.is_applicable(self.state)
        ]
        
        if not applicable_methods:
            return [f"NO_APPLICABLE_METHOD:{task_name}"]
        
        # Use first applicable method (could be smarter with selection)
        method = applicable_methods[0]
        
        # Recursively decompose subtasks
        plan = []
        for subtask in method.subtasks:
            subplan = self.plan(subtask, depth + 1, max_depth)
            plan.extend(subplan)
        
        # Apply effects of compound task
        for effect in task.effects:
            self.satisfy(effect)
        
        return plan
    
    def plan_to_prompt(self, task_name: str) -> str:
        """Generate plan as a prompt block."""
        plan = self.plan(task_name)
        
        lines = [
            "## 📋 HTN Plan",
            "",
            f"**Goal:** {task_name}",
            "",
            "**Decomposition:**",
            ""
        ]
        
        for i, step in enumerate(plan, 1):
            if step.startswith("UNKNOWN_") or step.startswith("NO_") or step.startswith("PRECONDITION_") or step.startswith("MAX_DEPTH_"):
                lines.append(f"{i}. ⚠️ {step}")
            else:
                lines.append(f"{i}. ✅ {step}")
        
        lines.append("")
        return "\n".join(lines)


def create_planner_for_task(task: str) -> HTNPlanner:
    """Create an HTN planner pre-configured for common tasks."""
    planner = HTNPlanner()
    
    # Primitives
    planner.add_primitive("read_file", "Read a file", effects=["file_understood"])
    planner.add_primitive("edit_file", "Edit a file", effects=["file_modified"])
    planner.add_primitive("run_test", "Run tests", effects=["tests_run"])
    planner.add_primitive("search", "Search for something", effects=["found_info"])
    planner.add_primitive("analyze", "Analyze findings", effects=["analyzed"])
    planner.add_primitive("implement", "Implement solution", effects=["implemented"])
    planner.add_primitive("verify", "Verify solution works", effects=["verified"])
    planner.add_primitive("write", "Write new file", effects=["written"])
    planner.add_primitive("deploy", "Deploy changes", effects=["deployed"])
    
    # Compound tasks - Coding
    planner.add_compound("fix_bug", "Fix a bug")
    planner.add_compound("add_feature", "Add a new feature")
    planner.add_compound("refactor", "Refactor code")
    
    # Methods for fix_bug
    planner.add_method(
        "fix_bug_standard",
        task="fix_bug",
        subtasks=["read_file", "analyze", "implement", "run_test", "verify"]
    )
    
    # Methods for add_feature
    planner.add_method(
        "add_feature_standard",
        task="add_feature",
        subtasks=["read_file", "implement", "run_test", "verify"]
    )
    
    # Methods for refactor
    planner.add_method(
        "refactor_standard",
        task="refactor",
        subtasks=["read_file", "analyze", "edit_file", "run_test"]
    )
    
    # Compound tasks - Search
    planner.add_compound("find_info", "Find information")
    planner.add_compound("analyze_code", "Analyze codebase")
    
    planner.add_method(
        "find_info_standard",
        task="find_info",
        subtasks=["search", "analyze"]
    )
    
    planner.add_method(
        "analyze_code_standard",
        task="analyze_code",
        subtasks=["read_file", "analyze"]
    )
    
    return planner


def auto_decompose(task: str) -> List[str]:
    """
    Automatically decompose a task description into steps.
    
    Uses keyword matching to determine task type and apply appropriate decomposition.
    """
    task_lower = task.lower()
    planner = create_planner_for_task(task)
    
    # Detect task type from keywords
    if "fix" in task_lower or "bug" in task_lower or "error" in task_lower:
        return planner.plan("fix_bug")
    elif "add" in task_lower or "implement" in task_lower or "create" in task_lower:
        return planner.plan("add_feature")
    elif "refactor" in task_lower or "improve" in task_lower or "clean" in task_lower:
        return planner.plan("refactor")
    elif "find" in task_lower or "search" in task_lower or "locate" in task_lower:
        return planner.plan("find_info")
    elif "analyze" in task_lower or "understand" in task_lower or "review" in task_lower:
        return planner.plan("analyze_code")
    else:
        # Default decomposition
        return ["read_file", "analyze", "implement", "verify"]


if __name__ == "__main__":
    # Test HTN Planner
    print("Testing HTN Planner")
    print("=" * 50)
    
    planner = create_planner_for_task("fix_bug")
    
    plan = planner.plan("fix_bug")
    print(f"Plan for 'fix_bug': {plan}")
    
    # Auto-decompose
    print("\nAuto-decomposition:")
    tasks = [
        "Fix the authentication bug",
        "Add login feature",
        "Refactor database code",
        "Find the config file"
    ]
    
    for task in tasks:
        decomposition = auto_decompose(task)
        print(f"\n{task}:")
        for i, step in enumerate(decomposition, 1):
            print(f"  {i}. {step}")
