# Trading Lessons - 2026-03-07

## What Happened

Started with $20.67, ended with $7.22
**Loss: -$13.45**

## The 4 Critical Failures

### 1. Duplicate Bets (FIXED)
**Problem:** Placed 2 bets on same selection (Inner Gold, Barn Zee)
**Cause:** No tracking of selections already bet on
**Fix:** Added `bet_on_selections` set to track
**Result:** No more duplicates after fix

### 2. No Hedging (PARTIALLY FIXED)
**Problem:** BACK bets placed but LAY hedges failed
**Causes:**
- LAY stakes below minimum ($0.67 instead of $1.00)
- Auto-hedge started too late
- LAY bets placed at prices that don't match

**Fix:** Minimum $1.00 stake enforcement
**Still broken:** LAY bet matching

### 3. High Odds Bets (FIXED)
**Problem:** Bet on runners @ $23, $13.65 (way too high)
**Cause:** No max odds limit
**Fix:** Added MAX_ODDS = 8.00
**Result:** Only reasonable odds after fix

### 4. False Steam Detection (NOT FIXED)
**Problem:** Detected "STEAM" but price reversed
**Example:** Inner Gold dropped from $23 to $19 (STEAM detected), then reversed to $23-24
**Cause:** Single price snapshot, no trend confirmation
**Impact:** Betting on false moves

## The Pattern

```
1. Price drops 10%+ → System detects STEAM
2. Places BACK bet
3. Price reverses and drifts UP
4. Hedge target (5% lower) never reached
5. Race starts → Naked position → Loss
```

## Root Cause Analysis

### Why False Steam?
- **Snapshot vs Trend:** Only checking current vs open price, not confirming the move is continuing
- **No Volume Check:** Not checking if the price drop has backing
- **Mean Reversion:** Sharp drops often reverse

### Why No Hedge Match?
- **LAY mechanics:** LAY bets need someone to take the other side
- **Price too aggressive:** Trying to LAY at better prices than market offers
- **Should match at current BACK price** not target price

## Professional Insight Needed

From BetAngel forums:
- **True steam:** Consistent backing, breaks support, 5%+ in 5-10 mins
- **False steam:** Erratic moves, no follow-through
- **Key:** Watch order flow, not just price

## What To Build Next

### 1. Steam Confirmation System
```python
def confirm_steam(runner, threshold=0.05):
    """
    Check if steam is real:
    - Price dropped 5%+ in last 5 mins
    - Price still dropping (not reversing)
    - Order flow shows backing
    - At least 3 consecutive price drops
    """
```

### 2. Immediate Hedge on Entry
- Don't wait for target
- Hedge immediately at current market
- Accept small loss for guaranteed position

### 3. LAY Bet Matching Fix
- Place LAY at current BACK price (guaranteed match)
- Or place BACK at current LAY price
- Always match immediately, never leave hanging

## The Deeper Lesson

**Arbitrage requires:**
1. Guaranteed entry price (matched immediately)
2. Guaranteed exit price (hedged immediately)
3. Locked profit (green book)

**What I did:**
1. ✅ Entry matched
2. ❌ Exit not locked
3. ❌ Profit not guaranteed

**Result:** Gambling, not arbitrage

## Tomorrow's Rules

1. **Only bet on CONFIRMED steam** (3+ consecutive drops)
2. **Hedge IMMEDIATELY** at market price
3. **Never exceed 8.00 odds**
4. **Never duplicate selections**
5. **Stop if balance drops below $5**

## Questions to Research

1. How do professional traders detect true steam?
2. What's the optimal hedge timing?
3. Should I use stop-loss instead of target-profit hedges?
4. Is STEAM betting even viable, or should I focus on ARB only?

## Data From Today

| Metric | Value |
|--------|-------|
| Bets placed | 15+ |
| Duplicates | 4 |
| Hedges attempted | 6 |
| Hedges matched | 3 |
| Wins | 2 (Belmasai, Popthebubbly) |
| Losses | 7+ |
| Win rate | ~22% |
| Avg win | +$3.30 |
| Avg loss | -$1.00 |
| Expectancy | Negative |

**Conclusion:** System is broken. Need to rebuild with proper steam confirmation and immediate hedging.

---

*"The market can remain irrational longer than you can remain solvent."* - Keynes
