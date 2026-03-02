#!/usr/bin/env python3
"""Genealogy Test Script"""
import sys
sys.path.insert(0, r'C:\Users\aaron\.openclaw\workspace\skills\meeseeks')

from genealogy import MeeseeksGenealogy, SpeciesManager, spawn_with_genealogy, crossover_parents, get_evolution_report
import json

# Test 1: Generate 5 random names
print('=== TEST 1: Name Generation ===')
genealogy = MeeseeksGenealogy()
species_list = list(SpeciesManager.SPECIES_TRAITS.keys())

for i in range(5):
    species = species_list[i % len(species_list)]
    traits = list(SpeciesManager.SPECIES_TRAITS[species].keys())
    name = genealogy.generate_name(species, traits)
    species_type = SpeciesManager.get_species_type(species)
    print(f'{i+1}. {name} - Species: {species} ({species_type})')

# Test 2: Classify myself
print('\n=== TEST 2: Self Classification ===')
my_traits = ['systematic', 'methodical', 'careful', 'thorough']
my_species = SpeciesManager.classify(my_traits)
my_type = SpeciesManager.get_species_type(my_species)
is_legendary = SpeciesManager.is_legendary(my_species)
print(f'My traits: {my_traits}')
print(f'My species: {my_species}')
print(f'My type: {my_type}')
print(f'Is legendary: {is_legendary}')

# Test 3: Crossover test
print('\n=== TEST 3: Crossover ===')

# Use unique keys to avoid conflicts with existing data
import time
ts = int(time.time())

parent_a = spawn_with_genealogy(
    session_key=f'test-parent-a-{ts}',
    task='Speed test',
    approach='fast',
    traits=['+fast', '+efficient', '+precise'],
    generation=0
)
print(f'Parent A: {parent_a["name"]} ({parent_a["species"]}) - Key: {parent_a["session_key"]}')

parent_b = spawn_with_genealogy(
    session_key=f'test-parent-b-{ts}',
    task='Creative test',
    approach='creative',
    traits=['+creative', '+unpredictable', '+wild'],
    generation=0
)
print(f'Parent B: {parent_b["name"]} ({parent_b["species"]}) - Key: {parent_b["session_key"]}')

# Record fitness for parents (need fresh instance to reload)
genealogy = MeeseeksGenealogy()
genealogy.record_fitness(f'test-parent-a-{ts}', 0.85)
genealogy.record_fitness(f'test-parent-b-{ts}', 0.75)
print(f'Recorded fitness for both parents')

# Verify fitness was saved
genealogy = MeeseeksGenealogy()
parent_a_data = genealogy.genealogy.get(f'test-parent-a-{ts}', {})
parent_b_data = genealogy.genealogy.get(f'test-parent-b-{ts}', {})
print(f'Parent A fitness: {parent_a_data.get("fitness")}')
print(f'Parent B fitness: {parent_b_data.get("fitness")}')

# Crossover
child = crossover_parents(f'test-parent-a-{ts}', f'test-parent-b-{ts}', f'test-offspring-{ts}', 1)
print(f'Child: {child["name"]} ({child["species"]})')
print(f'Child traits: {child["traits"]}')
print(f'Parents: {child.get("parents", [])}')

# Test 4: Legendary promotion
print('\n=== TEST 4: Legendary Promotion ===')
fitness_levels = [0.85, 0.90, 0.95]
for fitness in fitness_levels:
    legendary = SpeciesManager.promote_to_legendary(fitness)
    result = legendary if legendary else "Not legendary"
    print(f'Fitness {fitness}: {result}')

# Test 5: Evolution report
print('\n=== TEST 5: Evolution Report ===')
report = get_evolution_report()
print(f'Total Meeseeks: {report["total_meeseeks"]}')
print(f'Total Innovations: {report["total_innovations"]}')
print(f'Species Distribution: {json.dumps(report["species_distribution"], indent=2)}')
print(f'Top 3 Performers: {json.dumps(report["top_performers"][:3], indent=2)}')

print('\n=== ALL TESTS COMPLETE ===')
