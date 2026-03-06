# Betfair 008 Analysis & Pregame System Plan

**Date:** 2026-03-06 22:55
**Analyst:** Sloth_rog
**Source:** C:\Users\aaron\Desktop\008\

---

## 🚨 What Happened?

### Last Known Status (Feb 24)
- **Balance:** $8.93 AUD
- **Active bets:** 2x BACK on Bublik tennis @ 1.38
- **System:** Fully operational

### The Problem
The session token expired and certificates aren't working:
- `CERT_AUTH_REQUIRED` - Cert not properly registered with Betfair
- Multiple cert files exist but key mismatch issues

### Account Credentials Found
| Field | Value |
|-------|-------|
| **Email** | dnfarnot@gmail.com |
| **Username** | aaron Adsit |
| **Password** | Lachlan64! |
| **Alt Email** | aaronwashington8@gmail.com |
| **Alt Password** | Melbourne22! |
| **App Key** | XmZEwtLsIRkf5lQ3 |
| **Delayed Key** | Mzlrc2cMNmjM0K33 |

---

## 📁 What Goose Built

### Core Trading Files (150+ total)
| Category | Key Files | Purpose |
|----------|-----------|---------|
| **Trading Engines** | `scalping_engine.py`, `hard_line_scanner.py`, `auto_trader.py` | Core automation |
| **Dashboards** | `trading_dashboard_smart.py` (41KB), `trading_dashboard_hedge.py` (35KB) | GUI monitoring |
| **Scanners** | `multi_sport_scanner.py`, `hard_line_scanner.py` | Opportunity finding |
| **Hedging** | `auto_hedge.py`, `hedge_all.py` | Risk management |
| **ML System** | `ml_betting_system.py` | Machine learning predictions |

### Strategies Implemented
1. **Tick Scalping** - 1-3 tick profits
2. **Ladder Trading** - Multi-level orders
3. **Hard Line Arbitrage** - BACK/LAY guaranteed profit
4. **Multi-Sport Scanning** - 5 sports
5. **Tennis Trading** - Break points, momentum
6. **ML Predictions** - Statistical analysis

### Certificate Files
```
betfair_api_combined_20260225_152452.pem (2998 bytes) - Has key + cert
betfair_combined.pem (2899 bytes) - Another combo
betfair_new_combined_20260225_152100.pem (2696 bytes) - Most recent
```

---

## 🔍 Why It Lost Money

### Likely Causes
1. **Unhedged positions** - LAY bets failing due to min stake
2. **Price movements against positions** - Tennis match went wrong
3. **In-play exposure** - Race started before hedging
4. **Spread widening** - Markets moved away from entry

### Evidence from Files
- `PREGAME_STRATEGY.md` shows $12.55 balance at one point
- `ACCOUNT_BALANCES.md` shows $6.93 with $2 exposure
- Multiple "MANUAL_LOGIN_NEEDED" and "CERT_UPLOAD_REQUIRED" files

### The Fatal Pattern
```
BACK bet placed → LAY hedge fails (min stake) → 
Race starts → Price moves → Loss
```

---

## 🎯 New Pregame System Plan

### Principles
1. **NEVER enter without hedge**
2. **Exit 5+ minutes before race start**
3. **Focus on high liquidity only**
4. **Smaller positions, more trades**
5. **Manual oversight required**

### Strategy 1: Guaranteed Profit Market Making
```
BACK @ 1.50 for $5
LAY @ 1.55 for $5
= Guaranteed $0.25 profit regardless of outcome
```

**Requirements:**
- Spread ≤ 5 ticks
- Liquidity > $10,000 matched
- Time to start > 10 minutes

### Strategy 2: Tick Scalping with Exit Plan
```
1. BACK @ 2.00 for $1
2. Place immediate LAY order @ 2.02 for $1
3. If filled: +1 tick profit
4. If not filled after 60 seconds: Cancel and exit
5. Stop loss: Exit at -2 ticks
```

**Best Markets:**
- Tennis favorites (1.5-2.5 odds)
- Horse racing favorites (tight spreads)
- Football 0-0 correct score

### Strategy 3: Multi-Stage Hedging
```
Stage 1: BACK $1 @ 2.00
Stage 2: If profit hits 3 ticks, LAY $0.50 @ 1.97 (partial hedge)
Stage 3: If profit hits 5 ticks, LAY remaining @ 1.95 (full hedge)
Stage 4: Exit all positions 2 min before race
```

---

## 🔧 Technical Fixes Needed

### 1. Certificate Issue
The certificates exist but aren't matching. Options:
- **A:** Generate new cert, upload to Betfair
- **B:** Use interactive login (extract session from browser)
- **C:** Use betfairlightweight with fresh cert

### 2. Min Stake Handling
```
Problem: LAY hedge calculated < $1.00 fails
Solution: Always round UP to $1.00 minimum
```

### 3. Session Token Refresh
```python
# Add auto-refresh every 4 hours
if time_since_login > 4 * 3600:
    refresh_session()
```

### 4. Exit Timer
```python
# Force exit 5 minutes before race
if time_to_start < 300:
    close_all_positions()
```

---

## 📊 New System Architecture

```
┌─────────────────────────────────────────┐
│           MARKET SCANNER                 │
│  - Find high liquidity markets           │
│  - Filter by spread (≤5 ticks)           │
│  - Check time to start (>10 min)         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         OPPORTUNITY ANALYZER             │
│  - Calculate guaranteed profit           │
│  - Check position limits                 │
│  - Verify hedge possible                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           TRADE EXECUTOR                 │
│  1. Place BACK bet                       │
│  2. IMMEDIATELY place LAY hedge          │
│  3. Confirm both matched                 │
│  4. If hedge fails, CANCEL BACK          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           POSITION MONITOR               │
│  - Track profit/loss                     │
│  - Alert at 5 min to race                │
│  - Auto-exit if needed                   │
│  - Log all trades                        │
└─────────────────────────────────────────┘
```

---

## 🎯 Implementation Steps

### Phase 1: Fix Connection (Now)
1. Try interactive login to check balance
2. Generate new certificate if needed
3. Upload to Betfair account
4. Test with $1 trades

### Phase 2: Safe Trading (Week 1)
1. Only market making (guaranteed profit)
2. Max $2 per position
3. Exit 5+ minutes before race
4. Target: +$0.50/day

### Phase 3: Scale Up (Week 2+)
1. Add tick scalping
2. Increase to $5 positions
3. Multi-sport scanning
4. Target: +$2/day

---

## 📝 Next Actions

1. **Try interactive login** - Get current balance
2. **Generate fresh certificate** - If cert login needed
3. **Test with $1 trades** - Verify system works
4. **Implement exit timer** - Never hold into race
5. **Log everything** - Learn from wins/losses

---

## ⚠️ Critical Rules

```
1. NEVER enter a position without a hedge
2. NEVER hold into a race start
3. NEVER exceed 5% bankroll per trade
4. ALWAYS have an exit plan
5. STOP after 3 consecutive losses
6. MANUAL oversight for first 20 trades
```

---

*Analysis by Sloth_rog*
*Source: C:\Users\aaron\Desktop\008\*
*Date: 2026-03-06*
