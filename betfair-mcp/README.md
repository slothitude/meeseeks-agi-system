# Betfair MCP Server

A Model Context Protocol (MCP) server for the Betfair Exchange API. This allows AI assistants like Claude to interact with Betfair's betting exchange.

## Features

- **Betting API**: List events, markets, odds, place/cancel orders
- **Account API**: Check balance and account details
- **JSON-RPC Support**: Uses Betfair's official JSON-RPC API
- **TypeScript**: Fully typed for better development experience

## Installation

```bash
npm install
npm run build
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your Betfair credentials:
   ```
   BETFAIR_APP_KEY=your_app_key_here
   BETFAIR_SESSION_TOKEN=your_session_token_here
   ```

### Getting Credentials

1. **App Key**: Get from [Betfair Developer Portal](https://developer.betfair.com/)
2. **Session Token**: Obtain via Betfair's login/certificate authentication

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "betfair": {
      "command": "node",
      "args": ["/path/to/betfair-mcp/dist/index.js"],
      "env": {
        "BETFAIR_APP_KEY": "your_app_key",
        "BETFAIR_SESSION_TOKEN": "your_session_token"
      }
    }
  }
}
```

## Available Tools

### Betting API

| Tool | Description |
|------|-------------|
| `list_event_types` | List all available sports |
| `list_competitions` | List competitions for a sport |
| `list_events` | List events matching criteria |
| `list_market_catalogue` | List available markets |
| `list_market_book` | Get current prices/odds |
| `place_orders` | Place bets (⚠️ REAL MONEY) |
| `cancel_orders` | Cancel bets |
| `list_current_orders` | List open orders |

### Account API

| Tool | Description |
|------|-------------|
| `get_account_funds` | Get account balance |
| `get_account_details` | Get account info |

## Example Usage

### List Sports (Event Types)
```json
{
  "name": "list_event_types",
  "arguments": {
    "filter": {}
  }
}
```

### List Football Competitions
```json
{
  "name": "list_competitions",
  "arguments": {
    "filter": {
      "eventTypeIds": ["1"]
    }
  }
}
```

### Get Market Odds
```json
{
  "name": "list_market_book",
  "arguments": {
    "marketIds": ["1.23456789"],
    "priceProjection": {
      "priceData": ["EX_ALL_OFFERS", "EX_TRADED"]
    }
  }
}
```

### Place a Bet
```json
{
  "name": "place_orders",
  "arguments": {
    "marketId": "1.23456789",
    "instructions": [{
      "selectionId": 12345678,
      "side": "BACK",
      "orderType": "LIMIT",
      "limitOrder": {
        "size": 10.00,
        "price": 2.50,
        "persistenceType": "LAPSE"
      }
    }]
  }
}
```

## ⚠️ Warning

This server can place real bets with real money. Always:
- Test with small amounts first
- Double-check market and selection IDs
- Use `list_market_book` to verify odds before placing orders
- Never share your session token

## API Endpoints

- **Betting API**: `https://api.betfair.com/exchange/betting/json-rpc/v1`
- **Account API**: `https://api.betfair.com/exchange/account/json-rpc/v1`
- **Australian Exchange**: Set `BETFAIR_AUSTRALIAN=true` in environment

## Development

```bash
# Build
npm run build

# Watch mode
npm run dev
```

## License

MIT
