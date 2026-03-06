# SteamArb Implementation Plan
## Paper Trading Phase - March 7-14, 2026

---

## Week 1 Goals (March 7-14)

### Primary: Validate Core System
- ✅ ARB engine works with real data
- ✅ APIs stay connected for 6 hours
- ✅ Runner matching is accurate
- ✅ Opportunities are logged correctly

### Secondary: Collect Data
- Count real opportunities
- Measure actual R expectancy
- Compare to backtest results
- Identify patterns

### Tertiary: Learn
- What time of day has most opportunities?
- Which tracks are most profitable?
- What's the realistic win rate?
- Where does the system break?

---

## Paper Trading Schedule

### Day 1 (March 7) - Today
**Focus:** Does it work at all?

**Schedule:**
- 10:00 AM - System auto-starts
- 10:00 AM - 4:00 PM - Paper trading runs
- ~4:00 PM - Results delivered

**Success criteria:**
- ✅ At least 1 opportunity found
- ✅ System runs without crashing
- ✅ APIs stay connected

**Failure criteria:**
- ❌ Zero opportunities (might be slow day)
- ❌ System crashes
- ❌ API disconnections

**Action after:**
- Review results
- Identify issues
- Plan Day 2 adjustments

---

### Day 2 (March 8)
**Focus:** Optimize scanning

**Potential adjustments based on Day 1:**
- Adjust scan interval (30s → 15s if missing opportunities)
- Adjust ARB threshold (0.5% → 0.3% if too few)
- Add debugging to see why opportunities missed

**Success criteria:**
- ✅ More opportunities than Day 1
- ✅ Positive R expectancy

---

### Day 3 (March 9)
**Focus:** Data collection

**Tasks:**
- Record all opportunities with timestamps
- Track which tracks/times are best
- Measure spread between backtest and reality

**Success criteria:**
- ✅ 3 days of data
- ✅ Pattern emerging

---

### Days 4-7 (March 10-13)
**Focus:** Refinement

**Tasks:**
- Implement top 3 improvements from edge study
- Test time-based filters
- Compare ARB vs VALUE performance

**Success criteria:**
- ✅ Consistent positive R
- ✅ System stable for full week

---

### Day 7 (March 14)
**Focus:** Week 1 review

**Questions to answer:**
1. What was total R for the week?
2. Which engine performed best?
3. What time of day had most opportunities?
4. What were the biggest issues?
5. Ready to implement improvements?

---

## Implementation Roadmap

### Phase 1: Validation (Week 1) ✅ IN PROGRESS
**Goal:** Prove the system works

**Deliverables:**
- [ ] Real opportunities logged
- [ ] R expectancy measured
- [ ] Issues identified

**No changes during this phase - just observe.**

---

### Phase 2: Optimization (Week 2)
**Goal:** Improve R expectancy

**Planned improvements:**
1. Add Neds API (same as Ladbrokes, easy)
2. Implement time filters (5-60 min before race)
3. Lower ARB threshold to 0.3%
4. Add volume confirmation to STEAM

**Expected impact:** +0.050R/trade

---

### Phase 3: Expansion (Week 3-4)
**Goal:** Increase volume

**Planned additions:**
1. Add greyhounds
2. Add early market monitoring (24h before)
3. Test liquidity harvesting

**Expected impact:** 2x opportunities

---

### Phase 4: Scaling (Month 2)
**Goal:** Increase stake size

**Milestones:**
- If +R after Week 1: Keep paper trading
- If +R after Week 2: Keep paper trading
- If +R after Month 1: Scale to 1R = $5
- If +R after Month 2: Scale to 1R = $12.50
- If +R after Month 3: Scale to 1R = $25

---

## Paper Trading Configuration

### Current Settings
```python
STAKE_1R = 1.00          # $1 AUD per trade
COMMISSION = 0.05        # 5% Betfair commission
MIN_ARB_PROFIT_PCT = 0.5 # 0.5% minimum ARB profit
MIN_STEAM_DROP_PCT = 5.0 # 5% minimum price drop
MIN_VALUE_EDGE_PCT = 10.0 # 10% minimum value edge
POLL_INTERVAL = 30       # 30 seconds between scans
TRADING_HOURS = "10:00-17:00" # Brisbane time
EXIT_BUFFER = 120        # Exit 2 mins before race
```

### Safety Rules
1. **Never** enter if < 2 mins to race start
2. **Always** exit by 2 mins before race
3. **Never** hold positions into in-play
4. **Stop** at 5pm Brisbane
5. **Paper mode** - no real money

---

## Data to Track

### Per Opportunity
- Timestamp
- Engine (ARB/STEAM/VALUE)
- Runner name
- Meeting name
- Race number
- Back price
- Lay price
- Expected R
- Minutes to race start

### Daily Summary
- Total opportunities
- By engine breakdown
- Total R
- Win rate (if exit price known)
- API uptime
- Errors encountered

### Weekly Summary
- Total R for week
- Average R per day
- Best performing engine
- Best time of day
- Issues and fixes

---

## Success Metrics

### Week 1 (Minimum Viable)
- ✅ System runs without crashing
- ✅ At least 10 opportunities found
- ✅ Positive R expectancy (any amount)

### Week 2 (Optimization)
- ✅ R expectancy > 0.05R/trade
- ✅ More than 50 opportunities
- ✅ ARB win rate > 95%

### Month 1 (Validation)
- ✅ R expectancy > 0.05R/trade (consistent)
- ✅ More than 500 opportunities
- ✅ System runs 95%+ uptime

### Month 2 (Scaling)
- ✅ Scale to 1R = $5
- ✅ Weekly profit > $50
- ✅ Ready to increase stake

---

## Risk Management

### Kill Switches
1. If R expectancy < -0.05R for 3 days → Stop and review
2. If system crashes > 3 times in a day → Debug before restart
3. If API errors > 10% → Stop and investigate
4. If any bet placed with real money → STOP IMMEDIATELY (should never happen in paper mode)

### Maximum Daily Loss
- **Paper mode:** No real money at risk
- **When live:** Max 3R per day ($3 at 1R=$1)

### Maximum Position Size
- **Paper mode:** 1R per opportunity
- **When live:** Never more than 2% of bank per trade

---

## Communication

### Daily Reports
- Automatic Telegram notification at ~4pm
- Includes: Opportunities, R profit, by engine

### Weekly Reports
- Manual summary on Day 7
- Includes: Week total, patterns, issues, next steps

### Immediate Alerts
- System crash
- API failure
- Unexpected behavior

---

## Files

### Output Files
- `steamarb_opportunities.json` - All opportunities logged
- `steamarb_log.csv` - Trade history
- `steamarb_safe.log` - Safety events

### Monitoring
- `python steamarb_monitor.py` - Check status anytime
- `python night_watch_status.py` - Time to 10am

### Documentation
- `STEAMARB_READY.md` - System status
- `STEAMARB_10AM_GUIDE.md` - User guide
- `research/betfair_edge_study.md` - Edge research

---

## Next Action

**1h 13m to 10am.**

The system is armed and will auto-start.

**Your role:** Wait for ~4pm notification.

**My role:** Monitor and report results.

---

*Plan created: March 7th, 2026, 8:47 AM*
*Paper trading starts: March 7th, 2026, 10:00 AM*
*First results: March 7th, 2026, ~4:00 PM*
