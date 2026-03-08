#!/usr/bin/env python3
"""
WORK WORK Invoice - SMS Format
Simple text invoice for SMS messaging
"""

from datetime import datetime

def generate_sms_invoice(job_name, client, labour_total, materials_total, total, paid, owed, phone="0457 870 354"):
    """Generate SMS-friendly invoice text."""
    
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}"
    
    sms = f"""WORK WORK Invoice
#{invoice_num}
{datetime.now().strftime('%d/%m/%Y')}

Client: {client}
Job: {job_name}

Labour: ${labour_total:.2f}
Materials: ${materials_total:.2f}
TOTAL: ${total:.2f}

Paid: ${paid:.2f}
BALANCE: ${owed:.2f}

Terms: Cash on completion

Questions? Call Aaron
{phone}

Thank you!"""
    
    return sms

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 7:
        print("\nWORK WORK SMS Invoice Generator\n")
        print("Usage:")
        print("  python sms_invoice.py '[job]' '[client]' [labour] [materials] [total] [paid]")
        print("\nExample:")
        print("  python sms_invoice.py 'Dave\\'s Boat' 'Dave' 240 385 625 575")
        sys.exit(0)
    
    job = sys.argv[1]
    client = sys.argv[2]
    labour = float(sys.argv[3])
    materials = float(sys.argv[4])
    total = float(sys.argv[5])
    paid = float(sys.argv[6])
    owed = total - paid
    
    sms = generate_sms_invoice(job, client, labour, materials, total, paid, owed)
    print(sms)
