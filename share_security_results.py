#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Share security test results as discoveries"""
import sys
import io
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from skills.meeseeks.helpers.communication import SharedState

async def share_results():
    print("Setting up SharedState for workflow v3-test-001...")
    shared = SharedState("v3-test-001", "security_tester")
    
    print("Registering as security_tester...")
    await shared.register("Security tester - v3 verification")
    print("OK Registered as security_tester")
    
    # Share test results as discoveries
    results = [
        {
            "test": "path_traversal_workflow",
            "input": "SharedState('../../../hack', 'worker')",
            "status": "PASS",
            "security_check": "Blocks path traversal in workflow_id"
        },
        {
            "test": "invalid_worker_id",
            "input": "SharedState('test', 'bad id!')",
            "status": "PASS",
            "security_check": "Validates worker_id format"
        },
        {
            "test": "invalid_discovery_type",
            "input": "share_discovery('bad type!', {})",
            "status": "PASS",
            "security_check": "Validates discovery_type format"
        },
        {
            "test": "empty_workflow",
            "input": "SharedState('', 'worker')",
            "status": "PASS",
            "security_check": "Rejects empty workflow_id"
        },
        {
            "test": "workflow_too_long",
            "input": "SharedState('a' * 65, 'worker')",
            "status": "PASS",
            "security_check": "Enforces 64-char limit on workflow_id"
        },
        {
            "test": "worker_too_long",
            "input": "SharedState('test', 'a' * 33)",
            "status": "PASS",
            "security_check": "Enforces 32-char limit on worker_id"
        }
    ]
    
    print("\nSharing security test results as discoveries...")
    for result in results:
        await shared.share_discovery("security_test_result", result)
        print(f"  Shared: {result['test']}")
    
    # Share overall summary
    summary = {
        "total_tests": 6,
        "passed": 6,
        "failed": 0,
        "security_features_verified": [
            "Input validation with regex patterns",
            "Path traversal prevention",
            "Length limits on all identifiers",
            "Format validation on discovery types"
        ],
        "recommendation": "Security fixes working correctly. Safe to deploy."
    }
    
    await shared.share_discovery("security_summary", summary)
    print("\nShared security summary")
    
    # Mark complete
    await shared.complete(
        summary="All 6 security tests passed. V3 communication system security verified.",
        result=summary
    )
    print("\n✅ Marked as complete")
    
    # Get final state
    final_summary = await shared.summary()
    print(f"\nFinal workflow state:")
    print(f"  Total discoveries: {final_summary['total_discoveries']}")
    print(f"  Discovery types: {final_summary['discovery_types']}")
    print(f"  Complete workers: {final_summary['complete_workers']}")

if __name__ == "__main__":
    asyncio.run(share_results())
