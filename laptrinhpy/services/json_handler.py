"""
json_handler.py
----------------
Lớp dùng chung để đọc/ghi/sao lưu dữ liệu JSON một cách an toàn.
Đáp ứng yêu cầu: dùng with, xử lý file chưa tồn tại/rỗng/sai định dạng/không có quyền truy cập,
tạo backup trước khi ghi đè để hạn chế mất dữ liệu.
"""

import json
import os
import shutil
from datetime import datetime


class JSONHandlerError(Exception):
    """Ngoại lệ tùy chỉnh cho các lỗi liên quan đến đọc/ghi JSON."""
    pass


class JSONHandler:
    def __init__(self, file_path: str, default_data=None):
        """
        file_path: đường dẫn tới file JSON quản lý.
        default_data: dữ liệu mặc định nếu file chưa tồn tại (list hoặc dict).
        """
        self.file_path = file_path
        self.default_data = default_data if default_data is not None else []
        # Đảm bảo thư mục chứa file tồn tại
        folder = os.path.dirname(self.file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

    def load(self):
        """Đọc dữ liệu từ file JSON. Trả về default_data nếu file chưa tồn tại hoặc rỗng."""
        if not os.path.exists(self.file_path):
            # File chưa tồn tại -> tạo file mới với dữ liệu mặc định
            self.save(self.default_data, backup=False)
            return self.default_data

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    # File rỗng
                    return self.default_data
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise JSONHandlerError(
                f"File '{self.file_path}' sai định dạng JSON: {e}"
            )
        except PermissionError:
            raise JSONHandlerError(
                f"Không có quyền truy cập file '{self.file_path}'."
            )
        except OSError as e:
            raise JSONHandlerError(f"Lỗi khi đọc file '{self.file_path}': {e}")

    def save(self, data, backup: bool = True):
        """Ghi dữ liệu ra file JSON. Tạo file .bak trước khi ghi đè nếu backup=True."""
        try:
            if backup and os.path.exists(self.file_path):
                self._backup()

            # Ghi ra file tạm trước, sau đó thay thế file gốc để tránh mất dữ liệu
            # nếu chương trình bị lỗi giữa chừng khi đang ghi.
            tmp_path = self.file_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            shutil.move(tmp_path, self.file_path)

        except PermissionError:
            raise JSONHandlerError(
                f"Không có quyền ghi vào file '{self.file_path}'."
            )
        except OSError as e:
            raise JSONHandlerError(f"Lỗi khi ghi file '{self.file_path}': {e}")

    def _backup(self):
        """Sao lưu file hiện tại thành <file>.bak trước khi ghi đè."""
        try:
            shutil.copy2(self.file_path, self.file_path + ".bak")
        except OSError:
            # Backup lỗi thì không nên chặn thao tác chính, chỉ bỏ qua và ghi log ở tầng trên
            pass

    def restore_backup(self):
        """Khôi phục dữ liệu từ file .bak nếu tồn tại."""
        bak_path = self.file_path + ".bak"
        if not os.path.exists(bak_path):
            raise JSONHandlerError("Không tìm thấy file backup để khôi phục.")
        shutil.copy2(bak_path, self.file_path)


def append_log(log_path: str, message: str):
    """Ghi một dòng log kèm timestamp vào file văn bản (dùng cho auth/log thao tác)."""
    folder = os.path.dirname(log_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except OSError:
        # Không để lỗi ghi log làm crash chức năng chính
        pass
