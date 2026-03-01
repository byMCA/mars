from flask import Flask
import requests
import os

app = Flask(__name__)

# ==============================
# ENV'den API Ayarları
# ==============================
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "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")
MAIL_FROM = os.getenv("MAIL_FROM", "marsplatformsocial@marsofficial.com")
# ==============================

def send_mail_via_api(to_email):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"name": "Mars Platform 🚀", "email": MAIL_FROM},
        "to": [{"email": to_email}],
        "subject": "Mars Platform Test Mail via API",
        "htmlContent": """
        <html>
            <body>
                <h2>Mars Platform 🚀</h2>
                <p>Hello! This is a test email sent via Brevo API.</p>
            </body>
        </html>
        """,
        "textContent": "Hello! This is a test email sent via Brevo API."
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201, 202]:
        return "✅ Mail başarıyla gönderildi via API"
    else:
        return f"❌ Mail gönderilemedi via API: {response.status_code} - {response.text}"

@app.route("/send-test")
def send_mail_route():
    result = send_mail_via_api("akta.cemal@gmail.com")
    return f"<h2>{result}</h2>"

@app.route("/")
def index():
    return "<h1>Mars Platform Mail Test</h1><p>Go to <a href='/send-test'>/send-test</a> to send test mail.</p>"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)