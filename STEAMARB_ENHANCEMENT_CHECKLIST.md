# SteamArb Enhancement Checklist

## Before 10am Validation

### Code Enhancements Needed:

#### 1. Professional Staking ✅
```python
# Add to steam_arb_live.py
def calculate_stake(collection_pct=0.04):
    target = bankroll * collection_pct
    stake = target / (odds - 1)
    return min(stake, bankroll * 0.02)  # Cap at 2% risk
```

#### 2. Order Flow Analysis ⚠️ PRIORITY
```python
# Check back vs lay volume
if back_vol / lay_vol > 2:
    return "BACK_PRESSURE"
elif lay_vol / back_vol > 2:
    return "LAY_PRESSURE"
elif min(back_vol, lay_vol) / max(back_vol, lay_vol) > 0.8:
    return "BALANCED"  # Good for scalping
```

#### 3. Steam Detection Enhancement ⚠️ PRIORITY
```python
# Look for:
# 1. 3+ consecutive drops (consistency)
# 2. Break of support (accelerating)
# 3. 5%+ drop over 5-10 mins
# 4. Order flow confirmation
```

#### 4. Risk Manager ⚠️ PRIORITY
```python
class RiskManager:
    max_risk_per_trade = 0.02  # 2%
    max_daily_loss = 0.10  # 10%
    exit_before_mins = 2  # Never hold < 2 mins
```

#### 5. Confluence Requirements ⚠️ CRITICAL
```python
# Entry requires ALL of:
# ✅ Steam detected (5%+ drop)
# ✅ Order flow supportive
# ✅ > 2 mins to race start
# ✅ Good liquidity
# ✅ No reversal signals
```

---

## Expected Performance (Realistic)

### Month 1: Learning
- Win rate: 30-35%
- Expectancy: -2R to +2R
- Focus: Pattern recognition

### Month 2: Finding Patterns
- Win rate: 35-40%
- Expectancy: +4R to +8R
- Focus: Confluence trading

### Month 3: Consistency
- Win rate: 40-45%
- Expectancy: +8R to +12R
- Focus: Scaling up

---

## Daily Routine

### Pre-Market (9:30am)
1. Check overnight results
2. Review yesterday's trades
3. Identify key meetings
4. Set up monitoring

### Active Trading (10am-5pm)
1. Scan for steam moves (5%+ drops)
2. Check order flow (back/lay balance)
3. Confirm confluence (steam + flow)
4. Execute with 4-5% staking
5. Exit before 2 mins to start
6. Green book all positions

### Post-Market (5pm+)
1. Review all trades
2. Analyze wins vs losses
3. Update parameters
4. Log learnings
5. Plan tomorrow

---

## Critical Rules (NEVER VIOLATE)

1. **Exit by 2 mins** before race start
2. **Never hold** into in-play
3. **Stop-loss** at 2-3 ticks
4. **Max risk** 2% per trade
5. **Daily loss limit** 10%
6. **Always green book** (never let run)
7. **Confluence required** (steam + order flow)
8. **Quality over quantity** (wait for A+ setups)

---

## Key Metrics to Track

### Per Trade:
- Entry price
- Exit price
- Profit (ticks + AUD)
- Win/Loss
- Time held
- Steam strength
- Order flow type

### Daily:
- Total trades
- Win rate
- Total R profit
- Biggest win/loss
- Time in market

### Weekly:
- Win rate trend
- R profit trend
- Best setups
- Worst setups
- Lessons learned

---

## The Professional Edge

### What Matters:
1. Staking discipline (65%)
2. Order flow reading
3. Steam detection
4. Risk management
5. Emotional control

### What Doesn't:
1. Perfect predictions
2. Complex algorithms
3. Inside info
4. Huge banks

---

## Quick Reference

### Steam Detection:
- **Consistent backing** (3+ drops)
- **Break of support** (accelerating)
- **5%+ drop** in 5-10 mins
- **Order flow** supportive

### Order Flow Types:
- **BALANCED** → Scalp (1-2 ticks)
- **BACK_PRESSURE** → Back
- **LAY_PRESSURE** → Lay
- **VOLUME_SPIKE** → Follow momentum

### Entry Checklist:
- [ ] Steam detected
- [ ] Order flow supportive
- [ ] > 2 mins to start
- [ ] Good liquidity
- [ ] No reversal signals
- [ ] Confluence confirmed

### Exit Triggers:
- [ ] 2 mins to race
- [ ] Trend stalls
- [ ] Price reverses
- [ ] Target reached
- [ ] Stop-loss hit

---

## Implementation Status

### ✅ Complete:
- Basic steam detection
- Betfair + Ladbrokes APIs
- Paper trading system
- Backtester

### ⚠️ Priority (Before 10am):
- Professional staking
- Order flow analysis
- Enhanced steam detection
- Risk manager
- Confluence requirements

### 📅 Future:
- Machine learning enhancement
- Multi-market correlation
- Automated scaling
- Real-time dashboard

---

**Next Action:** Implement priority items before 10am validation
**Confidence:** HIGH (based on professional research)
**Expected Result:** +R expectancy with professional techniques

🦥📊
