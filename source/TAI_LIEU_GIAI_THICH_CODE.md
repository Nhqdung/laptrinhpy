# TÀI LIỆU TOÀN DIỆN GIẢI THÍCH CODE & PHỤC VỤ THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN

> **Mục tiêu của tài liệu:** Cung cấp đầy đủ kiến thức về cấu trúc mã nguồn, luồng dữ liệu, thuật toán và các câu trả lời mẫu cho mọi câu hỏi phản biện của giảng viên khi đứng thuyết trình trên lớp.

---

## 📑 MỤC LỤC
1. [Tổng Quan Kiến Trúc Dự Án (Architectural Overview)](#1-tổng-quan-kiến-trúc-dự-án)
2. [Chi Tiết Từng Module & Tệp Tin](#2-chi-tiết-từng-module--tệp-tin)
   - [2.1. main.py - Điểm khởi chạy (Entry Point)](#21-mainpy)
   - [2.2. data_manager.py - Bộ xử lý nghiệp vụ & Bảo mật](#22-data_managerpy)
   - [2.3. email_service.py - Tích hợp Dịch vụ Ngoài Gmail SMTP](#23-email_servicepy)
   - [2.4. algorithms/ - Thuật toán tìm đường & Thiết kế mở rộng](#24-algorithms)
   - [2.5. gui/ - Giao diện đồ họa Tkinter tương tác](#25-gui)
   - [2.6. services/ - Tầng xử lý bổ trợ](#26-services)
   - [2.7. test_data.py - Bộ 48 ca kiểm thử tự động](#27-test_datapy)
3. [Giải Thích Sâu Về Các Thuật Toán Cốt Lõi](#3-giải-thích-sâu-về-các-thuật-toán-cốt-lõi)
   - [3.1. Thuật toán BFS (Breadth-First Search) trên Lưới 2D](#31-thuật-toán-bfs-trên-lưới-2d)
   - [3.2. Thuật toán Mã hóa Mật khẩu PBKDF2-HMAC-SHA256 & Salt](#32-thuật-toán-mã-hóa-mật-khẩu-pbkdf2)
   - [3.3. Cơ chế Khóa Tài Khoản Chống Tấn Công Dò Quét (Brute-Force)](#33-cơ-chế-khóa-tài-khoản)
   - [3.4. Kỹ thuật Lưu Trữ An Toàn Atomic File Write](#34-kỹ-thuật-lưu-trữ-an-toàn-atomic-write)
4. [Kịch Bản Hỏi - Đáp (Q&A) Với Giảng Viên Trên Lớp](#4-kịch-bản-hỏi---đáp-qa-với-giảng-viên)

---

## 1. TỔNG QUAN KIẾN TRÚC DỰ ÁN

Dự án áp dụng mô hình kiến trúc phân lớp hướng đối tượng (**Layered MVC Architecture**):

```text
               +-----------------------------------+
               |        GIAO DIỆN (VIEW)           |
               |  (gui/login_window, main_window)  |
               +-----------------+-----------------+
                                 |  Bắt sự kiện (Events)
                                 v
               +-----------------------------------+
               |     ĐIỀU KHIỂN (CONTROLLER)       |
               |  (control_panel, algorithms/)     |
               +-----------------+-----------------+
                                 |  Gọi hàm nghiệp vụ
                                 v
               +-----------------------------------+
               |       MÔ HÌNH DỮ LIỆU (MODEL)     |
               |   (data_manager.py, services/)    |
               +-----------------+-----------------+
                                 |  Lưu trữ an toàn
                                 v
               +-----------------------------------+
               |       LƯU TRỮ (PERSISTENCE)       |
               |  (users.json, maps.json, history) |
               +-----------------------------------+
```

* **Tầng View (`gui/`)**: Chịu trách nhiệm hiển thị giao diện người dùng bằng Tkinter, lắng nghe tương tác click chuột, phím bấm và cập nhật hoạt ảnh (animation). Không can thiệp vào logic tính toán đường đi.
* **Tầng Controller (`algorithms/`, `gui/control_panel.py`)**: Tiếp nhận yêu cầu tìm đường, điều phối thuật toán duyệt từng ô trên lưới, quản lý hàng đợi và thời gian trễ (delay) mô phỏng.
* **Tầng Model (`data_manager.py`, `services/`)**: Quản lý toàn bộ dữ liệu, kiểm tra tính hợp lệ (Regex), băm mật khẩu, sinh OTP, đọc/ghi tệp tin JSON an toàn.
* **Tầng Tích Hợp Ngoài (`email_service.py`)**: Kết nối giao thức SMTP để gửi mail OTP thực tế tới hòm thư người dùng.

---

## 2. CHI TIẾT TỪNG MODULE & TỆP TIN

### 2.1. `main.py`
* **Vai trò:** Điểm khởi chạy duy nhất của chương trình khi chạy bằng Python.
* **Nội dung:** Khởi tạo lớp `MainWindow` từ `gui.main_window` và kích hoạt vòng lặp sự kiện `app.mainloop()`.
* **Cách giải thích trên lớp:** *"File `main.py` đóng vai trò là Entry Point tối giản, tuân thủ nguyên tắc Single Responsibility, chỉ có nhiệm vụ khởi động cửa sổ chính của ứng dụng."*

### 2.2. `data_manager.py`
Là file quan trọng nhất quản lý dữ liệu và xác thực logic:
* **Hàm băm mật khẩu `_hash_password(password, salt)`:**
  * Sinh một chuỗi ngẫu nhiên cryptographic salt 16 bytes bằng `os.urandom(16)`.
  * Áp dụng thuật toán băm chuẩn ngân hàng/bảo mật cao: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)`.
  * Trả về cặp `(salt_hex, key_hex)` để lưu trữ vào `users.json`.
* **Hàm xác minh mật khẩu `_verify_password(password, salt_hex, key_hex)`:**
  * Lấy salt từ dữ liệu cũ, băm lại mật khẩu người dùng vừa nhập rồi so sánh chuỗi hash với `key_hex`.
* **Hàm `validate_user_input(username, phone, email, password)`:**
  * Sử dụng Regular Expression (Regex) để kiểm tra định dạng:
    * `username`: Bắt đầu bằng chữ cái, dài từ 3-20 ký tự gồm chữ, số, gạch dưới (`^[a-zA-Z][a-zA-Z0-9_]{2,19}$`).
    * `phone`: Đúng 10 chữ số, bắt đầu bằng số 0 (`^0[0-9]{9}$`).
    * `email`: Chuỗi email chuẩn, thuộc các domain phổ biến (`gmail.com`, `yahoo.com`, `huit.edu.vn`,...).
    * `password`: Tối thiểu 8 ký tự, có ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số, 1 ký tự đặc biệt (`(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])`).
* **Hàm chống Brute-force `login(...)`:**
  * Kiểm tra `failed_attempts`. Nếu vượt quá 5 lần sai, kích hoạt khóa tài khoản trong 5 phút (`lockout_until = datetime.now() + 5 phút`).
* **Hàm OTP:**
  * `generate_otp()`: Sinh số ngẫu nhiên 6 chữ số (`f"{random.randint(0, 999999):06d}"`).
  * Gắn hạn sử dụng `expires_at = datetime.now() + timedelta(minutes=10)`.

### 2.3. `email_service.py`
* **Vai trò:** Dịch vụ gửi email thông báo mã OTP qua giao thức mạng SMTP.
* **Công nghệ sử dụng:**
  * Thư viện `smtplib` chuẩn của Python với chế độ bảo mật SSL (`SMTP_SSL` qua cổng 465).
  * Máy chủ: `smtp.gmail.com`.
  * Đọc thông tin người gửi và App Password từ file `.env` qua `python-dotenv`.
* **Cách giải thích trên lớp:** *"Để đảm bảo an toàn thông tin, dự án không hardcode mật khẩu trong mã nguồn mà đọc biến môi trường từ tệp `.env`. Kết nối được mã hóa đường truyền SSL."*

### 2.4. `algorithms/`
* **`base_algorithm.py`:**
  * Chứa lớp trừu tượng `BaseAlgorithm` kế thừa từ `abc.ABC`.
  * Định nghĩa các phương thức trừu tượng bắt buộc: `initialize()`, `step()`, `find_path()`, `get_stats()`.
  * Mọi thuật toán tìm đường (BFS, DFS, A*, Dijkstra) đều phải kế thừa từ lớp này.
* **`grid_bfs.py`:**
  * Cài đặt cụ thể thuật toán BFS cho lưới ô vuông 2D.
  * Sử dụng `collections.deque` làm hàng đợi `queue` (hỗ trợ thao tác `popleft()` với độ phức tạp $O(1)$).
  * Sử dụng từ điển `parent = {}` để lưu lại ô nút cha của từng ô, phục vụ việc truy vết đường đi ngược lại từ Đích về Start.
  * Hỗ trợ hàm `step()`: Mỗi lần gọi sẽ mở rộng một bước tìm kiếm. Điều này cho phép giao diện Tkinter vẽ từng bước một (animation) mà không làm đơ ứng dụng.
* **`algorithms_registry.py`:**
  * Áp dụng **Factory Method Pattern**. Đăng ký danh sách thuật toán qua Registry dictionary.
  * Giúp hệ thống dễ dàng bổ sung thuật toán mới trong tương lai mà không cần viết lại giao diện.

### 2.5. `gui/`
* **`main_window.py`:** Cửa sổ làm việc chính, tích hợp thanh menu, quản lý trạng thái phiên làm việc (session người dùng đăng nhập), điều phối giữa Canvas và Control Panel.
* **`grid_canvas.py`:** Kế thừa từ `tk.Canvas`. Xử lý sự kiện chuột để vẽ tường, đổi màu ô khi thuật toán chạy, chuyển đổi qua lại giữa tọa độ pixel và chỉ số `(hàng, cột)`.
* **`control_panel.py`:** Bảng điều khiển gồm các nút chức năng: Bắt đầu, Tạm dừng, Xóa tường, Chọn thuật toán, Thanh trượt tốc độ.
* **`login_window.py`:** Cửa sổ chứa 3 tab: Đăng nhập, Đăng ký (nhập thông tin & OTP), Quên mật khẩu (gửi OTP khôi phục).
* **`theme.py`:** Quản lý bảng màu Dark/Light Mode đồng bộ cho toàn bộ ứng dụng.

### 2.6. `services/`
* **`json_handler.py`:** Cung cấp hàm đọc/ghi tệp tin JSON an toàn, tự động bắt lỗi cú pháp nếu file bị hỏng hoặc chưa tồn tại.
* **`external_service.py`:** Chứa các hàm hỗ trợ gọi dịch vụ ngoài bổ trợ.

### 2.7. `test_data.py`
* Chứa **48 ca kiểm thử tự động (Unit / Integration Tests)** được viết bằng Python thuần (không cần cài thêm pytest).
* Kiểm tra toàn diện từ kiểm tra tính hợp lệ dữ liệu đầu vào (tên, email, số điện thoại, mật khẩu), logic đăng ký, logic băm, mã OTP, chống brute-force khóa tài khoản, đến lưu/tải bản đồ và ghi lịch sử.
* Đạt tỷ lệ thành công tuyệt đối: **48/48 PASS (100%)**.

---

## 3. GIẢI THÍCH SÂU VỀ CÁC THUẬT TOÁN CỐT LÕI

### 3.1. Thuật toán BFS (Breadth-First Search) trên Lưới 2D
* **Nguyên lý hoạt động:**
  1. Đưa điểm xuất phát $(S)$ vào hàng đợi `Queue` và đánh dấu đã thăm (`visited.add(S)`).
  2. Lấy ô đầu hàng đợi ra (First-In, First-Out).
  3. Xét 4 ô lân cận (Lên, Xuống, Trái, Phải):
     * Nếu ô nằm trong phạm vi lưới, chưa từng thăm và không phải là tường chướng ngại vật:
       * Đưa ô đó vào `Queue`.
       * Đánh dấu ô đó là đã thăm.
       * Ghi nhận quan hệ: `parent[ô_lân_cận] = ô_hiện_tại`.
       * Nếu ô lân cận chính là Đích đến $(T)$ $\rightarrow$ Dừng thuật toán.
  4. Lặp lại bước 2 cho đến khi hàng đợi rỗng hoặc đã tìm thấy đích.
  5. **Truy vết đường đi ngắn nhất (Path Reconstruction):** Bắt đầu từ $T$, lần ngược theo `parent[T]`, `parent[parent[T]]` cho đến khi gặp $S$. Đảo ngược danh sách lại ta được đường đi ngắn nhất.
* **Độ phức tạp:**
  * Thời gian (Time Complexity): $O(V + E) = O(R \times C)$ với $R, C$ là số hàng và số cột của lưới (mỗi ô và cạnh được duyệt tối đa một lần).
  * Không gian (Space Complexity): $O(R \times C)$ để lưu trữ `visited`, `parent` và hàng đợi `Queue`.
* **Tính chất quan trọng:** Trên đồ thị không trọng số (mỗi bước đi có chi phí bằng 1), BFS **luôn luôn đảm bảo** tìm ra đường đi ngắn nhất với số bước ít nhất.

---

### 3.2. Thuật toán Mã hóa Mật khẩu PBKDF2
* **Tại sao không lưu mật khẩu thô (Plaintext)?** Vì nếu file `users.json` bị lộ, toàn bộ tài khoản người dùng sẽ bị chiếm đoạt.
* **Tại sao không dùng MD5 hay SHA-256 thông thường?**
  * MD5 và SHA-256 là hàm băm một chiều rất nhanh, kẻ tấn công có thể dùng bảng cầu vồng (Rainbow Table) hoặc dùng card đồ họa GPU để thử hàng tỷ mật khẩu mỗi giây.
* **Giải pháp của dự án:** Dùng **PBKDF2-HMAC-SHA256**:
  * Mỗi người dùng có một `salt` ngẫu nhiên 16 bytes riêng biệt, chống hoàn toàn kỹ thuật tấn công bằng Rainbow Table.
  * Số vòng lặp băm kéo dài: `100,000` lần lặp. Thời gian tính toán cho 1 mật khẩu mất khoảng vài mili-giây đối với người dùng bình thường (không nhận thấy độ trễ), nhưng khiến kẻ tấn công mất hàng nghìn năm nếu muốn dò quét brute-force số lượng lớn.

---

### 3.3. Cơ chế Khóa Tài Khoản Chống Tấn Công Dò Quét (Brute-Force)
* Mỗi khi người dùng gõ sai mật khẩu, `failed_attempts` tăng thêm 1.
* Nếu gõ sai liên tiếp 5 lần:
  * Hệ thống tự động ghi nhận thời điểm khóa: `lockout_until = datetime.now() + 5 phút`.
  * Trong suốt 5 phút này, dù người dùng có nhập đúng mật khẩu thì hệ thống vẫn từ chối đăng nhập và thông báo rõ thời gian còn lại cần chờ.
* Khi người dùng nhập đúng mật khẩu trước khi bị khóa: `failed_attempts` tự động reset về 0.

---

### 3.4. Kỹ thuật Lưu Trữ An Toàn Atomic File Write
Khi lưu `users.json` hoặc `maps.json`:
* Nếu ghi đè trực tiếp lên file đang có, lỡ máy tính bị sập nguồn hoặc tắt app đột ngột đúng khoảnh khắc đó, file sẽ bị rỗng (0 bytes) và hỏng toàn bộ dữ liệu.
* Dự án áp dụng phương pháp **Atomic Write**:
  1. Ghi toàn bộ dữ liệu ra một file tạm: `users.json.tmp`.
  2. Dùng lệnh `os.replace("users.json.tmp", "users.json")`. Lệnh này ở cấp hệ điều hành là một thao tác đơn nguyên (atomic operation), đảm bảo dữ liệu luôn toàn vẹn 100%, không bao giờ bị hỏng dở dang.

---

## 4. KỊCH BẢN HỎI - ĐÁP (Q&A) VỚI GIẢNG VIÊN

Dưới đây là các câu hỏi giảng viên hay đặt ra nhất và câu trả lời chuẩn xác giúp bạn đạt điểm tối đa:

### ❓ Câu 1: Em hãy giải thích tại sao thuật toán BFS luôn tìm được đường đi ngắn nhất trên lưới này?
> **Trả lời:** Dạ thưa thầy/cô, trên lưới tọa độ này, chi phí di chuyển giữa hai ô kề nhau là như nhau (bằng 1 đơn vị, đồ thị không trọng số). Thuật toán BFS duyệt theo cơ chế vết dầu loang (lan tỏa theo từng lớp bán kính), tức là duyệt hết tất cả các ô cách điểm xuất phát 1 bước, sau đó mới duyệt các ô cách 2 bước, 3 bước... Vì vậy, ngay khoảnh khắc đầu tiên thuật toán chạm tới điểm Đích, đường đi tới ô đó chắc chắn có số bước ngắn nhất.

### ❓ Câu 2: Khi chạy mô phỏng hoạt ảnh (animation), làm sao để giao diện Tkinter không bị đơ (Not Responding)?
> **Trả lời:** Dạ thưa thầy/cô, thay vì dùng một vòng lặp `while True` với lệnh `time.sleep()` gây tắc nghẽn luồng giao diện chính (Main GUI Thread), nhóm em đã thiết kế thuật toán theo cơ chế bước `step()`. Mỗi lần giao diện gọi `root.after(delay, run_step)`, ứng dụng chỉ tính toán và vẽ 1 bước rồi trả quyền kiểm soát lại cho Mainloop của Tkinter, sau đó hẹn lịch gọi bước tiếp theo. Nhờ vậy, người dùng vẫn có thể bấm nút Tạm dừng (Pause), Xóa hoặc kéo chuột bình thường mà không bị treo phần mềm.

### ❓ Câu 3: Mật khẩu người dùng được lưu trữ như thế nào trong tệp users.json?
> **Trả lời:** Dạ thưa thầy/cô, mật khẩu hoàn toàn không được lưu ở dạng văn bản thô. Nhóm em sử dụng thuật toán PBKDF2 kết hợp HMAC-SHA256 với Salt ngẫu nhiên 16 bytes và 100.000 vòng lặp băm. Mỗi tài khoản có một mã Salt riêng biệt lưu kèm chuỗi Hash. Kể cả hai người dùng đặt cùng một mật khẩu thì chuỗi Hash lưu trong file `users.json` vẫn hoàn toàn khác nhau, ngăn chặn triệt để hình thức tấn công Rainbow Table.

### ❓ Câu 4: Nếu muốn thêm một thuật toán mới (ví dụ A* hoặc Dijkstra) vào dự án thì phải sửa những đâu?
> **Trả lời:** Dạ thưa thầy/cô, dự án áp dụng nguyên lý thiết kế Open/Closed Principle và mẫu Factory Pattern. Em chỉ cần tạo một file thuật toán mới kế thừa lớp `BaseAlgorithm` trong thư mục `algorithms/`, cài đặt hàm `step()` và `find_path()`, sau đó đăng ký vào `algorithms_registry.py`. Toàn bộ giao diện người dùng, Canvas và Control Panel sẽ tự động nhận diện thuật toán mới trong menu chọn mà không cần sửa đổi bất kỳ dòng code giao diện nào.

### ❓ Câu 5: Em đã kiểm thử phần mềm như thế nào để chứng minh hệ thống hoạt động ổn định?
> **Trả lời:** Dạ thưa thầy/cô, nhóm em đã xây dựng một bộ kiểm thử tự động gồm **48 ca kiểm thử (Test Cases)** trong file `test_data.py`. Bộ kiểm thử này kiểm tra toàn bộ các ca bình thường và ca biên: từ kiểm tra Regex số điện thoại, email, mật khẩu; kiểm tra trùng lặp tài khoản; kiểm tra tính năng gửi OTP; kiểm tra khóa tài khoản sau 5 lần sai mật khẩu; đến kiểm tra tính toàn vẹn của dữ liệu bản đồ JSON. Khi chạy lệnh `python test_data.py`, toàn bộ 48/48 ca đều đạt kết quả PASS tuyệt đối.

