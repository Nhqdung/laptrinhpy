"""
Kiểm thử DataManager: ràng buộc dữ liệu, đăng ký, xác thực email, đăng nhập,
quên mật khẩu, lưu/tải bản đồ, lịch sử chạy.

Chạy:  python test_data.py
Script dùng thư mục dữ liệu TẠM nên không làm thay đổi data/users.json thật.
Kết quả in ra dạng bảng (đầu vào, kết quả mong đợi, kết quả thực tế, trạng thái)
để chép thẳng vào bảng kiểm thử trong báo cáo.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import data_manager as dmod

# Trỏ DataManager sang thư mục tạm trước khi tạo đối tượng
TMP_DIR = Path(tempfile.mkdtemp(prefix="pathfinding_test_"))
dmod.DATA_DIR = TMP_DIR
dmod.USERS_FILE = TMP_DIR / "users.json"
dmod.MAPS_FILE = TMP_DIR / "maps.json"
dmod.HISTORY_FILE = TMP_DIR / "history.json"

dm = dmod.DataManager()

results = []


def check(group, case_input, expected, actual, note=""):
    status = "PASS" if expected == actual else "FAIL"
    results.append((group, case_input, expected, actual, status, note))


def section(title):
    print(f"\n==================== {title} ====================")


# ---------------------------------------------------------------- 1. Tên tài khoản
for value, expected in [
    ("sinhvien", True),      # chữ thường vẫn hợp lệ
    ("Sinhvien01", True),
    ("dung_2004", True),
    ("Sinh vien", False),    # có khoảng trắng
    ("SV", False),           # quá ngắn
    ("1abc", False),         # bắt đầu bằng số
    ("", False),             # rỗng
]:
    ok, msg = dm.validate_username(value)
    check("Tên tài khoản", repr(value), expected, ok, msg)

# ---------------------------------------------------------------- 2. Số điện thoại
for value, expected in [
    ("098765432", False),    # 9 số
    ("09876543210", False),  # 11 số
    ("1987654321", False),   # không bắt đầu bằng 0
    ("0987654321", True),
]:
    ok, msg = dm.validate_phone(value)
    check("Số điện thoại", repr(value), expected, ok, msg)

# ---------------------------------------------------------------- 3. Email
for value, expected in [
    ("user@gmail.com", True),
    ("user@yahoo.com", True),
    ("2001250117@huit.edu.vn", True),   # email trường, toàn số
    ("user@fake.com", False),           # domain không được hỗ trợ
    ("abc@@gmail.com", False),          # sai định dạng
    ("", False),
]:
    ok, msg = dm.validate_email(value)
    check("Email", repr(value), expected, ok, msg)

# ---------------------------------------------------------------- 4. Mật khẩu
for value, expected in [
    ("Matkhau@123", True),
    ("yeu", False),
    ("matkhau@123", False),  # thiếu chữ hoa
]:
    ok, msg = dm.validate_password_strength(value)
    check("Mật khẩu", repr(value), expected, ok, msg)

# ---------------------------------------------------------------- 5. Đăng ký + chống trùng
ok, msg, otp = dm.register_user("Nguoidung1", "Matkhau@123", "nguoidung1@gmail.com", "0911000001")
check("Đăng ký", "dữ liệu hợp lệ", True, ok, msg)
check("Đăng ký", "hợp lệ -> có sinh OTP", True, otp is not None)

ok, msg, _ = dm.register_user("nguoidung1", "Matkhau@123", "khac@gmail.com", "0911000002")
check("Đăng ký", "trùng tên (khác hoa/thường)", False, ok, msg)

ok, msg, _ = dm.register_user("Nguoidung2", "Matkhau@123", "nguoidung1@gmail.com", "0911000002")
check("Đăng ký", "trùng email", False, ok, msg)

ok, msg, _ = dm.register_user("Nguoidung2", "Matkhau@123", "nguoidung2@gmail.com", "0911000001")
check("Đăng ký", "trùng số điện thoại", False, ok, msg)

ok, msg, _ = dm.register_user("Nguoidung2", "yeu", "nguoidung2@gmail.com", "0911000002")
check("Đăng ký", "mật khẩu yếu", False, ok, msg)

# ---------------------------------------------------------------- 6. Xác thực email + đăng nhập
ok, msg = dm.authenticate_user("Nguoidung1", "Matkhau@123")
check("Xác thực email", "đăng nhập khi chưa xác thực", False, ok, msg)

ok, msg = dm.confirm_email_otp("Nguoidung1", "000000")
check("Xác thực email", "nhập sai OTP", False, ok, msg)

ok, msg, otp = dm.register_user("Nguoidung3", "Matkhau@123", "nguoidung3@gmail.com", "0911000003")
ok_confirm, msg = dm.confirm_email_otp("Nguoidung3", otp)
check("Xác thực email", "nhập đúng OTP", True, ok_confirm, msg)

ok, msg = dm.authenticate_user("Nguoidung3", "Matkhau@123")
check("Đăng nhập", "đúng tài khoản + mật khẩu (đã xác thực)", True, ok)

ok, msg = dm.authenticate_user("Nguoidung3", "Saimatkhau@1")
check("Đăng nhập", "sai mật khẩu", False, ok, msg)

ok, msg = dm.authenticate_user("KhongTonTai", "Matkhau@123")
check("Đăng nhập", "tài khoản không tồn tại", False, ok, msg)

ok, msg = dm.authenticate_user("admin", "Admin@123456")
check("Đăng nhập", "admin mặc định", True, ok, msg)

# Khóa tài khoản sau nhiều lần sai
ok, msg, otp = dm.register_user("Locktest", "Matkhau@123", "locktest@gmail.com", "0911000004")
dm.confirm_email_otp("Locktest", otp)
for _ in range(dm.MAX_FAILED_ATTEMPTS):
    dm.authenticate_user("Locktest", "Sai@matkhau1")
ok, msg = dm.authenticate_user("Locktest", "Matkhau@123")
check("Đăng nhập", f"đúng mật khẩu sau {dm.MAX_FAILED_ATTEMPTS} lần sai (bị khóa)", False, ok, msg)

# ---------------------------------------------------------------- 7. Quên mật khẩu + OTP
ok, msg, _ = dm.request_password_reset("Nguoidung3", "saiemail@gmail.com")
check("Quên mật khẩu", "email không khớp tài khoản", False, ok, msg)

ok, msg, otp = dm.request_password_reset("Nguoidung3", "nguoidung3@gmail.com")
check("Quên mật khẩu", "email khớp -> sinh OTP", True, ok, msg)

ok, msg = dm.verify_otp_and_reset_password("Nguoidung3", "000000", "NewPass@2026")
check("Quên mật khẩu", "OTP sai", False, ok, msg)

ok, msg = dm.verify_otp_and_reset_password("Nguoidung3", otp, "yeu")
check("Quên mật khẩu", "OTP đúng nhưng mật khẩu mới yếu", False, ok, msg)

ok, msg = dm.verify_otp_and_reset_password("Nguoidung3", otp, "NewPass@2026")
check("Quên mật khẩu", "OTP đúng + mật khẩu mới hợp lệ", True, ok, msg)

ok, msg = dm.authenticate_user("Nguoidung3", "NewPass@2026")
check("Quên mật khẩu", "đăng nhập bằng mật khẩu mới", True, ok, msg)

# ---------------------------------------------------------------- 8. Bản đồ + lịch sử
sample_map = {
    "map_name": "Bản đồ thử nghiệm", "author": "Nguoidung3",
    "rows": 20, "cols": 30, "start": [0, 0], "end": [19, 29],
    "walls": [[1, 1], [1, 2], [1, 3]],
}
ok, msg = dm.save_map(dict(sample_map))
check("Bản đồ", "lưu bản đồ hợp lệ", True, ok, msg)
check("Bản đồ", "đọc lại: có 1 bản đồ", 1, len(dm.get_all_maps()))

ok, msg = dm.save_map({**sample_map, "start": [3, 3], "end": [3, 3]})
check("Bản đồ", "điểm đầu trùng điểm đích", False, ok, msg)

ok, msg = dm.save_map({**sample_map, "rows": 0})
check("Bản đồ", "kích thước lưới = 0 (biên)", False, ok, msg)

ok, msg = dm.save_map({**sample_map, "end": None})
check("Bản đồ", "thiếu điểm đích", False, ok, msg)

map_id = dm.get_all_maps()[0]["map_id"]
check("Bản đồ", "tải theo ID tồn tại", True, dm.load_map_by_id(map_id) is not None)
check("Bản đồ", "tải theo ID không tồn tại", True, dm.load_map_by_id("MAP_999") is None)

check("Lịch sử", "ghi 1 lần chạy thuật toán", True,
      dm.log_run_history({"username": "Nguoidung3", "algorithm": "BFS",
                          "visited_count": 97, "path_length": 19, "elapsed_sec": 0.001}))

# ---------------------------------------------------------------- In bảng kết quả
section("BẢNG KẾT QUẢ KIỂM THỬ")
print(f"{'#':>3} | {'Nhóm':<15} | {'Đầu vào':<48} | {'Mong đợi':<9} | {'Thực tế':<9} | Trạng thái")
print("-" * 112)
for i, (group, case_input, expected, actual, status, _note) in enumerate(results, 1):
    print(f"{i:>3} | {group:<15} | {case_input:<48} | {str(expected):<9} | {str(actual):<9} | {status}")

failed = [r for r in results if r[4] == "FAIL"]
print("-" * 112)
print(f"Tổng: {len(results) - len(failed)}/{len(results)} PASS")
if failed:
    print("\nCác ca FAIL (kèm thông báo của hệ thống):")
    for group, case_input, expected, actual, _s, note in failed:
        print(f"  - [{group}] {case_input}: mong đợi {expected}, thực tế {actual} | {note}")

shutil.rmtree(TMP_DIR, ignore_errors=True)
sys.exit(1 if failed else 0)