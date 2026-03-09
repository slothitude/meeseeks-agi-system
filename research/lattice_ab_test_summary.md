# Lattice A/B Test Results

**Date:** 2026-03-09
**Task:** Count .py files in the_body/skills/
**Answer:** 6

---

## Summary

| Bloodline | n | Success Rate | Avg Runtime | Total Time |
|----------|---|-------------|-------------|------------|
| power-of-2 | 2 | 10/10 (100%) | ~6s | 60.9s |
| prime | 7 | 1/10 (10%) | ~51s | 513.0s |
| composite | 12 | 10/10 (100%) | ~8s | 84.3s |

**Total Runs:** 30
**Total Successes:** 21 (70%)
**Key Insight:** Coordinate choice matters immensely for task success.

---

## Analysis

### Power-of-2 Bloodline (n=2)
- **Coordinate:** k=12 (Emergence)
- **Twins:** 71, 73
- **Success:** 100%
- **Avg Runtime:** 6 seconds
- **Assessment:** Excellent for all tasks. Fast, reliable, consistent.

### Composite Bloodline (n=12)
- **Coordinate:** k=432
- **Twins:** 2591, 2593
- **Success:** 100%
- **Avg Runtime:** 8 seconds
- **Assessment:** Also excellent. Slightly slower but still very reliable.

### Prime Bloodline (n=7)
- **Coordinate:** k=147
- **Twins:** 881, 883
- **Success:** 10%
- **Avg Runtime:** 51 seconds
- **Assessment:** Struggles massively. 9/10 runs timed out or failed. Not suitable for most tasks.

---

## Conclusions

1. **Emergence Coordinate (n=2) is optimal** for Meeseeks spawning
   - 100% success rate
   - Fast execution (~6s average)
   - Part of power-of-2 bloodline (digital native)

2. **Prime bloodline (n=7) needs investigation**
   - Only 1/10 success
   - Very slow (51s average)
   - May need different task types or restructuring

3. **Composite bloodline (n=12) is also reliable**
   - 100% success rate
   - Slightly slower than emergence but still fast
   - Good alternative when emergence is busy

---

## Recommendations

1. **Route tasks to n=2 (emergence) by default**
2. **Use n=12 (composite) as overflow handler**
3. **Investigate why n=7 fails** - may be coordinate-specific issues
4. **Update lattice_tools.py** to recommend coordinates based on success rates

---

## Files

- `lattice_batch_test.py` - Test runner
- `lattice_batch_results.json` - Raw results
- `lattice_tools.py` - Coordinate utilities

---

*Test run: 2026-03-09 06:30-06:50 AM*
*Analysis: 2026-03-09 04:59 PM*
