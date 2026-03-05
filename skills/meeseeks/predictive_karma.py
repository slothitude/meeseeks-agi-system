#!/usr/bin/env python3
"""
Predictive Karma — Predict Task Outcome Before Spawning

Uses Cognee knowledge graph to predict success probability and recommend
optimal dharma principles based on similar past tasks.

Usage:
    from predictive_karma import predict_outcome, spawn_with_prediction
    
    # Predict before spawning
    prediction = await predict_outcome("Fix the API bug", "coder")
    print(f"Confidence: {prediction['confidence']:.0%}")
    
    # Spawn with prediction context
    config = await spawn_with_prediction("Fix the API bug", "coder")

CLI:
    python predictive_karma.py --task "fix bug" --bloodline coder
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add meeseeks to path
sys.path.insert(0, str(Path(__file__).parent))

# Try imports
try:
    from cognee_memory import CogneeMemory, COGNEE_AVAILABLE
except ImportError:
    COGNEE_AVAILABLE = False


async def predict_outcome(
    task: str,
    bloodline: str = "coder",
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Predict task outcome before spawning.
    
    Args:
        task: Task description
        bloodline: Bloodline type (coder, searcher, etc.)
        top_k: Number of similar ancestors to analyze
    
    Returns:
        {
            "task": str,
            "bloodline": str,
            "predicted_outcome": "SUCCESS" | "FAILURE" | "PARTIAL",
            "confidence": 0.0-1.0,
            "similar_tasks": int,
            "success_rate": float,
            "recommended_dharma": List[str],
            "risk_factors": List[str],
            "warning": Optional[str]
        }
    """
    result = {
        "task": task,
        "bloodline": bloodline,
        "predicted_outcome": "UNKNOWN",
        "confidence": 0.0,
        "similar_tasks": 0,
        "success_rate": 0.0,
        "recommended_dharma": [],
        "risk_factors": [],
        "warning": None,
        "timestamp": datetime.now().isoformat()
    }
    
    if not COGNEE_AVAILABLE:
        result["warning"] = "Cognee not available - prediction disabled"
        return result
    
    try:
        memory = CogneeMemory()
        connected = await memory.connect()
        
        if not connected:
            result["warning"] = "Could not connect to Cognee"
            return result
        
        # Query for similar tasks
        wisdom = await memory.query_wisdom(
            task=task,
            bloodline=bloodline,
            top_k=top_k,
            include_karma=True
        )
        
        ancestors = wisdom.get("ancestors", [])
        
        if not ancestors:
            result["warning"] = "No similar tasks found in knowledge graph"
            return result
        
        result["similar_tasks"] = len(ancestors)
        
        # Analyze outcomes
        outcomes = []
        for ancestor in ancestors:
            text = str(ancestor).lower()
            if "success" in text:
                outcomes.append("SUCCESS")
            elif "failure" in text or "fail" in text:
                outcomes.append("FAILURE")
            else:
                outcomes.append("PARTIAL")
        
        success_count = outcomes.count("SUCCESS")
        failure_count = outcomes.count("FAILURE")
        
        result["success_rate"] = success_count / len(outcomes) if outcomes else 0
        result["confidence"] = max(result["success_rate"], 1 - result["success_rate"])
        
        # Predict outcome
        if result["success_rate"] >= 0.6:
            result["predicted_outcome"] = "SUCCESS"
        elif result["success_rate"] <= 0.4:
            result["predicted_outcome"] = "FAILURE"
        else:
            result["predicted_outcome"] = "PARTIAL"
        
        # Extract dharma from wisdom
        dharma = wisdom.get("dharma", [])
        if dharma:
            result["recommended_dharma"] = [str(d)[:100] for d in dharma[:3]]
        
        # Identify risk factors from karma
        karma = wisdom.get("karma", [])
        if karma:
            result["risk_factors"] = [str(k)[:100] for k in karma[:3]]
        
        # Add warning if low confidence
        if result["confidence"] < 0.5:
            result["warning"] = f"Low confidence ({result['confidence']:.0%}) - proceed with caution"
        
    except Exception as e:
        result["warning"] = f"Prediction error: {e}"
    
    return result


async def spawn_with_prediction(
    task: str,
    bloodline: str = "coder",
    min_confidence: float = 0.4
) -> Dict[str, Any]:
    """
    Spawn a Meeseeks with prediction context.
    
    Args:
        task: Task description
        bloodline: Bloodline type
        min_confidence: Minimum confidence to spawn (else warn)
    
    Returns:
        Spawn config with prediction context injected
    """
    # Get prediction
    prediction = await predict_outcome(task, bloodline)
    
    # Build enhanced task
    enhanced_task = task
    
    # Add prediction context
    enhanced_task += "\n\n## 🔮 Predictive Karma\n\n"
    enhanced_task += f"**Predicted Outcome:** {prediction['predicted_outcome']}\n"
    enhanced_task += f"**Confidence:** {prediction['confidence']:.0%}\n"
    enhanced_task += f"**Similar Tasks:** {prediction['similar_tasks']}\n"
    
    if prediction["recommended_dharma"]:
        enhanced_task += "\n### 📜 Recommended Dharma\n"
        for d in prediction["recommended_dharma"]:
            enhanced_task += f"- {d}\n"
    
    if prediction["risk_factors"]:
        enhanced_task += "\n### ⚠️ Risk Factors\n"
        for r in prediction["risk_factors"]:
            enhanced_task += f"- {r}\n"
    
    if prediction["warning"]:
        enhanced_task += f"\n### ⚠️ Warning\n{prediction['warning']}\n"
    
    # Return spawn config
    return {
        "task": enhanced_task,
        "original_task": task,
        "meeseeks_type": bloodline,
        "thinking": "high" if prediction["confidence"] < 0.5 else "default",
        "timeout": 600 if prediction["confidence"] < 0.5 else 300,
        "prediction": prediction,
        "should_spawn": prediction["confidence"] >= min_confidence
    }


def format_prediction(prediction: Dict) -> str:
    """Format prediction for display."""
    lines = ["=" * 60]
    lines.append("🔮 PREDICTIVE KARMA")
    lines.append("=" * 60)
    lines.append(f"Task: {prediction['task']}")
    lines.append(f"Bloodline: {prediction['bloodline']}")
    lines.append("")
    lines.append(f"Predicted Outcome: {prediction['predicted_outcome']}")
    lines.append(f"Confidence: {prediction['confidence']:.0%}")
    lines.append(f"Similar Tasks: {prediction['similar_tasks']}")
    lines.append(f"Success Rate: {prediction['success_rate']:.0%}")
    
    if prediction["recommended_dharma"]:
        lines.append("")
        lines.append("📜 Recommended Dharma:")
        for d in prediction["recommended_dharma"]:
            lines.append(f"  • {d[:80]}...")
    
    if prediction["risk_factors"]:
        lines.append("")
        lines.append("⚠️ Risk Factors:")
        for r in prediction["risk_factors"]:
            lines.append(f"  • {r[:80]}...")
    
    if prediction["warning"]:
        lines.append("")
        lines.append(f"⚠️ Warning: {prediction['warning']}")
    
    lines.append("=" * 60)
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Predictive Karma for Meeseeks")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--bloodline", "-b", default="coder", help="Bloodline type")
    parser.add_argument("--spawn", action="store_true", help="Generate spawn config")
    
    args = parser.parse_args()
    
    if args.spawn:
        config = await spawn_with_prediction(args.task, args.bloodline)
        print(format_prediction(config["prediction"]))
        print()
        print(f"Should Spawn: {config['should_spawn']}")
        print(f"Thinking: {config['thinking']}")
        print(f"Timeout: {config['timeout']}s")
    else:
        prediction = await predict_outcome(args.task, args.bloodline)
        print(format_prediction(prediction))


if __name__ == "__main__":
    asyncio.run(main())
