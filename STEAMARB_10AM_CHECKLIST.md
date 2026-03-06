# SteamArb 10am Checklist

## ✅ Before 10am (Already Done)

- [x] Betfair API tested and working
- [x] Ladbrokes API tested and working
- [x] Steam engine code reviewed
- [x] Paper trading mode enabled
- [x] Cron job scheduled for 10am
- [x] Safety rules implemented

## ⏰ At 10am (Automatic)

- [ ] Isolated session spawns
- [ ] SteamArb engine starts
- [ ] APIs connect
- [ ] Scanning begins

## 🔍 After Session (Check These)

### 1. Check Notification
```
Look for Telegram message with:
- Total opportunities
- R profit
- By engine breakdown
```

### 2. Run Monitor
```bash
python steamarb_monitor.py
```

### 3. Review Files
```bash
# Check opportunities
cat steamarb_opportunities.json | python -m json.tool | head -50

# Check log
head -20 steamarb_log.csv
```

### 4. Validate Results

**Success Indicators:**
- ✅ Opportunities found (even 1 is good)
- ✅ Positive R expectancy
- ✅ No errors in logs
- ✅ All engines detected something

**Concern Indicators:**
- ⚠️ Zero opportunities (might be slow day)
- ⚠️ Negative R (need to investigate)
- ⚠️ API errors (credentials expired?)
- ⚠️ System crashed (bug in code)

## 📊 Expected Results (Day 1)

| Metric | Conservative | Optimistic |
|--------|-------------|------------|
| Opportunities | 5-20 | 50-100 |
| Win Rate | 50% | 70% |
| R Profit | +0.1R | +1.0R |
| AUD Profit | $0.10 | $1.00 |

## 🎯 Decision Points

### If Results Good
- Continue paper trading for 1 week
- Validate consistency
- Prepare for live trading

### If Results Bad
- Debug issues
- Adjust parameters
- Re-test tomorrow

### If No Data
- Check API connections
- Verify markets are open
- Check runner matching

## 📝 Questions to Answer

1. Did the system find opportunities?
2. Which engine found most? (ARB/STEAM/VALUE)
3. What was the average R per opportunity?
4. Were there any errors?
5. Did safety rules trigger?

## 🔧 Quick Commands

```bash
# Check status
python steamarb_monitor.py

# View opportunities
python -c "import json; print(json.dumps(json.load(open('steamarb_opportunities.json')), indent=2)[:500])"

# Count opportunities by engine
python -c "import json; opps=json.load(open('steamarb_opportunities.json')); print({'ARB': len([o for o in opps if o.get('engine')=='ARB']), 'STEAM': len([o for o in opps if o.get('engine')=='STEAM']), 'VALUE': len([o for o in opps if o.get('engine')=='VALUE'])})"

# Check log exists
ls -la steamarb_log.csv
```

---

## Remember

**This is Day 1.**
- No expectations of profit
- Goal is validation
- Systems working = success
- Small R = building blocks

**Patience is key.**
- Professional traders work for years
- We are at day 1
- Every system starts at 0
- Trust the process

---

*Checklist for March 7th, 2026 - First Paper Trading Day*
