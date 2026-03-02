import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")
import asyncio
from skills.meeseeks.helpers.communication import SharedState
import os

async def main():
    shared = SharedState("real-review-001", "reviewer_design")
    await shared.register("Design/quality reviewer")
    
    # Read the target file
    target = "C:/Users/aaron/.openclaw/workspace/skills/meeseeks/helpers/communication.py"
    with open(target, 'r', encoding='utf-8') as f:
        code = f.read()
    lines = code.split('\n')
    
    await shared.update_status(progress=25, lines_reviewed=len(lines))
    
    # Design analysis
    issues = []
    
    # Check for type hints
    if ':' in code and '->' in code:
        issues.append({'type': 'positive', 'issue': 'Uses type hints'})
    
    # Check for docstrings
    if '"""' in code or "'''" in code:
        issues.append({'type': 'positive', 'issue': 'Has docstrings'})
    
    # Check for error handling
    try_count = code.count('try:')
    if try_count > 0:
        issues.append({'type': 'positive', 'issue': f'Has {try_count} try/except blocks'})
    else:
        issues.append({'type': 'warning', 'issue': 'No error handling - file operations could fail'})
    
    # Check API design
    async_methods = code.count('async def')
    issues.append({'type': 'info', 'issue': f'{async_methods} async methods - good for I/O'})
    
    # Check for Optional types
    if 'Optional' in code:
        issues.append({'type': 'positive', 'issue': 'Uses Optional for nullable types'})
    
    # Share each finding
    for issue in issues:
        await shared.share_discovery('design_review', issue)
    
    await shared.update_status(progress=100, issues_found=len(issues))
    await shared.complete(summary=f'Design review complete: {len(issues)} findings')
    
    # Get summary
    summary = await shared.summary()
    print(f'Review complete: {summary}')

asyncio.run(main())
