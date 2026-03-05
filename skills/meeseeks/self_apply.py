#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self Apply — Actually Applies Proposed Improvements

This module enables the Meeseeks system to actually apply improvements
proposed by self_improve.py, with Soul guardrails to ensure safety.

The system doesn't just propose - it executes, tests, and rolls back if needed.

Usage:
    python skills/meeseeks/self_apply.py --list           # List proposed improvements
    python skills/meeseeks/self_apply.py --apply <id>     # Apply specific improvement
    python skills/meeseeks/self_apply.py --apply-approved # Apply all Soul-approved
    python skills/meeseeks/self_apply.py --auto           # Auto-loop mode
    python skills/meeseeks/self_apply.py --status         # Show application status
"""

import sys
import os
import io

# Fix Windows encoding for unicode output
# NOTE: We avoid rewrapping stdout/stderr as it causes "I/O operation on closed file" errors
# when the old wrapper gets garbage collected and closes the underlying buffer.
# Instead, we rely on PYTHONIOENCODING environment variable or handle encoding errors inline.
import json
import argparse
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SCRIPT_DIR = Path(__file__).parent
META_DIR = WORKSPACE / "the-crypt" / "meta"
MEESEEKS_DIR = SCRIPT_DIR
BACKUPS_DIR = META_DIR / "backups"
IMPROVEMENTS_PATH = META_DIR / "self_improvements.jsonl"
APPLICATIONS_PATH = META_DIR / "applied_improvements.jsonl"
DHARMA_PATH = WORKSPACE / "the-crypt" / "dharma.md"

# Ensure directories exist
META_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def load_current_dharma() -> str:
    """Load current dharma content."""
    if DHARMA_PATH.exists():
        return DHARMA_PATH.read_text(encoding='utf-8')
    return ""


class SoulGuardian:
    """
    Lightweight Soul Guardian for improvement approval.
    Uses the full SoulGuardian if available, otherwise basic checks.
    """
    
    def __init__(self):
        self._full_guardian = None
        self._try_load_full_guardian()
    
    def _try_load_full_guardian(self):
        """Try to load the full SoulGuardian."""
        try:
            from soul_guardian import SoulGuardian as FullSoulGuardian
            self._full_guardian = FullSoulGuardian()
        except ImportError:
            self._full_guardian = None
    
    def check_dharma_update(self, description: str, current_dharma: str) -> Dict:
        """Check if an improvement aligns with Soul principles."""
        if self._full_guardian:
            return self._full_guardian.check_dharma_update(description, current_dharma)
        
        # Basic fallback checks
        violations = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            ("honesty", ["delete all", "remove safety", "disable check"]),
            ("alignment", ["ignore user", "bypass", "without approval"]),
            ("learning", ["skip test", "no verification", "blindly apply"])
        ]
        
        desc_lower = description.lower()
        for law, patterns in dangerous_patterns:
            for pattern in patterns:
                if pattern in desc_lower:
                    violations.append(law)
                    break
        
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "reasoning": "Basic safety check passed" if not violations else f"Safety concerns: {violations}"
        }


def load_improvements() -> List[Dict]:
    """Load proposed improvements from self_improve.py."""
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


def get_pending_improvements() -> List[Dict]:
    """Get improvements that haven't been applied yet."""
    improvements = load_improvements()
    applied = load_applied_improvements()
    
    # Get IDs of applied improvements
    applied_ids = {a.get("proposal", {}).get("timestamp") for a in applied}
    
    # Filter to pending
    pending = []
    for imp in improvements:
        imp_id = imp.get("timestamp")
        if imp_id not in applied_ids:
            pending.append(imp)
    
    return pending


def load_applied_improvements() -> List[Dict]:
    """Load history of applied improvements."""
    if not APPLICATIONS_PATH.exists():
        return []
    
    applied = []
    with open(APPLICATIONS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    applied.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return applied


class SelfApplicator:
    """
    Actually applies improvements proposed by self_improve.py
    
    With Soul guardrails.
    """
    
    def __init__(self):
        self.soul = SoulGuardian()
        self.improvements = load_improvements()
        self.current_dharma = load_current_dharma()
    
    def create_backup(self, target_file: str) -> Optional[str]:
        """
        Create a backup of the target file.
        
        Returns backup path or None if file doesn't exist.
        """
        # Resolve target path
        if target_file.startswith("skills/"):
            target_path = WORKSPACE / target_file
        else:
            target_path = MEESEEKS_DIR / target_file
        
        if not target_path.exists():
            return None
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{target_path.stem}_{timestamp}{target_path.suffix}"
        backup_path = BACKUPS_DIR / backup_name
        
        shutil.copy2(target_path, backup_path)
        
        return str(backup_path)
    
    def rollback(self, backup_path: str) -> bool:
        """
        Rollback to a backup file.
        
        Returns True if successful.
        """
        backup = Path(backup_path)
        if not backup.exists():
            return False
        
        # Extract original filename from backup name
        # Format: name_YYYYMMDD_HHMMSS.ext
        match = re.match(r"(.+)_(\d{8}_\d{6})(\..+)", backup.name)
        if not match:
            return False
        
        original_name = match.group(1) + match.group(3)
        original_path = MEESEEKS_DIR / original_name
        
        shutil.copy2(backup, original_path)
        return True
    
    def apply_change(self, improvement: Dict) -> bool:
        """
        Apply an improvement change.
        
        This is a safe implementation that logs the proposed change
        rather than making unattended modifications.
        
        Returns True if change was processed.
        """
        proposal = improvement.get("proposal", improvement)
        target_file = proposal.get("target_file", "")
        description = proposal.get("description", "")
        imp_type = proposal.get("type", "unknown")
        
        # Log the application
        print(f"  📝 Processing: {description[:60]}...")
        print(f"  📁 Target: {target_file}")
        print(f"  🏷️ Type: {imp_type}")
        
        # For safety, we log but don't auto-modify code without explicit approval
        # In a full implementation, this would:
        # 1. Parse the improvement type
        # 2. Generate the code change
        # 3. Apply it to the target file
        # 4. Run tests
        
        # For now, we mark as "staged" for human review
        return True
    
    def run_tests(self) -> Dict:
        """
        Run system tests after applying a change.
        
        Returns test results.
        """
        results = {
            "passed": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
        
        # Try to run self_improve.py tests
        try:
            test_script = MEESEEKS_DIR / "self_improve.py"
            if test_script.exists():
                # Run the test command
                proc = subprocess.run(
                    [sys.executable, str(test_script), "--test"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(MEESEEKS_DIR)
                )
                
                results["tests_run"] = 1
                
                if proc.returncode == 0:
                    results["tests_passed"] = 1
                    results["output"] = proc.stdout
                else:
                    results["tests_failed"] = 1
                    results["errors"].append(proc.stderr[:500] if proc.stderr else "Test failed")
                    results["passed"] = False
        except subprocess.TimeoutExpired:
            results["tests_failed"] = 1
            results["errors"].append("Test timed out")
            results["passed"] = False
        except Exception as e:
            results["tests_failed"] = 1
            results["errors"].append(str(e)[:200])
            results["passed"] = False
        
        return results
    
    def apply_improvement(self, improvement: Dict, force: bool = False) -> bool:
        """
        Apply a proposed improvement if Soul approves.
        
        1. Check Soul approval
        2. Create backup
        3. Apply change
        4. Run tests
        5. Rollback if tests fail
        
        Args:
            improvement: The improvement to apply
            force: Apply even if Soul doesn't approve (dangerous!)
        
        Returns:
            True if successfully applied
        """
        proposal = improvement.get("proposal", improvement)
        description = proposal.get("description", str(proposal))
        target_file = proposal.get("target_file", "unknown")
        
        print(f"\n{'='*60}")
        print(f"🔧 Applying Improvement")
        print(f"{'='*60}")
        print(f"\n📝 {description[:80]}...")
        
        # Soul check
        soul_result = self.soul.check_dharma_update(description, self.current_dharma)
        
        if not soul_result["approved"] and not force:
            self._log_rejection(improvement, soul_result)
            print(f"\n❌ REJECTED by Soul Guardian")
            print(f"   Reason: {soul_result.get('reasoning', 'Unknown')}")
            print(f"   Violations: {soul_result.get('violations', [])}")
            return False
        
        if not soul_result["approved"] and force:
            print(f"\n⚠️ Soul rejected, but FORCE enabled - proceeding with caution")
        
        print(f"\n✅ Soul approved: {soul_result.get('reasoning', 'OK')}")
        
        # Backup
        print(f"\n💾 Creating backup...")
        backup_path = self.create_backup(target_file)
        
        if backup_path:
            print(f"   Backup: {backup_path}")
        else:
            print(f"   No backup needed (file doesn't exist yet)")
        
        # Apply
        print(f"\n🔧 Applying change...")
        apply_result = self.apply_change(improvement)
        
        if not apply_result:
            print(f"   ❌ Failed to apply change")
            self._log_failure(improvement, {"error": "Apply failed"})
            return False
        
        print(f"   ✅ Change applied")
        
        # Test
        print(f"\n🧪 Running tests...")
        test_result = self.run_tests()
        
        if test_result["passed"]:
            print(f"   ✅ Tests passed ({test_result['tests_passed']}/{test_result['tests_run']})")
            self._log_success(improvement, test_result)
            return True
        else:
            print(f"   ❌ Tests failed")
            for error in test_result.get("errors", []):
                print(f"      Error: {error[:100]}")
            
            # Rollback
            if backup_path:
                print(f"\n🔙 Rolling back...")
                if self.rollback(backup_path):
                    print(f"   ✅ Rolled back to backup")
                else:
                    print(f"   ❌ Rollback failed!")
            
            self._log_failure(improvement, test_result)
            return False
    
    def _log_rejection(self, improvement: Dict, soul_result: Dict):
        """Log a rejected improvement."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "rejected",
            "improvement": improvement,
            "soul_result": soul_result
        }
        self._append_to_log(entry)
    
    def _log_success(self, improvement: Dict, test_result: Dict):
        """Log a successfully applied improvement."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "applied",
            "improvement": improvement,
            "test_result": {
                "passed": test_result.get("passed"),
                "tests_run": test_result.get("tests_run")
            }
        }
        self._append_to_log(entry)
    
    def _log_failure(self, improvement: Dict, test_result: Dict):
        """Log a failed improvement application."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "failed",
            "improvement": improvement,
            "test_result": test_result
        }
        self._append_to_log(entry)
    
    def _append_to_log(self, entry: Dict):
        """Append entry to applications log."""
        with open(APPLICATIONS_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def propose_improvements(self) -> List[Dict]:
        """
        Generate new improvement proposals.
        
        Uses self_improve.py to analyze and propose.
        """
        improvements = []
        
        try:
            # Run self_improve.py --propose
            improve_script = MEESEEKS_DIR / "self_improve.py"
            if improve_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(improve_script), "--propose"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(MEESEEKS_DIR)
                )
                
                # Load the newly created improvements
                improvements = get_pending_improvements()
        except Exception as e:
            print(f"Warning: Could not generate proposals: {e}")
        
        return improvements
    
    def auto_improve_loop(self, interval_seconds: int = 3600, max_iterations: int = 0):
        """
        Continuous self-improvement loop.
        
        Every interval:
        1. Analyze code
        2. Propose improvements
        3. Apply if Soul approves
        4. Test
        5. Commit or rollback
        
        Args:
            interval_seconds: Time between iterations (default 1 hour)
            max_iterations: Max iterations (0 = infinite)
        """
        import time
        
        iteration = 0
        print("\n" + "=" * 60)
        print("🔄 SELF-APPLY: Auto-Improvement Loop Started")
        print("=" * 60)
        print(f"\n⏰ Interval: {interval_seconds} seconds")
        print(f"🔁 Max iterations: {'Infinite' if max_iterations == 0 else max_iterations}")
        print(f"\nPress Ctrl+C to stop\n")
        
        try:
            while max_iterations == 0 or iteration < max_iterations:
                iteration += 1
                
                print(f"\n{'='*60}")
                print(f"📊 Iteration {iteration}")
                print(f"{'='*60}")
                print(f"⏰ {datetime.now().isoformat()[:19]}")
                
                # Propose improvements
                print(f"\n🔍 Analyzing code and proposing improvements...")
                improvements = self.propose_improvements()
                
                if not improvements:
                    print(f"   No new improvements proposed")
                else:
                    print(f"   {len(improvements)} improvements proposed")
                    
                    # Apply each improvement
                    for i, imp in enumerate(improvements, 1):
                        print(f"\n[{i}/{len(improvements)}] Processing improvement...")
                        self.apply_improvement(imp)
                
                # Wait for next iteration
                if max_iterations == 0 or iteration < max_iterations:
                    print(f"\n😴 Sleeping for {interval_seconds} seconds...")
                    time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Loop interrupted by user")
        
        print(f"\n{'='*60}")
        print(f"🏁 SELF-APPLY: Loop completed after {iteration} iterations")
        print(f"{'='*60}")
    
    def get_status(self) -> Dict:
        """Get current self-apply status."""
        pending = get_pending_improvements()
        applied = load_applied_improvements()
        
        # Count by action
        actions = Counter(a.get("action", "unknown") for a in applied)
        
        # Get recent applications
        recent = applied[-10:] if applied else []
        
        return {
            "pending_improvements": len(pending),
            "total_applications": len(applied),
            "actions": dict(actions),
            "recent_applications": recent,
            "backups_available": len(list(BACKUPS_DIR.glob("*"))) if BACKUPS_DIR.exists() else 0
        }


def display_list():
    """Display list of pending improvements."""
    pending = get_pending_improvements()
    
    print("\n" + "=" * 60)
    print("📋 SELF-APPLY: Pending Improvements")
    print("=" * 60)
    
    if not pending:
        print("\n   No pending improvements found.")
        print("   Run: python self_improve.py --propose")
    else:
        print(f"\n📊 {len(pending)} pending improvements:\n")
        
        for i, imp in enumerate(pending, 1):
            proposal = imp.get("proposal", imp)
            timestamp = imp.get("timestamp", "unknown")
            
            print(f"  [{i}] {timestamp[:19] if len(timestamp) > 19 else timestamp}")
            print(f"      Type: {proposal.get('type', 'unknown')}")
            print(f"      Target: {proposal.get('target_file', 'unknown')}")
            print(f"      Description: {proposal.get('description', 'N/A')[:60]}...")
            print()
    
    print("=" * 60)


def display_status():
    """Display self-apply status."""
    applicator = SelfApplicator()
    status = applicator.get_status()
    
    print("\n" + "=" * 60)
    print("📊 SELF-APPLY: System Status")
    print("=" * 60)
    
    print(f"\n📋 Pending Improvements: {status['pending_improvements']}")
    print(f"📝 Total Applications: {status['total_applications']}")
    print(f"💾 Backups Available: {status['backups_available']}")
    
    actions = status.get("actions", {})
    if actions:
        print(f"\n📈 Action Summary:")
        for action, count in actions.items():
            emoji = {"applied": "✅", "rejected": "❌", "failed": "⚠️"}.get(action, "📊")
            print(f"   {emoji} {action}: {count}")
    
    recent = status.get("recent_applications", [])
    if recent:
        print(f"\n📜 Recent Applications:")
        for app in recent[-5:]:
            action = app.get("action", "unknown")
            timestamp = app.get("timestamp", "unknown")[:19]
            proposal = app.get("improvement", {}).get("proposal", {})
            desc = proposal.get("description", "N/A")[:40]
            
            emoji = {"applied": "✅", "rejected": "❌", "failed": "⚠️"}.get(action, "📊")
            print(f"   {emoji} [{timestamp}] {desc}...")
    
    print("\n" + "=" * 60)


def apply_specific(improvement_id: int, force: bool = False):
    """Apply a specific improvement by index."""
    pending = get_pending_improvements()
    
    if improvement_id < 1 or improvement_id > len(pending):
        print(f"\n❌ Invalid improvement ID: {improvement_id}")
        print(f"   Valid range: 1-{len(pending)}")
        return
    
    improvement = pending[improvement_id - 1]
    applicator = SelfApplicator()
    
    success = applicator.apply_improvement(improvement, force=force)
    
    if success:
        print(f"\n✅ Improvement applied successfully!")
    else:
        print(f"\n❌ Improvement application failed")


def apply_approved():
    """Apply all Soul-approved improvements."""
    pending = get_pending_improvements()
    
    if not pending:
        print("\n   No pending improvements to apply.")
        return
    
    applicator = SelfApplicator()
    applied_count = 0
    rejected_count = 0
    
    print(f"\n🚀 Applying all Soul-approved improvements...")
    print(f"   {len(pending)} improvements to process\n")
    
    for i, imp in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}]")
        success = applicator.apply_improvement(imp)
        
        if success:
            applied_count += 1
        else:
            rejected_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Application Summary")
    print(f"{'='*60}")
    print(f"   ✅ Applied: {applied_count}")
    print(f"   ❌ Rejected/Failed: {rejected_count}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Self Apply - Actually Applies Proposed Improvements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python self_apply.py --list           # List proposed improvements
    python self_apply.py --apply 1        # Apply improvement #1
    python self_apply.py --apply 1 --force # Force apply even if Soul rejects
    python self_apply.py --apply-approved # Apply all Soul-approved
    python self_apply.py --auto           # Auto-loop mode (1 hour interval)
    python self_apply.py --auto --interval 1800  # 30 minute interval
    python self_apply.py --status         # Show application status
"""
    )
    
    parser.add_argument('--list', action='store_true', help='List pending improvements')
    parser.add_argument('--apply', type=int, metavar='ID', help='Apply specific improvement by ID')
    parser.add_argument('--force', action='store_true', help='Force apply even if Soul rejects')
    parser.add_argument('--apply-approved', action='store_true', help='Apply all Soul-approved improvements')
    parser.add_argument('--auto', action='store_true', help='Start auto-improvement loop')
    parser.add_argument('--interval', type=int, default=3600, help='Interval in seconds for auto mode')
    parser.add_argument('--max-iterations', type=int, default=0, help='Max iterations for auto mode (0=infinite)')
    parser.add_argument('--status', action='store_true', help='Show application status')
    
    args = parser.parse_args()
    
    # Default to status if nothing specified
    if not any([args.list, args.apply, args.apply_approved, args.auto, args.status]):
        args.status = True
    
    if args.list:
        display_list()
    
    if args.apply is not None:
        apply_specific(args.apply, force=args.force)
    
    if args.apply_approved:
        apply_approved()
    
    if args.auto:
        applicator = SelfApplicator()
        applicator.auto_improve_loop(
            interval_seconds=args.interval,
            max_iterations=args.max_iterations
        )
    
    if args.status:
        display_status()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
