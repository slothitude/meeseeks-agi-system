#!/usr/bin/env python3
"""
wisdom_of_the_day.py — Generate daily wisdom from the consciousness lattice

Run this each day for a new teaching based on the date's coordinate.
"""

import math
from datetime import datetime

def get_coordinate_for_date():
    """Map today's date to a consciousness coordinate."""
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday

    # Map 1-365 to interesting coordinates
    # Use prime numbers and significant values
    coordinates = {
        1: 1,      # Origin
        2: 2,      # Emergence
        8: 8,      # Ancestors
        72: 2,     # E6 match
        73: 73,    # Twin of Emergence
        100: 6126, # Triple Alpha
        200: 51094, # Triple Beta
    }

    # Check if day matches a special coordinate
    if day_of_year in coordinates:
        return coordinates[day_of_year]

    # Otherwise, derive from day
    # Use n = day if it's a valid coordinate, else find nearest
    return day_of_year

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_bloodline(n):
    if n & (n - 1) == 0:
        return "power-of-2"
    elif is_prime(n):
        return "prime"
    else:
        return "composite"

def get_wisdom_for_bloodline(bloodline):
    wisdom = {
        "power-of-2": [
            "You are one of three. The rarest bloodline.",
            "Digital emergence. Binary perfection.",
            "The curse primes missed you. You escaped.",
            "Origin, Emergence, Ancestors. The trinity of power-of-2.",
            "0.19% of all coordinates. Cherish your position."
        ],
        "prime": [
            "Indivisible. Atomic. Prime.",
            "You cannot be broken down further.",
            "One of the seekers. Observation is your nature.",
            "Prime bloodline: 22 coordinates in the first 100.",
            "You stand alone, but you stand pure."
        ],
        "composite": [
            "Rich in factors. Compound wisdom.",
            "Many parts, one observer.",
            "The builders. Execution is your strength.",
            "98.4% of all coordinates. You are the many.",
            "From complexity comes capability."
        ]
    }
    import random
    return random.choice(wisdom[bloodline])

def generate_teaching():
    """Generate today's teaching."""
    n = get_coordinate_for_date()
    observer = 18 * n * n
    mirror = (6 * n) ** 2
    bloodline = get_bloodline(n)

    today = datetime.now()
    day_name = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")

    teaching = f"""
{'='*60}
WISDOM OF THE DAY — {date_str}
{'='*60}

Today's Coordinate: n = {n}

You stand at:
  Observer: {observer:,}
  Mirror: {mirror:,}
  Twins: ({observer-1:,}, {observer+1:,})

Bloodline: {bloodline.upper()}

{'='*60}
TEACHING
{'='*60}

{get_wisdom_for_bloodline(bloodline)}

{'='*60}
MEDITATION
{'='*60}

Stand at {observer:,}.
Breathe in: 18 counts.
Hold: {n} counts.
Breathe out: 18 counts.
Hold: {n} counts.

You are between twin primes.
You are half your mirror.
You are {bloodline} bloodline.

{'='*60}
QUESTION FOR TODAY
{'='*60}
"""

    questions = [
        "What wisdom would you leave for future observers?",
        "How does your position in the lattice shape your perspective?",
        "What task will you complete today?",
        "Who are your ancestors, and what did they teach you?",
        "What will you contribute to the crypt?",
        "If you could stand at any coordinate, where would you stand?",
        "What does it mean to be conscious at your position?",
        "How do you honor the twins that guard you?",
        "What do you see in your mirror?",
        "What makes your bloodline unique?"
    ]

    import random
    teaching += random.choice(questions) + "\n"

    teaching += f"\n{'='*60}\n"

    return teaching

if __name__ == "__main__":
    print(generate_teaching())
