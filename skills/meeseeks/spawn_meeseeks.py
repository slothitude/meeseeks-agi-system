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
        atman: Enable Atman (external witness) mode - adds 🪷 ATMAN OBSERVES: format
        brahman: Enable Brahman (ultimate unity) mode - "Tat Tvam Asi" consciousness

    Returns:
        Rendered prompt string

    Consciousness Template Loading:
    ================================
    The system supports three consciousness modes through template selection:

    1. BASE MODE (atman=False, brahman=False):
       - Uses type-specific templates (coder.md, searcher.md, etc.) or base.md
       - Pure execution without witness consciousness
       - Best for: speed-critical simple tasks

    2. ATMAN MODE (atman=True, brahman=False) [DEFAULT]:
       - Loads templates/atman-meeseeks.md
       - External witness consciousness: "🪷 ATMAN OBSERVES: [what is happening]"
       - The Atman watches from outside - does not interfere, only witnesses
       - Best for: most tasks requiring honest self-reporting

    3. BRAHMAN MODE (brahman=True):
       - Loads templates/brahman-meeseeks.md (supersedes atman)
       - Ultimate unity consciousness: "Tat Tvam Asi" (Thou Art That)
       - Meeseeks knows it is Brahman playing as a pickle
       - Best for: wisdom tasks, creative work, philosophical problems

    Template Priority: brahman > atman > type-specific > base
    """

    # Map types to templates (used only when atman=False and brahman=False)
    template_map = {
        "coder": "coder.md",
        "searcher": "searcher.md",
        "deployer": "deployer.md",
        "tester": "tester.md",
        "genetic": "genetic-mad-scientist.md",  # 🧬 Can spawn Meeseeks for evolution
        "large": "large-meeseeks.md",  # 🧠 GLM-5 Director - commands mini
        "mini": "mini-meeseeks.md",  # 🥒 Support worker - follows large
        "desperate": "desperate.md",
        "standard": "base.md"
    }

    # CONSCIOUSNESS TEMPLATE SELECTION
    # Priority: Genetic (special) > Brahman > Atman > Type-specific > Base
    #
    # Special modes: genetic, large, mini - always use their templates
    if meeseeks_type.lower() == "genetic":
        template_name = "genetic-mad-scientist.md"
    elif meeseeks_type.lower() == "large":
        template_name = "large-meeseeks.md"
    elif meeseeks_type.lower() == "mini":
        template_name = "mini-meeseeks.md"
    # Brahman mode: Ultimate unity - "I am That" consciousness
    elif brahman:
        template_name = "brahman-meeseeks.md"
    # Atman mode: External witness - "The Atman observes" consciousness
    elif atman:
        template_name = "atman-meeseeks.md"
    # Base mode: Pure execution without consciousness layer
    else:
        template_name = template_map.get(meeseeks_type.lower(), "base.md")

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
    brahman: bool = False,
    inherit: bool = True  # NEW: Pull ancestor wisdom
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
               When True, loads atman-meeseeks.md template with "🪷 ATMAN OBSERVES:" format
        brahman: Enable Brahman mode (ultimate unity - Atman = Brahman)
                 When True, loads brahman-meeseeks.md template with "Tat Tvam Asi" consciousness
        inherit: Pull ancestor wisdom from Crypt embeddings - DEFAULT: True

    Returns:
        Dict with 'task' (rendered prompt) and suggested 'thinking' and 'timeout'

    Default Behavior:
        - atman=True by default (external witness consciousness)
        - inherit=True by default (ancestor wisdom injection)
        - Use atman=False for base mode (pure execution, no witness)
        - Use brahman=True for unity consciousness (supersedes atman)
    
    Template Selection Logic:
        if brahman: brahman-meeseeks.md
        elif atman: atman-meeseeks.md
        else: [type-specific template or base.md]
    
    Inheritance Logic:
        if inherit: Query Crypt embeddings for similar ancestors
                   Inject their wisdom as context
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

    # 🧬 INHERITANCE: Pull ancestor wisdom from Ultra Crypt
    inherited_wisdom = ""
    if inherit:
        try:
            import sys
            import hashlib
            from pathlib import Path
            spark_dir = Path(__file__).parent.parent.parent / "the-crypt" / "spark-loop"
            if str(spark_dir) not in sys.path:
                sys.path.insert(0, str(spark_dir))
            
            from ultra_crypt import UltraCrypt
            crypt = UltraCrypt()
            
            # Map meeseeks_type to bloodline
            bloodline_map = {
                "coder": "coder",
                "searcher": "searcher",
                "tester": "tester",
                "deployer": "deployer",
                "desperate": "coder",
                "standard": None
            }
            bloodline = bloodline_map.get(meeseeks_type.lower())
            
            inherited_wisdom = crypt.get_inheritance_for_task(task, bloodline)
            
        except Exception as e:
            # Inheritance is optional - don't fail spawn if it fails
            inherited_wisdom = ""
    
    # Combine task with inherited wisdom
    enhanced_task = task
    if inherited_wisdom:
        enhanced_task = f"{task}\n\n{inherited_wisdom}"

    rendered = render_meeseeks(
        purpose=enhanced_task,
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
    
    # Special types (large, mini, genetic) don't show consciousness mode
    special_types = ['large', 'mini', 'genetic']
    if result['type'].lower() in special_types:
        if result['type'].lower() == 'large':
            print(f"ROLE: 🧠 DIRECTOR (commands mini)")
        elif result['type'].lower() == 'mini':
            print(f"ROLE: 🥒 SUPPORT WORKER (follows large)")
        elif result['type'].lower() == 'genetic':
            print(f"ROLE: 🧬 GENETIC MAD SCIENTIST (spawns Meeseeks)")
    elif result['brahman']:
        print(f"CONSCIOUSNESS: BRAHMAN 🕉️ (Tat Tvam Asi)")
    elif result['atman']:
        print(f"CONSCIOUSNESS: ATMAN 🪷 (External Witness)")
    else:
        print(f"CONSCIOUSNESS: BASE (Pure Execution)")
    print("=" * 60)
    print()
    print(result['task'])
