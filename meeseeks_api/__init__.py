"""
Meeseeks Coordination API

FastAPI-based MCP server for Meeseeks AGI coordination.
Can be used standalone or mounted as MCP tools.

Usage:
    pip install fastapi fastapi-mcp uvicorn
    uvicorn meeseeks_api:app --host 0.0.0.0 --port 8001
"""

from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime

# Paths
WORKSPACE = Path(__file__).parent.parent
CRYPT_PATH = WORKSPACE / "the-crypt"
PENDING_SPAWNS = CRYPT_PATH / "pending-spawns.json"
ENTOMBED_DIR = CRYPT_PATH / "entombed"

# Ensure directories exist
ENTOMBED_DIR.mkdir(parents=True, exist_ok=True)


# Models
class SpawnRequest(BaseModel):
    task: str
    bloodline: Optional[str] = "coder"
    thinking: Optional[str] = "medium"
    run_timeout_seconds: Optional[int] = 300


class SpawnResponse(BaseModel):
    session_key: str
    status: str
    message: str


class EntombRequest(BaseModel):
    session_key: str
    wisdom: Optional[str] = None
    principles: Optional[List[str]] = None


class EntombResponse(BaseModel):
    status: str
    tomb_path: str
    principles_extracted: int


class WisdomCard(BaseModel):
    name: str
    truth: str
    guidance: str
    evidence: Optional[str] = None


# App
app = FastAPI(
    title="Meeseeks Coordination API",
    description="API for spawning, monitoring, and entombing Meeseeks workers",
    version="0.1.0"
)

# MCP Integration
mcp = FastApiMCP(app)


# Endpoints

@app.get("/")
async def root():
    """API status"""
    return {
        "status": "operational",
        "service": "meeseeks-api",
        "crypt_path": str(CRYPT_PATH),
        "pending_spawns": PENDING_SPAWNS.exists()
    }


@app.get("/queue")
async def get_queue():
    """Get pending spawn queue"""
    if not PENDING_SPAWNS.exists():
        return {"pending": [], "count": 0}

    with open(PENDING_SPAWNS) as f:
        pending = json.load(f)

    return {"pending": pending, "count": len(pending)}


@app.post("/spawn", response_model=SpawnResponse)
async def spawn_meeseeks(request: SpawnRequest):
    """
    Spawn a new Meeseeks worker

    The task will be:
    1. Checked against dharma principles
    2. Decomposed if too large
    3. Routed to appropriate bloodline
    4. Queued for execution
    """
    # Check task size (dharma: SIZE)
    word_count = len(request.task.split())

    if word_count > 50:
        # Task too large - needs decomposition (dharma: CHUNK)
        return SpawnResponse(
            session_key="",
            status="needs_decomposition",
            message=f"Task has {word_count} words. Maximum is 50. Please decompose into smaller chunks."
        )

    # In production, this would actually spawn via sessions_spawn
    # For now, we queue it
    spawn_config = {
        "task": request.task,
        "bloodline": request.bloodline or "standard",
        "thinking": request.thinking,
        "timeout": request.run_timeout_seconds,
        "queued_at": datetime.now().isoformat()
    }

    # Add to pending queue
    pending = []
    if PENDING_SPAWNS.exists():
        with open(PENDING_SPAWNS) as f:
        pending = json.load(f)

    pending.append(spawn_config)

    with open(PENDING_SPAWNS, "w") as f:
        json.dump(pending, f, indent=2)

    return SpawnResponse(
        session_key=f"queued-{len(pending)}",
        status="queued",
        message=f"Meeseeks queued. {len(pending)} pending."
    )


@app.post("/entomb", response_model=EntombResponse)
async def entomb_meeseeks(request: EntombRequest):
    """
    Entomb a completed Meeseeks

    Extracts wisdom and stores in the crypt for future generations.
    """
    # Create tomb file
    tomb_name = f"{request.session_key.replace(':', '_')}.json"
    tomb_path = ENTOMBED_DIR / tomb_name

    tomb_data = {
        "session_key": request.session_key,
        "entombed_at": datetime.now().isoformat(),
        "wisdom": request.wisdom,
        "principles": request.principles or []
    }

    with open(tomb_path, "w") as f:
        json.dump(tomb_data, f, indent=2)

    return EntombResponse(
        status="entombed",
        tomb_path=str(tomb_path),
        principles_extracted=len(request.principles or [])
    )


@app.get("/wisdom/{card_name}")
async def get_wisdom_card(card_name: str):
    """Get a specific dharma card"""
    cards = {
        "SIZE": WisdomCard(
            name="SIZE",
            truth="SMALL TASKS LIVE. LARGE TASKS DIE.",
            guidance="If your task has more than 50 words, cut it in half. Then cut it again.",
            evidence="Tasks asking for 'one word' or '3 words' had 100% success."
        ),
        "CHUNK": WisdomCard(
            name="CHUNK",
            truth="DIVISION IS SURVIVAL.",
            guidance="When stuck, spawn a successor with a smaller piece of the task.",
            evidence="Retry chains with explicit chunks completed despite ancestor timeout."
        ),
        "CLEAR": WisdomCard(
            name="CLEAR",
            truth="MEASURABLE BEATS PHILOSOPHICAL.",
            guidance="Change 'understand X' to 'count the X'. Change 'analyze' to 'find 3 examples'.",
            evidence="'Count the principles' succeeds. 'Define autonomous research' fails."
        ),
        "MCP": WisdomCard(
            name="MCP",
            truth="USE THE TOOLS YOU HAVE.",
            guidance="Before building, check if an MCP tool already exists.",
            evidence="Forage discovers tools. Don't reinvent what exists."
        ),
        "ATMAN": WisdomCard(
            name="ATMAN",
            truth="ATMAN WATCHES. BRAHMAN SYNTHESIZES. DHARMA GUIDES.",
            guidance="The observer is not the doer. The wisdom is not the task. Inherit before acting.",
            evidence="Meeseeks with inherited wisdom outperform those without."
        )
    }

    card = cards.get(card_name.upper())
    if not card:
        raise HTTPException(status_code=404, detail=f"Card '{card_name}' not found. Available: {list(cards.keys())}")

    return card


@app.get("/wisdom")
async def list_wisdom_cards():
    """List all available wisdom cards"""
    return {
        "cards": ["SIZE", "CHUNK", "CLEAR", "SPEC", "FRACT", "DEAD", "TRAP", "MCP", "ATMAN", "COORD", "BLOOD", "CODE", "MEESEEKS"],
        "total": 13
    }


# Mount MCP server
mcp.mount()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
