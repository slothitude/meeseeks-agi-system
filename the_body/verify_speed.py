"""
Quick verification that the_body fast path works and is fast.
"""

import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from the_body.cache import SkillsCache
from the_body.intercept import TheBody
from the_body.skills import SkillLs, SkillRead


def test_cache_speed():
    """Verify cache lookup is <1ms."""
    cache = SkillsCache()
    
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        skill, params = cache.lookup("exec", {"command": "ls"})
        times.append((time.perf_counter() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f"Cache lookup: {avg:.3f}ms avg (target: <1ms) - {'PASS' if avg < 1 else 'FAIL'}")
    return avg < 1


def test_ls_speed():
    """Verify ls skill is fast."""
    result = SkillLs.execute("exec", {"command": "ls"}, {"cmd": "ls"})
    print(f"Ls skill: {result.execution_time_ms:.2f}ms (target: <50ms) - {'PASS' if result.execution_time_ms < 50 else 'FAIL'}")
    return result.execution_time_ms < 50


def test_read_speed():
    """Verify read skill is fast."""
    test_file = Path("test_verify_temp.txt")
    test_file.write_text("test content\n" * 100)
    
    try:
        result = SkillRead.execute(
            "read",
            {"path": str(test_file)},
            {"path": str(test_file)}
        )
        print(f"Read skill: {result.execution_time_ms:.2f}ms (target: <20ms) - {'PASS' if result.execution_time_ms < 20 else 'FAIL'}")
        return result.execution_time_ms < 20
    finally:
        test_file.unlink(missing_ok=True)


def test_intercept_speedup():
    """Verify intercept provides speedup."""
    body = TheBody()
    
    # Mock slow passthrough
    def slow_passthrough(tool_name, args):
        time.sleep(0.005)  # 5ms simulated overhead
        return "slow_result"
    
    # Fast path test
    fast_times = []
    for _ in range(100):
        start = time.perf_counter()
        body.call_tool("exec", {"command": "ls"}, slow_passthrough)
        fast_times.append((time.perf_counter() - start) * 1000)
    
    fast_avg = sum(fast_times) / len(fast_times)
    
    # Slow path test (no matching skill)
    body.reset_stats()
    slow_times = []
    for _ in range(100):
        start = time.perf_counter()
        body.call_tool("exec", {"command": "nonexistent_xyz"}, slow_passthrough)
        slow_times.append((time.perf_counter() - start) * 1000)
    
    slow_avg = sum(slow_times) / len(slow_times)
    speedup = slow_avg / fast_avg if fast_avg > 0 else 0
    
    print(f"Fast path: {fast_avg:.2f}ms")
    print(f"Slow path: {slow_avg:.2f}ms")
    print(f"Speedup: {speedup:.1f}x (target: >1x) - {'PASS' if speedup > 1 else 'FAIL'}")
    print(f"Body stats: {body.get_stats()}")
    
    return speedup > 1


def main():
    print("="*60)
    print("the_body SPEED VERIFICATION")
    print("="*60)
    
    results = {
        "cache_speed": test_cache_speed(),
        "ls_speed": test_ls_speed(),
        "read_speed": test_read_speed(),
        "intercept_speedup": test_intercept_speedup(),
    }
    
    print("\n" + "="*60)
    passed = sum(results.values())
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: the_body is FAST!")
    else:
        print("FAILURE: Some speed tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
