"""
Skill: Count - Direct implementation for counting operations.

Executes in <10ms by:
- Direct subprocess call for wc -l
- Direct len() for Python counts
- Direct file line counting
"""

import subprocess
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
import os


@dataclass
class SkillMatch:
    """Result of skill matching."""
    matched: bool
    confidence: float
    params: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """Result of skill execution."""
    success: bool
    result: Any
    execution_time_ms: float
    error: Optional[str] = None


class SkillCount:
    """
    Count items - files, lines, matches, etc.
    
    Fast path patterns:
    - "wc -l <file>" → line count
    - "ls | wc -l" → file count
    - Python len() operations
    """
    
    NAME = "count"
    PATTERN = "count"
    SUCCESS_RATE = 1.0
    TARGET_TIME_MS = 10.0
    
    # Quick pattern signatures for O(1) matching
    SIGNATURES = [
        "wc -l",
        "wc -c",
        "| wc",
        "count",
        "measure-object",
        ".count(",
        "len(",
    ]
    
    @classmethod
    def match(cls, tool_name: str, args: Dict[str, Any]) -> SkillMatch:
        """
        O(1) pattern match for count operations.
        
        Returns immediately if pattern doesn't match.
        """
        if tool_name != "exec":
            return SkillMatch(matched=False, confidence=0.0)
        
        cmd = args.get("command", "").lower()
        
        # Quick substring check - O(n) where n = cmd length, but very fast
        for sig in cls.SIGNATURES:
            if sig in cmd:
                return SkillMatch(
                    matched=True,
                    confidence=0.95,
                    params={"raw_cmd": args.get("command", "")}
                )
        
        return SkillMatch(matched=False, confidence=0.0)
    
    @classmethod
    def execute(cls, tool_name: str, args: Dict[str, Any], params: Dict[str, Any]) -> ExecutionResult:
        """
        Direct execution - bypasses OpenClaw entirely.
        
        Executes the count command directly via subprocess.
        """
        start = time.perf_counter()
        
        try:
            cmd = args.get("command", "")
            
            # Direct subprocess execution - fast
            # Use shell=True for complex commands with pipes
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5.0  # Safety timeout
            )
            
            execution_time_ms = (time.perf_counter() - start) * 1000
            
            return ExecutionResult(
                success=result.returncode == 0,
                result=result.stdout.strip(),
                execution_time_ms=execution_time_ms,
                error=result.stderr if result.returncode != 0 else None
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                result=None,
                execution_time_ms=(time.perf_counter() - start) * 1000,
                error="Timeout"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=None,
                execution_time_ms=(time.perf_counter() - start) * 1000,
                error=str(e)
            )
