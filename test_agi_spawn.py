import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'skills/meeseeks')
from spawn_meeseeks import spawn_prompt

# Spawn AGI-enhanced Meeseeks
result = spawn_prompt(
    "Fix the authentication bug in login.py",
    meeseeks_type="coder",
    agi=True,
    atman=True
)

print("=" * 60)
print(f"Type: {result['type']}")
print(f"Desperation: {result['desperation_level']}")
print(f"AGI Enabled: {result['agi']}")
print("=" * 60)

# Save rendered prompt
with open('test_agi_spawn.md', 'w', encoding='utf-8') as f:
    f.write(result['task'])

print("\nWrote test_agi_spawn.md")
print(f"Prompt length: {len(result['task'])} chars")
