"""
the_body - Fast Action Executor for Meeseeks AGI

SPEED IS THE POINT.

Architecture:
    Meeseeks → TheBody.call_tool() 
                    ↓
             [O(1) Cache Lookup]
                    ↓
         ┌─────────┴─────────┐
         ↓                   ↓
    SKILL HIT            SKILL MISS
    (direct exec)     (passthrough)
    <10ms              OpenClaw
         
Performance Targets:
- Skill execution: <10ms
- Cache lookup: O(1)
- No reasoning in fast path
- No API calls in fast path
- 10x+ faster than OpenClaw for cached patterns
"""

from .cache import SkillsCache
from .intercept import TheBody
from .distress import DistressSignal, DistressTracker

__version__ = "0.2.0"
__all__ = ["TheBody", "SkillsCache", "DistressSignal", "DistressTracker"]

# Performance constants
TARGET_SKILL_TIME_MS = 10.0
SPEED_IMPROVEMENT_FACTOR = 10.0
