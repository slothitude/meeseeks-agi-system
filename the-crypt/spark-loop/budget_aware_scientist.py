#!/usr/bin/env python3
"""
BUDGET-AWARE GENETIC MAD SCIENTIST

Uses:
- GLM-5 (paid) for execution only
- ministral-3 (free) for routing/scoring

Budget: 400 GLM-5 requests per 5 hours
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fast_mini_meeseeks import FastMiniMeeseeks, FastResult
    MINI_AVAILABLE = True
except ImportError:
    MINI_AVAILABLE = False


@dataclass
class GLMBudget:
    """Track GLM-5 usage to stay under limit."""
    limit: int = 400
    window_hours: int = 5
    requests: List[float] = field(default_factory=list)
    
    def can_use(self, count: int = 1) -> bool:
        """Check if we have budget remaining."""
        cutoff = time.time() - (self.window_hours * 3600)
        self.requests = [r for r in self.requests if r > cutoff]
        return len(self.requests) + count <= self.limit
    
    def use(self, count: int = 1):
        """Record GLM-5 requests."""
        for _ in range(count):
            self.requests.append(time.time())
    
    def remaining(self) -> int:
        """Get remaining requests."""
        cutoff = time.time() - (self.window_hours * 3600)
        self.requests = [r for r in self.requests if r > cutoff]
        return self.limit - len(self.requests)
    
    def status(self) -> Dict:
        """Get budget status."""
        return {
            "limit": self.limit,
            "used": len(self.requests),
            "remaining": self.remaining(),
            "window_hours": self.window_hours
        }


@dataclass
class TaskPlan:
    """Execution plan for a task."""
    task: str
    complexity: str
    approach: str
    glm_requests_needed: int
    can_execute: bool
    reason: str


class BudgetAwareScientist:
    """
    Genetic mad scientist that respects GLM-5 budget.
    
    Strategy:
    1. Classify with ministral-3 (FREE)
    2. Check budget
    3. Execute with GLM-5 (PAID) or ministral-3 (FREE fallback)
    4. Evaluate with ministral-3 (FREE)
    """
    
    def __init__(self, mini_model: str = "ministral-3"):
        self.budget = GLMBudget()
        self.mini = FastMiniMeeseeks(mini_model) if MINI_AVAILABLE else None
        
    def plan_task(self, task: str) -> TaskPlan:
        """
        Plan how to execute a task.
        Uses FREE ministral-3 for classification.
        """
        # Classify with mini model (FREE)
        if self.mini:
            classification = self.mini.classify(task)
            complexity = classification.output.get("complexity", "moderate")
        else:
            complexity = "moderate"  # Default
        
        # Determine GLM-5 requests needed
        requests_map = {
            "simple": 1,      # Direct solve
            "moderate": 2,    # 2 helpers
            "complex": 3      # Full genetic (alpha, beta, gamma)
        }
        
        glm_needed = requests_map.get(complexity, 2)
        can_execute = self.budget.can_use(glm_needed)
        
        if can_execute:
            approach = "glm-5"
            reason = f"Using {glm_needed} GLM-5 request(s)"
        else:
            approach = "ministral-3"
            reason = f"GLM-5 budget exhausted, using local model"
            glm_needed = 0
            can_execute = True  # Can still execute with mini
        
        return TaskPlan(
            task=task,
            complexity=complexity,
            approach=approach,
            glm_requests_needed=glm_needed,
            can_execute=can_execute,
            reason=reason
        )
    
    def execute_with_budget(self, task: str, plan: TaskPlan) -> Dict:
        """
        Execute task respecting budget.
        """
        result = {
            "task": task,
            "complexity": plan.complexity,
            "approach": plan.approach,
            "glm_used": 0,
            "budget_remaining": self.budget.remaining()
        }
        
        if plan.approach == "glm-5" and plan.can_execute:
            # Use GLM-5 for execution
            # This would call sessions_spawn with GLM-5
            self.budget.use(plan.glm_requests_needed)
            result["glm_used"] = plan.glm_requests_needed
            result["execution"] = "GLM-5 (paid)"
            result["budget_remaining"] = self.budget.remaining()
            
        else:
            # Fallback to ministral-3
            result["execution"] = "ministral-3 (free)"
            result["glm_used"] = 0
        
        return result
    
    def solve(self, task: str) -> Dict:
        """
        Full solve workflow with budget awareness.
        """
        # 1. Plan (FREE)
        plan = self.plan_task(task)
        
        # 2. Execute (PAID or FREE)
        result = self.execute_with_budget(task, plan)
        
        # 3. Evaluate (FREE)
        if self.mini and "execution" in result:
            fitness = self.mini.fitness(task, str(result))
            result["fitness"] = fitness.output
            result["fitness_time_ms"] = fitness.elapsed_ms
        
        return result
    
    def status(self) -> Dict:
        """Get current status."""
        return {
            "budget": self.budget.status(),
            "mini_available": MINI_AVAILABLE
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Budget-Aware Genetic Scientist")
    parser.add_argument("task", nargs="?", default="Fix the API bug")
    parser.add_argument("--status", "-s", action="store_true", help="Show budget status")
    parser.add_argument("--plan", "-p", action="store_true", help="Plan task without executing")
    parser.add_argument("--model", "-m", default="ministral-3", help="Mini model")
    
    args = parser.parse_args()
    
    scientist = BudgetAwareScientist(args.model)
    
    if args.status:
        status = scientist.status()
        print("\n💰 GLM-5 BUDGET STATUS\n")
        print(f"Limit: {status['budget']['limit']} requests per {status['budget']['window_hours']} hours")
        print(f"Used: {status['budget']['used']}")
        print(f"Remaining: {status['budget']['remaining']}")
        print(f"Mini Available: {status['mini_available']}")
        return
    
    if args.plan:
        plan = scientist.plan_task(args.task)
        print(f"\n📋 TASK PLAN\n")
        print(f"Task: {plan.task}")
        print(f"Complexity: {plan.complexity}")
        print(f"Approach: {plan.approach}")
        print(f"GLM-5 Requests: {plan.glm_requests_needed}")
        print(f"Can Execute: {plan.can_execute}")
        print(f"Reason: {plan.reason}")
        return
    
    # Full solve
    result = scientist.solve(args.task)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
