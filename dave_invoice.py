#!/usr/bin/env python3
"""Generate Dave's Boat invoice with new template"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
from pathlib import Path

def create_dave_invoice():
    """Generate Dave's Boat invoice"""
    
    # Job details
    job_name = "Dave's Boat (HHO)"
    client = "Dave"
    invoice_num = f"WW-{datetime.now().strftime('%Y%m%d')}"
    date_str = datetime.now().strftime("%d %B %Y")
    
    # Labour items
    labour_items = [
        ("Two technicians @ $40/hr x 6 hours", 240)
    ]
    labour_total = 240
    materials = 385
    total = 625
    paid = 575
    owed = 40
    
    # Create PDF
    filename = "invoices/Daves_Boat_invoice.pdf"
    Path("invoices").mkdir(exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Colors
    dark_blue = HexColor('#1a365d')
    light_gray = HexColor('#f7fafc')
    
    # Header
    header_height = 37*mm
    c.setFillColor(dark_blue)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    
    c.setStrokeColor(HexColor('#0d1f3c'))
    c.setLineWidth(2)
    c.rect(0, height - header_height, width, header_height, fill=0, stroke=1)
    
    # Logo
    logo_path = Path("invoices/work_work_logo.jpg")
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 15*mm, height - 30*mm, width=25*mm, height=25*mm, mask='auto')
        except:
            pass
    
    # Company info
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(45*mm, height - 15*mm, "WORK WORK")
    
    c.setFont("Helvetica", 9)
    c.drawString(45*mm, height - 26*mm, "Electrical • Electronics • Marine Engineering")
    c.drawString(45*mm, height - 35*mm, "Ph: 0457 870 354")
    
    # Invoice details
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 15*mm, height - 15*mm, f"INVOICE #{invoice_num}")
    
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 15*mm, height - 25*mm, date_str)
    c.drawRightString(width - 15*mm, height - 33*mm, f"Client: {client}")
    
    # Job box
    y = height - 50*mm
    c.setFillColor(light_gray)
    c.rect(20*mm, y - 20*mm, width - 40*mm, 20*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(25*mm, y - 8*mm, f"Job: {job_name}")
    c.setFont("Helvetica", 9)
    c.drawString(25*mm, y - 16*mm, "Terms: Cash on completion")
    
    # Work description
    y_desc = height - 78*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y_desc, "Work Completed:")
    c.setFont("Helvetica", 9)
    
    work_items = [
        "• Installed bilge pump system",
        "• Installed PWM controller",
        "• Electrical wiring and connections",
        "• System tested and operational"
    ]
    
    y_line = y_desc - 6*mm
    for item in work_items:
        c.drawString(25*mm, y_line, item)
        y_line -= 5*mm
    
    # Labour
    y = height - 108*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "LABOUR")
    c.line(20*mm, y - 3*mm, width - 20*mm, y - 3*mm)
    
    c.setFont("Helvetica", 11)
    y_offset = 12*mm
    for description, amount in labour_items:
        c.drawString(25*mm, y - y_offset, description)
        c.drawRightString(width - 25*mm, y - y_offset, f"${amount:.2f}")
        y_offset += 8*mm
    
    # Materials
    y_mat = y - y_offset - 8*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y_mat, "MATERIALS")
    c.line(20*mm, y_mat - 3*mm, width - 20*mm, y_mat - 3*mm)
    
    c.setFont("Helvetica", 11)
    c.drawString(25*mm, y_mat - 12*mm, "Cigarettes, shunts, misc, PWM's")
    c.drawRightString(width - 25*mm, y_mat - 12*mm, f"${materials:.2f}")
    
    # Total
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
    
    c.setFont("Helvetica", 12)
    c.drawString(20*mm, y_total - 42*mm, "Paid:")
    c.drawRightString(width - 25*mm, y_total - 42*mm, f"${paid:.2f}")
    
    # Balance
    balance_y = y_total - 60*mm
    c.setFillColor(HexColor('#fff3cd'))
    c.rect(20*mm, balance_y - 8*mm, width - 40*mm, 18*mm, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, balance_y, "BALANCE DUE:")
    c.drawRightString(width - 25*mm, balance_y, f"${owed:.2f}")
    
    # Payment info
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, balance_y - 18*mm, "Payment: Australia Post Everyday Mastercard • Contact Aaron for BSB/Account")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 30*mm, "Thank you for your business!")
    c.drawCentredString(width/2, 20*mm, "Questions? Call Aaron on 0457 870 354")
    
    c.save()
    
    return filename

if __name__ == "__main__":
    filename = create_dave_invoice()
    print(f"PDF created: {filename}")
