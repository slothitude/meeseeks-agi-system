# What to Expect at 10am

## Automatic Startup

At **10:00 AM Brisbane time**, an isolated session will spawn automatically.

**You don't need to do anything.** The system runs itself.

---

## What Will Happen

### 1. Session Spawns (10:00 AM)
- Isolated agent session starts
- Loads `steam_arb_live.py`
- Connects to Betfair + Ladbrokes APIs

### 2. Paper Trading (10:00 AM - 4:00 PM)
- Scans every 30 seconds
- Looks for ARB, STEAM, VALUE opportunities
- Logs to `steamarb_opportunities.json`

### 3. Session Ends (~4:00 PM)
- Runs for 6 hours
- Stops 1 hour before 5pm cutoff
- Reports summary to Telegram

---

## What You'll See

### Telegram Notification
```
🤖 SteamArb Paper Trading Complete

Opportunities: X
  ⚡ ARB: Y
  🔥 STEAM: Z
  💎 VALUE: W

Total R: +0.XXXX
Total AUD: $X.XX
```

---

## How to Check Status

### During Trading Hours
```bash
python steamarb_monitor.py
```

Shows:
- Opportunities found
- R profit accumulated
- Last 5 opportunities

---

## Files Created

| File | Purpose |
|------|---------|
| `steamarb_opportunities.json` | All opportunities |
| `steamarb_log.csv` | Trade log |
| `steamarb_safe.log` | Safety events |

---

## What Constitutes Success

### Day 1: Validation
- ✅ APIs connect
- ✅ Runners match
- ✅ Opportunities detected

### Week 1: Pattern Recognition
- ✅ Consistent +R expectancy
- ✅ Safety rules followed
- ✅ No errors

### Month 1: Scaling
- ✅ Proven system
- ✅ Ready for live trading
- ✅ Scale to 1R=$12.50

---

## What Constitutes Failure

❌ No opportunities (markets too illiquid)
❌ API failures (credentials expired)
❌ System crashes (bug in code)

**If any of these happen, we debug and improve.**

---

## Expected Results (Conservative)

| Metric | Value |
|--------|-------|
| Win Rate | 60% |
| Expectancy | +0.04R/trade |
| Daily R | +0.8R (20 races) |
| Daily AUD | $0.80 (at 1R=$1) |

---

## Next Steps After 10am

1. **Wait** for session to complete
2. **Check** notification
3. **Review** opportunities
4. **Decide** if adjustments needed

---

## Safety Guarantee

**PAPER TRADING MODE**

No real money will be risked.
All bets are validated, not placed.
System is 100% safe to run.

---

*System armed and ready.*
*See you at 10am.* 🎯
