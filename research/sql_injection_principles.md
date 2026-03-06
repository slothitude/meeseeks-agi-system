# SQL Injection - AGI Learning Guide

## Core Concept

**SQL Injection** = Inserting SQL commands via user input to manipulate database queries.

**The Meta-Principle:**
> "SQL makes no real distinction between the control and data planes"

This is THE key insight. The database doesn't know what's "supposed" to be data vs. code.

---

## The Attack Pattern

```
1. Find input vector (form field, URL param, etc.)
2. Test for vulnerability (inject a quote, see if it breaks)
3. Identify the query structure
4. Craft payload to manipulate the query
5. Extract data / Modify data / Execute commands
```

---

## Example Breakdown

### Example 1: Breaking the Query

**Normal input:** `Firstname: evil'ex`

**Resulting query:**
```sql
SELECT id, firstname, lastname FROM authors 
WHERE firstname = 'evil'ex' AND lastname ='newman'
```

**What happened:** The single quote closed the string early, leaving `ex'` as invalid SQL.

**The vulnerability:** User input treated as part of the command structure.

### Example 2: Always True Attack

**Malicious input:** `name' OR 'a'='a`

**Resulting query:**
```sql
SELECT * FROM items 
WHERE owner = 'wiley' AND itemname = 'name' OR 'a'='a';
```

**What happened:** `OR 'a'='a'` is always true, so ALL rows are returned.

**The vulnerability:** Logic manipulation through injection.

### Example 3: Multi-Statement Attack

**Malicious input:** `name'); DELETE FROM items; --`

**Resulting queries:**
```sql
SELECT * FROM items WHERE owner = 'hacker' AND itemname = 'name';
DELETE FROM items;
-- (comment ignores the rest)
```

**What happened:** Three statements executed: query, delete, comment.

**The vulnerability:** Statement separator (;) allows command chaining.

---

## AGI Principles Extracted

### 1. Context Mixing Vulnerability

**SQL doesn't distinguish data from commands.**

**AGI Lesson:** When building systems, ALWAYS separate:
- What users provide (untrusted)
- What the system executes (trusted)

**Application:** Meeseeks should treat ALL external input as potentially containing commands. Sanitize at boundaries.

### 2. The Meta-Character Problem

**A single quote `'` can change the meaning of everything.**

**AGI Lesson:** Small changes in input can have massive effects. Test edge cases.

**Application:** When Meeseeks processes input, check for:
- Quote characters
- Command separators
- Comment markers
- Escape sequences

### 3. Logic Manipulation

**`OR 'a'='a'` bypasses all filters.**

**AGI Lesson:** Tautologies are powerful. "Always true" conditions break authorization.

**Application:** When checking permissions, ensure conditions can't be OR'd into triviality.

### 4. Defense in Depth

**Multiple layers of protection:**
- Input validation (allow-list preferred)
- Parameterized queries (NEVER string concatenation)
- Least privilege database connections
- Error message sanitization

**AGI Lesson:** Never rely on a single defense. Layer protections.

---

## The Safe Pattern

```java
// VULNERABLE
String query = "SELECT * FROM items WHERE owner = '" + userName + "'";

// SAFE
String query = "SELECT * FROM items WHERE owner = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, userName);
```

**Key difference:** In the safe version, user input is NEVER part of the query structure. It's a parameter.

---

## For Meeseeks Architecture

### Input Boundary Checks

When a Meeseeks receives ANY input:

1. **What is the expected type?** (string, number, boolean)
2. **What characters are allowed?** (allow-list)
3. **Where will this be used?** (SQL, shell, file path, URL)
4. **What context-specific dangers exist?** (quotes, semicolons, etc.)

### The Parameterization Principle

**NEVER interpolate user input into commands.**

Instead:
```
1. Define the command structure (with placeholders)
2. Validate input against expected pattern
3. Bind input to placeholders
4. Execute
```

This applies to:
- SQL queries
- Shell commands
- File paths
- URLs
- Any external system

---

## Practice Targets (DVWA)

1. **Low difficulty:** No protection, direct injection
2. **Medium difficulty:** Some filtering, bypass techniques needed
3. **High difficulty:** Strong filtering, advanced bypasses
4. **Impossible:** Proper parameterization, no vulnerability

---

## Key Takeaways

1. **Data/Command Confusion** = Root cause of injection attacks
2. **Small Inputs, Big Effects** = One character can change everything
3. **Parameterization** = The universal defense
4. **Defense in Depth** = Layer protections
5. **Test Boundaries** = Every input is an attack vector

---

*Extracted from OWASP SQL Injection Guide*
*For AGI self-study*
*2026-03-06*
