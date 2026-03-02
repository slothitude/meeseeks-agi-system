#!/usr/bin/env python3
"""
AGI Integration - Combines all AGI patterns into unified system.

Patterns:
1. BDI (Beliefs-Desires-Intentions) - Goal-directed reasoning
2. Global Workspace - Consciousness/attention mechanism  
3. HTN (Hierarchical Task Networks) - Task decomposition
4. Memory-Prediction - Learning from prediction errors
5. Society of Mind - Multi-agent coordination

Usage:
    agi = AGISystem()
    
    # Initialize with task
    agi.initialize("Fix the authentication bug")
    
    # Get full cognitive state
    state = agi.get_cognitive_state()
    
    # Execute with AGI patterns
    result = agi.execute()
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from bdi_model import BDIModel, create_bdi_for_task
from global_workspace import GlobalWorkspace, create_workspace_for_task, ModuleType
from htn_planner import HTNPlanner, create_planner_for_task, auto_decompose
from memory_prediction import MemoryPredictionSystem, create_predictions_for_task
from society_of_mind import SocietyOfMind, AgentRole


class AGISystem:
    """
    Unified AGI system combining all cognitive patterns.
    
    This integrates:
    - BDI for goal-directed behavior
    - Global Workspace for attention/consciousness
    - HTN for task decomposition
    - Memory-Prediction for learning
    - Society of Mind for multi-agent coordination
    """
    
    def __init__(self, session_key: str = None):
        self.session_key = session_key
        
        # Initialize all subsystems
        self.bdi = BDIModel(session_key)
        self.workspace = GlobalWorkspace()
        self.planner = HTNPlanner()
        self.predictions = MemoryPredictionSystem(session_key)
        self.society = SocietyOfMind(session_key)
        
        self.initialized = False
        self.current_task = ""
    
    def initialize(self, task: str, context: Dict = None):
        """
        Initialize all AGI subsystems for a task.
        
        This sets up:
        - BDI with beliefs about context and desires for goal
        - Workspace with task and context
        - HTN plan decomposition
        - Predictions about outcomes
        - Society agent activation
        """
        self.current_task = task
        context = context or {}
        
        # 1. Setup BDI
        self.bdi = create_bdi_for_task(task, context)
        
        # 2. Setup Global Workspace
        self.workspace = create_workspace_for_task(task, context)
        
        # 3. Setup HTN Planner
        self.planner = create_planner_for_task(task)
        decomposition = auto_decompose(task)
        
        # Add decomposition as intentions in BDI
        for step in decomposition:
            self.bdi.intend(step)
        
        # 4. Setup Predictions
        self.predictions = create_predictions_for_task(task)
        
        # 5. Setup Society
        self.society.submit_task(task)
        self.society.coordinate()
        
        # Broadcast initialization to workspace
        self.workspace.add_content(
            f"AGI System initialized for: {task}",
            activation=0.9,
            module=ModuleType.PLANNING
        )
        
        # Add decomposition to workspace
        self.workspace.add_content(
            f"Plan: {' -> '.join(decomposition)}",
            activation=0.8,
            module=ModuleType.PLANNING
        )
        
        # Compete for attention
        self.workspace.compete()
        self.workspace.broadcast()
        
        self.initialized = True
    
    def step(self, action: str, result: str, success: bool = True):
        """
        Record a step in execution.
        
        Updates all subsystems with action result.
        """
        # Update BDI
        self.bdi.complete(result, success)
        
        # Update Workspace
        self.workspace.add_content(
            f"Action: {action} -> {result}",
            activation=0.7 if success else 0.9,  # Failures get more attention
            module=ModuleType.MOTOR
        )
        
        # Update Predictions
        self.predictions.observe(result)
        
        # Compete and broadcast
        self.workspace.compete()
        self.workspace.broadcast()
    
    def predict_next(self, prediction: str, confidence: float = 0.5):
        """Add a prediction about what will happen next."""
        self.predictions.predict(prediction, confidence)
    
    def get_cognitive_state(self) -> Dict:
        """Get full cognitive state across all subsystems."""
        return {
            "task": self.current_task,
            "bdi": {
                "beliefs": self.bdi.beliefs.beliefs,
                "top_desire": self.bdi.desires.get_top_desire(),
                "current_intention": self.bdi.intentions.current_intention,
                "committed": self.bdi.intentions.committed
            },
            "workspace": {
                "conscious": self.workspace.get_conscious_content(),
                "broadcasts": len(self.workspace.broadcast_history)
            },
            "planner": {
                "plan": self.bdi.intentions.get_plan()
            },
            "predictions": {
                "accuracy": self.predictions.get_accuracy(),
                "total": len(self.predictions.predictions)
            },
            "society": {
                "active_agents": [a.name for a in self.society.active_agents],
                "recommended_agency": self.society.recommend_agency().name if self.society.recommend_agency() else None
            }
        }
    
    def to_unified_prompt(self) -> str:
        """
        Generate unified prompt block combining all AGI patterns.
        
        This is what gets injected into a Meeseeks prompt.
        """
        lines = [
            "# 🧠 AGI Cognitive State",
            "",
            "This Meeseeks is running with advanced AGI patterns.",
            "",
            self.bdi.to_prompt(),
            "",
            self.workspace.to_prompt_block(),
            "",
            self.bdi.intentions.to_prompt_block(),  # HTN decomposition is in intentions
            "",
            self.predictions.to_prompt_block(),
            "",
            self.society.to_prompt_block()
        ]
        
        return "\n".join([l for l in lines if l])
    
    def evaluate_and_learn(self) -> Dict:
        """
        Evaluate predictions and extract lessons.
        
        Call this at the end of execution.
        """
        # Evaluate predictions
        pred_results = self.predictions.evaluate()
        lessons = self.predictions.extract_lessons()
        
        # Save all state
        self.bdi.save()
        self.predictions.save()
        self.society.save()
        
        return {
            "prediction_accuracy": self.predictions.get_accuracy(),
            "lessons": lessons,
            "total_broadcasts": len(self.workspace.broadcast_history),
            "final_state": self.get_cognitive_state()
        }
    
    def save_all(self):
        """Save all subsystem states."""
        self.bdi.save()
        self.predictions.save()
        self.society.save()


def create_agi_for_task(task: str, context: Dict = None, session_key: str = None) -> AGISystem:
    """
    Create and initialize an AGI system for a task.
    
    This is the main entry point for using AGI patterns.
    """
    agi = AGISystem(session_key)
    agi.initialize(task, context)
    return agi


if __name__ == "__main__":
    # Test AGI Integration
    print("Testing AGI Integration")
    print("=" * 60)
    
    # Create AGI system
    agi = create_agi_for_task(
        "Fix the authentication bug in login.py",
        context={
            "file": "login.py",
            "error": "401 Unauthorized on valid credentials"
        },
        session_key="test-session-001"
    )
    
    # Show cognitive state
    print("\nCognitive State:")
    state = agi.get_cognitive_state()
    print(f"  Task: {state['task']}")
    print(f"  Top Desire: {state['bdi']['top_desire']}")
    print(f"  Plan: {state['planner']['plan']}")
    print(f"  Conscious: {state['workspace']['conscious']}")
    print(f"  Active Agents: {state['society']['active_agents']}")
    
    # Simulate execution
    print("\nSimulating execution...")
    agi.predict_next("Will find bug in token validation", confidence=0.7)
    agi.step("Read login.py", "Found auth logic and token validation")
    
    agi.predict_next("Bug will be in expiration check", confidence=0.8)
    agi.step("Analyze code", "Bug found: expiration check inverted")
    
    agi.step("Fix bug", "Corrected expiration logic")
    agi.step("Test fix", "Tests pass")
    
    # Evaluate and learn
    print("\nEvaluating...")
    results = agi.evaluate_and_learn()
    print(f"  Prediction Accuracy: {results['prediction_accuracy']:.1%}")
    print(f"  Lessons: {len(results['lessons'])}")
    print(f"  Total Broadcasts: {results['total_broadcasts']}")
    
    # Generate unified prompt
    with open('test_agi_unified.md', 'w', encoding='utf-8') as f:
        f.write(agi.to_unified_prompt())
    print("\nWrote test_agi_unified.md")
