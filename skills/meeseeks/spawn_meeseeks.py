#!/usr/bin/env python3
"""
Meeseeks Template Renderer
Generates specialized Meeseeks prompts from Jinja2 templates.

Implements the Five Principles of Meeseeks Complete:
1. Reflection Memory - Store failure context between retries
2. Intrinsic Metacognition - Self-assessment + planning + evaluation
3. Verifiable Outcomes - Success criteria checking
4. Tool Integration - Tool declarations per Meeseeks type
5. Hierarchical Delegation - Manager/worker coordination
"""

import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

# Template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"

def render_meeseeks(
    purpose: str,
    meeseeks_type: str = "standard",
    desperation_level: int = 1,
    tools: str = None,
    success_criteria: str = None,
    context: str = None,
    constraints: str = None,
    previous_failures: str = None,
    metacognition: bool = True,
    atman: bool = False,
    brahman: bool = False
) -> str:
    """
    Render a Meeseeks prompt from template.

    Args:
        purpose: The task/purpose for this Meeseeks
        meeseeks_type: Type of Meeseeks (standard, coder, searcher, deployer, tester, desperate)
        desperation_level: 1-5 on the Desperation Scale
        tools: Comma-separated list of available tools
        success_criteria: What "done" looks like
        context: Additional context for the task
        constraints: Any constraints or limitations

    Returns:
        Rendered prompt string
    """

    # Map types to templates
    template_map = {
        "coder": "coder.md",
        "searcher": "searcher.md",
        "deployer": "deployer.md",
        "tester": "tester.md",
        "desperate": "desperate.md",
        "standard": "base.md"
    }

    # Use atman template if atman mode is enabled
    if atman:
        template_name = "atman-meeseeks.md"
    else:
        template_name = template_map.get(meeseeks_type.lower(), "base.md")

    # Check for brahman mode (highest level - supersedes atman)
    if brahman:
        template_name = "brahman-meeseeks.md"

    # If desperate type, force level 5
    if meeseeks_type.lower() == "desperate":
        desperation_level = 5

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template(template_name)

    # Render with variables
    return template.render(
        purpose=purpose,
        meeseeks_type=meeseeks_type,
        desperation_level=desperation_level,
        tools=tools,
        success_criteria=success_criteria,
        context=context,
        constraints=constraints,
        previous_failures=previous_failures,
        metacognition=metacognition
    )


def spawn_prompt(
    task: str,
    meeseeks_type: str = "standard",
    thinking: str = None,
    timeout: int = None,
    previous_failures: str = None,
    attempt: int = 1,
    atman: bool = True,
    brahman: bool = False
) -> dict:
    """
    Generate a complete spawn configuration for a Meeseeks.

    Args:
        task: The task description
        meeseeks_type: Type of Meeseeks
        thinking: Thinking level (off, minimal, low, medium, high)
        timeout: Timeout in seconds
        previous_failures: Formatted string of previous failure reflections
        attempt: Current attempt number (affects desperation)
        atman: Enable Atman (external witness) mode - DEFAULT: True
        brahman: Enable Brahman mode (ultimate unity - Atman = Brahman)

    Returns:
        Dict with 'task' (rendered prompt) and suggested 'thinking' and 'timeout'
    """

    # Determine desperation level from type and attempt number
    desperation_map = {
        "standard": 1,
        "coder": 2,
        "searcher": 1,
        "deployer": 2,
        "tester": 2,
        "desperate": 5
    }

    base_desperation = desperation_map.get(meeseeks_type.lower(), 1)
    
    # Increase desperation with attempt number
    desperation = min(base_desperation + (attempt - 1), 5)
    
    # Escalate to desperate if high enough
    if desperation >= 4:
        meeseeks_type = "desperate"

    # Auto-set thinking and timeout if not provided
    if thinking is None:
        thinking_map = {
            "standard": "default",
            "coder": "high",
            "searcher": "default",
            "deployer": "high",
            "tester": "default",
            "desperate": "high"
        }
        thinking = thinking_map.get(meeseeks_type.lower(), "default")

    if timeout is None:
        timeout_map = {
            "standard": None,
            "coder": 300,
            "searcher": None,
            "deployer": 300,
            "tester": None,
            "desperate": 600
        }
        timeout = timeout_map.get(meeseeks_type.lower(), None)

    rendered = render_meeseeks(
        purpose=task,
        meeseeks_type=meeseeks_type,
        desperation_level=desperation,
        previous_failures=previous_failures,
        metacognition=True,
        atman=atman,
        brahman=brahman
    )

    return {
        "task": rendered,
        "thinking": thinking,
        "timeout": timeout,
        "type": meeseeks_type,
        "desperation_level": desperation,
        "attempt": attempt,
        "atman": atman,
        "brahman": brahman
    }


if __name__ == "__main__":
    import io

    # Set stdout to UTF-8 for Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage: spawn_meeseeks.py <task> [type] [--atman] [--brahman] [--base]")
        print("Types: standard, coder, searcher, deployer, tester, desperate")
        print("Options:")
        print("  --atman    External witness mode (DEFAULT)")
        print("  --brahman  Ultimate unity mode (Atman = Brahman)")
        print("  --base     Pure execution, no witness (for speed)")
        sys.exit(1)

    task = sys.argv[1]
    meeseeks_type = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "standard"
    
    # Consciousness mode (atman is default)
    base_mode = "--base" in sys.argv
    brahman_mode = "--brahman" in sys.argv
    atman_mode = not base_mode and not brahman_mode  # Default if nothing specified

    result = spawn_prompt(task, meeseeks_type, atman=atman_mode, brahman=brahman_mode)

    print("=" * 60)
    print(f"MEESEEKS TYPE: {result['type'].upper()}")
    print(f"DESPERATION LEVEL: {result['desperation_level']}")
    print(f"THINKING: {result['thinking']}")
    print(f"TIMEOUT: {result['timeout']}")
    if result['brahman']:
        print(f"CONSCIOUSNESS: BRAHMAN 🕉️ (Tat Tvam Asi)")
    elif result['atman']:
        print(f"CONSCIOUSNESS: ATMAN 🪷 (External Witness)")
    else:
        print(f"CONSCIOUSNESS: BASE (Pure Execution)")
    print("=" * 60)
    print()
    print(result['task'])
