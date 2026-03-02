#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security tests for v3 communication system"""
import sys
import io
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from skills.meeseeks.helpers.communication import SharedState, ValidationError

async def run_security_tests():
    print("=" * 60)
    print("SECURITY TESTS FOR V3 COMMUNICATION SYSTEM")
    print("=" * 60)
    
    results = []
    
    # TEST 1: Path traversal in workflow_id
    print("\n[TEST 1] Path traversal in workflow_id")
    print("Input: SharedState('../../../hack', 'worker')")
    try:
        bad = SharedState("../../../hack", "worker")
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("path_traversal_workflow", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        print(f"   Error: {e}")
        results.append(("path_traversal_workflow", "PASS", str(e)))
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
        results.append(("path_traversal_workflow", "FAIL", f"Wrong exception: {type(e).__name__}"))
    
    # TEST 2: Invalid worker_id (spaces and special chars)
    print("\n[TEST 2] Invalid worker_id")
    print("Input: SharedState('test', 'bad id!')")
    try:
        bad = SharedState("test", "bad id!")
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("invalid_worker_id", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        print(f"   Error: {e}")
        results.append(("invalid_worker_id", "PASS", str(e)))
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
        results.append(("invalid_worker_id", "FAIL", f"Wrong exception: {type(e).__name__}"))
    
    # TEST 3: Invalid discovery_type
    print("\n[TEST 3] Invalid discovery_type")
    print("Input: await shared.share_discovery('bad type!', {})")
    try:
        shared = SharedState("test_workflow", "test_worker")
        await shared.register("Security test")
        await shared.share_discovery("bad type!", {})
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("invalid_discovery_type", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        print(f"   Error: {e}")
        results.append(("invalid_discovery_type", "PASS", str(e)))
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
        results.append(("invalid_discovery_type", "FAIL", f"Wrong exception: {type(e).__name__}"))
    
    # TEST 4: Additional edge cases
    print("\n[TEST 4] Empty workflow_id")
    try:
        bad = SharedState("", "worker")
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("empty_workflow", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        results.append(("empty_workflow", "PASS", str(e)))
    
    print("\n[TEST 5] Workflow_id too long (>64 chars)")
    try:
        bad = SharedState("a" * 65, "worker")
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("workflow_too_long", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        results.append(("workflow_too_long", "PASS", str(e)))
    
    print("\n[TEST 6] Worker_id too long (>32 chars)")
    try:
        bad = SharedState("test", "a" * 33)
        print("❌ FAIL: Should have raised ValidationError")
        results.append(("worker_too_long", "FAIL", "No exception raised"))
    except ValidationError as e:
        print(f"✅ PASS: Caught ValidationError")
        results.append(("worker_too_long", "PASS", str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for test_name, status, detail in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {test_name}: {status}")
        if status == "FAIL":
            print(f"   Detail: {detail}")
    
    print("\n" + "=" * 60)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_security_tests())
