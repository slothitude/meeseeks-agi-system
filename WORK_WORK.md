# WORK WORK - Job Tracking System

Secretary: Sloth_rog 🦥

---

## Quick Commands

| You say | I do |
|---------|------|
| `new job [name]` | Create new job entry |
| `[job] + [hrs] [task]` | Add labour hours |
| `[job] bought [item] $[amount]` | Add materials |
| `photo [job] [type]` | Log photo (you send image, I categorise) |
| `invoice [job]` | Generate full bill |
| `paid [job] $[amount]` | Record payment |
| `jobs` | List active jobs |
| `photos [job]` | Show all photos for job |

---

## Photo Types

| Type | Purpose |
|------|---------|
| `ref` | Reference - how it goes together |
| `apart` | Disassembly - order of parts |
| `broken` | Evidence - damaged parts |
| `done` | Completed work |
| `receipt` | Proof of purchase |

**Example:**
```
[You send photo]
You: "Dave's boat broken"
Me: Logged as broken part evidence for Dave's boat
```

---

## Photo Storage

```
photos/
├── daves-boat/
│   ├── ref/
│   │   └── 2026-03-08_wiring-before.jpg
│   ├── apart/
│   │   └── 2026-03-08_panel-removal.jpg
│   ├── broken/
│   │   └── 2026-03-08_fried-mosfet.jpg
│   └── done/
│       └── 2026-03-08_install-complete.jpg
├── joshs-boat/
│   └── ...
└── barry-barcode/
    └── ...
```

---

## Active Jobs

| Job | Status | Labour | Materials | Total | Paid | Owed | Photos |
|-----|--------|--------|-----------|-------|------|------|--------|
| Dave's Boat (HHO) | Active | $240 | $385 | $625 | $0 | $625 | 0 |
| Josh's Boat | Ongoing | TBD | TBD | TBD | $0 | TBD | 0 |
| Barry Barcode | Pending | TBD | TBD | TBD | $0 | TBD | 0 |

**Total Outstanding: $625+**

---

## Job Details

### Dave's Boat (HHO)

**Labour:**
| Date | Task | Hours | Rate | Amount |
|------|------|-------|------|--------|
| 2026-03-08 | Install bilge | 4 | $40 | $160 |
| 2026-03-08 | Install PWM | 2 | $40 | $80 |
| | **Total** | **6** | | **$240** |

**Materials:**
| Date | Item | Amount |
|------|------|--------|
| 2026-03-08 | Cigarettes + other | $130 |
| 2026-03-08 | Shunts | $95 |
| 2026-03-08 | Misc | $20 |
| 2026-03-08 | PWM's | $140 |
| | **Total** | **$385** |

**Photos:**
| Date | Type | Description | File |
|------|------|-------------|------|
| — | — | — | — |

**Summary:**
- Labour: $240
- Materials: $385
- **Total: $625**
- **Paid: $0**
- **Owed: $625**

---

### Josh's Boat

**Status:** Ongoing (generator + electrical)

**Labour:** TBD
**Materials:** TBD
**Photos:** None yet

---

### Barry Barcode

**Status:** Software built, install pending

**Labour:** TBD
**Materials:** TBD
**Photos:** None yet

---

## Payments Received

| Date | Job | Amount | Method |
|------|-----|--------|--------|
| — | — | — | — |

---

**Default Rate: $40/hr**

_Last updated: 2026-03-08 08:56_
