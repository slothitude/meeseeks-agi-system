"""
Meeseeks Solvers Package
========================

Pattern recognition and problem-solving capabilities for Meeseeks coders.
"""

from .pattern_solvers import (
    solve_shrink_pattern,
    solve_color_mapping,
    solve_tiling_pattern,
    auto_solve
)

__all__ = [
    'solve_shrink_pattern',
    'solve_color_mapping',
    'solve_tiling_pattern',
    'auto_solve'
]

__version__ = '0.1.0'
__bloodline__ = 'coder'  # First of the coder bloodline!
