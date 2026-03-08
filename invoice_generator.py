#!/usr/bin/env python3
"""
WORK WORK Invoice Generator
Automatically generates invoices from WORK_WORK.md data
"""

import re
from datetime import datetime
from pathlib import Path

def parse_job_data(job_name):
    """Parse WORK_WORK.md to extract job data."""
    work_file = Path("WORK_WORK.md")
    if not work_file.exists():
        return None
    
    content = work_file.read_text()
    
    # Find the job section
    job_pattern = rf"### {re.escape(job_name)}.*?(?=###|\Z)"
    job_match = re.search(job_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not job_match:
        return None
    
    job_section = job_match.group(0)
    
    data = {
        'name': job_name,
        'client': '',
        'status': '',
        'labour': [],
        'labour_total': 0,
        'materials': [],
        'materials_total': 0,
        'payments': [],
        'paid_total': 0,
        'total': 0,
        'owed': 0
    }
    
    # Extract client
    client_match = re.search(r'\*\*Client:\*\*\s*(.+)', job_section)
    if client_match:
        data['client'] = client_match.group(1).strip()
    
    # Extract status
    status_match = re.search(r'\*\*Status:\*\*\s*(.+)', job_section)
    if status_match:
        data['status'] = status_match.group(1).strip()
    
    # Extract labour entries
    labour_pattern = r'\|\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\s*\|\s*(.+?)\s*\|\s*([\d.]+)\s*\|\s*\$?([\d.]+)\s*\|\s*\$?([\d.]+)\s*\|'
    for match in re.finditer(labour_pattern, job_section):
        data['labour'].append({
            'date': match.group(1),
            'task': match.group(2).strip(),
            'hours': float(match.group(3)),
            'rate': float(match.group(4)),
            'amount': float(match.group(5))
        })
        data['labour_total'] += float(match.group(5))
    
    # Extract materials entries
    materials_pattern = r'\|\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\s*\|\s*(.+?)\s*\|\s*\$?([\d.]+)\s*\|'
    for match in re.finditer(materials_pattern, job_section):
        # Skip if this is a labour row (has more columns)
        if match.group(0).count('|') > 4:
            continue
        data['materials'].append({
            'date': match.group(1),
            'item': match.group(2).strip(),
            'amount': float(match.group(3))
        })
        data['materials_total'] += float(match.group(3))
    
    # Extract summary totals
    total_match = re.search(r'\*\*Total:\*\*\s*\$?([\d.]+)', job_section)
    if total_match:
        data['total'] = float(total_match.group(1))
    
    paid_match = re.search(r'\*\*Paid:\*\*\s*\$?([\d.]+)', job_section)
    if paid_match:
        data['paid_total'] = float(paid_match.group(1))
    
    owed_match = re.search(r'\*\*Owed:\*\*\s*\$?([\d.]+)', job_section)
    if owed_match:
        data['owed'] = float(owed_match.group(1))
    
    return data

def generate_invoice(job_name, include_split=False):
    """Generate an invoice for a job."""
    data = parse_job_data(job_name)
    
    if not data:
        return f"Job '{job_name}' not found."
    
    # Generate invoice number
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}-{job_name.replace(' ', '-').replace('(', '').replace(')', '')[:20]}"
    
    invoice = f"""# INVOICE

![WORK WORK Logo](work_work_logo.jpg)

**WORK WORK**  
Electrical + Electronics + Programming

---

**Invoice #:** {invoice_num}  
**Date:** {datetime.now().strftime('%d %B %Y')}  
**Client:** {data['client'] or job_name}  
**Job:** {job_name}  
**Terms:** Cash on completion

---

## Labour

| Date | Description | Hours | Rate | Amount |
|------|-------------|-------|------|--------|
"""
    
    for item in data['labour']:
        invoice += f"| {item['date']} | {item['task']} | {item['hours']:.1f} | ${item['rate']:.2f} | ${item['amount']:.2f} |\n"
    
    if not data['labour']:
        invoice += "| — | No labour logged yet | — | — | — |\n"
    
    invoice += f"| | **Subtotal** | **{sum(item['hours'] for item in data['labour']):.1f}** | | **${data['labour_total']:.2f}** |\n"

    invoice += f"""
## Materials

| Date | Description | Amount |
|------|-------------|--------|
"""
    
    for item in data['materials']:
        invoice += f"| {item['date']} | {item['item']} | ${item['amount']:.2f} |\n"
    
    if not data['materials']:
        invoice += "| — | No materials logged yet | — |\n"
    
    invoice += f"| | **Subtotal** | **${data['materials_total']:.2f}** |\n"

    total = data['total'] or (data['labour_total'] + data['materials_total'])
    paid = data['paid_total']
    owed = data['owed'] or (total - paid)
    
    invoice += f"""
---

## Summary

| | |
|---|---|
| Labour | ${data['labour_total']:.2f} |
| Materials | ${data['materials_total']:.2f} |
| **Total Due** | **${total:.2f}** |
"""

    if paid > 0:
        invoice += f"""
## Payments Received

| Date | Amount | Method |
|------|--------|--------|
| See payment history | ${paid:.2f} | Various |
"""
    
    invoice += f"""
---

## **BALANCE DUE: ${owed:.2f}**

---

**Payment:** Cash on completion

**Thank you for your business!**

---
"""

    if include_split:
        profit = total - data['materials_total']
        split = profit / 2
        
        invoice += f"""
**INTERNAL - Split Calculation:**

```
Invoice Total:              ${total:.2f}
- Materials:                ${data['materials_total']:.2f}
= Net Profit:               ${profit:.2f}

Split 50/50:
  Aaron's share:            ${split:.2f}
  Luke's share:             ${split:.2f}

Plus reimburse materials to payer
```
---
"""
    
    return invoice

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nWORK WORK Invoice Generator\n")
        print("Usage:")
        print("  python invoice_generator.py [job name]")
        print("  python invoice_generator.py [job name] --split")
        print("\nExample:")
        print("  python invoice_generator.py 'Dave\\'s Boat (HHO)'")
        print("  python invoice_generator.py 'Dave\\'s Alternator' --split")
        sys.exit(0)
    
    job_name = sys.argv[1]
    include_split = '--split' in sys.argv
    
    invoice = generate_invoice(job_name, include_split)
    print(invoice)
    
    # Save to file
    invoice_file = Path(f"invoices/{job_name.replace(' ', '-').replace('(', '').replace(')', '')}_invoice.md")
    invoice_file.parent.mkdir(exist_ok=True)
    invoice_file.write_text(invoice)
    print(f"\n---\nSaved to: {invoice_file}")
