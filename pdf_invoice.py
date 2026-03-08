#!/usr/bin/env python3
"""
WORK WORK - PDF Invoice Generator
Professional PDF invoices with logo for Telegram
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
from pathlib import Path

def create_pdf_invoice(job_name, client, workers, materials, total, paid, logo_path="invoices/work_work_logo.jpg"):
    """Generate professional PDF invoice with logo and labour breakdown"""
    
    owed = total - paid
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}"
    date_str = datetime.now().strftime("%d %B %Y")
    
    # Calculate labour total from workers
    labour_total = sum(w[4] for w in workers)  # amount is 5th element
    
    # Create PDF
    filename = f"invoices/{job_name.replace(' ', '_').replace('(', '').replace(')', '')}_invoice.pdf"
    Path("invoices").mkdir(exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Colors
    dark_blue = HexColor('#1a365d')
    light_gray = HexColor('#f7fafc')
    
    # Header background
    c.setFillColor(dark_blue)
    c.rect(0, height - 80*mm, width, 80*mm, fill=1, stroke=0)
    
    # Try to add logo
    logo_file = Path(logo_path)
    if logo_file.exists():
        try:
            c.drawImage(str(logo_file), 20*mm, height - 70*mm, width=50*mm, height=50*mm, mask='auto')
        except:
            pass  # If logo fails, continue without it
    
    # Company name (white text)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(45*mm, height - 15*mm, "WORK WORK")
    
    c.setFont("Helvetica", 12)
    c.drawString(80*mm, height - 42*mm, "Electrical • Electronics • Marine Engineering")
    c.drawString(80*mm, height - 50*mm, "Ph: 0457 870 354")
    
    # Invoice details (right side)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - 20*mm, height - 30*mm, f"INVOICE #{invoice_num}")
    
    c.setFont("Helvetica", 11)
    c.drawRightString(width - 20*mm, height - 42*mm, date_str)
    c.drawRightString(width - 20*mm, height - 52*mm, f"Client: {client}")
    
    # Job details box
    y = height - 100*mm
    c.setFillColor(light_gray)
    c.rect(20*mm, y - 25*mm, width - 40*mm, 25*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25*mm, y - 10*mm, f"Job: {job_name}")
    c.setFont("Helvetica", 10)
    c.drawString(25*mm, y - 20*mm, "Terms: Cash on completion")
    
    # Labour section with breakdown
    y = height - 140*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "LABOUR")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
    y_offset = 15*mm
    for name, hours, rate, fuel, amount in workers:
        fuel_str = f" + ${fuel:.0f} fuel" if fuel > 0 else ""
        c.drawString(25*mm, y - y_offset, f"{name}: {hours:.0f} hrs @ ${rate:.0f}/hr{fuel_str}")
        c.drawRightString(width - 25*mm, y - y_offset, f"${amount:.2f}")
        y_offset += 10*mm
    
    # Materials section
    y = height - (140 + y_offset + 10)*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "MATERIALS")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
    if materials > 0:
        c.drawString(25*mm, y - 15*mm, "Parts and supplies")
        c.drawRightString(width - 25*mm, y - 15*mm, f"${materials:.2f}")
    else:
        c.drawString(25*mm, y - 15*mm, "Owner supplied")
        c.drawRightString(width - 25*mm, y - 15*mm, "$0.00")
    
    # Total section
    y = height - (140 + y_offset + 60)*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, "Labour:")
    c.drawRightString(width - 25*mm, y, f"${labour_total:.2f}")
    
    c.drawString(20*mm, y - 12*mm, "Materials:")
    c.drawRightString(width - 25*mm, y - 12*mm, f"${materials:.2f}")
    
    c.line(width - 80*mm, y - 18*mm, width - 25*mm, y - 18*mm)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y - 30*mm, "TOTAL:")
    c.drawRightString(width - 25*mm, y - 30*mm, f"${total:.2f}")
    
    if paid > 0:
        c.setFont("Helvetica", 12)
        c.drawString(20*mm, y - 45*mm, "Paid:")
        c.drawRightString(width - 25*mm, y - 45*mm, f"${paid:.2f}")
    
    # Balance due - highlighted
    balance_y = y - 70*mm
    c.setFillColor(HexColor('#fff3cd'))
    c.rect(20*mm, balance_y - 10*mm, width - 40*mm, 20*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25*mm, balance_y, "BALANCE DUE:")
    c.drawRightString(width - 25*mm, balance_y, f"${owed:.2f}")
    
    # Payment info
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, balance_y - 25*mm, "Payment: Australia Post Everyday Mastercard")
    c.drawString(20*mm, balance_y - 35*mm, "Contact Aaron for BSB/Account details")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 30*mm, "Thank you for your business!")
    c.drawCentredString(width/2, 20*mm, "Questions? Call Aaron on 0457 870 354")
    
    c.save()
    
    return filename

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_invoice.py '[job]' '[client]' '[workers_json]' [materials] [total] [paid]")
        print("\nWorkers JSON format: [{\"name\":\"Aaron\",\"hours\":3,\"rate\":40,\"fuel\":20,\"amount\":140}, ...]")
        sys.exit(1)
    
    import json
    
    job = sys.argv[1]
    client = sys.argv[2]
    workers = json.loads(sys.argv[3])
    materials = float(sys.argv[4])
    total = float(sys.argv[5])
    paid = float(sys.argv[6]) if len(sys.argv) > 6 else 0
    
    filename = create_pdf_invoice(job, client, workers, materials, total, paid)
    print(f"PDF created: {filename}")
