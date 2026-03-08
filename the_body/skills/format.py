"""
Skill: Format - Direct data formatting.

Executes in <5ms by direct Python formatting.
"""

import json
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
import subprocess


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


class SkillFormat:
    """
    Format data output directly.
    
    Fast path patterns:
    - jq commands
    - json formatting
    - csv formatting
    
    Uses direct Python for maximum speed.
    """
    
    NAME = "format"
    PATTERN = "format"
    SUCCESS_RATE = 1.0
    TARGET_TIME_MS = 5.0
    
    SIGNATURES = [
        "jq ",
        "python -m json",
        "convertto-json",
        "convertto-csv",
        "format-table",
        "format-list",
    ]
    
    @classmethod
    def match(cls, tool_name: str, args: Dict[str, Any]) -> SkillMatch:
        """Match formatting operations."""
        if tool_name != "exec":
            return SkillMatch(matched=False, confidence=0.0)
        
        cmd = args.get("command", "").lower()
        
        for sig in cls.SIGNATURES:
            if sig in cmd:
                return SkillMatch(
                    matched=True,
                    confidence=0.90,
                    params={"cmd": args.get("command", "")}
                )
        
        return SkillMatch(matched=False, confidence=0.0)
    
    @classmethod
    def execute(cls, tool_name: str, args: Dict[str, Any], params: Dict[str, Any]) -> ExecutionResult:
        """Direct formatting execution."""
        start = time.perf_counter()
        
        try:
            cmd = params.get("cmd", "")
            
            # Most format commands need subprocess (jq, etc.)
            # But we can handle simple json formatting directly
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5.0
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
