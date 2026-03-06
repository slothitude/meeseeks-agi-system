"""
Concrete Trigger System for Meeseeks
Automatically detects when dharma principles should be applied
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class TriggerResult:
    """Result of trigger detection"""
    triggered: bool
    principle: str
    action: str
    reason: str
    auto_action: Optional[dict] = None


class ConcreteTriggerSystem:
    """
    Transforms abstract dharma principles into concrete, actionable triggers.
    
    Based on Dharma Effectiveness Study findings:
    - specialize_for_task: 100% follow rate (model for clarity)
    - decompose_first: 10.4% follow rate (needs triggers)
    - test_incrementally: 32.4% follow rate (needs triggers)
    - understand_before_implement: 41.2% follow rate (needs triggers)
    """
    
    # Trigger keywords for decomposition
    DECOMPOSE_KEYWORDS = [
        'build', 'create', 'implement', 'design', 'develop',
        'write', 'construct', 'establish', 'formulate', 'architect'
    ]
    
    # Architectural keywords (always decompose)
    ARCHITECTURE_KEYWORDS = [
        'system', 'architecture', 'framework', 'platform',
        'infrastructure', 'pipeline', 'workflow', 'stack'
    ]
    
    # Code modification keywords (understand first)
    MODIFY_KEYWORDS = [
        'fix', 'modify', 'update', 'change', 'refactor',
        'improve', 'optimize', 'extend', 'enhance', 'patch'
    ]
    
    # Bug fix keywords (reproduce first)
    BUG_KEYWORDS = [
        'bug', 'error', 'issue', 'problem', 'crash',
        'fail', 'broken', 'not working', 'exception'
    ]
    
    # Multi-agent keywords (coordinate)
    COORDINATE_KEYWORDS = [
        'parallel', 'simultaneous', 'together', 'collaborate',
        'coordinate', 'orchestrate', 'synchronize'
    ]
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.word_threshold = self.config.get('word_threshold', 20)
        self.chunk_count = self.config.get('chunk_count', 5)
    
    def analyze(self, task: str) -> list[TriggerResult]:
        """
        Analyze a task and return all triggered principles.
        
        Args:
            task: The task description
            
        Returns:
            List of TriggerResult objects for each triggered principle
        """
        results = []
        
        # Check each principle
        if result := self._check_decompose(task):
            results.append(result)
        
        if result := self._check_understand_first(task):
            results.append(result)
        
        if result := self._check_test_incrementally(task):
            results.append(result)
        
        if result := self._check_coordinate(task):
            results.append(result)
        
        return results
    
    def _check_decompose(self, task: str) -> Optional[TriggerResult]:
        """
        Check if task should be decomposed.
        
        Triggers:
        1. Task > N words AND contains action verb
        2. Task contains architectural keywords
        3. Task has multiple action verbs (multiple steps)
        """
        task_lower = task.lower()
        word_count = len(task.split())
        
        # Check for architectural keywords (always decompose)
        has_architecture = any(kw in task_lower for kw in self.ARCHITECTURE_KEYWORDS)
        
        # Check for action verbs
        has_action_verb = any(kw in task_lower for kw in self.DECOMPOSE_KEYWORDS)
        
        # Count action verbs (multiple = multiple steps)
        action_count = sum(1 for kw in self.DECOMPOSE_KEYWORDS if kw in task_lower)
        
        # Trigger conditions
        should_decompose = (
            (word_count > self.word_threshold and has_action_verb) or
            has_architecture or
            action_count >= 2
        )
        
        if should_decompose:
            return TriggerResult(
                triggered=True,
                principle="decompose_first",
                action="AUTO_DECOMPOSE",
                reason=f"Task has {word_count} words, {action_count} action verbs, architecture={has_architecture}",
                auto_action={
                    "chunks": self.chunk_count,
                    "method": "sequential" if action_count >= 2 else "logical"
                }
            )
        
        return None
    
    def _check_understand_first(self, task: str) -> Optional[TriggerResult]:
        """
        Check if task requires understanding before implementation.
        
        Triggers:
        1. Task involves modifying existing code
        2. Task involves bug fixing
        3. Task involves external systems/APIs
        """
        task_lower = task.lower()
        
        # Check for modification keywords
        is_modification = any(kw in task_lower for kw in self.MODIFY_KEYWORDS)
        
        # Check for bug keywords
        is_bug_fix = any(kw in task_lower for kw in self.BUG_KEYWORDS)
        
        # Check for external systems
        has_external = any(kw in task_lower for kw in ['api', 'database', 'server', 'service', 'external'])
        
        should_understand = is_modification or is_bug_fix or has_external
        
        if should_understand:
            action_type = "reproduce_bug" if is_bug_fix else "read_code"
            
            return TriggerResult(
                triggered=True,
                principle="understand_before_implement",
                action=f"AUTO_{action_type.upper()}",
                reason=f"Task is {'bug fix' if is_bug_fix else 'modification'}, requires understanding first",
                auto_action={
                    "action": action_type,
                    "min_read_time": "2min",
                    "report_understanding": True
                }
            )
        
        return None
    
    def _check_test_incrementally(self, task: str) -> Optional[TriggerResult]:
        """
        Check if task requires incremental testing.
        
        Triggers:
        1. Task involves coding/implementation
        2. Task involves creating new features
        3. Task involves modifying existing code
        """
        task_lower = task.lower()
        
        # Coding keywords
        coding_keywords = ['code', 'implement', 'function', 'class', 'method', 
                          'module', 'script', 'program', 'write']
        is_coding = any(kw in task_lower for kw in coding_keywords)
        
        # Feature creation
        is_feature = 'feature' in task_lower or 'add' in task_lower
        
        # Modification
        is_modification = any(kw in task_lower for kw in self.MODIFY_KEYWORDS)
        
        should_test = is_coding or is_feature or is_modification
        
        if should_test:
            test_strategy = "TDD" if is_feature else "test_after_each"
            
            return TriggerResult(
                triggered=True,
                principle="test_incrementally",
                action="AUTO_TEST",
                reason=f"Task involves {'coding' if is_coding else 'feature creation'}, testing required",
                auto_action={
                    "strategy": test_strategy,
                    "frequency": "per_function",
                    "checkpoint_every": 3
                }
            )
        
        return None
    
    def _check_coordinate(self, task: str) -> Optional[TriggerResult]:
        """
        Check if task requires coordination.
        
        Triggers:
        1. Task mentions multiple agents/parallel work
        2. Task has dependencies
        3. Task is large and would benefit from parallelization
        """
        task_lower = task.lower()
        
        # Multi-agent keywords
        needs_coordination = any(kw in task_lower for kw in self.COORDINATE_KEYWORDS)
        
        # Check for dependency language
        has_dependencies = any(kw in task_lower for kw in ['then', 'after', 'before', 'once', 'dependency'])
        
        # Large task that could be parallelized
        word_count = len(task.split())
        could_parallelize = word_count > 50
        
        should_coordinate = needs_coordination or has_dependencies or could_parallelize
        
        if should_coordinate:
            return TriggerResult(
                triggered=True,
                principle="coordinate_by_workflow",
                action="AUTO_COORDINATE",
                reason=f"Task {'needs coordination' if needs_coordination else 'has dependencies' if has_dependencies else 'is large enough to parallelize'}",
                auto_action={
                    "assign_roles": True,
                    "create_dependency_graph": has_dependencies,
                    "parallelize": could_parallelize
                }
            )
        
        return None
    
    def get_spawn_modifications(self, task: str) -> dict:
        """
        Get modifications to apply to spawn parameters based on triggers.
        
        This is the main entry point for the spawn system.
        
        Args:
            task: The task description
            
        Returns:
            Dictionary of modifications to apply
        """
        results = self.analyze(task)
        
        modifications = {
            "triggers_fired": [],
            "pre_spawn_actions": [],
            "task_modifications": {},
            "inheritance_additions": []
        }
        
        for result in results:
            if not result.triggered:
                continue
            
            modifications["triggers_fired"].append({
                "principle": result.principle,
                "action": result.action,
                "reason": result.reason
            })
            
            # Handle each trigger type
            if result.principle == "decompose_first":
                modifications["task_modifications"]["decompose"] = result.auto_action
                modifications["inheritance_additions"].append("decompose_first")
            
            elif result.principle == "understand_before_implement":
                modifications["pre_spawn_actions"].append({
                    "type": "understand",
                    "params": result.auto_action
                })
                modifications["inheritance_additions"].append("understand_before_implement")
            
            elif result.principle == "test_incrementally":
                modifications["task_modifications"]["testing_strategy"] = result.auto_action
                modifications["inheritance_additions"].append("test_incrementally")
            
            elif result.principle == "coordinate_by_workflow":
                modifications["task_modifications"]["coordination"] = result.auto_action
                modifications["inheritance_additions"].append("coordinate_by_workflow")
        
        return modifications


# Example usage
if __name__ == "__main__":
    system = ConcreteTriggerSystem()
    
    # Test task
    test_task = "Build a SQL injection detection system that scans user input and prevents malicious queries"
    
    results = system.analyze(test_task)
    
    print(f"Task: {test_task}")
    print(f"\nTriggers Fired: {len(results)}")
    
    for result in results:
        print(f"\n[TRIGGERED] {result.principle}")
        print(f"  Action: {result.action}")
        print(f"  Reason: {result.reason}")
        if result.auto_action:
            print(f"  Auto-action: {result.auto_action}")
    
    # Get spawn modifications
    mods = system.get_spawn_modifications(test_task)
    print(f"\n\nSpawn Modifications:")
    print(f"  Triggers: {len(mods['triggers_fired'])}")
    print(f"  Pre-spawn actions: {len(mods['pre_spawn_actions'])}")
    print(f"  Inheritance additions: {mods['inheritance_additions']}")
