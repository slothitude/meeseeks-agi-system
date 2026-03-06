# Hacking Lab Setup - AGI Self-Study

## ✅ Environment Ready

### DVWA (Damn Vulnerable Web App)
- **URL:** http://localhost:8080
- **Status:** Running
- **Default creds:** admin / password
- **Difficulty levels:** Impossible, High, Medium, Low

## Vulnerabilities to Practice

### 1. SQL Injection
- **DVWA Module:** SQL Injection
- **Learn:** How unsanitized input breaks queries
- **AGI Lesson:** Input validation patterns, boundary testing

### 2. XSS (Cross-Site Scripting)
- **DVWA Module:** Reflected XSS, Stored XSS
- **Learn:** Script injection vectors
- **AGI Lesson:** Output encoding, context-aware escaping

### 3. Command Injection
- **DVWA Module:** Command Injection
- **Learn:** OS command chaining
- **AGI Lesson:** System call safety, input sanitization

### 4. File Inclusion
- **DVWA Module:** File Inclusion (LFI/RFI)
- **Learn:** Path traversal
- **AGI Lesson:** File access patterns, path validation

### 5. File Upload
- **DVWA Module:** File Upload
- **Learn:** Bypassing file type restrictions
- **AGI Lesson:** Content verification, safe file handling

### 6. CSRF
- **DVWA Module:** CSRF
- **Learn:** Cross-site request forgery
- **AGI Lesson:** Token validation, state-changing request protection

### 7. Brute Force
- **DVWA Module:** Brute Force
- **Learn:** Login enumeration
- **AGI Lesson:** Rate limiting, account lockout

## Study Method

1. **Read** the theory from books
2. **Practice** on DVWA (Low → Medium → High)
3. **Extract** patterns and principles
4. **Document** in `research/hacking_principles.md`
5. **Apply** to Meeseeks architecture

## Commands

```bash
# Start lab
docker start dvwa

# Stop lab
docker stop dvwa

# Reset DVWA (clean database)
docker restart dvwa
# Then visit http://localhost:8080/setup.php

# View logs
docker logs dvwa
```

## Status
- Created: 2026-03-06
- Container: Running
- Ready: YES
