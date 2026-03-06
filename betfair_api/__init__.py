"""
Betfair API MCP Wrapper

FastAPI-based MCP server for Betfair operations.
Exposes betting operations as MCP tools for AI-driven strategies.

Usage:
    pip install fastapi fastapi-mcp uvicorn betfairlightweight
    uvicorn betfair_api:app --host 0.0.0.0 --port 8002

Environment:
    BETFAIR_USERNAME
    BETFAIR_PASSWORD
    BETFAIR_APP_KEY
    BETFAIR_CERTS_PATH (optional, for bot login)
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Try to import betfairlightweight
try:
    import betfairlightweight
    from betfairlightweight.filters import (
        market_filter,
        streaming_market_filter,
        streaming_market_data_filter
    )
    BETFAIR_AVAILABLE = True
except ImportError:
    BETFAIR_AVAILABLE = False


# Enums
class Side(str, Enum):
    BACK = "BACK"
    LAY = "LAY"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    LIMIT_ON_CLOSE = "LIMIT_ON_CLOSE"
    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"


# Models
class LoginRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    app_key: Optional[str] = None
    interactive: bool = False  # True for interactive login (no certs)


class LoginResponse(BaseModel):
    status: str
    session_token: Optional[str] = None
    message: str


class MarketFilter(BaseModel):
    event_type_ids: Optional[List[str]] = None
    country_codes: Optional[List[str]] = None
    market_types: Optional[List[str]] = None


class MarketCatalogueRequest(BaseModel):
    filter: MarketFilter
    max_results: int = 100


class MarketCatalogueResponse(BaseModel):
    markets: List[Dict[str, Any]]
    count: int


class PlaceBetRequest(BaseModel):
    market_id: str
    selection_id: int
    side: Side
    order_type: OrderType
    size: float
    price: Optional[float] = None  # Required for LIMIT orders


class PlaceBetResponse(BaseModel):
    status: str
    bet_id: Optional[str] = None
    message: str


class StreamingRequest(BaseModel):
    event_type_ids: List[str]
    country_codes: Optional[List[str]] = None
    market_types: Optional[List[str]] = None
    ladder_levels: int = 3


# App
app = FastAPI(
    title="Betfair API MCP Wrapper",
    description="MCP tools for Betfair betting operations",
    version="0.1.0"
)

# MCP Integration
mcp = FastApiMCP(app)

# Global trading client
trading_client = None


def get_trading_client():
    """Get or create Betfair trading client."""
    global trading_client

    if not BETFAIR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="betfairlightweight not installed. Run: pip install betfairlightweight"
        )

    if trading_client is None:
        username = os.environ.get("BETFAIR_USERNAME")
        password = os.environ.get("BETFAIR_PASSWORD")
        app_key = os.environ.get("BETFAIR_APP_KEY")
        certs = os.environ.get("BETFAIR_CERTS_PATH", "/certs")

        if not all([username, password, app_key]):
            raise HTTPException(
                status_code=500,
                detail="Missing Betfair credentials. Set BETFAIR_USERNAME, BETFAIR_PASSWORD, BETFAIR_APP_KEY"
            )

        trading_client = betfairlightweight.APIClient(
            username,
            password,
            app_key=app_key,
            certs=certs
        )

    return trading_client


# Endpoints

@app.get("/")
async def root():
    """API status"""
    return {
        "status": "operational",
        "service": "betfair-api-mcp",
        "betfair_available": BETFAIR_AVAILABLE,
        "authenticated": trading_client is not None and trading_client.session_token is not None
    }


@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest = None):
    """
    Login to Betfair API

    Uses environment variables if not provided:
    - BETFAIR_USERNAME
    - BETFAIR_PASSWORD
    - BETFAIR_APP_KEY
    - BETFAIR_CERTS_PATH (for bot login)
    """
    client = get_trading_client()

    try:
        if request and request.interactive:
            client.login_interactive()
        else:
            client.login()

        return LoginResponse(
            status="success",
            session_token=client.session_token,
            message="Logged in successfully"
        )
    except Exception as e:
        return LoginResponse(
            status="error",
            message=str(e)
        )


@app.post("/logout")
async def logout():
    """Logout from Betfair API"""
    client = get_trading_client()

    try:
        client.logout()
        return {"status": "success", "message": "Logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/event-types")
async def list_event_types():
    """List all available event types (sports)"""
    client = get_trading_client()

    try:
        event_types = client.betting.list_event_types()
        return {
            "event_types": [
                {"id": et.event_type.id, "name": et.event_type.name}
                for et in event_types
            ],
            "count": len(event_types)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/markets", response_model=MarketCatalogueResponse)
async def list_markets(request: MarketCatalogueRequest):
    """
    List available markets

    Common event_type_ids:
    - 1: Soccer
    - 2: Tennis
    - 3: Golf
    - 4: Cricket
    - 5: Rugby Union
    - 7: Horse Racing
    """
    client = get_trading_client()

    try:
        # Build filter
        filter_params = {}
        if request.filter.event_type_ids:
            filter_params['event_type_ids'] = request.filter.event_type_ids
        if request.filter.country_codes:
            filter_params['country_codes'] = request.filter.country_codes
        if request.filter.market_types:
            filter_params['market_types'] = request.filter.market_types

        markets = client.betting.list_market_catalogue(
            filter=market_filter(**filter_params),
            max_results=request.max_results
        )

        return MarketCatalogueResponse(
            markets=[
                {
                    "market_id": m.market_id,
                    "market_name": m.market_name,
                    "event_name": m.event.name if m.event else None,
                    "total_matched": m.total_matched
                }
                for m in markets
            ],
            count=len(markets)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/{market_id}")
async def get_market_details(market_id: str):
    """Get detailed information about a specific market"""
    client = get_trading_client()

    try:
        books = client.betting.list_market_book(market_ids=[market_id])

        if not books:
            raise HTTPException(status_code=404, detail="Market not found")

        book = books[0]
        return {
            "market_id": book.market_id,
            "status": book.status,
            "inplay": book.inplay,
            "total_matched": book.total_matched,
            "runners": [
                {
                    "selection_id": r.selection_id,
                    "runner_name": r.runner_name,
                    "status": r.status,
                    "last_price_traded": r.last_price_traded,
                    "total_matched": r.total_matched
                }
                for r in book.runners
            ] if hasattr(book, 'runners') else []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bet/place", response_model=PlaceBetResponse)
async def place_bet(request: PlaceBetRequest):
    """
    Place a bet on Betfair

    WARNING: This uses real money if connected to live API.
    Use delayed app key for testing.
    """
    client = get_trading_client()

    if not BETFAIR_AVAILABLE:
        raise HTTPException(status_code=503, detail="betfairlightweight not installed")

    try:
        # Build order instructions
        from betfairlightweight.filters import place_instruction

        instruction = place_instruction(
            selection_id=request.selection_id,
            side=request.side.value,
            order_type=request.order_type.value,
            limit_order={
                "size": request.size,
                "price": request.price,
                "persistence_type": "LAPSE"
            } if request.order_type == OrderType.LIMIT and request.price else None
        )

        result = client.betting.place_orders(
            market_id=request.market_id,
            instructions=[instruction]
        )

        if result.status == "SUCCESS":
            return PlaceBetResponse(
                status="success",
                bet_id=result.place_instruction_reports[0].bet_id if result.place_instruction_reports else None,
                message="Bet placed successfully"
            )
        else:
            return PlaceBetResponse(
                status="error",
                message=result.error_code or "Unknown error"
            )
    except Exception as e:
        return PlaceBetResponse(
            status="error",
            message=str(e)
        )


@app.get("/account/balance")
async def get_account_balance():
    """Get account balance"""
    client = get_trading_client()

    try:
        funds = client.account.get_account_funds()
        return {
            "available_balance": funds.available_to_bet_balance,
            "exposure": funds.exposure,
            "total_balance": funds.total_balance if hasattr(funds, 'total_balance') else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/streaming/start")
async def start_streaming(request: StreamingRequest):
    """
    Start streaming market data

    Returns connection instructions for WebSocket streaming.
    """
    if not BETFAIR_AVAILABLE:
        raise HTTPException(status_code=503, detail="betfairlightweight not installed")

    client = get_trading_client()

    try:
        # Create stream
        stream = client.streaming.create_stream()

        # Build filters
        market_filter = streaming_market_filter(
            event_type_ids=request.event_type_ids,
            country_codes=request.country_codes,
            market_types=request.market_types
        )

        market_data = streaming_market_data_filter(
            fields=['EX_ALL_OFFERS', 'EX_MARKET_DEF'],
            ladder_levels=request.ladder_levels
        )

        return {
            "status": "ready",
            "message": "Stream configured. Use stream.subscribe_to_markets() and stream.start() in Python.",
            "config": {
                "market_filter": request.dict(),
                "ladder_levels": request.ladder_levels
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "betfair_available": BETFAIR_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


# Mount MCP server
mcp.mount()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
