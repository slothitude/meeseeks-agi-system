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
    
    data = {
        'name': job_name,
        'client': '',
        'status': '',
        'labour': [],
        'labour_total': 0,
        'materials': [],
        'materials_total': 0,
        'fuel_total': 0,
        'payments': [],
        'paid_total': 0,
        'total': 0,
        'owed': 0
    }
    
    # Find the job section for client/status
    job_pattern = rf"### {re.escape(job_name)}.*?(?=###|\Z)"
    job_match = re.search(job_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if job_match:
        job_section = job_match.group(0)
        
        # Extract client
        client_match = re.search(r'\*\*Client:\*\*\s*(.+)', job_section)
        if client_match:
            data['client'] = client_match.group(1).strip()
        
        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(.+)', job_section)
        if status_match:
            data['status'] = status_match.group(1).strip()
        
        # Extract summary totals from job section
        total_match = re.search(r'\*\*Total:\*\*\s*\$?([\d.]+)', job_section)
        if total_match:
            data['total'] = float(total_match.group(1))
        
        paid_match = re.search(r'\*\*Paid:\*\*\s*\$?([\d.]+)', job_section)
        if paid_match:
            data['paid_total'] = float(paid_match.group(1))
        
        owed_match = re.search(r'\*\*Owed:\*\*\s*\$?([\d.]+)', job_section)
        if owed_match:
            data['owed'] = float(owed_match.group(1))
    
    # Parse Hours Tracker table (central tracking) - simple line-by-line approach
    in_hours_section = False
    for line in content.split('\n'):
        if '## Hours Tracker' in line:
            in_hours_section = True
            continue
        if in_hours_section and line.startswith('##'):
            break
        if in_hours_section and line.startswith('|') and 'Date' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 8:
                row_job = parts[2]
                
                # Check if this row matches our job (partial match)
                if job_name.lower() in row_job.lower() or row_job.lower() in job_name.lower():
                    date = parts[1]
                    who = parts[3]
                    hours = float(parts[4])
                    rate = float(parts[5].replace('$', ''))
                    fuel_str = parts[6].replace('$', '').strip()
                    fuel = 0 if not fuel_str or not fuel_str[0].isdigit() else float(fuel_str)
                    amount = float(parts[7].replace('$', ''))
                    
                    data['labour'].append({
                        'date': date,
                        'who': who,
                        'hours': hours,
                        'rate': rate,
                        'fuel': fuel,
                        'amount': amount
                    })
                    data['labour_total'] += amount
                    data['fuel_total'] += fuel
    
    # Parse Receipts Tracker table (central tracking)
    in_receipts_section = False
    for line in content.split('\n'):
        if '## Receipts Tracker' in line:
            in_receipts_section = True
            continue
        if in_receipts_section and line.startswith('##'):
            break
        if in_receipts_section and line.startswith('|') and 'Date' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                row_job = parts[2]
                
                # Check if this row matches our job
                if job_name.lower() in row_job.lower() or row_job.lower() in job_name.lower():
                    data['materials'].append({
                        'date': parts[1],
                        'item': parts[3],
                        'amount': float(parts[4].replace('$', '')),
                        'paid_by': parts[5]
                    })
                    data['materials_total'] += float(parts[4].replace('$', ''))
    
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

| Date | Who | Hours | Rate | Fuel | Amount |
|------|-----|-------|------|------|--------|
"""
    
    for item in data['labour']:
        fuel_str = f"${item.get('fuel', 0):.2f}" if item.get('fuel', 0) > 0 else "—"
        invoice += f"| {item['date']} | {item.get('who', '—')} | {item['hours']:.1f} | ${item['rate']:.2f} | {fuel_str} | ${item['amount']:.2f} |\n"
    
    if not data['labour']:
        invoice += "| — | — | — | — | — | — |\n"
    
    total_hours = sum(item['hours'] for item in data['labour'])
    invoice += f"| | **Subtotal** | **{total_hours:.1f}** | | | **${data['labour_total']:.2f}** |\n"

    invoice += f"""
## Materials

| Date | Description | Amount |
|------|-------------|--------|
"""
    
    for item in data['materials']:
        invoice += f"| {item['date']} | {item['item']} | ${item['amount']:.2f} |\n"
    
    if not data['materials']:
        invoice += "| — | No materials | — |\n"
    
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

**Payment Options:**

**Cash on completion** OR direct transfer to:

| | |
|---|---|
| **Account Name** | Aaron King |
| **BSB** | 016-964 |
| **Account** | 114998156 |

*(Australia Post Everyday Mastercard - instant notification)*

---

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
