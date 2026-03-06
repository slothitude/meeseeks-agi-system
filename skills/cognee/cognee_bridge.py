#!/usr/bin/env python3
"""
Cognee Bridge - Calls Python 3.13 Cognee from Python 3.14

Since Cognee requires Python 3.10-3.13 but Sloth_rog runs on 3.14,
this bridge uses subprocess to call Cognee operations.

Usage:
    python cognee_bridge.py ingest "path/to/file.md"
    python cognee_bridge.py query "search term"
    python cognee_bridge.py status
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

# Python 3.13 executable (full path for Windows)
PYTHON313 = r"C:\ProgramData\chocolatey\bin\python3.13.exe"

# Cognee script that runs under 3.13
COGNEE_SCRIPT = Path(__file__).parent / "cognee_worker.py"


def call_cognee(action: str, data: str = None) -> Dict[str, Any]:
    """
    Call Cognee via Python 3.13 subprocess.
    
    Args:
        action: "ingest", "query", or "status"
        data: File path for ingest, query string for query
    
    Returns:
        Dict with success, result, or error
    """
    cmd = [PYTHON313, str(COGNEE_SCRIPT), action]
    if data:
        cmd.append(data)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        if result.returncode == 0:
            # Try to parse JSON output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (120s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def ingest_file(file_path: str) -> Dict[str, Any]:
    """Ingest a file into Cognee knowledge graph."""
    return call_cognee("ingest", file_path)


def query_wisdom(query: str) -> Dict[str, Any]:
    """Query Cognee for wisdom."""
    return call_cognee("query", query)


def get_status() -> Dict[str, Any]:
    """Get Cognee status."""
    return call_cognee("status")


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cognee_bridge.py <action> [data]")
        print("Actions: ingest, query, status")
        sys.exit(1)
    
    action = sys.argv[1]
    data = sys.argv[2] if len(sys.argv) > 2 else None
    
    if action == "ingest":
        result = ingest_file(data)
    elif action == "query":
        result = query_wisdom(data)
    elif action == "status":
        result = get_status()
    else:
        result = {"success": False, "error": f"Unknown action: {action}"}
    
    print(json.dumps(result, indent=2))
