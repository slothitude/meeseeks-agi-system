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
    
    # Small header block (letterhead style) with border
    header_height = 37*mm  # Adds ~5px blue space below text before border
    c.setFillColor(dark_blue)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    
    # Border around header
    c.setStrokeColor(HexColor('#0d1f3c'))  # Darker blue for border
    c.setLineWidth(2)
    c.rect(0, height - header_height, width, header_height, fill=0, stroke=1)
    
    # Try to add logo
    logo_path = Path("invoices/work_work_logo.jpg")
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 15*mm, height - 30*mm, width=25*mm, height=25*mm, mask='auto')
        except Exception as e:
            print(f"Logo failed: {e}")
    
    # Company name (white text, inside header)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(45*mm, height - 15*mm, "WORK WORK")
    
    c.setFont("Helvetica", 9)
    c.drawString(45*mm, height - 26*mm, "Electrical • Electronics • Marine Engineering")
    c.drawString(45*mm, height - 35*mm, "Ph: 0457 870 354")
    
    # Invoice details (right side, inside header)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 15*mm, height - 15*mm, f"INVOICE #{invoice_num}")
    
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 15*mm, height - 25*mm, date_str)
    c.drawRightString(width - 15*mm, height - 33*mm, f"Client: {client}")
    
    # Job details box
    y = height - 50*mm  # Adjusted for smaller header
    c.setFillColor(light_gray)
    c.rect(20*mm, y - 20*mm, width - 40*mm, 20*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(25*mm, y - 8*mm, f"Job: {job_name}")
    c.setFont("Helvetica", 9)
    c.drawString(25*mm, y - 16*mm, "Terms: Cash on completion")
    
    # Work description section
    y_desc = height - 75*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y_desc, "Work Completed:")
    c.setFont("Helvetica", 9)
    
    work_items = [
        "• Installed new fuel pump (owner supplied)",
        "• Generator started and tested",
        "• Identified coolant system issue - requires investigation",
        "• Bilge pump float requires securing"
    ]
    
    y_line = y_desc - 6*mm
    for item in work_items:
        c.drawString(25*mm, y_line, item)
        y_line -= 5*mm
    
    # Labour section with breakdown (more compact)
    y = height - 100*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "LABOUR")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
    y_offset = 12*mm
    for description, amount in labour_items:
        c.drawString(25*mm, y - y_offset, description)
        c.drawRightString(width - 25*mm, y - y_offset, f"${amount:.2f}")
        y_offset += 8*mm
    
    # Materials section (compact)
    y_mat = y - y_offset - 8*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y_mat, "MATERIALS")
    c.line(20*mm, y_mat - 3*mm, width - 20*mm, y_mat - 3*mm)
    
    c.setFont("Helvetica", 11)
    c.drawString(25*mm, y_mat - 12*mm, "Owner supplied")
    c.drawRightString(width - 25*mm, y_mat - 12*mm, "$0.00")
    
    # Total section (compact)
    y_total = y_mat - 35*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y_total, "Labour:")
    c.drawRightString(width - 25*mm, y_total, f"${labour_total:.2f}")
    
    c.drawString(20*mm, y_total - 10*mm, "Materials:")
    c.drawRightString(width - 25*mm, y_total - 10*mm, f"${materials:.2f}")
    
    c.line(width - 80*mm, y_total - 15*mm, width - 25*mm, y_total - 15*mm)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y_total - 28*mm, "TOTAL:")
    c.drawRightString(width - 25*mm, y_total - 28*mm, f"${total:.2f}")
    
    # Balance due - highlighted (compact)
    balance_y = y_total - 55*mm
    c.setFillColor(HexColor('#fff3cd'))
    c.rect(20*mm, balance_y - 8*mm, width - 40*mm, 18*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, balance_y, "BALANCE DUE:")
    c.drawRightString(width - 25*mm, balance_y, f"${owed:.2f}")
    
    # Payment info (compact)
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, balance_y - 18*mm, "Payment: Australia Post Everyday Mastercard • Contact Aaron for BSB/Account")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 30*mm, "Thank you for your business!")
    c.drawCentredString(width/2, 20*mm, "Questions? Call Aaron on 0457 870 354")
    
    c.save()
    
    return filename

if __name__ == "__main__":
    filename = create_josh_invoice()
    print(f"PDF created: {filename}")
