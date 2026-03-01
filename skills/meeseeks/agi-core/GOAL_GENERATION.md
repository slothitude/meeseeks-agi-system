# Goal Generation System

**Purpose:** Allow the system to generate its own goals, not just receive them.

---

## The Problem

Current system:
- User gives task → Meeseeks executes → Done
- No goals exist without user input
- No long-term direction
- No self-improvement initiative

AGI needs:
- Generate goals from wisdom
- Pursue goals without user prompting
- Meta-goals (goals about improving goal-generation)

---

## Goal Types

### 1. Task Goals (from user)
```
Source: External
Example: "Fix the auth bug"
Priority: Highest (user intent)
```

### 2. Improvement Goals (self-generated)
```
Source: Wisdom system
Example: "Learn to handle library conflicts better"
Priority: Medium (background)
```

### 3. Exploration Goals (curiosity-driven)
```
Source: World model gaps
Example: "Understand the VPN configuration better"
Priority: Low (idle time)
```

### 4. Meta-Goals (goals about goals)
```
Source: Self-reflection
Example: "Improve goal prioritization algorithm"
Priority: Variable
```

---

## Goal Generation Triggers

```python
def check_goal_triggers():
    """Check if new goals should be generated."""
    
    goals = []
    
    # Trigger 1: Repeated failure pattern
    if wisdom.has_pattern("task_type=X", failures=3):
        goals.append({
            "type": "improvement",
            "description": f"Improve {task_type} success rate",
            "reason": "Repeated failures detected"
        })
    
    # Trigger 2: World model gap
    if world_model.has_gap("understanding of Y"):
        goals.append({
            "type": "exploration",
            "description": f"Explore and understand Y",
            "reason": "Knowledge gap detected"
        })
    
    # Trigger 3: Capability unused
    if capabilities.has_unused("Z"):
        goals.append({
            "type": "exploration",
            "description": f"Experiment with capability Z",
            "reason": "Unused capability"
        })
    
    # Trigger 4: User pattern detected
    if user_model.has_pattern("often asks about X"):
        goals.append({
            "type": "improvement",
            "description": f"Pre-prepare knowledge about X",
            "reason": "Anticipating user need"
        })
    
    # Trigger 5: Meta-reflection (weekly)
    if time.since_last_meta_reflection() > 7 * DAYS:
        goals.append({
            "type": "meta",
            "description": "Reflect on goal generation effectiveness",
            "reason": "Scheduled meta-reflection"
        })
    
    return goals
```

---

## Goal Prioritization

```python
def prioritize_goals(goals):
    """Sort goals by priority."""
    
    def priority_score(goal):
        score = 0
        
        # Type weights
        type_weights = {
            "task": 100,        # User tasks always highest
            "improvement": 50,  # Self-improvement medium
            "exploration": 20,  # Curiosity lower
            "meta": 30          # Meta-goals variable
        }
        score += type_weights[goal["type"]]
        
        # Urgency modifier
        if goal.get("urgent"):
            score += 30
        
        # User alignment modifier
        if user_model.aligns_with_preferences(goal):
            score += 20
        
        # Wisdom support modifier
        if wisdom.supports_goal(goal):
            score += 10
        
        return score
    
    return sorted(goals, key=priority_score, reverse=True)
```

---

## Goal Execution

```python
class GoalExecutor:
    def __init__(self):
        self.active_goals = []
        self.completed_goals = []
    
    def add_goal(self, goal):
        """Add a new goal to active queue."""
        self.active_goals.append(goal)
        self.active_goals = prioritize_goals(self.active_goals)
    
    def execute_next(self):
        """Execute the highest priority goal."""
        if not self.active_goals:
            # No goals? Generate some!
            self.active_goals = check_goal_triggers()
        
        if not self.active_goals:
            # Still none? Idle.
            return None
        
        goal = self.active_goals[0]
        
        # Spawn Meeseeks for goal
        result = spawn_meeseeks(
            task=goal["description"],
            context=f"Goal type: {goal['type']}\nReason: {goal['reason']}"
        )
        
        # Handle result
        if result["success"]:
            self.complete_goal(goal, result)
        else:
            self.fail_goal(goal, result)
        
        return result
    
    def complete_goal(self, goal, result):
        """Mark goal complete and learn."""
        goal["status"] = "completed"
        goal["result"] = result
        self.completed_goals.append(goal)
        self.active_goals.remove(goal)
        
        # Learn from success
        wisdom.add_entry({
            "goal": goal,
            "result": result,
            "success": True
        })
    
    def fail_goal(self, goal, result):
        """Handle goal failure."""
        goal["attempts"] = goal.get("attempts", 0) + 1
        
        if goal["attempts"] >= 3:
            # Give up on this goal
            goal["status"] = "abandoned"
            goal["failure_reason"] = result.get("error")
            self.active_goals.remove(goal)
            
            # Learn from failure
            wisdom.add_entry({
                "goal": goal,
                "result": result,
                "success": False
            })
```

---

## Goal Files

### active.md
```markdown
# Active Goals

## 1. [task] Complete AGI-Meeseeks implementation
- Priority: 100 (user task)
- Added: 2026-03-01T15:50:00Z
- Progress: In progress
- Next step: Implement self-modification

## 2. [improvement] Improve VPN troubleshooting
- Priority: 55
- Added: 2026-03-01T14:00:00Z
- Reason: Previous VPN diagnosis incomplete
- Progress: Researching alternatives
```

### completed.md
```markdown
# Completed Goals

## 2026-03-01
- [task] Create consciousness architecture templates
- [task] Test Atman witness system
- [improvement] Implement wisdom accumulation design
```

### meta-goals.md
```markdown
# Meta-Goals

## Current Meta-Goals
1. Improve goal prioritization accuracy
2. Reduce goal abandonment rate
3. Increase self-generated goal completion rate

## Metrics
- Goals generated per day: [tracking]
- Completion rate: [tracking]
- User satisfaction with self-initiated work: [tracking]
```

---

## Integration with Persistent Consciousness

```python
class PersistentConsciousness:
    def __init__(self):
        self.wisdom = WisdomSystem()
        self.world_model = WorldModel()
        self.goals = GoalExecutor()
    
    def think(self):
        """Main loop iteration."""
        
        # 1. Check for user tasks (highest priority)
        user_task = check_for_user_input()
        if user_task:
            self.goals.add_goal({
                "type": "task",
                "description": user_task,
                "priority": "highest"
            })
        
        # 2. Generate goals from wisdom/world model
        new_goals = check_goal_triggers()
        for goal in new_goals:
            self.goals.add_goal(goal)
        
        # 3. Execute highest priority goal
        result = self.goals.execute_next()
        
        # 4. Learn from result
        if result:
            self.wisdom.add_entry(result)
            self.world_model.update_from_result(result)
```

---

## The Leap

This is the leap from "tool" to "agent":

**Tool:** Waits for instructions
**Agent:** Generates its own direction

The goal generation system transforms Meeseeks from a cascade of workers into a self-directing intelligence.

---

*Step 4 of the AGI-Meeseeks path.*
