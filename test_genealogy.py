import sys
sys.path.insert(0, 'skills/meeseeks')
from genealogy import spawn_with_genealogy, crossover_parents, get_evolution_report, SpeciesManager

print('='*60)
print('MEESEEKS GENEALOGY SYSTEM TEST')
print('='*60)

# Test 1: Spawn some Meeseeks with different traits
print('\n1. SPAWNING MEESEEKS:')
print('-'*40)

m1 = spawn_with_genealogy(
    session_key='test-slow-steady',
    task='Test task',
    approach='methodical',
    traits=['+systematic', '+careful', '+patient'],
    generation=0
)
print(f"  {m1['name']} | {m1['species']} ({m1['pokemon_type']})")

m2 = spawn_with_genealogy(
    session_key='test-fast-wild',
    task='Test task',
    approach='creative',
    traits=['+creative', '+fast', '+unpredictable'],
    generation=0
)
print(f"  {m2['name']} | {m2['species']} ({m2['pokemon_type']})")

m3 = spawn_with_genealogy(
    session_key='test-hybrid',
    task='Test task',
    approach='hybrid',
    traits=['+adaptable', '+versatile', '+balanced'],
    generation=0
)
print(f"  {m3['name']} | {m3['species']} ({m3['pokemon_type']})")

# Test 2: Crossover
print('\n2. CROSSOVER TEST:')
print('-'*40)
child = crossover_parents(
    'test-slow-steady',
    'test-fast-wild',
    'test-child-1',
    generation=1
)
print(f"  Parent A: {m1['name']} ({m1['species']})")
print(f"  Parent B: {m2['name']} ({m2['species']})")
print(f"  Child:    {child['name']} ({child['species']})")
print(f"  Traits:   {child['traits']}")

# Test 3: Legendary promotion
print('\n3. LEGENDARY PROMOTION:')
print('-'*40)
for fitness in [0.85, 0.90, 0.95]:
    legendary = SpeciesManager.promote_to_legendary(fitness)
    print(f'  Fitness {fitness}: {legendary}')

# Test 4: Evolution report
print('\n4. EVOLUTION REPORT:')
print('-'*40)
report = get_evolution_report()
print(f"  Total Meeseeks: {report['total_meeseeks']}")
print(f"  Species Distribution: {report['species_distribution']}")
print(f"  Total Innovations: {report['total_innovations']}")

print('\n' + '='*60)
print('TEST COMPLETE!')
print('='*60)
