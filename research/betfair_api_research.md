# Betfair Exchange API Research

**Date:** 2026-03-06
**Purpose:** API integration for potential betting automation

---

## Overview

Betfair Exchange is a betting exchange platform with a comprehensive API (API-NG) that allows:
- Betting operations (place/cancel/replace bets)
- Market data streaming (real-time odds)
- Account operations (balance, P&L)
- Historical data access

---

## Python Library: betfairlightweight

**GitHub:** https://github.com/betcode-org/betfair
**Stars:** 491
**PyPI:** `betfairlightweight`

### Installation
```bash
pip install betfairlightweight
# With speed optimizations (C/Rust libraries):
pip install betfairlightweight[speed]
```

### Supported Python
3.9, 3.10, 3.11, 3.12, 3.13, 3.14

---

## Authentication

### Requirements
1. **App Key** - Get from Betfair Developer Portal
2. **SSL Certificates** - For bot (non-interactive) login
3. **Username/Password**

### Setup SSL Certs
Follow: https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login

Save `.crt` and `.key` files locally (default: `/certs`)

---

## Usage Examples

### Login (Bot/Non-Interactive)
```python
import betfairlightweight

trading = betfairlightweight.APIClient(
    'username',
    'password',
    app_key='app_key',
    certs='/certs'
)
trading.login()
```

### Login (Interactive - Less Secure)
```python
trading = betfairlightweight.APIClient(
    'username',
    'password',
    app_key='app_key'
)
trading.login_interactive()
```

### List Event Types
```python
event_types = trading.betting.list_event_types()
# [<EventTypeResult>, <EventTypeResult>, ...]
```

---

## Available Endpoints

| Endpoint | Purpose |
|----------|---------|
| `trading.login` | Bot login |
| `trading.login_interactive` | Interactive login |
| `trading.keep_alive` | Keep session alive |
| `trading.logout` | End session |
| `trading.betting` | Betting operations |
| `trading.account` | Account operations |
| `trading.navigation` | Navigation data |
| `trading.scores` | Race status API |
| `trading.streaming` | Exchange Stream API |
| `trading.historical` | Historic data API |
| `trading.in_play_service` | In-play service |
| `trading.race_card` | Race card data |

---

## Streaming API

Real-time market data streaming:

```python
from betfairlightweight.filters import (
    streaming_market_filter,
    streaming_market_data_filter,
)

betfair_socket = trading.streaming.create_stream()

market_filter = streaming_market_filter(
    event_type_ids=['7'],        # Horse racing
    country_codes=['IE'],        # Ireland
    market_types=['WIN'],
)
market_data_filter = streaming_market_data_filter(
    fields=['EX_ALL_OFFERS', 'EX_MARKET_DEF'],
    ladder_levels=3
)

betfair_socket.subscribe_to_markets(
    market_filter=market_filter,
    market_data_filter=market_data_filter,
)

betfair_socket.start()  # blocking
```

---

## Historical Data

Access historical market data for backtesting:

```python
# List available data
trading.historic.get_my_data()
# [{'plan': 'Basic Plan', 'purchaseItemId': 1343, 'sport': 'Cricket', ...}]

# Stream historical data (same format as live streaming)
stream = trading.streaming.create_historical_stream(
    file_path='horse-racing-pro-sample',
)
stream.start()

# Or use generator for iteration
stream = trading.streaming.create_historical_generator_stream(
    file_path='horse-racing-pro-sample',
)
g = stream.get_generator()
for market_books in g():
    print(market_books)
```

---

## Integration with Meeseeks AGI

### Potential Use Cases
1. **Market Monitoring** - Spawn Meeseeks to watch specific markets
2. **Automated Betting** - Execute strategies via n8n workflows
3. **Backtesting** - Use historical data to test strategies
4. **Risk Management** - Monitor positions and auto-hedge

### n8n Workflow Idea
```
Webhook Trigger → Betfair API → Process Odds → Decision Logic → Place Bet
                      ↓
               Log to Database
```

### MCP Integration
Could create FastAPI MCP wrapper:
```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

@app.post("/betfair/place-bet")
async def place_bet(market_id: str, selection_id: int, stake: float):
    # Betfair logic here
    pass

mcp = FastApiMCP(app)
mcp.mount()
```

---

## Getting Started Checklist

- [ ] Create Betfair account
- [ ] Apply for Developer App Key
- [ ] Generate SSL certificates
- [ ] Install `betfairlightweight`
- [ ] Test login and basic operations
- [ ] Explore available markets
- [ ] Build first automated strategy

---

## Official Documentation

- **Main Docs:** https://docs.developer.betfair.com/
- **Getting Started:** https://betfair-developer-docs.atlassian.net/wiki/spaces/1smk3cen4v3lu3yomq5qye0ni/pages/2687786/Getting+Started
- **betfairlightweight:** https://github.com/betcode-org/betfair

---

## Notes

- **Rate Limits:** Check Market Data Request Limits in docs
- **Delayed vs Live Key:** Delayed key is free but has 1-60s delay
- **Best Practice:** Read official Best Practice guide
- **Demo Tools:** API Demo Tools available for testing

---

*Research for potential betting automation integration*
