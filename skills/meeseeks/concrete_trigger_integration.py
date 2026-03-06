"""
Integrate concrete triggers into spawn_meeseeks.py

This patches the spawn system to automatically apply dharma principles
based on task content analysis.
"""

import sys
from pathlib import Path

# Add the skills directory to path
sys.path.insert(0, str(Path(__file__).parent / "skills" / "meeseeks"))

from concrete_triggers import ConcreteTriggerSystem, TriggerResult

def integrate_triggers():
    """
    Integration point for concrete triggers in spawn pipeline.
    
    This would be called in spawn_meeseeks.py before spawning:
    
    from concrete_trigger_integration import apply_triggers_to_task
    
    def spawn_prompt(task, ...):
        # Apply concrete triggers first
        modifications = apply_triggers_to_task(task)
        
        if modifications.get("decompose"):
            # Spawn chunks instead
            return spawn_chunks(task, modifications["decompose"]["chunks"])
        
        # Continue with normal spawn...
    """
    pass

def apply_triggers_to_task(task: str, config: dict = None) -> dict:
    """
    Analyze task and return spawn modifications.
    
    Args:
        task: The task description
        config: Optional configuration for trigger thresholds
        
    Returns:
        Dictionary of modifications to apply to spawn
    """
    system = ConcreteTriggerSystem(config)
    return system.get_spawn_modifications(task)

def should_decompose_task(task: str) -> bool:
    """Quick check if task should be decomposed"""
    system = ConcreteTriggerSystem()
    results = system.analyze(task)
    
    for result in results:
        if result.principle == "decompose_first" and result.triggered:
            return True
    return False

def get_task_triggers(task: str) -> list:
    """Get list of triggered principles for a task"""
    system = ConcreteTriggerSystem()
    results = system.analyze(task)
    return [(r.principle, r.reason) for r in results if r.triggered]

# Example integration
if __name__ == "__main__":
    test_tasks = [
        "Build a SQL injection detection system",
        "Fix the authentication bug in login.php",
        "Count the principles in dharma.md",
        "Design and implement a complete authentication system with OAuth2 support"
    ]
    
    print("=== Concrete Trigger Integration ===\n")
    
    for task in test_tasks:
        print(f"Task: {task[:60]}...")
        
        # Check triggers
        triggers = get_task_triggers(task)
        print(f"Triggers: {len(triggers)}")
        for principle, reason in triggers:
            print(f"  - {principle}: {reason[:50]}...")
        
        # Check decomposition
        should_decomp = should_decompose_task(task)
        print(f"Should decompose: {should_decomp}")
        print()
