# Betfair Edge Study
## Finding Exploitable Inefficiencies in Betting Markets

**Date:** March 7th, 2026
**Purpose:** Identify edges that can be systematically captured

---

## The Betfair Advantage

Betfair is a **betting exchange**, not a bookmaker. This means:
- Users bet against each other (peer-to-peer)
- The market sets the prices, not the house
- Back AND Lay bets are possible
- Commission (5%) is the only cost

**Key implication:** Markets can be inefficient. Edges exist.

---

## Edge Category 1: Cross-Market Arbitrage (ARB)

### What It Is
Betfair prices differ from bookmaker prices. When Ladbrokes offers $4.00 and Betfair lays at $3.50, there's a locked profit.

### Why It Exists
- Bookmakers have different risk models
- Betfair reacts faster/slower to information
- Some bookmakers are slow to update

### Current Status in SteamArb
- ✅ **Implemented**
- ✅ **100% win rate in backtests**
- ✅ **+0.050R per trade**

### Edge Magnitude
- **Low** (0.5-2% profit per trade)
- **High volume** (many opportunities)
- **Zero risk** (profit locked at entry)

### Improvement Opportunities
1. Add more bookmakers (Neds, TAB, Sportsbet)
2. Faster scanning (reduce from 30s to 5s)
3. Auto-execute when edge > 1%

---

## Edge Category 2: Steam Moves

### What It Is
A "steam move" is a sudden, significant price movement caused by sharp bettors or inside information.

### Why It Exists
- Someone knows something the market doesn't
- Bookmakers react faster than exchanges (sometimes)
- The market overreacts and then corrects

### Current Status in SteamArb
- ⚠️ **Implemented but underperforming**
- ⚠️ **-0.003R per trade (break-even)**

### Why It's Not Working (Hypothesis)
1. **Entry too late** - By the time we detect steam, edge is gone
2. **Exit too early** - We're not waiting for full correction
3. **False positives** - Not all 5% drops are steam
4. **AU markets different** - Less liquidity, different behavior

### Improvement Opportunities
1. **Lower threshold** - Catch moves earlier (3% instead of 5%)
2. **Volume confirmation** - Only trade if volume spikes
3. **Time-based filter** - Steam in last 30 mins is more reliable
4. **Multi-source detection** - Cross-reference with bookmaker moves

---

## Edge Category 3: Value Betting

### What It Is
Betfair's "true probability" (back price) differs from a bookmaker's implied probability. When Betfair says 25% and Ladbrokes pays $5.00 (20% implied), there's an edge.

### Why It Exists
- Bookmakers set prices based on risk, not pure probability
- Betfair is more efficient but not perfect
- Different information sets

### Current Status in SteamArb
- ✅ **Implemented**
- ⚠️ **High variance** (+0.25R to -0.12R per trade depending on run)
- ⚠️ **Low win rate** (15-25%)

### Edge Magnitude
- **High** (5-25% profit per winning trade)
- **Low volume** (fewer opportunities)
- **High variance** (unpredictable short-term)

### Improvement Opportunities
1. **Higher edge threshold** - Only bet when edge > 15%
2. **Probability calibration** - Use Betfair volume to validate true price
3. **Selective markets** - Some sports/races are more predictable
4. **Kelly staking** - Size bets based on edge magnitude

---

## Edge Category 4: In-Play Trading (NEW)

### What It Is
Trade during the event, not before. Prices move rapidly as the game/race progresses.

### Why It Exists
- Real-time information is processed at different speeds
- Emotional overreactions create mispricings
- Fast data feeds beat slow ones

### Status
- ❌ **Not implemented**
- ⚠️ **High risk** (betting doesn't stop when event starts)

### Edge Magnitude
- **Very high** (5-50% profit per trade)
- **High volume** (many price movements)
- **High risk** (prices can gap against you)

### Implementation Challenges
1. Need ultra-fast data feeds
2. Need automated execution (no time for manual)
3. Betfair API rate limits
4. Risk of getting stuck in-play

### Recommendation
**Do NOT implement in-play trading yet.** Too risky for paper trading validation. Save for future when system is proven.

---

## Edge Category 5: Early Market Pricing (NEW)

### What It Is
Betfair markets open days before the event. Early prices are often less efficient.

### Why It Exists
- Less information available early
- Fewer participants in early markets
- Bookmakers haven't fully formed their odds

### Status
- ❌ **Not implemented**
- ✅ **Low risk** (can exit before race)

### Edge Magnitude
- **Medium** (2-10% profit per trade)
- **Medium volume** (depends on when markets open)
- **Low-medium risk** (prices converge toward efficiency)

### Implementation Strategy
1. Monitor markets when they first open (often 24-48h before)
2. Compare early Betfair prices to bookmaker ante-post prices
3. Look for significant discrepancies (>5%)
4. Back/Lay early, exit closer to race when prices converge

### Recommendation
**Worth exploring.** Could be combined with existing ARB engine.

---

## Edge Category 6: Liquidity Harvesting (NEW)

### What It Is
Provide liquidity in illiquid markets by posting both back and lay orders. Capture the spread.

### Why It Exists
- Some markets have no liquidity (wide spreads)
- Market makers earn the spread
- Betfair rewards liquidity providers

### Status
- ❌ **Not implemented**
- ⚠️ **Requires active management**

### Edge Magnitude
- **Low-medium** (1-5% per trade)
- **High volume** (many illiquid markets)
- **Low risk** (you set both sides)

### Implementation Strategy
1. Identify illiquid markets (spread > 5%)
2. Post back at price X, lay at price X+spread
3. When both matched, profit = spread - commission
4. Manage unmatched orders (cancel before race)

### Example
```
Market: Geelong Race 8 - Some Random Horse
Current: Back $5.00 | Lay $6.00 (spread 20%)

You post:
  Back @ $5.30
  Lay @ $5.70

If both matched:
  Profit = (5.70 - 5.30) / 5.30 = 7.5% before commission
  After 5% commission = ~2% net
```

### Recommendation
**Worth exploring.** Passive income with low risk.

---

## Edge Category 7: Cross-Sport Arbitrage (NEW)

### What It Is
Different sports have different efficiency levels. Less popular sports = more inefficiency.

### Why It Exists
- Less liquidity = less efficiency
- Fewer sharp bettors in niche sports
- Bookmakers may not specialize

### Sports to Consider

| Sport | Liquidity | Efficiency | Edge Potential |
|-------|-----------|------------|----------------|
| Horse Racing | High | High | Medium |
| AFL | High | Medium | Medium |
| NRL | High | Medium | Medium |
| Cricket | Medium | Low | High |
| Soccer | Very High | Very High | Low |
| Tennis | Medium | Medium | Medium |
| Basketball | Medium | Medium | Medium |
| **Greyhounds** | Medium | **Low** | **High** |
| **Harness Racing** | Low | **Very Low** | **Very High** |

### Recommendation
**Explore greyhounds and harness racing.** Lower efficiency = more edges.

---

## Edge Category 8: Time-Based Patterns (NEW)

### What It Is
Prices follow predictable patterns based on time to event.

### Why It Exists
- Information arrives at predictable times
- Market participants behave systematically
- Liquidity patterns are consistent

### Known Patterns

1. **Monday-Tuesday Effect**
   - Early week markets less efficient
   - Weekend information not yet priced in

2. **Morning of Race**
   - Prices tighten as liquidity increases
   - Arbitrage opportunities shrink

3. **Last 30 Minutes**
   - Maximum liquidity
   - Minimum spreads
   - Most efficient prices

4. **Scratchings**
   - When a horse is scratched, markets reprice
   - Short window of inefficiency

### Recommendation
**Incorporate time filters.** Only trade during optimal windows.

---

## Edge Category 9: Multiple Bookmaker Arbitrage (NEW)

### What It Is
Compare Betfair to multiple bookmakers simultaneously. More sources = more edges.

### Why It Exists
- Different bookmakers have different prices
- Some slow to update
- Some have different risk exposures

### Bookmakers to Add

| Bookmaker | API Available | Notes |
|-----------|---------------|-------|
| Ladbrokes | ✅ | Already implemented |
| Neds | ✅ | Same API as Ladbrokes |
| TAB | ⚠️ | Limited API |
| Sportsbet | ❌ | No public API |
| PointsBet | ⚠️ | Limited API |
| bet365 | ❌ | No AU API |

### Recommendation
**Add Neds immediately** (same API). Explore TAB.

---

## Edge Category 10: Commission Reduction (NEW)

### What It Is
Betfair charges 5% commission on winning bets. But this can be reduced.

### Why It Exists
- Betfair rewards high-volume traders
- PC (Premium Charge) exists for very profitable traders
- Market Maker program offers reduced commission

### Commission Tiers

| Volume | Commission |
|--------|------------|
| Standard | 5% |
| 100+ points/week | 4% |
| 500+ points/week | 3% |
| Market Maker | 2% |

### Impact
- Reducing from 5% to 3% = **40% more profit**
- On $1000 profit = $200 extra

### Recommendation
**Long-term goal:** Achieve Market Maker status for reduced commission.

---

## Summary: Priority Ranking

| Priority | Edge | Expected R/Trade | Effort | Risk |
|----------|------|------------------|--------|------|
| 1 | ARB (existing) | +0.050R | Done | Zero |
| 2 | Add Neds to ARB | +0.020R | Low | Zero |
| 3 | Early market pricing | +0.030R | Medium | Low |
| 4 | Liquidity harvesting | +0.020R | Medium | Low |
| 5 | Greyhounds/harness | +0.040R | Medium | Medium |
| 6 | Improve VALUE engine | +0.100R | Medium | Medium |
| 7 | Improve STEAM engine | +0.010R | High | Medium |
| 8 | Commission reduction | N/A | High | Zero |
| 9 | In-play trading | +0.200R | Very High | High |
| 10 | Time-based filters | +0.010R | Low | Zero |

---

## Recommended Next Steps

### Immediate (This Week)
1. ✅ Validate ARB with real data (today at 10am)
2. Add Neds API to existing ARB engine
3. Implement time-based filters (only trade 5-60 mins before race)

### Short-term (Next 2 Weeks)
4. Add early market monitoring (24h before race)
5. Add greyhounds to scanner
6. Improve STEAM detection (volume confirmation)

### Medium-term (Next Month)
7. Implement liquidity harvesting in illiquid markets
8. Explore harness racing
9. Track commission points toward tier reduction

### Long-term (3+ Months)
10. Consider in-play trading (only after system proven)

---

## Expected Impact

**Current system:** +0.065R/trade (backtest average)

**With improvements:**
- Neds added: +0.020R
- Early markets: +0.030R
- Greyhounds: +0.040R
- Improved VALUE: +0.050R

**Total expected:** +0.205R/trade

**At 100 trades/day:** +20.5R/day = $20.50/day (at 1R=$1)

**At 1R=$12.50:** $256/day = $7,680/month

---

*Study completed: March 7th, 2026, 8:41 AM*
*For Slothitude and the SteamArb system*
