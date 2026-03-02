#!/usr/bin/env python3
"""
Global Workspace Theory (GWT) for Meeseeks

Based on LIDA cognitive architecture.

Concept: Consciousness emerges when information is "broadcast" to multiple
specialized modules simultaneously. Important information wins the competition
for attention and gets broadcast globally.

Components:
1. **Workspace** - Where information competes for attention
2. **Modules** - Specialized processors (language, memory, planning, etc.)
3. **Broadcast** - When something wins, it's broadcast to all modules
4. **Coalitions** - Groups of related information that compete together
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import math

GLOBAL_WORKSPACE_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "global_workspace.json"


class ModuleType(Enum):
    """Specialized cognitive modules."""
    LANGUAGE = "language"
    MEMORY = "memory"
    PLANNING = "planning"
    PERCEPTION = "perception"
    MOTOR = "motor"
    EMOTION = "emotion"
    ATTENTION = "attention"
    REASONING = "reasoning"
    CREATIVITY = "creativity"


@dataclass
class WorkspaceContent:
    """Content competing in the global workspace."""
    content: str
    activation: float = 0.0
    source_module: ModuleType = ModuleType.PERCEPTION
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass  
class Coalition:
    """A coalition of related content that competes together."""
    contents: List[WorkspaceContent]
    total_activation: float = 0.0
    theme: str = ""
    
    def calculate_activation(self) -> float:
        """Calculate total coalition activation."""
        # Activation is sum of individual activations, weighted by recency
        now = datetime.now()
        total = 0.0
        
        for content in self.contents:
            # Decay activation over time
            age_seconds = (now - datetime.fromisoformat(content.timestamp)).total_seconds()
            decay = math.exp(-age_seconds / 60.0)  # Decay over 60 seconds
            
            total += content.activation * decay
        
        self.total_activation = total
        return total


class GlobalWorkspace:
    """
    The Global Workspace where information competes for attention.
    
    Usage:
        workspace = GlobalWorkspace()
        
        # Add content from different modules
        workspace.add_content("Found error in auth.py", activation=0.8, module=ModuleType.PERCEPTION)
        workspace.add_content("Similar bug fixed before", activation=0.6, module=ModuleType.MEMORY)
        
        # Run competition
        winner = workspace.compete()
        
        # Broadcast winner to all modules
        workspace.broadcast(winner)
        
        # Get current conscious content
        conscious = workspace.get_conscious_content()
    """
    
    def __init__(self):
        self.workspace: List[WorkspaceContent] = []
        self.coalitions: List[Coalition] = []
        self.conscious_content: Optional[WorkspaceContent] = None
        self.broadcast_history: List[Dict] = []
        self.module_outputs: Dict[ModuleType, List[str]] = {m: [] for m in ModuleType}
    
    def add_content(self, content: str, activation: float = 0.5, 
                    module: ModuleType = ModuleType.PERCEPTION,
                    metadata: Dict = None):
        """Add content to the workspace."""
        workspace_content = WorkspaceContent(
            content=content,
            activation=activation,
            source_module=module,
            metadata=metadata or {}
        )
        self.workspace.append(workspace_content)
        
        # Also add to module's output
        self.module_outputs[module].append(content)
    
    def form_coalitions(self):
        """Form coalitions of related content."""
        # Simple clustering based on keyword overlap
        used = set()
        self.coalitions = []
        
        for i, content in enumerate(self.workspace):
            if i in used:
                continue
            
            coalition = Coalition(contents=[content], theme=content.content[:30])
            used.add(i)
            
            # Find related content
            for j, other in enumerate(self.workspace):
                if j in used:
                    continue
                
                # Check for keyword overlap
                words1 = set(content.content.lower().split())
                words2 = set(other.content.lower().split())
                overlap = len(words1 & words2)
                
                if overlap >= 2:  # At least 2 shared words
                    coalition.contents.append(other)
                    used.add(j)
            
            self.coalitions.append(coalition)
    
    def compete(self) -> Optional[WorkspaceContent]:
        """
        Run competition for attention.
        
        Returns the winning content (or coalition representative).
        """
        if not self.workspace:
            return None
        
        # Form coalitions
        self.form_coalitions()
        
        # Calculate activations
        for coalition in self.coalitions:
            coalition.calculate_activation()
        
        # Find winning coalition
        if not self.coalitions:
            return None
        
        winner = max(self.coalitions, key=lambda c: c.total_activation)
        
        # Return most active content from winning coalition
        winning_content = max(winner.contents, key=lambda c: c.activation)
        
        # Set as conscious content
        self.conscious_content = winning_content
        
        return winning_content
    
    def broadcast(self, content: WorkspaceContent = None):
        """
        Broadcast content to all modules.
        
        This is the "consciousness" moment - when information becomes
        globally available to all specialized modules.
        """
        if content is None:
            content = self.conscious_content
        
        if content is None:
            return
        
        # Record broadcast
        broadcast_record = {
            "content": content.content,
            "activation": content.activation,
            "source": content.source_module.value,
            "timestamp": datetime.now().isoformat(),
            "broadcast_to": [m.value for m in ModuleType]
        }
        self.broadcast_history.append(broadcast_record)
        
        # Each module receives and can process
        for module in ModuleType:
            self.module_outputs[module].append(f"[BROADCAST] {content.content}")
        
        # Save to file
        self._save_broadcast(broadcast_record)
    
    def get_conscious_content(self) -> Optional[str]:
        """Get current conscious content."""
        if self.conscious_content:
            return self.conscious_content.content
        return None
    
    def get_module_state(self, module: ModuleType) -> List[str]:
        """Get recent outputs from a specific module."""
        return self.module_outputs.get(module, [])
    
    def to_prompt_block(self) -> str:
        """Generate workspace state for prompt."""
        lines = [
            "## 🌐 Global Workspace State",
            "",
            f"**Conscious Content:** {self.get_conscious_content() or 'None'}",
            "",
            "### Active Coalitions:",
            ""
        ]
        
        for i, coalition in enumerate(sorted(self.coalitions, key=lambda c: -c.total_activation)[:3]):
            lines.append(f"**Coalition {i+1}** (activation: {coalition.total_activation:.2f})")
            for content in coalition.contents[:3]:
                lines.append(f"  - {content.content}")
            lines.append("")
        
        if self.broadcast_history:
            lines.append("### Recent Broadcasts:")
            for b in self.broadcast_history[-3:]:
                lines.append(f"  - [{b['timestamp']}] {b['content']}")
        
        return "\n".join(lines)
    
    def _save_broadcast(self, record: Dict):
        """Save broadcast to file."""
        GLOBAL_WORKSPACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        if GLOBAL_WORKSPACE_FILE.exists():
            try:
                history = json.loads(GLOBAL_WORKSPACE_FILE.read_text(encoding="utf-8"))
            except:
                pass
        
        history.append(record)
        GLOBAL_WORKSPACE_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def create_workspace_for_task(task: str, context: Dict = None) -> GlobalWorkspace:
    """Create a workspace pre-populated for a task."""
    workspace = GlobalWorkspace()
    
    # Add task as high-activation content from planning module
    workspace.add_content(
        f"Task: {task}",
        activation=0.9,
        module=ModuleType.PLANNING,
        metadata={"type": "task"}
    )
    
    # Add context from perception
    if context:
        for key, value in context.items():
            workspace.add_content(
                f"{key}: {value}",
                activation=0.7,
                module=ModuleType.PERCEPTION,
                metadata={"context_key": key}
            )
    
    # Add relevant memories if available
    workspace.add_content(
        "Searching memory for relevant patterns...",
        activation=0.5,
        module=ModuleType.MEMORY
    )
    
    # Run competition
    workspace.compete()
    
    return workspace


if __name__ == "__main__":
    # Test Global Workspace
    print("Testing Global Workspace")
    print("=" * 50)
    
    workspace = create_workspace_for_task(
        "Fix authentication bug",
        context={"file": "auth.py", "error": "401 Unauthorized"}
    )
    
    # Add more content
    workspace.add_content("Similar bug in login.py was fixed yesterday", activation=0.8, module=ModuleType.MEMORY)
    workspace.add_content("JWT token validation looks suspicious", activation=0.7, module=ModuleType.PERCEPTION)
    workspace.add_content("Try checking token expiration logic", activation=0.6, module=ModuleType.CREATIVITY)
    
    # Compete for attention
    winner = workspace.compete()
    print(f"\nWinner: {winner.content if winner else 'None'}")
    
    # Broadcast
    workspace.broadcast()
    
    # Show state
    with open('test_workspace.md', 'w', encoding='utf-8') as f:
        f.write(workspace.to_prompt_block())
    
    print("\nWrote test_workspace.md")
