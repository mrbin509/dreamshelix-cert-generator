from flask import Flask, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheet Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("DreamsHelix Certificates").sheet1
data = sheet.get_all_records()

@app.route('/')
def home():
    return "DreamsHelix Certificate Verification System"

@app.route('/verify')
def verify():
    cert_id = request.args.get("cert_id")
    for row in data:
        if row['Certificate ID'] == cert_id:
            return render_template("verified.html", row=row)
    return render_template("not_found.html")
