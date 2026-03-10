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

    # Calculate labour total from workers (exclude fuel from labour)
    labour_total = sum(w[1] * w[2] for w in workers)  # hours * rate
    fuel_total = sum(w[3] for w in workers)  # fuel amounts

    # Create PDF
    filename = f"invoices/{job_name.replace(' ', '_').replace('(', '').replace(')', '')}_invoice.pdf"
    Path("invoices").mkdir(exist_ok=True)

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Colors
    dark_blue = HexColor('#1a365d')
    light_gray = HexColor('#f7fafc')

    # Header background (smaller)
    c.setFillColor(dark_blue)
    c.rect(0, height - 50*mm, width, 50*mm, fill=1, stroke=0)

    # Try to add logo (smaller)
    logo_file = Path(logo_path)
    if logo_file.exists():
        try:
            c.drawImage(str(logo_file), 20*mm, height - 45*mm, width=35*mm, height=35*mm, mask='auto')
        except:
            pass

    # Company name (white text)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60*mm, height - 18*mm, "WORK WORK")

    c.setFont("Helvetica", 10)
    c.drawString(60*mm, height - 32*mm, "Electrical • Electronics • Marine Engineering")
    c.drawString(60*mm, height - 42*mm, "Ph: 0457 870 354")

    # Invoice details (right side)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 20*mm, height - 20*mm, f"INVOICE #{invoice_num}")

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20*mm, height - 32*mm, date_str)
    c.drawRightString(width - 20*mm, height - 42*mm, f"Client: {client}")

    # Job details (compact)
    y = height - 65*mm
    c.setFillColor(light_gray)
    c.rect(20*mm, y - 18*mm, width - 40*mm, 18*mm, fill=1, stroke=0)

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(25*mm, y - 7*mm, f"Job: {job_name}")
    c.setFont("Helvetica", 9)
    c.drawString(25*mm, y - 15*mm, "Terms: Cash on completion")

    # Labour section (compact, no names)
    y = height - 90*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "LABOUR")
    c.line(20*mm, y - 2*mm, width - 20*mm, y - 2*mm)

    c.setFont("Helvetica", 10)
    total_hours = sum(w[1] for w in workers)
    num_workers = len(workers)
    hours_per_worker = total_hours / num_workers if num_workers > 0 else 0
    rate = workers[0][2] if workers else 40

    if num_workers == 1:
        c.drawString(25*mm, y - 10*mm, f"{total_hours:.0f} hrs @ ${rate:.0f}/hr")
    else:
        c.drawString(25*mm, y - 10*mm, f"{num_workers} technicians × {hours_per_worker:.0f} hrs each @ ${rate:.0f}/hr")

    c.drawRightString(width - 25*mm, y - 10*mm, f"${labour_total:.2f}")

    # Materials section (includes fuel)
    y = height - 115*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "MATERIALS")
    c.line(20*mm, y - 2*mm, width - 20*mm, y - 2*mm)

    c.setFont("Helvetica", 10)
    mat_line = 10*mm
    if materials > 0:
        c.drawString(25*mm, y - mat_line, "Parts and supplies")
        c.drawRightString(width - 25*mm, y - mat_line, f"${materials:.2f}")
        mat_line += 7*mm

    if fuel_total > 0:
        c.drawString(25*mm, y - mat_line, "Fuel")
        c.drawRightString(width - 25*mm, y - mat_line, f"${fuel_total:.2f}")
        mat_line += 7*mm

    if materials == 0 and fuel_total == 0:
        c.drawString(25*mm, y - mat_line, "Owner supplied")
        c.drawRightString(width - 25*mm, y - mat_line, "$0.00")

    materials_total = materials + fuel_total

    # Total section
    y = height - 145*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Labour:")
    c.drawRightString(width - 25*mm, y, f"${labour_total:.2f}")

    c.drawString(20*mm, y - 8*mm, "Materials:")
    c.drawRightString(width - 25*mm, y - 8*mm, f"${materials_total:.2f}")

    c.line(width - 50*mm, y - 12*mm, width - 25*mm, y - 12*mm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y - 22*mm, "TOTAL:")
    c.drawRightString(width - 25*mm, y - 22*mm, f"${total:.2f}")

    if paid > 0:
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, y - 32*mm, "Paid:")
        c.drawRightString(width - 25*mm, y - 32*mm, f"${paid:.2f}")

    # Balance due - COMPACT (with extra spacing after total)
    balance_y = height - 180*mm
    c.setFillColor(HexColor('#1a365d'))
    c.rect(15*mm, balance_y - 8*mm, width - 30*mm, 16*mm, fill=1, stroke=0)

    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, balance_y - 3*mm, "AMOUNT TO PAY:")
    c.drawRightString(width - 25*mm, balance_y - 3*mm, f"${owed:.2f}")

    # Payment info - COMPACT
    pay_y = height - 195*mm
    c.setFillColor(HexColor('#e8f4f8'))
    c.rect(15*mm, pay_y - 15*mm, width - 30*mm, 25*mm, fill=1, stroke=1)

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(25*mm, pay_y + 3*mm, "PAYMENT:")

    c.setFont("Helvetica", 9)
    c.drawString(25*mm, pay_y - 5*mm, "Cash OR BSB: 016-964  Acc: 114998156")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(25*mm, pay_y - 13*mm, "Name: Aaron King")

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 25*mm, "Thank you for your business! Questions? Call 0457 870 354")

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
