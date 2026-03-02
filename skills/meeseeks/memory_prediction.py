#!/usr/bin/env python3
"""
Memory-Prediction Framework for Meeseeks

Based on Jeff Hawkins' Hierarchical Temporal Memory (HTM) theory.

Concept: The brain is a prediction machine. It constantly predicts what
will happen next and learns from prediction errors.

Components:
1. **Predictions** - What the agent expects to happen
2. **Outcomes** - What actually happened
3. **Prediction Errors** - Difference between prediction and outcome
4. **Learning** - Updating predictions based on errors

Usage in Meeseeks:
- Before each action, predict what will happen
- After action, record actual outcome
- Track prediction accuracy
- Learn from errors (entomb predictions with results)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math

PREDICTIONS_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "predictions.json"


@dataclass
class Prediction:
    """A prediction about what will happen."""
    description: str
    confidence: float  # 0.0 to 1.0
    context: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    outcome: Optional[str] = None
    was_correct: Optional[bool] = None
    error_type: Optional[str] = None


class MemoryPredictionSystem:
    """
    Memory-Prediction learning system.
    
    Usage:
        mp = MemoryPredictionSystem()
        
        # Before action, make prediction
        mp.predict("File will contain class definition", confidence=0.7)
        mp.predict("Bug will be in authentication logic", confidence=0.8)
        
        # After action, record outcome
        mp.observe("File contains class and functions")
        mp.observe("Bug was in token validation")
        
        # Evaluate predictions
        mp.evaluate()
        
        # Get prediction accuracy
        accuracy = mp.get_accuracy()
        
        # Learn from errors
        lessons = mp.extract_lessons()
    """
    
    def __init__(self, session_key: str = None):
        self.session_key = session_key
        self.predictions: List[Prediction] = []
        self.observations: List[str] = []
        self.evaluated = False
    
    def predict(self, description: str, confidence: float = 0.5, context: Dict = None):
        """Make a prediction before taking action."""
        prediction = Prediction(
            description=description,
            confidence=confidence,
            context=context or {}
        )
        self.predictions.append(prediction)
        return prediction
    
    def observe(self, outcome: str):
        """Record an observation after action."""
        self.observations.append(outcome)
    
    def evaluate(self) -> Dict:
        """
        Evaluate predictions against observations.
        
        Returns evaluation summary.
        """
        if self.evaluated:
            return {"status": "already_evaluated"}
        
        results = {
            "total_predictions": len(self.predictions),
            "correct": 0,
            "incorrect": 0,
            "uncertain": 0,
            "errors": []
        }
        
        for pred in self.predictions:
            # Try to match prediction to observations
            matched = False
            for obs in self.observations:
                match_result = self._match_prediction_to_observation(pred.description, obs)
                
                if match_result == "correct":
                    pred.was_correct = True
                    pred.outcome = obs
                    results["correct"] += 1
                    matched = True
                    break
                elif match_result == "incorrect":
                    pred.was_correct = False
                    pred.outcome = obs
                    pred.error_type = self._classify_error(pred.description, obs)
                    results["incorrect"] += 1
                    results["errors"].append({
                        "prediction": pred.description,
                        "outcome": obs,
                        "error_type": pred.error_type
                    })
                    matched = True
                    break
            
            if not matched:
                pred.was_correct = None
                results["uncertain"] += 1
        
        self.evaluated = True
        return results
    
    def _match_prediction_to_observation(self, prediction: str, observation: str) -> str:
        """
        Determine if prediction matches observation.
        
        Returns: "correct", "incorrect", or "uncertain"
        """
        pred_lower = prediction.lower()
        obs_lower = observation.lower()
        
        # Simple keyword matching
        pred_keywords = set(pred_lower.split())
        obs_keywords = set(obs_lower.split())
        
        # Check for direct contradiction
        contradiction_words = [
            ("will", "didn't"),
            ("contains", "empty"),
            ("has", "missing"),
            ("works", "fails"),
            ("success", "error"),
            ("found", "not found"),
            ("exists", "doesn't exist")
        ]
        
        for w1, w2 in contradiction_words:
            if w1 in pred_keywords and w2 in obs_keywords:
                return "incorrect"
        
        # Check for overlap
        overlap = pred_keywords & obs_keywords
        
        # Significant overlap = correct
        if len(overlap) >= 2:
            return "correct"
        
        # Some overlap = uncertain
        if len(overlap) >= 1:
            return "uncertain"
        
        # No overlap but no contradiction = uncertain
        return "uncertain"
    
    def _classify_error(self, prediction: str, outcome: str) -> str:
        """Classify the type of prediction error."""
        pred_lower = prediction.lower()
        out_lower = outcome.lower()
        
        if "not found" in out_lower or "doesn't exist" in out_lower:
            return "assumed_existence"
        elif "unexpected" in out_lower or "surprise" in out_lower:
            return "unexpected_result"
        elif "error" in out_lower or "failed" in out_lower:
            return "assumed_success"
        elif "different" in out_lower or "instead" in out_lower:
            return "wrong_assumption"
        else:
            return "general_misjudgment"
    
    def get_accuracy(self) -> float:
        """Get prediction accuracy (0.0 to 1.0)."""
        if not self.predictions:
            return 0.0
        
        if not self.evaluated:
            self.evaluate()
        
        total = len(self.predictions)
        correct = sum(1 for p in self.predictions if p.was_correct == True)
        
        return correct / total if total > 0 else 0.0
    
    def extract_lessons(self) -> List[Dict]:
        """
        Extract lessons from prediction errors.
        
        These become tricks/patterns for future Meeseeks.
        """
        if not self.evaluated:
            self.evaluate()
        
        lessons = []
        
        for pred in self.predictions:
            if pred.was_correct == False:
                lesson = {
                    "prediction": pred.description,
                    "actual": pred.outcome,
                    "error_type": pred.error_type,
                    "lesson": self._generate_lesson(pred),
                    "confidence_before": pred.confidence,
                    "suggested_confidence": max(0.1, pred.confidence - 0.3)
                }
                lessons.append(lesson)
        
        return lessons
    
    def _generate_lesson(self, pred: Prediction) -> str:
        """Generate a lesson from a prediction error."""
        error_type = pred.error_type or "unknown"
        
        lessons_by_type = {
            "assumed_existence": f"Don't assume things exist - verify first. I assumed '{pred.description}' but {pred.outcome}",
            "unexpected_result": f"Be prepared for unexpected outcomes. Expected '{pred.description}' but got {pred.outcome}",
            "assumed_success": f"Don't assume success - check for errors. Expected '{pred.description}' but {pred.outcome}",
            "wrong_assumption": f"Question assumptions more carefully. Assumed '{pred.description}' but {pred.outcome}",
            "general_misjudgment": f"Prediction '{pred.description}' was wrong. Actual: {pred.outcome}"
        }
        
        return lessons_by_type.get(error_type, f"Prediction failed: {pred.description}")
    
    def to_prompt_block(self) -> str:
        """Generate predictions block for prompt."""
        lines = [
            "## 🔮 Memory-Prediction State",
            ""
        ]
        
        if self.predictions:
            lines.append("### Current Predictions:")
            for pred in self.predictions:
                conf_str = "HIGH" if pred.confidence > 0.7 else "MEDIUM" if pred.confidence > 0.4 else "LOW"
                status = ""
                if pred.was_correct is not None:
                    status = " ✅" if pred.was_correct else " ❌"
                lines.append(f"- [{conf_str}]{status} {pred.description}")
            lines.append("")
        
        if self.observations:
            lines.append("### Observations:")
            for obs in self.observations[-5:]:
                lines.append(f"- {obs}")
            lines.append("")
        
        if self.evaluated:
            accuracy = self.get_accuracy()
            lines.append(f"**Prediction Accuracy:** {accuracy:.1%}")
        
        return "\n".join(lines)
    
    def save(self):
        """Save predictions to file."""
        if not self.session_key:
            return
        
        PREDICTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "session_key": self.session_key,
            "predictions": [
                {
                    "description": p.description,
                    "confidence": p.confidence,
                    "outcome": p.outcome,
                    "was_correct": p.was_correct,
                    "error_type": p.error_type
                }
                for p in self.predictions
            ],
            "observations": self.observations,
            "accuracy": self.get_accuracy(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing
        all_data = {}
        if PREDICTIONS_FILE.exists():
            try:
                all_data = json.loads(PREDICTIONS_FILE.read_text(encoding="utf-8"))
            except:
                pass
        
        all_data[self.session_key] = data
        PREDICTIONS_FILE.write_text(json.dumps(all_data, indent=2), encoding="utf-8")


def create_predictions_for_task(task: str) -> MemoryPredictionSystem:
    """Create prediction system with initial predictions for a task."""
    mp = MemoryPredictionSystem()
    
    task_lower = task.lower()
    
    # Generate initial predictions based on task type
    if "fix" in task_lower or "bug" in task_lower:
        mp.predict("Bug will be reproducible", confidence=0.7)
        mp.predict("Fix will require single file change", confidence=0.6)
        mp.predict("Tests will pass after fix", confidence=0.8)
    elif "create" in task_lower or "build" in task_lower:
        mp.predict("Will create 1-3 new files", confidence=0.6)
        mp.predict("Implementation will work first try", confidence=0.4)
        mp.predict("Will need minor adjustments", confidence=0.7)
    elif "search" in task_lower or "find" in task_lower:
        mp.predict("Information will be found in first 3 results", confidence=0.6)
        mp.predict("Search terms will need refinement", confidence=0.5)
    
    return mp


if __name__ == "__main__":
    # Test Memory-Prediction System
    print("Testing Memory-Prediction System")
    print("=" * 50)
    
    mp = create_predictions_for_task("Fix the authentication bug")
    
    print("\nInitial predictions:")
    for pred in mp.predictions:
        print(f"  - {pred.description} (confidence: {pred.confidence})")
    
    # Simulate observations
    print("\nObserving outcomes...")
    mp.observe("Bug was reproducible with specific inputs")
    mp.observe("Fix required changes to 2 files")
    mp.observe("Tests passed after fix")
    
    # Evaluate
    results = mp.evaluate()
    print(f"\nEvaluation: {results}")
    
    # Extract lessons
    lessons = mp.extract_lessons()
    if lessons:
        print("\nLessons learned:")
        for lesson in lessons:
            print(f"  - {lesson['lesson']}")
    else:
        print("\nAll predictions were correct or uncertain!")
    
    # Show accuracy
    print(f"\nAccuracy: {mp.get_accuracy():.1%}")
    
    # Generate prompt block
    with open('test_predictions.md', 'w', encoding='utf-8') as f:
        f.write(mp.to_prompt_block())
    print("\nWrote test_predictions.md")
