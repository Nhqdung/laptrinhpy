# 🧭 Ứng Dụng Mô Phỏng Thuật Toán Tìm Đường Trên Lưới (Pathfinding Visualizer)

Dự án ứng dụng Desktop bằng **Python & Tkinter** mô phỏng trực quan các thuật toán tìm kiếm đường đi ngắn nhất trên lưới 2D (BFS, DFS, Dijkstra, A*...), hỗ trợ vẽ vật cản tương tác, lưu/tải bản đồ mê cung, hệ thống bảo mật tài khoản người dùng và xác thực mã OTP thực tế qua Gmail SMTP.

---

## 🗂️ CẤU TRÚC DỰ ÁN TRÊN GITHUB

Để thuận tiện tối đa cho việc **chạy ứng dụng trên lớp** và **thuyết trình giải thích mã nguồn**, dự án được chia rõ ràng thành 2 phần độc lập:

```text
laptrinhpy/
│
├── 🚀 chaynhanh_exe.bat              <-- Bấm đúp tại đây để mở app ngay từ thư mục gốc!
│
├── 📁 .exe/                          <-- PHẦN 1: BẢN CHẠY NGAY (.EXE) DÀNH CHO DEMO
│   ├── TimDuongTrenLuoi.exe          # File ứng dụng chạy độc lập (KHÔNG CẦN CÀI PYTHON)
│   ├── Chay_App.bat                  # Script click đúp để mở phần mềm
│   ├── .env                          # Cấu hình dịch vụ gửi email OTP Gmail
│   └── data/                         # CSDL JSON (tài khoản, bản đồ, lịch sử)
│
├── 📁 source/                        <-- PHẦN 2: MÃ NGUỒN DÀNH CHO THUYẾT TRÌNH & CHẤM CODE
│   ├── main.py                       # File chạy chính của chương trình Python
│   ├── data_manager.py               # Quản lý dữ liệu, mã hóa PBKDF2, OTP, chống brute-force
│   ├── email_service.py              # Dịch vụ gửi mail OTP Gmail SMTP SSL
│   ├── test_data.py                  # Bộ 48 ca kiểm thử tự động (48/48 PASS)
│   ├── requirements.txt              # Thư viện phụ thuộc
│   ├── .env                          # Cấu hình biến môi trường
│   ├── .env.example                  # Mẫu cấu hình
│   ├── Chay_Code.bat                 # Script chạy nhanh bằng Python
│   ├── Chay_Kiem_Thu_Test.bat        # Script chạy bộ kiểm thử tự động
│   ├── algorithms/                   # Module thuật toán (BFS, Base Interface, Registry)
│   ├── gui/                          # Giao diện đồ họa Tkinter (Canvas, Control panel, Windows)
│   ├── services/                     # Dịch vụ xử lý JSON và External API
│   ├── data/                         # Dữ liệu JSON gốc
│   └── TAI_LIEU_GIAI_THICH_CODE.md   # TÀI LIỆU TOÀN DIỆN GIẢI THÍCH CODE & CÂU HỎI BẢO VỆ
│
├── .gitignore                        # Loại bỏ file rác, cache khi đẩy lên Git
└── README.md                         # Tài liệu giới thiệu dự án
```

---

## 🎯 CÁCH SỬ DỤNG TRÊN LỚP

### 1️⃣ Khi muốn BẬT APP NGAY để demo (Không cần máy trường có Python):
1. Bấm đúp chuột vào file **`chaynhanh_exe.bat`** ở thư mục gốc (hoặc vào thư mục **`.exe`** bấm **`TimDuongTrenLuoi.exe`** / **`Chay_App.bat`**).
2. Đăng nhập ngay bằng tài khoản Quản trị viên có sẵn:
   * **Tài khoản:** `admin`
   * **Mật khẩu:** `Admin@123456`

---

### 2️⃣ Khi muốn GIẢI THÍCH CODE & CHẤM ĐIỂM với Giảng viên:
1. Mở thư mục **`source`** trong VS Code hoặc IDE.
2. Mở file **`TAI_LIEU_GIAI_THICH_CODE.md`** để tham khảo chi tiết:
   * Mô hình kiến trúc MVC phân tầng.
   * Giải thích tường tận từng hàm trong `data_manager.py` (Mã hóa mật khẩu bằng `PBKDF2-HMAC-SHA256` với Salt ngẫu nhiên 16 bytes, khóa tài khoản chống brute-force, atomic file write).
   * Phân tích thuật toán **BFS trên lưới 2D** (Hàng đợi FIFO deque, ma trận visited, mảng parent truy vết đường đi ngắn nhất).
   * Câu hỏi phản biện thường gặp của giảng viên và câu trả lời mẫu đạt điểm tối đa.
3. Chạy mã nguồn:
   ```bash
   cd source
   pip install -r requirements.txt
   python main.py
   ```
4. Biểu diễn bộ 48 ca kiểm thử tự động khi giảng viên yêu cầu chứng minh chất lượng code:
   ```bash
   python test_data.py
   ```
   *(Kết quả: 48/48 ca PASS)*
