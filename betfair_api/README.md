# Betfair API MCP Wrapper

FastAPI-based MCP server for Betfair operations.

## Installation

```bash
cd betfair_api
pip install -r requirements.txt
```

## Setup

### 1. Get Betfair Credentials

1. Create Betfair account
2. Apply for Developer App Key: https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Application+Keys
3. Generate SSL certificates for bot login: https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login

### 2. Set Environment Variables

```bash
export BETFAIR_USERNAME="your_username"
export BETFAIR_PASSWORD="your_password"
export BETFAIR_APP_KEY="your_app_key"
export BETFAIR_CERTS_PATH="/path/to/certs"  # Optional
```

### 3. Run Server

```bash
uvicorn betfair_api:app --host 0.0.0.0 --port 8002
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| POST | `/login` | Login to Betfair |
| POST | `/logout` | Logout from Betfair |
| GET | `/event-types` | List all sports |
| POST | `/markets` | List available markets |
| GET | `/market/{market_id}` | Get market details |
| POST | `/bet/place` | Place a bet |
| GET | `/account/balance` | Get account balance |
| POST | `/streaming/start` | Start market streaming |

## MCP Integration

This server is MCP-enabled via `fastapi-mcp`. All endpoints are exposed as MCP tools.

### Example Usage

```python
# List event types
event_types = await call_mcp("betfair_list_event_types", {})

# List horse racing markets
markets = await call_mcp("betfair_list_markets", {
    "filter": {
        "event_type_ids": ["7"],
        "country_codes": ["GB"]
    },
    "max_results": 10
})

# Place a bet
result = await call_mcp("betfair_place_bet", {
    "market_id": "1.12345678",
    "selection_id": 12345,
    "side": "BACK",
    "order_type": "LIMIT",
    "size": 10.00,
    "price": 2.50
})
```

## n8n Integration

This API can be called from n8n workflows:

1. Add HTTP Request node
2. Set URL to `http://localhost:8002/markets`
3. Set method to POST
4. Add body with market filter

## Warning

⚠️ **This uses real money if connected to live API.**

Use a **delayed app key** for testing. Live operations require:
- Live app key
- SSL certificates
- Funded account

## Common Event Type IDs

| ID | Sport |
|----|-------|
| 1 | Soccer |
| 2 | Tennis |
| 3 | Golf |
| 4 | Cricket |
| 5 | Rugby Union |
| 7 | Horse Racing |
| 8 | Boxing |
| 10 | Basketball |
| 11 | American Football |

## Resources

- [Betfair API Docs](https://docs.developer.betfair.com/)
- [betfairlightweight](https://github.com/betcode-org/betfair)
- [FastAPI MCP](https://github.com/tadata-org/fastapi_mcp)
