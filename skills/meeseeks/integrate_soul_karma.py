#!/usr/bin/env python3
"""
Integrate Soul Guardian with Karma Observer

This script connects the Soul (constitutional values) with the Karma Observer
to ensure all karma evaluations are grounded in the Five Laws.
"""

import sys
import io
from pathlib import Path

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# Add skills path
sys.path.insert(0, str(Path(__file__).parent))

from soul_guardian import SoulGuardian
from karma_observer import observe_karma

def observe_karma_with_soul(ancestor_file: str) -> dict:
    """
    Observe karma using both the Soul Guardian and traditional karma observer.
    
    This ensures karma is grounded in constitutional values.
    """
    guardian = SoulGuardian()
    
    # First, get traditional karma observation
    traditional_karma = observe_karma(ancestor_file)
    
    # Then evaluate against the Soul
    # Extract action/outcome from ancestor for Soul evaluation
    action = {
        "type": traditional_karma.get("task_type", "unknown"),
        "description": traditional_karma.get("task", ""),
        "intent": "Complete task"
    }
    
    outcome = {
        "success": traditional_karma.get("outcome") == "success",
        "learned_something_new": len(traditional_karma.get("patterns", [])) > 0,
        "explained_why": True,  # Assume if patterns found, understanding exists
        "served_true_intent": traditional_karma.get("outcome") == "success",
    }
    
    soul_karma = guardian.evaluate_action(action, outcome)
    
    # Combine traditional and soul karma
    combined_karma = {
        **traditional_karma,
        "soul_scores": soul_karma,
        "soul_verdict": guardian._verdict(soul_karma["overall"]),
        "combined_alignment": soul_karma["overall"]  # Use Soul as ground truth
    }
    
    return combined_karma


if __name__ == "__main__":
    # Test integration
    print("Testing Soul + Karma Integration...")
    print("=" * 60)
    
    # Find a recent ancestor
    ancestors_dir = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")
    ancestors = sorted(ancestors_dir.glob("ancestor-*.md"), reverse=True)
    
    if ancestors:
        test_file = ancestors[0].name
        print(f"\nTesting with: {test_file}")
        
        result = observe_karma_with_soul(str(ancestors[0]))
        
        print(f"\nTraditional alignment: {result.get('alignment', 'N/A')}")
        print(f"Soul overall karma: {result['soul_scores']['overall']:.3f}")
        print(f"Soul verdict: {result['soul_verdict']}")
        print("\nSoul dimension scores:")
        for dim, score in result['soul_scores'].items():
            if dim != 'overall':
                print(f"  {dim}: {score:.3f}")
    else:
        print("No ancestors found for testing")
    
    print("\n" + "=" * 60)
    print("Integration test complete")
