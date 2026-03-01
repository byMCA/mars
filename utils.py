import os
import random
import smtplib
import string
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_mars_id(origin_region):
    """
    Kullanıcının kökenine ve yıla göre benzersiz bir Mars Vatandaşlık ID'si üretir.
    Format: MARS-[YIL]-[BÖLGE]-[HASH]
    Örnek: MARS-2026-EU-X92F
    """
    
    # 1. Mevcut Yılı Al
    year = datetime.now().year
    
    # 2. Bölge Kodlarını Eşleştir
    # Formdan gelen 'value' değerleri ile buradakiler eşleşmelidir.
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
    # Örn: A4K9, X1Y2 vb.
    chars = string.ascii_uppercase + string.digits
    unique_suffix = ''.join(random.choices(chars, k=4))
    
    # 4. Parçaları Birleştir
    mars_id = f"MARS-{year}-{code}-{unique_suffix}"
    
    return mars_id


def generate_reset_code(length: int = 6) -> str:
    """Produce a numeric verification code for password resets."""
    return ''.join(random.choices(string.digits, k=length))


def send_reset_email(recipient_email: str, verification_code: str) -> bool:
    """Send the verification code to the given email. Falls back to console logging."""
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = int(os.getenv('MAIL_PORT', '0') or 0)
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_sender = os.getenv('MAIL_FROM', mail_username)
    use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    reset_base_url = os.getenv('RESET_PORTAL_URL', '')
    reset_link = f"{reset_base_url}?email={recipient_email}" if reset_base_url else ''

    plain_body = (
        "Merhaba,\n\n"
        "Şifre sıfırlama talebiniz için doğrulama kodunuz: "
        f"{verification_code}. Kod 10 dakika boyunca geçerlidir."
        + (f"\n\nBağlantı: {reset_link}" if reset_link else "")
    )

    cta_block = ""
    if reset_link:
        cta_block = f"""
        <div style=\"text-align:center;\">
            <a href=\"{reset_link}\" style=\"display:inline-block;padding:14px 32px;border-radius:999px;background:linear-gradient(90deg,#ff5f6d,#ffc371);color:#05060c;font-size:13px;font-weight:700;text-decoration:none;letter-spacing:0.3em;text-transform:uppercase;\">Reset Paneline Git</a>
            <p style=\"margin-top:14px;font-size:11px;color:#6d779c;\">Bağlantı 10 dakika boyunca geçerlidir.</p>
        </div>
        """

    html_body = f"""
    <!DOCTYPE html>
    <html lang=\"tr\">
    <head>
        <meta charset=\"UTF-8\" />
        <title>Mars Kolonisi Şifre Sıfırlama</title>
    </head>
    <body style=\"margin:0;padding:0;background:#05060c;font-family:'Segoe UI',Arial,sans-serif;color:#f5f5f5;\">
        <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:linear-gradient(135deg,#05060c 0%,#101732 40%,#370505 100%);padding:32px 16px;\">
            <tr>
                <td align=\"center\">
                    <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"max-width:540px;border-radius:18px;background:#0b0f1f;border:1px solid rgba(255,255,255,0.1);box-shadow:0 25px 65px rgba(0,0,0,0.65);overflow:hidden;\">
                        <tr>
                            <td style=\"padding:32px 40px 16px;background:radial-gradient(circle at 20% 20%,rgba(0,240,255,0.18),transparent 60%);\">
                                <p style=\"letter-spacing:0.4em;font-size:11px;text-transform:uppercase;color:#4de7ff;margin:0 0 12px;\">Security Channel</p>
                                <h1 style=\"font-size:26px;margin:0;color:#ffffff;\">Şifre Sıfırlama Kodu</h1>
                                <p style=\"font-size:14px;line-height:1.6;color:#cbd5ff;margin:18px 0 0;\">
                                    Koloni kimliğinizi korumak için tek kullanımlık doğrulama kodu oluşturuldu. Bu kod {verification_code}
                                    <strong style=\"color:#ff7b5c;\">10 dakika</strong> boyunca geçerlidir.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style=\"padding:24px 40px 8px;\">
                                <div style=\"text-align:center;border:1px dashed rgba(255,255,255,0.2);padding:18px;border-radius:12px;background:rgba(13,18,41,0.85);\">
                                    <p style=\"margin:0;font-size:12px;text-transform:uppercase;letter-spacing:0.5em;color:#8f9bd1;\">Kodunuz</p>
                                    <p style=\"margin:12px 0 0;font-size:46px;letter-spacing:0.3em;color:#ffffff;font-weight:700;\">{verification_code}</p>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td style=\"padding:8px 40px 32px;\">
                                <p style=\"font-size:13px;line-height:1.7;color:#9da6c6;margin:0 0 18px;\">
                                    Kodunuzu korumalı paneldeki doğrulama alanına girerek yeni erişim anahtarınızı oluşturabilirsiniz.
                                </p>
                                {cta_block}
                            </td>
                        </tr>
                        <tr>
                            <td style=\"padding:24px 40px;background:#070910;border-top:1px solid rgba(255,255,255,0.08);\">
                                <p style=\"margin:0;font-size:11px;color:#5f698d;text-transform:uppercase;letter-spacing:0.4em;\">Mars Security Division</p>
                                <p style=\"margin:12px 0 0;font-size:12px;color:#7f89ad;\">Bu mesaj şifreli quantum kanalı üzerinden iletilmiştir. Kodunuzu kimseyle paylaşmayın.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MIMEMultipart('alternative')
    message['Subject'] = 'Mars Kolonisi | Şifre Sıfırlama Kodu'
    message['From'] = mail_sender or 'no-reply@mars-colony'
    message['To'] = recipient_email
    message.attach(MIMEText(plain_body, 'plain', 'utf-8'))
    message.attach(MIMEText(html_body, 'html', 'utf-8'))

    if not all([mail_server, mail_port, mail_username, mail_password, mail_sender]):
        print('MAIL_* ortam değişkenleri tanımlı olmadığı için kod konsola yazıldı:')
        print(f'Reset code for {recipient_email}: {verification_code}')
        return False

    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            if use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(message)
        return True
    except Exception as exc:
        print(f'Secret key e-postaya gönderilemedi ({exc}). Kod konsola yazıldı: {verification_code}')
        return False

# Test etmek istersen bu dosya tek başına çalıştırıldığında örnek basar
if __name__ == "__main__":
    print(generate_mars_id("Avrupa Federasyonu"))
    print(generate_mars_id("Asya Pasifik"))