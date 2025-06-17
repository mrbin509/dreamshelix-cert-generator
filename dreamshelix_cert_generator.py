import gspread
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from fpdf import FPDF
from datetime import date
import os

# === CONFIGURATION ===
GOOGLE_SHEET_NAME = "DreamsHelix Certificates"
CERT_TEMPLATE = "cert_templates/base_template.png"  # Put your certificate background image here
QR_URL_PREFIX = "https://script.google.com/macros/s/YOUR_APPS_SCRIPT_QR_URL/exec?cert_id="

# === FOLDER SETUP ===
os.makedirs("certificates", exist_ok=True)
os.makedirs("qr_codes", exist_ok=True)

# === GOOGLE SHEETS AUTH ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1
data = sheet.get_all_records()

# === GENERATE CERTIFICATE ID ===
def generate_cert_id(batch, course, index):
    return f"{batch}{course[:4].upper()}{str(index).zfill(3)}"

# === QR CODE GENERATION ===
def generate_qr(cert_id):
    qr_url = QR_URL_PREFIX + cert_id
    img = qrcode.make(qr_url)
    path = f"qr_codes/{cert_id}.png"
    img.save(path)
    return path

# === GENERATE PDF CERTIFICATE ===
def generate_certificate_pdf(name, cert_id, qr_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Certificate template image (A4 size)
    pdf.image(CERT_TEMPLATE, x=0, y=0, w=210, h=297)

    # Student Name Positioning
    pdf.set_font("Arial", "B", 18)
    pdf.set_xy(60, 120)  # Adjust this based on your template
    pdf.cell(100, 10, name, 0, 1, "C")

    # QR Code Positioning
    pdf.image(qr_path, x=160, y=240, w=30)

    # Save PDF
    pdf_path = f"certificates/{cert_id}.pdf"
    pdf.output(pdf_path)

    return pdf_path

# === MAIN SCRIPT ===
for i, row in enumerate(data):
    name = row["Name"]
    email = row["Email"]
    course = row["Course"]
    batch = row["Batch"]

    cert_id = generate_cert_id(batch, course, i+1)
    qr_path = generate_qr(cert_id)
    pdf_path = generate_certificate_pdf(name, cert_id, qr_path)

    # Update Sheet (columns: F, G, H => 6, 7, 8)
    sheet.update_cell(i + 2, 6, cert_id)                # Certificate ID
    sheet.update_cell(i + 2, 7, str(date.today()))      # Issue Date
    sheet.update_cell(i + 2, 8, "Issued")               # Status

    print(f"✅ Certificate generated for {name} → {pdf_path}")