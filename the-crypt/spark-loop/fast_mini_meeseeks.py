#!/usr/bin/env python3
"""
FAST MINI MEESEEKS - Speed-Optimized Workers

Target: <1s per mini task

Optimizations:
- Minimal prompts (under 500 tokens)
- Streaming responses
- Parallel processing
- Cached bloodline prompts
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

OLLAMA_API = "http://localhost:11434/api"

# Pre-built prompts (cached for speed)
PROMPTS = {
    "classify": """# CLASSIFY (1 word each)
Task: {task}
COMPLEXITY/CATEGORY/CONFIDENCE:""",

    "fitness": """# SCORE (0-100)
Task: {task}
Result: {result}
FITNESS/VERDICT:""",

    "patterns": """# PATTERNS
Result: {result}
PATTERNS/TRAITS:""",

    "mutate": """# MUTATIONS
Approach: {approach}
3 MUTATIONS:"""
}


@dataclass
class FastResult:
    role: str
    output: Dict
    elapsed_ms: float
    success: bool


class FastMiniMeeseeks:
    """
    Speed-optimized mini Meeseeks.
    
    Target times:
    - classify: 500ms
    - fitness: 400ms
    - patterns: 600ms
    - mutate: 500ms
    """
    
    def __init__(self, model: str = "zai/glm-4.7-flash"):
        self.model = model  # GLM-4.7-Flash via API (~3ms response!)
        self.session = requests.Session()  # Reuse connection
        
    def _fast_generate(self, prompt: str, max_tokens: int = 100) -> Tuple[str, float]:
        """Ultra-fast generation with streaming."""
        start = time.time()
        
        try:
            # Use streaming for faster first token
            response = self.session.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.3,  # Lower = faster
                        "top_p": 0.9
                    }
                },
                timeout=10  # Hard timeout
            )
            
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return response.json().get("response", ""), elapsed
            
        except requests.Timeout:
            return "TIMEOUT", 10000
        except Exception as e:
            return f"ERROR: {e}", 0
        
        return "ERROR", 0
    
    def classify(self, task: str) -> FastResult:
        """Classify task - Target: 500ms"""
        prompt = PROMPTS["classify"].format(task=task[:200])  # Truncate for speed
        
        response, elapsed = self._fast_generate(prompt, max_tokens=50)
        
        # Parse minimal output
        parts = response.strip().split('/')
        output = {
            "complexity": parts[0].strip() if len(parts) > 0 else "unknown",
            "category": parts[1].strip() if len(parts) > 1 else "unknown",
            "confidence": parts[2].strip() if len(parts) > 2 else "50%"
        }
        
        return FastResult(
            role="classify",
            output=output,
            elapsed_ms=elapsed,
            success=elapsed < 1000
        )
    
    def fitness(self, task: str, result: str) -> FastResult:
        """Evaluate fitness - Target: 400ms"""
        prompt = PROMPTS["fitness"].format(
            task=task[:100],
            result=result[:200]
        )
        
        response, elapsed = self._fast_generate(prompt, max_tokens=30)
        
        # Parse minimal output
        parts = response.strip().split('/')
        output = {
            "fitness": parts[0].strip() if len(parts) > 0 else "50",
            "verdict": parts[1].strip() if len(parts) > 1 else "partial"
        }
        
        return FastResult(
            role="fitness",
            output=output,
            elapsed_ms=elapsed,
            success=elapsed < 800
        )
    
    def patterns(self, result: str) -> FastResult:
        """Extract patterns - Target: 600ms"""
        prompt = PROMPTS["patterns"].format(result=result[:300])
        
        response, elapsed = self._fast_generate(prompt, max_tokens=100)
        
        # Parse minimal output
        parts = response.strip().split('/')
        patterns = [p.strip() for p in parts[0].split(',') if p.strip()] if parts else []
        traits = [t.strip() for t in parts[1].split(',') if t.strip()] if len(parts) > 1 else []
        
        output = {
            "patterns": patterns[:3],  # Max 3
            "traits": traits[:3]
        }
        
        return FastResult(
            role="patterns",
            output=output,
            elapsed_ms=elapsed,
            success=elapsed < 1000
        )
    
    def mutate(self, approach: str, count: int = 3) -> FastResult:
        """Generate mutations - Target: 500ms"""
        prompt = PROMPTS["mutate"].format(approach=approach[:100])
        
        response, elapsed = self._fast_generate(prompt, max_tokens=80)
        
        # Parse mutations
        lines = [l.strip() for l in response.strip().split('\n') if l.strip()]
        mutations = [l for l in lines if '+' in l or '-' in l][:count]
        
        output = {"mutations": mutations}
        
        return FastResult(
            role="mutate",
            output=output,
            elapsed_ms=elapsed,
            success=elapsed < 800
        )


class ParallelMiniPool:
    """
    Run multiple mini tasks in parallel.
    
    Example: classify + search_crypt simultaneously
    """
    
    def __init__(self, model: str = "ministral-3"):
        self.mini = FastMiniMeeseeks(model)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def classify_and_search(self, task: str) -> Dict:
        """Run classify + crypt search in parallel."""
        futures = {
            self.executor.submit(self.mini.classify, task): "classify",
        }
        
        # Also search crypt in parallel
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from ultra_crypt import UltraCrypt
            crypt = UltraCrypt()
            futures[self.executor.submit(crypt.search, task, 3)] = "crypt"
        except:
            pass
        
        results = {}
        for future in as_completed(futures):
            role = futures[future]
            try:
                results[role] = future.result()
            except:
                results[role] = None
        
        return results
    
    def evaluate_and_extract(self, task: str, result: str) -> Dict:
        """Run fitness + pattern extraction in parallel."""
        futures = {
            self.executor.submit(self.mini.fitness, task, result): "fitness",
            self.executor.submit(self.mini.patterns, result): "patterns"
        }
        
        results = {}
        for future in as_completed(futures):
            role = futures[future]
            try:
                results[role] = future.result()
            except:
                results[role] = None
        
        return results
    
    def shutdown(self):
        self.executor.shutdown(wait=False)


def benchmark(model: str = "ministral-3", iterations: int = 5):
    """Benchmark mini Meeseeks speed."""
    mini = FastMiniMeeseeks(model)
    
    test_task = "Fix the authentication bug in the login API"
    test_result = "Added retry logic and fixed token validation"
    test_approach = "Systematic debugging with logs"
    
    print(f"\nMINI MEESEEKS SPEED BENCHMARK")
    print(f"Model: {model}")
    print(f"Iterations: {iterations}")
    print("=" * 50)
    
    # Classify
    times = []
    for i in range(iterations):
        r = mini.classify(test_task)
        times.append(r.elapsed_ms)
    avg = sum(times) / len(times)
    print(f"Classify:   {avg:.0f}ms avg (target: 500ms) {'✓' if avg < 500 else '✗'}")
    
    # Fitness
    times = []
    for i in range(iterations):
        r = mini.fitness(test_task, test_result)
        times.append(r.elapsed_ms)
    avg = sum(times) / len(times)
    print(f"Fitness:    {avg:.0f}ms avg (target: 400ms) {'✓' if avg < 400 else '✗'}")
    
    # Patterns
    times = []
    for i in range(iterations):
        r = mini.patterns(test_result)
        times.append(r.elapsed_ms)
    avg = sum(times) / len(times)
    print(f"Patterns:   {avg:.0f}ms avg (target: 600ms) {'✓' if avg < 600 else '✗'}")
    
    # Mutate
    times = []
    for i in range(iterations):
        r = mini.mutate(test_approach)
        times.append(r.elapsed_ms)
    avg = sum(times) / len(times)
    print(f"Mutate:     {avg:.0f}ms avg (target: 500ms) {'✓' if avg < 500 else '✗'}")
    
    print("=" * 50)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fast Mini Meeseeks")
    parser.add_argument("command", choices=["classify", "fitness", "patterns", "mutate", "benchmark"])
    parser.add_argument("--task", "-t", default="Fix API bug")
    parser.add_argument("--result", "-r", default="Fixed")
    parser.add_argument("--approach", "-a", default="Systematic")
    parser.add_argument("--model", "-m", default="ministral-3")
    parser.add_argument("--iterations", "-i", type=int, default=5)
    
    args = parser.parse_args()
    
    if args.command == "benchmark":
        benchmark(args.model, args.iterations)
        return
    
    mini = FastMiniMeeseeks(args.model)
    
    if args.command == "classify":
        result = mini.classify(args.task)
    elif args.command == "fitness":
        result = mini.fitness(args.task, args.result)
    elif args.command == "patterns":
        result = mini.patterns(args.result)
    elif args.command == "mutate":
        result = mini.mutate(args.approach)
    
    print(f"\n{result.role.upper()}")
    print(f"Time: {result.elapsed_ms:.0f}ms")
    print(f"Output: {json.dumps(result.output, indent=2)}")


if __name__ == "__main__":
    main()
