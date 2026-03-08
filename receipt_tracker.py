#!/usr/bin/env python3
"""
WORK WORK Receipt Tracker
- Stores receipt photos in folders by job
- Tracks in JSON database
- Links to jobs for reimbursement
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

RECEIPTS_DB = Path("receipts/receipts_db.json")
RECEIPTS_FOLDER = Path("receipts")

def load_db():
    """Load receipts database."""
    if not RECEIPTS_DB.exists():
        return {"schema": "work_work_receipts_v1", "receipts": [], "summary": {"total_receipts": 0, "aaron_total": 0, "luke_total": 0}}
    return json.loads(RECEIPTS_DB.read_text())

def save_db(db):
    """Save receipts database."""
    RECEIPTS_DB.parent.mkdir(exist_ok=True)
    RECEIPTS_DB.write_text(json.dumps(db, indent=2))

def add_receipt(job: str, item: str, amount: float, paid_by: str, photo_path: str = None, note: str = ""):
    """Add a receipt to the database."""
    db = load_db()
    
    # Create receipt ID
    receipt_id = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create job folder
    job_folder = RECEIPTS_FOLDER / job.replace(" ", "-").lower()
    job_folder.mkdir(exist_ok=True, parents=True)
    
    # Copy photo if provided
    photo_dest = None
    if photo_path:
        photo_ext = Path(photo_path).suffix
        photo_dest = job_folder / f"{receipt_id}{photo_ext}"
        shutil.copy(photo_path, photo_dest)
        photo_dest = str(photo_dest)
    
    # Create receipt record
    receipt = {
        "id": receipt_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "job": job,
        "item": item,
        "amount": amount,
        "paid_by": paid_by.lower(),
        "photo": photo_dest,
        "note": note,
        "reimbursed": False
    }
    
    db["receipts"].append(receipt)
    
    # Update summary
    db["summary"]["total_receipts"] += 1
    if paid_by.lower() == "aaron":
        db["summary"]["aaron_total"] += amount
    elif paid_by.lower() == "luke":
        db["summary"]["luke_total"] += amount
    
    save_db(db)
    
    return receipt

def get_job_receipts(job: str):
    """Get all receipts for a job."""
    db = load_db()
    return [r for r in db["receipts"] if r["job"].lower() == job.lower()]

def get_totals():
    """Get receipt totals by person."""
    db = load_db()
    return db["summary"]

def list_all():
    """List all receipts."""
    db = load_db()
    return db["receipts"]

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nWORK WORK Receipt Tracker\n")
        print("Usage:")
        print("  python receipt_tracker.py add [job] [item] [amount] [Aaron/Luke] [photo_path]")
        print("  python receipt_tracker.py job [job_name]")
        print("  python receipt_tracker.py totals")
        print("  python receipt_tracker.py list")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "add" and len(sys.argv) >= 6:
        job = sys.argv[2]
        item = sys.argv[3]
        amount = float(sys.argv[4].replace("$", ""))
        paid_by = sys.argv[5]
        photo = sys.argv[6] if len(sys.argv) > 6 else None
        
        receipt = add_receipt(job, item, amount, paid_by, photo)
        print(f"\n✓ Receipt added: {receipt['id']}")
        print(f"  Job: {job}")
        print(f"  Item: {item}")
        print(f"  Amount: ${amount:.2f}")
        print(f"  Paid by: {paid_by}")
        if photo:
            print(f"  Photo: {receipt['photo']}")
    
    elif cmd == "job" and len(sys.argv) >= 3:
        job = sys.argv[2]
        receipts = get_job_receipts(job)
        print(f"\nReceipts for {job}:")
        print("-" * 60)
        total = 0
        for r in receipts:
            print(f"  {r['date']} | {r['item']} | ${r['amount']:.2f} | {r['paid_by']}")
            total += r['amount']
        print(f"\nTotal: ${total:.2f}")
    
    elif cmd == "totals":
        totals = get_totals()
        print(f"\nReceipt Totals:")
        print("-" * 60)
        print(f"  Total receipts: {totals['total_receipts']}")
        print(f"  Aaron paid: ${totals['aaron_total']:.2f}")
        print(f"  Luke paid: ${totals['luke_total']:.2f}")
        print(f"  Combined: ${totals['aaron_total'] + totals['luke_total']:.2f}")
    
    elif cmd == "list":
        receipts = list_all()
        print(f"\nAll Receipts ({len(receipts)}):")
        print("-" * 60)
        for r in receipts:
            print(f"  {r['id']} | {r['date']} | {r['job']} | {r['item']} | ${r['amount']:.2f} | {r['paid_by']}")
    
    else:
        print("Unknown command. Use: add, job, totals, list")
