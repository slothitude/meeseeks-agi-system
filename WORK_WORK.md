# WORK WORK - Job Tracking System

**Electrical · Electronics · Programming · Marine Engineering**

**Secretary:** Sloth_rog 🦥
**Updated:** 2026-03-08 19:41

---

## 📊 Quick Totals

| Job | Labour | Materials | Fuel | Total | Paid | Owed |
|-----|--------|-----------|-----|-------|------|------|
| Dave's Boat | $240 | $385 | $0 | $625 | $575 | **$50** |
| Dave's Alternator | $52 | $0 | $20 | $72 | $0 | **$72** |
| Josh's Boat | $400 | $21 | $20 | $441 | $0 | **$441** |
| Yugi | $120 | $80 | $20 | $220 | $0 | **$220** |
| **TOTAL** | **$812** | **$486** | **$60** | **$1358** | **$575** | **$783** |

**Outstanding: $783**
- Dave's Boat: $50
- Dave's Alternator: $72 (in progress)
- Josh: $441 (pending invoice)
- Yugi: $220

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

### Payment Method
**Australia Post Everyday Mastercard** (Business Float)
- **Type:** Prepaid Mastercard with BSB/Account
- **BSB:** 016-964
- **Account:** 114998156
- **Accepts:** Direct transfers from clients (like bank account)
- **Cash Access:** ATM ($3.50 fee) or Post Office Bank@Post (5 mins away)
- **Security:** No link to bank account, Mastercard Zero Liability
- **App:** Real-time balance, transaction monitoring
- **Scraper:** `auspost_balance.py` - returns live balance as JSON

**How it works:**
- Aaron loads job income onto card
- OpenClaw tracks each person's share
- Pay Luke via card handoff or ATM/PO cash
- Both parties know where they stand

**No ABN** - intentionally informal, option to formalise later

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

| Job | Client | Status | Labour | Materials | Total | Paid | Owed |
|-----|--------|--------|--------|-----------|-------|------|------|
| Dave's Boat (HHO) | Dave | **$50 owed** | $240 | $385 | $625 | $575 | **$50** |
| Josh's Boat | Josh | Active | $400 | $21 | $441 | $0 | **$441** |
| Yugi | Yugi | Active | $120 | $80 | $220 | $0 | **$220** |
| Dave's Alternator | Dave | Active | $52 | $0 | $52 | $0 | **$52** |
| Merc V8 | Hayden | New | $0 | $0 | TBD | $0 | TBD |
| Barry Allan Samsung | Barry Allan | Tomorrow | $0 | $0 | TBD | $0 | TBD |
| Barry Barcode | Barry | Pending | $0 | $0 | TBD | $0 | TBD |

**Total Outstanding: $701** ($50 Dave + $431 Josh + $220 Yugi)

---

## Current Owings (Live)

### Josh's Boat - Not Yet Invoiced
| Person | Hours | Labour | Fuel | Materials | Cash Out | Admin | Parts | TOTAL OWED |
|--------|-------|--------|-----|-----------|----------|-------|-------|------------|
| Aaron | 5 | $200 | $20 | $0 | $37.95 | $10 | $10 | **$277.95** |
| Luke | 5 | $200 | $0 | $0 | $0 | $0 | $0 | **$200** |
| **Total** | 10 | $400 | $20 | $0 | $37.95 | $10 | $10 | **$477.95** |

*Invoice not generated yet. Will split 50/50 when invoiced.*
*Aaron's cash out: $37.95 (card + deposit + fuel plug)*
*Admin fee: $10 (Aaron)*
*Parts: $10 (fuel plug)*

### Dave's Boat - Invoiced
| Person | Status |
|--------|--------|
| Aaron | $50 owed from Dave |
| Luke | $0 |

**Grand Total Owed to Work Work: $783**
- Dave's Boat: $50
- Dave's Alternator: $72 (in progress)
- Josh owes: $441 (not yet invoiced)

---

## Hours Tracker

| Date | Job | Who | Hours | Rate | Fuel | Amount |
|------|-----|-----|-------|------|------|--------|
| 2026-03-08 | Dave's Boat (HHO) | Aaron | 4 | $40 | — | $160 |
| 2026-03-08 | Dave's Boat (HHO) | Aaron | 2 | $40 | — | $80 |
| 2026-03-08 | Josh's Boat | Aaron | 3 | $40 | $20 | $140 |
| 2026-03-08 | Josh's Boat | Luke | 3 | $40 | — | $120 |
| 2026-03-09 | Josh's Boat | Aaron | 2 | $40 | — | $80 |
| 2026-03-09 | Josh's Boat | Luke | 2 | $40 | — | $80 |
| 2026-03-10 | Yugi | Aaron | 2 | $40 | $20 | $100 |
| 2026-03-10 | Yugi | Luke | 1 | $40 | — | $40 |
| 2026-03-10 | Dave's Alternator | Aaron | 1.3 | $40 | $20 | $72 |

**Aaron's Total:** $632
**Luke's Total:** $240

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
| 2026-03-09 | Work Work | Card + Deposit | $27.95 | Aaron |
| 2026-03-10 | Josh's Boat | Fuel plug | $10 | Aaron |

**Aaron's Cash:** $37.95
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
**Status:** Active - Diagnostic

**Sessions:**
- Morning: 8:30-9:49 AM (1h 19m) - winding check, cap wiring
- Afternoon: 1:59 PM - ongoing

**Running Total:**
- Labour: $52 (1.3 hrs @ $40)
- Fuel: $20
- **Total: $72**

**Details:**
- Capacitor-driven generator (NOT AVR)
- Voltage drop: 238VAC 51Hz → 180V
- Windings: All 0.5Ω balanced (delta, 6 wires 3+3)
- Cap wiring done
- Next: Pull genny, hunt cap/line fault

**Photo:** `photos/dave_alternator/2026-03-10_0845_ref.jpg`

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

**Running Total:**
- Labour: $400 (Aaron $200 + Luke $200)
- Fuel: $20 (Aaron)
- Materials: $11 (Aaron)
- Admin: $10 (Aaron)
- Parts: $10 (Aaron - fuel plug)
- **Total: $441** (not yet invoiced)

**Work Done:**
- **Started:** 2026-03-08 @ 2:00 PM
- **Finished:** 2026-03-08 @ 5:00 PM
- **Duration:** 3 hours
- **Task:** Generator + bilge work
  - Installed new fuel pump (50% off)
  - Got generator started
  - Stopped due to low/loss of coolant (needs investigation)
  - Found bilge pump float not secured (needs securing)

**Pending:**
- Plumber's tape (tomorrow)
- Coolant issue investigation
- Secure bilge pump float

**Invoice Generated:** 2026-03-08
- Invoice #: WW-20260308
- Total: $441
- Balance: $441 (pending payment)

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
