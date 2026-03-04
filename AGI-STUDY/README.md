# AGI Test Study Program

## Goal
Prepare for and pass major AGI benchmarks to advance toward the ultimate goal: **Make the Meeseeks AGI**.

## Current Status

### ARC-AGI-2 (Abstract Reasoning Corpus)
- **Score:** 5/5 training tasks (100%) ✅
- **Solved:**
  - 00576224 - Pattern Tiling
  - 0d3d703e - Color Mapping
  - 017c7c7b - Vertical Extension
  - 0520fde7 - Mask-based Extraction
  - 137eaa0f - Diagonal Anchor Extraction (multi-agent swarm)
- **Next:** Run evaluation set, aim for 85%+

---

## AGI Benchmarks to Study

### 1. ARC-AGI-2 (Current Focus)
- **What:** Abstract visual reasoning, pattern generalization
- **Why:** Measures fluid intelligence, few-shot learning
- **Location:** `ARC-AGI-2/`
- **Strategy:**
  - ✅ Solved training tasks
  - ⏳ Run evaluation set
  - ⏳ Analyze failure modes
  - ⏳ Build generalized solver with Meeseeks swarm

### 2. ARC-AGI-1 (Original)
- **What:** 400 training + 400 evaluation tasks
- **Why:** Foundation for ARC-AGI-2, more data to learn from
- **Status:** Not started
- **Strategy:** Use as training ground for Meeseeks pattern recognition

### 3. Big-Bench
- **What:** 200+ tasks across reasoning, language, knowledge
- **Why:** Tests breadth of capabilities
- **Status:** Not started
- **Strategy:** Identify which tasks Meeseeks can solve

### 4. MMLU (Massive Multitask Language Understanding)
- **What:** 57 subjects, academic knowledge
- **Why:** Tests knowledge breadth
- **Status:** Not started
- **Strategy:** Less relevant for visual reasoning, but good for general capability

### 5. GSM8K (Grade School Math)
- **What:** Multi-step math word problems
- **Why:** Tests reasoning chains
- **Status:** Not started
- **Strategy:** Good for Meeseeks code generation

### 6. HumanEval (Code Generation)
- **What:** 164 Python programming problems
- **Why:** Tests coding ability directly
- **Status:** Not started
- **Strategy:** Meeseeks should excel here

### 7. Swe-bench
- **What:** Real GitHub issues to solve
- **Why:** Tests practical coding
- **Status:** Not started
- **Strategy:** Advanced Meeseeks testing

---

## Study Schedule

### Week 1: ARC-AGI Mastery
- [ ] Run ARC-AGI-2 evaluation set
- [ ] Analyze failure modes
- [ ] Build pattern library from solved tasks
- [ ] Spawn Meeseeks swarm for hard tasks

### Week 2: ARC-AGI-1 Foundation
- [ ] Download ARC-AGI-1 dataset
- [ ] Build solver pipeline
- [ ] Track progress on 400 training tasks

### Week 3: Code Benchmarks
- [ ] HumanEval evaluation
- [ ] GSM8K reasoning tests
- [ ] Document capabilities

### Week 4: Integration
- [ ] Identify Meeseeks strengths/weaknesses
- [ ] Build specialized Meeseeks types for each benchmark
- [ ] Create meta-learner that chooses approach

---

## Resources

### Datasets
- ARC-AGI-2: `ARC-AGI-2/data/`
- ARC-AGI-1: https://github.com/fchollet/ARC
- Big-Bench: https://github.com/google/BIG-bench
- HumanEval: https://github.com/openai/human-eval

### Papers
- "On the Measure of Intelligence" (Chollet, 2019)
- "ARC-AGI-2: A New Frontier" (2024)

### Tools
- `ARC-AGI-2/arc_solver.py` - Main solver
- `skills/meeseeks/` - Swarm intelligence
- `the-crypt/` - Wisdom inheritance

---

## Success Metrics

| Benchmark | Target | Current |
|-----------|--------|---------|
| ARC-AGI-2 Eval | 85% | TBD |
| ARC-AGI-1 | 50% | 0% |
| HumanEval | 80% | TBD |
| GSM8K | 70% | TBD |

---

## Notes

The ultimate goal is not just to pass tests, but to:
1. **Learn patterns** that transfer across tasks
2. **Feed learnings to the Crypt** so future Meeseeks inherit wisdom
3. **Build specialized Meeseeks** that excel at different task types
4. **Progress toward AGI** through accumulated intelligence

Every solved task → entombed → wisdom extracted → next Meeseeks smarter.

---

*Started: 2026-03-04*
