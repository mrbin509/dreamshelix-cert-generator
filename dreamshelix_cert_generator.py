import gspread
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from fpdf import FPDF
from datetime import date
import os

# === CONFIGURATION ===
GOOGLE_SHEET_NAME = "DreamsHelix Certificates"
CERT_TEMPLATE = "cert_templates.jpg"  # Your certificate background image (A4 landscape)
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
class CertificatePDF(FPDF):
    def header(self):
        pass  # No header

    def footer(self):
        pass  # No footer

def generate_certificate_pdf(name, cert_id, qr_path):
    # A4 landscape: 297 x 210 mm
    pdf = CertificatePDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # Add custom font (Great Vibes)
    pdf.add_font('GreatVibes', '', 'GreatVibes-Regular.ttf', uni=True)
    pdf.set_font('GreatVibes', '', 36)  # Bigger and stylish for the name

    # Certificate template
    pdf.image(CERT_TEMPLATE, x=0, y=0, w=297, h=210)

    # Add Name
    name_y = 100  # Adjust as per your template design
    pdf.set_xy(0, name_y)
    pdf.cell(297, 15, name, border=0, ln=1, align='C')

    # Add QR Code (bottom-left)
    qr_size = 30
    margin = 10
    qr_x = margin
    qr_y = 210 - qr_size - margin
    pdf.image(qr_path, x=qr_x, y=qr_y, w=qr_size, h=qr_size)

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

    cert_id = generate_cert_id(batch, course, i + 1)
    qr_path = generate_qr(cert_id)
    pdf_path = generate_certificate_pdf(name, cert_id, qr_path)

    # Update Sheet (columns: F, G, H => 6, 7, 8)
    sheet.update_cell(i + 2, 6, cert_id)                # Certificate ID
    sheet.update_cell(i + 2, 7, str(date.today()))      # Issue Date
    sheet.update_cell(i + 2, 8, "Issued")               # Status

    print(f"✅ Certificate generated for {name} → {pdf_path}")