# 📖 TÀI LIỆU TOÀN DIỆN GIẢI THÍCH CODE & THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN

Tài liệu được phân chia rõ ràng thành **3 PHẦN TRỌNG TÂM** theo đúng kiến trúc của ứng dụng, giúp bạn dễ dàng tra cứu, trả lời câu hỏi và tự tin thuyết trình trước giảng viên và các bạn:

* **PHẦN 1: GIAO DIỆN (GUI & TRỰC QUAN HÓA)**
* **PHẦN 2: THUẬT TOÁN (TÌM ĐƯỜNG & MÔ PHỎNG LƯỚI)**
* **PHẦN 3: DỮ LIỆU & TÀI KHOẢN (BẢO MẬT, OTP & JSON)**

---

# 🎨 PHẦN 1: GIAO DIỆN (GUI & TRỰC QUAN HÓA)

Phần giao diện được xây dựng bằng thư viện chuẩn **Tkinter** của Python, nằm toàn bộ trong thư mục `gui/` và file điều phối `main.py`.

```text
gui/
├── main_window.py      # Cửa sổ chính tích hợp toàn bộ thành phần
├── grid_canvas.py      # Lưới vẽ tương tác (vẽ tường, hiển thị ô duyệt)
├── control_panel.py    # Thanh công cụ & nút bấm điều khiển
├── login_window.py     # Cửa sổ Đăng nhập, Đăng ký & Quên mật khẩu (OTP)
└── theme.py            # Quản lý bảng màu Dark Mode / Light Mode
```

---

### 1.1. `main.py` & `main_window.py` (Điều phối tổng thể)
* **`main.py`:**
  * Điểm khởi chạy (Entry Point) tối giản.
  * Khởi tạo đối tượng `MainWindow()` và kích hoạt `app.mainloop()`.
* **`main_window.py`:**
  * Đóng vai trò là **Container trung tâm**, kết nối `GridCanvas`, `ControlPanel` và `DataManager`.
  * Quản lý trạng thái phiên làm việc (Session) của tài khoản đang đăng nhập (hiển thị tên người dùng ở góc trên, nút Đăng xuất).
  * Xử lý luồng chuyển cảnh: Nếu chưa đăng nhập → mở `LoginWindow`; Đăng nhập thành công → mở khóa toàn bộ tính năng mô phỏng.

---

### 1.2. `grid_canvas.py` (Lưới vẽ tương tác)
* **Kế thừa:** `tk.Canvas`.
* **Chuyển đổi tọa độ toán học ↔ Tọa độ pixel màn hình:**
  * Kích thước mỗi ô là `cell_size` (mặc định 25px đến 30px).
  * **Từ tọa độ pixel chuột `(x, y)` → Chỉ số ô `(row, col)`:**
    ```python
    row = y // cell_size
    col = x // cell_size
    ```
  * **Từ chỉ số ô `(row, col)` → Tọa độ pixel hình chữ nhật vẽ trên Canvas:**
    ```python
    x1 = col * cell_size
    y1 = row * cell_size
    x2 = x1 + cell_size
    y2 = y1 + cell_size
    ```
* **Xử lý sự kiện chuột (Mouse Event Binding):**
  * `<Button-1>` & `<B1-Motion>`: Nhấn và kéo chuột trái để **Vẽ tường chướng ngại vật** liên tục.
  * `<Button-3>` & `<B3-Motion>`: Nhấn và kéo chuột phải để **Xóa tường chướng ngại vật**.
  * Chống vẽ đè: Kiểm tra không cho phép biến ô **Start (Bắt đầu)** và ô **Target (Đích)** thành tường.
* **Cơ chế cập nhật màu sắc trạng thái ô:**
  * `START`: Màu xanh lá cây (Green).
  * `TARGET`: Màu đỏ (Red).
  * `WALL`: Màu xám đậm / đen (Obstacle).
  * `VISITED`: Màu xanh dương nhạt / ngọc bích (Hiển thị làn sóng đang duyệt).
  * `PATH`: Màu vàng rực rỡ (Đường đi ngắn nhất tìm được).

---

### 1.3. `control_panel.py` (Bảng điều khiển & Hoạt ảnh Animation)
* **Các nút chức năng:**
  * **Bắt đầu tìm đường (Start):** Khởi tạo thuật toán và bắt đầu vòng lặp hoạt ảnh.
  * **Tạm dừng / Tiếp tục (Pause/Resume):** Giữ nguyên trạng thái hàng đợi và ma trận duyệt.
  * **Xóa tường / Làm mới (Clear Walls / Reset Grid):** Đưa lưới về trạng thái ban đầu.
  * **Thanh trượt tốc độ (Speed Slider):** Điều chỉnh độ trễ `delay` (từ 5ms đến 100ms) giữa các bước vẽ.
  * **Lưu / Tải bản đồ (Save/Load Map):** Mở hộp thoại nhập tên để lưu trạng thái mê cung vào CSDL JSON.
* **⚡ Kỹ thuật hoạt ảnh không làm đơ giao diện (`root.after`):**
  * **Vấn đề thường gặp:** Dùng vòng lặp `while True` kết hợp `time.sleep()` sẽ làm luồng giao diện (Main Thread) bị nghẽn → Cửa sổ báo "(Not Responding)", không bấm được Pause hay chuột.
  * **Giải pháp trong code:** Sử dụng phương thức `root.after(delay_ms, self.step_animation)`. Mỗi lần chỉ tính toán và đổi màu đúng 1 bước duyệt của thuật toán, sau đó nhường quyền xử lý cho hệ điều hành vẽ màn hình, rồi hẹn lịch gọi bước tiếp theo.

---

### 1.4. `login_window.py` (Cửa sổ xác thực người dùng)
* Thiết kế dạng giao diện hiện đại với **3 Tab / Chế độ:**
  1. **Đăng nhập (Sign In):** Nhập username & password.
  2. **Đăng ký (Sign Up):** Nhập họ tên, email, SĐT, mật khẩu → Chuyển sang màn hình nhập **mã OTP 6 số**.
  3. **Quên mật khẩu (Forgot Password):** Nhập email nhận OTP → Nhập mật khẩu mới.
* Tự động hiển thị nhãn lỗi màu đỏ trực quan khi nhập sai dữ liệu (Validation feedback).

---

### 1.5. `theme.py` (Giao diện Sáng / Tối)
* Định nghĩa từ điển chứa bảng mã màu chuẩn: `THEMES["dark"]` và `THEMES["light"]`.
* Khi người dùng bấm nút chuyển chế độ, hàm cập nhật sẽ duyệt qua các Widget để đổi màu nền (`bg`), màu chữ (`fg`) và vẽ lại lưới Canvas với tông màu mới.

---

### 💡 Câu Hỏi Thầy Cô Thường Hỏi Về Phần Giao Diện & Câu Trả Lời Mẫu

* **❓ Giảng viên hỏi:** *Làm thế nào để khi người dùng rê chuột nhanh thì các ô tường được vẽ liên tục không bị đứt đoạn?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, em bắt sự kiện `<B1-Motion>` (vừa nhấn vừa di chuyển chuột). Trong hàm xử lý, em tính toán tọa độ `(row, col)` tức thời dưới con trỏ chuột và cập nhật ngay vào ma trận lưới. Đồng thời chỉ đổi màu các ô chưa phải là tường để tối ưu hóa hiệu năng render của Tkinter."*

* **❓ Giảng viên hỏi:** *Tại sao khi thuật toán chạy vẽ hàng trăm ô mà giao diện vẫn mượt, không bị treo ứng dụng?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, thay vì dùng `time.sleep()` làm block Main Event Loop, em sử dụng cơ chế Non-blocking thông qua hàm `root.after()`. Mỗi tick chỉ xử lý 1 bước của thuật toán rồi trả quyền cập nhật màn hình lại cho Tkinter, nhờ đó người dùng vẫn bấm được nút Dừng hoặc tương tác bình thường."*

---

# 🧠 PHẦN 2: THUẬT TOÁN (TÌM ĐƯỜNG & MÔ PHỎNG LƯỚI)

Phần thuật toán nằm độc lập trong thư mục `algorithms/`, được thiết kế theo đúng nguyên lý Hướng đối tượng (OOP) và mẫu thiết kế **Factory / Registry Pattern**.

```text
algorithms/
├── base_algorithm.py       # Lớp trừu tượng khuôn mẫu (Interface)
├── grid_bfs.py             # Cài đặt chi tiết thuật toán BFS trên lưới 2D
└── algorithms_registry.py  # Đăng ký và quản lý các thuật toán
```

---

### 2.1. `base_algorithm.py` (Khuôn mẫu lớp trừu tượng)
* Áp dụng nguyên lý **Open/Closed Principle** trong thiết kế hướng đối tượng:
  * Kế thừa từ `abc.ABC` (Abstract Base Class).
  * Khai báo các phương thức trừu tượng `@abstractmethod` bắt buộc mọi thuật toán phải có:
    * `initialize(grid, start, target)`: Thiết lập dữ liệu ban đầu.
    * `step()`: Thực hiện duyệt đúng **một bước** (để phục vụ vẽ hoạt ảnh).
    * `find_path()`: Trả về danh sách tọa độ các ô tạo thành đường đi ngắn nhất.
    * `get_stats()`: Trả về các thông số (Số ô đã duyệt, độ dài đường đi, thời gian chạy).

---

### 2.2. `grid_bfs.py` (Thuật toán Tìm kiếm theo chiều rộng - BFS)

#### A. Cấu trúc dữ liệu sử dụng:
1. **Hàng đợi `queue = collections.deque()` (FIFO - First In, First Out):**
   * Chứa các ô đang chờ được duyệt tiếp theo.
   * Sử dụng `deque` để thao tác lấy phần tử đầu `popleft()` đạt độ phức tạp O(1) (nếu dùng `list.pop(0)` thông thường sẽ mất O(N)).
2. **Tập hợp `visited = set()`:**
   * Lưu các tọa độ `(r, c)` đã được ghé thăm để tránh bị lặp vô tận.
   * Tra cứu trong `set` mất thời gian O(1).
3. **Từ điển cha-con `parent = {}` (Backtracking Map):**
   * Lưu lại ô đi trước của từng ô: `parent[neighbor] = current`.
   * Đây là cấu trúc quan trọng nhất để **truy vết ngược lại đường đi** sau khi đã chạm tới đích.

#### B. Quy tắc di chuyển 4 hướng (4-directional Movement):
```python
DIRECTIONS = [
    (-1, 0),  # Lên trên (Up)
    (1, 0),   # Xuống dưới (Down)
    (0, -1),  # Sang trái (Left)
    (0, 1)    # Sang phải (Right)
]
```

#### C. Các bước thực thi thuật toán:
1. **Khởi tạo:**
   * Đưa điểm xuất phát `S(start_row, start_col)` vào `queue`.
   * Thêm `S` vào `visited`.
2. **Trong mỗi bước (`step()`):**
   * Lấy ô hiện tại `(r, c)` ra khỏi đầu hàng đợi bằng `queue.popleft()`.
   * Nếu `(r, c) == target`: Đã tìm thấy đích! Dừng thuật toán và tiến hành truy vết.
   * Ngược lại, xét 4 ô lân cận `(nr, nc)`:
     * Điều kiện hợp lệ:
       1. `0 <= nr < Số hàng` và `0 <= nc < Số cột` (nằm trong biên).
       2. Lưới tại `(nr, nc)` **không phải là tường** (Not a wall).
       3. `(nr, nc)` **chưa từng có trong `visited`**.
     * Nếu thỏa mãn cả 3 điều kiện:
       * Thêm `(nr, nc)` vào `visited`.
       * Ghi nhận dấu vết: `parent[(nr, nc)] = (r, c)`.
       * Đẩy `(nr, nc)` vào cuối hàng đợi: `queue.append((nr, nc))`.
3. **Truy vết đường đi ngắn nhất (Reconstruct Path):**
   * Bắt đầu từ ô Đích: `curr = target`.
   * Chừng nào `curr in parent`:
     * Thêm `curr` vào danh sách `path`.
     * Lùi về ô cha: `curr = parent[curr]`.
   * Thêm ô `start` vào cuối, sau đó đảo ngược danh sách `path.reverse()`.

#### D. Độ phức tạp tính toán:
* **Thời gian (Time Complexity):** `O(V + E)`
  * Với lưới `R` hàng, `C` cột: Số đỉnh `V = R * C`, số cạnh tối đa `E = 4 * R * C`.
  * Do đó độ phức tạp là **tuyến tính O(R * C)**. Mỗi ô chỉ được đưa vào hàng đợi tối đa 1 lần.
* **Bộ nhớ (Space Complexity):** `O(R * C)` để lưu trữ `queue`, `visited` và `parent`.

---

### 2.3. `algorithms_registry.py` (Mở rộng thuật toán)
* Quản lý danh sách các thuật toán dưới dạng từ điển `REGISTRY = {"BFS": GridBFS, ...}`.
* **Ý nghĩa:** Khi bạn muốn thêm thuật toán **A\***, **Dijkstra** hay **DFS**, bạn chỉ cần tạo file mới kế thừa `BaseAlgorithm` rồi đăng ký 1 dòng vào đây. Giao diện sẽ tự động hiển thị tên thuật toán mới mà không cần chỉnh sửa bất kỳ dòng code GUI nào!

---

### 💡 Câu Hỏi Thầy Cô Thường Hỏi Về Phần Thuật Toán & Câu Trả Lời Mẫu

* **❓ Giảng viên hỏi:** *Tại sao thuật toán BFS luôn đảm bảo tìm được đường đi ngắn nhất trên lưới này?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, trên lưới ô vuông này, khoảng cách di chuyển giữa hai ô kề nhau luôn bằng nhau (không trọng số, chi phí = 1 đơn vị). BFS hoạt động theo cơ chế hàng đợi FIFO, tức là duyệt theo từng lớp bán kính: thăm hết tất cả các ô cách điểm đầu 1 bước, rồi mới đến các ô cách 2 bước, 3 bước... Do đó, thời điểm đầu tiên thuật toán chạm đến ô Đích thì số bước đi từ điểm Bắt đầu đến ô Đích đó chắc chắn là nhỏ nhất."*

* **❓ Giảng viên hỏi:** *Nếu trên lưới không có đường đi đến đích (bị tường bao kín hoàn toàn) thì thuật toán xử lý thế nào?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, thuật toán sẽ duyệt hết tất cả các ô có thể đi tới được. Khi hàng đợi `queue` trở nên rỗng mà vẫn chưa gặp điểm Đích, hàm `step()` sẽ trả về kết quả không tìm thấy đường đi (`NO_PATH`), giao diện sẽ hiển thị thông báo cho người dùng biết là đích đến không thể chạm tới."*

* **❓ Giảng viên hỏi:** *Hàm truy vết đường đi hoạt động ra sao?*
  * **👉 Trả lời:** *"Dạ trong quá trình duyệt, mỗi khi tìm thấy một ô lân cận hợp lệ, em lưu lại tọa độ ô đi trước vào từ điển `parent[ô_mới] = ô_hiện_tại`. Khi chạm đích, em lần ngược từ Đích về ô cha, rồi ô ông nội... cho tới khi gặp điểm Bắt đầu, sau đó đảo ngược danh sách lại là thu được lộ trình hoàn chỉnh."*

---

# 🔒 PHẦN 3: DỮ LIỆU & TÀI KHOẢN (BẢO MẬT, OTP & JSON)

Toàn bộ phần xử lý nghiệp vụ, kiểm tra đầu vào, mã hóa mật khẩu, gửi email OTP và lưu trữ CSDL nằm trong `data_manager.py`, `email_service.py` và thư mục `data/`.

```text
source/
├── data_manager.py      # Bộ xử lý nghiệp vụ, băm mật khẩu, chống brute-force, quản lý JSON
├── email_service.py     # Dịch vụ gửi email OTP qua Gmail SMTP SSL (Port 465)
├── test_data.py         # Bộ 48 ca kiểm thử tự động toàn diện
├── services/
│   └── json_handler.py  # Đọc/ghi JSON an toàn
└── data/
    ├── users.json       # Cơ sở dữ liệu tài khoản (đã mã hóa)
    ├── maps.json        # Bản đồ người dùng lưu lại
    └── history.json     # Lịch sử các phiên mô phỏng
```

---

### 3.1. Xác Thực Dữ Liệu Đầu Vào Bằng Biểu Thức Chính Quy (Regex)
Hàm `validate_user_input()` kiểm tra chặt chẽ tính hợp lệ trước khi cho phép đăng ký:
* **Tên đăng nhập (Username):** `^[a-zA-Z][a-zA-Z0-9_]{2,19}$`
  * Bắt buộc bắt đầu bằng chữ cái.
  * Chỉ chứa chữ cái, số, gạch dưới. Độ dài từ 3 đến 20 ký tự.
* **Số điện thoại (Phone):** `^0[0-9]{9}$`
  * Bắt đầu bằng chữ số `0`, gồm đúng 10 chữ số chuẩn định dạng Việt Nam.
* **Email:** Kiểm tra cú pháp chuẩn RFC và nằm trong danh sách domain hợp lệ (`gmail.com`, `yahoo.com`, `huit.edu.vn`...).
* **Mật khẩu (Password):** `(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])`
  * Tối thiểu 8 ký tự.
  * Phải có ít nhất: 1 chữ hoa, 1 chữ thường, 1 chữ số và 1 ký tự đặc biệt.

---

### 3.2. Thuật Toán Mã Hóa Mật Khẩu Chuẩn Ngân Hàng: PBKDF2 + Salt
Hệ thống **tuyệt đối không lưu mật khẩu thô (Plaintext)**:
* **Cơ chế băm trong hàm `_hash_password()`:**
  1. Mỗi tài khoản khi tạo sẽ được sinh một mã ngẫu nhiên **Salt 16 bytes** bằng hàm bảo mật của hệ điều hành: `os.urandom(16)`.
  2. Sử dụng thuật toán:
     ```python
     hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
     ```
  3. Băm liên tục **100.000 vòng lặp** (Iterations).
* **Tại sao không dùng MD5 hay SHA-256 thông thường?**
  * MD5 và SHA-256 tính toán cực nhanh, hacker có thể dùng card đồ họa GPU thử hàng tỷ mật khẩu mỗi giây hoặc tra bảng băm có sẵn (Rainbow Table).
  * Với PBKDF2 + 100.000 vòng lặp kèm Salt riêng, hacker hoàn toàn bất khả thi trong việc dò quét mật khẩu hàng loạt.

---

### 3.3. Cơ Chế Chống Tấn Công Dò Quét (Brute-Force Lockout)
* Trong file `users.json`, mỗi tài khoản có trường:
  * `failed_attempts`: Số lần gõ sai mật khẩu liên tiếp.
  * `lockout_until`: Thời điểm hết hạn khóa tài khoản.
* **Quy tắc:**
  * Nếu người dùng gõ sai mật khẩu **5 lần liên tiếp** → Hệ thống tự động khóa tài khoản trong **5 phút**.
  * Trong thời gian 5 phút này, dù có nhập đúng mật khẩu, hệ thống vẫn từ chối và báo rõ số phút còn phải chờ.
  * Khi nhập đúng mật khẩu trước mốc 5 lần sai → Tự động reset `failed_attempts` về 0.

---

### 3.4. Xác Thực Hai Lớp (OTP) Qua Gmail SMTP Thật
* **Sinh mã OTP:** `random.randint(0, 999999)` định dạng 6 chữ số (ví dụ: `482910`).
* **Thời hạn hiệu lực:** 10 phút (`expires_at = datetime.now() + timedelta(minutes=10)`).
* **Gửi mail (`email_service.py`):**
  * Sử dụng thư viện `smtplib` với kết nối bảo mật `SMTP_SSL` qua cổng **465**.
  * Máy chủ máy chủ: `smtp.gmail.com`.
  * Đọc thông tin người gửi và App Password từ file cấu hình bảo mật `.env` (không hardcode vào mã nguồn).

---

### 3.5. Lưu Trữ An Toàn Tuyệt Đối (Atomic File Write)
* **Nguy cơ:** Khi đang ghi đè file `users.json`, nếu người dùng tắt app hoặc máy tính bị mất điện, file sẽ bị đứt đoạn, trở thành rỗng (0 bytes) và hỏng toàn bộ tài khoản.
* **Giải pháp trong code:**
  1. Ghi dữ liệu ra một file tạm: `users.json.tmp`.
  2. Dùng lệnh `os.replace("users.json.tmp", "users.json")`.
  3. Thao tác `os.replace` ở tầng nhân hệ điều hành là **thao tác đơn nguyên (Atomic)**: Hoặc là file cũ còn nguyên, hoặc là file mới được thay thế trọn vẹn, không bao giờ có trạng thái file bị hỏng dở dang.

---

### 3.6. Bộ 48 Ca Kiểm Thử Tự Động (`test_data.py`)
Dự án tích hợp sẵn bộ kiểm thử tự động toàn diện kiểm tra 100% logic của tầng dữ liệu:
* Ca 1 - 7: Kiểm thử định dạng Tên tài khoản.
* Ca 8 - 11: Kiểm thử định dạng Số điện thoại.
* Ca 12 - 17: Kiểm thử định dạng Email & tên miền.
* Ca 18 - 20: Kiểm thử độ mạnh mật khẩu.
* Ca 21 - 26: Kiểm thử logic Đăng ký (trùng tên, trùng mail, trùng SĐT).
* Ca 27 - 29: Kiểm thử xác thực mã OTP.
* Ca 30 - 34: Kiểm thử Đăng nhập & cơ chế Khóa sau 5 lần sai (Brute-force).
* Ca 35 - 40: Kiểm thử chức năng Quên mật khẩu & cấp lại mật khẩu mới.
* Ca 41 - 47: Kiểm thử tính toàn vẹn khi Lưu & Tải bản đồ JSON.
* Ca 48: Kiểm thử ghi nhận lịch sử mô phỏng.
* **Kết quả:** **48/48 ca PASS (100%)**.

---

### 💡 Câu Hỏi Thầy Cô Thường Hỏi Về Dữ Liệu & Tài Khoản & Câu Trả Lời Mẫu

* **❓ Giảng viên hỏi:** *Tại sao trong file users.json mật khẩu nhìn giống một chuỗi ký tự loằng ngoằng, em có giải mã ngược lại được không?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, đây là hàm băm một chiều (One-way Hash Function) PBKDF2-SHA256 kết hợp mã Salt ngẫu nhiên 16 bytes. Về mặt toán học và mật mã học, hàm băm này không thể giải mã ngược lại ra mật khẩu ban đầu được. Khi người dùng đăng nhập, hệ thống sẽ lấy mật khẩu họ vừa gõ, dùng chính mã Salt cũ để băm lại, nếu hai chuỗi băm trùng nhau thì chứng tỏ mật khẩu chính xác."*

* **❓ Giảng viên hỏi:** *Nếu người dùng nhập sai mã OTP thì mã đó có bị mất không và hết hạn sau bao lâu?*
  * **👉 Trả lời:** *"Dạ thưa thầy/cô, mã OTP được cấu hình hết hạn sau 10 phút kể từ lúc sinh ra. Nếu nhập sai, hệ thống sẽ báo lỗi và cho phép nhập lại cho đến khi hết hạn. Khi hết hạn hoặc người dùng yêu cầu gửi lại, mã OTP cũ sẽ bị hủy và hệ thống sẽ sinh ra một mã hoàn toàn mới."*

* **❓ Giảng viên hỏi:** *Dữ liệu bản đồ được lưu xuống file JSON như thế nào?*
  * **👉 Trả lời:** *"Dạ trong file `maps.json`, mỗi bản đồ được lưu thành một đối tượng JSON gồm: ID bản đồ, Tên bản đồ, Tọa độ điểm bắt đầu `start: [r, c]`, Tọa độ điểm đích `target: [r, c]`, Kích thước lưới `[rows, cols]` và danh sách tọa độ của toàn bộ các ô tường `walls: [[r1, c1], [r2, c2], ...]`. Khi người dùng tải lại bản đồ, hệ thống chỉ cần đọc danh sách tọa độ này và gán lại lên Canvas."*

---

# 📊 BẢNG TỔNG KẾT NHANH ĐỂ TRẢ LỜI NHANH TRÊN

| Thành phần | Công nghệ / Thuật toán | Ưu điểm cốt lõi |
| :--- | :--- | :--- |
| **Giao diện** | Python Tkinter, Non-blocking Canvas | Trực quan, chạy mượt không giật lag nhờ `root.after()`. |
| **Tìm đường** | BFS (Breadth-First Search), `deque` | Đảm bảo 100% luôn tìm được đường đi ngắn nhất với độ phức tạp `O(R * C)`. |
| **Mở rộng code** | OOP, Factory Method Registry | Dễ dàng thêm thuật toán mới mà không cần chạm vào code giao diện. |
| **Mật khẩu** | PBKDF2-HMAC-SHA256, 100.000 vòng, 16B Salt | Chống Rainbow Table, chống GPU Brute-force đạt chuẩn bảo mật cao. |
| **An toàn tài khoản** | Khóa 5 phút khi sai 5 lần | Chống tấn công dò quét mật khẩu tự động. |
| **Xác thực** | OTP 6 số ngẫu nhiên + Gmail SMTP SSL 465 | Xác thực người dùng thật qua hòm thư điện tử. |
| **Lưu trữ tệp** | Atomic File Write (`os.replace`) | Không bao giờ bị hỏng file dữ liệu JSON khi sập nguồn đột ngột. |
| **Kiểm thử** | 48 Test Cases tự động (`test_data.py`) | Đạt 48/48 PASS, chứng minh phần mềm hoạt động chính xác và ổn định. |
