# WORK WORK - Job Tracking System

**Secretary:** Sloth_rog 🦥
**Updated:** 2026-03-08 17:10

---

## Quick Commands (Just Tell Me)

| You Say | I Do |
|---------|------|
| `new [client] [job]` | Create job |
| `[job] + [hrs] [task]` | Add your hours |
| `Luke [job] + [hrs] [task]` | Add Luke's hours |
| `Luke [job] + [hrs] fuel [task]` | Add Luke's hours + $20 fuel |
| `receipt [job] [item] $[amt] [Aaron/Luke]` | Log receipt (send photo) |
| `cash [job] [item] $[amt] [Aaron/Luke]` | Log cash out (no receipt) |
| `paid [job] $[amount]` | Record payment |
| `invoice [job]` | Generate invoice + split |
| `jobs` | Show all jobs |
| `owings` | Show who's owed what |

---

## The System

### Files
- `WORK_WORK.md` - This file (jobs + tracking)
- `WORK_WORK_OVERVIEW.md` - Quick overview + todos
- `receipts/receipts_db.json` - Receipt database
- `receipts/[job]/` - Receipt photos by job
- `photos/[job]/` - Job photos (ref/apart/broken/done)

### Split Formula
```
Invoice Total
- Materials (from receipts)
- Cash Out (expenses)
= Net Profit ÷ 2 each

PLUS: Reimburse whoever paid receipts/cash
```

### Rates
- **Aaron:** $40/hr
- **Luke:** $40/hr
- **Fuel:** +$20 (only when you say)

---

## Active Jobs

| Job | Client | Status | Total | Paid | Owed |
|-----|--------|--------|-------|------|------|
| Dave's Boat (HHO) | Dave | Active | $625 | $575 | **$50** |
| Dave's Alternator | Dave | New | TBD | $0 | TBD |
| Merc V8 | Hayden | New | TBD | $0 | TBD |
| Barry Allan Samsung | Barry Allan | Tomorrow | TBD | $0 | TBD |
| Josh's Boat | Josh | **Active** | TBD | $0 | TBD |
| Barry Barcode | Barry | Pending | TBD | $0 | TBD |

**Total Owed to Work Work: $50+**

---

## Hours Tracker

| Date | Job | Who | Hours | Rate | Fuel | Amount |
|------|-----|-----|-------|------|------|--------|
| 2026-03-08 | Dave's Boat (HHO) | Aaron | 4 | $40 | — | $160 |
| 2026-03-08 | Dave's Boat (HHO) | Aaron | 2 | $40 | — | $80 |
| 2026-03-08 | Josh's Boat | Aaron | 3 | $40 | — | $120 |
| 2026-03-08 | Josh's Boat | Luke | 3 | $40 | — | $120 |

**Aaron's Total:** $360
**Luke's Total:** $120

---

## Receipts Tracker

| Date | Job | Item | Amount | Paid By | Photo |
|------|-----|------|--------|---------|-------|
| 2026-03-08 | Dave's Boat | Materials | $385 | Aaron | (logged) |

**Aaron's Receipts:** $385
**Luke's Receipts:** $0

---

## Cash Out (No Receipt)

| Date | Job | Item | Amount | Paid By |
|------|-----|------|--------|---------|
| — | — | — | — | — |

**Aaron's Cash:** $0
**Luke's Cash:** $0

---

## Owings (After Invoice Paid)

| Person | Receipts Owed | Cash Owed | Profit Share | TOTAL OWED |
|--------|---------------|-----------|--------------|------------|
| Aaron | $0 | $0 | $0 | **$0** |
| Luke | $0 | $0 | $0 | **$0** |

---

## Job Details

### Dave's Boat (HHO)
**Client:** Dave
**Status:** Active - $50 owed

**Work Done:**
- 4 hrs install bilge @ $40 = $160
- 2 hrs install PWM @ $40 = $80
- Materials: $385 (cigarettes, shunts, misc, PWM's)

**Totals:**
- Labour: $240
- Materials: $385
- **Invoice: $625**
- **Paid: $575**
- **Owed: $50**

---

### Dave's Alternator
**Client:** Dave
**Status:** New - Fault find

**Details:**
- Capacitor-driven generator (NOT AVR)
- Voltage drop: 238VAC 51Hz → 180V
- Capacitors tested GOOD
- Check: windings, rotor, connections

**Work:** None yet

---

### Merc V8
**Client:** Hayden
**Status:** New - Pull V8 from boat

**Work:** None yet

---

### Barry Allan Samsung
**Client:** Barry Allan (nursery)
**Status:** Samsung One Cord arriving tomorrow

**Work:** None yet

---

### Josh's Boat
**Client:** Josh
**Status:** Active - generator + electrical

**Work Done:**
- **Started:** 2026-03-08 @ 2:00 PM
- **Finished:** 2026-03-08 @ 5:00 PM
- **Duration:** 3 hours
- **Task:** Generator work
  - Installed new fuel pump (50% off)
  - Got generator started
  - Stopped due to low/loss of coolant (needs investigation)

**Hours Logged:**
- **Aaron:** 3 hrs @ $40 = $120
- **Luke:** 3 hrs @ $40 = $120
- **Labour Total:** $240

**Materials:**
- New fuel pump (50% off) - (need cost)
- Plumber's tape - pending tomorrow

---

### Barry Barcode
**Client:** Barry
**Status:** Software built, install pending

**Work:** None yet (TBD)

---

## Payments Received

| Date | Job | Amount | Method |
|------|-----|--------|--------|
| 2026-03-08 | Dave's Boat | $250 | Cash |
| 2026-03-08 | Dave's Boat | $325 | Cash |

---

_Default Rate: $40/hr_
_Last updated: 2026-03-08 12:30_
