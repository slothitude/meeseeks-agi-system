# SteamArb Backtest Analysis - 2026-03-07 03:04 AM

## Hourly Backtest Results (500 races)

### Performance by Engine

| Engine | Trades | Win Rate | Total R | R/Trade | Status |
|--------|--------|----------|---------|---------|--------|
| ⚡ ARB | 2,387 | 100.0% | +118.33 | +0.050 | ✅ Excellent |
| 🔥 STEAM | 156 | 63.5% | -0.38 | -0.002 | ⚠️ Needs tuning |
| 💎 VALUE | 589 | 22.1% | +154.56 | +0.262 | ✅ High variance but profitable |

### Combined Performance
- **Total Trades:** 3,132
- **Total R:** +272.51R
- **Avg R/Trade:** +0.087R
- **Total AUD:** +$272.51 (at 1R=$1)

### Analysis

#### ARB Engine ✅
- Perfect 100% win rate (expected - it's locked profit)
- Volume dominates (76% of all trades)
- Consistent +0.050R per trade
- **Status:** Working as designed

#### STEAM Engine ⚠️
- 63.5% win rate (below expected 65-70%)
- Slightly negative (-0.002R per trade)
- Only 5% of trades (low volume)
- **Issue:** May need parameter adjustment:
  - Lower MIN_STEAM_DROP_PCT (currently 5%)
  - Tighter spread requirements
  - Better timing on exits

#### VALUE Engine ✅
- Low win rate (22.1%) but highest R-per-trade (+0.262)
- High variance strategy
- 19% of trades
- **Status:** Working - variance is expected

### Recommendations

#### For 10am Paper Trading (Day 1)
- **Keep all engines enabled** - need real data to validate
- **Focus on ARB** - most reliable
- **Monitor STEAM closely** - if still negative after 50 trades, investigate
- **Accept VALUE variance** - it's working as designed

#### For Future Improvement
1. **STEAM tuning:**
   - Lower MIN_STEAM_DROP_PCT to 4%
   - Add spread filter (max 1.5 tick spread)
   - Improve lay price prediction

2. **ARB scaling:**
   - This is the core engine
   - Focus on finding more ARB opportunities
   - Tighter runner name matching

3. **VALUE patience:**
   - Low win rate is expected
   - Don't disable after bad day
   - Trust the math over 100+ trades

### Expected Day 1 Results (Conservative)

Based on backtest, if we see 50 trades:
- ARB: ~38 trades, +1.9R
- STEAM: ~2-3 trades, ~0R
- VALUE: ~10 trades, +2.6R (high variance)
- **Total:** ~+4.5R or $4.50

But Day 1 goal is **validation**, not profit.

---

*Analysis complete at 3:04 AM*
*7 hours until 10am validation*
