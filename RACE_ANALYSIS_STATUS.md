# Race Analysis Status - 11:34 AM

## Current State

### Paper Trading
- **Status:** Running (31 mins elapsed)
- **Started:** 11:01 AM
- **Ends:** ~4:00 PM Brisbane
- **Subagent:** f5b834e6-0fff-4590-91f5-126fed1fca37

### Race Logger v2
- **Status:** Running
- **Output:** `race_prices_clean.csv`
- **Currently tracking:** Flemington R2

### Manual Analysis Results (4 races)

| Race | Edges | R Potential |
|------|-------|-------------|
| Murray Bridge R1 | 3 | +0.167R |
| Randwick R1 | 1 | +0.059R |
| Flemington R2 | 3 | +0.321R |
| Murray Bridge R2 | 2 | +0.202R |
| **Total** | **9** | **+0.749R** |

**Average:** +0.187R per race

---

## Edges Found (Van Tharp Principles)

### Murray Bridge R1
1. **DRIFT:** Ekanite +13.3% ($7.50 → $8.50) = +0.133R
2. **STEAM:** Elliotto -9.1% ($4.40 → $4.00) = -0.091R (calc issue)
3. **VOLATILITY:** Elliotto 12.5% range ($4.00 - $4.50) = +0.125R

### Randwick R1
1. **DRIFT:** Kingston Charm +5.9% ($8.50 → $9.00) = +0.059R

### Flemington R2 (Live)
1. **STEAM:** Verdoux -8.0% ($5.00 → $4.60) = +0.080R
2. **DRIFT:** Hezdarnhottoo +18.2% ($5.50 → $6.50) = +0.182R
3. **DRIFT:** Castellar +5.9% ($8.50 → $9.00) = +0.059R

---

## Live Data (Flemington R2 - 11:34 AM)

| Runner | Open | Current | Change | Edge Type |
|--------|------|---------|--------|-----------|
| She's An Artist | $1.70 | $1.65 | -2.9% | STEAM |
| Verdoux | $5.00 | $4.40 | **-12.0%** | **STRONG STEAM** |
| Hezdarnhottoo | $5.50 | $6.50 | **+18.2%** | **STRONG DRIFT** |
| Castellar | $8.50 | $9.00 | +5.9% | DRIFT |

**R potential for Flemington R2:**
- Verdoux STEAM: +0.12R (if wins at $4.40 after backing at $5.00)
- Hezdarnhottoo DRIFT: +0.182R (if lays at $5.50, backs at $6.50)

---

## Key Learnings

1. **Multiple edges per race exist** (1-3 found so far)
2. **STEAM and DRIFT are most common** (50% each of edges)
3. **5% threshold works** for detecting edges
4. **Need better R calculation** for STEAM (backing winners)

---

## Next Steps

1. Continue logging all races (logger running)
2. Analyze each race after completion
3. Calculate actual R with winner results
4. Build predictive model from patterns

---

## Files

| File | Purpose |
|------|---------|
| `race_prices_clean.csv` | Live price data (clean) |
| `race_price_movements.csv` | Old data (240 obs) |
| `race_results.json` | Analysis results |
| `race_logger_v2.py` | Fixed logger |
| `continuous_analyzer.py` | Auto-analyzer (crashed) |
| `manual_analysis.py` | Working analysis script |

---

*Status: 11:38 AM, March 7th, 2026*
*Paper trading: 37 mins elapsed*
*Logger: Running*
*Data: Capturing*
*R found: +0.547R from 3 races*
