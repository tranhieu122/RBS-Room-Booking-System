"""Email notification helper – su dung SMTP (Gmail App Password).

De kich hoat:
1. Dat EMAIL_ENABLED=true trong file .env
2. Dien SMTP_USER, SMTP_PASSWORD (App Password tu Google Account)

Neu EMAIL_ENABLED=false (mac dinh), moi lenh gui mail se bi bo qua yên lang.
"""
from __future__ import annotations
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# ── Doc cau hinh tu bien moi truong (da duoc load_dotenv() nan truoc) ─────────
_ENABLED  = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
_PORT     = int(os.getenv("SMTP_PORT", "587"))
_USER     = os.getenv("SMTP_USER",     "")
_PASSWORD = os.getenv("SMTP_PASSWORD", "")
_FROM     = os.getenv("SMTP_FROM",     _USER)


def send_booking_notification(
    to_email: str,
    user_name: str,
    booking_id: str,
    room_id: str,
    booking_date: str,
    slot: str,
    new_status: str,
) -> bool:
    """Gui email thong bao khi trang thai dat phong thay doi.

    Tra ve True neu gui thanh cong, False neu bi tat hoac co loi.
    """
    if not _ENABLED:
        logger.debug("Email disabled – bo qua thong bao cho %s", to_email)
        return False
    if not to_email or "@" not in to_email:
        return False

    status_label = {
        "Da duyet": "DA DUOC DUYET ✅",
        "Tu choi":  "BI TU CHOI ❌",
    }.get(new_status, new_status.upper())

    subject = f"[QLPH] Yeu cau dat phong {booking_id} – {status_label}"

    html_body = f"""
<html><body style="font-family:Arial,sans-serif;color:#222;">
<div style="max-width:540px;margin:auto;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
  <div style="background:#1a2f5e;padding:20px 28px;">
    <h2 style="color:white;margin:0;">He Thong Quan Ly Dat Phong Hoc</h2>
    <p style="color:#93c5fd;margin:4px 0 0;">Nhom 24 – Thong bao tu dong</p>
  </div>
  <div style="padding:24px 28px;">
    <p>Xin chao <strong>{user_name}</strong>,</p>
    <p>Yeu cau dat phong cua ban vua duoc cap nhat:</p>
    <table style="border-collapse:collapse;width:100%;margin:16px 0;">
      <tr style="background:#f1f5f9;">
        <td style="padding:8px 12px;font-weight:bold;">Ma dat phong</td>
        <td style="padding:8px 12px;">{booking_id}</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;font-weight:bold;">Phong hoc</td>
        <td style="padding:8px 12px;">{room_id}</td>
      </tr>
      <tr style="background:#f1f5f9;">
        <td style="padding:8px 12px;font-weight:bold;">Ngay dat</td>
        <td style="padding:8px 12px;">{booking_date}</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;font-weight:bold;">Ca hoc</td>
        <td style="padding:8px 12px;">{slot}</td>
      </tr>
      <tr style="background:#f1f5f9;">
        <td style="padding:8px 12px;font-weight:bold;">Trang thai moi</td>
        <td style="padding:8px 12px;font-weight:bold;color:{'#15803d' if new_status=='Da duyet' else '#dc2626'};">
          {status_label}
        </td>
      </tr>
    </table>
    {'<p style="color:#15803d;">✅ Phong da san sang – vui long den dung gio.</p>'
     if new_status == "Da duyet"
     else '<p style="color:#dc2626;">❌ Yeu cau bi tu choi. Vui long lien he Admin de biet them chi tiet.</p>'}
  </div>
  <div style="background:#f8fafc;padding:12px 28px;font-size:12px;color:#94a3b8;">
    Email nay duoc gui tu dong boi He Thong QLPH – Nhom 24.
    Vui long khong tra loi email nay.
  </div>
</div>
</body></html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = _FROM
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(_HOST, _PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(_USER, _PASSWORD)
            server.sendmail(_FROM, [to_email], msg.as_bytes())
        logger.info("Email thong bao gui thanh cong toi %s", to_email)
        return True
    except Exception as exc:
        logger.warning("Khong gui duoc email toi %s: %s", to_email, exc)
        return False
