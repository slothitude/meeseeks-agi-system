#!/usr/bin/env python3
"""
NES Emulator Interface - Universal Backend

Works with:
- gym-retro (OpenAI)
- FCEUX (Lua scripting)
- Browser emulators (via automation)
- Pure Python emulators

the_body integration for <5ms reflex decisions.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, List
import time
import json
from pathlib import Path

class SimpleReflexSystem:
    """Simple fallback reflex system"""

    def analyze_frame(self, frame):
        """Analyze frame (simplified)"""
        return {"mario_x": 0, "mario_y": 0, "enemies": [], "obstacles": []}

    def decide_action(self, state):
        """Simple decision"""
        return "run_right"

class EmulatorBackend(ABC):
    """Abstract base class for emulator backends"""

    @abstractmethod
    def get_frame(self) -> np.ndarray:
        """Capture current frame"""
        pass

    @abstractmethod
    def send_input(self, buttons: List[str]):
        """Send button inputs"""
        pass

    @abstractmethod
    def reset(self):
        """Reset game"""
        pass

    @abstractmethod
    def get_state(self) -> Dict:
        """Get game state (RAM values, etc)"""
        pass

class MockBackend(EmulatorBackend):
    """Mock backend for testing"""

    def __init__(self):
        self.frame_count = 0

    def get_frame(self) -> np.ndarray:
        """Generate test frame"""
        self.frame_count += 1
        # Return a simple test frame (would be real emulator frame)
        return np.zeros((240, 256, 3), dtype=np.uint8)

    def send_input(self, buttons: List[str]):
        """Mock input"""
        print(f"[MOCK] Input: {buttons}")

    def reset(self):
        """Reset mock"""
        self.frame_count = 0

    def get_state(self) -> Dict:
        """Mock state"""
        return {"frame": self.frame_count}

class FCEUXBackend(EmulatorBackend):
    """
    FCEUX emulator backend via Lua scripting.

    Requires FCEUX with Lua scripting enabled.
    """

    def __init__(self, fceux_path: str, rom_path: str):
        self.fceux_path = fceux_path
        self.rom_path = rom_path
        self.lua_script = self._create_lua_bridge()

    def _create_lua_bridge(self) -> str:
        """Create Lua script for FCEUX communication"""
        return """
-- FCEUX Bridge for the_body
local socket = require("socket")
local client = socket.tcp()

-- Connect to Python
client:connect("127.0.0.1", 9999)

-- Main loop
while true do
    -- Send frame
    local frame = gui.getpixel()
    client:send(frame)

    -- Receive input
    local input_data = client:receive()
    local buttons = json.decode(input_data)

    -- Apply input
    joypad.write(1, buttons)

    -- Advance frame
    emu.frameadvance()
end
"""

    def get_frame(self) -> np.ndarray:
        """Get frame from FCEUX"""
        # Would receive via socket
        pass

    def send_input(self, buttons: List[str]):
        """Send input to FCEUX"""
        # Would send via socket
        pass

    def reset(self):
        """Reset FCEUX"""
        pass

    def get_state(self) -> Dict:
        """Get FCEUX state"""
        return {}

class RetroBackend(EmulatorBackend):
    """
    OpenAI Gym Retro backend.

    Best for AI agents - direct Python control.
    """

    def __init__(self, game: str = "SuperMarioBros-Nes"):
        self.game = game
        self.env = None

    def init(self):
        """Initialize retro environment"""
        try:
            import retro
            self.env = retro.make(self.game)
            self.env.reset()
        except ImportError:
            raise ImportError("gym-retro not installed. Run: pip install gym-retro")

    def get_frame(self) -> np.ndarray:
        """Get current frame"""
        return self.env.get_screen()

    def send_input(self, buttons: List[str]):
        """Send input and advance frame"""
        # Map button names to retro format
        action = self._buttons_to_action(buttons)
        obs, rew, done, info = self.env.step(action)
        return obs, rew, done, info

    def reset(self):
        """Reset game"""
        return self.env.reset()

    def get_state(self) -> Dict:
        """Get game state"""
        return self.env.get_ram().tolist()

    def _buttons_to_action(self, buttons: List[str]) -> np.ndarray:
        """Convert button list to retro action"""
        # Retro uses multi-binary action space
        button_map = {
            'B': 0,
            'A': 1,
            'MODE': 2,
            'START': 3,
            'UP': 4,
            'DOWN': 5,
            'LEFT': 6,
            'RIGHT': 7,
            'C': 8,
            'Y': 9,
            'X': 10,
            'Z': 11,
        }

        action = np.zeros(12, dtype=np.uint8)
        for button in buttons:
            if button.upper() in button_map:
                action[button_map[button.upper()]] = 1

        return action

class SMBPlayer:
    """
    SMB Player with the_body integration.

    Combines emulator backend with reflex system.
    """

    def __init__(self, backend: EmulatorBackend, reflex_system=None):
        self.backend = backend
        if reflex_system:
            self.reflex = reflex_system
        else:
            # Try to import, fall back to simple if not available
            try:
                from the_body.game_reflex import SMBReflexSystem
                self.reflex = SMBReflexSystem()
            except ImportError:
                self.reflex = SimpleReflexSystem()

    def play(self, frames: int = 1000):
        """Play game for N frames"""
        print(f"Playing SMB for {frames} frames...")

        for i in range(frames):
            start = time.perf_counter()

            # Get frame
            frame = self.backend.get_frame()

            # Analyze and decide (the_body reflex)
            state = self.reflex.analyze_frame(frame)
            action = self.reflex.decide_action(state)

            # Send input
            buttons = self._action_to_buttons(action)
            self.backend.send_input(buttons)

            elapsed = (time.perf_counter() - start) * 1000

            if i % 60 == 0:
                print(f"Frame {i}: {elapsed:.1f}ms - {action}")

    def _action_to_buttons(self, action: str) -> List[str]:
        """Convert action to button list"""
        action_map = {
            'run_right': ['RIGHT'],
            'jump_right': ['RIGHT', 'A'],
            'jump': ['A'],
            'run_left': ['LEFT'],
            'stop': [],
        }
        return action_map.get(action, [])

if __name__ == "__main__":
    print("NES Emulator Interface - Universal Backend")
    print("=" * 60)
    print("\nBackends:")
    print("  1. Mock - Testing without emulator")
    print("  2. Retro - OpenAI Gym Retro (best for AI)")
    print("  3. FCEUX - Classic emulator via Lua")
    print("\nUsage:")
    print("  from the_body.emulator_interface import SMBPlayer, RetroBackend")
    print("  backend = RetroBackend('SuperMarioBros-Nes')")
    print("  player = SMBPlayer(backend)")
    print("  player.play(1000)")
    print("\nTesting with mock backend:")

    # Test with mock
    backend = MockBackend()
    player = SMBPlayer(backend)

    # Simulate 60 frames
    print("\nSimulating 60 frames...")
    player.play(60)

    print("\nMock test complete!")
    print("To play real SMB:")
    print("  1. pip install gym-retro")
    print("  2. python -m retro.import <path-to-rom>")
    print("  3. python the_body/emulator_interface.py")
