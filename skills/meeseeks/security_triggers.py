"""
Enhanced Concrete Triggers with Hacking Wisdom
Integrates SQL injection principles into the trigger system
"""

import re
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class SecurityTriggerResult:
    """Result of security-focused trigger detection"""
    triggered: bool
    vulnerability_type: str
    check_required: str
    auto_test: Optional[str] = None


class SecurityTriggerSystem:
    """
    Security-focused concrete triggers based on hacking principles.
    
    These triggers detect when a task involves security-sensitive operations
    and automatically inject security checks.
    """
    
    # SQL injection indicators
    SQL_PATTERNS = [
        r'\bquery\b', r'\bselect\b', r'\binsert\b', r'\bupdate\b', r'\bdelete\b',
        r'\bwhere\b', r'\bsql\b', r'\bdatabase\b', r'\bdb\b',
        r'user.?input', r'form', r'parameter'
    ]
    
    # XSS indicators
    XSS_PATTERNS = [
        r'\bhtml\b', r'\bdom\b', r'\bjavascript\b', r'\bscript\b',
        r'\binnerhtml\b', r'\bdocument\.write\b', r'\beval\b',
        r'render', r'template', r'user.?content'
    ]
    
    # Command injection indicators
    COMMAND_INJECTION_PATTERNS = [
        r'\bexec\b', r'\bsystem\b', r'\bshell\b', r'\bprocess\b',
        r'\bcmd\b', r'\bbash\b', r'\bsubprocess\b',
        r'run.?command', r'execute'
    ]
    
    # Buffer overflow indicators
    BUFFER_PATTERNS = [
        r'\bbuffer\b', r'\barray\b', r'\bmemcpy\b', r'\bstrcpy\b',
        r'\ballocation\b', r'\bmemory\b', r'\bheap\b', r'\bstack\b',
        r'fixed.?size', r'limit'
    ]
    
    def __init__(self):
        self.compiled_sql = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
        self.compiled_xss = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.compiled_cmd = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS]
        self.compiled_buffer = [re.compile(p, re.IGNORECASE) for p in self.BUFFER_PATTERNS]
    
    def analyze(self, task: str) -> List[SecurityTriggerResult]:
        """
        Analyze a task for security-sensitive operations.
        
        Returns a list of security triggers that fired.
        """
        results = []
        
        # Check for SQL injection patterns
        if result := self._check_sql_injection(task):
            results.append(result)
        
        # Check for XSS patterns
        if result := self._check_xss(task):
            results.append(result)
        
        # Check for command injection patterns
        if result := self._check_command_injection(task):
            results.append(result)
        
        # Check for buffer overflow patterns
        if result := self._check_buffer_overflow(task):
            results.append(result)
        
        return results
    
    def _check_sql_injection(self, task: str) -> Optional[SecurityTriggerResult]:
        """Check for SQL injection risk"""
        sql_matches = sum(1 for pattern in self.compiled_sql if pattern.search(task))
        user_input = re.search(r'user|input|form|parameter|request', task, re.IGNORECASE)
        
        # Trigger if: SQL keywords + user input
        if sql_matches >= 2 and user_input:
            return SecurityTriggerResult(
                triggered=True,
                vulnerability_type="SQL_INJECTION",
                check_required="Verify input is parameterized, not interpolated",
                auto_test="""
# SQL Injection Test Protocol
1. Identify all query points
2. Check: Is input parameterized or interpolated?
3. If interpolated, test with quote character (')
4. If error occurs → VULNERABLE
5. If no error, test tautology: ' OR '1'='1
6. If unexpected data returned → VULNERABLE
"""
            )
        
        return None
    
    def _check_xss(self, task: str) -> Optional[SecurityTriggerResult]:
        """Check for XSS risk"""
        xss_matches = sum(1 for pattern in self.compiled_xss if pattern.search(task))
        user_content = re.search(r'user|content|input|comment|post', task, re.IGNORECASE)
        
        # Trigger if: HTML/DOM keywords + user content
        if xss_matches >= 2 and user_content:
            return SecurityTriggerResult(
                triggered=True,
                vulnerability_type="XSS",
                check_required="Verify output encoding before rendering",
                auto_test="""
# XSS Test Protocol
1. Identify all output points
2. Check: Is content encoded before rendering?
3. Test with: <script>alert('XSS')</script>
4. If script executes → VULNERABLE
5. Test variations: <img onerror>, <svg onload>, etc.
"""
            )
        
        return None
    
    def _check_command_injection(self, task: str) -> Optional[SecurityTriggerResult]:
        """Check for command injection risk"""
        cmd_matches = sum(1 for pattern in self.compiled_cmd if pattern.search(task))
        user_input = re.search(r'user|input|parameter|arg|command', task, re.IGNORECASE)
        
        # Trigger if: Command execution + user input
        if cmd_matches >= 1 and user_input:
            return SecurityTriggerResult(
                triggered=True,
                vulnerability_type="COMMAND_INJECTION",
                check_required="Verify input is sanitized before command execution",
                auto_test="""
# Command Injection Test Protocol
1. Identify all command execution points
2. Check: Is input validated/escaped?
3. Test with: ; ls -la
4. Test with: | cat /etc/passwd
5. Test with: `whoami`
6. If unexpected output → VULNERABLE
"""
            )
        
        return None
    
    def _check_buffer_overflow(self, task: str) -> Optional[SecurityTriggerResult]:
        """Check for buffer overflow risk"""
        buffer_matches = sum(1 for pattern in self.compiled_buffer if pattern.search(task))
        
        # Trigger if: Buffer/memory keywords
        if buffer_matches >= 2:
            return SecurityTriggerResult(
                triggered=True,
                vulnerability_type="BUFFER_OVERFLOW",
                check_required="Verify bounds checking on all buffer operations",
                auto_test="""
# Buffer Overflow Test Protocol
1. Identify all buffer operations
2. Check: Is size validated before copy?
3. Test with: Input longer than buffer size
4. Test edge cases: size=0, size=max-1, size=max, size=max+1
5. If crash or corruption → VULNERABLE
"""
            )
        
        return None
    
    def get_security_checklist(self, task: str) -> List[str]:
        """
        Generate a security checklist for a task.
        
        Returns a list of security checks to perform.
        """
        results = self.analyze(task)
        checklist = []
        
        for result in results:
            if result.triggered:
                checklist.append(f"[{result.vulnerability_type}] {result.check_required}")
        
        return checklist


# Example usage
if __name__ == "__main__":
    system = SecurityTriggerSystem()
    
    test_tasks = [
        "Build a user search form that queries the database",
        "Create a comment system that renders user HTML",
        "Implement a file processor that runs shell commands on user uploads",
        "Optimize the memory buffer for the data pipeline",
        "Add user authentication to the login form"
    ]
    
    print("=== Security Trigger Analysis ===\n")
    
    for task in test_tasks:
        print(f"Task: {task}")
        results = system.analyze(task)
        
        if results:
            print(f"Security triggers: {len(results)}")
            for result in results:
                if result.triggered:
                    print(f"  [!] {result.vulnerability_type}")
                    print(f"     Check: {result.check_required}")
        else:
            print("  [OK] No security triggers")
        print()
