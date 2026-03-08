"""
Distress Signal Protocol for the_body.

When a skill fails repeatedly, emit DISTRESS_SIGNAL upstream.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class DistressSignal:
    """
    Signal emitted when a skill pattern fails repeatedly.
    """
    tool: str
    pattern: str
    failure_count: int
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for upstream consumption."""
        return {
            "type": "DISTRESS_SIGNAL",
            "tool": self.tool,
            "pattern": self.pattern,
            "failure_count": self.failure_count,
            "message": self.message,
            "timestamp": self.timestamp,
            "context": self.context
        }
    
    def to_json(self) -> str:
        """JSON string for transmission."""
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        return f"🚨 DISTRESS: {self.tool}/{self.pattern} failed {self.failure_count}x - {self.message}"


class DistressTracker:
    """
    Track failures and emit distress signals when threshold exceeded.
    """
    
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.failures: Dict[str, int] = {}
        self.signals: list[DistressSignal] = []
    
    def record_failure(self, tool: str, pattern: str, context: Optional[Dict] = None) -> Optional[DistressSignal]:
        """
        Record failure and emit signal if threshold exceeded.
        """
        key = f"{tool}:{pattern}"
        self.failures[key] = self.failures.get(key, 0) + 1
        
        if self.failures[key] >= self.threshold:
            signal = DistressSignal(
                tool=tool,
                pattern=pattern,
                failure_count=self.failures[key],
                message=f"Pattern '{pattern}' failed {self.failures[key]}x on '{tool}'",
                context=context or {}
            )
            self.signals.append(signal)
            return signal
        
        return None
    
    def reset(self, tool: str, pattern: str) -> None:
        """Reset failure count after success."""
        key = f"{tool}:{pattern}"
        self.failures.pop(key, None)
    
    def get_failure_count(self, tool: str, pattern: str) -> int:
        """Get current failure count."""
        return self.failures.get(f"{tool}:{pattern}", 0)
