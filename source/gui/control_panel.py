"""
control_panel.py
----------------
Bảng điều khiển trực quan (Sidebar): lựa chọn công cụ vẽ, điều chỉnh tốc độ,
các nút thao tác chạy/reset/lưu/tải và bảng thống kê kết quả dạng thẻ chỉ số (Metric Cards).
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_SUCCESS,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    FONT_HEADING, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_VAL, FONT_TINY
)


class ControlPanel(ttk.Frame):
    def __init__(self, master, on_run, on_reset, on_save, on_load,
                 on_speed_change, on_mode_change):
        super().__init__(master, padding=12)

        self.speed_var = tk.IntVar(value=20)
        self.mode_var = tk.StringVar(value="start")
        self._on_speed_change = on_speed_change
        self._on_mode_change = on_mode_change

        self._build_ui(on_run, on_reset, on_save, on_load)
        self._on_mode_change(self.mode_var.get())

    def _build_ui(self, on_run, on_reset, on_save, on_load):
        # 1. Thẻ chọn chế độ vẽ
        tool_frame = ttk.LabelFrame(self, text="  🛠 Chế độ vẽ  ", style="Card.TLabelframe", padding=(12, 10))
        tool_frame.pack(fill="x", pady=(0, 10))

        modes = [
            ("🟢  Điểm bắt đầu (Start)", "start"),
            ("🔴  Điểm đích (Target)", "end"),
            ("⬛  Vẽ vật cản (Wall)", "wall"),
        ]
        for text, val in modes:
            rb = ttk.Radiobutton(
                tool_frame,
                text=text,
                value=val,
                variable=self.mode_var,
                command=self._on_mode_selected
            )
            rb.pack(anchor="w", pady=3)

        hint_lbl = ttk.Label(
            tool_frame,
            text="💡 Chuột trái: Đặt / Vẽ tường\n    Chuột phải: Xóa ô",
            style="SubHeader.TLabel",
            justify="left"
        )
        hint_lbl.pack(anchor="w", pady=(6, 0))

        # 2. Thẻ điều chỉnh tốc độ
        speed_frame = ttk.LabelFrame(self, text="  ⚡ Tốc độ mô phỏng  ", style="Card.TLabelframe", padding=(12, 10))
        speed_frame.pack(fill="x", pady=(0, 10))

        scale_row = ttk.Frame(speed_frame, style="Card.TFrame")
        scale_row.pack(fill="x", pady=(2, 2))

        self.speed_scale = ttk.Scale(
            scale_row,
            from_=1,
            to=200,
            orient="horizontal",
            style="Horizontal.TScale",
            command=self._on_scale_moved
        )
        self.speed_scale.set(self.speed_var.get())
        self.speed_scale.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.speed_spin = ttk.Spinbox(
            scale_row,
            from_=1,
            to=200,
            textvariable=self.speed_var,
            width=4,
            command=self._on_speed_entry_changed
        )
        self.speed_spin.pack(side="right")
        self.speed_spin.bind("<Return>", lambda e: self._on_speed_entry_changed())
        self.speed_spin.bind("<FocusOut>", lambda e: self._on_speed_entry_changed())

        speed_hint = ttk.Frame(speed_frame, style="Card.TFrame")
        speed_hint.pack(fill="x", pady=(4, 0))
        ttk.Label(speed_hint, text="Nhanh (1ms)", font=FONT_TINY, foreground=COLOR_TEXT_MUTED, background=COLOR_BG_CARD).pack(side="left")
        ttk.Label(speed_hint, text="Chậm (200ms)", font=FONT_TINY, foreground=COLOR_TEXT_MUTED, background=COLOR_BG_CARD).pack(side="right")

        # 3. Thẻ các nút hành động (Actions)
        action_frame = ttk.LabelFrame(self, text="  🎮 Điều khiển  ", style="Card.TLabelframe", padding=(12, 10))
        action_frame.pack(fill="x", pady=(0, 10))

        run_btn = ttk.Button(action_frame, text="▶  CHẠY TÌM ĐƯỜNG", style="Success.TButton", command=on_run)
        run_btn.pack(fill="x", pady=(2, 6))

        reset_btn = ttk.Button(action_frame, text="⟲  Reset lưới", style="Danger.TButton", command=on_reset)
        reset_btn.pack(fill="x", pady=(0, 8))

        map_btn_frame = ttk.Frame(action_frame, style="Card.TFrame")
        map_btn_frame.pack(fill="x")
        ttk.Button(map_btn_frame, text="💾 Lưu", style="Secondary.TButton", command=on_save).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(map_btn_frame, text="📂 Tải", style="Secondary.TButton", command=on_load).pack(side="right", fill="x", expand=True, padx=(4, 0))

        # 4. Thẻ thống kê kết quả (Live Metrics Card)
        stat_frame = ttk.LabelFrame(self, text="  📊 Thống kê kết quả  ", style="Card.TLabelframe", padding=(12, 10))
        stat_frame.pack(fill="x", pady=(0, 10))

        # 3 Card thống kê con
        self.stat_visited_var = tk.StringVar(value="-")
        self.stat_path_var = tk.StringVar(value="-")
        self.stat_time_var = tk.StringVar(value="-")

        self._create_metric_card(stat_frame, "🔍 Ô đã duyệt", self.stat_visited_var)
        self._create_metric_card(stat_frame, "📏 Độ dài đường đi", self.stat_path_var)
        self._create_metric_card(stat_frame, "⏱ Thời gian chạy", self.stat_time_var)

        # 5. Chú giải màu sắc (Legend)
        legend_frame = ttk.LabelFrame(self, text="  🎨 Chú giải màu sắc  ", style="Card.TLabelframe", padding=(10, 8))
        legend_frame.pack(fill="x", pady=(0, 10))

        legend_items = [
            ("🟢 Bắt đầu (S)", "🔴 Đích đến (E)"),
            ("⬛ Vật cản (Wall)", "🟦 Đã duyệt"),
            ("🟨 Đường đi ngắn nhất", ""),
        ]
        for row in legend_items:
            r_frame = ttk.Frame(legend_frame, style="Card.TFrame")
            r_frame.pack(fill="x", pady=1)
            ttk.Label(r_frame, text=row[0], font=FONT_TINY, foreground=COLOR_TEXT_MAIN, background=COLOR_BG_CARD).pack(side="left")
            if row[1]:
                ttk.Label(r_frame, text=row[1], font=FONT_TINY, foreground=COLOR_TEXT_MAIN, background=COLOR_BG_CARD).pack(side="right")

        # 6. Trạng thái người dùng
        self.status_var = tk.StringVar(value="Chưa đăng nhập")
        status_box = ttk.Frame(self, style="Card.TFrame", padding=(8, 6))
        status_box.pack(fill="x", side="bottom")
        self.user_lbl = ttk.Label(status_box, textvariable=self.status_var, font=FONT_SMALL, foreground=COLOR_TEXT_MUTED, background=COLOR_BG_CARD)
        self.user_lbl.pack(anchor="w")

    def _create_metric_card(self, parent, label_text, var):
        card = tk.Frame(parent, bg=COLOR_PRIMARY_LIGHT, bd=1, relief="solid", highlightthickness=0)
        card.configure(highlightbackground=COLOR_BORDER_LIGHT)
        card.pack(fill="x", pady=3)

        inner = tk.Frame(card, bg=COLOR_PRIMARY_LIGHT, padx=8, pady=4)
        inner.pack(fill="x")

        lbl = tk.Label(inner, text=label_text, font=FONT_TINY, fg=COLOR_TEXT_MUTED, bg=COLOR_PRIMARY_LIGHT)
        lbl.pack(side="left")

        val = tk.Label(inner, textvariable=var, font=FONT_STAT_VAL, fg=COLOR_PRIMARY, bg=COLOR_PRIMARY_LIGHT)
        val.pack(side="right")

    def _on_mode_selected(self):
        self._on_mode_change(self.mode_var.get())

    def _on_scale_moved(self, value_str):
        value = int(float(value_str))
        self.speed_var.set(value)
        self._on_speed_change(value)

    def _on_speed_entry_changed(self):
        try:
            value = int(self.speed_var.get())
        except (ValueError, tk.TclError):
            value = 20
        value = max(1, min(200, value))
        self.speed_var.set(value)
        self.speed_scale.set(value)
        self._on_speed_change(value)

    def show_result(self, visited_count: int, path_length: int, elapsed_seconds: float):
        if visited_count == 0 and path_length == 0 and elapsed_seconds == 0:
            self.stat_visited_var.set("-")
            self.stat_path_var.set("-")
            self.stat_time_var.set("-")
        else:
            self.stat_visited_var.set(f"{visited_count} ô")
            self.stat_path_var.set(f"{path_length} bước" if path_length > 0 else "Không tìm thấy")
            self.stat_time_var.set(f"{elapsed_seconds * 1000:.2f} ms")

    def show_user(self, username: str, role: str):
        role_vn = "Quản trị viên" if role == "admin" else "Người dùng"
        self.status_var.set(f"👤 {username} ({role_vn})")
