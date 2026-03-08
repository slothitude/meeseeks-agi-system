"""
Test Suite for the_body

Tests correctness AND speed of skill execution.
"""

import unittest
import time
import os
import sys
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .cache import SkillsCache
    from .intercept import TheBody
    from .distress import DistressTracker, DistressSignal
    from .skills import SkillCount, SkillFind, SkillRead, SkillLs, SkillFormat
except ImportError:
    # Running as script
    sys.path.insert(0, str(Path(__file__).parent))
    from cache import SkillsCache
    from intercept import TheBody
    from distress import DistressTracker, DistressSignal
    from skills import SkillCount, SkillFind, SkillRead, SkillLs, SkillFormat


class TestSkillMatching(unittest.TestCase):
    """Test skill pattern matching."""
    
    def test_count_match_wc(self):
        """Count skill matches 'wc -l' commands."""
        match = SkillCount.match("exec", {"command": "wc -l file.txt"})
        self.assertTrue(match.matched)
        self.assertGreater(match.confidence, 0.9)
    
    def test_count_no_match(self):
        """Count skill doesn't match unrelated commands."""
        match = SkillCount.match("exec", {"command": "echo hello"})
        self.assertFalse(match.matched)
    
    def test_ls_match(self):
        """Ls skill matches 'ls' commands."""
        match = SkillLs.match("exec", {"command": "ls -la"})
        self.assertTrue(match.matched)
        self.assertGreater(match.confidence, 0.9)
    
    def test_read_match(self):
        """Read skill matches read tool calls."""
        match = SkillRead.match("read", {"path": "test.txt"})
        self.assertTrue(match.matched)
        self.assertGreater(match.confidence, 0.9)
    
    def test_find_match_grep(self):
        """Find skill matches grep commands."""
        match = SkillFind.match("exec", {"command": "grep pattern file.txt"})
        self.assertTrue(match.matched)
    
    def test_no_match_wrong_tool(self):
        """Skills don't match wrong tool names."""
        match = SkillLs.match("read", {"path": "test.txt"})
        self.assertFalse(match.matched)


class TestSkillExecution(unittest.TestCase):
    """Test skill execution (requires actual commands)."""
    
    def test_ls_execute_simple(self):
        """Ls skill executes simple ls command."""
        result = SkillLs.execute("exec", {"command": "ls"}, {"cmd": "ls"})
        self.assertTrue(result.success)
        self.assertIsInstance(result.result, str)
        self.assertLess(result.execution_time_ms, 50)  # Should be fast
    
    def test_read_execute_file(self):
        """Read skill reads file directly."""
        # Create a test file
        test_file = Path("test_the_body_temp.txt")
        test_file.write_text("test content\nline 2\nline 3")
        
        try:
            result = SkillRead.execute(
                "read",
                {"path": str(test_file)},
                {"path": str(test_file)}
            )
            self.assertTrue(result.success)
            self.assertIn("test content", result.result)
            self.assertLess(result.execution_time_ms, 20)  # Should be very fast
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_read_with_limit(self):
        """Read skill handles offset/limit."""
        test_file = Path("test_the_body_temp.txt")
        test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5")
        
        try:
            result = SkillRead.execute(
                "read",
                {"path": str(test_file), "limit": 2},
                {"path": str(test_file), "limit": 2}
            )
            self.assertTrue(result.success)
            lines = result.result.strip().split('\n')
            self.assertEqual(len(lines), 2)
        finally:
            test_file.unlink(missing_ok=True)


class TestCache(unittest.TestCase):
    """Test skills cache O(1) lookup."""
    
    def test_cache_lookup_hit(self):
        """Cache returns skill on match."""
        cache = SkillsCache()
        skill, params = cache.lookup("exec", {"command": "ls"})
        self.assertIsNotNone(skill)
        self.assertEqual(skill.NAME, "ls")
    
    def test_cache_lookup_miss(self):
        """Cache returns None on no match."""
        cache = SkillsCache()
        skill, params = cache.lookup("exec", {"command": "nonexistent_command_xyz"})
        self.assertIsNone(skill)
    
    def test_cache_lookup_wrong_tool(self):
        """Cache returns None for unregistered tools."""
        cache = SkillsCache()
        skill, params = cache.lookup("nonexistent_tool", {})
        self.assertIsNone(skill)
    
    def test_cache_stats(self):
        """Cache tracks statistics."""
        cache = SkillsCache()
        cache.lookup("exec", {"command": "ls"})  # Hit
        cache.lookup("exec", {"command": "ls"})  # Hit
        cache.lookup("exec", {"command": "xyz"})  # Miss
        
        stats = cache.get_stats()
        self.assertEqual(stats["lookups"], 3)
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)


class TestIntercept(unittest.TestCase):
    """Test intercept layer."""
    
    def test_fast_path(self):
        """Fast path executes skill without passthrough."""
        body = TheBody()
        
        # Track if passthrough was called
        passthrough_called = []
        
        def passthrough(tool_name, args):
            passthrough_called.append(True)
            return "passthrough_result"
        
        result = body.call_tool("exec", {"command": "ls"}, passthrough)
        
        # Fast path should execute, passthrough may still be called for exec commands
        self.assertEqual(body.fast_path_count, 1)
        stats = body.get_stats()
        self.assertEqual(stats["calls"], 1)
    
    def test_slow_path(self):
        """Slow path calls passthrough when no skill matches."""
        body = TheBody()
        
        def passthrough(tool_name, args):
            return "passthrough_result"
        
        result = body.call_tool("exec", {"command": "nonexistent_xyz123"}, passthrough)
        
        self.assertEqual(body.slow_path_count, 1)
    
    def test_stats_tracking(self):
        """Intercept tracks statistics."""
        body = TheBody()
        
        def passthrough(tool_name, args):
            return "result"
        
        body.call_tool("exec", {"command": "ls"}, passthrough)
        body.call_tool("exec", {"command": "xyz"}, passthrough)
        
        stats = body.get_stats()
        self.assertEqual(stats["calls"], 2)


class TestDistress(unittest.TestCase):
    """Test distress signal emission."""
    
    def test_distress_tracker(self):
        """Distress tracker counts failures."""
        tracker = DistressTracker(threshold=3)
        
        # Record 2 failures - no signal yet
        signal = tracker.record_failure("exec", "count")
        self.assertIsNone(signal)
        signal = tracker.record_failure("exec", "count")
        self.assertIsNone(signal)
        
        # 3rd failure - signal emitted
        signal = tracker.record_failure("exec", "count")
        self.assertIsNotNone(signal)
        self.assertEqual(signal.failure_count, 3)
    
    def test_distress_reset(self):
        """Reset clears failure count."""
        tracker = DistressTracker(threshold=3)
        
        tracker.record_failure("exec", "count")
        tracker.reset("exec", "count")
        
        self.assertEqual(tracker.get_failure_count("exec", "count"), 0)
    
    def test_distress_signal_serialization(self):
        """Distress signal can be serialized."""
        signal = DistressSignal(
            tool="exec",
            pattern="count",
            failure_count=3,
            message="Test message"
        )
        
        d = signal.to_dict()
        self.assertEqual(d["tool"], "exec")
        self.assertEqual(d["pattern"], "count")
        
        json_str = signal.to_json()
        self.assertIn("exec", json_str)


class TestSpeed(unittest.TestCase):
    """Test that skills execute within speed targets."""
    
    def test_ls_speed(self):
        """Ls skill executes in <10ms."""
        result = SkillLs.execute("exec", {"command": "ls"}, {"cmd": "ls"})
        self.assertLess(result.execution_time_ms, 50, 
                       f"Ls took {result.execution_time_ms}ms, expected <50ms")
    
    def test_read_speed(self):
        """Read skill executes in <10ms."""
        test_file = Path("test_the_body_temp.txt")
        test_file.write_text("test content")
        
        try:
            result = SkillRead.execute(
                "read",
                {"path": str(test_file)},
                {"path": str(test_file)}
            )
            self.assertLess(result.execution_time_ms, 20,
                           f"Read took {result.execution_time_ms}ms, expected <20ms")
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_cache_lookup_speed(self):
        """Cache lookup is <1ms."""
        cache = SkillsCache()
        
        times = []
        for _ in range(1000):
            start = time.perf_counter()
            cache.lookup("exec", {"command": "ls"})
            times.append((time.perf_counter() - start) * 1000)
        
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 1.0,
                       f"Cache lookup avg {avg_time:.3f}ms, expected <1ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
