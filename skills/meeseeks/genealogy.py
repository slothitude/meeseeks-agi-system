#!/usr/bin/env python3
"""
NEAT-style Genealogy for Meeseeks

Tracks innovation history, enables crossover, and protects species diversity.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import random

# Meeseeks name generator - custom species
FIRST_NAMES = [
    "Fred",  # The OG
    "Morty", "Rick", "Summer", "Beth", "Jerry",
    "Carl", "Lenny", "Dale", "Barry", "Larry",
    "Phil", "Bill", "Bob", "Ted", "Ed",
    "Spike", "Tank", "Rocket", "Blaze", "Storm",
]

# Custom Meeseeks species with unique traits
MEESEEKS_SPECIES = {
    # Systematic/Methodical types
    "Glimworm": {"systematic": 0.8, "methodical": 0.7, "careful": 0.6},
    "Slogturtle": {"systematic": 0.7, "patient": 0.9, "steady": 0.8},
    "Dustbadger": {"methodical": 0.8, "thorough": 0.7, "underground": 0.6},
    
    # Creative/Unconventional types
    "Sparkmote": {"creative": 0.9, "unpredictable": 0.8, "electric": 0.7},
    "Dreamjelly": {"creative": 0.8, "fluid": 0.7, "amorphous": 0.6},
    "Chaosnewt": {"unconventional": 0.9, "wild": 0.8, "random": 0.7},
    
    # Fast/Efficient types
    "Swiftmoth": {"fast": 0.9, "efficient": 0.8, "nocturnal": 0.6},
    "Zapbeetle": {"fast": 0.8, "precise": 0.7, "staccato": 0.6},
    "Flickerfin": {"fast": 0.8, "agile": 0.8, "aquatic": 0.5},
    
    # Hybrid/Balanced types
    "Morphling": {"hybrid": 0.8, "adaptable": 0.9, "shapeshifter": 0.7},
    "Omnikin": {"balanced": 0.8, "versatile": 0.7, "flexible": 0.6},
    "Fusebeast": {"hybrid": 0.7, "combined": 0.8, "merged": 0.6},
    
    # Specialized types
    "Silkmaker": {"analytical": 0.8, "precise": 0.8, "weaver": 0.7},
    "Gloomshark": {"powerful": 0.9, "deep": 0.8, "patient": 0.7},
    "Mnemoelephant": {"reliable": 0.8, "memory": 0.9, "wise": 0.7},
    
    # Unique/Niche types
    "Echoozer": {"reflective": 0.8, "feedback": 0.7, "resonant": 0.6},
    "Pulseclaw": {"rhythmic": 0.8, "regular": 0.7, "heartbeat": 0.6},
    "Vinespeaker": {"connected": 0.8, "network": 0.7, "growing": 0.6},
    "Staticat": {"charged": 0.8, "jumpy": 0.7, "shocking": 0.6},
    "Bogwalker": {"patient": 0.9, "slow": 0.8, "steady": 0.7},
    
    # Legendary (for exceptional performers)
    "Starweaver": {"legendary": 0.9, "cosmic": 0.8, "infinite": 0.9},
    "Voidwyrn": {"legendary": 0.9, "ancient": 0.8, "primordial": 0.7},
    "Prismkin": {"legendary": 0.8, "multifaceted": 0.9, "perfect": 0.8},
    "Aetherdrake": {"legendary": 0.8, "transcendent": 0.8, "ethereal": 0.7},
    
    # === NEW SPECIES - Evolution 2026-03-02 ===
    # Nebulon - Distributed/Cloud specialists
    "Nebulon": {"distributed": 0.9, "cloud": 0.8, "parallel": 0.7, "expansive": 0.6},
    # Crystaleer - Precision and exact calculation
    "Crystaleer": {"precision": 0.95, "exact": 0.9, "crystalline": 0.8, "calculated": 0.7},
    # Shadekin - Stealth/Background task specialists  
    "Shadekin": {"stealth": 0.9, "background": 0.8, "quiet": 0.7, "unseen": 0.6},
    # Fluxbeast - Dynamic/Constant adaptation
    "Fluxbeast": {"flux": 0.9, "dynamic": 0.8, "shifting": 0.7, "adaptive": 0.8},
    # Ouroboros - Self-referential/Recursive
    "Ouroboros": {"recursive": 0.9, "self-referential": 0.8, "infinite-loop": 0.7, "ouroboric": 0.8},
}

# Trick library - stores what worked and what didn't
TRICKS_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "tricks.json"

# Default tricks that are known to work
DEFAULT_TRICKS = {
    "coder": {
        "worked": [
            "Read error logs before assuming the problem",
            "Small commits make rollback easier",
            "Check imports first when getting NameError",
            "Use print debugging when stuck",
            "Read the existing code before writing new code",
            "Run tests after every significant change",
        ],
        "failed": [
            "Assuming you understand without reading",
            "Making large changes without testing",
            "Ignoring deprecation warnings",
        ]
    },
    "searcher": {
        "worked": [
            "Start broad, then narrow search terms",
            "Check multiple search engines",
            "Look for official documentation first",
            "Verify findings with multiple sources",
        ],
        "failed": [
            "Stopping at first result",
            "Trusting single source blindly",
        ]
    },
    "tester": {
        "worked": [
            "Test edge cases explicitly",
            "Write tests before fixing bugs",
            "Use property-based testing for complex logic",
        ],
        "failed": [
            "Only testing happy path",
            "Skipping edge cases",
        ]
    },
    "deployer": {
        "worked": [
            "Test in staging first",
            "Keep rollback plan ready",
            "Deploy incrementally",
        ],
        "failed": [
            "Deploying all at once",
            "No rollback plan",
        ]
    },
    "standard": {
        "worked": [
            "Break complex tasks into smaller pieces",
            "Ask for clarification when truly stuck",
            "Verify completion before reporting done",
        ],
        "failed": [
            "Giving up without trying alternatives",
            "Assuming completion without verification",
        ]
    }
}

# Paths
GENEALOGY_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "genealogy.json"
SPECIES_DIR = Path(__file__).parent.parent.parent / "the-crypt" / "species"


class InnovationTracker:
    """Tracks innovations across Meeseeks generations."""
    
    _instance = None
    _innovations = {}
    _next_innovation_num = 0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """Load existing innovations."""
        if GENEALOGY_FILE.exists():
            data = json.loads(GENEALOGY_FILE.read_text(encoding="utf-8"))
            self._innovations = data.get("innovations", {})
            self._next_innovation_num = data.get("next_innovation", 0)
    
    def _save(self):
        """Save innovations to disk."""
        GENEALOGY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "innovations": self._innovations,
            "next_innovation": self._next_innovation_num,
            "updated": datetime.now().isoformat()
        }
        GENEALOGY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def register_innovation(self, approach: str, traits: List[str]) -> int:
        """Register a new innovation and return its ID."""
        # Create unique key for this approach+traits combo
        key = hashlib.md5(f"{approach}:{sorted(traits)}".encode()).hexdigest()[:8]
        
        # Check if already exists
        for innov_id, innov in self._innovations.items():
            if innov.get("key") == key:
                return int(innov_id)
        
        # New innovation
        innov_num = self._next_innovation_num
        self._next_innovation_num += 1
        
        self._innovations[str(innov_num)] = {
            "key": key,
            "approach": approach,
            "traits": traits,
            "created": datetime.now().isoformat(),
            "count": 1
        }
        
        self._save()
        return innov_num
    
    def get_innovation(self, innov_id: int) -> Optional[Dict]:
        """Get innovation by ID."""
        return self._innovations.get(str(innov_id))


class MeeseeksGenealogy:
    """Tracks genealogy of Meeseeks."""
    
    def __init__(self):
        self.tracker = InnovationTracker()
        self.genealogy = self._load_genealogy()
    
    def _load_genealogy(self) -> Dict:
        """Load genealogy data."""
        if GENEALOGY_FILE.exists():
            data = json.loads(GENEALOGY_FILE.read_text(encoding="utf-8"))
            return data.get("genealogy", {})
        return {}
    
    def _save_genealogy(self):
        """Save genealogy data."""
        data = {
            "genealogy": self.genealogy,
            "innovations": self.tracker._innovations,
            "next_innovation": self.tracker._next_innovation_num,
            "updated": datetime.now().isoformat()
        }
        GENEALOGY_FILE.parent.mkdir(parents=True, exist_ok=True)
        GENEALOGY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def generate_name(self, species: str, traits: List[str]) -> str:
        """Generate a unique name for a Meeseeks."""
        # All Meeseeks have last name "Meeseeks"
        # First names based on species
        species_first_names = {
            # Systematic
            "Glimworm": ["Glow", "Shine", "Lume", "Dusk"],
            "Slogturtle": ["Tank", "Shell", "Plod", "Steady"],
            "Dustbadger": ["Dirt", "Dust", "Digger", "Root"],
            # Creative
            "Sparkmote": ["Flash", "Spark", "Jolt", "Tingle"],
            "Dreamjelly": ["Drift", "Flow", "Wisp", "Haze"],
            "Chaosnewt": ["Wild", "Random", "Entropy", "Scramble"],
            # Fast
            "Swiftmoth": ["Flit", "Zoom", "Wing", "Shimmer"],
            "Zapbeetle": ["Click", "Buzz", "Snap", "Zap"],
            "Flickerfin": ["Ripple", "Flash", "Dart", "Glide"],
            # Hybrid
            "Morphling": ["Shift", "Change", "Morph", "Adapt"],
            "Omnikin": ["All", "Every", "Versa", "Flex"],
            "Fusebeast": ["Merge", "Blend", "Join", "Fuse"],
            # Specialized
            "Silkmaker": ["Thread", "Weave", "Spin", "Loom"],
            "Gloomshark": ["Depth", "Dark", "Void", "Abyss"],
            "Mnemoelephant": ["Memory", "Recall", "Think", "Remember"],
            # Unique
            "Echoozer": ["Reverb", "Echo", "Return", "Bounce"],
            "Pulseclaw": ["Beat", "Thrum", "Pulse", "Rhythm"],
            "Vinespeaker": ["Root", "Branch", "Connect", "Grow"],
            "Staticat": ["Shock", "Fuzz", "Crackle", "Hiss"],
            "Bogwalker": ["Mire", "Swamp", "Tread", "Muck"],
            # Legendary
            "Starweaver": ["Cosmos", "Nova", "Stellar", "Infinite"],
            "Voidwyrn": ["Null", "Abyss", "Ancient", "Primordial"],
            "Prismkin": ["Spectrum", "Rainbow", "Perfect", "Prism"],
            "Aetherdrake": ["Ethereal", "Transcend", "Beyond", "Sublime"],
            # NEW SPECIES - Evolution 2026-03-02
            "Nebulon": ["Cloud", "Mist", "Vapor", "Nebula", "Diffuse"],
            "Crystaleer": ["Crystal", "Shard", "Facet", "Prism", "Geode"],
            "Shadekin": ["Shadow", "Dusk", "Shade", "Umbra", "Phantom"],
            "Fluxbeast": ["Flux", "Shift", "Change", "Flow", "Current"],
            "Ouroboros": ["Loop", "Cycle", "Eternal", "Infinite", "Circle"],
        }
        
        # 10% chance of being "Fred Meeseeks" - the original
        if random.random() < 0.1:
            return "Fred Meeseeks"
        
        # Get first name options
        first_options = species_first_names.get(species, FIRST_NAMES)
        
        # Pick first name
        first = random.choice(first_options)
        
        # All Meeseeks have last name "Meeseeks"
        return f"{first} Meeseeks"
    
    def register_birth(
        self,
        session_key: str,
        generation: int,
        approach: str,
        traits: List[str],
        parent_id: Optional[str] = None,
        second_parent_id: Optional[str] = None,
        species: str = "Eevee"
    ) -> str:
        """Register a new Meeseeks birth."""
        
        # Register innovation
        innov_id = self.tracker.register_innovation(approach, traits)
        
        # Generate name
        name = self.generate_name(species, traits)
        
        # Create genealogy entry
        entry = {
            "session_key": session_key,
            "name": name,
            "generation": generation,
            "approach": approach,
            "traits": traits,
            "innovation_id": innov_id,
            "parent_id": parent_id,
            "second_parent_id": second_parent_id,
            "species": species,
            "pokemon_type": SpeciesManager.get_species_type(species),
            "fitness": None,
            "status": "active",
            "born": datetime.now().isoformat()
        }
        
        self.genealogy[session_key] = entry
        self._save_genealogy()
        
        return f"gen-{generation}-{species}-{innov_id}", name
    
    def record_fitness(self, session_key: str, fitness: float, behavior: Dict = None):
        """Record fitness score for a Meeseeks."""
        if session_key in self.genealogy:
            self.genealogy[session_key]["fitness"] = fitness
            self.genealogy[session_key]["behavior"] = behavior or {}
            self.genealogy[session_key]["status"] = "completed"
            self._save_genealogy()
    
    def get_ancestry(self, session_key: str, depth: int = 3) -> List[Dict]:
        """Get ancestry chain for a Meeseeks."""
        ancestry = []
        current = self.genealogy.get(session_key)
        
        for _ in range(depth):
            if not current:
                break
            ancestry.append(current)
            parent_id = current.get("parent_id")
            if parent_id:
                current = self.genealogy.get(parent_id)
            else:
                break
        
        return ancestry
    
    def crossover(
        self,
        parent_a_key: str,
        parent_b_key: str,
        crossover_ratio: float = 0.5
    ) -> Tuple[str, List[str]]:
        """
        Perform crossover between two parent Meeseeks.
        
        Returns:
            (approach, combined_traits)
        """
        parent_a = self.genealogy.get(parent_a_key, {})
        parent_b = self.genealogy.get(parent_b_key, {})
        
        # Combine approaches
        approach_a = parent_a.get("approach", "unknown")
        approach_b = parent_b.get("approach", "unknown")
        
        fitness_a = parent_a.get("fitness", 0) or 0
        fitness_b = parent_b.get("fitness", 0) or 0
        
        if fitness_a > fitness_b:
            approach = approach_a
        else:
            approach = approach_b
        
        # Combine traits
        traits_a = set(parent_a.get("traits", []))
        traits_b = set(parent_b.get("traits", []))
        
        # Shared traits always inherited
        shared = traits_a & traits_b
        
        # Unique traits: randomly select based on fitness
        unique_a = traits_a - traits_b
        unique_b = traits_b - traits_a
        
        combined = list(shared)
        fitness_a_val = parent_a.get("fitness", 0.5) or 0.5
        fitness_b_val = parent_b.get("fitness", 0.5) or 0.5
        
        for trait in unique_a:
            if hash(trait) % 100 < (fitness_a_val * 100):
                combined.append(trait)
        for trait in unique_b:
            if hash(trait) % 100 < (fitness_b_val * 100):
                combined.append(trait)
        
        return approach, combined
    
    def get_species_members(self, species: str) -> List[Dict]:
        """Get all members of a species."""
        return [
            entry for entry in self.genealogy.values()
            if entry.get("species") == species
        ]
    
    def get_top_performers(self, limit: int = 10, species: str = None) -> List[Dict]:
        """Get top performing Meeseeks."""
        candidates = list(self.genealogy.values())
        
        if species:
            candidates = [c for c in candidates if c.get("species") == species]
        
        # Filter to completed with fitness
        candidates = [c for c in candidates if c.get("fitness") is not None]
        
        # Sort by fitness
        candidates.sort(key=lambda x: x.get("fitness", 0), reverse=True)
        
        return candidates[:limit]


class SpeciesManager:
    """Manages species classification and protection."""
    
    # Use custom Meeseeks species
    SPECIES_TRAITS = MEESEEKS_SPECIES
    
    # Species types
    SPECIES_TYPES = {
        # Systematic
        "Glimworm": "Burrower",
        "Slogturtle": "Reptile",
        "Dustbadger": "Digger",
        # Creative
        "Sparkmote": "Elemental",
        "Dreamjelly": "Amorphous",
        "Chaosnewt": "Amphibian",
        # Fast
        "Swiftmoth": "Flyer",
        "Zapbeetle": "Insect",
        "Flickerfin": "Swimmer",
        # Hybrid
        "Morphling": "Shapeshifter",
        "Omnikin": "Versatile",
        "Fusebeast": "Hybrid",
        # Specialized
        "Silkmaker": "Weaver",
        "Gloomshark": "Deep",
        "Mnemoelephant": "Mnemonic",
        # Unique
        "Echoozer": "Resonant",
        "Pulseclaw": "Rhythmic",
        "Vinespeaker": "Network",
        "Staticat": "Electric",
        "Bogwalker": "Swamp",
        # Legendary
        "Starweaver": "Cosmic",
        "Voidwyrn": "Primordial",
        "Prismkin": "Perfect",
        "Aetherdrake": "Transcendent",
        # NEW SPECIES - Evolution 2026-03-02
        "Nebulon": "Distributed",
        "Crystaleer": "Precision",
        "Shadekin": "Stealth",
        "Fluxbeast": "Dynamic",
        "Ouroboros": "Recursive",
    }
    
    @classmethod
    def classify(cls, traits: List[str]) -> str:
        """Classify Meeseeks into a custom species based on traits."""
        trait_set = set(t.lower().replace("+", "").replace("-", "") for t in traits)
        
        best_species = "Morphling"  # default - adaptable
        best_score = 0
        
        for species, trait_scores in cls.SPECIES_TRAITS.items():
            score = sum(
                score for trait, score in trait_scores.items()
                if trait in trait_set
            )
            if score > best_score:
                best_score = score
                best_species = species
        
        return best_species
    
    @classmethod
    def get_species_type(cls, species: str) -> str:
        """Get the type of a species."""
        return cls.SPECIES_TYPES.get(species, "Creature")
    
    @classmethod
    def is_legendary(cls, species: str) -> bool:
        """Check if species is legendary (cosmic beings for top performers)."""
        legendaries = {"Starweaver", "Voidwyrn", "Prismkin", "Aetherdrake"}
        return species in legendaries
    
    @classmethod
    def promote_to_legendary(cls, fitness: float) -> Optional[str]:
        """Promote high-fitness Meeseeks to legendary status."""
        if fitness >= 0.95:
            return "Starweaver"  # Perfect execution - weaves reality
        elif fitness >= 0.90:
            return "Voidwyrn"   # Near-perfect - ancient primordial power
        elif fitness >= 0.85:
            # Choose legendary based on specialty
            import random
            return random.choice(["Prismkin", "Aetherdrake"])
        return None
    
    @classmethod
    def protect_innovation(cls, species: str, generation: int, population: List[Dict]) -> bool:
        """
        Determine if a species should be protected from elimination.
        
        New species (few members) get protection for first 3 generations.
        """
        species_members = [m for m in population if m.get("species") == species]
        
        # Protect new species
        if len(species_members) < 3 and generation < 3:
            return True
        
        return False


def spawn_with_genealogy(
    session_key: str,
    task: str,
    approach: str,
    traits: List[str],
    generation: int = 0,
    parent_id: str = None,
    second_parent_id: str = None
) -> Dict:
    """
    Spawn a Meeseeks with genealogy tracking.
    
    Returns spawn info with genealogy data.
    """
    genealogy = MeeseeksGenealogy()
    
    # Classify species
    species = SpeciesManager.classify(traits)
    
    # Register birth
    innov_id, name = genealogy.register_birth(
        session_key=session_key,
        generation=generation,
        approach=approach,
        traits=traits,
        parent_id=parent_id,
        second_parent_id=second_parent_id,
        species=species
    )
    
    return {
        "session_key": session_key,
        "name": name,
        "innovation_id": innov_id,
        "species": species,
        "pokemon_type": SpeciesManager.get_species_type(species),
        "generation": generation,
        "traits": traits,
        "approach": approach
    }


def crossover_parents(
    parent_a_key: str,
    parent_b_key: str,
    child_session_key: str,
    generation: int
) -> Dict:
    """
    Create a child Meeseeks from two parents via crossover.
    
    Returns spawn info for the child.
    """
    genealogy = MeeseeksGenealogy()
    
    # Perform crossover
    approach, traits = genealogy.crossover(parent_a_key, parent_b_key)
    
    # Classify species
    species = SpeciesManager.classify(traits)
    
    # Register birth
    innov_id, name = genealogy.register_birth(
        session_key=child_session_key,
        generation=generation,
        approach=approach,
        traits=traits,
        parent_id=parent_a_key,
        second_parent_id=parent_b_key,
        species=species
    )
    
    return {
        "session_key": child_session_key,
        "name": name,
        "innovation_id": innov_id,
        "species": species,
        "pokemon_type": SpeciesManager.get_species_type(species),
        "generation": generation,
        "traits": traits,
        "approach": approach,
        "parents": [parent_a_key, parent_b_key]
    }


def get_evolution_report() -> Dict:
    """Generate a report on the evolution state."""
    genealogy = MeeseeksGenealogy()
    
    # Get all entries
    all_entries = list(genealogy.genealogy.values())
    
    # Species distribution
    species_dist = {}
    for entry in all_entries:
        sp = entry.get("species", "unknown")
        species_dist[sp] = species_dist.get(sp, 0) + 1
    
    # Top performers
    top = genealogy.get_top_performers(limit=5)
    
    # Generation stats
    gen_stats = {}
    for entry in all_entries:
        gen = entry.get("generation", 0)
        if gen not in gen_stats:
            gen_stats[gen] = {"count": 0, "total_fitness": 0, "completed": 0}
        gen_stats[gen]["count"] += 1
        if entry.get("fitness") is not None:
            gen_stats[gen]["total_fitness"] += entry.get("fitness", 0)
            gen_stats[gen]["completed"] += 1
    
    # Calculate averages
    for gen in gen_stats:
        if gen_stats[gen]["completed"] > 0:
            gen_stats[gen]["avg_fitness"] = (
                gen_stats[gen]["total_fitness"] / gen_stats[gen]["completed"]
            )
    
    return {
        "total_meeseeks": len(all_entries),
        "species_distribution": species_dist,
        "top_performers": [
            {"session": m["session_key"], "fitness": m["fitness"], "species": m["species"]}
            for m in top
        ],
        "generation_stats": gen_stats,
        "total_innovations": len(genealogy.tracker._innovations)
    }


if __name__ == "__main__":
    # Test the system
    print("Testing NEAT-style genealogy...")
    
    # Register some test Meeseeks
    result1 = spawn_with_genealogy(
        session_key="test-alpha-1",
        task="Test task",
        approach="systematic",
        traits=["+systematic", "+careful"],
        generation=0
    )
    print(f"Alpha spawned: {result1}")
    
    result2 = spawn_with_genealogy(
        session_key="test-beta-1",
        task="Test task",
        approach="creative",
        traits=["+creative", "+fast"],
        generation=0
    )
    print(f"Beta spawned: {result2}")
    
    # Record fitness
    genealogy = MeeseeksGenealogy()
    genealogy.record_fitness("test-alpha-1", 0.72)
    genealogy.record_fitness("test-beta-1", 0.68)
    
    # Crossover
    child = crossover_parents(
        "test-alpha-1",
        "test-beta-1",
        "test-child-1",
        generation=1
    )
    print(f"Child spawned via crossover: {child}")
    
    # Report
    report = get_evolution_report()
    print(f"\nEvolution Report:")
    print(json.dumps(report, indent=2))
