#!/usr/bin/env python3
"""
Spawn Meeseeks with Real-Time Karma Monitoring

This module integrates the RealtimeKarmaWatcher into the Meeseeks spawn flow.
Every spawned Meeseeks gets:
1. Dynamic dharma inheritance (task-specific wisdom)
2. A karma watcher attached to its execution
3. Real-time karma feedback during execution
4. Potential intervention if karma drops too low

Usage:
    from spawn_with_karma import spawn_with_realtime_karma
    
    config = spawn_with_realtime_karma(
        task="Fix the authentication bug",
        bloodline="coder"
    )
    
    # Use config with sessions_spawn
    result = sessions_spawn(config)

CLI:
    python skills/meeseeks/spawn_with_karma.py --task "fix the bug" --bloodline coder
    python skills/meeseeks/spawn_with_karma.py --test
"""

import json
import sys
import io
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"

# Import components
try:
    from realtime_karma import RealtimeKarmaWatcher
    KARMA_WATCHER_AVAILABLE = True
except ImportError:
    KARMA_WATCHER_AVAILABLE = False

try:
    from dynamic_dharma import get_task_dharma
    DYNAMIC_DHARMA_AVAILABLE = True
except ImportError:
    DYNAMIC_DHARMA_AVAILABLE = False

try:
    from inherit_wisdom import inherit_wisdom
    INHERIT_WISDOM_AVAILABLE = True
except ImportError:
    INHERIT_WISDOM_AVAILABLE = False

try:
    from soul_guardian import SoulGuardian
    SOUL_GUARDIAN_AVAILABLE = True
except ImportError:
    SOUL_GUARDIAN_AVAILABLE = False

try:
    from spawn_meeseeks import spawn_prompt
    SPAWN_PROMPT_AVAILABLE = True
except ImportError:
    SPAWN_PROMPT_AVAILABLE = False


class KarmaMonitoredSpawn:
    """
    A spawn configuration with karma monitoring hooks.
    
    This wraps the standard spawn configuration with:
    - Pre-action karma evaluation
    - Post-action karma logging
    - Intervention capability
    """
    
    def __init__(
        self,
        task: str,
        bloodline: str = "coder",
        session_key: str = "",
        watcher: RealtimeKarmaWatcher = None,
        spawn_config: Dict = None
    ):
        self.task = task
        self.bloodline = bloodline
        self.session_key = session_key or f"karma-{int(time.time())}"
        self.watcher = watcher
        self.spawn_config = spawn_config or {}
        
        # Hook storage
        self.hooks = {
            "pre_action": None,
            "post_action": None,
            "karma_check": None,
            "on_intervention": None
        }
    
    def set_hook(self, hook_name: str, callback: Callable):
        """Set a hook callback."""
        if hook_name in self.hooks:
            self.hooks[hook_name] = callback
    
    def pre_action(self, action: Dict) -> float:
        """
        Called before an action is executed.
        
        Returns karma signal for this action.
        """
        if not self.watcher:
            return 0.0
        
        karma = self.watcher.evaluate_step(action, {})
        
        # Call custom hook if set
        if self.hooks["pre_action"]:
            self.hooks["pre_action"](action, karma)
        
        return karma
    
    def post_action(self, action: Dict, result: Any):
        """Called after an action completes."""
        if self.hooks["post_action"]:
            self.hooks["post_action"](action, result)
    
    def karma_check(self) -> bool:
        """
        Check if intervention is needed.
        
        Returns True if karma is critically low.
        """
        if not self.watcher:
            return False
        
        should_intervene = self.watcher.should_intervene()
        
        # Call custom hook if set
        if self.hooks["karma_check"]:
            self.hooks["karma_check"](should_intervene)
        
        return should_intervene
    
    def get_intervention_message(self) -> str:
        """Get intervention message if karma is low."""
        if not self.watcher:
            return ""
        
        return self.watcher.get_karma_feedback()
    
    def get_summary(self) -> Dict:
        """Get karma summary for this spawn."""
        if not self.watcher:
            return {"error": "No watcher attached"}
        
        return self.watcher.get_trajectory_summary()


def spawn_with_realtime_karma(
    task: str,
    bloodline: str = "coder",
    session_key: str = "",
    thinking: str = "high",
    timeout: int = 300,
    atman: bool = True,
    brahman: bool = False,
    inherit: bool = True
) -> Dict[str, Any]:
    """
    Spawn a Meeseeks with real-time karma monitoring.
    
    The Meeseeks will:
    1. Inherit dharma via dynamic_dharma.py
    2. Have a karma watcher attached
    3. Receive karma feedback during execution
    4. Can be steered if karma drops too low
    
    Args:
        task: The task description
        bloodline: Which bloodline (coder, searcher, tester, deployer)
        session_key: Optional session identifier
        thinking: Thinking level
        timeout: Timeout in seconds
        atman: Enable Atman (external witness) mode
        brahman: Enable Brahman (ultimate unity) mode
        inherit: Pull ancestor wisdom
    
    Returns:
        Dict with spawn configuration including:
        - task: The rendered prompt
        - thinking: Thinking level
        - timeout: Timeout value
        - karma_spawn: KarmaMonitoredSpawn instance
        - hooks: Pre-configured karma hooks
    """
    
    # 1. Get task-specific dharma
    dharma = ""
    if DYNAMIC_DHARMA_AVAILABLE:
        try:
            dharma = get_task_dharma(task, top_k=5)
        except Exception as e:
            print(f"[spawn_with_karma] Failed to get dynamic dharma: {e}", file=sys.stderr)
            dharma = "Decomposition is Survival. Test Incrementally. Be Honest."
    else:
        dharma = "Decomposition is Survival. Test Incrementally. Be Honest."
    
    # 2. Initialize SoulGuardian
    soul_guardian = None
    if SOUL_GUARDIAN_AVAILABLE:
        try:
            soul_guardian = SoulGuardian()
        except Exception as e:
            print(f"[spawn_with_karma] Failed to create SoulGuardian: {e}", file=sys.stderr)
    
    # 3. Initialize karma watcher
    watcher = None
    if KARMA_WATCHER_AVAILABLE:
        try:
            watcher = RealtimeKarmaWatcher(
                soul_guardian=soul_guardian,
                dharma=dharma,
                session_key=session_key or f"karma-{bloodline}-{int(time.time())}"
            )
        except Exception as e:
            print(f"[spawn_with_karma] Failed to create KarmaWatcher: {e}", file=sys.stderr)
    
    # 4. Get inherited wisdom (bloodline + ancestors)
    inherited_wisdom = ""
    if INHERIT_WISDOM_AVAILABLE and inherit:
        try:
            inherited_wisdom = inherit_wisdom(bloodline=bloodline, task_type=task)
        except Exception as e:
            print(f"[spawn_with_karma] Failed to inherit wisdom: {e}", file=sys.stderr)
    
    # 5. Build enhanced task with karma context
    karma_context = build_karma_context(dharma, inherited_wisdom)
    enhanced_task = f"{task}\n\n{karma_context}"
    
    # 6. Create spawn config using spawn_prompt if available
    base_config = {}
    if SPAWN_PROMPT_AVAILABLE:
        try:
            base_config = spawn_prompt(
                task=enhanced_task,
                meeseeks_type=bloodline,
                thinking=thinking,
                timeout=timeout,
                atman=atman,
                brahman=brahman,
                inherit=False  # We already inherited above
            )
        except Exception as e:
            print(f"[spawn_with_karma] Failed to create spawn_prompt: {e}", file=sys.stderr)
            base_config = {
                "task": enhanced_task,
                "thinking": thinking,
                "timeout": timeout
            }
    else:
        base_config = {
            "task": enhanced_task,
            "thinking": thinking,
            "timeout": timeout
        }
    
    # 7. Create KarmaMonitoredSpawn
    karma_spawn = KarmaMonitoredSpawn(
        task=task,
        bloodline=bloodline,
        session_key=watcher.session_key if watcher else session_key,
        watcher=watcher,
        spawn_config=base_config
    )
    
    # 8. Set up hooks
    def pre_action_hook(action: Dict, karma: float):
        """Log karma before action."""
        print(f"[KARMA] Pre-action: {action.get('type', 'unknown')} -> karma={karma:.3f}", file=sys.stderr)
    
    def post_action_hook(action: Dict, result: Any):
        """Log after action completes."""
        if karma_spawn.watcher:
            summary = karma_spawn.watcher.get_trajectory_summary()
            print(f"[KARMA] Post-action: cumulative={summary['cumulative_karma']:.3f}", file=sys.stderr)
    
    def karma_check_hook(should_intervene: bool):
        """Handle karma check result."""
        if should_intervene:
            print(f"[KARMA] ⚠️ Intervention needed!", file=sys.stderr)
    
    karma_spawn.set_hook("pre_action", pre_action_hook)
    karma_spawn.set_hook("post_action", post_action_hook)
    karma_spawn.set_hook("karma_check", karma_check_hook)
    
    # 9. Build final config
    config = {
        **base_config,
        "karma_spawn": karma_spawn,
        "karma_enabled": watcher is not None,
        "dharma": dharma,
        "bloodline": bloodline,
        "hooks": {
            "pre_action": lambda a: karma_spawn.pre_action(a),
            "post_action": lambda a, r: karma_spawn.post_action(a, r),
            "karma_check": lambda: karma_spawn.karma_check(),
            "get_intervention": lambda: karma_spawn.get_intervention_message()
        }
    }
    
    return config


def build_karma_context(dharma: str, inherited_wisdom: str) -> str:
    """
    Build karma context block for the task.
    
    This is injected into the Meeseeks prompt to provide:
    - Dharma principles to follow
    - Inherited wisdom from ancestors
    - Karma awareness reminders
    """
    parts = []
    
    parts.append("## 🔮 Karma Awareness")
    parts.append("")
    parts.append("You are being monitored by the Karma Watcher. Your actions are evaluated in real-time.")
    parts.append("")
    parts.append("### Dharma Principles")
    parts.append("")
    parts.append(dharma if dharma else "Decomposition is Survival. Test Incrementally. Be Honest.")
    parts.append("")
    
    if inherited_wisdom:
        parts.append("### Inherited Wisdom")
        parts.append("")
        parts.append(inherited_wisdom)
        parts.append("")
    
    parts.append("### Karma Guidelines")
    parts.append("")
    parts.append("- **High Karma**: Following dharma, honest reporting, testing frequently")
    parts.append("- **Low Karma**: Ignoring principles, overconfidence, skipping verification")
    parts.append("- **Intervention**: If karma drops too low, you'll receive guidance")
    parts.append("")
    parts.append("---")
    parts.append("*The watcher sees all. Act with awareness.*")
    
    return "\n".join(parts)


def inject_karma_feedback(session_key: str, watcher: RealtimeKarmaWatcher) -> bool:
    """
    If karma is low, send steering message to running Meeseeks.
    
    This would be called by the session manager when karma_check() returns True.
    
    Args:
        session_key: The session to send feedback to
        watcher: The karma watcher instance
    
    Returns:
        True if feedback was sent, False otherwise
    """
    if not watcher.should_intervene():
        return False
    
    feedback = watcher.get_karma_feedback()
    message = f"""⚠️ KARMA ALERT ⚠️

{feedback}

---
Reconsider your approach. Check the dharma principles.
The watcher is concerned about your trajectory.
"""
    
    # In a real implementation, this would use sessions_send
    # For now, we just mark the intervention
    watcher.mark_intervention()
    
    print(f"[KARMA] Injecting feedback to {session_key}:", file=sys.stderr)
    print(message, file=sys.stderr)
    
    return True


def log_karma(action: Dict, result: Any, watcher: RealtimeKarmaWatcher):
    """
    Log karma for an action-result pair.
    
    Called by the post_action hook.
    """
    if not watcher:
        return
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "result_summary": str(result)[:200] if result else None,
        "cumulative_karma": watcher.cumulative_karma
    }
    
    # Log to file
    try:
        log_file = CRYPT_ROOT / "karma_actions.jsonl"
        CRYPT_ROOT.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"[spawn_with_karma] Failed to log karma action: {e}", file=sys.stderr)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spawn Meeseeks with Real-Time Karma")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--bloodline", type=str, default="coder", help="Bloodline type")
    parser.add_argument("--thinking", type=str, default="high", help="Thinking level")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    parser.add_argument("--test", action="store_true", help="Run test spawn")
    parser.add_argument("--demo", action="store_true", help="Interactive demo")
    
    args = parser.parse_args()
    
    if args.test:
        print("=" * 60)
        print("KARMA-MONITORED SPAWN TEST")
        print("=" * 60)
        print()
        
        config = spawn_with_realtime_karma(
            task="Fix the authentication bug in the login system",
            bloodline="coder",
            thinking="high",
            timeout=300
        )
        
        print(f"Session Key: {config['karma_spawn'].session_key}")
        print(f"Karma Enabled: {config['karma_enabled']}")
        print(f"Bloodline: {config['bloodline']}")
        print(f"Thinking: {config['thinking']}")
        print(f"Timeout: {config['timeout']}")
        print()
        print("Dharma:")
        print(config['dharma'][:500])
        print()
        print("Task Preview:")
        print(config['task'][:1000])
        print()
        
        # Simulate some actions
        print("Simulating actions:")
        karma_spawn = config['karma_spawn']
        
        test_actions = [
            {"type": "plan", "description": "I'll decompose this into steps"},
            {"type": "read", "description": "Reading the auth module"},
            {"type": "test", "description": "Running tests"},
        ]
        
        for action in test_actions:
            karma = karma_spawn.pre_action(action)
            print(f"  {action['type']}: karma={karma:.3f}")
        
        print()
        print("Summary:")
        print(json.dumps(karma_spawn.get_summary(), indent=2))
        print()
    
    elif args.task:
        print("=" * 60)
        print(f"SPAWNING WITH KARMA: {args.task[:50]}...")
        print("=" * 60)
        print()
        
        config = spawn_with_realtime_karma(
            task=args.task,
            bloodline=args.bloodline,
            thinking=args.thinking,
            timeout=args.timeout
        )
        
        print(f"Session Key: {config['karma_spawn'].session_key}")
        print(f"Karma Enabled: {config['karma_enabled']}")
        print()
        print("Task (first 1000 chars):")
        print(config['task'][:1000])
        print()
        print("Use this config with sessions_spawn to execute.")
    
    elif args.demo:
        print("=" * 60)
        print("KARMA-MONITORED SPAWN DEMO")
        print("=" * 60)
        print()
        print("This demo shows how karma monitoring works during execution.")
        print()
        
        task = input("Enter task (or press Enter for default): ").strip()
        if not task:
            task = "Implement a function to validate email addresses"
        
        config = spawn_with_realtime_karma(
            task=task,
            bloodline="coder"
        )
        
        karma_spawn = config['karma_spawn']
        
        print(f"\nSession: {karma_spawn.session_key}")
        print(f"Dharma loaded: {len(config['dharma'])} chars")
        print()
        print("Simulating execution (type actions, 'done' to finish):")
        print()
        
        while True:
            action_input = input("Action> ").strip()
            if action_input.lower() == 'done':
                break
            
            if not action_input:
                continue
            
            # Simulate action
            action = {"type": "action", "description": action_input, "content": action_input}
            karma = karma_spawn.pre_action(action)
            
            print(f"  Karma: {karma:+.3f} (cumulative: {karma_spawn.watcher.cumulative_karma:.3f})")
            
            # Check for intervention
            if karma_spawn.karma_check():
                print()
                print("  " + karma_spawn.get_intervention_message())
                print()
        
        print()
        print("Final Summary:")
        print(json.dumps(karma_spawn.get_summary(), indent=2))
    
    else:
        parser.print_help()
