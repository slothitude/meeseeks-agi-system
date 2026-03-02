# 008 Betfair Trading System - Full Analysis

## Overview

This is a **complete Betfair scalping system** with multiple components:
- API integration with cert auth
- Multiple trading bots
- GUI dashboard
- Auto-hedging
- Risk management
- Research documentation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BETFAIR API LAYER                        │
│  aus_cert_login.py → betfair_config.json                    │
│  (Certificate authentication, session token)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE API CLIENT                           │
│  betfair_api.py                                              │
│  - place_back_bet() / place_lay_bet()                        │
│  - get_market_book() / get_current_orders()                  │
│  - cancel_orders()                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TRADING ENGINES                           │
│                                                              │
│  scalping_bot.py      → Basic scalper (1-2 ticks)           │
│  scalping_engine.py   → Advanced scanner with CLI           │
│  smart_trader.py      → 3rd favorite specialist             │
│  auto_trader.py       → Automated execution                 │
│  live_trader.py       → In-play trading                     │
│  multi_trader.py      → Multi-market execution              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    HEDGING LAYER                             │
│                                                              │
│  auto_hedge.py        → Monitors positions, auto-hedges     │
│  hedge_all.py         → Batch hedge all positions           │
│  auto_hedge.py        → Standalone hedge module             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    RISK MANAGEMENT                           │
│                                                              │
│  risk_manager.py      → Stake sizing, daily limits          │
│  - Max 1% per trade                                          │
│  - Daily loss limit: $1                                      │
│  - Daily profit target: $2                                   │
│  - Max 5 consecutive losses                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│                                                              │
│  trading_dashboard.py       → Full GUI                       │
│  trading_dashboard_hedge.py → GUI with auto-hedge           │
│  trading_dashboard_smart.py → Smart trading GUI             │
│  scalping_gui.py            → Scalping interface            │
│  gui_trader.py              → General GUI                   │
│  cashout_timer_gui.py       → Cashout countdown             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Authentication (aus_cert_login.py)
- Uses **certificate-based login** (non-interactive)
- Betfair AU endpoint: `identitysso-cert.betfair.com.au`
- Certificate file: `betfair_combined.pem`
- Stores session token in `betfair_config.json`

**Status:** ✅ Working
- Account: dnfarnot@gmail.com
- App Key: XmZEwtLsIRkf5lQ3
- Session token refreshes automatically

---

### 2. Core API (betfair_api.py)

**Methods:**
- `place_back_bet(market_id, selection_id, odds, stake)`
- `place_lay_bet(market_id, selection_id, odds, stake)`
- `get_market_book(market_id)` - Get current prices
- `get_account_balance()` - Check funds
- `cancel_orders(market_id, bet_id)`
- `get_current_orders(market_id)`

**Features:**
- FILL_OR_KILL orders (instant or cancel)
- LAPSE persistence (auto-cancel at suspension)
- Auto-logging to `betfair_api_log.txt`

---

### 3. Scalping Bot (scalping_bot.py)

**Strategy:**
```
1. Scan AU horse racing markets
2. Filter: Min liquidity $10,000
3. Find spreads ≤ 2 ticks
4. BACK at current price
5. Place LAY order 2 ticks higher
6. Wait for both to match
7. Green up (guaranteed profit)
```

**Settings:**
- Stake: $1.00
- Take profit: 2 ticks
- Stop loss: 3 ticks
- Max positions: 3
- Max trade time: 60 seconds

**Risk Limits:**
- Daily profit target: $2.00
- Daily loss limit: $1.00
- Max consecutive losses: 5

---

### 4. Scalping Engine (scalping_engine.py)

**Advanced scanner with multiple modes:**

```
Mode 1: Scan only - List opportunities
Mode 2: Auto-trade - Execute first opportunity
Mode 3: Continuous - Scan every 5 minutes
```

**Filters:**
- Spread: 1-10 ticks (configurable)
- Countries: AU, GB, IE
- Min stake: $1.00 (enforced)
- Max risk: 5% of bankroll

**Opportunity Detection:**
```python
if spread >= 0.01 and spread <= 0.10:
    if min_profit >= -0.05:  # Allow small loss for testing
        opportunity_found()
```

---

### 5. Smart Trader (smart_trader.py)

**Special Strategy: 3rd Favorite Scalping**

```
1. Get all markets
2. Sort runners by BACK price (favorites)
3. Select ONLY the 3rd favorite
4. Check spread >= 5%
5. Check liquidity >= $50 both sides
6. BACK 3rd favorite
7. Wait for price to DROP
8. LAY at lower price
9. Lock in profit
```

**Why 3rd Favorite?**
- 1st favorite: Too stable (no movement)
- 2nd favorite: Often follows 1st
- 3rd favorite: Sweet spot for volatility
- 4th+: Too volatile (risky)

**Criteria:**
- Spread percentage: >= 5%
- Price range: 2.0 - 10.0
- Liquidity: >= $50 each side

---

### 6. Auto-Hedge Module (auto_hedge.py)

**How It Works:**
```
Every 30 seconds:
1. Get all matched BACK orders
2. Get current LAY prices
3. Calculate tick profit
4. If tick_profit >= min_profit_ticks:
   - Calculate hedge LAY stake
   - Place LAY bet
   - Lock in guaranteed profit
```

**Hedge Calculation:**
```python
lay_stake = (back_price / lay_price) * back_stake

profit_if_win = (back_price - 1) * back_stake - (lay_price - 1) * lay_stake
profit_if_lose = -back_stake + lay_stake

guaranteed_profit = min(profit_if_win, profit_if_lose)
```

**Example:**
```
BACK $1.00 @ 2.20
Current LAY: 2.17 (3 ticks profit)

Hedge: LAY $1.01 @ 2.17
If wins:  +$1.20 - $1.18 = +$0.02
If loses: -$1.00 + $1.01 = +$0.01

GUARANTEED: $0.01 profit
```

---

### 7. Risk Manager (risk_manager.py)

**Stake Calculation (Kelly-inspired):**
```python
def calculate_stake(bankroll, price, stop_loss_ticks):
    max_risk = bankroll * 0.01  # 1% per trade
    potential_loss = (stop_loss_ticks * 0.01) / price
    stake = max_risk / potential_loss
    
    # Clamp to limits
    stake = min(stake, max_stake, bankroll * 0.10)
    stake = max(stake, min_stake)
    
    return round(stake, 2)
```

**Trading Guards:**
```python
def can_trade(bankroll):
    if daily_pnl <= -daily_loss_limit:
        return False, "Daily loss limit reached"
    
    if daily_pnl >= daily_profit_target:
        return False, "Daily profit target reached"
    
    if consecutive_losses >= 5:
        return False, "Max consecutive losses"
    
    if hour < 8 or hour >= 23:
        return False, "Outside trading hours"
    
    if bankroll < 5:
        return False, "Insufficient bankroll"
    
    return True, "OK"
```

---

### 8. Trading Dashboard (trading_dashboard.py)

**GUI Features:**
- **Left Panel:** Market opportunities list
- **Middle Panel:** Open positions + Hedged trades
- **Right Panel:** Controls + Activity log
- **Status Bar:** Balance, exposure, alerts

**Controls:**
- Start/Stop monitoring
- Manual scan
- Auto-execute toggle
- Stake amount input
- Min spread setting

**Auto-Features:**
- Scan every 5 minutes
- Auto-hedge every 30 seconds
- Alert on tight spreads (≤1 tick)

---

## Strategy Documents

### AMAZING_STRATEGY.md

**8 Advanced Strategies Documented:**

1. **Weighted Scalping** - Entry criteria based on liquidity + timing
2. **Momentum Trading** - Follow volume spikes
3. **Statistical Arbitrage** - Value betting with probability models
4. **Kelly Criterion** - Optimal stake sizing
5. **Multi-Stage Hedging** - Partial hedge → Full hedge
6. **Time-Based Entry** - Best times to trade
7. **Correlation Arbitrage** - Cross-market opportunities
8. **Stop-Loss Automation** - Trailing stops

**Implementation Phases:**
- Phase 1: Kelly + Stop-loss (Week 1)
- Phase 2: Volume tracking + Momentum (Week 2)
- Phase 3: Multi-stage hedging + ML (Week 3)

---

### WEEKLY_TRADING_SCHEDULE.md

**Peak Liquidity Windows (AEDT):**

| Time | Sport | Liquidity |
|------|-------|-----------|
| 2:00-6:00 AM | NFL Sunday | HIGHEST |
| 10:00 PM-2:00 AM | Premier League | Very High |
| 10:00 PM-2:00 AM | UK Horse Racing | Very High |
| 4:00-6:00 AM | Champions League | High |
| 8:00 AM-1:00 PM | NBA | Good |
| 11:00 AM-5:00 PM | AU Horse Racing | Good |

**Best Days:**
- **Saturday:** Premier League + UK racing (peak)
- **Sunday:** NFL (highest liquidity of week)
- **Tuesday/Wednesday:** Champions League

---

## Configuration Files

### betfair_config.json
```json
{
  "app_key": "XmZEwtLsIRkf5lQ3",
  "app_key_delayed": "Mzlrc2cMNmjM0K33",
  "session_token": "hbW3tcuobmmVYQZsdGfDJs3kDyivt3efdNoPGKyxmLE=",
  "extracted_at": "2026-02-25 15:39",
  "notes": {
    "account": "dnfarnot@gmail.com",
    "method": "Certificate login"
  }
}
```

### hedged_trades_config.json
```json
{
  "min_profit_ticks": 3,
  "stake": 1.00
}
```

---

## Current Status

### Account (as of 2026-02-25)
- Balance: ~$6.93
- Exposure: $2.00
- Open positions: 8-9 BACK bets

### What's Working
✅ Certificate authentication
✅ API calls (markets, prices, orders)
✅ Auto-hedge module
✅ Risk management
✅ GUI dashboard

### What Needs Work
🔲 Session token refresh (manual currently)
🔲 Better market selection
🔲 Stop-loss automation
🔲 Performance analytics
🔲 Kelly Criterion stake sizing

---

## How to Use

### Quick Start
```bash
cd C:\Users\aaron\Desktop\008
python trading_dashboard_hedge.py
```

### Manual Scalp
```bash
python scalping_engine.py
# Choose mode 1 (scan)
# Review opportunities
# Execute if desired
```

### Auto-Hedge Only
```bash
python auto_hedge.py
# Runs continuously
# Hedges when profit >= min_profit_ticks
```

### Hedge All Positions Now
```bash
python hedge_all.py
# Scans all open BACK bets
# Hedges each one if profitable
```

---

## Key Lessons from the Code

### 1. Scalping is About Spread + Liquidity
```python
if spread <= 2 and liquidity >= 10000:
    # Good scalping opportunity
```

### 2. Always Hedge Before Race Starts
```python
if minutes_to_start < 5:
    hedge_all_positions()  # Avoid volatility
```

### 3. Risk Management is Critical
```python
if consecutive_losses >= 5:
    stop_trading()  # Take a break
```

### 4. Session Tokens Expire
- Need to refresh periodically
- Certificate login gets new token
- Store in config file

### 5. Min Stake is $1.00
- Betfair enforces minimum
- Can't go smaller for testing
- Must manage bankroll carefully

---

## Files Summary

### Core Files (Must Have)
- `betfair_config.json` - Credentials
- `betfair_api.py` - API client
- `aus_cert_login.py` - Authentication
- `scalping_engine.py` - Main trader

### GUI Files
- `trading_dashboard_hedge.py` - Full GUI
- `scalping_gui.py` - Scalping interface
- `gui_trader.py` - General GUI

### Automation Files
- `auto_hedge.py` - Auto-hedging
- `hedge_all.py` - Batch hedge
- `auto_trader.py` - Automated trading

### Documentation
- `README.md` - Overview
- `AMAZING_STRATEGY.md` - 8 strategies
- `SYSTEM_GUIDE.md` - How to use
- `WEEKLY_TRADING_SCHEDULE.md` - Peak times
- `BETANGEL_RESEARCH.md` - BetAngel research
- `SCALPING_RESEARCH.md` - Scalping research

---

## Recommendations

### Immediate Actions
1. Run `trading_dashboard_hedge.py`
2. Set Min Profit to 3 ticks
3. Set Stake to $1.00
4. Start Auto-Hedge
5. Monitor during peak hours

### Next Improvements
1. Add trailing stop-loss
2. Implement Kelly Criterion sizing
3. Build performance analytics
4. Add multi-stage hedging
5. Create backtesting system

### Risk Warnings
⚠️ Session tokens expire - need refresh
⚠️ Markets suspend at race start
⚠️ Min stake $1.00 enforced
⚠️ Commission affects profits (5%)
⚠️ In-play is risky for beginners

---

*Analysis completed: 2026-03-02*
*System location: C:\Users\aaron\Desktop\008\*
