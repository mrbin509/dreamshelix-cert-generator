from flask import Flask, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)  # <-- fixed here

# Google Sheet Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("DreamsHelix Certificates").sheet1

# Show loading screen first
@app.route("/")
def loading():
    return render_template("loading.html")

#@app.route('/home')
#def home():
 #   return render_template("scanner.html")  # new template for QR scanner

@app.route('/home')
def verify():
    cert_id = request.args.get("cert_id")
    data = sheet.get_all_records()  # moved inside for freshness
    for row in data:
        if row['Certificate ID'] == cert_id:
            return render_template("scanner.html", row=row)
    return render_template("scanner.html")


@app.route('/verify')
def verify():
    cert_id = request.args.get("cert_id")
    data = sheet.get_all_records()  # moved inside for freshness
    for row in data:
        if row['Certificate ID'] == cert_id:
            return render_template("verified.html", row=row)
    return render_template("not_found.html")