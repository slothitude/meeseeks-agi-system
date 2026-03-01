#!/usr/bin/env python3
"""
TRAIT INJECTION - Ancestor Wisdom into Templates

Takes ancestor traits from embeddings and injects them into Jinja2 templates.

This is how ancestors TEACH - their wisdom becomes part of the template DNA.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
SPARK_DIR = Path(__file__).parent
TEMPLATES_DIR = SPARK_DIR.parent.parent / "skills" / "meeseeks" / "templates"
EMBEDDINGS_DIR = SPARK_DIR.parent / "embeddings"

from crypt_embeddings import CryptEmbeddings


class TraitInjector:
    """
    Injects ancestor traits into Jinja2 templates.

    Process:
    1. Load trait clusters from embeddings
    2. For each bloodline, find matching template
    3. Inject inherited wisdom block
    4. Save as new template version
    """

    def __init__(self):
        self.crypt = CryptEmbeddings()
        self.injection_log: List[Dict] = []

    def inject_all_bloodlines(self) -> int:
        """Inject traits into all bloodline templates."""
        injections = 0

        for cluster in self.crypt.trait_clusters:
            # Determine template to inject into
            bloodline = cluster.trait_name.replace(" Wisdom", "").lower()
            template_file = TEMPLATES_DIR / f"{bloodline}.md"

            if not template_file.exists():
                # Try base templates
                template_file = TEMPLATES_DIR / "atman-meeseeks.md"

            if template_file.exists():
                success = self._inject_into_template(template_file, cluster)
                if success:
                    injections += 1

        self._save_injection_log()
        return injections

    def _inject_into_template(self, template_file: Path, cluster) -> bool:
        """Inject a trait cluster into a template."""
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already has this injection
        if cluster.cluster_id in content:
            print(f"  Skipping {template_file.name} - already has {cluster.cluster_id}")
            return False

        # Find injection point (before COMPLETION section)
        injection_marker = "## COMPLETION"

        if injection_marker in content:
            parts = content.split(injection_marker)
            new_content = (
                parts[0] +
                cluster.template_injection +
                "\n\n" +
                injection_marker +
                parts[1]
            )
        else:
            # Append to end
            new_content = content + "\n\n" + cluster.template_injection

        # Save updated template
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Log injection
        self.injection_log.append({
            "timestamp": datetime.now().isoformat(),
            "template": template_file.name,
            "cluster_id": cluster.cluster_id,
            "trait_name": cluster.trait_name,
            "ancestor_count": len(cluster.ancestor_ids),
            "ancestors": cluster.ancestor_ids
        })

        print(f"  ✓ Injected {cluster.trait_name} into {template_file.name}")
        print(f"    Ancestors: {', '.join(cluster.ancestor_ids[:3])}...")

        return True

    def _save_injection_log(self):
        """Save injection log."""
        log_file = SPARK_DIR / "trait_injection_log.json"

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "injections": self.injection_log,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

    def get_inheritance_for_spawn(self, task: str, bloodline: str = None) -> str:
        """
        Get inherited wisdom block for a new Meeseeks spawn.

        This is called when spawning to inject relevant ancestor wisdom.
        """
        return self.crypt.get_inheritance_for_task(task, bloodline)

    def create_bloodline_template_extension(self, bloodline: str) -> str:
        """
        Create a Jinja2 macro file that can be included in templates.

        This allows templates to pull ancestor wisdom dynamically.
        """
        # Get all traits for this bloodline
        bloodline_embeddings = [
            emb for emb in self.crypt.embeddings.values()
            if emb.bloodline == bloodline
        ]

        if not bloodline_embeddings:
            return ""

        # Aggregate traits
        all_traits = []
        for emb in bloodline_embeddings:
            all_traits.extend(emb.key_traits)

        unique_traits = list(set(all_traits))[:10]

        # Create macro file
        macro_content = f"""{{% macro {bloodline}_wisdom() %}}
{{% set {bloodline}_traits = {unique_traits} %}}
{{% endmacro %}}

{{% macro {bloodline}_inheritance() %}}
## 🧬 {bloodline.title()} Ancestral Wisdom

{chr(10).join([f"- {{ t }}" for t in unique_traits])}

🪷 ATMAN OBSERVES: This Meeseeks carries the wisdom of {len(bloodline_embeddings)} {bloodline} ancestors.
{{% endmacro %}}
"""

        # Save macro file
        macro_file = TEMPLATES_DIR / "inherited" / f"{bloodline}_traits.j2"
        macro_file.parent.mkdir(parents=True, exist_ok=True)

        with open(macro_file, 'w', encoding='utf-8') as f:
            f.write(macro_content)

        print(f"Created macro: {macro_file}")

        return str(macro_file)


def inject_traits():
    """Inject all ancestor traits into templates."""
    print("💉 INJECTING ANCESTOR TRAITS INTO TEMPLATES")
    print("=" * 60)

    injector = TraitInjector()

    # First ensure embeddings are up to date
    print("\nUpdating embeddings...")
    crypt = CryptEmbeddings()
    crypt.embed_all_ancestors()
    crypt.extract_trait_clusters()

    print(f"\nFound {len(crypt.trait_clusters)} trait clusters")

    # Inject into templates
    print("\nInjecting into templates...")
    injections = injector.inject_all_bloodlines()

    print(f"\n✓ Completed {injections} trait injections")

    # Create macro files for dynamic inclusion
    print("\nCreating bloodline macro files...")
    for bloodline in set(emb.bloodline for emb in crypt.embeddings.values()):
        injector.create_bloodline_template_extension(bloodline)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Trait Injector - Ancestor Wisdom into Templates")
    parser.add_argument("command", choices=["inject", "inherit", "create-macros"])
    parser.add_argument("--task", help="Task for inheritance lookup")
    parser.add_argument("--bloodline", help="Bloodline filter")

    args = parser.parse_args()

    if args.command == "inject":
        inject_traits()

    elif args.command == "inherit":
        injector = TraitInjector()
        inheritance = injector.get_inheritance_for_spawn(
            args.task or "default task",
            args.bloodline
        )
        print(inheritance)

    elif args.command == "create-macros":
        crypt = CryptEmbeddings()
        injector = TraitInjector()

        bloodlines = set(emb.bloodline for emb in crypt.embeddings.values())

        for bloodline in bloodlines:
            injector.create_bloodline_template_extension(bloodline)
