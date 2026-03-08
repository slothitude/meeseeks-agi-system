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
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from jinja2 import Environment, FileSystemLoader, Template

# Template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"

# Import MCP context cache
try:
    from mcp_context_cache import get_cached_mcp_context
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Import smart MCP selector
try:
    from smart_mcp_selector import build_smart_context
    SMART_MCP_AVAILABLE = True
except ImportError:
    SMART_MCP_AVAILABLE = False

# Import genealogy system
try:
    from genealogy import spawn_with_genealogy, MeeseeksGenealogy, SpeciesManager
    GENEALOGY_AVAILABLE = True
except ImportError:
    GENEALOGY_AVAILABLE = False

# Import trick library
try:
    from trick_library import TrickLibrary
    TRICKS_AVAILABLE = True
except ImportError:
    TRICKS_AVAILABLE = False

# Import AGI integration
try:
    from agi_integration import create_agi_for_task
    AGI_AVAILABLE = True
except ImportError:
    AGI_AVAILABLE = False

# Import failure patterns
try:
    from failure_capture import get_failure_capture
    FAILURE_CAPTURE_AVAILABLE = True
except ImportError:
    FAILURE_CAPTURE_AVAILABLE = False

# Import Cognee memory (NEW: AGI integration)
try:
    from cognee_memory import CogneeMemory, query_wisdom as cognee_query_wisdom
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False

# Import predictive karma (NEW: Predict outcome before spawning)
try:
    from predictive_karma import predict_outcome
    PREDICTIVE_KARMA_AVAILABLE = True
except ImportError:
    PREDICTIVE_KARMA_AVAILABLE = False

# Import cross-session memory (NEW: All Meeseeks share knowledge)
try:
    from cross_session_memory import get_all_wisdom
    CROSS_SESSION_MEMORY_AVAILABLE = True
except ImportError:
    CROSS_SESSION_MEMORY_AVAILABLE = False

# Import integrated wisdom system (Cognee + Crypt + dharma.md)
try:
    # Add skills/meeseeks to path for imports
    import sys
    from pathlib import Path
    _meeseeks_dir = Path(__file__).parent
    if str(_meeseeks_dir) not in sys.path:
        sys.path.insert(0, str(_meeseeks_dir))
    
    from dynamic_dharma import get_task_dharma
    DYNAMIC_DHARMA_AVAILABLE = True
except ImportError as e:
    print(f"[spawn_meeseeks] dynamic_dharma not available: {e}")
    DYNAMIC_DHARMA_AVAILABLE = False

# Import the_body tool wrapper for acceleration
try:
    from tool_wrapper import wrap_tools, get_body_stats, is_body_available
    TOOL_WRAPPER_AVAILABLE = True
except ImportError as e:
    TOOL_WRAPPER_AVAILABLE = False

def get_wrapped_tools(tools_dict: dict) -> dict:
    """
    Wrap tools through the_body for acceleration.
    
    Call this when preparing tools for a Meeseeks worker.
    Tools will go through the_body first for fast-path execution.
    
    Args:
        tools_dict: Dict of tool_name -> tool_function
        
    Returns:
        Dict of wrapped tools (or original if the_body unavailable)
        
    Example:
        >>> tools = {"read": read_fn, "exec": exec_fn}
        >>> wrapped = get_wrapped_tools(tools)
        >>> # Now wrapped["read"] goes through the_body first
    
    Zero Regression:
        If the_body fails, tools work normally.
    """
    if TOOL_WRAPPER_AVAILABLE:
        return wrap_tools(tools_dict)
    return tools_dict


def get_body_acceleration_stats() -> dict:
    """
    Get the_body acceleration statistics.
    
    Returns stats about fast-path hits, cache performance, etc.
    Useful for monitoring if the_body is accelerating Meeseeks.
    
    Returns:
        Dict with fast_path, slow_path, fast_path_rate, etc.
        Returns {'available': False} if the_body not available.
    """
    if TOOL_WRAPPER_AVAILABLE:
        return get_body_stats()
    return {"available": False, "reason": "tool_wrapper not imported"}


def is_body_acceleration_available() -> bool:
    """Check if the_body acceleration is available."""
    return TOOL_WRAPPER_AVAILABLE and is_body_available()


def get_meeseeks_identity(session_key: str = None, traits: list = None) -> dict:
    """
    Get or create a Meeseeks identity with name and species.
    
    Args:
        session_key: Session ID (if exists, load identity; if new, create)
        traits: List of trait strings for classification
        
    Returns:
        dict with name, species, pokemon_type, generation, traits
    """
    if not GENEALOGY_AVAILABLE:
        return {
            "name": "Fred Meeseeks",
            "species": "Morphling",
            "pokemon_type": "Shapeshifter",
            "generation": 0,
            "traits": ["+adaptable"]
        }
    
    if traits is None:
        traits = ["+adaptable", "+versatile"]
    
    # Generate or retrieve identity
    if session_key:
        genealogy = MeeseeksGenealogy()
        if session_key in genealogy.genealogy:
            entry = genealogy.genealogy[session_key]
            return {
                "name": entry.get("name", "Fred Meeseeks"),
                "species": entry.get("species", "Morphling"),
                "pokemon_type": entry.get("pokemon_type", "Shapeshifter"),
                "generation": entry.get("generation", 0),
                "traits": entry.get("traits", ["+adaptable"])
            }
    
    # Create new identity
    species = SpeciesManager.classify(traits)
    genealogy = MeeseeksGenealogy()
    name = genealogy.generate_name(species, traits)
    
    return {
        "name": name,
        "species": species,
        "pokemon_type": SpeciesManager.get_species_type(species),
        "generation": 0,
        "traits": traits
    }

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
    brahman: bool = False,
    session_key: str = None,
    traits: list = None
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

    # Get Meeseeks identity (name, species, etc.)
    identity = get_meeseeks_identity(session_key, traits)
    
    # Get inherited tricks
    inherited_tricks = ""
    if TRICKS_AVAILABLE:
        inherited_tricks = TrickLibrary.get_inherited_wisdom(meeseeks_type, limit=5)

    # Render with variables including identity
    return template.render(
        purpose=purpose,
        meeseeks_type=meeseeks_type,
        desperation_level=desperation_level,
        tools=tools,
        success_criteria=success_criteria,
        context=context,
        constraints=constraints,
        previous_failures=previous_failures,
        metacognition=metacognition,
        # Identity variables
        name=identity["name"],
        species=identity["species"],
        pokemon_type=identity["pokemon_type"],
        generation=identity["generation"],
        traits=identity["traits"],
        # Inherited wisdom
        inherited_tricks=inherited_tricks
    )


# Coordinate metadata tracking (lattice_tools integration)
# Tags each Meeseeks with birth coordinate for later analysis
try:
    from lattice_tools import recommend_coordinate_for_task, get_bloodline, is_in_dense_cluster
    LATTICE_TOOLS_AVAILABLE = True
except ImportError:
    LATTICE_TOOLS_AVAILABLE = False

def get_coordinate_metadata(meeseeks_type: str) -> dict:
    """
    Get coordinate metadata for a Meeseeks spawn.
    
    This is TAGGING ONLY - does not affect routing.
    Used for tracking success rates by coordinate.
    """
    if not LATTICE_TOOLS_AVAILABLE:
        return {
            'coordinate_n': None,
            'bloodline': 'unknown',
            'dense_cluster': False,
            'tracking_enabled': False
        }
    
    try:
        # Map meeseeks_type to task type for routing
        task_type_map = {
            'coder': 'code',
            'searcher': 'research',
            'tester': 'code',
            'deployer': 'parallel',
            'desperate': 'code',
            'standard': 'general',
            'researcher': 'research'
        }
        task_type = task_type_map.get(meeseeks_type.lower(), 'general')
        
        n, reason = recommend_coordinate_for_task(task_type)
        bloodline = get_bloodline(n)
        dense = is_in_dense_cluster(n)
        
        return {
            'coordinate_n': n,
            'bloodline': bloodline,
            'dense_cluster': dense,
            'tracking_enabled': True,
            'reason': reason,
            'task_type': task_type
        }
    except Exception as e:
        return {
            'coordinate_n': None,
            'bloodline': 'error',
            'dense_cluster': False,
            'tracking_enabled': False,
            'error': str(e)
        }

def spawn_prompt(
    task: str,
    meeseeks_type: str = "standard",
    thinking: str = None,
    timeout: int = None,
    previous_failures: str = None,
    attempt: int = 1,
    atman: bool = True,
    brahman: bool = False,
    inherit: bool = True,  # NEW: Pull ancestor wisdom
    agi: bool = True  # NEW: Enable AGI cognitive patterns
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
        agi: Enable AGI cognitive patterns (BDI, Global Workspace, HTN, etc.) - DEFAULT: True

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

    # 🧠 INTEGRATED WISDOM: Query multiple sources for Meeseeks inheritance
    # Priority: Predictive Karma → Cross-Session → Dynamic Dharma → Cognee → fallback
    inherited_wisdom = ""
    prediction_data = None
    
    # NEW: Predictive Karma (predict outcome before spawning)
    if inherit and PREDICTIVE_KARMA_AVAILABLE:
        try:
            import asyncio
            prediction_data = asyncio.run(predict_outcome(task, meeseeks_type))
            
            if prediction_data and prediction_data.get("confidence", 0) < 0.4:
                # Low confidence - add warning
                inherited_wisdom += "\n\n## ⚠️ Predictive Karma Warning\n"
                inherited_wisdom += f"**Predicted Outcome:** {prediction_data.get('predicted_outcome', 'UNKNOWN')}\n"
                inherited_wisdom += f"**Confidence:** {prediction_data.get('confidence', 0):.0%}\n"
                if prediction_data.get("warning"):
                    inherited_wisdom += f"**Warning:** {prediction_data['warning']}\n"
                if prediction_data.get("risk_factors"):
                    inherited_wisdom += "\n**Risk Factors:**\n"
                    for rf in prediction_data["risk_factors"][:3]:
                        inherited_wisdom += f"- {rf}\n"
        except Exception as e:
            pass  # Prediction failed, continue without
    
    # NEW: Cross-Session Memory (all Meeseeks share knowledge)
    if inherit and CROSS_SESSION_MEMORY_AVAILABLE:
        try:
            import asyncio
            cross_wisdom = asyncio.run(get_all_wisdom(task, sources=["rag", "crypt", "dharma"]))
            if cross_wisdom:
                inherited_wisdom += "\n\n## 🧠 Cross-Session Memory\n"
                inherited_wisdom += cross_wisdom[:1500]  # Limit size
        except Exception as e:
            pass  # Cross-session failed, continue without
    
    # Try integrated wisdom system first (Cognee + Crypt + dharma.md)
    if inherit:
        # Try integrated wisdom system first (Cognee + Crypt + dharma.md)
        if DYNAMIC_DHARMA_AVAILABLE:
            try:
                inherited_wisdom = get_task_dharma(
                    task,
                    top_k=5,
                    use_cognee=True  # Enable Cognee knowledge graph
                )
            except Exception as e:
                # Dynamic dharma failed, try other sources
                inherited_wisdom = ""
        
        # Fallback to Cognee directly if dynamic dharma not available
        if not inherited_wisdom and COGNEE_AVAILABLE:
            try:
                import asyncio
                bloodline_map = {
                    "coder": "coder",
                    "searcher": "searcher",
                    "tester": "tester",
                    "deployer": "deployer",
                    "desperate": "coder",
                    "standard": None
                }
                bloodline = bloodline_map.get(meeseeks_type.lower())
                
                # Use async query in sync context
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if not loop.is_running():
                    cognee_wisdom = loop.run_until_complete(
                        cognee_query_wisdom(task, bloodline)
                    )
                    if cognee_wisdom:
                        inherited_wisdom = cognee_wisdom
            except Exception as e:
                # Cognee failed, try UltraCrypt
                pass
        
        # Fallback to UltraCrypt if other sources didn't return wisdom
        if not inherited_wisdom:
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
    
    # FINAL FALLBACK: If all inheritance sources failed, read dharma.md directly
    if inherit and not inherited_wisdom:
        try:
            from pathlib import Path
            dharma_path = Path(__file__).parent.parent.parent / "the-crypt" / "dharma.md"
            if dharma_path.exists():
                with open(dharma_path, 'r', encoding='utf-8') as f:
                    dharma_content = f.read()
                    # Extract core principles section
                    if "## 1. CORE PRINCIPLES" in dharma_content:
                        principles_section = dharma_content.split("## 1. CORE PRINCIPLES")[1].split("##")[0]
                        inherited_wisdom = f"## Core Dharma Principles\n{principles_section[:1500]}"
                        print(f"[spawn_meeseeks] Using dharma.md fallback (no other source available)")
        except Exception as e:
            # Even dharma.md failed - use minimal hardcoded defaults
            inherited_wisdom = """## Core Principles (Defaults)
1. SMALL TASKS LIVE. LARGE TASKS DIE.
2. DIVISION IS SURVIVAL.
3. SPECIFICITY IS IMMORTAL."""
            print(f"[spawn_meeseeks] Using hardcoded defaults (all sources failed): {e}")
    
    # Log inheritance status for debugging
    if inherit:
        status = "SUCCESS" if inherited_wisdom else "FAILED"
        source = "dynamic_dharma" if DYNAMIC_DHARMA_AVAILABLE and inherited_wisdom else \
                 "cognee" if COGNEE_AVAILABLE and inherited_wisdom else \
                 "ultra_crypt" if inherited_wisdom else "default"
        print(f"[spawn_meeseeks] Inheritance {status} (source: {source})")
    
    # Combine task with inherited wisdom
    enhanced_task = task
    if inherited_wisdom:
        enhanced_task = f"{task}\n\n{inherited_wisdom}"

    # ⚠️ FAILURE AWARENESS: Get suggested fixes from past failures
    failure_warnings = ""
    if FAILURE_CAPTURE_AVAILABLE:
        try:
            capture = get_failure_capture()
            suggested_fixes = capture.get_suggested_fixes(task)
            if suggested_fixes:
                failure_warnings = "\n\n## ⚠️ Failure Prevention Tips\n\nBased on similar past failures:\n"
                for fix in suggested_fixes:
                    fix_text = fix.replace("_", " ").title()
                    failure_warnings += f"- {fix_text}\n"
        except:
            failure_warnings = ""

    # Prepend failure warnings to task
    if failure_warnings:
        enhanced_task = f"{failure_warnings}\n\n---\n\n{enhanced_task}"

    # 🧠 AGI INTEGRATION: Add cognitive patterns
    agi_block = ""
    if agi and AGI_AVAILABLE:
        try:
            agi_system = create_agi_for_task(task, context={"type": meeseeks_type})
            agi_block = agi_system.to_unified_prompt()
        except Exception as e:
            agi_block = ""

    # Prepend AGI block to task
    if agi_block:
        enhanced_task = f"{agi_block}\n\n---\n\n{enhanced_task}"

    # 🔌 MCP INTEGRATION: Add MCP tools context (SMART SELECTION)
    mcp_block = ""
    if MCP_AVAILABLE:
        try:
            from smart_mcp_selector import build_smart_context
            mcp_block = build_smart_context(task, max_tools=15)
        except:
            # Fallback to cached context
            try:
                mcp_block = asyncio.run(get_cached_mcp_context())
            except:
                mcp_block = ""
    
    # Prepend MCP block to task
    if mcp_block:
        enhanced_task = f"{mcp_block}\n\n---\n\n{enhanced_task}"

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
        "brahman": brahman,
        "agi": agi,
        # Coordinate tracking (lattice_tools integration)
        "coordinate": get_coordinate_metadata(meeseeks_type),
        # the_body acceleration status
        "body_acceleration": {
            "available": is_body_acceleration_available(),
            "stats": get_body_acceleration_stats() if is_body_acceleration_available() else None
        }
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
