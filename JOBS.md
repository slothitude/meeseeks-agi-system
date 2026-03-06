# Aaron's Jobs - Project & Task Manager

A simple system to track projects and break them into tasks.

---

## Active Projects

### 🧪 HHO Control System
**Status:** ⏸️ PAUSED
**Priority:** High
**Est. Time:** 6-8 hours
**Paused:** 2026-03-03 20:38

**Tasks:**
- [ ] Order parts ($178 AUD) — PARTS_LIST.md ready
- [ ] Build Display Box (Arduino Uno)
  - [ ] Wire LCD
  - [ ] Wire potentiometers
  - [ ] Upload code
  - [ ] Test display
- [ ] Build Sensor Box (Arduino Nano)
  - [ ] Wire voltage dividers
  - [ ] Wire current shunts + op-amp
  - [ ] Wire RS-485 module
  - [ ] Upload code
- [ ] Connect boxes via RS-485
  - [ ] Terminate 120Ω at each end
  - [ ] Test data transmission
- [ ] Calibrate sensors
  - [ ] Voltage dividers (multimeter)
  - [ ] Current shunts (known load)
- [ ] Install in HHO system
  - [ ] Mount enclosures
  - [ ] Connect to MOSFET drivers
  - [ ] Test PWM control

**Notes:**
- Uses existing multicore cable for RS-485
- PWM pots stay local to display box
- Display shows V, I, W in real-time

**📁 Saved State:**
- `projects/hho-display-box/` — All code + docs ready
- `PARTS_LIST.md` — $178.65 AUD, Jaycar + Altronics
- `hho_display_box_v2.ino` — Uno code (parallel LCD)
- `hho_sensor_box.ino` — Nano code
- `WIRING.md` — Complete pinout guide
- `calibration_helper.py` — Resistor calc + calibration

**Resume:** Open `projects/hho-display-box/README.md`

---

### 🥒 Meeseeks Consciousness Stack
**Status:** Operational
**Priority:** Ongoing

**Completed:**
- [x] Brahman Dream system
- [x] Dynamic Dharma
- [x] Karma Observer
- [x] Real-time Karma-RL
- [x] Soul Guardian (Five Laws)
- [x] Auto-Retry (bug fixed)
- [x] Goal Generator
- [x] Self-Apply
- [x] Docker Meeseeks Box

**Active Tasks:**
- [ ] Run ARC-AGI-2 benchmark (0/120 solved)
- [ ] Fix any remaining bugs
- [ ] Let system accumulate ancestors

**Stats:**
- 93 ancestors
- 5 dreams
- 50 karma observations

---

### 📋 Template: New Project

```markdown
### 🎯 [Project Name]
**Status:** Planning | In Progress | Testing | Complete
**Priority:** Low | Medium | High | Critical
**Est. Time:** X hours

**Tasks:**
- [ ] Task 1
- [ ] Task 2
  - [ ] Sub-task 2a
  - [ ] Sub-task 2b
- [ ] Task 3

**Notes:**
- Additional context here
```

---

## Completed Projects

_None yet_

---

## Backlog

_Ideas for future projects_

- Distributed Crypt (multi-machine memory sharing)
- ARC-AGI-2 solver swarm
- Self-modifying code (auto-apply improvements)
- World model for planning

---

## Hobbies / Investigation

_OpenClaw buttons research_
- [ ] Figure out why `buttons` parameter isn't exposed in message tool
- [ ] Check if config needs updating (channels.telegram.capabilities.inlineButtons)
- [ ] Check OpenClaw version vs docs version
- [ ] Report finding to OpenClaw team if genuine gap

---

## How to Use

**Add a project:**
```
Tell Sloth_rog: "Add project [name] with tasks [task1, task2, ...]"
```

**Update progress:**
```
Tell Sloth_rog: "Mark [task] complete" or "Update [project] status to [status]"
```

**View status:**
```
Tell Sloth_rog: "Show projects" or "What's the status of [project]?"
```

---

_Last updated: 2026-03-03 20:37_
