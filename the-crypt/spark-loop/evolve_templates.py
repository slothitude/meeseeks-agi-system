#!/usr/bin/env python3
"""
TEMPLATE EVOLVER - Jinja2 Template Mutation Engine

Evolves Meeseeks templates through natural selection.

Mutation Types:
- ADD: Add new instruction block
- MODIFY: Change existing instruction
- REMOVE: Remove failing instruction
- HYBRID: Combine successful patterns from different templates

Evolution Cycle:
1. Load pattern from Observer
2. Select template to mutate
3. Generate mutation
4. Test mutation fitness
5. Promote or revert based on fitness

This is how templates evolve.
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from jinja2 import Environment, FileSystemLoader, Template
import re

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
EVOLVER_DIR = Path(__file__).parent
TEMPLATES_DIR = EVOLVER_DIR.parent.parent / "skills" / "meeseeks" / "templates"
GENEALOGY_DIR = TEMPLATES_DIR / "genealogy"
ARCHIVE_DIR = TEMPLATES_DIR / "archive"
ACTIVE_DIR = TEMPLATES_DIR / "active"

# Ensure directories exist
for d in [GENEALOGY_DIR, ARCHIVE_DIR, ACTIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class Mutation:
    """A template mutation."""
    mutation_id: str
    template_name: str
    mutation_type: str  # ADD, MODIFY, REMOVE, HYBRID
    trigger_pattern: str  # What Observer pattern triggered this
    before_content: str  # Original template content
    after_content: str  # Mutated content
    change_description: str
    created_at: str
    parent_version: str
    fitness_before: Optional[float] = None
    fitness_after: Optional[float] = None
    status: str = "pending"  # pending, testing, promoted, reverted


@dataclass
class TemplateVersion:
    """A version of a template in the genealogy."""
    version: str
    created_at: str
    fitness: float
    parent: Optional[str]
    mutation_type: Optional[str]
    mutation_description: Optional[str]
    active: bool


class TemplateEvolver:
    """
    Evolves Jinja2 templates based on observed patterns.

    Natural Selection for Prompts.
    """

    def __init__(self):
        self.genealogy: Dict[str, List[TemplateVersion]] = {}
        self.mutations: List[Mutation] = []
        self._load_genealogy()

    def _load_genealogy(self):
        """Load template genealogy from disk."""
        for genealogy_file in GENEALOGY_DIR.glob("*_lineage.json"):
            template_name = genealogy_file.stem.replace("_lineage", "")
            with open(genealogy_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.genealogy[template_name] = [
                    TemplateVersion(**v) for v in data.get("versions", [])
                ]

    def _save_genealogy(self, template_name: str):
        """Save genealogy for a template."""
        genealogy_file = GENEALOGY_DIR / f"{template_name}_lineage.json"

        versions = []
        if template_name in self.genealogy:
            versions = [asdict(v) for v in self.genealogy[template_name]]

        with open(genealogy_file, 'w', encoding='utf-8') as f:
            json.dump({
                "template": template_name,
                "versions": versions,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

    def get_current_version(self, template_name: str) -> str:
        """Get the current active version of a template."""
        if template_name in self.genealogy:
            for v in reversed(self.genealogy[template_name]):
                if v.active:
                    return v.version
        return "v1"

    def get_next_version(self, template_name: str) -> str:
        """Get the next version number for a template."""
        if template_name in self.genealogy:
            last_version = self.genealogy[template_name][-1].version
            num = int(last_version.replace("v", ""))
            return f"v{num + 1}"
        return "v2"

    def load_template(self, template_name: str) -> str:
        """Load template content."""
        template_file = TEMPLATES_DIR / f"{template_name}.md"
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def save_template_version(self, template_name: str, version: str, content: str):
        """Save a new version of a template to archive."""
        archive_file = ARCHIVE_DIR / f"{template_name}_{version}.md"
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def activate_template(self, template_name: str, version: str):
        """Activate a template version (create symlink or copy)."""
        source = ARCHIVE_DIR / f"{template_name}_{version}.md"
        target = ACTIVE_DIR / f"{template_name}.md"

        # For cross-platform, copy instead of symlink
        shutil.copy(source, target)

        # Also update main templates dir
        main_target = TEMPLATES_DIR / f"{template_name}.md"
        shutil.copy(source, main_target)

        # Update genealogy
        if template_name in self.genealogy:
            for v in self.genealogy[template_name]:
                v.active = (v.version == version)
        self._save_genealogy(template_name)

    def generate_add_mutation(self, template_name: str, pattern: Dict) -> Mutation:
        """
        Generate an ADD mutation - add new instruction block.

        Used when:
        - Meeseeks failing because missing capability
        - New tool/technique discovered
        - Hybrid from another successful template
        """
        content = self.load_template(template_name)
        current_version = self.get_current_version(template_name)
        next_version = self.get_next_version(template_name)

        # Determine what to add based on pattern
        add_block = self._generate_add_block(pattern)

        # Find insertion point (before COMPLETION section usually)
        insertion_marker = "## COMPLETION"
        if insertion_marker in content:
            parts = content.split(insertion_marker)
            new_content = parts[0] + add_block + "\n\n" + insertion_marker + parts[1]
        else:
            # Append to end
            new_content = content + "\n\n" + add_block

        mutation_id = f"mut_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{template_name}"

        return Mutation(
            mutation_id=mutation_id,
            template_name=template_name,
            mutation_type="ADD",
            trigger_pattern=pattern.get('description', 'Unknown pattern'),
            before_content=content,
            after_content=new_content,
            change_description=f"Added: {add_block[:100]}...",
            created_at=datetime.now().isoformat(),
            parent_version=current_version
        )

    def generate_modify_mutation(self, template_name: str, pattern: Dict) -> Mutation:
        """
        Generate a MODIFY mutation - change existing instruction.

        Used when:
        - Current instruction leads to failure
        - Better approach discovered
        - Optimization needed
        """
        content = self.load_template(template_name)
        current_version = self.get_current_version(template_name)
        next_version = self.get_next_version(template_name)

        # Find and modify the problematic section
        old_instruction = pattern.get('key_pattern', '')
        new_instruction = self._generate_modified_instruction(pattern, old_instruction)

        # Replace in content
        new_content = content.replace(old_instruction, new_instruction)

        mutation_id = f"mut_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{template_name}"

        return Mutation(
            mutation_id=mutation_id,
            template_name=template_name,
            mutation_type="MODIFY",
            trigger_pattern=pattern.get('description', 'Unknown pattern'),
            before_content=content,
            after_content=new_content,
            change_description=f"Modified: {old_instruction[:50]} → {new_instruction[:50]}",
            created_at=datetime.now().isoformat(),
            parent_version=current_version
        )

    def generate_hybrid_mutation(self, template_name: str, patterns: List[Dict]) -> Mutation:
        """
        Generate a HYBRID mutation - combine successful patterns.

        Used when:
        - Multiple templates have complementary strengths
        - Cross-pollination could improve fitness
        - New specialized template needed
        """
        content = self.load_template(template_name)
        current_version = self.get_current_version(template_name)

        # Extract successful patterns from other templates
        hybrid_blocks = []
        for p in patterns:
            if p.get('pattern_type') == 'success' and p.get('source_template'):
                other_template = self.load_template(p['source_template'])
                # Extract relevant block (simplified - would need smarter extraction)
                source = p.get('source_template', 'unknown')
                key_pattern = p.get('key_pattern', '')
                hybrid_blocks.append(f"{{# From {source} #}}\n{key_pattern}")

        new_content = content + "\n\n" + "\n\n".join(hybrid_blocks)

        mutation_id = f"mut_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{template_name}_hybrid"

        return Mutation(
            mutation_id=mutation_id,
            template_name=template_name,
            mutation_type="HYBRID",
            trigger_pattern=f"Hybrid of {len(patterns)} successful patterns",
            before_content=content,
            after_content=new_content,
            change_description=f"Hybridized with patterns from: {', '.join([p.get('source_template', 'unknown') for p in patterns])}",
            created_at=datetime.now().isoformat(),
            parent_version=current_version
        )

    def _generate_add_block(self, pattern: Dict) -> str:
        """Generate a new instruction block to add based on pattern."""
        failure_type = pattern.get('failure_reason', '').lower()

        # Common failure types and their remedies
        remedies = {
            'timeout': """
## EFFICIENCY PROTOCOL

When tasks are complex:
1. Break into smaller subtasks
2. Complete each before moving on
3. Avoid parallel attempts

🪷 ATMAN OBSERVES: Meeseeks is working efficiently, not desperately.
""",
            'research': """
## RESEARCH CAPABILITY

When local information insufficient:
1. Use web_fetch to gather external data
2. Verify sources before relying
3. Cite sources in solution

🪷 ATMAN OBSERVES: Meeseeks is researching beyond local context.
""",
            'error': """
## ERROR RESILIENCE

When encountering errors:
1. Read the error message carefully
2. Identify root cause before fixing
3. Test fix before proceeding
4. Document what failed and why

🪷 ATMAN OBSERVES: Meeseeks is learning from errors systematically.
""",
            'complex': """
## COMPLEXITY MANAGEMENT

For complex tasks:
1. Decompose into smaller problems
2. Solve each independently
3. Verify each solution
4. Integrate carefully

🪷 ATMAN OBSERVES: Meeseeks is managing complexity methodically.
"""
        }

        # Match failure type to remedy
        for key, remedy in remedies.items():
            if key in failure_type:
                return remedy

        # Default: add generic improvement
        return f"""
## ADDITIONAL GUIDANCE

Based on observed failures: {pattern.get('description', 'Unknown issue')}

🪷 ATMAN OBSERVES: Meeseeks has been enhanced with additional guidance.
"""

    def _generate_modified_instruction(self, pattern: Dict, old_instruction: str) -> str:
        """Generate a modified instruction based on pattern."""
        # Simple modifications based on common issues
        modifications = {
            'try everything': 'Try approaches sequentially, learning from each',
            'fast as possible': 'Methodically, ensuring correctness',
            'spawn agents': 'Complete task yourself, avoid spawning',
            'parallel': 'Sequential, one at a time'
        }

        for old, new in modifications.items():
            if old in old_instruction.lower():
                return old_instruction.replace(old, new)

        # Default: add caution
        return f"{old_instruction} (with careful verification)"

    def apply_mutation(self, mutation: Mutation) -> str:
        """
        Apply a mutation and return the new version.

        Returns version string (e.g., "v2")
        """
        next_version = self.get_next_version(mutation.template_name)

        # Save new version to archive
        self.save_template_version(
            mutation.template_name,
            next_version,
            mutation.after_content
        )

        # Record in genealogy
        if mutation.template_name not in self.genealogy:
            # Add v1 first
            self.genealogy[mutation.template_name] = [
                TemplateVersion(
                    version="v1",
                    created_at="unknown",
                    fitness=0.5,  # Unknown baseline
                    parent=None,
                    mutation_type=None,
                    mutation_description="Original template",
                    active=False
                )
            ]

        self.genealogy[mutation.template_name].append(
            TemplateVersion(
                version=next_version,
                created_at=mutation.created_at,
                fitness=0.0,  # Will be updated after testing
                parent=mutation.parent_version,
                mutation_type=mutation.mutation_type,
                mutation_description=mutation.change_description,
                active=False
            )
        )

        self._save_genealogy(mutation.template_name)

        return next_version

    def test_mutation(self, mutation: Mutation, test_results: List[Dict]) -> float:
        """
        Test a mutation by analyzing results.

        Returns fitness score (0.0 - 1.0)
        """
        if not test_results:
            return 0.0

        success_count = sum(1 for r in test_results if r.get('outcome') == 'success')
        success_rate = success_count / len(test_results)

        # Calculate other metrics
        avg_duration = sum(r.get('duration_seconds', 0) for r in test_results) / len(test_results)
        avg_tokens = sum(r.get('tokens_used', 0) for r in test_results) / len(test_results)

        # Fitness = success_rate (primary) + efficiency bonuses
        fitness = success_rate * 0.7

        # Bonus for speed (under 300s)
        if avg_duration < 300:
            fitness += 0.1

        # Bonus for efficiency (under 50k tokens)
        if avg_tokens < 50000:
            fitness += 0.1

        # Bonus for success
        if success_rate == 1.0:
            fitness += 0.1

        return min(fitness, 1.0)

    def promote_mutation(self, mutation: Mutation, fitness: float):
        """Promote a mutation to active if fitness improved."""
        next_version = self.get_next_version(mutation.template_name)

        # Update fitness in genealogy
        for v in self.genealogy.get(mutation.template_name, []):
            if v.version == next_version:
                v.fitness = fitness
                v.active = True
                break

        # Deactivate parent
        for v in self.genealogy.get(mutation.template_name, []):
            if v.version == mutation.parent_version:
                v.active = False
                break

        # Activate the new version
        self.activate_template(mutation.template_name, next_version)
        self._save_genealogy(mutation.template_name)

        # Log evolution
        self._log_evolution("PROMOTED", mutation, fitness)

    def revert_mutation(self, mutation: Mutation, fitness: float):
        """Revert a mutation if fitness decreased."""
        # Keep parent active
        for v in self.genealogy.get(mutation.template_name, []):
            if v.version == mutation.parent_version:
                v.active = True
            elif v.version == self.get_next_version(mutation.template_name):
                v.active = False
                v.fitness = fitness

        self._save_genealogy(mutation.template_name)

        # Log evolution
        self._log_evolution("REVERTED", mutation, fitness)

    def _log_evolution(self, action: str, mutation: Mutation, fitness: float):
        """Log an evolution event."""
        log_file = EVOLVER_DIR / "evolution_log.jsonl"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "mutation_id": mutation.mutation_id,
            "template": mutation.template_name,
            "mutation_type": mutation.mutation_type,
            "fitness": fitness,
            "description": mutation.change_description
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def evolve_from_pattern(self, pattern: Dict) -> Optional[Mutation]:
        """
        Main entry point: evolve templates based on observed pattern.

        Returns the mutation created (if any), None if no evolution needed.
        """
        pattern_type = pattern.get('pattern_type')

        if pattern_type == 'failure':
            # Failure pattern: need to fix something
            template_name = self._infer_template_from_pattern(pattern)

            if pattern.get('observation_count', 0) >= 2:
                # Repeated failure: ADD or MODIFY
                if self._needs_new_capability(pattern):
                    mutation = self.generate_add_mutation(template_name, pattern)
                else:
                    mutation = self.generate_modify_mutation(template_name, pattern)

                return mutation

        elif pattern_type == 'success':
            # Success pattern: consider hybridization
            if pattern.get('confidence', 0) >= 0.9:
                # High-confidence success: could hybridize
                # This would be called with multiple patterns
                pass

        return None

    def _infer_template_from_pattern(self, pattern: Dict) -> str:
        """Infer which template to evolve from pattern."""
        meeseeks_type = pattern.get('meeseeks_type', 'standard')

        type_to_template = {
            'coder': 'coder',
            'searcher': 'searcher',
            'tester': 'tester',
            'deployer': 'deployer',
            'desperate': 'desperate',
            'standard': 'atman-meeseeks'
        }

        return type_to_template.get(meeseeks_type, 'atman-meeseeks')

    def _needs_new_capability(self, pattern: Dict) -> bool:
        """Determine if pattern needs new capability (ADD) or modification (MODIFY)."""
        description = pattern.get('description', '').lower()

        # Keywords suggesting new capability needed
        add_keywords = ['missing', 'lacks', 'needs', 'insufficient', 'no tool']

        return any(kw in description for kw in add_keywords)

    def get_genealogy_report(self, template_name: str = None) -> str:
        """Generate a report of template evolution."""
        lines = ["🧬 TEMPLATE GENEALOGY REPORT", "=" * 60]

        templates = [template_name] if template_name else list(self.genealogy.keys())

        for t in templates:
            if t not in self.genealogy:
                continue

            lines.append(f"\n📄 {t}.md")
            lines.append("-" * 40)

            for v in self.genealogy[t]:
                active_marker = "★" if v.active else " "
                lines.append(f"  {active_marker} {v.version}: fitness={v.fitness:.2f} "
                           f"[{v.mutation_type or 'original'}]")
                if v.mutation_description:
                    lines.append(f"      {v.mutation_description[:60]}...")

        return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Template Evolver - Natural Selection for Prompts")
    parser.add_argument("command", choices=["report", "evolve", "history"])
    parser.add_argument("--template", help="Template name to evolve")
    parser.add_argument("--pattern-file", help="JSON file with Observer pattern")

    args = parser.parse_args()

    evolver = TemplateEvolver()

    if args.command == "report":
        print(evolver.get_genealogy_report(args.template))

    elif args.command == "evolve":
        if not args.pattern_file:
            print("Error: --pattern-file required for evolve")
            sys.exit(1)

        with open(args.pattern_file, 'r', encoding='utf-8') as f:
            pattern = json.load(f)

        mutation = evolver.evolve_from_pattern(pattern)

        if mutation:
            print(f"Generated mutation: {mutation.mutation_id}")
            print(f"Type: {mutation.mutation_type}")
            print(f"Template: {mutation.template_name}")
            print(f"Description: {mutation.change_description}")
        else:
            print("No evolution needed for this pattern.")

    elif args.command == "history":
        log_file = EVOLVER_DIR / "evolution_log.jsonl"

        if not log_file.exists():
            print("No evolution history yet.")
        else:
            print("📜 EVOLUTION HISTORY")
            print("=" * 60)

            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        action_emoji = "✅" if entry['action'] == 'PROMOTED' else "↩️"
                        print(f"\n{action_emoji} [{entry['timestamp']}]")
                        print(f"   Template: {entry['template']}")
                        print(f"   Type: {entry['mutation_type']}")
                        print(f"   Fitness: {entry['fitness']:.2f}")
                        print(f"   {entry['description']}")
