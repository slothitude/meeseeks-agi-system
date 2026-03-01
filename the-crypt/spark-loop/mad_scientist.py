#!/usr/bin/env python3
"""
GENETIC MAD SCIENTIST - Meeseeks that spawns Meeseeks

Enables rapid learning through parallel evolution.

Usage:
    python mad_scientist.py "optimize the API for speed" --report
"""

import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
import subprocess
import threading
import queue

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "meeseeks"))

# Constants
MAX_GENERATIONS = 5
POPULATION_SIZE = 3
MAX_SPAWNS = 20
SPAWN_TIMEOUT = 60


@dataclass
class Spawn:
    """A spawned Meeseeks."""
    id: str
    generation: int
    approach: str
    mutation: str
    task: str
    status: str = "pending"  # pending, running, success, failed, timeout
    fitness: float = 0.0
    result: str = ""
    error: str = ""
    started_at: str = ""
    completed_at: str = ""
    tokens_used: int = 0
    duration_ms: int = 0


@dataclass
class Generation:
    """A generation of spawns."""
    number: int
    spawns: List[Spawn]
    best_fitness: float = 0.0
    avg_fitness: float = 0.0
    converged: bool = False
    stagnation: bool = False


class GeneticMadScientist:
    """
    A Meeseeks that uses genetic algorithms to evolve solutions.
    
    Evolution Process:
    1. Assess task complexity
    2. Spawn diverse initial population
    3. Evaluate fitness of each spawn
    4. Select best performers
    5. Mutate for next generation
    6. Repeat until convergence
    """
    
    def __init__(self, task: str, workspace: Path = None):
        self.task = task
        self.workspace = workspace or Path.cwd()
        self.generations: List[Generation] = []
        self.total_spawns = 0
        self.best_solution: Optional[Dict] = None
        self.evolution_log: List[str] = []
        self.spawn_queue: queue.Queue = queue.Queue()
        self.results_queue: queue.Queue = queue.Queue()
        
    def assess_complexity(self) -> str:
        """Assess task complexity."""
        complex_indicators = [
            "optimize", "design", "architecture", "algorithm",
            "best approach", "multiple ways", "unclear", "explore",
            "figure out", "decide", "compare", "versus", "vs"
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
        """Main solving loop."""
        complexity = self.assess_complexity()
        self._log(f"Task: {self.task[:50]}...")
        self._log(f"Complexity: {complexity}")
        
        start_time = time.time()
        
        if complexity == "SIMPLE":
            result = self._solve_direct()
        elif complexity == "MODERATE":
            result = self._solve_with_helpers(2)
        else:
            result = self._solve_genetic()
        
        elapsed = time.time() - start_time
        
        return {
            **result,
            "elapsed_seconds": elapsed,
            "evolution_log": self.evolution_log
        }
    
    def _solve_direct(self) -> Dict:
        """Solve directly."""
        self._log("Strategy: Direct solve (no spawns)")
        
        return {
            "strategy": "direct",
            "solution": None,  # Would be filled by actual solve
            "spawns_used": 0,
            "generations": 0,
            "best_fitness": 0.0
        }
    
    def _solve_with_helpers(self, n_helpers: int) -> Dict:
        """Spawn helpers."""
        self._log(f"Strategy: {n_helpers} helpers")
        
        population = []
        for i in range(n_helpers):
            approach = chr(ord('A') + i)
            spawn = self._spawn_worker(approach, 0, "")
            population.append(spawn)
        
        generation = self._evaluate_generation(0, population)
        self.generations.append(generation)
        
        return {
            "strategy": "helpers",
            "solution": self.best_solution,
            "spawns_used": self.total_spawns,
            "generations": 1,
            "best_fitness": generation.best_fitness
        }
    
    def _solve_genetic(self) -> Dict:
        """Full genetic algorithm."""
        self._log("Strategy: Genetic evolution")
        
        # Initial population with diverse approaches
        initial_approaches = [
            ("A", "systematic", "Step-by-step methodical approach"),
            ("B", "creative", "Novel unconventional approach"),
            ("C", "hybrid", "Combine best of multiple methods")
        ]
        
        population = []
        for approach_id, approach_name, approach_desc in initial_approaches[:POPULATION_SIZE]:
            if self.total_spawns >= MAX_SPAWNS:
                break
            spawn = self._spawn_worker(approach_id, 0, "", approach_desc)
            population.append(spawn)
        
        prev_best = 0.0
        stagnation_count = 0
        
        for gen_num in range(MAX_GENERATIONS):
            self._log(f"Generation {gen_num}: {len(population)} individuals")
            
            # Evaluate
            generation = self._evaluate_generation(gen_num, population)
            self.generations.append(generation)
            
            # Check termination conditions
            if generation.best_fitness >= 0.95:
                self._log(f"CONVERGED: Solution found ({generation.best_fitness:.0%})")
                generation.converged = True
                break
            
            if generation.best_fitness <= prev_best:
                stagnation_count += 1
                if stagnation_count >= 3:
                    self._log("STAGNATION: No improvement for 3 generations")
                    generation.stagnation = True
                    break
            else:
                stagnation_count = 0
            
            prev_best = generation.best_fitness
            
            # Mutate for next generation
            if gen_num < MAX_GENERATIONS - 1 and self.total_spawns < MAX_SPAWNS:
                population = self._mutate(generation)
        
        return {
            "strategy": "genetic",
            "solution": self.best_solution,
            "spawns_used": self.total_spawns,
            "generations": len(self.generations),
            "best_fitness": self.generations[-1].best_fitness if self.generations else 0.0
        }
    
    def _spawn_worker(self, approach_id: str, generation: int, parent_approach: str, 
                      approach_desc: str = "") -> Spawn:
        """Spawn a worker Meeseeks."""
        spawn_id = f"gen{generation}_{approach_id}"
        
        if parent_approach:
            full_approach = f"{parent_approach}{approach_id}"
        else:
            full_approach = approach_id
        
        self._log(f"  Spawn {spawn_id}: {approach_desc or full_approach}")
        
        spawn = Spawn(
            id=spawn_id,
            generation=generation,
            approach=full_approach,
            mutation=approach_id,
            task=self.task,
            status="running",
            started_at=datetime.now().isoformat()
        )
        
        self.total_spawns += 1
        
        # Simulate spawn work (in real impl, would use sessions_spawn)
        # For simulation, generate varied fitness based on approach
        base_fitness = 0.5
        approach_bonus = {
            "A": 0.15,
            "B": 0.10,
            "C": 0.20,
            "+speed": -0.05,
            "+accuracy": 0.10,
            "+creative": 0.05,
            "+safe": 0.08
        }
        
        for key, bonus in approach_bonus.items():
            if key in full_approach:
                base_fitness += bonus
        
        # Add some randomness
        import random
        base_fitness += random.uniform(-0.1, 0.1)
        base_fitness = max(0.0, min(1.0, base_fitness))
        
        spawn.status = "success"
        spawn.fitness = base_fitness
        spawn.result = f"Result from approach {full_approach}"
        spawn.completed_at = datetime.now().isoformat()
        spawn.duration_ms = int(random.uniform(1000, 5000))
        
        return spawn
    
    def _evaluate_generation(self, gen_num: int, population: List[Spawn]) -> Generation:
        """Evaluate all spawns in generation."""
        fitnesses = [s.fitness for s in population if s.status == "success"]
        
        if not fitnesses:
            return Generation(
                number=gen_num,
                spawns=population,
                best_fitness=0.0,
                avg_fitness=0.0
            )
        
        generation = Generation(
            number=gen_num,
            spawns=population,
            best_fitness=max(fitnesses),
            avg_fitness=sum(fitnesses) / len(fitnesses)
        )
        
        # Track best
        best_spawn = max(population, key=lambda s: s.fitness)
        if self.best_solution is None or best_spawn.fitness > self.best_solution.get("fitness", 0):
            self.best_solution = {
                "approach": best_spawn.approach,
                "fitness": best_spawn.fitness,
                "result": best_spawn.result,
                "generation": gen_num,
                "spawn_id": best_spawn.id
            }
        
        # Log results
        for spawn in population:
            status_icon = "OK" if spawn.status == "success" else "XX"
            self._log(f"    [{status_icon}] {spawn.id}: {spawn.fitness:.0%}")
        
        self._log(f"  Best: {generation.best_fitness:.0%}, Avg: {generation.avg_fitness:.0%}")
        
        return generation
    
    def _mutate(self, generation: Generation) -> List[Spawn]:
        """Create next generation by mutating best performers."""
        # Sort by fitness
        sorted_spawns = sorted(
            [s for s in generation.spawns if s.status == "success"],
            key=lambda s: s.fitness,
            reverse=True
        )
        
        if not sorted_spawns:
            return []
        
        # Take top performers
        survivors = sorted_spawns[:2]
        
        self._log(f"  Survivors: {', '.join(s.id for s in survivors)}")
        
        # Mutation types
        mutations = [
            ("+speed", "Optimize for speed"),
            ("+accuracy", "Improve accuracy"),
            ("+creative", "Try creative variation"),
            ("+safe", "Add safety checks")
        ]
        
        # Create new population
        new_population = []
        next_gen = generation.number + 1
        
        for survivor in survivors:
            # Each survivor produces 2 mutations
            for mutation_id, mutation_desc in mutations[:2]:
                if self.total_spawns >= MAX_SPAWNS:
                    break
                
                spawn = self._spawn_worker(
                    mutation_id,
                    next_gen,
                    survivor.approach,
                    f"{survivor.approach} + {mutation_desc}"
                )
                new_population.append(spawn)
        
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
            f"**Total Spawns:** {self.total_spawns}",
            f"**Generations:** {len(self.generations)}",
            ""
        ]
        
        # Generation summary
        if self.generations:
            lines.append("## Generation Summary")
            lines.append("")
            lines.append("| Gen | Population | Best | Avg | Status |")
            lines.append("|-----|------------|------|-----|--------|")
            
            for gen in self.generations:
                status = "converged" if gen.converged else ("stagnated" if gen.stagnation else "evolving")
                lines.append(f"| {gen.number} | {len(gen.spawns)} | {gen.best_fitness:.0%} | {gen.avg_fitness:.0%} | {status} |")
            
            lines.append("")
        
        # Best solution
        if self.best_solution:
            lines.extend([
                "## Best Solution",
                "",
                f"**Approach:** `{self.best_solution['approach']}`",
                f"**Fitness:** {self.best_solution['fitness']:.0%}",
                f"**Generation:** {self.best_solution['generation']}",
                f"**Spawn ID:** {self.best_solution['spawn_id']}",
                "",
                f"**Result:**",
                f"```",
                self.best_solution['result'],
                f"```",
                ""
            ])
        
        # Evolution log
        lines.extend([
            "## Evolution Log",
            "",
            "```"
        ])
        lines.extend(self.evolution_log)
        lines.append("```")
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Genetic Mad Scientist - Evolve Solutions")
    parser.add_argument("task", help="Task to solve")
    parser.add_argument("--report", action="store_true", help="Show full report")
    parser.add_argument("--max-generations", type=int, default=MAX_GENERATIONS, help="Max generations")
    parser.add_argument("--population-size", type=int, default=POPULATION_SIZE, help="Population size")
    
    args = parser.parse_args()
    
    scientist = GeneticMadScientist(args.task)
    scientist.MAX_GENERATIONS = args.max_generations
    scientist.POPULATION_SIZE = args.population_size
    
    result = scientist.solve()
    
    print("\n" + "=" * 60)
    
    if args.report:
        print(scientist.get_report())
    else:
        print(f"\nStrategy: {result['strategy']}")
        print(f"Spawns used: {result['spawns_used']}")
        print(f"Generations: {result['generations']}")
        print(f"Best fitness: {result.get('best_fitness', 0):.0%}")
        print(f"Elapsed: {result.get('elapsed_seconds', 0):.1f}s")
        
        if scientist.best_solution:
            print(f"\nBest approach: {scientist.best_solution['approach']}")


if __name__ == "__main__":
    main()
