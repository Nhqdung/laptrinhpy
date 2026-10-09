import os
import re
import json
import hashlib
import random
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "users.json"
MAPS_FILE = DATA_DIR / "maps.json"
HISTORY_FILE = DATA_DIR / "history.json"


class DataManager:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.MAX_FAILED_ATTEMPTS = 5
        self.LOCKOUT_DURATION_MINUTES = 5
        self.ensure_default_files()

    def _hash_password(self, password: str, salt: bytes = None) -> tuple:
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt.hex(), key.hex()

    def _verify_password(self, password: str, salt_hex: str, key_hex: str) -> bool:
        try:
            salt = bytes.fromhex(salt_hex)
            _, check_key_hex = self._hash_password(password, salt)
            return check_key_hex == key_hex
        except Exception:
            return False

    def _read_json(self, file_path: Path):
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, file_path: Path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def ensure_default_files(self):
        if not USERS_FILE.exists() or USERS_FILE.stat().st_size == 0:
            salt_hex, hash_hex = self._hash_password("Admin@123456")
            default_users = [{
                "user_id": "U001",
                "username": "admin",
                "email": "admin@gmail.com",
                "phone": "0987654321",
                "salt": salt_hex,
                "password_hash": hash_hex,
                "failed_attempts": 0,
                "lock_until": None,
                "role": "admin",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "otp_code": None,
                "otp_expiry": None,
                "is_verified": True
            }]
            self._write_json(USERS_FILE, default_users)

        if not MAPS_FILE.exists() or MAPS_FILE.stat().st_size == 0:
            default_maps = [{
                "map_id": "MAP_SAMPLE",
                "map_name": "Bản đồ mẫu",
                "author": "admin",
                "rows": 25,
                "cols": 35,
                "start": [2, 2],
                "end": [20, 30],
                "walls": [[5, i] for i in range(5, 25)],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            self._write_json(MAPS_FILE, default_maps)

        if not HISTORY_FILE.exists() or HISTORY_FILE.stat().st_size == 0:
            self._write_json(HISTORY_FILE, [])

    def validate_password_strength(self, password: str):
        if len(password) < 8:
            return False, "Mật khẩu phải dài tối thiểu 8 ký tự!"
        if not re.search(r"[A-Z]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 chữ hoa (A-Z)!"
        if not re.search(r"[a-z]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 chữ thường (a-z)!"
        if not re.search(r"[0-9]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 số (0-9)!"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%...)!"
        return True, "Hợp lệ"
    
    def validate_username(self, username: str):
        """Tên tài khoản: Viết liền không khoảng trắng, in hoa chữ cái đầu."""
        if not username:
            return False, "Tên tài khoản không được để trống!"
        if " " in username:
            return False, "Tên tài khoản phải viết liền, không được chứa khoảng trắng!"
        if not re.match(r"^[a-z][a-zA-Z0-9_]{2,}$", username):
            return False, "Tên tài khoản phải bắt đầu bằng chữ cái, chỉ gồm chữ, số hoặc dấu gạch dưới (tối thiểu 3 ký tự)!"
        return True, "Hợp lệ"
  
    
    def register_user(self, username: str, password: str, email: str = "", phone: str = ""):
        username = username.strip()

        # 1. Kiểm tra Tên tài khoản
        is_user_valid, user_msg = self.validate_username(username)
        if not is_user_valid:
            return False, user_msg, None

        # 2. Kiểm tra Email
        is_email_valid, email_msg = self.validate_email(email)
        if not is_email_valid:
            return False, email_msg, None

        # 3. Kiểm tra Số điện thoại
        is_phone_valid, phone_msg = self.validate_phone(phone)
        if not is_phone_valid:
            return False, phone_msg, None

        # 4. Kiểm tra Mật khẩu mạnh
        is_pass_valid, pass_msg = self.validate_password_strength(password)
        if not is_pass_valid:
            return False, pass_msg, None

        users = self._read_json(USERS_FILE)
        
        # Kiểm tra trùng tên tài khoản (không phân biệt hoa thường)
        if any(u.get("username", "").lower() == username.lower() for u in users):
            return False, "Tài khoản đã tồn tại trên hệ thống!", None

        # Kiểm tra trùng Email hoặc SĐT đã đăng ký
        clean_email = email.strip().lower()
        clean_phone = phone.strip()
        if any(u.get("email", "").lower() == clean_email for u in users):
            return False, "Email này đã được sử dụng cho một tài khoản khác!", None
        if any(u.get("phone", "") == clean_phone for u in users):
            return False, "Số điện thoại này đã được sử dụng cho một tài khoản khác!", None

        salt_hex, key_hex = self._hash_password(password)
        otp = f"{random.randint(100000, 999999)}"
        expiry = datetime.now() + timedelta(minutes=5)
        new_user = {
            "user_id": f"U{len(users) + 1:03d}",
            "username": username,
            "email": clean_email,
            "phone": clean_phone,
            "salt": salt_hex,
            "password_hash": key_hex,
            "failed_attempts": 0,
            "lock_until": None,
            "role": "user",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "otp_code": otp,
            "otp_expiry": expiry.strftime("%Y-%m-%d %H:%M:%S"),
            "is_verified": False
        }
        users.append(new_user)
        self._write_json(USERS_FILE, users)
        return True, "Đăng ký thành công! Vui lòng xác thực email bằng mã OTP để hoàn tất.", otp

    def confirm_email_otp(self, username: str, otp_input: str):
        """Xác thực email bằng mã OTP được sinh lúc đăng ký."""
        users = self._read_json(USERS_FILE)
        user = next((u for u in users if u.get("username") == username), None)

        if not user:
            return False, "Tài khoản không tồn tại trên hệ thống!"
        if user.get("is_verified"):
            return True, "Tài khoản đã được xác thực trước đó."

        saved_otp = user.get("otp_code")
        expiry_str = user.get("otp_expiry")
        if not saved_otp or not expiry_str:
            return False, "Chưa có yêu cầu xác thực nào cho tài khoản này!"

        if datetime.now() > datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S"):
            return False, "Mã xác nhận đã hết hạn! Vui lòng đăng ký lại."

        if str(otp_input).strip() != str(saved_otp):
            return False, "Mã xác nhận không chính xác!"

        user["is_verified"] = True
        user["otp_code"] = None
        user["otp_expiry"] = None
        self._write_json(USERS_FILE, users)
        return True, "Xác thực email thành công! Bây giờ bạn có thể đăng nhập."
 
    
    def authenticate_user(self, username: str, password: str):
        users = self._read_json(USERS_FILE)
        user = next((u for u in users if u.get("username") == username), None)

        if not user:
            return False, "Tài khoản hoặc mật khẩu không chính xác!"

        if not user.get("is_verified", True):
            return False, "Tài khoản chưa xác thực email! Vui lòng nhập mã OTP đã gửi trước khi đăng nhập."

        now = datetime.now()
        if user.get("lock_until"):
            try:
                lock_time = datetime.strptime(user["lock_until"], "%Y-%m-%d %H:%M:%S")
                if now < lock_time:
                    remaining_sec = int((lock_time - now).total_seconds())
                    return False, f"Tài khoản bị khóa tạm thời. Thử lại sau {remaining_sec}s!"
                else:
                    user["lock_until"] = None
                    user["failed_attempts"] = 0
            except Exception:
                user["lock_until"] = None
                user["failed_attempts"] = 0

        salt = user.get("salt")
        pwd_hash = user.get("password_hash")
        if not salt or not pwd_hash:
            return False, "Dữ liệu tài khoản bị lỗi!"

        if self._verify_password(password, salt, pwd_hash):
            user["failed_attempts"] = 0
            user["lock_until"] = None
            self._write_json(USERS_FILE, users)
            return True, user
        else:
            user["failed_attempts"] = user.get("failed_attempts", 0) + 1
            if user["failed_attempts"] >= self.MAX_FAILED_ATTEMPTS:
                lock_until = now + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
                user["lock_until"] = lock_until.strftime("%Y-%m-%d %H:%M:%S")
                self._write_json(USERS_FILE, users)
                return False, f"Nhập sai {self.MAX_FAILED_ATTEMPTS} lần liên tiếp. Khóa tài khoản trong {self.LOCKOUT_DURATION_MINUTES} phút!"
            self._write_json(USERS_FILE, users)
            attempts_left = self.MAX_FAILED_ATTEMPTS - user["failed_attempts"]
            return False, f"Sai mật khẩu! Còn {attempts_left} lần thử."

    # --- CHỨC NĂNG QUÊN MẬT KHẨU & OTP ---
    def request_password_reset(self, username: str, contact_input: str):
        """Kiểm tra email hoặc số điện thoại, sinh OTP và trả về kết quả."""
        users = self._read_json(USERS_FILE)
        user = next((u for u in users if u.get("username") == username), None)

        if not user:
            return False, "Tài khoản không tồn tại trên hệ thống!", None

        contact = contact_input.strip()
        user_email = user.get("email", "").strip()
        user_phone = user.get("phone", "").strip()

        # Kiểm tra trùng với Email HOẶC Số điện thoại
        if contact not in (user_email, user_phone) or not contact:
            return False, "Email hoặc Số điện thoại không khớp với tài khoản!", None

        # Sinh mã ngẫu nhiên 6 chữ số
        otp = f"{random.randint(100000, 999999)}"
        expiry = datetime.now() + timedelta(minutes=5)

        user["otp_code"] = otp
        user["otp_expiry"] = expiry.strftime("%Y-%m-%d %H:%M:%S")
        self._write_json(USERS_FILE, users)

        return True, f"Đã gửi mã xác nhận đến {contact}!", otp

    def verify_otp_and_reset_password(self, username: str, otp_input: str, new_password: str):
        """Xác minh OTP và cập nhật mật khẩu mới."""
        users = self._read_json(USERS_FILE)
        user = next((u for u in users if u.get("username") == username), None)

        if not user:
            return False, "Tài khoản không tồn tại!"

        saved_otp = user.get("otp_code")
        expiry_str = user.get("otp_expiry")

        if not saved_otp or not expiry_str:
            return False, "Chưa gửi yêu cầu lấy lại mật khẩu!"

        if datetime.now() > datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S"):
            user["otp_code"] = None
            user["otp_expiry"] = None
            self._write_json(USERS_FILE, users)
            return False, "Mã xác nhận đã hết hạn! Vui lòng gửi lại."

        if str(saved_otp) != str(otp_input).strip():
            return False, "Mã xác nhận không chính xác!"

        is_valid, msg = self.validate_password_strength(new_password)
        if not is_valid:
            return False, msg

        salt_hex, key_hex = self._hash_password(new_password)
        user["salt"] = salt_hex
        user["password_hash"] = key_hex
        user["failed_attempts"] = 0
        user["lock_until"] = None
        user["otp_code"] = None
        user["otp_expiry"] = None
        self._write_json(USERS_FILE, users)
        return True, "Đặt lại mật khẩu thành công! Hãy đăng nhập lại."
  
    # ================= CHỨC NĂNG XUẤT DỮ LIỆU TÀI KHOẢN ===========
    def get_registered_users(self):
        """Lấy danh sách tất cả tài khoản đã đăng ký (chỉ lấy thông tin công khai)."""
        users = self._read_json(USERS_FILE)
        safe_users = []
        for u in users:
            safe_users.append({
                "user_id": u.get("user_id"),
                "username": u.get("username"),
                "role": u.get("role"),
                "email": u.get("email", ""),
                "phone": u.get("phone", ""),
                "created_at": u.get("created_at")
            })
        return safe_users
    
    
    # ==================== KIỂM TRA RÀNG BUỘC SĐT & EMAIL ====================

    def validate_phone(self, phone: str):
        """Số điện thoại phải đủ đúng 10 số, không hơn không kém, bắt đầu bằng số 0."""
        phone = phone.strip()
        if not phone:
            return False, "Số điện thoại không được để trống!"
        # ^0\d{9}$ : bắt đầu bằng 0, tiếp theo là đúng 9 chữ số
        if not re.match(r"^0\d{9}$", phone):
            return False, "Số điện thoại không hợp lệ! (Phải đủ đúng 10 số và bắt đầu bằng số 0)"
        return True, "Hợp lệ"

    def validate_email(self, email: str):
        """Email phải đúng định dạng chuẩn và thuộc domain phổ biến hoặc .edu.vn."""
        email = email.strip().lower()
        if not email:
            return False, "Email không được để trống!"

        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", email):
            return False, "Email không đúng định dạng!"

        domain = email.split("@", 1)[1]
        allowed_domains = ("gmail.com", "outlook.com", "hotmail.com", "yahoo.com")
        if not (domain in allowed_domains or domain.endswith(".edu.vn")):
            return False, ("Email phải thuộc gmail.com, outlook.com, hotmail.com, yahoo.com "
                            "hoặc email trường học (đuôi .edu.vn)!")

        return True, "Hợp lệ"
    
    # ==================== QUẢN LÝ DỮ LIỆU BẢN ĐỒ ====================

    def save_map(self, map_data: dict):
        """Lưu bản đồ và kiểm tra tính hợp lệ dữ liệu biên."""
        rows = map_data.get("rows", 0)
        cols = map_data.get("cols", 0)
        start = map_data.get("start")
        end = map_data.get("end")

        if rows <= 0 or cols <= 0:
            return False, "Kích thước lưới không hợp lệ (phải > 0)!"
        if not start or not end:
            return False, "Bản đồ phải có đủ điểm bắt đầu và điểm kết thúc!"
        if start == end:
            return False, "Điểm bắt đầu và kết thúc không được trùng nhau!"

        maps = self._read_json(MAPS_FILE)
        map_id = map_data.get("map_id") or f"MAP_{len(maps) + 1:03d}"
        map_data["map_id"] = map_id
        map_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Cập nhật nếu trùng ID, thêm mới nếu chưa có
        maps = [m for m in maps if m.get("map_id") != map_id]
        maps.append(map_data)
        self._write_json(MAPS_FILE, maps)
        return True, "Lưu bản đồ thành công!"

    def get_all_maps(self):
        """Lấy toàn bộ danh sách bản đồ đã lưu."""
        return self._read_json(MAPS_FILE)

    def load_map_by_id(self, map_id: str):
        """Tải chi tiết một bản đồ theo ID."""
        maps = self._read_json(MAPS_FILE)
        for m in maps:
            if m.get("map_id") == map_id:
                return m
        return None

    def log_run_history(self, log_entry: dict):
        """Ghi nhận lịch sử mô phỏng phục vụ thống kê."""
        history = self._read_json(HISTORY_FILE)
        log_entry["run_id"] = f"RUN_{len(history) + 1:04d}"
        log_entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append(log_entry)
        self._write_json(HISTORY_FILE, history)
        return True