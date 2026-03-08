"""
Skill: Ls - Direct directory listing.

Executes in <10ms by direct os.listdir() or subprocess.
"""

import os
import subprocess
import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path


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


class SkillLs:
    """
    List directory contents directly.
    
    Fast path patterns:
    - "ls" command
    - "dir" command
    - "Get-ChildItem"
    
    Uses os.listdir() for maximum speed when possible.
    """
    
    NAME = "ls"
    PATTERN = "ls"
    SUCCESS_RATE = 1.0
    TARGET_TIME_MS = 10.0
    
    SIGNATURES = [
        "ls",
        "dir ",
        "get-childitem",
        "list ",
    ]
    
    @classmethod
    def match(cls, tool_name: str, args: Dict[str, Any]) -> SkillMatch:
        """Match directory listing operations."""
        if tool_name != "exec":
            return SkillMatch(matched=False, confidence=0.0)
        
        cmd = args.get("command", "").lower()
        
        # Quick match on ls/dir commands
        cmd_stripped = cmd.strip()
        
        # Exact match for simple ls
        if cmd_stripped == "ls" or cmd_stripped.startswith("ls ") or cmd_stripped.startswith("ls\t"):
            return SkillMatch(matched=True, confidence=0.98, params={"cmd": args.get("command", "")})
        
        if "get-childitem" in cmd or "dir " in cmd:
            return SkillMatch(matched=True, confidence=0.95, params={"cmd": args.get("command", "")})
        
        return SkillMatch(matched=False, confidence=0.0)
    
    @classmethod
    def execute(cls, tool_name: str, args: Dict[str, Any], params: Dict[str, Any]) -> ExecutionResult:
        """Direct directory listing."""
        start = time.perf_counter()
        
        try:
            cmd = params.get("cmd", "").strip()
            
            # Fast path: Simple ls without flags
            if cmd == "ls" or cmd == "ls .":
                # Direct os.listdir() - fastest possible
                items = os.listdir('.')
                execution_time_ms = (time.perf_counter() - start) * 1000
                return ExecutionResult(
                    success=True,
                    result='\n'.join(items),
                    execution_time_ms=execution_time_ms
                )
            
            # Fast path: ls with specific directory
            if cmd.startswith("ls ") and "|" not in cmd and ">" not in cmd:
                parts = cmd.split(None, 1)
                if len(parts) == 2:
                    target_dir = parts[1].strip()
                    if os.path.isdir(target_dir):
                        items = os.listdir(target_dir)
                        execution_time_ms = (time.perf_counter() - start) * 1000
                        return ExecutionResult(
                            success=True,
                            result='\n'.join(items),
                            execution_time_ms=execution_time_ms
                        )
            
            # General path: Use subprocess for complex commands
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
