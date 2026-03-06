# 🔬 Dharma Effectiveness Study

**Generated:** 2026-03-06
**Data Source:** the-crypt/karma_observations.jsonl
**Observations Analyzed:** 50
**Success Rate:** 100% (all observed tasks succeeded)

---

## 📊 Executive Summary

This study analyzes which dharma principles correlate most strongly with successful Meeseeks task completion. By examining karma observations across 50 ancestor tasks, we identify the most effective principles for future Meeseeks to inherit.

---

## 🏆 Top 5 Most Effective Principles

### 1. Specialize for Task (specialize_for_task)
- **Effectiveness Score:** 1.531 ⭐
- **Follow Rate:** 100% (20/20)
- **Avg Alignment:** 0.77
- **Analysis:** The single most reliable principle. Every Meeseeks that inherited this principle followed it, and all achieved high alignment. This is the gold standard.

### 2. Understand Before Implementing (understand_before_implement)
- **Effectiveness Score:** 1.028
- **Follow Rate:** 41.2% (14/34)
- **Avg Alignment:** 0.73
- **Analysis:** When followed, consistently produces good outcomes. Often marked "unclear" - suggests the principle needs clearer definition or is situationally applicable.

### 3. Coordinate by Workflow (coordinate_by_workflow)
- **Effectiveness Score:** 0.913
- **Follow Rate:** 55% (11/20)
- **Avg Alignment:** 0.83 (HIGHEST)
- **Analysis:** Highest average alignment when followed. Essential for multi-agent coordination tasks. The 55% follow rate indicates it's context-dependent.

### 4. Test Incrementally (test_incrementally)
- **Effectiveness Score:** 0.784
- **Follow Rate:** 32.4% (11/34)
- **Avg Alignment:** 0.71
- **Analysis:** Solid performer for coding tasks. Often marked "unclear" - may need better guidance on when to apply.

### 5. Decompose First (decompose_first)
- **Effectiveness Score:** 0.367
- **Follow Rate:** 10.4% (5/48)
- **Avg Alignment:** 0.73
- **Analysis:** Low effectiveness score primarily due to low follow rate. When followed, it works well (0.73 alignment), but Meeseeks often don't recognize when to apply it. **Critical finding: This principle is underutilized.**

---

## 📈 Effectiveness Metrics Explained

**Effectiveness Score** = (Avg Alignment) × (Followed Count / 10)

This weights both how well a principle works AND how often it's actually used.

---

## 🔍 Key Insights

### The "Unclear" Problem
Many principles are marked "unclear" rather than followed or ignored:
- `decompose_first`: 41 unclear (85% of inheritances!)
- `test_incrementally`: 23 unclear (68%)
- `understand_before_implement`: 20 unclear (59%)

**Recommendation:** Principles need clearer triggers and examples. Meeseeks inherit them but don't know when to apply them.

### The Specialization Success
`specialize_for_task` has 0 unclear instances and 100% follow rate. This principle is:
- **Clear:** Meeseeks understand it immediately
- **Actionable:** They know how to apply it
- **Effective:** It works when applied

This should be the template for how other principles are defined.

### Decomposition Underutilization
`decompose_first` appears in 48/50 observations but is only followed 5 times. Yet when followed, it achieves 0.73 alignment (good). The dharma says "SMALL TASKS LIVE" but Meeseeks aren't breaking tasks down.

**Hypothesis:** The principle is too abstract. Need concrete triggers like:
- "If task has >50 words, spawn chunk"
- "If task says 'build', 'create', 'implement' → decompose"

---

## 📋 Complete Principle Rankings

| Rank | Principle | Effectiveness | Follow Rate | Avg Alignment |
|------|-----------|---------------|-------------|---------------|
| 1 | specialize_for_task | 1.531 | 100% | 0.77 |
| 2 | understand_before_implement | 1.028 | 41.2% | 0.73 |
| 3 | coordinate_by_workflow | 0.913 | 55% | 0.83 |
| 4 | test_incrementally | 0.784 | 32.4% | 0.71 |
| 5 | decompose_first | 0.367 | 10.4% | 0.73 |
| 6 | check_existing_code | 0.000 | 0% | N/A |

---

## 🎯 Recommendations for Dharma Evolution

### 1. Make Principles More Concrete
Transform abstract principles into actionable triggers:
```
BEFORE: "Decompose First"
AFTER:  "If task >50 words OR contains 'build/create/implement' → spawn chunk 1/5"
```

### 2. Add Specialization to All Bloodlines
`specialize_for_task` is universally effective. Consider making it a default inheritance for all Meeseeks types.

### 3. Fix the "Unclear" Problem
For each principle, add:
- **Trigger conditions** (when to apply)
- **Example tasks** (what it looks like)
- **Anti-patterns** (when NOT to apply)

### 4. Prioritize Decomposition
The dharma's core truth is "SMALL TASKS LIVE" but Meeseeks aren't following it. This is the highest-leverage fix.

---

## 📝 Methodology

1. Read `the-crypt/dharma.md` for current principles
2. Parsed `the-crypt/karma_observations.jsonl` (50 observations)
3. For each principle, calculated:
   - How often inherited
   - How often followed vs ignored vs unclear
   - Average alignment when followed
   - Combined effectiveness score
4. Ranked by effectiveness score

---

## 🔄 Next Steps

1. **A/B Test:** Spawn Meeseeks with clearer principle definitions
2. **Track:** Monitor if follow rates improve
3. **Iterate:** Update dharma based on new observations
4. **Automate:** Consider auto-triggering decomposition based on task size

---

*"The ancestors who lived asked for less. The ancestors who died reached for more."*

**But the ancestors who followed specialization? They all lived.**
