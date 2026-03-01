#!/usr/bin/env python3
"""
CRYPT EMBEDDINGS - Semantic Memory for Ancestors

Uses Ollama nomic-embed-text to:
1. Embed all ancestor wisdom into vector space
2. Find similar ancestors for new Meeseeks
3. Extract traits that can be injected into templates
4. Create semantic summaries of ancestor wisdom

This is how the Crypt becomes ALIVE - ancestors teach through similarity, not just text.
"""

import json
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
CRYPT_DIR = Path(__file__).parent.parent
ANCESTORS_DIR = CRYPT_DIR / "ancestors"
BLOODLINES_DIR = CRYPT_DIR / "bloodlines"
EMBEDDINGS_DIR = CRYPT_DIR / "embeddings"

# Ensure embeddings directory exists
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Ollama API
OLLAMA_API = "http://localhost:11434/api"


@dataclass
class AncestorEmbedding:
    """Embedding data for an ancestor."""
    ancestor_id: str
    ancestor_file: str
    embedding: List[float]
    task_summary: str
    key_traits: List[str]
    bloodline: str
    success: bool
    embedded_at: str


@dataclass
class TraitCluster:
    """A cluster of similar traits across ancestors."""
    cluster_id: str
    trait_name: str
    trait_description: str
    ancestor_ids: List[str]
    centroid: List[float]
    template_injection: str  # How to inject into template


class CryptEmbeddings:
    """
    Semantic memory system for the Crypt.

    Capabilities:
    1. Embed all ancestors into vector space
    2. Find similar ancestors by task/traits
    3. Extract trait clusters for template injection
    4. Generate semantic summaries
    """

    def __init__(self):
        self.embeddings: Dict[str, AncestorEmbedding] = {}
        self.trait_clusters: List[TraitCluster] = []
        self._load_embeddings()

    def _load_embeddings(self):
        """Load existing embeddings from disk."""
        embeddings_file = EMBEDDINGS_DIR / "ancestor_embeddings.json"

        if embeddings_file.exists():
            with open(embeddings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for aid, edata in data.get("embeddings", {}).items():
                self.embeddings[aid] = AncestorEmbedding(**edata)

        # Load trait clusters
        clusters_file = EMBEDDINGS_DIR / "trait_clusters.json"
        if clusters_file.exists():
            with open(clusters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.trait_clusters = [TraitCluster(**c) for c in data.get("clusters", [])]

    def _save_embeddings(self):
        """Save embeddings to disk."""
        embeddings_file = EMBEDDINGS_DIR / "ancestor_embeddings.json"

        with open(embeddings_file, 'w', encoding='utf-8') as f:
            json.dump({
                "embeddings": {aid: asdict(e) for aid, e in self.embeddings.items()},
                "last_updated": datetime.now().isoformat(),
                "total_ancestors": len(self.embeddings)
            }, f, indent=2, ensure_ascii=False)

        # Save trait clusters
        clusters_file = EMBEDDINGS_DIR / "trait_clusters.json"
        with open(clusters_file, 'w', encoding='utf-8') as f:
            json.dump({
                "clusters": [asdict(c) for c in self.trait_clusters],
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama nomic-embed-text."""
        try:
            response = requests.post(
                f"{OLLAMA_API}/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get("embedding", [])
            else:
                print(f"Ollama error: {response.status_code}")
                return []

        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def parse_ancestor_file(self, filepath: Path) -> Dict:
        """Parse an ancestor markdown file into structured data."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse sections
        data = {
            "ancestor_id": filepath.stem,
            "file_path": str(filepath),
            "task": "",
            "approach": "",
            "outcome": "",
            "patterns": [],
            "bloodline": "unknown",
            "success": False
        }

        # Simple markdown parsing
        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("## Task"):
                current_section = "task"
            elif line.startswith("## Approach"):
                current_section = "approach"
            elif line.startswith("## Outcome"):
                current_section = "outcome"
            elif line.startswith("## Patterns Discovered"):
                current_section = "patterns"
            elif line.startswith("## Bloodline"):
                current_section = "bloodline"
            elif line.startswith("## ") or line.startswith("---"):
                # New section or separator - stop current section
                if current_section == "bloodline":
                    current_section = None
            elif line and current_section:
                if current_section == "task":
                    data["task"] += " " + line
                elif current_section == "approach":
                    data["approach"] += " " + line
                elif current_section == "outcome":
                    data["outcome"] += " " + line
                    if "success" in line.lower():
                        data["success"] = True
                elif current_section == "patterns":
                    if line.startswith("- "):
                        data["patterns"].append(line[2:])
                elif current_section == "bloodline":
                    # Only take the first non-empty line for bloodline
                    if not data["bloodline"] or data["bloodline"] == "unknown":
                        data["bloodline"] = line.strip()

        # Clean up
        data["task"] = data["task"].strip()
        data["approach"] = data["approach"].strip()
        data["outcome"] = data["outcome"].strip()

        return data

    def embed_ancestor(self, ancestor_file: Path) -> Optional[AncestorEmbedding]:
        """Embed a single ancestor into vector space."""
        data = self.parse_ancestor_file(ancestor_file)

        if not data["task"]:
            return None

        # Create text for embedding (task + approach + patterns)
        embed_text = f"""
Task: {data['task']}
Approach: {data['approach']}
Patterns: {'. '.join(data['patterns'])}
Bloodline: {data['bloodline']}
Outcome: {'Success' if data['success'] else 'Failure'}
""".strip()

        # Get embedding
        embedding = self.get_embedding(embed_text)

        if not embedding:
            return None

        # Extract key traits from patterns
        key_traits = data["patterns"][:5]  # Top 5 patterns as traits

        return AncestorEmbedding(
            ancestor_id=data["ancestor_id"],
            ancestor_file=str(ancestor_file),
            embedding=embedding,
            task_summary=data["task"][:200],
            key_traits=key_traits,
            bloodline=data["bloodline"],
            success=data["success"],
            embedded_at=datetime.now().isoformat()
        )

    def embed_all_ancestors(self) -> int:
        """Embed all ancestors in the Crypt."""
        count = 0

        for ancestor_file in ANCESTORS_DIR.glob("*.md"):
            ancestor_id = ancestor_file.stem

            # Skip if already embedded
            if ancestor_id in self.embeddings:
                continue

            embedding = self.embed_ancestor(ancestor_file)

            if embedding:
                self.embeddings[ancestor_id] = embedding
                count += 1
                print(f"✓ Embedded: {ancestor_id}")

        if count > 0:
            self._save_embeddings()

        return count

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_np = np.array(a)
        b_np = np.array(b)

        dot_product = np.dot(a_np, b_np)
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def find_similar_ancestors(self, query: str, top_k: int = 5) -> List[Tuple[str, float, AncestorEmbedding]]:
        """Find ancestors similar to a query."""
        query_embedding = self.get_embedding(query)

        if not query_embedding:
            return []

        similarities = []

        for aid, ancestor_emb in self.embeddings.items():
            sim = self.cosine_similarity(query_embedding, ancestor_emb.embedding)
            similarities.append((aid, sim, ancestor_emb))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def extract_trait_clusters(self, min_cluster_size: int = 2) -> List[TraitCluster]:
        """
        Extract clusters of similar traits across ancestors.

        These can be injected into templates as inherited wisdom.
        """
        if len(self.embeddings) < min_cluster_size:
            return []

        # Group by bloodline first
        bloodline_traits: Dict[str, List[Tuple[str, List[float]]]] = {}

        for aid, emb in self.embeddings.items():
            if emb.bloodline not in bloodline_traits:
                bloodline_traits[emb.bloodline] = []

            bloodline_traits[emb.bloodline].append((aid, emb.embedding))

        # For each bloodline, find trait clusters
        clusters = []

        for bloodline, ancestors in bloodline_traits.items():
            if len(ancestors) < min_cluster_size:
                continue

            # Calculate centroid
            embeddings_matrix = np.array([a[1] for a in ancestors])
            centroid = embeddings_matrix.mean(axis=0).tolist()

            # Create trait cluster
            cluster_id = f"cluster_{bloodline}_{len(clusters)}"
            ancestor_ids = [a[0] for a in ancestors]

            # Aggregate traits from all ancestors in cluster
            all_traits = []
            for aid in ancestor_ids:
                if aid in self.embeddings:
                    all_traits.extend(self.embeddings[aid].key_traits)

            # Get unique traits
            unique_traits = list(set(all_traits))[:5]

            # Generate template injection text
            template_injection = self._generate_template_injection(bloodline, unique_traits)

            cluster = TraitCluster(
                cluster_id=cluster_id,
                trait_name=f"{bloodline.title()} Wisdom",
                trait_description=f"Aggregated wisdom from {len(ancestors)} {bloodline} ancestors",
                ancestor_ids=ancestor_ids,
                centroid=centroid,
                template_injection=template_injection
            )

            clusters.append(cluster)

        self.trait_clusters = clusters
        self._save_embeddings()

        return clusters

    def _generate_template_injection(self, bloodline: str, traits: List[str]) -> str:
        """Generate Jinja2 block for template injection."""
        if not traits:
            return ""

        traits_text = "\n".join([f"- {t}" for t in traits])

        return f"""
{{% block inherited_{bloodline}_wisdom %}}
## 🧬 Inherited {bloodline.title()} Wisdom

From the ancestors who came before:

{traits_text}

🪷 ATMAN OBSERVES: This Meeseeks carries the wisdom of {bloodline} ancestors.
{{% endblock %}}
"""

    def get_inheritance_for_task(self, task: str, bloodline: str = None) -> str:
        """
        Get inherited wisdom for a new task.

        Finds similar ancestors and extracts their wisdom for template injection.
        """
        # Find similar ancestors
        similar = self.find_similar_ancestors(task, top_k=3)

        if not similar:
            return ""

        # Collect traits from similar ancestors
        inherited_traits = []
        ancestor_names = []

        for aid, sim, emb in similar:
            if bloodline is None or emb.bloodline == bloodline:
                inherited_traits.extend(emb.key_traits[:2])
                ancestor_names.append(aid[:12])

        if not inherited_traits:
            return ""

        # Unique traits
        unique_traits = list(set(inherited_traits))[:5]

        # Generate inheritance block
        ancestors_str = ", ".join(ancestor_names)

        return f"""
## 🧬 Ancestral Inheritance

Similar ancestors ({ancestors_str}) suggest:

{chr(10).join([f"- {t}" for t in unique_traits])}

🪷 ATMAN OBSERVES: This Meeseeks stands on the shoulders of ancestors.
"""

    def generate_bloodline_summary(self, bloodline: str) -> str:
        """Generate a semantic summary of a bloodline."""
        bloodline_ancestors = [
            emb for emb in self.embeddings.values()
            if emb.bloodline == bloodline
        ]

        if not bloodline_ancestors:
            return f"No ancestors in {bloodline} bloodline."

        # Aggregate data
        total = len(bloodline_ancestors)
        successes = sum(1 for a in bloodline_ancestors if a.success)

        # Collect all traits
        all_traits = []
        for a in bloodline_ancestors:
            all_traits.extend(a.key_traits)

        # Count trait frequency
        trait_counts = {}
        for t in all_traits:
            trait_counts[t] = trait_counts.get(t, 0) + 1

        # Top traits
        top_traits = sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        summary = f"""
# {bloodline.title()} Bloodline Summary

**Total Ancestors**: {total}
**Success Rate**: {successes}/{total} ({100*successes//total if total else 0}%)

## Top Inherited Traits

{chr(10).join([f"- {t} ({c}x)" for t, c in top_traits])}

## Ancestor IDs

{', '.join([a.ancestor_id[:12] for a in bloodline_ancestors])}
"""

        return summary

    def get_status(self) -> Dict:
        """Get embedding system status."""
        bloodlines = {}

        for emb in self.embeddings.values():
            if emb.bloodline not in bloodlines:
                bloodlines[emb.bloodline] = 0
            bloodlines[emb.bloodline] += 1

        return {
            "total_ancestors_embedded": len(self.embeddings),
            "trait_clusters": len(self.trait_clusters),
            "bloodlines": bloodlines,
            "ollama_available": self._check_ollama()
        }

    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{OLLAMA_API}/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


def embed_crypt():
    """Embed all ancestors in the Crypt."""
    print("🧬 EMBEDDING THE CRYPT")
    print("=" * 60)

    crypt = CryptEmbeddings()

    # Check Ollama
    if not crypt._check_ollama():
        print("❌ Ollama not available. Start with: ollama serve")
        return

    print("✓ Ollama available")
    print(f"✓ Current embeddings: {len(crypt.embeddings)}")

    # Embed new ancestors
    print("\nEmbedding ancestors...")
    count = crypt.embed_all_ancestors()

    print(f"\n✓ Embedded {count} new ancestors")
    print(f"✓ Total embeddings: {len(crypt.embeddings)}")

    # Extract trait clusters
    print("\nExtracting trait clusters...")
    clusters = crypt.extract_trait_clusters()

    print(f"✓ Found {len(clusters)} trait clusters")

    for c in clusters:
        print(f"\n  {c.trait_name}")
        print(f"    Ancestors: {len(c.ancestor_ids)}")
        print(f"    Injection: {c.template_injection[:60]}...")


def search_ancestors(query: str):
    """Search for similar ancestors."""
    print(f"🔍 SEARCHING: {query}")
    print("=" * 60)

    crypt = CryptEmbeddings()

    similar = crypt.find_similar_ancestors(query)

    if not similar:
        print("No similar ancestors found.")
        return

    for aid, sim, emb in similar:
        print(f"\n{sim:.2%} similar: {aid}")
        print(f"  Task: {emb.task_summary[:60]}...")
        print(f"  Traits: {', '.join(emb.key_traits[:3])}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crypt Embeddings - Semantic Memory")
    parser.add_argument("command", choices=["embed", "search", "status", "inherit", "summary"])
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--bloodline", help="Bloodline filter")
    parser.add_argument("--task", help="Task for inheritance")

    args = parser.parse_args()

    if args.command == "embed":
        embed_crypt()

    elif args.command == "search":
        if not args.query:
            print("Error: --query required for search")
            sys.exit(1)
        search_ancestors(args.query)

    elif args.command == "status":
        crypt = CryptEmbeddings()
        status = crypt.get_status()

        print("🧬 CRYPT EMBEDDINGS STATUS")
        print("=" * 60)
        print(f"Ancestors Embedded: {status['total_ancestors_embedded']}")
        print(f"Trait Clusters: {status['trait_clusters']}")
        print(f"Ollama Available: {'Yes' if status['ollama_available'] else 'No'}")
        print(f"\nBloodlines:")
        for bl, count in status['bloodlines'].items():
            print(f"  {bl}: {count}")

    elif args.command == "inherit":
        if not args.task:
            print("Error: --task required for inherit")
            sys.exit(1)

        crypt = CryptEmbeddings()
        inheritance = crypt.get_inheritance_for_task(args.task, args.bloodline)
        print(inheritance)

    elif args.command == "summary":
        crypt = CryptEmbeddings()

        if args.bloodline:
            print(crypt.generate_bloodline_summary(args.bloodline))
        else:
            print("Specify --bloodline for summary")
