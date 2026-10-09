import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

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
        self.title("Ứng dụng mô phỏng tìm đường trên lưới")
        self.resizable(False, False)

        self.dm = DataManager()
        self.current_user = None

        self._build_menu()

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        self.canvas = GridCanvas(body, rows=20, cols=30, cell_size=24)
        self.canvas.pack(side="left", padx=10, pady=10)

        self.control_panel = ControlPanel(
            body,
            on_run=self._on_run,
            on_reset=self._on_reset,
            on_save=self._on_save_map,
            on_load=self._on_load_map,
            on_speed_change=self.canvas.set_speed,
            on_mode_change=self.canvas.set_mode,
        )
        self.control_panel.pack(side="right", fill="y", padx=10, pady=10)

        self.withdraw()
        LoginWindow(self, self.dm, self._on_login_success)

    def _on_login_success(self, user_info: dict):
        self.current_user = user_info
        self.control_panel.show_user(user_info["username"], user_info["role"])
        self.deiconify()

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Bản đồ mới", command=self._on_reset)
        file_menu.add_command(label="Lưu bản đồ", command=self._on_save_map)
        file_menu.add_command(label="Tải bản đồ", command=self._on_load_map)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.destroy)
        menubar.add_cascade(label="Tệp", menu=file_menu)

        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="Đăng xuất", command=self.destroy)
        menubar.add_cascade(label="Tài khoản", menu=account_menu)

        self.config(menu=menubar)

    def _on_reset(self):
        self.canvas.reset_grid()
        self.control_panel.show_result(0, 0, 0)

    def _on_run(self):
        if self.canvas.start is None or self.canvas.end is None:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng đặt điểm đầu và điểm đích trước.")
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
                messagebox.showinfo("Kết quả", "Không tìm thấy đường đi giữa 2 điểm.")

        self.canvas.animate_result(visited_order, path, on_done=show_stats)

    def _build_grid_from_canvas(self) -> Grid:
        grid = Grid(self.canvas.rows, self.canvas.cols)
        grid.start = self.canvas.start
        grid.end = self.canvas.end
        grid.obstacles = {tuple(w) for w in self.canvas.get_walls()}
        return grid

    def _on_save_map(self):
        if self.canvas.start is None or self.canvas.end is None:
            messagebox.showwarning("Thiếu dữ liệu", "Cần đặt điểm đầu/đích trước khi lưu.")
            return
        name = simpledialog.askstring("Lưu bản đồ", "Nhập tên bản đồ:")
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
            messagebox.showinfo("Trống", "Chưa có bản đồ nào được lưu.")
            return
        names = [m["map_name"] for m in maps]
        name = simpledialog.askstring(
            "Tải bản đồ", f"Nhập tên bản đồ cần tải:\nCác bản đồ có: {', '.join(names)}"
        )
        if not name:
            return
        matches = [m for m in maps if name.strip().lower() in m["map_name"].lower()]
        if not matches:
            messagebox.showerror("Lỗi", f"Không tìm thấy bản đồ '{name}'.")
            return
        m = matches[0]
        self.canvas.load_state(m["rows"], m["cols"], m["start"], m["end"], m["walls"])
        self.control_panel.show_result(0, 0, 0)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
