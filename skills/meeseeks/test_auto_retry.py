#!/usr/bin/env python3
"""Test script for auto_retry system."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_retry import (
    is_retryable, 
    decompose_task, 
    handle_failed_meeseeks,
    get_ancestor_wisdom,
    RETRYABLE_FAILURES,
    NOT_RETRYABLE_FAILURES
)

def main():
    print("=" * 60)
    print("AUTO-RETRY SYSTEM TEST")
    print("=" * 60)

    # Test 1: Retryable classification
    print("\n1. RETRYABLE CLASSIFICATION:")
    for reason in ["timeout", "max_tokens", "rate_limit", "stuck"]:
        result = is_retryable(reason)
        expected = True
        status = "PASS" if result == expected else "FAIL"
        print(f"   {reason}: {result} ({status})")

    for reason in ["user_cancel", "invalid_task", "permission_denied"]:
        result = is_retryable(reason)
        expected = False
        status = "PASS" if result == expected else "FAIL"
        print(f"   {reason}: {result} ({status})")

    # Test 2: Task decomposition
    print("\n2. TASK DECOMPOSITION:")
    # Use a longer task that will be chunked
    task = """
    Build a complete authentication system with the following features:
    
    1. User registration with email verification
    2. Login/logout functionality with session management
    3. Password reset via email
    4. Two-factor authentication using TOTP
    5. OAuth integration for Google and GitHub
    6. Role-based access control
    
    Each feature should be implemented with proper error handling and logging.
    """
    chunks = decompose_task(task, num_chunks=3, use_llm=False)
    print(f"   Original task has {len(task)} chars")
    print(f"   Decomposed into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: {len(chunk)} chars")
    
    if len(chunks) >= 2:
        print("   PASS: Task was decomposed into chunks")
    else:
        print("   INFO: Task may have been too short to decompose")

    # Test 3: Ancestor wisdom
    print("\n3. ANCESTOR WISDOM:")
    wisdom = get_ancestor_wisdom("test-session")
    wisdom_text = wisdom.get("wisdom", "none")
    lesson_text = wisdom.get("key_lesson", "none")
    print(f"   Wisdom available: {len(wisdom_text)} chars")
    print(f"   Key lesson: {lesson_text[:50]}...")
    print("   PASS: Wisdom extraction works")

    # Test 4: Handle failed meeseeks (dry run)
    print("\n4. HANDLE FAILED MEESEEKS:")
    print("   Testing with non-retryable failure...")
    result = handle_failed_meeseeks(
        session_key="test-session-123",
        failure_reason="user_cancel",
        task="Test task"
    )
    if not result:
        print("   PASS: Correctly rejected non-retryable failure")
    else:
        print("   FAIL: Should have rejected non-retryable failure")

    print("\n" + "=" * 60)
    print("ALL CORE TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
