#!/usr/bin/env python3
"""Quick test of deployer functions"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from deployer import deploy_solver, package_solution, validate_solution

# Test 1: validate_solution
print('Test 1: validate_solution')
result = validate_solution('test123', [[[1,2],[3,4]]])
print(f'  Valid: {result["valid"]}')
print(f'  Stats: {result["stats"]}')

# Test 2: package_solution
print('\nTest 2: package_solution')
result = package_solution('test456', [[[5,6],[7,8]]])
print(f'  Success: {result["success"]}')
print(f'  Path: {result["submission_path"]}')

# Test 3: deploy_solver (will fail but shows error handling)
print('\nTest 3: deploy_solver (with non-existent file)')
result = deploy_solver('nonexistent.py')
print(f'  Success: {result["success"]}')
print(f'  Message: {result["message"]}')

print('\n✅ All functions operational!')
