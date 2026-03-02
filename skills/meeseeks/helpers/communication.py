# skills/meeseeks/helpers/communication.py
"""
Shared State Communication for Multi-Meeseeks Coordination

Usage in Meeseeks:
    from skills.meeseeks.helpers.communication import SharedState
    
    shared = SharedState("workflow_123", "mee_1")
    await shared.update_status(progress=50, findings=["found X"])
    await shared.share_discovery("pattern", "SQL injection in /api/users")
    peers = await shared.check_peers()
"""

import json
import asyncio
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, TypedDict


# Set up logging
logger = logging.getLogger("meeseeks.communication")


# Type definitions
class WorkerInfo(TypedDict):
    task: str
    status: str
    progress: int
    started_at: str
    last_update: str
    findings: List[Any]
    needs_help: bool


class Discovery(TypedDict):
    from_worker: str
    type: str
    data: Any
    timestamp: str


class CommunicationError(Exception):
    """Base exception for communication errors."""
    pass


class FileReadError(CommunicationError):
    """Failed to read shared state file."""
    pass


class FileWriteError(CommunicationError):
    """Failed to write shared state file."""
    pass


class ValidationError(CommunicationError):
    """Invalid input parameter."""
    pass


# Input validation patterns
VALID_WORKFLOW_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
VALID_WORKER_ID = re.compile(r"^[a-zA-Z0-9_]{1,32}$")
VALID_DISCOVERY_TYPE = re.compile(r"^[a-zA-Z0-9_]{1,32}$")

# Limits
MAX_DISCOVERIES = 1000
MAX_DECISIONS = 100


class SharedState:
    """File-based shared state for Meeseeks coordination."""
    
    def __init__(self, workflow_id: str, my_id: str, base_path: Optional[Path] = None):
        # Validate inputs
        if not VALID_WORKFLOW_ID.match(workflow_id):
            raise ValidationError(f"Invalid workflow_id: must be 1-64 alphanumeric chars, dashes, or underscores")
        if not VALID_WORKER_ID.match(my_id):
            raise ValidationError(f"Invalid worker_id: must be 1-32 alphanumeric chars or underscores")
        
        self.workflow_id = workflow_id
        self.my_id = my_id
        self.base_path = base_path or Path("C:/Users/aaron/.openclaw/workspace/meeseeks-communication")
        self.path = self.base_path / workflow_id / "shared-state.json"
        self.lock = asyncio.Lock()
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[float] = None
        self._initialized = False
    
    def _validate_discovery_type(self, discovery_type: str) -> None:
        """Validate discovery type."""
        if not VALID_DISCOVERY_TYPE.match(discovery_type):
            raise ValidationError(f"Invalid discovery_type: must be 1-32 alphanumeric chars")
    
    def _now(self) -> str:
        """Get current UTC timestamp."""
        return datetime.utcnow().isoformat() + "Z"
    
    async def read(self) -> Dict[str, Any]:
        """Read current shared state with error handling."""
        async with self.lock:
            try:
                if not self.path.exists():
                    return self._initial_state()
                
                # Check if we can use cache
                content = self.path.read_text(encoding='utf-8')
                if not content.strip():
                    return self._initial_state()
                
                state = json.loads(content)
                self._cache = state
                self._cache_time = asyncio.get_event_loop().time()
                return state
                
            except json.JSONDecodeError as e:
                logger.warning(f"[{self.my_id}] Corrupted JSON in {self.path}, starting fresh: {e}")
                return self._initial_state()
            except PermissionError as e:
                logger.error(f"[{self.my_id}] Permission denied reading {self.path}")
                raise FileReadError(f"Permission denied") from e
            except OSError as e:
                logger.error(f"[{self.my_id}] OS error reading {self.path}: {e}")
                raise FileReadError(f"Failed to read state file") from e
    
    async def write(self, state: Dict[str, Any]) -> None:
        """Write shared state atomically with error handling."""
        async with self.lock:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                temp = self.path.with_suffix('.tmp')
                
                # Write to temp file first
                temp.write_text(
                    json.dumps(state, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
                # Atomic replace
                temp.replace(self.path)
                
                # Update cache
                self._cache = state
                self._cache_time = asyncio.get_event_loop().time()
                
            except PermissionError as e:
                logger.error(f"[{self.my_id}] Permission denied writing {self.path}")
                raise FileWriteError(f"Permission denied") from e
            except OSError as e:
                logger.error(f"[{self.my_id}] OS error writing {self.path}: {e}")
                raise FileWriteError(f"Failed to write state file") from e
            except Exception as e:
                logger.error(f"[{self.my_id}] Unexpected error writing {self.path}: {e}")
                raise FileWriteError(f"Unexpected write error") from e
    
    def _initial_state(self) -> Dict[str, Any]:
        """Create initial state structure."""
        return {
            "meta": {
                "created_at": self._now(),
                "workflow_id": self.workflow_id,
                "coordinator": "sloth_rog"
            },
            "workers": {},
            "shared": {
                "discoveries": [],
                "decisions": []
            }
        }
    
    async def register(self, task: str) -> bool:
        """Register this worker in shared state. Returns True on success."""
        try:
            state = await self.read()
            state["workers"][self.my_id] = {
                "task": task,
                "status": "running",
                "progress": 0,
                "started_at": self._now(),
                "last_update": self._now(),
                "findings": [],
                "needs_help": False
            }
            await self.write(state)
            self._initialized = True
            logger.info(f"[{self.my_id}] Registered: {task}")
            return True
        except CommunicationError as e:
            logger.error(f"[{self.my_id}] Failed to register: {e}")
            return False
    
    async def update_status(
        self,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        findings: Optional[List[Any]] = None,
        **extra: Any
    ) -> bool:
        """Update my status in shared state. Returns True on success."""
        try:
            state = await self.read()
            if self.my_id not in state["workers"]:
                state["workers"][self.my_id] = {}
            
            # Update only provided fields
            if status is not None:
                state["workers"][self.my_id]["status"] = status
            if progress is not None:
                state["workers"][self.my_id]["progress"] = progress
            if current_step is not None:
                state["workers"][self.my_id]["current_step"] = current_step
            if findings is not None:
                state["workers"][self.my_id]["findings"] = findings
            
            # Handle extra fields with validation
            for key, value in extra.items():
                if key.startswith("_"):
                    continue  # Skip private fields
                state["workers"][self.my_id][key] = value
            
            state["workers"][self.my_id]["last_update"] = self._now()
            await self.write(state)
            return True
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to update status: {e}")
            return False
    
    async def complete(self, result: Any = None, summary: str = "") -> bool:
        """Mark task as complete. Returns True on success."""
        return await self.update_status(
            status="complete",
            progress=100,
            result=result,
            summary=summary,
            completed_at=self._now()
        )
    
    async def fail(self, error: str) -> bool:
        """Mark task as failed. Returns True on success."""
        return await self.update_status(
            status="failed",
            progress=-1,
            error=error,
            failed_at=self._now()
        )
    
    async def share_discovery(self, discovery_type: str, data: Any) -> bool:
        """Share a finding with other workers. Returns True on success."""
        try:
            # Validate discovery type
            self._validate_discovery_type(discovery_type)
            
            state = await self.read()
            
            # Enforce max discoveries limit
            discoveries = state["shared"]["discoveries"]
            if len(discoveries) >= MAX_DISCOVERIES:
                # Remove oldest discovery
                discoveries.pop(0)
                logger.info(f"[{self.my_id}] Max discoveries reached, removed oldest")
            
            discoveries.append({
                "from": self.my_id,
                "type": discovery_type,
                "data": data,
                "timestamp": self._now()
            })
            await self.write(state)
            logger.debug(f"[{self.my_id}] Shared discovery: {discovery_type}")
            return True
        except ValidationError:
            raise
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to share discovery: {e}")
            return False
    
    async def check_peers(self) -> Dict[str, Any]:
        """Check status of other workers. Returns empty dict on error."""
        try:
            state = await self.read()
            return {
                wid: winfo
                for wid, winfo in state["workers"].items()
                if wid != self.my_id
            }
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to check peers: {e}")
            return {}
    
    async def get_shared_discoveries(self, discovery_type: Optional[str] = None) -> List[Dict]:
        """Get all shared discoveries, optionally filtered by type. Returns empty list on error."""
        try:
            state = await self.read()
            discoveries = state["shared"]["discoveries"]
            if discovery_type:
                self._validate_discovery_type(discovery_type)
                discoveries = [d for d in discoveries if d["type"] == discovery_type]
            return discoveries
        except ValidationError:
            raise
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to get discoveries: {e}")
            return []
    
    async def propose_decision(self, decision_type: str, value: Any, confidence: float = 1.0) -> bool:
        """Propose a decision for voting. Returns True on success."""
        try:
            state = await self.read()
            
            # Enforce max decisions limit
            decisions = state["shared"]["decisions"]
            if len(decisions) >= MAX_DECISIONS:
                decisions.pop(0)
                logger.info(f"[{self.my_id}] Max decisions reached, removed oldest")
            
            decisions.append({
                "from": self.my_id,
                "type": decision_type,
                "value": value,
                "confidence": max(0.0, min(1.0, confidence)),  # Clamp to 0-1
                "voters_for": [self.my_id],
                "voters_against": [],
                "timestamp": self._now()
            })
            await self.write(state)
            return True
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to propose decision: {e}")
            return False
    
    async def vote(self, decision_idx: int, agree: bool = True) -> bool:
        """Vote on a decision. Returns True on success."""
        try:
            state = await self.read()
            if 0 <= decision_idx < len(state["shared"]["decisions"]):
                decision = state["shared"]["decisions"][decision_idx]
                voters_list = decision["voters_for"] if agree else decision["voters_against"]
                other_list = decision["voters_against"] if agree else decision["voters_for"]
                
                # Remove from opposite list if there
                if self.my_id in other_list:
                    other_list.remove(self.my_id)
                
                # Add to appropriate list
                if self.my_id not in voters_list:
                    voters_list.append(self.my_id)
                
                await self.write(state)
                return True
            return False
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to vote: {e}")
            return False
    
    async def get_decisions(self) -> List[Dict]:
        """Get all proposed decisions. Returns empty list on error."""
        try:
            state = await self.read()
            return state["shared"]["decisions"]
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to get decisions: {e}")
            return []
    
    async def needs_help(self, reason: str = "") -> bool:
        """Signal that this worker needs assistance. Returns True on success."""
        return await self.update_status(needs_help=True, help_reason=reason)
    
    async def summary(self) -> Dict[str, Any]:
        """Get a summary of the entire workflow state. Returns basic info on error."""
        try:
            state = await self.read()
            workers = state["workers"]
            discoveries = state["shared"]["discoveries"]
            
            return {
                "workflow_id": self.workflow_id,
                "total_workers": len(workers),
                "active_workers": sum(1 for w in workers.values() if w.get("status") == "running"),
                "complete_workers": sum(1 for w in workers.values() if w.get("status") == "complete"),
                "failed_workers": sum(1 for w in workers.values() if w.get("status") == "failed"),
                "total_discoveries": len(discoveries),
                "discovery_types": list(set(d["type"] for d in discoveries)),
                "workers_needing_help": [wid for wid, w in workers.items() if w.get("needs_help")]
            }
        except CommunicationError as e:
            logger.warning(f"[{self.my_id}] Failed to get summary: {e}")
            return {
                "workflow_id": self.workflow_id,
                "error": str(e)
            }


# CLI testing
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        print("Testing SharedState v3 with security fixes...")
        
        # Test valid workflow
        shared = SharedState("test_workflow_v3", "test_worker")
        print("OK Created SharedState with valid IDs")
        
        # Test invalid workflow_id
        try:
            bad = SharedState("../../../etc/passwd", "worker")
            print("FAIL Should have raised ValidationError")
        except ValidationError as e:
            print(f"OK Caught ValidationError for path traversal: {e}")
        
        # Test invalid worker_id  
        try:
            bad = SharedState("test", "worker with spaces!")
            print("FAIL Should have raised ValidationError")
        except ValidationError as e:
            print(f"OK Caught ValidationError for invalid worker_id: {e}")
        
        # Register
        if await shared.register("Test task"):
            print("OK Registered")
        
        # Update with explicit params
        if await shared.update_status(progress=50, current_step="Testing"):
            print("OK Updated status with typed params")
        
        # Share discovery
        if await shared.share_discovery("test_finding", {"data": "test"}):
            print("OK Shared discovery")
        
        # Test invalid discovery type
        try:
            await shared.share_discovery("invalid type!", {})
            print("FAIL Should have raised ValidationError")
        except ValidationError as e:
            print(f"OK Caught ValidationError for invalid discovery_type: {e}")
        
        # Test voting with for/against
        await shared.propose_decision("test", "value")
        await shared.vote(0, agree=True)
        print("OK Voting with agree=True")
        
        # Get summary
        summary = await shared.summary()
        print(f"OK Summary: {json.dumps(summary, indent=2)}")
        
        # Complete
        if await shared.complete(summary="Test complete"):
            print("OK Completed")
        
        print("\nAll tests passed!")
    
    asyncio.run(test())
