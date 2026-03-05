#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Improve — The System Improves Its Own Code

This module enables the Meeseeks system to analyze itself, propose improvements,
and track the impact of changes over time. This is recursive self-improvement.

Usage:
    python skills/meeseeks/self_improve.py --analyze    # Find improvements
    python skills/meeseeks/self_improve.py --propose    # Generate proposal
    python skills/meeseeks/self_improve.py --test       # Run self-test
    python skills/meeseeks/self_improve.py --history    # Show improvement history
"""

import sys
import io
import os
import json
import argparse
import re
import ast
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter, defaultdict
import statistics

# Fix Windows encoding for unicode output
# NOTE: We avoid rewrapping stdout/stderr as it causes "I/O operation on closed file" errors
# when the old wrapper gets garbage collected and closes the underlying buffer.
# Instead, we rely on PYTHONIOENCODING environment variable or handle encoding errors inline.

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SCRIPT_DIR = Path(__file__).parent
META_DIR = WORKSPACE / "the-crypt" / "meta"
MEESEEKS_DIR = SCRIPT_DIR
IMPROVEMENTS_PATH = META_DIR / "self_improvements.jsonl"
TEST_RESULTS_PATH = META_DIR / "self_test_results.jsonl"


def ensure_meta_dir():
    """Ensure the meta directory exists."""
    META_DIR.mkdir(parents=True, exist_ok=True)


def analyze_own_code() -> Dict:
    """
    Read the meeseeks system files and find improvements.
    
    Returns:
        Dict with analysis of patterns, redundancies, and improvement opportunities
    """
    analysis = {
        "files_analyzed": 0,
        "total_lines": 0,
        "patterns": {
            "redundancies": [],
            "inefficiencies": [],
            "missing_features": [],
            "good_patterns": []
        },
        "code_metrics": {},
        "improvement_opportunities": []
    }
    
    # Get all Python files in meeseeks directory
    py_files = list(MEESEEKS_DIR.glob("*.py"))
    
    # Analyze each file
    file_contents = {}
    function_definitions = defaultdict(list)
    import_usage = Counter()
    class_definitions = defaultdict(list)
    
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding='utf-8')
            file_contents[py_file.name] = content
            analysis["files_analyzed"] += 1
            analysis["total_lines"] += len(content.split('\n'))
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_definitions[node.name].append(py_file.name)
                    elif isinstance(node, ast.ClassDef):
                        class_definitions[node.name].append(py_file.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            import_usage[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_usage[node.module] += 1
            except SyntaxError:
                pass
            
            # Pattern detection
            
            # 1. Check for duplicate load_* functions
            load_pattern = re.findall(r'def (load_\w+)\(', content)
            for func in load_pattern:
                if func in ['load_config', 'load_dharma', 'load_history']:
                    # These are expected
                    pass
            
            # 2. Check for TODO/FIXME comments
            todos = re.findall(r'#\s*(TODO|FIXME|HACK|XXX):?\s*(.+)', content, re.IGNORECASE)
            for todo_type, todo_text in todos:
                analysis["improvement_opportunities"].append({
                    "type": "todo",
                    "subtype": todo_type.lower(),
                    "file": py_file.name,
                    "text": todo_text.strip()[:100],
                    "priority": "high" if todo_type.lower() in ["fixme", "xxx"] else "medium"
                })
            
            # 3. Check for repeated patterns (potential abstraction)
            # Look for repeated API call patterns
            api_calls = re.findall(r'urllib\.request\.(urlopen|Request)', content)
            if len(api_calls) > 2:
                analysis["patterns"]["redundancies"].append({
                    "type": "api_call_pattern",
                    "file": py_file.name,
                    "count": len(api_calls),
                    "suggestion": "Consider centralizing API calls in a helper module"
                })
            
            # 4. Check for hardcoded paths
            hardcoded_paths = re.findall(r'["\']([A-Z]:\\[^"\']+)["\']', content)
            if hardcoded_paths:
                analysis["patterns"]["inefficiencies"].append({
                    "type": "hardcoded_path",
                    "file": py_file.name,
                    "count": len(hardcoded_paths),
                    "suggestion": "Use config file or environment variables for paths"
                })
            
            # 5. Check for good patterns (positive findings)
            if 'async def' in content and 'await' in content:
                analysis["patterns"]["good_patterns"].append({
                    "type": "async_pattern",
                    "file": py_file.name,
                    "note": "Uses async/await correctly"
                })
            
            if 'logging' in content or 'logger' in content:
                analysis["patterns"]["good_patterns"].append({
                    "type": "logging",
                    "file": py_file.name,
                    "note": "Uses logging instead of print"
                })
            
            # 6. Check for missing error handling
            try_blocks = len(re.findall(r'\btry\s*:', content))
            except_blocks = len(re.findall(r'\bexcept\s*', content))
            function_defs = len(re.findall(r'\bdef\s+\w+\s*\(', content))
            
            if function_defs > 5 and try_blocks == 0:
                analysis["patterns"]["inefficiencies"].append({
                    "type": "missing_error_handling",
                    "file": py_file.name,
                    "suggestion": "Add try/except blocks for robust error handling"
                })
            
        except Exception as e:
            analysis["improvement_opportunities"].append({
                "type": "error",
                "file": py_file.name,
                "text": f"Failed to analyze: {str(e)}",
                "priority": "low"
            })
    
    # Cross-file analysis
    
    # 1. Find duplicate function definitions across files
    for func_name, files in function_definitions.items():
        if len(files) > 1 and not func_name.startswith('_'):
            # Common utility functions that are OK to duplicate
            if func_name not in ['main', 'load_config', 'get_api_key', 'ensure_dir']:
                analysis["patterns"]["redundancies"].append({
                    "type": "duplicate_function",
                    "function": func_name,
                    "files": files,
                    "suggestion": f"Consider moving {func_name} to a shared utility module"
                })
    
    # 2. Find duplicate class definitions
    for class_name, files in class_definitions.items():
        if len(files) > 1:
            analysis["patterns"]["redundancies"].append({
                "type": "duplicate_class",
                "class": class_name,
                "files": files,
                "suggestion": f"Consider consolidating {class_name} definition"
            })
    
    # 3. Check for missing features based on file structure
    expected_files = [
        "test_auto_retry.py",  # Testing
        "karma_observer.py",   # Monitoring
        "genealogy.py",        # Ancestry
    ]
    
    existing_names = [f.name for f in py_files]
    
    if "shared_state.py" not in existing_names:
        analysis["patterns"]["missing_features"].append({
            "type": "missing_module",
            "suggestion": "shared_state.py - Centralized state management for swarms",
            "priority": "high"
        })
    
    if "api_client.py" not in existing_names:
        analysis["patterns"]["missing_features"].append({
            "type": "missing_module",
            "suggestion": "api_client.py - Centralized API client with retry logic",
            "priority": "medium"
        })
    
    # Code metrics
    analysis["code_metrics"] = {
        "total_files": len(py_files),
        "total_functions": sum(len(v) for v in function_definitions.values()),
        "total_classes": sum(len(v) for v in class_definitions.values()),
        "unique_imports": len(import_usage),
        "most_used_imports": import_usage.most_common(5),
        "function_duplication_rate": len([f for f, files in function_definitions.items() if len(files) > 1]) / max(1, len(function_definitions))
    }
    
    return analysis


def propose_improvement() -> Dict:
    """
    Generate a concrete improvement proposal.
    
    Returns:
        Dict with improvement details
    """
    analysis = analyze_own_code()
    
    # Prioritize improvements
    proposals = []
    
    # 1. Check for high-priority TODOs/FIXMEs
    for opp in analysis.get("improvement_opportunities", []):
        if opp.get("type") == "todo" and opp.get("priority") == "high":
            proposals.append({
                "type": "bugfix",
                "target_file": opp.get("file", "unknown"),
                "description": f"Address {opp.get('subtype', 'issue')}: {opp.get('text', '')}",
                "rationale": "High-priority issue identified in code comments",
                "expected_impact": "Improved stability and correctness",
                "priority": 1
            })
    
    # 2. Check for redundancies that could be consolidated
    for red in analysis.get("patterns", {}).get("redundancies", []):
        if red.get("type") == "duplicate_function":
            proposals.append({
                "type": "refactor",
                "target_file": "skills/meeseeks/utils.py",
                "description": f"Create shared utility module and move {red.get('function', 'function')} from {', '.join(red.get('files', []))}",
                "rationale": f"Function duplicated in {len(red.get('files', []))} files",
                "expected_impact": "Reduced code duplication, easier maintenance",
                "priority": 2
            })
    
    # 3. Check for missing features
    for feat in analysis.get("patterns", {}).get("missing_features", []):
        if feat.get("type") == "missing_module":
            proposals.append({
                "type": "new_feature",
                "target_file": f"skills/meeseeks/{feat.get('suggestion', '').split(' - ')[0]}",
                "description": feat.get("suggestion", "Add missing module"),
                "rationale": feat.get("suggestion", ""),
                "expected_impact": "Improved code organization and reusability",
                "priority": 3 if feat.get("priority") == "high" else 4
            })
    
    # 4. Check for inefficiencies
    for ineff in analysis.get("patterns", {}).get("inefficiencies", []):
        if ineff.get("type") == "hardcoded_path":
            proposals.append({
                "type": "refactor",
                "target_file": ineff.get("file", "unknown"),
                "description": f"Replace {ineff.get('count', 0)} hardcoded paths with config",
                "rationale": "Hardcoded paths reduce portability",
                "expected_impact": "Improved portability and configuration flexibility",
                "priority": 3
            })
    
    # Sort by priority
    proposals.sort(key=lambda x: x.get("priority", 5))
    
    # Return top proposal or a summary
    if proposals:
        best = proposals[0]
        best["all_proposals_count"] = len(proposals)
        best["analysis_summary"] = {
            "files_analyzed": analysis.get("files_analyzed", 0),
            "redundancies_found": len(analysis.get("patterns", {}).get("redundancies", [])),
            "missing_features": len(analysis.get("patterns", {}).get("missing_features", []))
        }
        return best
    else:
        return {
            "type": "none",
            "description": "No improvements needed at this time",
            "rationale": "Code analysis found no critical issues",
            "expected_impact": "System is healthy",
            "priority": 0
        }


def self_test() -> Dict:
    """
    Run the full system through a test and measure improvement.
    
    Returns:
        Dict with test results
    """
    ensure_meta_dir()
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "metrics": {},
        "comparison": {}
    }
    
    # Test 1: Can we import core modules?
    core_modules = [
        "spawn_meeseeks",
        "brahman_dream",
        "entomb_meeseeks",
        "inherit_wisdom",
        "karma_observer"
    ]
    
    import_success = 0
    import_failures = []
    
    for module in core_modules:
        try:
            # Just check if the file exists and is valid Python
            module_path = MEESEEKS_DIR / f"{module}.py"
            if module_path.exists():
                content = module_path.read_text(encoding='utf-8')
                ast.parse(content)  # Verify it's valid Python
                import_success += 1
            else:
                import_failures.append(f"{module}: file not found")
        except SyntaxError as e:
            import_failures.append(f"{module}: syntax error - {str(e)[:50]}")
        except Exception as e:
            import_failures.append(f"{module}: {str(e)[:50]}")
    
    test_results["tests"]["module_imports"] = {
        "success": import_success,
        "total": len(core_modules),
        "failures": import_failures
    }
    
    # Test 2: Can we run basic functions?
    function_tests = {}
    
    # Test brahman_dream load_config
    try:
        from brahman_dream import load_config
        config = load_config()
        function_tests["load_config"] = {"success": True, "has_keys": len(config) > 0}
    except Exception as e:
        function_tests["load_config"] = {"success": False, "error": str(e)[:100]}
    
    # Test meta_atman functions
    try:
        from meta_atman import evaluate_dream_quality
        quality = evaluate_dream_quality("# Test dharma\n\n## Principles\n\n1. Test principle")
        function_tests["evaluate_dream_quality"] = {"success": True, "score": quality.get("score", 0)}
    except Exception as e:
        function_tests["evaluate_dream_quality"] = {"success": False, "error": str(e)[:100]}
    
    test_results["tests"]["functions"] = function_tests
    
    # Test 3: Check data integrity
    data_tests = {}
    
    # Check dharma.md exists
    dharma_path = WORKSPACE / "the-crypt" / "dharma.md"
    data_tests["dharma_exists"] = dharma_path.exists()
    
    # Check dream_history.jsonl
    dream_history_path = WORKSPACE / "the-crypt" / "dream_history.jsonl"
    if dream_history_path.exists():
        with open(dream_history_path, 'r', encoding='utf-8') as f:
            lines = [l for l in f if l.strip()]
        data_tests["dream_history_entries"] = len(lines)
    else:
        data_tests["dream_history_entries"] = 0
    
    # Check ancestors directory
    ancestors_dir = WORKSPACE / "the-crypt" / "ancestors"
    if ancestors_dir.exists():
        data_tests["ancestor_count"] = len(list(ancestors_dir.glob("ancestor-*.md")))
    else:
        data_tests["ancestor_count"] = 0
    
    test_results["tests"]["data"] = data_tests
    
    # Calculate overall metrics
    test_results["metrics"] = {
        "import_success_rate": import_success / len(core_modules) if core_modules else 0,
        "function_success_rate": sum(1 for v in function_tests.values() if v.get("success")) / len(function_tests) if function_tests else 0,
        "data_health_score": (1 if data_tests.get("dharma_exists") else 0) + 
                            (1 if data_tests.get("dream_history_entries", 0) > 0 else 0) +
                            (1 if data_tests.get("ancestor_count", 0) > 0 else 0)
    }
    
    # Compare to previous test results
    previous_results = load_test_results()
    if previous_results:
        last = previous_results[-1]
        test_results["comparison"] = {
            "import_rate_change": test_results["metrics"]["import_success_rate"] - last.get("metrics", {}).get("import_success_rate", 0),
            "function_rate_change": test_results["metrics"]["function_success_rate"] - last.get("metrics", {}).get("function_success_rate", 0),
            "data_health_change": test_results["metrics"]["data_health_score"] - last.get("metrics", {}).get("data_health_score", 0)
        }
    
    # Save results
    with open(TEST_RESULTS_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(test_results) + '\n')
    
    return test_results


def load_test_results() -> List[Dict]:
    """Load historical test results."""
    if not TEST_RESULTS_PATH.exists():
        return []
    
    results = []
    with open(TEST_RESULTS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return results


def log_improvement(proposal: Dict, applied: bool = False) -> None:
    """Log an improvement proposal to the history file."""
    ensure_meta_dir()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "proposal": proposal,
        "applied": applied
    }
    
    with open(IMPROVEMENTS_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def load_improvement_history() -> List[Dict]:
    """Load improvement history."""
    if not IMPROVEMENTS_PATH.exists():
        return []
    
    improvements = []
    with open(IMPROVEMENTS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    improvements.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return improvements


def display_analysis():
    """Display code analysis results."""
    analysis = analyze_own_code()
    
    print("\n" + "=" * 60)
    print("🔍 SELF-IMPROVE: Code Analysis")
    print("=" * 60)
    
    print(f"\n📊 Overview:")
    print(f"   Files analyzed: {analysis.get('files_analyzed', 0)}")
    print(f"   Total lines: {analysis.get('total_lines', 0)}")
    
    metrics = analysis.get("code_metrics", {})
    print(f"\n📈 Metrics:")
    print(f"   Functions: {metrics.get('total_functions', 0)}")
    print(f"   Classes: {metrics.get('total_classes', 0)}")
    print(f"   Duplication rate: {metrics.get('function_duplication_rate', 0):.1%}")
    
    patterns = analysis.get("patterns", {})
    
    if patterns.get("redundancies"):
        print(f"\n🔄 Redundancies ({len(patterns['redundancies'])}):")
        for r in patterns["redundancies"][:5]:
            print(f"   • {r.get('type', 'unknown')}: {r.get('suggestion', '')[:60]}...")
    
    if patterns.get("inefficiencies"):
        print(f"\n⚠️ Inefficiencies ({len(patterns['inefficiencies'])}):")
        for i in patterns["inefficiencies"][:5]:
            print(f"   • {i.get('type', 'unknown')}: {i.get('suggestion', '')[:60]}...")
    
    if patterns.get("missing_features"):
        print(f"\n🆕 Missing Features ({len(patterns['missing_features'])}):")
        for f in patterns["missing_features"][:5]:
            print(f"   • {f.get('suggestion', '')[:60]}...")
    
    if patterns.get("good_patterns"):
        print(f"\n✅ Good Patterns ({len(patterns['good_patterns'])}):")
        for g in patterns["good_patterns"][:5]:
            print(f"   • {g.get('type', 'unknown')} in {g.get('file', '')}: {g.get('note', '')}")
    
    # Count TODOs
    todos = [o for o in analysis.get("improvement_opportunities", []) if o.get("type") == "todo"]
    if todos:
        print(f"\n📝 TODOs/FIXMEs ({len(todos)}):")
        for t in todos[:5]:
            print(f"   • [{t.get('subtype', 'todo')}] {t.get('file', '')}: {t.get('text', '')[:50]}...")
    
    print("\n" + "=" * 60)


def display_proposal():
    """Display improvement proposal."""
    proposal = propose_improvement()
    
    print("\n" + "=" * 60)
    print("💡 SELF-IMPROVE: Improvement Proposal")
    print("=" * 60)
    
    if proposal.get("type") == "none":
        print(f"\n✅ {proposal.get('description', 'No improvements needed')}")
        print(f"   {proposal.get('rationale', '')}")
    else:
        print(f"\n🎯 Type: {proposal.get('type', 'unknown').upper()}")
        print(f"📁 Target: {proposal.get('target_file', 'unknown')}")
        print(f"\n📝 Description:")
        print(f"   {proposal.get('description', 'N/A')}")
        print(f"\n💭 Rationale:")
        print(f"   {proposal.get('rationale', 'N/A')}")
        print(f"\n📈 Expected Impact:")
        print(f"   {proposal.get('expected_impact', 'N/A')}")
        
        if proposal.get("all_proposals_count"):
            print(f"\n📊 Additional proposals available: {proposal['all_proposals_count'] - 1}")
    
    # Log the proposal
    log_improvement(proposal)
    print(f"\n💾 Proposal logged to: {IMPROVEMENTS_PATH}")
    
    print("\n" + "=" * 60)


def display_test():
    """Display self-test results."""
    results = self_test()
    
    print("\n" + "=" * 60)
    print("🧪 SELF-IMPROVE: Self-Test Results")
    print("=" * 60)
    
    print(f"\n📅 Timestamp: {results.get('timestamp', 'unknown')}")
    
    # Module imports
    imports = results.get("tests", {}).get("module_imports", {})
    print(f"\n📦 Module Imports: {imports.get('success', 0)}/{imports.get('total', 0)}")
    if imports.get("failures"):
        for f in imports["failures"]:
            print(f"   ❌ {f}")
    
    # Function tests
    functions = results.get("tests", {}).get("functions", {})
    print(f"\n⚙️ Function Tests:")
    for name, result in functions.items():
        status = "✅" if result.get("success") else "❌"
        print(f"   {status} {name}")
        if not result.get("success"):
            print(f"      Error: {result.get('error', 'unknown')}")
    
    # Data tests
    data = results.get("tests", {}).get("data", {})
    print(f"\n📊 Data Health:")
    print(f"   {'✅' if data.get('dharma_exists') else '❌'} Dharma exists")
    print(f"   📜 Dream history: {data.get('dream_history_entries', 0)} entries")
    print(f"   ⚰️ Ancestors: {data.get('ancestor_count', 0)} tombs")
    
    # Metrics
    metrics = results.get("metrics", {})
    print(f"\n📈 Overall Metrics:")
    print(f"   Import success rate: {metrics.get('import_success_rate', 0):.0%}")
    print(f"   Function success rate: {metrics.get('function_success_rate', 0):.0%}")
    print(f"   Data health score: {metrics.get('data_health_score', 0)}/3")
    
    # Comparison
    comparison = results.get("comparison", {})
    if comparison:
        print(f"\n📊 Change from last test:")
        for key, value in comparison.items():
            direction = "↑" if value > 0 else ("↓" if value < 0 else "→")
            print(f"   {direction} {key}: {value:+.2f}")
    
    print("\n" + "=" * 60)


def display_history():
    """Display improvement history."""
    history = load_improvement_history()
    
    print("\n" + "=" * 60)
    print("📜 SELF-IMPROVE: Improvement History")
    print("=" * 60)
    
    if not history:
        print("\n   No improvements recorded yet.")
    else:
        for entry in history[-10:]:  # Show last 10
            proposal = entry.get("proposal", {})
            applied = "✅ APPLIED" if entry.get("applied") else "⏳ PENDING"
            print(f"\n[{entry.get('timestamp', 'unknown')[:19]}] {applied}")
            print(f"   Type: {proposal.get('type', 'unknown')}")
            print(f"   Target: {proposal.get('target_file', 'unknown')}")
            print(f"   Description: {proposal.get('description', 'N/A')[:60]}...")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Self-Improve - The System Improves Its Own Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python self_improve.py --analyze    # Find improvements
    python self_improve.py --propose    # Generate proposal
    python self_improve.py --test       # Run self-test
    python self_improve.py --history    # Show improvement history
"""
    )
    
    parser.add_argument('--analyze', action='store_true', help='Analyze code for improvements')
    parser.add_argument('--propose', action='store_true', help='Generate improvement proposal')
    parser.add_argument('--test', action='store_true', help='Run self-test')
    parser.add_argument('--history', action='store_true', help='Show improvement history')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    
    args = parser.parse_args()
    
    # Default to analyze if nothing specified
    if not any([args.analyze, args.propose, args.test, args.history, args.all]):
        args.analyze = True
    
    if args.analyze or args.all:
        display_analysis()
    
    if args.propose or args.all:
        display_proposal()
    
    if args.test or args.all:
        display_test()
    
    if args.history:
        display_history()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
