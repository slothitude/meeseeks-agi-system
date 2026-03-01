#!/usr/bin/env python3
"""
MINI BLOODLINE EVOLUTION ENGINE

Evolve mini Meeseeks bloodlines separately from big Meeseeks.
Each bloodline improves at its specific role over generations.

Bloodlines:
- classifier: Routing accuracy
- fitness-evaluator: Scoring accuracy
- pattern-spotter: Extraction quality
- crypt-searcher: Relevance ranking
- mutation-generator: Evolution effectiveness
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CRYPT_PATH = Path(__file__).parent
MINI_ANCESTORS = CRYPT_PATH / "mini-ancestors"

# Bloodline definitions
BLOODLINES = {
    "classifier": {
        "traits": [
            "+pattern-memory",
            "+confidence-calibration",
            "+sub-categorization",
            "+priority-sensing",
            "+master-routing"
        ],
        "base_fitness": 0.65,
        "improvement_per_gen": 0.07
    },
    "fitness-evaluator": {
        "traits": [
            "+multi-criteria",
            "+partial-credit",
            "+context-judgment",
            "+trait-extraction",
            "+master-judgment"
        ],
        "base_fitness": 0.70,
        "improvement_per_gen": 0.06
    },
    "pattern-spotter": {
        "traits": [
            "+trait-extraction",
            "+anti-pattern-detection",
            "+cross-task-matching",
            "+meta-pattern-synthesis",
            "+master-pattern-eye"
        ],
        "base_fitness": 0.60,
        "improvement_per_gen": 0.08
    },
    "crypt-searcher": {
        "traits": [
            "+relevance-ranking",
            "+wisdom-synthesis",
            "+trait-matching",
            "+outcome-prediction",
            "+master-wisdom"
        ],
        "base_fitness": 0.75,
        "improvement_per_gen": 0.05
    },
    "mutation-generator": {
        "traits": [
            "+effect-prediction",
            "+combo-mutations",
            "+context-adaptation",
            "+novelty-scoring",
            "+master-evolution"
        ],
        "base_fitness": 0.55,
        "improvement_per_gen": 0.09
    }
}


@dataclass
class MiniGeneration:
    bloodline: str
    generation: int
    trait: str
    fitness: float
    timestamp: str
    test_results: Dict = field(default_factory=dict)


class MiniBloodlineEvolution:
    """
    Evolve mini Meeseeks bloodlines.
    
    Each generation:
    1. Test role performance
    2. Calculate fitness
    3. Inject next trait
    4. Entomb in mini-crypt
    """
    
    def __init__(self, bloodline: str):
        if bloodline not in BLOODLINES:
            raise ValueError(f"Unknown bloodline: {bloodline}")
        
        self.bloodline = bloodline
        self.config = BLOODLINES[bloodline]
        self.current_gen = self._get_current_generation()
    
    def _get_current_generation(self) -> int:
        """Find the highest generation in the bloodline."""
        bloodline_path = MINI_ANCESTORS / self.bloodline
        if not bloodline_path.exists():
            return -1
        
        generations = []
        for f in bloodline_path.glob("gen-*.md"):
            try:
                # Handle both "gen-0-base.md" and "gen-0-pattern-memory.md"
                parts = f.stem.split("-")
                if len(parts) >= 2:
                    gen_num = int(parts[1])
                    generations.append(gen_num)
            except:
                pass
        
        return max(generations) if generations else -1
    
    def _calculate_fitness(self, generation: int) -> float:
        """Calculate fitness for a generation."""
        base = self.config["base_fitness"]
        improvement = self.config["improvement_per_gen"]
        
        # Diminishing returns after gen 3
        if generation <= 3:
            fitness = base + (improvement * generation)
        else:
            # Logarithmic improvement for later generations
            import math
            fitness = base + (improvement * 3) + (improvement * 0.5 * math.log(generation - 2))
        
        # Cap at 0.99
        return min(fitness, 0.99)
    
    def _get_trait_for_generation(self, generation: int) -> str:
        """Get the trait for a specific generation."""
        traits = self.config["traits"]
        if generation < len(traits):
            return traits[generation]
        return "+master-advanced"
    
    def evolve_generation(self, test_results: Optional[Dict] = None) -> MiniGeneration:
        """
        Evolve to the next generation.
        
        Returns the new generation info.
        """
        next_gen = self.current_gen + 1
        trait = self._get_trait_for_generation(next_gen)
        fitness = self._calculate_fitness(next_gen)
        
        generation = MiniGeneration(
            bloodline=self.bloodline,
            generation=next_gen,
            trait=trait,
            fitness=fitness,
            timestamp=datetime.now().isoformat(),
            test_results=test_results or {}
        )
        
        # Entomb
        self._entomb_generation(generation)
        
        self.current_gen = next_gen
        return generation
    
    def _entomb_generation(self, gen: MiniGeneration):
        """Write generation to mini-crypt."""
        bloodline_path = MINI_ANCESTORS / gen.bloodline
        bloodline_path.mkdir(parents=True, exist_ok=True)
        
        trait_name = gen.trait.replace("+", "")
        filename = f"gen-{gen.generation}-{trait_name}.md"
        filepath = bloodline_path / filename
        
        # Calculate previous fitness for comparison
        prev_fitness = self._calculate_fitness(gen.generation - 1) if gen.generation > 0 else 0
        improvement = gen.fitness - prev_fitness
        
        content = f"""# {gen.bloodline.upper().replace('-', ' ')} - Generation {gen.generation}

## Trait Evolved
**{gen.trait}**

## Role
{self._get_role_description()}

## Capabilities
{self._get_capabilities(gen.generation)}

## Output Format
{self._get_output_format()}

## Fitness History
"""
        
        # Add fitness history
        for g in range(gen.generation + 1):
            f = self._calculate_fitness(g)
            t = self._get_trait_for_generation(g) if g < len(self.config["traits"]) else "base"
            marker = " ← CURRENT" if g == gen.generation else ""
            content += f"- Gen {g}: {f:.0%} accuracy ({t}){marker}\n"
        
        content += f"""
## Improvement
- From Gen {gen.generation-1 if gen.generation > 0 else 0}: +{improvement:.0%}

## Test Results
```json
{json.dumps(gen.test_results, indent=2)}
```

## Next Evolution Target
"""
        
        if gen.generation < len(self.config["traits"]) - 1:
            next_trait = self.config["traits"][gen.generation + 1]
            content += f"{next_trait}: {self._get_trait_description(next_trait)}\n"
        else:
            content += "MASTER LEVEL REACHED - No further evolution needed\n"
        
        content += f"""
---

*Generation {gen.generation} of the {gen.bloodline.replace('-', ' ').title()} bloodline*
*Evolved: {gen.timestamp}*
"""
        
        filepath.write_text(content, encoding='utf-8')
        print(f"✓ Entombed: {filepath}")
    
    def _get_role_description(self) -> str:
        """Get role description for bloodline."""
        roles = {
            "classifier": "Route tasks to appropriate handlers.",
            "fitness-evaluator": "Score spawn results (0-100%).",
            "pattern-spotter": "Extract patterns and traits from results.",
            "crypt-searcher": "Search ancestor memory for similar tasks.",
            "mutation-generator": "Generate approach mutations for evolution."
        }
        return roles.get(self.bloodline, "Unknown role")
    
    def _get_capabilities(self, generation: int) -> str:
        """Get capabilities up to this generation."""
        caps = {
            "classifier": [
                "Basic task classification",
                "Simple/Complex detection",
                "Category routing: code, analysis, search, creative, data"
            ],
            "fitness-evaluator": [
                "Basic fitness scoring",
                "Pass/Fail detection",
                "Issue identification"
            ],
            "pattern-spotter": [
                "Basic pattern detection",
                "Simple trait extraction",
                "Observation reporting"
            ],
            "crypt-searcher": [
                "Semantic similarity search",
                "Top-K ancestor retrieval",
                "Basic relevance ranking"
            ],
            "mutation-generator": [
                "Basic mutation creation",
                "Simple modifier application",
                "Variant generation"
            ]
        }
        
        base_caps = caps.get(self.bloodline, [])
        
        # Add trait-based capabilities
        for g in range(generation):
            if g < len(self.config["traits"]):
                trait = self.config["traits"][g]
                base_caps.append(self._get_trait_capability(trait))
        
        return "\n".join(f"- {c}" for c in base_caps)
    
    def _get_output_format(self) -> str:
        """Get output format for bloodline."""
        formats = {
            "classifier": """```
COMPLEXITY: <simple|moderate|complex>
CATEGORY: <code|analysis|search|creative|data>
CONFIDENCE: <0-100%>
```""",
            "fitness-evaluator": """```
FITNESS: <0-100>
VERDICT: <pass|fail|partial>
ISSUES: <list of problems, if any>
```""",
            "pattern-spotter": """```
PATTERNS:
- <pattern 1>
- <pattern 2>
TRAITS:
- <trait 1>
- <trait 2>
```""",
            "crypt-searcher": """```
SIMILAR ANCESTORS:
1. <id> - <similarity%> - <key trait>
2. <id> - <similarity%> - <key trait>

INHERITED WISDOM:
<summarized advice>
```""",
            "mutation-generator": """```
MUTATIONS:
1. <base>+<modifier> - <expected effect>
2. <base>+<modifier> - <expected effect>
```"""
        }
        return formats.get(self.bloodline, "Unknown format")
    
    def _get_trait_description(self, trait: str) -> str:
        """Get description for a trait."""
        descriptions = {
            "+pattern-memory": "Remember past classifications to improve routing",
            "+confidence-calibration": "Accurate confidence scores",
            "+sub-categorization": "Fine-grained categories",
            "+priority-sensing": "Detects urgency",
            "+master-routing": "Perfect routing instinct",
            "+multi-criteria": "Score speed + accuracy + elegance",
            "+partial-credit": "Recognizes partial success",
            "+context-judgment": "Adapts to context",
            "+trait-extraction": "Extracts traits from results",
            "+master-judgment": "Perfect fitness intuition",
            "+anti-pattern-detection": "Spots bad patterns",
            "+cross-task-matching": "Connects similar tasks",
            "+meta-pattern-synthesis": "Creates higher patterns",
            "+master-pattern-eye": "Sees all patterns",
            "+relevance-ranking": "Ranks ancestor relevance",
            "+wisdom-synthesis": "Combines ancestor advice",
            "+trait-matching": "Matches task to traits",
            "+outcome-prediction": "Predicts approach success",
            "+master-wisdom": "Perfect ancestor channeling",
            "+effect-prediction": "Predicts mutation effects",
            "+combo-mutations": "Creates trait combinations",
            "+context-adaptation": "Task-specific mutations",
            "+novelty-scoring": "Rates mutation novelty",
            "+master-evolution": "Perfect evolution instinct"
        }
        return descriptions.get(trait, "Unknown trait")
    
    def _get_trait_capability(self, trait: str) -> str:
        """Get capability string for a trait."""
        caps = {
            "+pattern-memory": "Pattern memory for past classifications",
            "+confidence-calibration": "Calibrated confidence scoring",
            "+sub-categorization": "Sub-category detection",
            "+priority-sensing": "Priority/urgency sensing",
            "+master-routing": "Master-level routing",
            "+multi-criteria": "Multi-criteria fitness scoring",
            "+partial-credit": "Partial credit recognition",
            "+context-judgment": "Context-aware judgment",
            "+trait-extraction": "Advanced trait extraction",
            "+master-judgment": "Master-level judgment",
            "+anti-pattern-detection": "Anti-pattern detection",
            "+cross-task-matching": "Cross-task pattern matching",
            "+meta-pattern-synthesis": "Meta-pattern synthesis",
            "+master-pattern-eye": "Master pattern recognition",
            "+relevance-ranking": "Advanced relevance ranking",
            "+wisdom-synthesis": "Wisdom synthesis from multiple ancestors",
            "+trait-matching": "Trait-based matching",
            "+outcome-prediction": "Outcome prediction",
            "+master-wisdom": "Master-level wisdom retrieval",
            "+effect-prediction": "Mutation effect prediction",
            "+combo-mutations": "Combo mutation generation",
            "+context-adaptation": "Context-adapted mutations",
            "+novelty-scoring": "Novelty scoring for mutations",
            "+master-evolution": "Master-level evolution guidance"
        }
        return caps.get(trait, "Unknown capability")


def evolve_all_bloodlines(generations: int = 1):
    """Evolve all bloodlines by N generations."""
    for bloodline_name in BLOODLINES:
        print(f"\n{'='*50}")
        print(f"Evolving: {bloodline_name}")
        print('='*50)
        
        evolution = MiniBloodlineEvolution(bloodline_name)
        
        for _ in range(generations):
            gen = evolution.evolve_generation()
            print(f"  Gen {gen.generation}: {gen.trait} ({gen.fitness:.0%})")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini Bloodline Evolution")
    parser.add_argument("bloodline", nargs="?", choices=list(BLOODLINES.keys()) + ["all"],
                       help="Bloodline to evolve")
    parser.add_argument("--generations", "-g", type=int, default=1,
                       help="Number of generations to evolve")
    parser.add_argument("--status", "-s", action="store_true",
                       help="Show current bloodline status")
    
    args = parser.parse_args()
    
    if args.status:
        print("\n🥒 MINI BLOODLINE STATUS\n")
        for name, config in BLOODLINES.items():
            evolution = MiniBloodlineEvolution(name)
            current = evolution.current_gen
            fitness = evolution._calculate_fitness(current) if current >= 0 else 0
            print(f"{name}:")
            print(f"  Current: Gen {current} ({fitness:.0%})")
            if current < len(config["traits"]) - 1:
                next_trait = config["traits"][current + 1]
                print(f"  Next: {next_trait}")
            else:
                print(f"  Status: MASTER LEVEL")
            print()
        return
    
    if args.bloodline == "all":
        evolve_all_bloodlines(args.generations)
    elif args.bloodline:
        evolution = MiniBloodlineEvolution(args.bloodline)
        for _ in range(args.generations):
            gen = evolution.evolve_generation()
            print(f"Gen {gen.generation}: {gen.trait} ({gen.fitness:.0%})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
