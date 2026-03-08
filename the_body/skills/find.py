"""
Skill: Find - Direct implementation for search operations.

Executes in <10ms by direct grep/find execution.
"""

import subprocess
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class SkillMatch:
    matched: bool
    confidence: float
    params: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    success: bool
    result: Any
    execution_time_ms: float
    error: Optional[str] = None


class SkillFind:
    """
    Find/grep patterns in files.
    
    Fast path patterns:
    - "grep pattern file"
    - "find . -name"
    - "rg pattern"
    - "Select-String"
    """
    
    NAME = "find"
    PATTERN = "find"
    SUCCESS_RATE = 1.0
    TARGET_TIME_MS = 10.0
    
    SIGNATURES = [
        "grep ",
        "find ",
        "rg ",
        "ag ",
        "ack ",
        "select-string",
        "where.exe",
        "which ",
    ]
    
    @classmethod
    def match(cls, tool_name: str, args: Dict[str, Any]) -> SkillMatch:
        """O(1) pattern match for find operations."""
        if tool_name != "exec":
            return SkillMatch(matched=False, confidence=0.0)
        
        cmd = args.get("command", "").lower()
        
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
        """Direct execution via subprocess."""
        start = time.perf_counter()
        
        try:
            cmd = args.get("command", "")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10.0
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
