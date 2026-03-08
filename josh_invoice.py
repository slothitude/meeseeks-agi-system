#!/usr/bin/env python3
"""
WORK WORK - Josh's Boat Invoice Generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
from pathlib import Path

def create_josh_invoice():
    """Generate Josh's Boat invoice with logo and labour breakdown"""
    
    # Job details
    job_name = "Josh's Boat"
    client = "Josh"
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}"
    date_str = datetime.now().strftime("%d %B %Y")
    
    # Labour breakdown (generic, no names)
    labour_items = [
        ("Two technicians @ $40/hr x 3 hours", 240),
        ("Fuel allowance", 20)
    ]
    labour_total = 260
    materials = 0
    total = labour_total + materials
    paid = 0
    owed = total - paid
    
    # Create PDF
    safe_name = job_name.replace(' ', '_').replace("'", '')
    filename = f"invoices/{safe_name}_invoice.pdf"
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
    logo_path = Path("invoices/work_work_logo.jpg")
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 20*mm, height - 70*mm, width=50*mm, height=50*mm, mask='auto')
        except Exception as e:
            print(f"Logo failed: {e}")
    
    # Company name (white text, inside header)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 32)
    c.drawString(20*mm, height - 25*mm, "OVERLAP")
    
    c.setFont("Helvetica", 12)
    c.drawString(20*mm, height - 38*mm, "Electrical • Electronics • Marine Engineering")
    c.drawString(20*mm, height - 50*mm, "Ph: 0457 870 354")
    
    # Invoice details (right side, inside header)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 20*mm, height - 25*mm, f"INVOICE #{invoice_num}")
    
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20*mm, height - 38*mm, date_str)
    c.drawRightString(width - 20*mm, height - 50*mm, f"Client: {client}")
    
    # Job details box
    y = height - 100*mm
    c.setFillColor(light_gray)
    c.rect(20*mm, y - 25*mm, width - 40*mm, 25*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25*mm, y - 10*mm, f"Job: {job_name}")
    c.setFont("Helvetica", 10)
    c.drawString(25*mm, y - 20*mm, "Terms: Cash on completion")
    
    # Work description section
    y_desc = height - 130*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y_desc, "Work Completed:")
    c.setFont("Helvetica", 10)
    
    work_items = [
        "• Installed new fuel pump (owner supplied)",
        "• Generator started and tested",
        "• Identified coolant system issue - requires investigation",
        "• Bilge pump float requires securing"
    ]
    
    y_line = y_desc - 8*mm
    for item in work_items:
        c.drawString(25*mm, y_line, item)
        y_line -= 6*mm
    
    # Labour section with breakdown
    y = height - 170*mm  # Adjusted for work description
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "LABOUR")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
    y_offset = 15*mm
    for description, amount in labour_items:
        c.drawString(25*mm, y - y_offset, description)
        c.drawRightString(width - 25*mm, y - y_offset, f"${amount:.2f}")
        y_offset += 10*mm
    
    # Materials section
    y = height - (140 + y_offset + 10)*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "MATERIALS")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
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
    filename = create_josh_invoice()
    print(f"PDF created: {filename}")
