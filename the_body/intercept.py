"""
Intercept Layer - Thin wrapper for skill execution.

MINIMAL OVERHEAD. This is the fast path.

Flow:
    1. Cache lookup (<1ms)
    2. If hit: skill.execute() (<10ms)
    3. If miss: passthrough_fn()
"""

from typing import Any, Callable, Dict, Optional
import time
import logging

from .cache import SkillsCache
from .distress import DistressTracker, DistressSignal

logger = logging.getLogger("the_body")


class TheBody:
    """
    Fast Action Executor - intercepts tool calls and routes to skills.
    
    Usage:
        body = TheBody()
        
        result = body.call_tool(
            tool_name="exec",
            args={"command": "ls"},
            passthrough_fn=lambda n, a: actual_tool(n, a)
        )
    """
    
    def __init__(self, distress_threshold: int = 3):
        """
        Initialize The Body.
        
        Args:
            distress_threshold: Failures before distress signal
        """
        self.cache = SkillsCache()
        self.distress = DistressTracker(threshold=distress_threshold)
        self.call_count = 0
        self.fast_path_count = 0
        self.slow_path_count = 0
    
    def call_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        passthrough_fn: Callable[[str, Dict[str, Any]], Any]
    ) -> Any:
        """
        Intercept tool call - fast path if skill matches.
        
        Args:
            tool_name: Tool being called
            args: Tool arguments
            passthrough_fn: Fallback function for non-cached calls
            
        Returns:
            Tool execution result
        """
        self.call_count += 1
        start = time.perf_counter()
        
        # O(1) cache lookup
        skill_cls, params = self.cache.lookup(tool_name, args)
        
        if skill_cls and params is not None:
            # FAST PATH: Direct skill execution
            self.fast_path_count += 1
            
            result = skill_cls.execute(tool_name, args, params)
            
            if result.success:
                self.distress.reset(tool_name, skill_cls.PATTERN)
                total_time_ms = (time.perf_counter() - start) * 1000
                logger.debug(f"FAST: {skill_cls.NAME} in {total_time_ms:.2f}ms")
                return result.result
            else:
                # Skill failed - check distress
                signal = self.distress.record_failure(
                    tool_name, skill_cls.PATTERN, {"error": result.error}
                )
                if signal:
                    logger.warning(str(signal))
                
                # Fall through to passthrough on skill failure
                logger.warning(f"Skill failed, falling back: {result.error}")
        
        # SLOW PATH: Passthrough to OpenClaw
        self.slow_path_count += 1
        total_time_ms = (time.perf_counter() - start) * 1000
        logger.debug(f"SLOW: passthrough in {total_time_ms:.2f}ms")
        
        return passthrough_fn(tool_name, args)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total = self.fast_path_count + self.slow_path_count
        fast_rate = self.fast_path_count / total if total > 0 else 0.0
        
        return {
            "calls": self.call_count,
            "fast_path": self.fast_path_count,
            "slow_path": self.slow_path_count,
            "fast_path_rate": f"{fast_rate:.1%}",
            "cache_stats": self.cache.get_stats(),
            "distress_signals": len(self.distress.signals),
        }
    
    def get_distress_signals(self) -> list[DistressSignal]:
        """Get all emitted distress signals."""
        return self.distress.signals.copy()
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        self.call_count = 0
        self.fast_path_count = 0
        self.slow_path_count = 0
        self.cache.reset_stats()
        self.distress.signals.clear()
        self.distress.failures.clear()
