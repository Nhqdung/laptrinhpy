"""
theme.py
--------
Định nghĩa hệ thống màu sắc (Color Palette), Typography và cấu hình giao diện
ttk.Style hiện đại cho ứng dụng mô phỏng thuật toán tìm đường trên lưới.
"""

import tkinter as tk
from tkinter import ttk

# ==================== BẢNG MÀU HIỆN ĐẠI (COLOR PALETTE) ====================
COLOR_BG_APP = "#F1F5F9"         # Slate-100: Màu nền ứng dụng dịu mắt
COLOR_BG_CARD = "#FFFFFF"        # White: Thẻ/khối nội dung
COLOR_BORDER = "#CBD5E1"         # Slate-300: Đường viền thẻ
COLOR_BORDER_LIGHT = "#E2E8F0"   # Slate-200: Viền ngăn cách nhẹ

COLOR_PRIMARY = "#4F46E5"        # Indigo-600: Nút chính / điểm nhấn
COLOR_PRIMARY_HOVER = "#4338CA"  # Indigo-700
COLOR_PRIMARY_LIGHT = "#EEF2FF"  # Indigo-50

COLOR_SUCCESS = "#10B981"        # Emerald-500: Nút chạy / Bắt đầu
COLOR_SUCCESS_HOVER = "#059669"
COLOR_SUCCESS_LIGHT = "#ECFDF5"

COLOR_DANGER = "#EF4444"         # Red-500: Nút xóa / Cảnh báo
COLOR_DANGER_HOVER = "#DC2626"
COLOR_DANGER_LIGHT = "#FEF2F2"

COLOR_WARNING = "#F59E0B"        # Amber-500
COLOR_WARNING_LIGHT = "#FFFBEB"

COLOR_INFO = "#0284C7"           # Sky-600
COLOR_INFO_LIGHT = "#F0F9FF"

COLOR_TEXT_MAIN = "#0F172A"      # Slate-900: Tiêu đề, chữ chính
COLOR_TEXT_MUTED = "#64748B"     # Slate-500: Chữ phụ, mô tả
COLOR_TEXT_LIGHT = "#94A3B8"     # Slate-400: Gợi ý, nhãn mờ

# Màu sắc trên Grid Canvas
GRID_COLORS = {
    "empty": "#FFFFFF",
    "wall": "#1E293B",           # Slate-800: Tường đen xanh bóng bẩy
    "start": "#10B981",          # Xanh ngọc lục bảo (Start)
    "end": "#F43F5E",            # Đỏ hồng tươi (End)
    "visited": "#93C5FD",        # Xanh dương pastel mượt mà (Visited)
    "path": "#FBBF24",           # Vàng cam rực rỡ (Shortest Path)
    "grid_line": "#E2E8F0",      # Đường kẻ lưới mảnh nhẹ
    "grid_border": "#94A3B8",    # Viền ngoài của khung lưới
}

# ==================== TYPOGRAPHY (FONT CHỮ) ====================
FONT_NAME = "Segoe UI"
FONT_TITLE = (FONT_NAME, 14, "bold")
FONT_SUBTITLE = (FONT_NAME, 11, "bold")
FONT_HEADING = (FONT_NAME, 10, "bold")
FONT_BODY = (FONT_NAME, 10)
FONT_BODY_BOLD = (FONT_NAME, 10, "bold")
FONT_SMALL = (FONT_NAME, 9)
FONT_SMALL_BOLD = (FONT_NAME, 9, "bold")
FONT_TINY = (FONT_NAME, 8)
FONT_STAT_VAL = (FONT_NAME, 13, "bold")


def center_window(window: tk.Tk | tk.Toplevel, width: int = None, height: int = None):
    """Căn giữa cửa sổ trên màn hình desktop."""
    window.update_idletasks()
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def apply_theme(root: tk.Tk):
    """
    Khởi tạo và cấu hình bộ phong cách (ttk.Style) đồng bộ cho toàn bộ giao diện.
    Sử dụng theme 'clam' để có khả năng kiểm soát toàn bộ màu sắc, border, hover states.
    """
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=COLOR_BG_APP)

    # 1. Cấu hình Frame & Label chung
    style.configure("TFrame", background=COLOR_BG_APP)
    style.configure("Card.TFrame", background=COLOR_BG_CARD, relief="solid", borderwidth=1)
    
    style.configure(
        "TLabel",
        background=COLOR_BG_APP,
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY
    )
    style.configure(
        "Card.TLabel",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY
    )
    style.configure(
        "Header.TLabel",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT_MAIN,
        font=FONT_TITLE
    )
    style.configure(
        "SubHeader.TLabel",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT_MUTED,
        font=FONT_SMALL
    )
    style.configure(
        "Muted.TLabel",
        background=COLOR_BG_APP,
        foreground=COLOR_TEXT_MUTED,
        font=FONT_SMALL
    )

    # 2. Cấu hình LabelFrame (Card box)
    style.configure(
        "Card.TLabelframe",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT_MAIN,
        relief="solid",
        borderwidth=1,
        bordercolor=COLOR_BORDER
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=COLOR_BG_CARD,
        foreground=COLOR_PRIMARY,
        font=FONT_HEADING
    )

    # 3. Cấu hình Button - Phân cấp hành động rõ ràng
    # Nút mặc định
    style.configure(
        "TButton",
        font=FONT_BODY_BOLD,
        background="#E2E8F0",
        foreground=COLOR_TEXT_MAIN,
        borderwidth=1,
        focusthickness=0,
        focuscolor="none",
        padding=(10, 6)
    )
    style.map(
        "TButton",
        background=[("active", "#CBD5E1"), ("pressed", "#94A3B8")],
        relief=[("pressed", "sunken")]
    )

    # Nút Primary (Indigo)
    style.configure(
        "Primary.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 7)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", "#3730A3")]
    )

    # Nút Success (Emerald - Chạy thuật toán)
    style.configure(
        "Success.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_SUCCESS,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 7)
    )
    style.map(
        "Success.TButton",
        background=[("active", COLOR_SUCCESS_HOVER), ("pressed", "#047857")]
    )

    # Nút Danger (Rose - Reset)
    style.configure(
        "Danger.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_DANGER,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 7)
    )
    style.map(
        "Danger.TButton",
        background=[("active", COLOR_DANGER_HOVER), ("pressed", "#B91C1C")]
    )

    # Nút Secondary / Outline
    style.configure(
        "Secondary.TButton",
        font=FONT_BODY,
        background="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        borderwidth=1,
        bordercolor=COLOR_BORDER,
        padding=(10, 6)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#F8FAFC"), ("pressed", "#E2E8F0")]
    )

    # 4. Cấu hình Entry & Spinbox
    style.configure(
        "TEntry",
        fieldbackground="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        padding=6,
        borderwidth=1,
        font=FONT_BODY
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", COLOR_PRIMARY)]
    )

    style.configure(
        "TSpinbox",
        fieldbackground="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        padding=4,
        borderwidth=1,
        font=FONT_BODY
    )

    # 5. Cấu hình Radiobutton & Scale
    style.configure(
        "TRadiobutton",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY,
        padding=3
    )

    style.configure(
        "Horizontal.TScale",
        background=COLOR_BG_CARD,
        troughcolor="#E2E8F0",
        borderwidth=0
    )

    # 6. Cấu hình Separator
    style.configure("TSeparator", background=COLOR_BORDER_LIGHT)

    return style
