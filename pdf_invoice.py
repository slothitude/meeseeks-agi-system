#!/usr/bin/env python3
"""
WORK WORK Invoice - PDF Generator
Creates professional PDF invoices with logo
"""

from fpdf import FPDF
from datetime import datetime
from pathlib import Path

class WorkWorkPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        
    def header(self):
        # Add logo if exists
        logo_path = Path("invoices/work_work_logo.jpg")
        if logo_path.exists():
            self.image(str(logo_path), x=10, y=10, w=50)
        
        self.ln(30)
        
        # Business name
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'WORK WORK', ln=True, align='C')
        
        self.set_font('Arial', '', 12)
        self.cell(0, 8, 'Electrical · Electronics · Programming', ln=True, align='C')
        self.cell(0, 8, 'Ph: 0457 870 354', ln=True, align='C')
        self.ln(10)

def create_pdf_invoice(job_name, client, labour_items, materials_items, total, paid, owed, output_file):
    """Generate PDF invoice."""
    
    pdf = WorkWorkPDF()
    
    # Invoice details
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}-{job_name.replace(' ', '-')[:15]}"
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'INVOICE #{invoice_num}', ln=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f'Date: {datetime.now().strftime("%d %B %Y")}', ln=True)
    pdf.cell(0, 8, f'Client: {client}', ln=True)
    pdf.cell(0, 8, f'Job: {job_name}', ln=True)
    pdf.cell(0, 8, 'Terms: Cash on completion', ln=True)
    pdf.ln(10)
    
    # Labour section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'LABOUR', ln=True)
    pdf.set_font('Arial', '', 10)
    
    # Table header
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 8, 'Date', 1, 0, 'C', True)
    pdf.cell(80, 8, 'Description', 1, 0, 'C', True)
    pdf.cell(20, 8, 'Hours', 1, 0, 'C', True)
    pdf.cell(25, 8, 'Rate', 1, 0, 'C', True)
    pdf.cell(25, 8, 'Amount', 1, 1, 'C', True)
    
    labour_total = 0
    for item in labour_items:
        pdf.cell(30, 8, item.get('date', '-'), 1, 0, 'C')
        pdf.cell(80, 8, item.get('task', '-')[:40], 1, 0, 'L')
        pdf.cell(20, 8, f"{item.get('hours', 0):.1f}", 1, 0, 'C')
        pdf.cell(25, 8, f"${item.get('rate', 0):.2f}", 1, 0, 'R')
        pdf.cell(25, 8, f"${item.get('amount', 0):.2f}", 1, 1, 'R')
        labour_total += item.get('amount', 0)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(155, 8, 'Labour Subtotal:', 1, 0, 'R')
    pdf.cell(25, 8, f"${labour_total:.2f}", 1, 1, 'R')
    pdf.ln(5)
    
    # Materials section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'MATERIALS', ln=True)
    pdf.set_font('Arial', '', 10)
    
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 8, 'Date', 1, 0, 'C', True)
    pdf.cell(120, 8, 'Description', 1, 0, 'C', True)
    pdf.cell(30, 8, 'Amount', 1, 1, 'C', True)
    
    materials_total = 0
    for item in materials_items:
        pdf.cell(30, 8, item.get('date', '-'), 1, 0, 'C')
        pdf.cell(120, 8, item.get('item', '-')[:60], 1, 0, 'L')
        pdf.cell(30, 8, f"${item.get('amount', 0):.2f}", 1, 1, 'R')
        materials_total += item.get('amount', 0)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(150, 8, 'Materials Subtotal:', 1, 0, 'R')
    pdf.cell(30, 8, f"${materials_total:.2f}", 1, 1, 'R')
    pdf.ln(10)
    
    # Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, '', 0, 0)
    pdf.cell(50, 10, 'Labour:', 1, 0, 'R')
    pdf.cell(30, 10, f"${labour_total:.2f}", 1, 1, 'R')
    
    pdf.cell(100, 10, '', 0, 0)
    pdf.cell(50, 10, 'Materials:', 1, 0, 'R')
    pdf.cell(30, 10, f"${materials_total:.2f}", 1, 1, 'R')
    
    pdf.cell(100, 10, '', 0, 0)
    pdf.cell(50, 10, 'TOTAL DUE:', 1, 0, 'R')
    pdf.cell(30, 10, f"${total:.2f}", 1, 1, 'R')
    
    if paid > 0:
        pdf.cell(100, 10, '', 0, 0)
        pdf.cell(50, 10, 'Paid:', 1, 0, 'R')
        pdf.cell(30, 10, f"${paid:.2f}", 1, 1, 'R')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(255, 255, 200)
    pdf.cell(100, 12, '', 0, 0)
    pdf.cell(50, 12, 'BALANCE DUE:', 1, 0, 'R', True)
    pdf.cell(30, 12, f"${owed:.2f}", 1, 1, 'R', True)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Thank you for your business!', ln=True, align='C')
    
    # Save PDF
    output_path = Path("invoices") / output_file
    output_path.parent.mkdir(exist_ok=True)
    pdf.output(str(output_path))
    
    return str(output_path)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 7:
        print("\nWORK WORK PDF Invoice Generator\n")
        print("Usage:")
        print("  python pdf_invoice.py '[job]' '[client]' [labour] [materials] [total] [paid]")
        print("\nExample:")
        print("  python pdf_invoice.py 'Dave\\'s Boat' 'Dave' 240 385 625 575")
        print("\nOutput: invoices/job_name_invoice.pdf")
        sys.exit(0)
    
    job = sys.argv[1]
    client = sys.argv[2]
    labour = float(sys.argv[3])
    materials = float(sys.argv[4])
    total = float(sys.argv[5])
    paid = float(sys.argv[6])
    owed = total - paid
    
    # Create simple items for demo
    labour_items = [{'date': datetime.now().strftime('%d/%m/%Y'), 'task': 'Work completed', 'hours': labour/40, 'rate': 40, 'amount': labour}]
    materials_items = [{'date': datetime.now().strftime('%d/%m/%Y'), 'item': 'Materials', 'amount': materials}]
    
    output_file = f"{job.replace(' ', '_').replace('(', '').replace(')', '')}_invoice.pdf"
    
    pdf_path = create_pdf_invoice(job, client, labour_items, materials_items, total, paid, owed, output_file)
    print(f"\n✓ PDF Invoice created: {pdf_path}")
