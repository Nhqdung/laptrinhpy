"""
main_window.py
--------------
Cửa sổ chính của ứng dụng Mô phỏng tìm đường trên lưới.
Bao gồm thanh điều hướng (Header Bar), bảng lưới trực quan (GridCanvas),
bảng điều khiển chức năng (ControlPanel) và hộp thoại tương tác hiện đại.
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from gui.theme import (
    apply_theme, center_window,
    COLOR_BG_APP, COLOR_BG_CARD, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from gui.grid_canvas import GridCanvas
from gui.control_panel import ControlPanel
from gui.login_window import LoginWindow
from data_manager import DataManager
from algorithms.grid_bfs import Grid
from algorithms.algorithms_registry import ALGORITHMS

DEFAULT_ALGORITHM = ALGORITHMS["BFS"]


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mô phỏng thuật toán tìm đường trên lưới")
        self.resizable(False, False)

        # Áp dụng theme và kiểu dáng hiện đại
        apply_theme(self)

        self.dm = DataManager()
        self.current_user = None

        self._build_menu()
        self._build_header()

        # Thân ứng dụng (Body layout)
        body = ttk.Frame(self, padding=(12, 10))
        body.pack(fill="both", expand=True)

        # Lưới Canvas
        self.canvas = GridCanvas(body, rows=20, cols=30, cell_size=24)
        self.canvas.pack(side="left", padx=(0, 10), pady=0)

        # Bảng điều khiển Sidebar
        self.control_panel = ControlPanel(
            body,
            on_run=self._on_run,
            on_reset=self._on_reset,
            on_save=self._on_save_map,
            on_load=self._on_load_map,
            on_speed_change=self.canvas.set_speed,
            on_mode_change=self.canvas.set_mode,
        )
        self.control_panel.pack(side="right", fill="both", expand=True, pady=0)

        # Khởi chạy cửa sổ đăng nhập
        self.withdraw()
        LoginWindow(self, self.dm, self._on_login_success)

    def _build_header(self):
        """Tạo thanh Header Bar hiện đại phía trên cùng cửa sổ."""
        header_frame = tk.Frame(self, bg=COLOR_BG_CARD, height=52, bd=1, relief="solid")
        header_frame.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header_frame.pack(fill="x", side="top")

        # Khối bên trái: Tên ứng dụng + Badge thuật toán
        left_box = tk.Frame(header_frame, bg=COLOR_BG_CARD, padx=14, pady=8)
        left_box.pack(side="left")

        app_title = tk.Label(
            left_box,
            text="🧭 TÌM ĐƯỜNG TRÊN LƯỚI",
            font=FONT_HEADING,
            fg=COLOR_PRIMARY,
            bg=COLOR_BG_CARD
        )
        app_title.pack(side="left")

        algo_badge = tk.Label(
            left_box,
            text="THUẬT TOÁN: BFS",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_PRIMARY_LIGHT,
            padx=8,
            pady=3,
            bd=1,
            relief="solid"
        )
        algo_badge.configure(highlightbackground=COLOR_PRIMARY_LIGHT)
        algo_badge.pack(side="left", padx=(12, 0))

        # Khối bên phải: Thông tin người dùng + Nút đăng xuất
        right_box = tk.Frame(header_frame, bg=COLOR_BG_CARD, padx=14, pady=8)
        right_box.pack(side="right")

        self.user_chip_var = tk.StringVar(value="👤 Khách")
        self.user_chip_lbl = tk.Label(
            right_box,
            textvariable=self.user_chip_var,
            font=FONT_SMALL,
            fg=COLOR_TEXT_MAIN,
            bg="#F1F5F9",
            padx=10,
            pady=4,
            bd=1,
            relief="solid"
        )
        self.user_chip_lbl.configure(highlightbackground=COLOR_BORDER_LIGHT)
        self.user_chip_lbl.pack(side="left", padx=(0, 8))

        logout_btn = ttk.Button(
            right_box,
            text="Đăng xuất",
            style="Secondary.TButton",
            command=self._logout
        )
        logout_btn.pack(side="left")

    def _on_login_success(self, user_info: dict):
        self.current_user = user_info
        role_vn = "Quản trị viên" if user_info.get("role") == "admin" else "Người dùng"
        self.user_chip_var.set(f"👤 {user_info['username']} ({role_vn})")
        self.control_panel.show_user(user_info["username"], user_info["role"])
        self.deiconify()
        center_window(self)

    def _logout(self):
        """Xử lý đăng xuất tài khoản và mở lại cửa sổ đăng nhập."""
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất tài khoản?"):
            self.withdraw()
            self.current_user = None
            self._on_reset()
            LoginWindow(self, self.dm, self._on_login_success)

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Bản đồ mới", command=self._on_reset)
        file_menu.add_command(label="Lưu bản đồ", command=self._on_save_map)
        file_menu.add_command(label="Tải bản đồ", command=self._on_load_map)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.destroy)
        menubar.add_cascade(label="Tệp (File)", menu=file_menu)

        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="Đăng xuất", command=self._logout)
        menubar.add_cascade(label="Tài khoản", menu=account_menu)

        self.config(menu=menubar)

    def _on_reset(self):
        self.canvas.reset_grid()
        self.control_panel.show_result(0, 0, 0)

    def _on_run(self):
        if self.canvas.start is None or self.canvas.end is None:
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Vui lòng đặt điểm bắt đầu (Start) và điểm đích (Target) trên lưới trước khi chạy."
            )
            return

        grid = self._build_grid_from_canvas()

        start_time = time.perf_counter()
        visited_order, path = DEFAULT_ALGORITHM.find_path(grid)
        elapsed = time.perf_counter() - start_time

        self.dm.log_run_history({
            "username": self.current_user["username"],
            "algorithm": DEFAULT_ALGORITHM.name,
            "visited_count": len(visited_order),
            "path_length": len(path),
            "elapsed_sec": round(elapsed, 6),
        })

        def show_stats():
            self.control_panel.show_result(len(visited_order), len(path), elapsed)
            if not path:
                messagebox.showinfo("Kết quả", "Không tìm thấy đường đi giữa 2 điểm (bị chặn hoàn toàn).")

        self.canvas.animate_result(visited_order, path, on_done=show_stats)

    def _build_grid_from_canvas(self) -> Grid:
        grid = Grid(self.canvas.rows, self.canvas.cols)
        grid.start = self.canvas.start
        grid.end = self.canvas.end
        grid.obstacles = {tuple(w) for w in self.canvas.get_walls()}
        return grid

    def _on_save_map(self):
        if self.canvas.start is None or self.canvas.end is None:
            messagebox.showwarning("Thiếu dữ liệu", "Cần đặt điểm bắt đầu và điểm đích trước khi lưu bản đồ.")
            return
        name = simpledialog.askstring("Lưu bản đồ", "Nhập tên cho bản đồ này:")
        if not name:
            return
        map_data = {
            "map_name": name.strip(),
            "author": self.current_user["username"],
            "rows": self.canvas.rows,
            "cols": self.canvas.cols,
            "start": list(self.canvas.start),
            "end": list(self.canvas.end),
            "walls": self.canvas.get_walls(),
        }
        ok, msg = self.dm.save_map(map_data)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return
        messagebox.showinfo("Thành công", msg)

    def _on_load_map(self):
        maps = self.dm.get_all_maps()
        if not maps:
            messagebox.showinfo("Thông báo", "Chưa có bản đồ nào được lưu trong hệ thống.")
            return

        # Mở hộp thoại chọn bản đồ trực quan
        LoadMapDialog(self, maps, self._apply_loaded_map)

    def _apply_loaded_map(self, m: dict):
        self.canvas.load_state(m["rows"], m["cols"], m["start"], m["end"], m["walls"])
        self.control_panel.show_result(0, 0, 0)
        messagebox.showinfo("Tải bản đồ", f"Đã nạp thành công bản đồ: '{m['map_name']}'")


class LoadMapDialog(tk.Toplevel):
    """Hộp thoại trực quan cho phép người dùng chọn bản đồ từ danh sách thay vì phải gõ tay."""
    def __init__(self, master, maps: list, on_select_callback):
        super().__init__(master)
        self.title("Tải bản đồ đã lưu")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_APP)
        self.maps = maps
        self.on_select_callback = on_select_callback

        self._build_ui()
        self.grab_set()
        center_window(self, 400, 320)

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_BG_CARD, padx=16, pady=12, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header.pack(fill="x")
        tk.Label(header, text="📂 DANH SÁCH BẢN ĐỒ", font=FONT_SUBTITLE, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack()

        body = tk.Frame(self, bg=COLOR_BG_CARD, padx=18, pady=14, bd=1, relief="solid")
        body.configure(highlightbackground=COLOR_BORDER_LIGHT)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        tk.Label(body, text="Chọn bản đồ bạn muốn nạp vào lưới:", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w", pady=(0, 6))

        # Listbox kèm Scrollbar
        list_frame = tk.Frame(body, bg=COLOR_BG_CARD)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.map_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=FONT_BODY,
            selectbackground=COLOR_PRIMARY,
            selectforeground="#FFFFFF",
            bd=1,
            relief="solid"
        )
        scrollbar.config(command=self.map_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.map_listbox.pack(side="left", fill="both", expand=True)

        for m in self.maps:
            self.map_listbox.insert("end", f"🗺 {m['map_name']} (Tác giả: {m.get('author', 'N/A')})")

        self.map_listbox.selection_set(0)

        # Nút bấm
        btn_frame = tk.Frame(body, bg=COLOR_BG_CARD)
        btn_frame.pack(fill="x")

        load_btn = ttk.Button(btn_frame, text="Nạp bản đồ này", style="Primary.TButton", command=self._confirm_load)
        load_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        cancel_btn = ttk.Button(btn_frame, text="Hủy", style="Secondary.TButton", command=self.destroy)
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

        self.map_listbox.bind("<Double-Button-1>", lambda e: self._confirm_load())

    def _confirm_load(self):
        sel = self.map_listbox.curselection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 bản đồ từ danh sách.")
            return
        selected_map = self.maps[sel[0]]
        self.destroy()
        self.on_select_callback(selected_map)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
