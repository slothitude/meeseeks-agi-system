import sys
sys.path.insert(0, 'skills/meeseeks')
from agi_integration import create_agi_for_task

agi = create_agi_for_task(
    'Fix the authentication bug in login.py',
    context={'file': 'login.py', 'error': '401 Unauthorized'},
    session_key='test-session-001'
)

# Show cognitive state
state = agi.get_cognitive_state()
print('Cognitive State:')
print('  Task:', state['task'])
print('  Top Desire:', state['bdi']['top_desire'])
print('  Plan:', state['planner']['plan'])
print('  Conscious:', state['workspace']['conscious'])
print('  Active Agents:', state['society']['active_agents'])

# Simulate execution
print('\nSimulating execution...')
agi.predict_next('Will find bug in token validation', confidence=0.7)
agi.step('Read login.py', 'Found auth logic and token validation')

agi.predict_next('Bug will be in expiration check', confidence=0.8)
agi.step('Analyze code', 'Bug found: expiration check inverted')

agi.step('Fix bug', 'Corrected expiration logic')
agi.step('Test fix', 'Tests pass')

# Evaluate
results = agi.evaluate_and_learn()
print('\nPrediction Accuracy:', results['prediction_accuracy'])
print('Total Broadcasts:', results['total_broadcasts'])

# Write unified prompt
with open('test_agi_unified.md', 'w', encoding='utf-8') as f:
    f.write(agi.to_unified_prompt())
print('\nWrote test_agi_unified.md')
