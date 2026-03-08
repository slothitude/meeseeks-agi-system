#!/usr/bin/env python3
"""
the_body Reflex System - SMB Game Player

Combines:
- the_body for reflex speed
- GLM-4.6v for visual recognition
- OpenCV templates for pattern matching
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time

@dataclass
class GameState:
    """Current game state"""
    mario_x: int = 0
    mario_y: int = 0
    enemies: List[Tuple[int, int]] = None
    obstacles: List[Tuple[int, int]] = None
    coins: List[Tuple[int, int]] = None
    score: int = 0
    lives: int = 3
    time_left: int = 400

    def __post_init__(self):
        if self.enemies is None:
            self.enemies = []
        if self.obstacles is None:
            self.obstacles = []
        if self.coins is None:
            self.coins = []

class SMBReflexSystem:
    """
    Reflex system for Super Mario Bros using the_body architecture.

    Speed is key - all decisions must be <10ms.
    """

    def __init__(self):
        # Pre-trained templates (would be loaded from files)
        self.templates = {
            'mario_small': None,
            'mario_big': None,
            'goomba': None,
            'koopa': None,
            'block': None,
            'coin': None,
            'pipe': None,
        }

        # Game state
        self.state = GameState()

        # Reflex actions (pre-compiled for speed)
        self.reflexes = {
            'jump_enemy': self._reflex_jump_enemy,
            'jump_obstacle': self._reflex_jump_obstacle,
            'collect_coin': self._reflex_collect_coin,
            'avoid_pit': self._reflex_avoid_pit,
        }

    def load_templates(self, template_dir: str):
        """Load OpenCV templates for visual recognition"""
        for name in self.templates:
            path = f"{template_dir}/{name}.png"
            try:
                self.templates[name] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            except:
                print(f"Warning: Could not load template {name}")

    def analyze_frame(self, frame: np.ndarray) -> GameState:
        """
        Analyze game frame using OpenCV + GLM-4.6v.

        Target: <10ms
        """
        start = time.perf_counter()

        # Convert to grayscale for template matching
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Fast template matching for known objects
        for name, template in self.templates.items():
            if template is None:
                continue

            # Template matching (this is where speed matters)
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)

            # Update game state based on matches
            if name == 'mario_small' or name == 'mario_big':
                if len(locations[0]) > 0:
                    self.state.mario_x = locations[1][0]
                    self.state.mario_y = locations[0][0]
            elif name in ['goomba', 'koopa']:
                self.state.enemies = list(zip(locations[1], locations[0]))

        elapsed = (time.perf_counter() - start) * 1000
        print(f"Frame analysis: {elapsed:.2f}ms")

        return self.state

    def decide_action(self, state: GameState) -> str:
        """
        Decide next action based on game state.

        Uses reflex system for speed.
        Target: <5ms
        """
        start = time.perf_counter()

        # Priority order: survive > collect > progress
        action = "run_right"  # Default

        # Check reflexes in priority order
        if self._should_jump_enemy(state):
            action = self.reflexes['jump_enemy'](state)
        elif self._should_jump_obstacle(state):
            action = self.reflexes['jump_obstacle'](state)
        elif self._should_collect_coin(state):
            action = self.reflexes['collect_coin'](state)

        elapsed = (time.perf_counter() - start) * 1000
        print(f"Decision: {elapsed:.2f}ms -> {action}")

        return action

    # Reflex checks (fast pattern matching)
    def _should_jump_enemy(self, state: GameState) -> bool:
        """Check if enemy is close enough to jump"""
        for ex, ey in state.enemies:
            if abs(ex - state.mario_x) < 50 and abs(ey - state.mario_y) < 30:
                return True
        return False

    def _should_jump_obstacle(self, state: GameState) -> bool:
        """Check if obstacle is close"""
        for ox, oy in state.obstacles:
            if abs(ox - state.mario_x) < 40:
                return True
        return False

    def _should_collect_coin(self, state: GameState) -> bool:
        """Check if coin is reachable"""
        for cx, cy in state.coins:
            if abs(cx - state.mario_x) < 30 and abs(cy - state.mario_y) < 50:
                return True
        return False

    # Reflex actions (pre-compiled)
    def _reflex_jump_enemy(self, state: GameState) -> str:
        return "jump_right"

    def _reflex_jump_obstacle(self, state: GameState) -> str:
        return "jump_right"

    def _reflex_collect_coin(self, state: GameState) -> str:
        return "jump_right"

    def _reflex_avoid_pit(self, state: GameState) -> str:
        return "jump"

# Integration with the_body
class SMBPlayer:
    """
    Full SMB player integrating:
    - Emulator interface
    - Visual recognition (GLM-4.6v + OpenCV)
    - Reflex system (the_body)
    """

    def __init__(self):
        self.reflex = SMBReflexSystem()
        self.emulator = None  # Would connect to emulator

    def play_frame(self, frame: np.ndarray):
        """Process one frame and send input"""
        # Analyze frame
        state = self.reflex.analyze_frame(frame)

        # Decide action
        action = self.reflex.decide_action(state)

        # Send to emulator
        self._send_input(action)

    def _send_input(self, action: str):
        """Send input to emulator"""
        # Map actions to key presses
        action_map = {
            'run_right': ['right'],
            'jump_right': ['right', 'a'],
            'jump': ['a'],
            'run_left': ['left'],
        }

        keys = action_map.get(action, [])
        # Would send to emulator via browser automation or direct input
        print(f"Input: {keys}")

if __name__ == "__main__":
    print("SMB Reflex System - the_body Integration")
    print("=" * 60)
    print("\nComponents:")
    print("  - OpenCV templates: Visual pattern matching")
    print("  - GLM-4.6v: Visual understanding (when templates fail)")
    print("  - the_body: Reflex decisions <10ms")
    print("\nUsage:")
    print("  1. Load emulator with SMB")
    print("  2. Capture frames")
    print("  3. Run reflex system on each frame")
    print("  4. Send inputs to emulator")
    print("\nSpeed targets:")
    print("  - Frame analysis: <10ms")
    print("  - Decision: <5ms")
    print("  - Total reflex loop: <20ms (50fps)")
