"""
Reflection Store - Persistent failure context storage for Meeseeks feedback loop.

Stores failure contexts in Knowledge Graph for cross-attempt learning.
"""

import json
from datetime import datetime
from typing import Optional
from pathlib import Path

class ReflectionStore:
    """
    Stores and retrieves reflection memory for Meeseeks retry loop.
    
    Storage backends:
    - Knowledge Graph (primary) - via MCP
    - Local JSON (fallback) - for offline/debug
    """
    
    def __init__(self, kg_client=None, local_path: str = None):
        self.kg_client = kg_client
        self.local_path = Path(local_path or "skills/meeseeks/reflections.json")
        self._ensure_local_file()
    
    def _ensure_local_file(self):
        """Ensure local JSON file exists."""
        if not self.local_path.exists():
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            self.local_path.write_text(json.dumps({"reflections": {}}))
    
    def store_failure(self, task_id: str, attempt: int, error: str, 
                      approach: str, reason: str, context: dict = None):
        """
        Store a failure context for future retries.
        
        Args:
            task_id: Unique identifier for the task
            attempt: Which attempt number failed
            error: The error message
            approach: What approach was tried
            reason: Why it failed (analyzed)
            context: Additional context (files, commands, etc.)
        """
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "attempt": attempt,
            "error": error,
            "approach": approach,
            "reason": reason,
            "context": context or {}
        }
        
        # Store in KG if available
        if self.kg_client:
            self._store_in_kg(task_id, reflection)
        
        # Always store locally as backup
        self._store_locally(task_id, reflection)
        
        return reflection
    
    def get_failures(self, task_id: str) -> list:
        """
        Retrieve all failure contexts for a task.
        
        Args:
            task_id: The task identifier
            
        Returns:
            List of reflection dicts, ordered by attempt
        """
        if self.kg_client:
            return self._get_from_kg(task_id)
        return self._get_locally(task_id)
    
    def format_reflections(self, task_id: str) -> str:
        """
        Format failures for injection into retry prompt.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Formatted string for prompt injection
        """
        failures = self.get_failures(task_id)
        
        if not failures:
            return ""
        
        lines = ["--- PREVIOUS ATTEMPTS FAILED ---"]
        
        for f in failures:
            lines.append(f"\n### Attempt {f['attempt']}:")
            lines.append(f"**Error:** {f['error']}")
            lines.append(f"**Approach tried:** {f['approach']}")
            lines.append(f"**Why it failed:** {f['reason']}")
        
        lines.append("\n⚠️ The above approaches did NOT work. Try a DIFFERENT approach.")
        lines.append("Analyze why previous attempts failed before proceeding.")
        
        return "\n".join(lines)
    
    def clear_failures(self, task_id: str):
        """Clear all failures for a task (after success)."""
        if self.kg_client:
            self._clear_from_kg(task_id)
        self._clear_locally(task_id)
    
    # --- Knowledge Graph Backend ---
    
    def _store_in_kg(self, task_id: str, reflection: dict):
        """Store reflection in Knowledge Graph entity."""
        entity_name = f"Task_Failures_{task_id}"
        observation = (
            f"Attempt {reflection['attempt']}: {reflection['approach']} failed - "
            f"{reflection['reason']} (Error: {reflection['error'][:100]})"
        )
        
        # Would call: goose run -t "Use mcpdocker/add_observation..."
        # For now, this is a placeholder for the actual MCP call
        if self.kg_client:
            try:
                self.kg_client.add_observation(entity_name, observation)
            except Exception as e:
                print(f"KG store failed: {e}, using local fallback")
    
    def _get_from_kg(self, task_id: str) -> list:
        """Retrieve reflections from Knowledge Graph."""
        entity_name = f"Task_Failures_{task_id}"
        
        if self.kg_client:
            try:
                entity = self.kg_client.read_entity(entity_name)
                # Parse observations into reflection format
                return self._parse_kg_observations(entity.get('observations', []))
            except Exception as e:
                print(f"KG retrieve failed: {e}, using local fallback")
        
        return self._get_locally(task_id)
    
    def _parse_kg_observations(self, observations: list) -> list:
        """Parse KG observations back into reflection dicts."""
        reflections = []
        for obs in observations:
            # Parse "Attempt N: approach failed - reason (Error: ...)"
            try:
                parts = obs.split(": ", 1)
                attempt = int(parts[0].replace("Attempt ", ""))
                rest = parts[1]
                
                approach_end = rest.find(" failed - ")
                approach = rest[:approach_end]
                
                reason_start = approach_end + len(" failed - ")
                reason_end = rest.find(" (Error: ")
                reason = rest[reason_start:reason_end]
                
                error = rest[reason_end + len(" (Error: "):-1]
                
                reflections.append({
                    "attempt": attempt,
                    "approach": approach,
                    "reason": reason,
                    "error": error
                })
            except:
                continue
        
        return sorted(reflections, key=lambda x: x['attempt'])
    
    def _clear_from_kg(self, task_id: str):
        """Clear reflections from Knowledge Graph."""
        entity_name = f"Task_Failures_{task_id}"
        
        if self.kg_client:
            try:
                self.kg_client.delete_entity(entity_name)
            except:
                pass
    
    # --- Local JSON Backend ---
    
    def _store_locally(self, task_id: str, reflection: dict):
        """Store reflection in local JSON file."""
        data = json.loads(self.local_path.read_text())
        
        if task_id not in data["reflections"]:
            data["reflections"][task_id] = []
        
        data["reflections"][task_id].append(reflection)
        
        self.local_path.write_text(json.dumps(data, indent=2))
    
    def _get_locally(self, task_id: str) -> list:
        """Retrieve reflections from local JSON file."""
        data = json.loads(self.local_path.read_text())
        return data["reflections"].get(task_id, [])
    
    def _clear_locally(self, task_id: str):
        """Clear reflections from local JSON file."""
        data = json.loads(self.local_path.read_text())
        
        if task_id in data["reflections"]:
            del data["reflections"][task_id]
        
        self.local_path.write_text(json.dumps(data, indent=2))


# Singleton instance
_store = None

def get_store(kg_client=None) -> ReflectionStore:
    """Get or create the reflection store singleton."""
    global _store
    if _store is None:
        _store = ReflectionStore(kg_client)
    return _store


# Convenience functions
def store_failure(task_id: str, attempt: int, error: str, 
                  approach: str, reason: str, context: dict = None):
    """Store a failure context."""
    return get_store().store_failure(task_id, attempt, error, approach, reason, context)

def get_failures(task_id: str) -> list:
    """Get all failures for a task."""
    return get_store().get_failures(task_id)

def format_reflections(task_id: str) -> str:
    """Format failures for prompt injection."""
    return get_store().format_reflections(task_id)

def clear_failures(task_id: str):
    """Clear failures after success."""
    return get_store().clear_failures(task_id)
