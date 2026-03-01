import os
import random
import string
from datetime import datetime

import requests

# Brevo API ayarları (ENV varsa onu kullanır, yoksa gömülü varsayılan)
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "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")
MAIL_FROM = os.getenv("MAIL_FROM", "marsplatformsocial@gmail.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Mars Platform 🚀")

def generate_mars_id(origin_region):
    """
    Kullanıcının kökenine ve yıla göre benzersiz bir Mars Vatandaşlık ID'si üretir.
    Format: MARS-[YIL]-[BÖLGE]-[HASH]
    Örnek: MARS-2026-EU-X92F
    """
    
    # 1. Mevcut Yılı Al
    year = datetime.now().year
    
    # 2. Bölge Kodlarını Eşleştir
    region_map = {
        "Avrupa Federasyonu": "EU",
        "Asya Pasifik": "AP",
        "Amerika": "AM",
        "Afrika Birleşik Devletleri": "AF",
        "Diğer": "UN" # Unknown (Bilinmeyen)
    }
    
    # Gelen bölge adını koda çevir, bulamazsa 'UN' yap
    code = region_map.get(origin_region, "UN")
    
    # 3. 4 Haneli Rastgele Kriptografik Sonek Oluştur (Harf + Rakam)
    chars = string.ascii_uppercase + string.digits
    unique_suffix = ''.join(random.choices(chars, k=4))
    
    # 4. Parçaları Birleştir
    mars_id = f"MARS-{year}-{code}-{unique_suffix}"
    
    return mars_id


def generate_reset_code(length: int = 6) -> str:
    """Produce a numeric verification code for password resets."""
    return ''.join(random.choices(string.digits, k=length))


def send_reset_email(recipient_email: str, verification_code: str, portal_link: str | None = None) -> bool:
    """Send reset code directly via Brevo API."""
    reset_link = portal_link or ''
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    text_body = (
        "Mars Platform | Şifre Sıfırlama\n\n"
        f"Doğrulama Kodu: {verification_code}\n"
        "Geçerlilik Süresi: 10 dakika\n"
        + (f"Sıfırlama Bağlantısı: {reset_link}\n" if reset_link else "")
        + "\nBu işlemi siz yapmadıysanız bu e-postayı dikkate almayın."
    )

    action_button = (
        f'<a href="{reset_link}" style="display:inline-block;padding:14px 28px;background:linear-gradient(90deg,#ff4f6d 0%,#ff9966 100%);color:#0a0c16;text-decoration:none;font-weight:800;font-size:12px;letter-spacing:0.18em;text-transform:uppercase;border-radius:999px;box-shadow:0 10px 30px rgba(255,79,109,0.35);">Şifre Paneline Git</a>'
        if reset_link else ''
    )

    html_body = f"""
        <!DOCTYPE html>
        <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Mars Platform | Şifre Sıfırlama</title>
            </head>
            <body style="margin:0;padding:0;background:#05070f;font-family:Segoe UI,Arial,sans-serif;color:#f5f7ff;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:radial-gradient(circle at 20% 0%,#1c2d67 0%,#0b1025 38%,#05070f 100%);padding:28px 12px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:620px;background:#0b1022;border:1px solid rgba(255,255,255,0.14);border-radius:22px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.55);">
                                <tr>
                                    <td style="padding:28px 34px 18px;background:linear-gradient(120deg,rgba(77,231,255,0.2) 0%,rgba(255,79,109,0.16) 48%,rgba(255,173,96,0.2) 100%);">
                                        <p style="margin:0 0 10px;color:#8deeff;font-size:11px;letter-spacing:0.42em;text-transform:uppercase;">Mars Security Channel</p>
                                        <h1 style="margin:0;font-size:30px;line-height:1.2;color:#ffffff;">Şifre Sıfırlama Talebi</h1>
                                        <p style="margin:14px 0 0;color:#d6dcff;font-size:14px;line-height:1.7;">
                                            Hesabınız için tek kullanımlık doğrulama kodu oluşturuldu. Kod yalnızca
                                            <strong style="color:#ffb17a;">10 dakika</strong> geçerlidir.
                                        </p>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:26px 34px 14px;">
                                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid rgba(255,255,255,0.16);border-radius:16px;background:linear-gradient(180deg,#101734 0%,#0a1024 100%);">
                                            <tr>
                                                <td align="center" style="padding:18px 12px 6px;">
                                                    <p style="margin:0;color:#96a5da;font-size:11px;letter-spacing:0.36em;text-transform:uppercase;">Doğrulama Kodu</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="center" style="padding:4px 12px 22px;">
                                                    <p style="margin:0;color:#ffffff;font-size:46px;line-height:1;letter-spacing:0.28em;font-weight:800;text-shadow:0 0 26px rgba(120,177,255,0.4);">{verification_code}</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:8px 34px 28px;">
                                        <p style="margin:0 0 20px;color:#b3bfeb;font-size:13px;line-height:1.75;">
                                            Kodu şifre sıfırlama ekranına girerek yeni parolanızı belirleyebilirsiniz.
                                        </p>
                                        <div style="text-align:center;">{action_button}</div>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:18px 34px;background:#070b18;border-top:1px solid rgba(255,255,255,0.1);">
                                        <p style="margin:0;color:#7e8bb8;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;">Mars Platform • Automated Security Mail</p>
                                        <p style="margin:10px 0 0;color:#9aa7d6;font-size:12px;line-height:1.65;">
                                            Bu işlemi siz yapmadıysanız hesabınız güvendedir, e-postayı yok sayabilirsiniz.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

    payload = {
        "sender": {"name": MAIL_FROM_NAME, "email": MAIL_FROM},
        "to": [{"email": recipient_email}],
        "subject": "Mars Kolonisi | Şifre Sıfırlama Kodu",
        "htmlContent": html_body,
        "textContent": text_body
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code in [200, 201, 202]:
            return True
        print(f"Brevo API mail hatası: {response.status_code} - {response.text}")
        return False
    except Exception as exc:
        print(f"Brevo API istek hatası: {exc}")
        return False

if __name__ == "__main__":
    # Test amaçlı kendi mail adresini yazıp gönderimi deneyebilirsin
    test_email = MAIL_FROM
    test_code = generate_reset_code()
    print(f"Mars ID (EU): {generate_mars_id('Avrupa Federasyonu')}")
    print(f"Mars ID (AP): {generate_mars_id('Asya Pasifik')}")
    
    if test_email:
        print(f"{test_email} adresine test maili gönderiliyor...")
        success = send_reset_email(test_email, test_code)
        if success:
            print("Mail başarıyla gönderildi!")
        else:
            print("Mail gönderilemedi, konsol loglarını kontrol edin.")