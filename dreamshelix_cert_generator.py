import gspread
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from fpdf import FPDF
from datetime import date
import os

# === CONFIGURATION ===
GOOGLE_SHEET_NAME = "DreamsHelix Certificates"
CERT_TEMPLATE = "cert_templates.jpg"
QR_URL_PREFIX = "https://check.dreamshelix.com/verify?cert_id="

# === FOLDER SETUP ===
os.makedirs("certificates", exist_ok=True)
os.makedirs("qr_codes", exist_ok=True)

# === GOOGLE SHEETS AUTH ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1
data = sheet.get_all_records()

# === CERTIFICATE ID FORMAT ===
def generate_cert_id(index):
    return f"DH-PWD-{str(index).zfill(5)}"

# === QR CODE GENERATION ===
def generate_qr(cert_id):
    qr_url = QR_URL_PREFIX + cert_id
    img = qrcode.make(qr_url)
    path = f"qr_codes/{cert_id}.png"
    img.save(path)
    return path

# === PDF CLASS ===
class CertificatePDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

# === CERTIFICATE GENERATION ===
def generate_certificate_pdf(name, cert_id, qr_path):
    # True A4 landscape in points
    pdf = CertificatePDF(orientation='L', unit='pt', format='A4')
    pdf.add_page()

    # A4 Landscape = 842pt × 595pt
    pdf.image(CERT_TEMPLATE, x=0, y=0, w=842, h=595)

    # === Fonts ===
    pdf.add_font('GreatVibes', '', 'GreatVibes-Regular.ttf', uni=True)
    pdf.add_font('Poppins', '', 'Poppins-Regular.ttf', uni=True)

    # === NAME (below “This is to certify that”) ===
    pdf.set_font('GreatVibes', '', 48)
    pdf.set_xy(0, 240)  # Y = slightly below "This is to certify that"
    pdf.cell(842, 40, name, align='C')

    # === CERTIFICATE ID (right of "Certificate ID -") ===
    pdf.set_font('Poppins', '', 12)
    cert_id_x = 300  # Right after "Certificate ID -"
    cert_id_y = 160
    pdf.set_xy(cert_id_x, cert_id_y)
    pdf.cell(200, 20, cert_id)

    # === QR Code ===
    pdf.image(qr_path, x=30, y=480, w=80, h=80)

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
    roll = row.get("Roll No", f"R{i+1:03}")

    cert_id = generate_cert_id(i + 1)
    qr_path = generate_qr(cert_id)
    pdf_path = generate_certificate_pdf(name, cert_id, qr_path)

    # Update Sheet
    sheet.update_cell(i + 2, 6, cert_id)               # Certificate ID
    sheet.update_cell(i + 2, 7, str(date.today()))     # Issue Date
    sheet.update_cell(i + 2, 8, "Issued")              # Status

    print(f"✅ Certificate generated for {name} → {pdf_path}")
