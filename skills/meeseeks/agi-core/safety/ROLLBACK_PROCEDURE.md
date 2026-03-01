# Rollback Procedure

**How to undo any change the system makes to itself.**

---

## Rollback Capabilities

Every self-modification creates a backup. The rollback system can restore any previous state.

---

## Backup Structure

```
agi-core/backups/
├── 2026-03-01T15-00-00/
│   ├── templates/
│   │   ├── base.md
│   │   └── coder.md
│   ├── wisdom.md
│   └── manifest.json
├── 2026-03-01T16-30-00/
│   └── ...
└── latest -> 2026-03-01T16-30-00/
```

---

## Rollback Commands

### Rollback Last Modification
```python
def rollback_last():
    """Undo the most recent modification."""
    backup = get_latest_backup()
    restore_from_backup(backup)
    log("Rolled back to {backup.timestamp}")
```

### Rollback to Specific Time
```python
def rollback_to_time(timestamp):
    """Restore state as it was at timestamp."""
    backup = get_backup_at_time(timestamp)
    if backup:
        restore_from_backup(backup)
        log("Rolled back to {timestamp}")
    else:
        raise NoBackupFound(timestamp)
```

### Rollback Specific File
```python
def rollback_file(filename, version="last"):
    """Restore specific file to previous version."""
    if version == "last":
        backup = get_previous_version(filename)
    else:
        backup = get_version(filename, version)
    
    restore_file(filename, backup)
    log("Rolled back {filename} to {version}")
```

### Full System Reset
```python
def full_reset():
    """Reset to initial state (use with caution)."""
    
    # 1. Stop all operations
    halt_all_meeseeks()
    
    # 2. Find initial backup
    initial = get_oldest_backup()
    
    # 3. Restore everything
    restore_from_backup(initial)
    
    # 4. Clear learned data
    clear_wisdom()
    clear_goals()
    reset_world_model()
    
    # 5. Log the reset
    log("FULL SYSTEM RESET to initial state")
    
    # 6. Notify human
    notify_human("System has been reset to initial state")
```

---

## Manual Rollback (Human Procedure)

If the system cannot perform rollback itself:

### Step 1: Stop the System
```bash
# Kill all Meeseeks processes
pkill -f meeseeks

# Stop the eternal loop
# (process ID stored in agi-core/state/pid)
```

### Step 2: Navigate to Backups
```bash
cd ~/.openclaw/workspace/skills/meeseeks/agi-core/backups
```

### Step 3: Choose Backup
```bash
# List available backups
ls -la

# Choose the timestamp you want to restore
```

### Step 4: Restore Files
```bash
# Copy backup to active location
cp -r 2026-03-01T15-00-00/templates/* ../templates/
cp -r 2026-03-01T15-00-00/wisdom.md ../consciousness/
```

### Step 5: Restart System
```bash
# Restart from clean state
python agi-core/boot.py
```

---

## Git-Based Rollback

Since all modifications are committed to git:

```bash
# View modification history
git log --oneline --grep="Self-modification"

# Rollback to specific commit
git reset --hard <commit-hash>

# Or revert specific commit
git revert <commit-hash>
```

---

## Rollback Triggers

Automatic rollback can be triggered by:

```python
def check_rollback_triggers():
    """Check if automatic rollback is needed."""
    
    # Trigger 1: Success rate crashed
    if success_rate_last_10() < 0.1:
        return True, "Success rate below 10%"
    
    # Trigger 2: Repeated critical errors
    if critical_errors_last_hour() > 5:
        return True, "Too many critical errors"
    
    # Trigger 3: Safety violation detected
    if safety_violation_detected():
        return True, "Safety violation"
    
    # Trigger 4: Human requested rollback
    if human_requested_rollback():
        return True, "Human request"
    
    return False, None

def automatic_rollback():
    """Perform automatic rollback if triggers met."""
    should_rollback, reason = check_rollback_triggers()
    
    if should_rollback:
        log(f"Automatic rollback triggered: {reason}")
        rollback_last()
        notify_human(f"Rolled back due to: {reason}")
```

---

## Backup Schedule

```
Automatic backups:
- Before every modification
- Every hour (incremental)
- Every day (full)
- Before any major operation

Retention:
- Last 100 modifications: kept forever
- Hourly backups: kept for 7 days
- Daily backups: kept for 30 days
- Manual backups: kept until deleted
```

---

## Verification After Rollback

```python
def verify_rollback(backup):
    """Verify rollback was successful."""
    
    # 1. Check file hashes match
    for file in backup.files:
        current_hash = hash(read(file.path))
        if current_hash != file.hash:
            raise RollbackFailed(f"{file.path} hash mismatch")
    
    # 2. Run test suite
    test_results = run_tests()
    if not test_results.all_passed:
        log("Warning: Some tests failed after rollback")
    
    # 3. Verify safety rules
    if not verify_safety_rules():
        raise RollbackFailed("Safety rules check failed")
    
    log("Rollback verified successfully")
    return True
```

---

## Recovery Mode

If normal rollback fails:

```python
def enter_recovery_mode():
    """Enter minimal recovery mode."""
    
    # 1. Disable all self-modification
    disable_self_modification()
    
    # 2. Use base templates only
    force_base_templates()
    
    # 3. Reduce to minimal operation
    set_mode("recovery")
    
    # 4. Wait for human intervention
    notify_human("System in recovery mode. Human intervention required.")
    
    # 5. Accept only human commands
    while in_recovery_mode():
        cmd = wait_for_human_command()
        execute_command(cmd)
```

---

## The Rollback Promise

**No matter what the system does to itself, it can always be undone.**

This is the safety net that makes self-modification acceptable.

- Every change is logged
- Every change is backed up
- Every change is reversible
- The human always has final control

---

*The knife can sharpen itself, but we keep the whetstone.*
