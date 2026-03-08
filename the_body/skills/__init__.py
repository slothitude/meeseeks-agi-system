"""
Pre-compiled skill callables for direct execution.

Each skill:
1. Has a match() function for O(1) pattern detection
2. Has an execute() function that runs DIRECTLY (no OpenClaw)
3. Executes in <10ms
4. Returns actual results, not passthrough markers
"""

from .count import SkillCount
from .find import SkillFind
from .read import SkillRead
from .ls import SkillLs
from .format import SkillFormat

__all__ = ["SkillCount", "SkillFind", "SkillRead", "SkillLs", "SkillFormat"]
