#!/usr/bin/env python3
"""
WORK WORK Invoice Generator
Generates simple invoices from WORK_WORK.md data
"""

import re
from datetime import datetime
from pathlib import Path

def parse_jobs():
    """Parse WORK_WORK.md to extract job summaries."""
    work_file = Path("WORK_WORK.md")
    if not work_file.exists():
        return None

    content = work_file.read_text()
    jobs = {}

    # Split by job sections
    sections = content.split('### ')

    for section in sections[1:]:  # Skip first empty section
        lines = section.split('\n')
        if not lines:
            continue

        job_name = lines[0].strip()

        # Look for summary section
        if '**Summary:**' in section:
            summary_start = section.index('**Summary:**')
            summary_section = section[summary_start:summary_start+500]

            # Extract values using simple string matching
            try:
                labour_match = re.search(r'Labour: \$([0-9.]+)', summary_section)
                materials_match = re.search(r'Materials: \$([0-9.]+)', summary_section)
                total_match = re.search(r'\*\*Total: \$([0-9.]+)\*\*', summary_section)
                paid_match = re.search(r'\*\*Paid: \$([0-9.]+)\*\*', summary_section)
                owed_match = re.search(r'\*\*Owed: \$([0-9.]+)\*\*', summary_section)

                if all([labour_match, materials_match, total_match, paid_match, owed_match]):
                    jobs[job_name] = {
                        'labour': float(labour_match.group(1)),
                        'materials': float(materials_match.group(1)),
                        'total': float(total_match.group(1)),
                        'paid': float(paid_match.group(1)),
                        'owed': float(owed_match.group(1))
                    }
            except Exception as e:
                print(f"Error parsing {job_name}: {e}")
                continue

    return jobs

def generate_invoice(job_name, job_data):
    """Generate a formatted invoice."""
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}-{job_name.replace(' ', '-').replace('(', '').replace(')', '')}"

    invoice = f"""
{'='*60}
WORK WORK - INVOICE
{'='*60}

Job: {job_name}
Date: {datetime.now().strftime('%Y-%m-%d')}
Invoice #: {invoice_num}

{'='*60}
SUMMARY
{'='*60}

Labour:         ${job_data['labour']:.2f}
Materials:      ${job_data['materials']:.2f}
-------------------------
TOTAL:          ${job_data['total']:.2f}

Paid:           ${job_data['paid']:.2f}
-------------------------
OWED:           ${job_data['owed']:.2f}

{'='*60}

Payment Details:
[Add payment method here]

Thank you for your business!

WORK WORK
Electrical + Electronics + Programming
"""

    return invoice

if __name__ == "__main__":
    import sys

    jobs = parse_jobs()

    if not jobs:
        print("No jobs found in WORK_WORK.md")
        sys.exit(1)

    if len(sys.argv) > 1:
        job_name = ' '.join(sys.argv[1:])
        # Try to find matching job
        matched = None
        for name in jobs.keys():
            if job_name.lower() in name.lower():
                matched = name
                break

        if matched:
            print(generate_invoice(matched, jobs[matched]))
        else:
            print(f"Job '{job_name}' not found.")
            print(f"Available jobs: {', '.join(jobs.keys())}")
    else:
        print("\nWORK WORK - Available Jobs:\n")
        for job_name, job_data in jobs.items():
            print(f"  {job_name}: ${job_data['total']:.2f} (${job_data['owed']:.2f} owed)")
        print("\nUsage: python work_work_invoice.py [job name]")
