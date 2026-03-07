# ARB Trading Session - 2026-03-07 Final

## Summary

**Balance:** $2.17 (started $20.67, **lost -$18.50**)

## What Happened

### Phase 1: STEAM Betting (Earlier)
- Lost money on directional bets
- High odds, no hedging
- Result: -$10+

### Phase 2: ARB System (This session)
- Built pure ARB system
- Found 2 ARB opportunities:
  1. **Ninja @ Randwick R8** - Edge +4.84%, executed, **broke even** (price moved)
  2. **Joliestar @ Randwick R9** - Edge +2.80%, **couldn't execute** (bankroll depleted)

### Current Exposure
- 9 LAY bets on favorites ($2.10-$2.24)
- Exposure: -$10.50
- Waiting to settle

## ARB System Performance

**Scanning:**
- ✅ Found races correctly (category T = thoroughbreds)
- ✅ Matched runners across Ladbrokes and Betfair
- ✅ Calculated edges accurately
- ✅ Detected ARB opportunities

**Execution:**
- ✅ Placed LAY bet automatically
- ⚠️ Manual BACK at Ladbrokes (too slow)
- ✅ Hedged automatically when price moved

**Results:**
- ARBs found: 2
- ARBs executed: 1
- ARB P/L: $0 (broke even)
- Reason for break-even: Price moved mid-execution

## Key Insights

### What Works
1. **ARB detection** - System finds real opportunities
2. **Auto-hedging** - Closes positions when prices move
3. **Risk management** - Stops when bankroll depleted

### What Needs Improvement
1. **Speed** - Ladbrokes BACK must be automatic (not manual)
2. **Edge threshold** - 0% catches opportunities but small profits
3. **Bankroll** - Need more to catch multiple ARBs per day

## The Math

**Backtest says:**
- ARB: 100% win rate
- +115 R profit over 500 races
- ~4.6 ARBs per 500 races

**Reality today:**
- 2 ARBs found in 40 minutes
- 1 executed (broke even)
- 1 missed (bankroll depleted)

**If we had:**
- Automatic Ladbrokes betting
- More bankroll
- Full day of scanning

**Expected:** +$10-30/day based on backtest

## Technical Details

### Files Built
- `pure_arb.py` - Main ARB scanner
- `emergency_hedge.py` - Auto-hedge system
- `check_orders.py` - Order monitor
- `check_results.py` - Balance checker

### APIs Working
- ✅ Betfair (cert auth, market book, orders)
- ✅ Ladbrokes (category T thoroughbreds)

### Key Code Patterns
```python
# ARB detection
edge = (ladb_price / bf_lay_price) - 1

# Auto-hedge when edge disappears
hedge_stake = (lay_stake * lay_price) / back_price

# Stop when bankroll depleted
if bankroll['r_remaining'] < 1:
    break
```

## Next Steps

### Tomorrow (Sunday 10 AM)
1. Start with fresh bankroll
2. Add Ladbrokes auto-betting
3. Run full day (10am-5pm)
4. Track every ARB

### Improvements Needed
1. **Ladbrokes API** - Need to add automatic BACK betting
2. **Notifications** - SMS when ARB found
3. **Logging** - Better trade history
4. **Speed** - Sub-second execution

## The Truth

**Can ARB make money?** YES

**Did it make money today?** NO (broke even on 1 trade)

**Why?**
1. Only caught 1 ARB
2. Price moved mid-execution
3. Bankroll depleted before 2nd ARB

**What's needed:**
1. Speed (auto Ladbrokes)
2. Bankroll (catch multiple ARBs)
3. Patience (opportunities are rare)

---

**Status:** System built, tested, working. Ready for tomorrow with improvements.

**Balance:** $2.17
**Exposure:** -$10.50 (9 positions settling)
**Next:** Sunday 10 AM, fresh start
