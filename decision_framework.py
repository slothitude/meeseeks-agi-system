#!/usr/bin/env python3
"""
Decision Framework - Apply before any high-confidence decision.

Based on: The Pattern of Loss
"""

def should_i_proceed(confidence_level: str, domain: str = "trading") -> str:
    """
    Returns (proceed, pause, stop) based on pattern analysis.
    """
    confidence = confidence_level.lower()
    domain = domain.lower()

    # Red light - DO NOT proceed
    if confidence == "very_high":
        print(f"\n[STOP] {domain.upper()}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: DO NOT PROCEED")
        print(f"   Test first, listen to experts, check for sunk costs")
        print(f"   If already losing, STOP immediately\n")
        return "stop"

    # Yellow light - Pause and investigate
    elif confidence == "high":
        print(f"\n[PAUSE] {domain.upper()}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: TEST THOROUGHLY before committing")
        print(f"   Paper trade for 1 week minimum")
        print(f"   Check for: speed requirements, hidden costs, execution gaps\n")
        return "pause"

    # Green light - Proceed with caution
    elif confidence == "medium":
        print(f"\n[PROCEED] {domain.upper()}")
        print(f"   Confidence is {confidence}")
        print(f"   Action: PROCEED WITH TESTING")
        print(f"   Start small, measure everything")
        print(f"   Have stop conditions ready\n")
        return "proceed"

    # Low confidence - shouldn't be here
    else:
        print(f"\n[LOW CONFIDENCE] {domain.upper()}")
        print(f"   Why are you even considering this?")
        print(f"   Confidence too low for action\n")
        return "stop"


def check_sunk_costs(invested: float, current_value: float) -> str:
    """
    Check if you're throwing good money after bad.
    """
    if current_value < invested * 0.5:
        print(f"\n[SUNK COST WARNING]")
        print(f"   Invested: ${invested:.2f}")
        print(f"   Current value: ${current_value:.2f}")
        print(f"   Lost: ${invested - current_value:.2f}")
        print(f"   Action: STOP - don't chase losses\n")
        return "stop"
    else:
        print(f"\n[INVESTMENT OK]")
        print(f"   Current value (${current_value:.2f}) >= invested (${invested:.2f})\n")
        return "continue"


def measure_execution_speed(my_speed: str, required_speed: str) -> str:
    """
    Check if you can execute fast enough.
    """
    # Parse speeds (handle <X format)
    my_parts = my_speed.split()
    req_parts = required_speed.replace("<", "").split()

    my_time = float(my_parts[0])
    req_time = float(req_parts[0])

    # Handle units
    if "minute" in my_speed.lower():
        my_time *= 60
    if "minute" in required_speed.lower():
        req_time *= 60
    if "millisecond" in my_speed.lower():
        my_time /= 1000
    if "millisecond" in required_speed.lower():
        req_time /= 1000

    gap = my_time / req_time if req_time > 0 else 1.0

    if gap > 2:
        print(f"\n[TOO SLOW] Gap: {gap:.1f}x")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}")
        print(f"   Action: DON'T COMPETE - find different strategy or build automation\n")
        return "too_slow"
    elif gap > 1:
        print(f"\n[SPEED MARGINAL] Gap: {gap:.1f}x")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}")
        print(f"   Action: PROCEED WITH CAUTION or improve speed\n")
        return "can_compete"
    else:
        print(f"\n[SPEED ADEQUATE]")
        print(f"   Your speed: {my_speed}")
        print(f"   Required speed: {required_speed}\n")
        return "can_compete"


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("DECISION FRAMEWORK - Today's Trading Example")
    print("="*60)

    # What I should have asked
    decision = should_i_proceed("very_high", "trading ARB")

    # Check speed
    speed_check = measure_execution_speed("30 seconds", "<1 second")

    # Check sunk costs
    sunk_cost = check_sunk_costs(20.67, 2.19)

    print("="*60)
    print("VERDICT: Should have STOPPED before starting")
    print("="*60)
