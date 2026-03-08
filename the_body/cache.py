"""
Skills Cache - O(1) lookup for pre-compiled skills.

Cache structure:
    SKILL_REGISTRY = {
        "exec": [SkillCount, SkillFind, SkillLs, SkillFormat],
        "read": [SkillRead],
    }

Lookup is O(1) for tool name, then O(n) for skill matching where n is small (5-10 skills).
Target: <1ms for cache lookup.
"""

import time
from typing import Any, Dict, Optional, Callable, Tuple
from dataclasses import dataclass

from .skills import SkillCount, SkillFind, SkillRead, SkillLs, SkillFormat


@dataclass
class CacheStats:
    """Cache performance statistics."""
    lookups: int = 0
    hits: int = 0
    misses: int = 0
    total_lookup_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        return self.hits / self.lookups if self.lookups > 0 else 0.0
    
    @property
    def avg_lookup_time_ms(self) -> float:
        return self.total_lookup_time_ms / self.lookups if self.lookups > 0 else 0.0


class SkillsCache:
    """
    O(1) skill lookup cache.
    
    Skills are indexed by tool name for fast initial lookup,
    then pattern-matched in sequence (typically 1-5 checks).
    
    Usage:
        cache = SkillsCache()
        skill, params = cache.lookup("exec", {"command": "ls -la"})
        if skill:
            result = skill.execute(...)
    """
    
    # Pre-compiled skill registry - built once at import time
    SKILL_REGISTRY: Dict[str, list] = {
        "exec": [SkillLs, SkillCount, SkillFind, SkillFormat],
        "read": [SkillRead],
    }
    
    def __init__(self):
        """Initialize cache with stats tracking."""
        self.stats = CacheStats()
    
    def lookup(self, tool_name: str, args: Dict[str, Any]) -> Tuple[Optional[Any], Optional[Dict]]:
        """
        Look up a skill for the given tool call.
        
        O(1) dict lookup + O(n) pattern match where n is small.
        
        Args:
            tool_name: Name of the tool being called
            args: Arguments passed to the tool
            
        Returns:
            (skill_class, match_params) if match found
            (None, None) if no match
        """
        start = time.perf_counter()
        self.stats.lookups += 1
        
        # O(1) tool lookup
        skills = self.SKILL_REGISTRY.get(tool_name)
        if not skills:
            self.stats.misses += 1
            self.stats.total_lookup_time_ms += (time.perf_counter() - start) * 1000
            return None, None
        
        # O(n) pattern match - n is typically 1-5
        for skill_cls in skills:
            match = skill_cls.match(tool_name, args)
            if match.matched:
                self.stats.hits += 1
                self.stats.total_lookup_time_ms += (time.perf_counter() - start) * 1000
                return skill_cls, match.params
        
        self.stats.misses += 1
        self.stats.total_lookup_time_ms += (time.perf_counter() - start) * 1000
        return None, None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "lookups": self.stats.lookups,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "hit_rate": f"{self.stats.hit_rate:.1%}",
            "avg_lookup_time_ms": f"{self.stats.avg_lookup_time_ms:.3f}",
            "total_lookup_time_ms": f"{self.stats.total_lookup_time_ms:.3f}",
        }
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = CacheStats()
