"""
grid_canvas.py
--------------
Custom Widget: kế thừa tk.Canvas để vẽ lưới ô vuông và xử lý toàn bộ tương tác chuột.

Quy ước click chuột trái:
    1) Click đầu tiên  -> đặt điểm ĐẦU (màu xanh lá)
    2) Click thứ hai    -> đặt điểm ĐÍCH (màu đỏ)
    3) Click/kéo sau đó -> vẽ VẬT CẢN (màu đen)
Click chuột phải trên 1 ô -> xóa ô đó về trạng thái trống (kể cả xóa start/end để đặt lại).
"""

import tkinter as tk

EMPTY, WALL, START, END, VISITED, PATH = "empty", "wall", "start", "end", "visited", "path"

COLOR_MAP = {
    EMPTY: "#ffffff",
    WALL: "#2b2b2b",
    START: "#2ecc71",
    END: "#e74c3c",
    VISITED: "#aed6f1",
    PATH: "#f4d03f",
}


class GridCanvas(tk.Canvas):
    def __init__(self, master, rows=20, cols=30, cell_size=24, **kwargs):
        width = cols * cell_size
        height = rows * cell_size
        super().__init__(master, width=width, height=height, bg="white",
                          highlightthickness=1, highlightbackground="#999999", **kwargs)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        self.states = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.end = None
        self.draw_mode = "start"  # "start" | "end" | "wall" - do ControlPanel điều khiển qua set_mode()
        self._rects = {}  # (r, c) -> canvas item id

        # tốc độ animation (ms giữa mỗi bước) - điều khiển bởi ControlPanel qua set_speed()
        self.step_delay_ms = 20
        self._animation_job = None

        self._draw_grid()
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<B1-Motion>", self._on_left_drag)
        self.bind("<Button-3>", self._on_right_click)

    # ---------------- Vẽ lưới ----------------
    def _draw_grid(self):
        self.delete("all")
        self._rects.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                x0, y0 = c * self.cell_size, r * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                rect_id = self.create_rectangle(
                    x0, y0, x1, y1,
                    fill=COLOR_MAP[self.states[r][c]], outline="#dddddd"
                )
                self._rects[(r, c)] = rect_id

    def _redraw_cell(self, r, c):
        self.itemconfig(self._rects[(r, c)], fill=COLOR_MAP[self.states[r][c]])

    def _cell_from_event(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None

    # ---------------- Sự kiện chuột ----------------
    def _on_left_click(self, event):
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell

        if self.draw_mode == "start":
            self._place_start(r, c)
        elif self.draw_mode == "end":
            self._place_end(r, c)
        else:  # "wall"
            self._toggle_wall(r, c)

    def _on_left_drag(self, event):
        # Kéo chuột chỉ có tác dụng khi đang ở chế độ vẽ vật cản (vẽ liên tiếp nhiều ô)
        if self.draw_mode != "wall":
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        if (r, c) != self.start and (r, c) != self.end and self.states[r][c] != WALL:
            self.states[r][c] = WALL
            self._redraw_cell(r, c)

    def _on_right_click(self, event):
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        if (r, c) == self.start:
            self.start = None
        if (r, c) == self.end:
            self.end = None
        self.states[r][c] = EMPTY
        self._redraw_cell(r, c)

    def _place_start(self, r, c):
        if (r, c) == self.end:
            return  # không cho trùng điểm đích
        if self.start is not None:
            old_r, old_c = self.start
            self.states[old_r][old_c] = EMPTY
            self._redraw_cell(old_r, old_c)
        self.start = (r, c)
        self._set_special_cell(r, c, START)

    def _place_end(self, r, c):
        if (r, c) == self.start:
            return  # không cho trùng điểm đầu
        if self.end is not None:
            old_r, old_c = self.end
            self.states[old_r][old_c] = EMPTY
            self._redraw_cell(old_r, old_c)
        self.end = (r, c)
        self._set_special_cell(r, c, END)

    def _set_special_cell(self, r, c, state):
        self.states[r][c] = state
        self._redraw_cell(r, c)

    def _toggle_wall(self, r, c):
        if (r, c) in (self.start, self.end):
            return
        self.states[r][c] = WALL if self.states[r][c] != WALL else EMPTY
        self._redraw_cell(r, c)

    # ---------------- API cho ControlPanel / MainWindow ----------------
    def set_mode(self, mode: str):
        """mode: 'start' | 'end' | 'wall' - đổi ý nghĩa của click chuột trái tiếp theo."""
        if mode in ("start", "end", "wall"):
            self.draw_mode = mode

    def set_speed(self, delay_ms: int):
        self.step_delay_ms = max(1, int(delay_ms))

    def reset_grid(self, rows=None, cols=None):
        """Xóa toàn bộ lưới về trạng thái ban đầu, có thể đổi kích thước."""
        if self._animation_job is not None:
            self.after_cancel(self._animation_job)
            self._animation_job = None
        if rows:
            self.rows = rows
        if cols:
            self.cols = cols
        self.config(width=self.cols * self.cell_size, height=self.rows * self.cell_size)
        self.states = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.draw_mode = "start"
        self._draw_grid()

    def clear_result_only(self):
        """Chỉ xóa các ô VISITED/PATH, giữ nguyên vật cản + start/end (dùng khi đổi thuật toán)."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.states[r][c] in (VISITED, PATH):
                    self.states[r][c] = EMPTY
                    self._redraw_cell(r, c)

    def get_walls(self):
        return [[r, c] for r in range(self.rows) for c in range(self.cols)
                if self.states[r][c] == WALL]

    def load_state(self, rows, cols, start, end, walls):
        """Nạp lại 1 bản đồ đã lưu (dùng khi Load Map từ MapManager)."""
        self.reset_grid(rows=rows, cols=cols)
        self.start = tuple(start)
        self.end = tuple(end)
        self._set_special_cell(*self.start, START)
        self._set_special_cell(*self.end, END)
        for w in walls:
            self.states[w[0]][w[1]] = WALL
            self._redraw_cell(w[0], w[1])

    def animate_result(self, visited_order, path, on_done=None):
        """
        Chạy animation: tô màu lần lượt các ô đã duyệt (visited_order), sau đó tô đường đi (path).
        visited_order, path: list các tuple (r, c).
        on_done: callback gọi khi animation kết thúc (vd để hiển thị số bước/thời gian).
        """
        self.clear_result_only()
        self._animate_step(list(visited_order), list(path), on_done)

    def _animate_step(self, remaining_visited, path, on_done):
        if remaining_visited:
            r, c = remaining_visited.pop(0)
            if (r, c) not in (self.start, self.end):
                self.states[r][c] = VISITED
                self._redraw_cell(r, c)
            self._animation_job = self.after(
                self.step_delay_ms, self._animate_step, remaining_visited, path, on_done
            )
        elif path:
            self._animate_path(path, on_done)
        else:
            self._animation_job = None
            if on_done:
                on_done()

    def _animate_path(self, remaining_path, on_done):
        if remaining_path:
            r, c = remaining_path.pop(0)
            if (r, c) not in (self.start, self.end):
                self.states[r][c] = PATH
                self._redraw_cell(r, c)
            self._animation_job = self.after(
                self.step_delay_ms, self._animate_path, remaining_path, on_done
            )
        else:
            self._animation_job = None
            if on_done:
                on_done()
