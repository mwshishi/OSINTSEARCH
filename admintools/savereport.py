import os
import json
# Add these imports for ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def save_as_json(data, report_name):
    root_dir = "OSINT_REPORTS"
    report_folder = os.path.join(root_dir, report_name)

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    if os.path.exists(report_folder):
        return "exists"

    os.makedirs(report_folder)
    with open(os.path.join(report_folder, "report.json"), "w") as f:
        json.dump(data, f, indent=4)
    return "saved"

def overwrite_json(data, report_name):
    root_dir = "OSINT_REPORTS"
    report_folder = os.path.join(root_dir, report_name)
    with open(os.path.join(report_folder, "report.json"), "w") as f:
        json.dump(data, f, indent=4)

def save_as_txt(data, report_name):
    report_folder = os.path.join("OSINT_REPORTS", report_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    with open(os.path.join(report_folder, "report.txt"), "w") as f:
        f.write(f"Report Name: {data['name']}\n\n")
        for bubble in data.get("bubbles", []):
            f.write(f"{bubble['type'].title()}: {bubble['label']}\n")
            for attr in bubble.get("attributes", []):
                f.write(f"    - {attr['name']}: {attr.get('value', '')} [{attr['status']}]\n")
            f.write("\n")

def save_as_pdf(data, report_name):
    """
    PDF ‘office‐modern’ cu:
    • Titlu într-o cutie albastru‐pastel
    • Identificator (Email/Phone/Username) scris cu albastru
    • Fiecare atribut: “found” afișat cu verde, “not found” cu roșu, altfel gri închis
    • Separatori subțiri între secțiuni
    • Imagini pe pagini separate, cu descriere și sursă
    """
    root_dir = "OSINT_REPORTS"
    report_folder = os.path.join(root_dir, report_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    pdf_path = os.path.join(report_folder, "report.pdf")
    c = pdfcanvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Culori
    alabaster_blue = colors.HexColor("#E4ECF7")   # albastru-pastel deschis
    office_blue = colors.HexColor("#2F5496")      # albastru “office”
    dark_gray = colors.HexColor("#333333")
    separator_gray = colors.HexColor("#CCCCCC")
    green_found = colors.HexColor("#2E8B57")      # verde pentru “found”
    red_notfound = colors.HexColor("#8B0000")     # roșu pentru “not found”

    margin = 50
    y = height - margin

    # ---- Prima pagină: Titlu ----
    title_box_height = 50
    c.setFillColor(alabaster_blue)
    c.rect(margin / 2, y - title_box_height, width - margin, title_box_height, fill=True, stroke=False)

    c.setFillColor(office_blue)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y - title_box_height / 2 + 6, "OSINT REPORT")
    y -= title_box_height + 20

    # ---- Numele raportului ----
    c.setFillColor(office_blue)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, f"Report Name: {data.get('name', '')}")
    y -= 24

    # Linia separator
    c.setStrokeColor(separator_gray)
    c.setLineWidth(1)
    c.line(margin, y, width - margin, y)
    y -= 18

    # ---- Bule (Email/Phone/Username) și atributele lor ----
    for bubble in data.get("bubbles", []):
        bubble_type = bubble.get("type", "").title() or "Unknown"
        bubble_label = bubble.get("label", "")
        attributes = bubble.get("attributes", [])

        # 1) Scrie “Type: label” (ex. “Email: john@example.com”)
        c.setFillColor(office_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"{bubble_type}: {bubble_label}")
        y -= 18

        # 2) Pentru fiecare atribut, colorează “found” cu verde, “not found” cu roșu
        for attr in attributes:
            name = attr.get("name", "")
            status = attr.get("status", "").lower()

            if status == "found":
                c.setFillColor(green_found)
            elif status == "not found":
                c.setFillColor(red_notfound)
            else:
                c.setFillColor(dark_gray)

            c.setFont("Helvetica", 11)
            c.drawString(margin + 20, y, f"{name}: {status}")
            y -= 15

            if y < margin + 100:
                c.showPage()
                y = height - margin
                # Re-desenăm separatorul pe pagina nouă
                c.setStrokeColor(separator_gray)
                c.setLineWidth(1)
                c.line(margin, y, width - margin, y)
                y -= 18

        # Spațiu după listă
        y -= 12

        # Separator subțire după fiecare buclă
        c.setStrokeColor(separator_gray)
        c.setLineWidth(0.5)
        c.line(margin + 10, y + 8, width - margin - 10, y + 8)

        if y < margin + 80:
            c.showPage()
            y = height - margin
            c.setStrokeColor(separator_gray)
            c.setLineWidth(1)
            c.line(margin, y, width - margin, y)
            y -= 18

    # ---- Secțiunea “Photos”: pagină nouă ----
    c.showPage()
    y = height - margin

    # Head “Photos” în cutie albăstrui‐pastel
    c.setFillColor(alabaster_blue)
    c.rect(margin / 2, y - 40, width - margin, 40, fill=True, stroke=False)
    c.setFillColor(office_blue)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y - 26, "Photos")
    y -= 60

    photo_folder = data.get("photo_folder")
    if photo_folder:
        photos_dir = os.path.join(report_folder, photo_folder)
        if os.path.isdir(photos_dir):
            for fname in sorted(os.listdir(photos_dir)):
                lower = fname.lower()
                if lower.endswith((".png", ".jpg", ".jpeg", ".gif")):
                    img_path = os.path.join(photos_dir, fname)
                    base, _ = os.path.splitext(fname)
                    txt_path = os.path.join(photos_dir, base + ".txt")

                    # 1) Desenăm imaginea, scalată la max. 200px înălțime
                    try:
                        img_reader = ImageReader(img_path)
                        img_w, img_h = img_reader.getSize()
                        max_w = width - 2 * margin
                        max_h = 200
                        scale = min(max_w / img_w, max_h / img_h, 1)
                        draw_w = img_w * scale
                        draw_h = img_h * scale
                        x_img = margin
                        y_img = y - draw_h

                        if y_img < margin:
                            c.showPage()
                            y = height - margin
                            y_img = y - draw_h

                        c.drawImage(img_reader, x_img, y_img, width=draw_w, height=draw_h)
                        y = y_img - 10
                    except Exception:
                        pass

                    # 2) Citim descrierea și sursa din fișierul .txt
                    desc = ""
                    src_txt = ""
                    if os.path.exists(txt_path):
                        try:
                            with open(txt_path, "r", encoding="utf-8") as ftxt:
                                lines = ftxt.read().splitlines()
                                if lines:
                                    desc = lines[0].replace("Description:", "").strip()
                                if len(lines) > 1:
                                    src_txt = lines[1].replace("Source:", "").strip()
                        except Exception:
                            pass

                    # 3) Scriem “Description:” cu albastru office și “Source:” cu gri
                    c.setFillColor(office_blue)
                    c.setFont("Helvetica-Bold", 11)
                    if desc:
                        c.drawString(margin, y, f"Description: {desc}")
                        y -= 16

                    c.setFillColor(dark_gray)
                    c.setFont("Helvetica", 10)
                    if src_txt:
                        c.drawString(margin, y, f"Source: {src_txt}")
                        y -= 20

                    # Separator subțire între poze
                    c.setStrokeColor(separator_gray)
                    c.setLineWidth(0.5)
                    c.line(margin, y + 10, width - margin, y + 10)

                    if y < margin + 80:
                        c.showPage()
                        y = height - margin

    c.save()


def get_next_available_name(base_name):
    i = 1
    while os.path.exists(os.path.join("OSINT_REPORTS", f"{base_name}({i})")):
        i += 1
    return f"{base_name}({i})"
