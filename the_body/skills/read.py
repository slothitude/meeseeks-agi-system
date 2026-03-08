"""
Skill: Read - Direct file reading.

Executes in <5ms by direct file I/O.
"""

import time
from typing import Any, Dict, Optional
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


class SkillRead:
    """
    Read file contents directly.
    
    Fast path patterns:
    - read tool with path
    - Simple single file reads
    
    Bypasses OpenClaw read tool entirely.
    """
    
    NAME = "read"
    PATTERN = "read"
    SUCCESS_RATE = 1.0
    TARGET_TIME_MS = 5.0  # File I/O is very fast
    
    @classmethod
    def match(cls, tool_name: str, args: Dict[str, Any]) -> SkillMatch:
        """Match read operations."""
        if tool_name == "read":
            path = args.get("path") or args.get("file_path")
            if path:
                # Determine read parameters
                params = {
                    "path": path,
                    "offset": args.get("offset"),
                    "limit": args.get("limit"),
                }
                return SkillMatch(
                    matched=True,
                    confidence=0.98,
                    params=params
                )
        
        # Also match exec commands that are simple file reads
        if tool_name == "exec":
            cmd = args.get("command", "").lower()
            if cmd.startswith("cat ") or cmd.startswith("type ") or "get-content" in cmd:
                return SkillMatch(
                    matched=True,
                    confidence=0.85,
                    params={"raw_cmd": args.get("command", "")}
                )
        
        return SkillMatch(matched=False, confidence=0.0)
    
    @classmethod
    def execute(cls, tool_name: str, args: Dict[str, Any], params: Dict[str, Any]) -> ExecutionResult:
        """Direct file read - bypasses OpenClaw."""
        start = time.perf_counter()
        
        try:
            # Direct file read path
            if "path" in params:
                path = Path(params["path"])
                
                if not path.exists():
                    return ExecutionResult(
                        success=False,
                        result=None,
                        execution_time_ms=(time.perf_counter() - start) * 1000,
                        error=f"File not found: {path}"
                    )
                
                # Read with optional offset/limit
                offset = params.get("offset")
                limit = params.get("limit")
                
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    if offset:
                        # Skip to offset
                        for _ in range(offset - 1):
                            f.readline()
                    
                    if limit:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= limit:
                                break
                            lines.append(line)
                        content = ''.join(lines)
                    else:
                        content = f.read()
                
                execution_time_ms = (time.perf_counter() - start) * 1000
                
                return ExecutionResult(
                    success=True,
                    result=content,
                    execution_time_ms=execution_time_ms
                )
            
            # Subprocess path for cat/type commands
            elif "raw_cmd" in params:
                import subprocess
                result = subprocess.run(
                    params["raw_cmd"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5.0
                )
                
                execution_time_ms = (time.perf_counter() - start) * 1000
                
                return ExecutionResult(
                    success=result.returncode == 0,
                    result=result.stdout,
                    execution_time_ms=execution_time_ms,
                    error=result.stderr if result.returncode != 0 else None
                )
            
            else:
                return ExecutionResult(
                    success=False,
                    result=None,
                    execution_time_ms=(time.perf_counter() - start) * 1000,
                    error="No valid read parameters"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=None,
                execution_time_ms=(time.perf_counter() - start) * 1000,
                error=str(e)
            )
