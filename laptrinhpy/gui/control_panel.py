import tkinter as tk
from tkinter import ttk


class ControlPanel(ttk.Frame):
    def __init__(self, master, on_run, on_reset, on_save, on_load,
                 on_speed_change, on_mode_change):
        super().__init__(master, padding=10)

        self.speed_var = tk.IntVar(value=20)
        self.mode_var = tk.StringVar(value="start")
        self._on_speed_change = on_speed_change

        row = 0

        ttk.Label(self, text="Chế độ vẽ:").grid(row=row, column=0, columnspan=3,
                                                  sticky="w", pady=(0, 2))
        row += 1
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=row, column=0, columnspan=3, sticky="ew")
        ttk.Radiobutton(mode_frame, text="🟢 Điểm đầu", value="start",
                         variable=self.mode_var, command=self._on_mode_selected).pack(
            anchor="w", pady=1)
        ttk.Radiobutton(mode_frame, text="🔴 Điểm đích", value="end",
                         variable=self.mode_var, command=self._on_mode_selected).pack(
            anchor="w", pady=1)
        ttk.Radiobutton(mode_frame, text="⬛ Vật cản", value="wall",
                         variable=self.mode_var, command=self._on_mode_selected).pack(
            anchor="w", pady=1)
        row += 1
        ttk.Label(self, text="(Click phải để xóa ô)",
                  foreground="#777777").grid(row=row, column=0, columnspan=3,
                                              sticky="w", pady=(0, 6))
        row += 1

        ttk.Label(self, text="Tốc độ (ms/bước):").grid(row=row, column=0, sticky="w", pady=4)
        self.speed_scale = ttk.Scale(
            self, from_=1, to=200, orient="horizontal",
            command=self._on_scale_moved
        )
        self.speed_scale.set(self.speed_var.get())
        self.speed_scale.grid(row=row, column=1, sticky="ew", pady=4)

        self.speed_spin = ttk.Spinbox(
            self, from_=1, to=200, textvariable=self.speed_var, width=5,
            command=self._on_speed_entry_changed
        )
        self.speed_spin.grid(row=row, column=2, sticky="w", padx=(5, 0))
        self.speed_spin.bind("<Return>", lambda e: self._on_speed_entry_changed())
        self.speed_spin.bind("<FocusOut>", lambda e: self._on_speed_entry_changed())
        row += 1

        ttk.Button(self, text="▶ Chạy", command=on_run).grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=(14, 2))
        row += 1
        ttk.Button(self, text="⟲ Reset lưới", command=on_reset).grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=2)
        row += 1
        ttk.Button(self, text="💾 Lưu bản đồ", command=on_save).grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=2)
        row += 1
        ttk.Button(self, text="📂 Tải bản đồ", command=on_load).grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=2)
        row += 1

        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1

        self.result_var = tk.StringVar(value="Ô đã duyệt: -    Độ dài đường đi: -    Thời gian: -")
        ttk.Label(self, textvariable=self.result_var, wraplength=190).grid(
            row=row, column=0, columnspan=3, sticky="w")
        row += 1

        self.status_var = tk.StringVar(value="Chưa đăng nhập")
        ttk.Label(self, textvariable=self.status_var, foreground="#555555").grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(20, 0))

        self.columnconfigure(1, weight=1)

        self._on_mode_change = on_mode_change
        self._on_mode_change(self.mode_var.get())

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
        self.result_var.set(
            f"Ô đã duyệt: {visited_count}    "
            f"Độ dài đường đi: {path_length} bước    "
            f"Thời gian: {elapsed_seconds*1000:.2f} ms"
        )

    def show_user(self, username: str, role: str):
        self.status_var.set(f"Đăng nhập: {username} ({role})")
