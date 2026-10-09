"""
email_service.py
-----------------
Gửi email OTP thật qua Gmail SMTP. Cần file .env ở thư mục gốc project với:
    EMAIL_SENDER=email_app_cua_ban@gmail.com
    EMAIL_APP_PASSWORD=chuoi16kytu_khong_co_khoang_trang

Lưu ý báo cáo: ghi rõ dùng Gmail SMTP (smtp.gmail.com) làm dịch vụ gửi mail bên ngoài.
"""

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()  # đọc file .env cùng cấp main.py

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


class EmailServiceError(Exception):
    """Ngoại lệ khi gửi email thất bại (thiếu cấu hình, sai mật khẩu app, mất mạng...)."""
    pass


def send_otp_email(to_email: str, otp: str) -> None:
    sender = os.environ.get("EMAIL_SENDER")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    if not sender or not app_password:
        raise EmailServiceError(
            "Chưa cấu hình EMAIL_SENDER / EMAIL_APP_PASSWORD trong file .env"
        )

    subject = "Mã xác nhận đặt lại mật khẩu - Ứng dụng tìm đường trên lưới"
    body = (
        f"Mã OTP của bạn là: {otp}\n\n"
        f"Mã có hiệu lực trong 5 phút. Nếu bạn không yêu cầu đặt lại mật khẩu, "
        f"hãy bỏ qua email này."
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.login(sender, app_password)
            server.sendmail(sender, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailServiceError(
            "Sai email hoặc App Password. Kiểm tra lại file .env."
        )
    except smtplib.SMTPException as e:
        raise EmailServiceError(f"Lỗi gửi email: {e}")
    except OSError:
        raise EmailServiceError("Không thể kết nối tới máy chủ SMTP (kiểm tra mạng).")
