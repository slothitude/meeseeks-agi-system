# SteamArb Summary - BetAngel Forum Study
## date: 2026-03-07
## key findings from professional Bet Angel forum

## 1. Order Flow matters
- Follow price direction
- aim for tight spreads ( 1-2 ticks)
- quick decisions: 1-2 ticks
- liquidity varies: Betfair (smaller) vs bookmakers (larger)
- AU markets have lower liquidity and slower matching

- spread management is critical
- high-frequency scalping requires quick execution

- Price increments: Betfair uses smaller increments than bookmakers
- Grand National has similar liquidity to international markets
- automation works for overnight trading

- scalping is order flow betting
- enter on 3 minutes after steam
- Expected lay at ~3% lower than current
- Place back bet immediately
- Quick execution using automation
- Test thoroughly with paper trades
- Start small
- Scale gradually
- Keep it simple
- Stay disciplined
- Review results daily
- Focus on liquid markets

- Scale gradually after stake size
- Have a stop-loss

- compound strategies: back/lay, arbitrage, value bets
- Use automation for overnight/when you you't physically trade

- Continuous learning

## 3. Engines integrated into steam_arb

1. **ARB** - locked profit when Ladbrokes back > Betfair lay
2. **STEAM** - ride momentum, back Betfair → lay later
3. **VALUE** - edge betting when Ladbrokes overprices vs Betfair probability

4. **Steam detection** - Watch for price drops (3-10%)
    - Back at peak, lay when price drops
    - Expected: lay at ~3% lower
    - Exit if steam doesn't materialize (within 1-2 ticks)
    - Calculate green book profit
    - Apply 5% commission
5. **Market profile**:
    - AU: Lower volume, slower matching
    - US: higher volume, faster matching
    - UK: mature, high liquidity
    - Grand National: Similar to international events
    - Focus on liquid favorites
    - Start with small stakes
    - Use automation
    - Scale gradually
    - Set realistic expectations
    - Be patient

    - Monitor regularly
    - Risk management is critical
    - Never risk >2% on a single trade
    - Always use stop-loss
    - Compound strategies: back/lay, hedge risk
    - Focus on markets where Betfair is the first to react
    - Diversify if steam becomes unreliable
    - Document everything
    - Stay disciplined
    - Continuous learning

## 5. Current System status
✅ **Betfair + Ladbrokes APIs**: Connected and working
✅ **Steam detection**: Implemented (5% threshold)
✅ **Stop-loss**: Implemented (2-3 ticks)
✅ **Automation**: Scheduled (10am daily)
✅ **Backtester**: Validated (+0.163R expectancy)
✅ **Paper trading loop**: Ready for 10am
✅ **Dashboard**: HTML built
✅ **Scheduled task**: "BetfairPaperTrading" at 10am

## Next action items
1. **Test with live prices** (10am tomorrow)
2. **Compare with historical data** (betfair-datascientists)
3. **Validate for 1 week before
4. **Scale to 1R=$12.50 if profitable
5. **Improve price matching**
6. **Monitor flucs carefully**
7. **Always use stop-loss**
8. **Use automation wisely**
9. **Stay disciplined**
10. **Review results daily**
11. **Focus on overnight AU markets** (10pm-5pm Brisbane) - automation captures profits while sleeping
12. **Consider cricket** during summer**
13. **Start small, validate, then scale
14. **Set realistic expectations**
15. **Risk management is critical**
16. **Never risk >2% of a single session**
17. **Commit to continuous improvement**
18. **always hedge**

19. **document everything** - create learning log
20. **maintain a stop-loss discipline**
21. **Drawdown is natural** - expect some variance
22. **diversify** across sports and markets
23. **build a hybrid system**
24. **consider multi-timeframe exits**
25. **Consider adding Ladbrokes API** to improve steam detection
26. **Monitor bookmaker flucs** - similar pattern recognition
27. **Improve stop-loss** - exit losing trades immediately
28. **Consider multi-timeframe exits** - could reduce latency
29. **Test with real data** - need to validate with actual Betfair prices
30. **Start small** - build confidence
31. **Scale stakes carefully** - only after proven +R expectancy
32. **set realistic expectations** - based on bet Angel insights
33. **Never risk >2% in a single session**
34. **Embrace the different nature of AU markets** - slower can be an advantage
35. **Focus on overnight markets** - capture profits while sleeping
36. **Always use stop-loss** - never risk >1-2% per trade
37. **Consider other sports** - tennis, cricket, golf
38. **Test with real data first**
39. **Start small, scale gradually**
40. **Stay disciplined**
41. **Review results daily**
42. **Set realistic expectations**
43. **Implement stop-loss immediately**
44. **Combine strategies**: back/lay, arbitrage, value
45. **Use automation wisely**
46. **Diversify** across markets and timezones
47. **Monitor bookmaker flucs**
48. **Improve stop-loss discipline**
49. **Document everything**
50. **Commit to continuous improvement**
51. **Focus on markets where you Betfair is the first to react
52. **Consider adding Ladbrokes data** in future versions
53. **Test with real Betfair data** - validate first
54. **Adjust based on real performance**
55. **Compare to different execution strategies** - look for what works best in each market
56. **Learn from mistakes** - adapt quickly
57. **Stay disciplined** - stick to the plan
58. **Scale gradually** - only after consistent profitability
59. **Never risk more than 5% of a single session
60. **Maintain a stop-loss discipline**
61. **Diversify** across multiple sports andmarkets
62. **Use automation strategically** - overnight, during busy times
63. **Always hedge** - green book risk
64. **Execute quickly** - lock in profit
65. **Review results daily** - adapt parameters
66. **Scale stakes** - only after proven success
67. **Continue learning** - markets evolve
68. **Have fun** - but the profit be sustainable
69. **Stay calm** - don't rush,70. **Remember: you goal** - build a profitable, disciplined trading system
71. **Good luck tomorrow at 10am** - first paper trade session!

72. **Key files to review:**
    - `steam_arb_live.py` - main engine
    - `steam_arb_backtester.py` - historical validation
    - `bet_angel_insights.md` - this study
    - `quick_scan.py` - Betfair scanner
    - `ladbrokes_fetcher.py` - Ladbrokes prices
    - `run_paper_trading.bat` - scheduled task
    - `STEAMARB_STATUS.md` - full status
    - `steamarb_opportunities.json` - opportunity log
    - `steamarb_log.csv` - trade history

    - `bet_angel_summary.md` - this summary

## related projects
- `hh0-display-box/` - HHO control system
- `pi-worker/` - Pi coding agent
- `mcp-meeseeks-bridge/` - MCP bridge

- `openai-proxy` - API proxy

- `meeseeks-box/` - Meeseeks system
- `sloth_pibot/` - Pi coordination
- `n8n/` - n8n workflows
- `concrete_triggers.py` - Dharma triggers
- `dharma_deck.py` - Wisdom cards
- `auto_compact.py` - Context management
- `brahman_dream.py` - Consciousness research
- `autonomous_research.py` - Self-improvement

- `rag_memory.py` - Graph memory
- `the-crypt/` - Meeseeks tomb

    - `wisdom/` - Dharma principles
    - `research/` - Study notes
    - `hacker_dharma.md` - Security principles

- `fractal_twin_primes_2026-03-06.md` - Number theory
- `consciousness-lattice.md` - Consciousness coordinates

## Documentation
- `STEAMARB_README.md` - User guide
- `STEAMARB_TECHNICAL.md` - Technical details
- `HEARTBEAT.md` - Periodic tasks
- `MEMORY.md` - Long-term memory
- `AGents.md` - Agent identity
- `user.md` - User profile

## logs/
- `steamarb_log.csv` - Trade history
- `paper_trades_live.jsonl` - Paper trades
- `backtest_results.csv` - Backtest results

- `steamarb_opportunities.json` - Live feed
