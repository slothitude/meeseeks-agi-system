#!/usr/bin/env python3
"""
Decision Framework - Apply before any high-confidence decision.

Based on: THE Pattern of Loss
"""

def should_i_proceed(confidence_level: str, domain: str = "Trading", "Projects", "Relationship") -> tuple:
    """
    Returns (proceed, pause, stop) based on pattern analysis.
    
    0 = STOP (Red light)
    1 = PAUSE (Yellow)
    2 = PROCEED (Green)
    """
    confidence = confidence_level.lower()
    domain = domain.lower()
    
    # Red light - DO NOT proceed
    if confidence == "very_high":
        print(f"🛑 STOP - {domain}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: DO not proceed")
        print(f"   Test first, listen to experts, check for sunk costs")
        print(f"   If already losing, STOP immediately")
        return "stop"
    
    # Yellow light - Pause and investigate
    elif confidence == "high":
        print(f"⚠️  PAUSE - {domain}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: test thoroughly before committing")
        print(f"   Paper trade for 1 week minimum")
        print(f"   Check for: speed requirements, hidden costs, execution gaps")
        return "pause"
    
    # Green light - Proceed with caution
    elif confidence == "medium":
        print(f"✅ PROCEED - {domain}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: proceed with testing")
        print(f"   Start small, measure everything")
        print(f"   Have stop conditions ready")
        return "proceed"
    
    # Low confidence - shouldn't be here
    else:
        print(f"❓ LOW CONFIDENCE - {domain}")
        print(f"   Why are you even considering this?")
        print(f"   Confidence too low for action")
        return "stop"


def check_sunk_costs(invested: float, current_value: float) -> str:
    """
    Check if you're throwing good money after bad.
    
    Returns (stop, continue) based on sunk cost analysis.
    """
    if current_value < invested * 0.5:
        print(f"\n💰 SUNK COST WARNING")
        print(f"   Invested: ${invested}")
        print(f"   Current value: {current_value}")
        print(f"   Lost: {invested - current_value:.2f}")
        print(f"   Action: STOP - don't chase losses")
        return "stop"
    else:
        print(f"\n✅ Investment OK")
        print(f"   Current value ({current_value}) > invested ({invested})")
        return "continue"


def measure_execution_speed(my_speed: str, required_speed: str) -> tuple:
    """
    Check if you can execute fast enough.
    
    Returns (can_compete, too_slow) based on speed analysis.
    """
    # Parse speeds
    speed_units = {"milliseconds": 0.001, "seconds": 1, "minutes": 60}
    
    my_time = float(my_speed.split()[0])
    my_unit = my_speed.split()[1] if len(my_speed.split()) > 1 else "seconds"
    my_seconds = my_time * speed_units.get(my_unit, 1)
    
    req_time = float(required_speed.split()[0])
    req_unit = required_speed.split()[1] if len(required_speed.split()) > 1 else "seconds"
    req_seconds = req_time * speed_units.get(req_unit, 1)
    
    gap = my_seconds / req_seconds if req_seconds > 0 else 1.0
    
    if gap > 2:
        print(f"\n🐢 TOO SLOW - Gap: {gap:.1f}x")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}")
        print(f"   Action: Don't compete - find different strategy or build automation")
        return "too_slow"
    elif gap > 1:
        print(f"\n⚠️ SPEED MARGINAL - Gap: {gap:.1f}x")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}")
        print(f"   Action: Proceed with caution or improve speed")
        return "can_compete"
    else:
        print(f"\n✅ SPEED ADEQUATE")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}")
        return "can_compete"


# Example usage
if __name__ == "__main__":
    # Trading ARB
    decision = should_i_proceed("very_high", "trading")
    print()
    
    # Check speed
    speed_check = measure_execution_speed("30 seconds", "<1 second")
    print()
    
    # Check sunk costs
    sunk_cost = check_sunk_costs(20.67, 2.19)
    print()
    
    # Project
    decision = should_i_proceed("high", "new feature")
    print()
    
    # Relationship
    decision = should_i_proceed("medium", "new relationship")
