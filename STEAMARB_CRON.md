# SteamArb Cron Jobs - 2026-03-07

## Job 1: Hourly Backtest
**Purpose:** Validate system with 500-race simulation every hour
**Cron ID:** 58efa2c3-ea4e-4bc7-87ea-e933fe2c3fb8
**Schedule:** Every hour
**Session:** Isolated (fresh context)
**Command:** `python steam_arb_backtester.py --demo --races 500`

## Job 2: Safe Paper Trading (Planned)
**Purpose:** Paper trade during active racing hours (10am-5pm Brisbane)
**Safety:** ALWAYS exit before race starts ( **Schedule:** Every 15 minutes during active hours
**Command:** `python steam_arb_safe.py --duration 60`

## Active Hours:
- Start: 10:00 AM Brisbane (start scanning)
- End: 5:00 PM Brisbane (stop all trading)

## Safety Rules:
1. Never enter position if < 2 mins to race start
2. Always exit by 2 mins before race
3. Exit immediately if market goes in-play
4. Stop all trading at 5pm
5. Log all trades to steamarb_opportunities.json

## Critical:
- NEVER hold positions into race start
- If < 2 mins to start → EXIT IMMEDIATE
- If market goes in-play → EXIT ALL
- This prevents catastrophic losses

## Next Steps:
1. Test during active hours (10am-5pm)
2. Validate safety rules
3. Check exit timing
4. Review results after first session
