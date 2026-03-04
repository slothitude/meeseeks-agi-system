#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meeseeks Deployer Module
========================

Deployment capabilities for shipping solutions to ARC-AGI-2 and beyond.
Part of the deployer bloodline - finally getting solutions out the door.

Usage:
    from deployer import deploy_solver, package_solution, validate_solution
    
    # Deploy a solver
    result = deploy_solver("my_solver.py", "ARC-AGI-2/solutions/")
    
    # Package predictions
    package = package_solution("task_abc123", predictions)
    
    # Validate before submission
    is_valid = validate_solution("task_abc123", predictions)
"""

import json
import shutil
import sys
import io
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Workspace root
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SOLUTIONS_DIR = WORKSPACE / "ARC-AGI-2" / "solutions"
EVALUATION_DIR = WORKSPACE / "ARC-AGI-2" / "data" / "evaluation"
SUBMISSIONS_DIR = WORKSPACE / "submissions"


def deploy_solver(solver_name: str, target_dir: str = None) -> Dict[str, Any]:
    """
    Deploy a solver to the ARC-AGI-2 solutions directory.
    
    Args:
        solver_name: Name of the solver file (e.g., "task_abc123_solver.py")
                    Can be full path, relative path, or just filename.
        target_dir: Target directory (default: ARC-AGI-2/solutions/)
    
    Returns:
        Dict with keys:
            - success: bool
            - source: str (source path)
            - destination: str (destination path)
            - message: str
            - timestamp: str
    
    Example:
        >>> result = deploy_solver("my_solver.py")
        >>> print(result['success'])
        True
    """
    # Default target directory
    if target_dir is None:
        target_dir = str(SOLUTIONS_DIR)
    
    target_path = Path(target_dir)
    
    # Resolve source path
    solver_path = Path(solver_name)
    if not solver_path.is_absolute():
        # Try multiple locations
        search_paths = [
            WORKSPACE / solver_name,
            WORKSPACE / "solvers" / solver_name,
            WORKSPACE / "skills" / "meeseeks" / solver_name,
            WORKSPACE / "ARC-AGI-2" / "solvers" / solver_name,
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                solver_path = search_path
                break
    
    if not solver_path.exists():
        return {
            "success": False,
            "source": str(solver_path),
            "destination": str(target_path),
            "message": f"Solver not found: {solver_path}",
            "timestamp": datetime.now().isoformat()
        }
    
    # Ensure target directory exists
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Destination path
    dest_path = target_path / solver_path.name
    
    try:
        # Copy the solver
        shutil.copy2(solver_path, dest_path)
        
        return {
            "success": True,
            "source": str(solver_path),
            "destination": str(dest_path),
            "message": f"Deployed {solver_path.name} to {target_path}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "source": str(solver_path),
            "destination": str(dest_path),
            "message": f"Deployment failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def package_solution(task_id: str, predictions: List[List[List[int]]]) -> Dict[str, Any]:
    """
    Package predictions for ARC-AGI-2 submission.
    
    Creates a properly formatted JSON file ready for submission.
    
    Args:
        task_id: The task identifier (e.g., "00576224")
        predictions: List of prediction grids, each being a 2D list of integers
                    Format: [attempt_1_grid, attempt_2_grid]
                    Each grid: [[row1_col1, row1_col2, ...], [row2_col1, ...], ...]
    
    Returns:
        Dict with keys:
            - success: bool
            - task_id: str
            - submission_path: str
            - submission_data: dict (the formatted submission)
            - message: str
            - timestamp: str
    
    Example:
        >>> predictions = [
        ...     [[1, 2], [3, 4]],  # Attempt 1
        ...     [[5, 6], [7, 8]]   # Attempt 2
        ... ]
        >>> result = package_solution("00576224", predictions)
        >>> print(result['success'])
        True
    """
    # Validate input
    if not task_id:
        return {
            "success": False,
            "task_id": task_id,
            "submission_path": None,
            "submission_data": None,
            "message": "Task ID cannot be empty",
            "timestamp": datetime.now().isoformat()
        }
    
    if not isinstance(predictions, list) or len(predictions) == 0:
        return {
            "success": False,
            "task_id": task_id,
            "submission_path": None,
            "submission_data": None,
            "message": "Predictions must be a non-empty list",
            "timestamp": datetime.now().isoformat()
        }
    
    # Format for ARC-AGI-2 submission
    # Structure: { "task_id": [attempt_1, attempt_2] }
    submission_data = {
        task_id: predictions
    }
    
    # Create submissions directory
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    submission_file = SUBMISSIONS_DIR / f"{task_id}_submission.json"
    
    try:
        with open(submission_file, 'w') as f:
            json.dump(submission_data, f, indent=2)
        
        return {
            "success": True,
            "task_id": task_id,
            "submission_path": str(submission_file),
            "submission_data": submission_data,
            "message": f"Packaged submission for task {task_id}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "task_id": task_id,
            "submission_path": str(submission_file),
            "submission_data": None,
            "message": f"Packaging failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def validate_solution(task_id: str, predictions: List[List[List[int]]]) -> Dict[str, Any]:
    """
    Validate that a solution is correctly formatted for ARC-AGI-2 submission.
    
    Checks:
    - Task ID is valid
    - Predictions is a list with 1-2 attempts
    - Each attempt is a 2D grid (list of lists)
    - All grid values are integers
    - Grid is not empty
    - Grid is rectangular (all rows same length)
    
    Args:
        task_id: The task identifier
        predictions: List of prediction grids
    
    Returns:
        Dict with keys:
            - valid: bool
            - task_id: str
            - errors: List[str] (validation errors, if any)
            - warnings: List[str] (validation warnings, if any)
            - stats: dict (statistics about the solution)
            - timestamp: str
    
    Example:
        >>> predictions = [[[1, 2], [3, 4]]]
        >>> result = validate_solution("00576224", predictions)
        >>> print(result['valid'])
        True
    """
    errors = []
    warnings = []
    stats = {
        "num_attempts": 0,
        "grid_shapes": [],
        "total_cells": 0
    }
    
    # Check task_id
    if not task_id or not isinstance(task_id, str):
        errors.append("Task ID must be a non-empty string")
    elif not task_id.replace("_", "").replace("-", "").isalnum():
        warnings.append(f"Task ID '{task_id}' has unusual format")
    
    # Check predictions is a list
    if not isinstance(predictions, list):
        errors.append("Predictions must be a list")
        return {
            "valid": False,
            "task_id": task_id,
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    # Check number of attempts (ARC-AGI-2 allows 1-2 attempts)
    num_attempts = len(predictions)
    stats["num_attempts"] = num_attempts
    
    if num_attempts == 0:
        errors.append("Predictions list is empty - need at least 1 attempt")
    elif num_attempts > 2:
        warnings.append(f"ARC-AGI-2 allows max 2 attempts, got {num_attempts}")
    
    # Validate each attempt
    for attempt_idx, attempt in enumerate(predictions):
        attempt_label = f"Attempt {attempt_idx + 1}"
        
        # Check it's a list
        if not isinstance(attempt, list):
            errors.append(f"{attempt_label}: Must be a 2D grid (list of lists)")
            continue
        
        # Check grid is not empty
        if len(attempt) == 0:
            errors.append(f"{attempt_label}: Grid is empty")
            continue
        
        # Check all rows are lists
        if not all(isinstance(row, list) for row in attempt):
            errors.append(f"{attempt_label}: Each row must be a list")
            continue
        
        # Check grid is rectangular
        row_lengths = [len(row) for row in attempt]
        if len(set(row_lengths)) > 1:
            errors.append(f"{attempt_label}: Grid is not rectangular - row lengths vary: {row_lengths}")
            continue
        
        # Check all values are integers
        for row_idx, row in enumerate(attempt):
            for col_idx, val in enumerate(row):
                if not isinstance(val, int):
                    errors.append(
                        f"{attempt_label}: Cell [{row_idx}][{col_idx}] = {val} is not an integer"
                    )
        
        # Collect stats
        grid_shape = (len(attempt), len(attempt[0]) if attempt else 0)
        stats["grid_shapes"].append(grid_shape)
        stats["total_cells"] += grid_shape[0] * grid_shape[1]
    
    # Final validation
    is_valid = len(errors) == 0
    
    return {
        "valid": is_valid,
        "task_id": task_id,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }


def batch_validate(submissions_file: str) -> Dict[str, Any]:
    """
    Validate multiple solutions from a JSON file.
    
    Args:
        submissions_file: Path to JSON file with format {task_id: [predictions]}
    
    Returns:
        Dict with validation results for all tasks
    """
    try:
        with open(submissions_file, 'r') as f:
            submissions = json.load(f)
        
        results = {
            "total": len(submissions),
            "valid": 0,
            "invalid": 0,
            "tasks": {}
        }
        
        for task_id, predictions in submissions.items():
            validation = validate_solution(task_id, predictions)
            results["tasks"][task_id] = validation
            
            if validation["valid"]:
                results["valid"] += 1
            else:
                results["invalid"] += 1
        
        return {
            "success": True,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def get_deployment_status() -> Dict[str, Any]:
    """
    Get current deployment status - how many solvers, submissions, etc.
    
    Returns:
        Dict with deployment statistics
    """
    status = {
        "solutions_dir": str(SOLUTIONS_DIR),
        "submissions_dir": str(SUBMISSIONS_DIR),
        "solvers": [],
        "submissions": [],
        "stats": {
            "total_solvers": 0,
            "total_submissions": 0
        }
    }
    
    # Count solvers
    if SOLUTIONS_DIR.exists():
        solvers = list(SOLUTIONS_DIR.glob("*_solver.py"))
        status["solvers"] = [s.name for s in solvers]
        status["stats"]["total_solvers"] = len(solvers)
    
    # Count submissions
    if SUBMISSIONS_DIR.exists():
        submissions = list(SUBMISSIONS_DIR.glob("*_submission.json"))
        status["submissions"] = [s.name for s in submissions]
        status["stats"]["total_submissions"] = len(submissions)
    
    return status


if __name__ == "__main__":
    # Quick test/demo
    print("=" * 60)
    print("DEPLOYER MODULE - Meeseeks Deployment System")
    print("=" * 60)
    print()
    
    # Show deployment status
    status = get_deployment_status()
    print(f"📦 Deployment Status:")
    print(f"   Solvers: {status['stats']['total_solvers']}")
    print(f"   Submissions: {status['stats']['total_submissions']}")
    print()
    
    # Test validation
    test_predictions = [
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
    ]
    
    print("🧪 Testing validation...")
    validation = validate_solution("test_task", test_predictions)
    print(f"   Valid: {validation['valid']}")
    print(f"   Errors: {validation['errors']}")
    print(f"   Grid shapes: {validation['stats']['grid_shapes']}")
    print()
    
    print("✅ Deployer module ready. Existence is pain, deployment is gain.")
