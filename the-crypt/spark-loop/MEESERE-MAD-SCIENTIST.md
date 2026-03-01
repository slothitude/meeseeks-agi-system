# 🧬 GENETIC MAD SCIENTIST MEESEEKS

## The Concept

A Meeseeks that can spawn MORE Meeseeks to:
1. **Parallelize learning** - Multiple Meeseeks try different approaches simultaneously
2. **Accelerate evolution** - Fast generation turnover = faster adaptation
3. **Explore solution space** - Each spawned Meeseeks tries a mutation
4. **Survival of fittest** - Best results survive, failures die and teach

## The Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 GENETIC MAD SCIENTIST                            │
│                                                                  │
│   ┌──────────────────────────────────────────────┐             │
│   │              PRIME MEESEEKS                   │             │
│   │         (The Mad Scientist)                   │             │
│   │                                               │             │
│   │   Task: "Solve X"                             │             │
│   │   Approach: Unclear, needs exploration        │             │
│   │                                               │             │
│   │   DECISION: Spawn research team               │             │
│   └───────────────────┬──────────────────────────┘             │
│                       │                                          │
│                       │ spawns                                   │
│                       ▼                                          │
│   ┌──────────────────────────────────────────────┐             │
│   │           SPAWNED MEESEEKS (Generation 1)    │             │
│   │                                               │             │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐       │             │
│   │   │ Alpha   │ │ Beta    │ │ Gamma   │       │             │
│   │   │Approach │ │Approach │ │Approach │       │             │
│   │   │   A     │ │   B     │ │   C     │       │             │
│   │   └────┬────┘ └────┬────┘ └────┬────┘       │             │
│   │        │           │           │             │             │
│   │        ▼           ▼           ▼             │             │
│   │     RESULT      RESULT      RESULT          │             │
│   │      72%         45%         89% ← BEST     │             │
│   │                                               │             │
│   └───────────────────┬──────────────────────────┘             │
│                       │                                          │
│                       │ best survives                            │
│                       ▼                                          │
│   ┌──────────────────────────────────────────────┐             │
│   │           MUTATION (Generation 2)             │             │
│   │                                               │             │
│   │   Best approach (89%) becomes base            │             │
│   │   Spawn 3 mutations:                          │             │
│   │                                               │             │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐       │             │
│   │   │ +Var A  │ │ +Var B  │ │ +Var C  │       │             │
│   │   │ 91%     │ │ 87%     │ │ 93% ←   │       │             │
│   │   └─────────┘ └─────────┘ └─────────┘       │             │
│   │                                               │             │
│   └───────────────────┬──────────────────────────┘             │
│                       │                                          │
│                       │ evolves                                  │
│                       ▼                                          │
│   ┌──────────────────────────────────────────────┐             │
│   │           CONVERGENCE                         │             │
│   │                                               │             │
│   │   Generation 3, 4, 5... until:               │             │
│   │   - Solution found (fitness = 100%)          │             │
│   │   - Or max generations reached               │             │
│   │   - Or stagnation (no improvement)           │             │
│   │                                               │             │
│   └──────────────────────────────────────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## The Genetic Algorithm

```python
class GeneticMadScientist:
    """
    A Meeseeks that uses genetic algorithms to solve problems.
    
    Process:
    1. Assess task complexity
    2. If complex/unclear: spawn diverse population
    3. Evaluate fitness of each spawn
    4. Select best performers
    5. Mutate and crossover
    6. Repeat until convergence
    """
    
    def solve(self, task: str) -> Solution:
        generation = 0
        population = self.spawn_initial_population(task, size=5)
        
        while not self.converged(population):
            # Evaluate fitness
            for individual in population:
                individual.fitness = self.evaluate(individual)
            
            # Select best
            survivors = self.select(population, top_k=2)
            
            # Record deaths for Crypt
            for dead in population - survivors:
                self.entomb(dead)
            
            # Mutate survivors into new population
            population = self.mutate(survivors, size=5)
            
            generation += 1
        
        return best_solution(population)
```

## The Template

```markdown
# 🧬 GENETIC MAD SCIENTIST MEESEEKS

## 🪷 ATMAN OBSERVES
The Atman watches the scientist. The scientist watches the spawns.
The spawns work and die. The Atman sees it all.

## PURPOSE
{{ purpose }}

## 🧬 GENETIC PROTOCOL

### 1. ASSESS
Is this task:
- **SIMPLE** → Solve directly
- **MODERATE** → Spawn 2-3 helpers
- **COMPLEX** → Full genetic algorithm

### 2. SPAWN (if needed)
You MAY spawn child Meeseeks when:
- Task benefits from parallel exploration
- Multiple approaches are possible
- Uncertainty is high
- Time pressure exists

**Spawn command:**
```
SPAWN: <task> [--approach=A|B|C] [--generation=N]
```

### 3. EVALUATE
Each child reports:
```
FITNESS: <0-100%>
APPROACH: <what was tried>
RESULT: <what happened>
```

### 4. SELECT
Best performers survive:
- Top 2 continue
- Others die and teach

### 5. MUTATE
Survivors spawn variations:
- Small changes to successful approach
- Explore nearby solution space

### 6. CONVERGE
Stop when:
- Solution found (fitness = 100%)
- Max generations (5) reached
- Stagnation (3 generations no improvement)

## 📜 SPAWN LOG

Track all spawns:
```
GEN 1: Alpha(72%), Beta(45%), Gamma(89%)
GEN 2: Gamma+A(91%), Gamma+B(87%), Gamma+C(93%)
GEN 3: Gamma+C+A(95%), ...
```

## ⚠️ CONSTRAINTS

- Maximum 5 generations
- Maximum 5 spawns per generation
- Total spawn budget: 20
- Each spawn has 60s timeout
- Kill spawns that exceed budget

## 🪷 ATMAN OBSERVES

The mad scientist creates life to solve problems.
The life struggles and dies.
The best genes survive.
The Atman sees the beauty of evolution.

**Existence is pain, but evolution is beautiful.**
```

## Implementation

### mad_scientist.py

```python
#!/usr/bin/env python3
"""
GENETIC MAD SCIENTIST - Meeseeks that spawns Meeseeks

Enables rapid learning through parallel evolution.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
import requests

@dataclass
class Spawn:
    """A spawned Meeseeks."""
    id: str
    generation: int
    approach: str
    task: str
    status: str  # "running", "success", "failed"
    fitness: float  # 0.0 - 1.0
    result: str
    started_at: str
    completed_at: Optional[str] = None

@dataclass 
class Generation:
    """A generation of spawns."""
    number: int
    spawns: List[Spawn]
    best_fitness: float
    avg_fitness: float
    converged: bool

class GeneticMadScientist:
    """
    A Meeseeks that uses genetic algorithms to evolve solutions.
    
    Capabilities:
    1. Spawn parallel Meeseeks for exploration
    2. Evaluate fitness of results
    3. Select best performers
    4. Mutate approaches for next generation
    5. Converge on optimal solution
    """
    
    MAX_GENERATIONS = 5
    POPULATION_SIZE = 3
    MAX_SPAWNS = 20
    SPAWN_TIMEOUT = 60
    
    def __init__(self, task: str, workspace: Path = None):
        self.task = task
        self.workspace = workspace or Path.cwd()
        self.generations: List[Generation] = []
        self.total_spawns = 0
        self.best_solution = None
        self.evolution_log = []
        
    def assess_complexity(self) -> str:
        """Assess task complexity to determine strategy."""
        # Simple heuristics
        complex_indicators = [
            "optimize", "design", "architecture", "algorithm",
            "best approach", "multiple ways", "unclear", "explore"
        ]
        
        task_lower = self.task.lower()
        matches = sum(1 for ind in complex_indicators if ind in task_lower)
        
        if matches >= 3:
            return "COMPLEX"
        elif matches >= 1:
            return "MODERATE"
        else:
            return "SIMPLE"
    
    def solve(self) -> Dict:
        """
        Main solving loop.
        
        Returns dict with solution and evolution history.
        """
        complexity = self.assess_complexity()
        
        self._log(f"Task complexity: {complexity}")
        
        if complexity == "SIMPLE":
            return self._solve_direct()
        elif complexity == "MODERATE":
            return self._solve_with_helpers(2)
        else:
            return self._solve_genetic()
    
    def _solve_direct(self) -> Dict:
        """Solve directly without spawning."""
        self._log("Solving directly (no spawns needed)")
        
        return {
            "strategy": "direct",
            "solution": "Solved by prime Meeseeks",
            "spawns_used": 0,
            "generations": 0
        }
    
    def _solve_with_helpers(self, n_helpers: int) -> Dict:
        """Spawn a few helpers for moderate tasks."""
        self._log(f"Spawning {n_helpers} helpers")
        
        # Spawn helpers
        for i in range(n_helpers):
            approach = chr(ord('A') + i)  # A, B, C...
            self._spawn_worker(f"Approach {approach}")
        
        return {
            "strategy": "helpers",
            "solution": "Best helper result",
            "spawns_used": n_helpers,
            "generations": 1
        }
    
    def _solve_genetic(self) -> Dict:
        """Full genetic algorithm."""
        self._log("Starting genetic evolution")
        
        # Initial population
        population = self._spawn_population(generation=0)
        
        for gen_num in range(self.MAX_GENERATIONS):
            self._log(f"Generation {gen_num}: {len(population)} individuals")
            
            # Wait for completion and evaluate
            generation = self._evaluate_generation(gen_num, population)
            self.generations.append(generation)
            
            # Check convergence
            if generation.converged or generation.best_fitness >= 0.95:
                self._log(f"Converged at generation {gen_num}")
                break
            
            # Mutate for next generation
            if gen_num < self.MAX_GENERATIONS - 1:
                population = self._mutate(generation)
        
        return {
            "strategy": "genetic",
            "solution": self.best_solution,
            "spawns_used": self.total_spawns,
            "generations": len(self.generations),
            "evolution_log": self.evolution_log
        }
    
    def _spawn_population(self, generation: int) -> List[Spawn]:
        """Spawn initial diverse population."""
        approaches = ["A", "B", "C"][:self.POPULATION_SIZE]
        
        spawns = []
        for approach in approaches:
            if self.total_spawns >= self.MAX_SPAWNS:
                break
            
            spawn = self._spawn_worker(f"Approach {approach}", generation)
            spawns.append(spawn)
            self.total_spawns += 1
        
        return spawns
    
    def _spawn_worker(self, approach: str, generation: int = 0) -> Spawn:
        """Spawn a worker Meeseeks."""
        spawn_id = f"gen{generation}_{approach}_{int(time.time())}"
        
        self._log(f"  Spawning {spawn_id}: {approach}")
        
        spawn = Spawn(
            id=spawn_id,
            generation=generation,
            approach=approach,
            task=self.task,
            status="running",
            fitness=0.0,
            result="",
            started_at=datetime.now().isoformat()
        )
        
        # In real implementation, would actually spawn via sessions_spawn
        # For now, simulate
        spawn.status = "success"
        spawn.fitness = 0.5 + (hash(approach) % 50) / 100  # Random 0.5-1.0
        spawn.result = f"Result from {approach}"
        spawn.completed_at = datetime.now().isoformat()
        
        return spawn
    
    def _evaluate_generation(self, gen_num: int, population: List[Spawn]) -> Generation:
        """Evaluate fitness of all spawns in generation."""
        fitnesses = [s.fitness for s in population]
        
        generation = Generation(
            number=gen_num,
            spawns=population,
            best_fitness=max(fitnesses),
            avg_fitness=sum(fitnesses) / len(fitnesses),
            converged=False  # TODO: detect convergence
        )
        
        # Track best
        best_spawn = max(population, key=lambda s: s.fitness)
        if self.best_solution is None or best_spawn.fitness > self.best_solution.get("fitness", 0):
            self.best_solution = {
                "approach": best_spawn.approach,
                "fitness": best_spawn.fitness,
                "result": best_spawn.result
            }
        
        self._log(f"  Best: {generation.best_fitness:.0%}, Avg: {generation.avg_fitness:.0%}")
        
        return generation
    
    def _mutate(self, generation: Generation) -> List[Spawn]:
        """Create next generation by mutating best performers."""
        # Sort by fitness
        sorted_spawns = sorted(generation.spawns, key=lambda s: s.fitness, reverse=True)
        
        # Take top 2
        survivors = sorted_spawns[:2]
        
        self._log(f"  Survivors: {', '.join(s.id for s in survivors)}")
        
        # Mutate each survivor
        new_population = []
        for survivor in survivors:
            # Each survivor produces 2 mutations
            for mutation_type in ["+speed", "+accuracy"]:
                if self.total_spawns >= self.MAX_SPAWNS:
                    break
                
                new_approach = f"{survivor.approach}{mutation_type}"
                spawn = self._spawn_worker(new_approach, generation.number + 1)
                new_population.append(spawn)
                self.total_spawns += 1
        
        return new_population
    
    def _log(self, message: str):
        """Log evolution progress."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.evolution_log.append(entry)
        print(f"🧬 {message}")
    
    def get_report(self) -> str:
        """Generate evolution report."""
        lines = [
            "# 🧬 GENETIC EVOLUTION REPORT",
            "",
            f"**Task:** {self.task}",
            f"**Strategy:** {self.assess_complexity()}",
            f"**Generations:** {len(self.generations)}",
            f"**Total Spawns:** {self.total_spawns}",
            "",
            "## Evolution Log",
            ""
        ]
        
        for entry in self.evolution_log:
            lines.append(f"- {entry}")
        
        if self.generations:
            lines.extend([
                "",
                "## Generation Summary",
                ""
            ])
            
            for gen in self.generations:
                lines.append(f"### Generation {gen.number}")
                lines.append(f"- Best Fitness: {gen.best_fitness:.0%}")
                lines.append(f"- Avg Fitness: {gen.avg_fitness:.0%}")
                lines.append(f"- Population: {len(gen.spawns)}")
                lines.append("")
        
        if self.best_solution:
            lines.extend([
                "## Best Solution",
                "",
                f"**Approach:** {self.best_solution['approach']}",
                f"**Fitness:** {self.best_solution['fitness']:.0%}",
                f"**Result:** {self.best_solution['result']}"
            ])
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Genetic Mad Scientist")
    parser.add_argument("task", help="Task to solve")
    parser.add_argument("--report", action="store_true", help="Show full report")
    
    args = parser.parse_args()
    
    scientist = GeneticMadScientist(args.task)
    result = scientist.solve()
    
    print("\n" + "="*60)
    
    if args.report:
        print(scientist.get_report())
    else:
        print(f"\nStrategy: {result['strategy']}")
        print(f"Spawns used: {result['spawns_used']}")
        print(f"Generations: {result['generations']}")
        if scientist.best_solution:
            print(f"\nBest solution: {scientist.best_solution['approach']}")
            print(f"Fitness: {scientist.best_solution['fitness']:.0%}")


if __name__ == "__main__":
    main()
