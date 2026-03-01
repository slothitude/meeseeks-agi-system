#!/usr/bin/env python3
"""
MINI MEESEEKS WORKER POOL

Small context models (4096 tokens) for specific tasks in the genetic workflow:
- Task classification
- Fitness evaluation  
- Pattern spotting
- Crypt search
- Mutation generation
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OLLAMA_API = "http://localhost:11434/api"

@dataclass
class MiniMeeseeksResult:
    role: str
    output: Dict
    elapsed_ms: float
    tokens_used: int
    model: str


class MiniMeeseeksPool:
    """
    Pool of small-model workers for genetic workflow.
    
    Models: ministral-3 (4096 ctx), tinyllama (2048 ctx), phi3-mini
    """
    
    def __init__(self, model: str = "ministral-3"):
        self.model = model
        self.results_history = []
        
    def _generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response from Ollama."""
        try:
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            return f"ERROR: {e}"
        return "ERROR: No response"
    
    def classify_task(self, task: str) -> MiniMeeseeksResult:
        """Classify task complexity and category."""
        prompt = f"""# CLASSIFIER

You are a task classifier. Analyze tasks and route to appropriate handler.

## TASK
{task}

## OUTPUT FORMAT
```
COMPLEXITY: <simple|moderate|complex>
CATEGORY: <code|analysis|search|creative|data>
CONFIDENCE: <0-100%>
```"""
        
        start = datetime.now()
        response = self._generate(prompt, max_tokens=100)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        # Parse output
        result = {"raw": response}
        for line in response.split('\n'):
            if line.startswith('COMPLEXITY:'):
                result['complexity'] = line.split(':')[1].strip()
            elif line.startswith('CATEGORY:'):
                result['category'] = line.split(':')[1].strip()
            elif line.startswith('CONFIDENCE:'):
                result['confidence'] = line.split(':')[1].strip()
        
        return MiniMeeseeksResult(
            role="classifier",
            output=result,
            elapsed_ms=elapsed,
            tokens_used=len(prompt.split()) + len(response.split()),
            model=self.model
        )
    
    def evaluate_fitness(self, task: str, result: str, criteria: str = "") -> MiniMeeseeksResult:
        """Evaluate fitness of a spawn result."""
        prompt = f"""# FITNESS EVALUATOR

You evaluate spawn results. Score outcomes.

## TASK
{task}

## RESULT
{result}

## CRITERIA
{criteria if criteria else "Task completed successfully"}

## OUTPUT FORMAT
```
FITNESS: <0-100>
VERDICT: <pass|fail|partial>
ISSUES: <list of problems, if any>
```"""
        
        start = datetime.now()
        response = self._generate(prompt, max_tokens=150)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        # Parse output
        result = {"raw": response}
        for line in response.split('\n'):
            if line.startswith('FITNESS:'):
                result['fitness'] = line.split(':')[1].strip()
            elif line.startswith('VERDICT:'):
                result['verdict'] = line.split(':')[1].strip()
            elif line.startswith('ISSUES:'):
                result['issues'] = line.split(':')[1].strip()
        
        return MiniMeeseeksResult(
            role="fitness_evaluator",
            output=result,
            elapsed_ms=elapsed,
            tokens_used=len(prompt.split()) + len(response.split()),
            model=self.model
        )
    
    def spot_patterns(self, task: str, result: str) -> MiniMeeseeksResult:
        """Extract patterns from a result."""
        prompt = f"""# PATTERN SPOTTER

You extract patterns from results.

## TASK
{task}

## RESULT
{result}

## OUTPUT FORMAT
```
PATTERNS:
- <pattern 1>
- <pattern 2>
TRAITS:
- <trait 1>
- <trait 2>
```"""
        
        start = datetime.now()
        response = self._generate(prompt, max_tokens=200)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        # Parse output
        result = {"raw": response}
        patterns = []
        traits = []
        in_patterns = False
        in_traits = False
        
        for line in response.split('\n'):
            if 'PATTERNS:' in line:
                in_patterns = True
                in_traits = False
            elif 'TRAITS:' in line:
                in_traits = True
                in_patterns = False
            elif line.startswith('- ') and in_patterns:
                patterns.append(line[2:].strip())
            elif line.startswith('- ') and in_traits:
                traits.append(line[2:].strip())
        
        result['patterns'] = patterns
        result['traits'] = traits
        
        return MiniMeeseeksResult(
            role="pattern_spotter",
            output=result,
            elapsed_ms=elapsed,
            tokens_used=len(prompt.split()) + len(response.split()),
            model=self.model
        )
    
    def search_crypt(self, task: str, top_k: int = 3) -> MiniMeeseeksResult:
        """Search ancestor memory for similar tasks."""
        # Use Ultra Crypt for semantic search
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from ultra_crypt import UltraCrypt
            crypt = UltraCrypt()
            
            start = datetime.now()
            results = crypt.search(task, top_k=top_k)
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            # Format output
            ancestors = []
            for aid, sim, task_text, traits in results:
                ancestors.append({
                    "id": aid,
                    "similarity": f"{sim:.0%}",
                    "key_trait": traits[0] if traits else "none"
                })
            
            return MiniMeeseeksResult(
                role="crypt_searcher",
                output={
                    "ancestors": ancestors,
                    "count": len(ancestors)
                },
                elapsed_ms=elapsed,
                tokens_used=0,
                model="ultra_crypt"
            )
        except Exception as e:
            return MiniMeeseeksResult(
                role="crypt_searcher",
                output={"error": str(e)},
                elapsed_ms=0,
                tokens_used=0,
                model="error"
            )
    
    def generate_mutations(self, base_approach: str, count: int = 3) -> MiniMeeseeksResult:
        """Generate approach mutations."""
        prompt = f"""# MUTATION GENERATOR

You generate approach mutations.

## BASE APPROACH
{base_approach}

## OUTPUT FORMAT
Generate {count} mutations:
```
MUTATIONS:
1. <base>+<modifier> - <expected effect>
2. <base>+<modifier> - <expected effect>
3. <base>+<modifier> - <expected effect>
```"""
        
        start = datetime.now()
        response = self._generate(prompt, max_tokens=200)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        # Parse output
        result = {"raw": response, "mutations": []}
        
        for line in response.split('\n'):
            if line.strip() and line[0].isdigit() and '+' in line:
                # Parse "1. base+modifier - effect"
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    mutation = parts[0].split('.', 1)[-1].strip()
                    effect = parts[1].strip()
                    result["mutations"].append({
                        "mutation": mutation,
                        "effect": effect
                    })
        
        return MiniMeeseeksResult(
            role="mutation_generator",
            output=result,
            elapsed_ms=elapsed,
            tokens_used=len(prompt.split()) + len(response.split()),
            model=self.model
        )


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini Meeseeks Worker Pool")
    parser.add_argument("command", choices=["classify", "fitness", "patterns", "search", "mutate"])
    parser.add_argument("--task", help="Task to process")
    parser.add_argument("--result", help="Result to evaluate")
    parser.add_argument("--approach", help="Base approach to mutate")
    parser.add_argument("--model", default="ministral-3", help="Model to use")
    
    args = parser.parse_args()
    
    pool = MiniMeeseeksPool(model=args.model)
    
    if args.command == "classify" and args.task:
        result = pool.classify_task(args.task)
        print(json.dumps(result.output, indent=2))
    
    elif args.command == "fitness" and args.task and args.result:
        result = pool.evaluate_fitness(args.task, args.result)
        print(json.dumps(result.output, indent=2))
    
    elif args.command == "patterns" and args.task and args.result:
        result = pool.spot_patterns(args.task, args.result)
        print(json.dumps(result.output, indent=2))
    
    elif args.command == "search" and args.task:
        result = pool.search_crypt(args.task)
        print(json.dumps(result.output, indent=2))
    
    elif args.command == "mutate" and args.approach:
        result = pool.generate_mutations(args.approach)
        print(json.dumps(result.output, indent=2))
    
    else:
        print("Missing required arguments")
        parser.print_help()


if __name__ == "__main__":
    main()
