"""
grid_canvas.py
--------------
Custom Widget: kế thừa tk.Canvas để vẽ lưới ô vuông và xử lý tương tác chuột.
Giao diện được thiết kế hiện đại, màu sắc trực quan, hiển thị ký hiệu điểm bắt đầu và đích.

Quy ước click chuột trái:
    1) Chế độ "start": đặt điểm BẮT ĐẦU (Start - màu xanh ngọc, ký hiệu 'S')
    2) Chế độ "end": đặt điểm ĐÍCH (Target - màu đỏ hồng, ký hiệu 'E')
    3) Chế độ "wall": vẽ VẬT CẢN (Wall - màu xám than sang trọng)
Click chuột phải trên 1 ô -> xóa ô đó về trạng thái trống (kể cả xóa start/end để đặt lại).
"""

import tkinter as tk
from gui.theme import GRID_COLORS, COLOR_BORDER

EMPTY, WALL, START, END, VISITED, PATH = "empty", "wall", "start", "end", "visited", "path"

COLOR_MAP = {
    EMPTY: GRID_COLORS["empty"],
    WALL: GRID_COLORS["wall"],
    START: GRID_COLORS["start"],
    END: GRID_COLORS["end"],
    VISITED: GRID_COLORS["visited"],
    PATH: GRID_COLORS["path"],
}


class GridCanvas(tk.Canvas):
    def __init__(self, master, rows=20, cols=30, cell_size=24, **kwargs):
        width = cols * cell_size
        height = rows * cell_size
        super().__init__(
            master,
            width=width,
            height=height,
            bg=GRID_COLORS["empty"],
            highlightthickness=2,
            highlightbackground=COLOR_BORDER,
            **kwargs
        )
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        self.states = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.end = None
        self.draw_mode = "start"
        self._rects = {}    # (r, c) -> canvas item id (rectangle)
        self._markers = {}  # (r, c) -> canvas item id (icon/text S or E)

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
        self._markers.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                x0, y0 = c * self.cell_size, r * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                rect_id = self.create_rectangle(
                    x0, y0, x1, y1,
                    fill=COLOR_MAP[self.states[r][c]],
                    outline=GRID_COLORS["grid_line"],
                    width=1
                )
                self._rects[(r, c)] = rect_id

    def _redraw_cell(self, r, c):
        state = self.states[r][c]
        self.itemconfig(
            self._rects[(r, c)],
            fill=COLOR_MAP[state],
            outline=GRID_COLORS["wall"] if state == WALL else GRID_COLORS["grid_line"]
        )

        # Xóa marker cũ nếu có
        if (r, c) in self._markers:
            self.delete(self._markers[(r, c)])
            del self._markers[(r, c)]

        # Vẽ ký hiệu cho điểm Start hoặc End
        if state in (START, END):
            cx = c * self.cell_size + self.cell_size / 2
            cy = r * self.cell_size + self.cell_size / 2
            label_text = "S" if state == START else "E"
            marker_id = self.create_text(
                cx, cy,
                text=label_text,
                fill="#FFFFFF",
                font=("Segoe UI", int(self.cell_size * 0.48), "bold")
            )
            self._markers[(r, c)] = marker_id

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
            return
        if self.start is not None:
            old_r, old_c = self.start
            self.states[old_r][old_c] = EMPTY
            self._redraw_cell(old_r, old_c)
        self.start = (r, c)
        self._set_special_cell(r, c, START)

    def _place_end(self, r, c):
        if (r, c) == self.start:
            return
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
        if mode in ("start", "end", "wall"):
            self.draw_mode = mode

    def set_speed(self, delay_ms: int):
        self.step_delay_ms = max(1, int(delay_ms))

    def reset_grid(self, rows=None, cols=None):
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
        for r in range(self.rows):
            for c in range(self.cols):
                if self.states[r][c] in (VISITED, PATH):
                    self.states[r][c] = EMPTY
                    self._redraw_cell(r, c)

    def get_walls(self):
        return [[r, c] for r in range(self.rows) for c in range(self.cols)
                if self.states[r][c] == WALL]

    def load_state(self, rows, cols, start, end, walls):
        self.reset_grid(rows=rows, cols=cols)
        self.start = tuple(start)
        self.end = tuple(end)
        self._set_special_cell(*self.start, START)
        self._set_special_cell(*self.end, END)
        for w in walls:
            self.states[w[0]][w[1]] = WALL
            self._redraw_cell(w[0], w[1])

    def animate_result(self, visited_order, path, on_done=None):
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
