"""
login_window.py
---------------
Giao diện Đăng nhập, Đăng ký, Quên mật khẩu và Xác thực OTP.
Được thiết kế hiện đại, căn giữa màn hình, thẻ Card sạch sẽ với font Segoe UI và biểu tượng trực quan.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from data_manager import DataManager
from email_service import send_otp_email, EmailServiceError
from gui.theme import (
    center_window,
    COLOR_BG_APP, COLOR_BG_CARD, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_TINY
)


class LoginWindow(tk.Toplevel):
    def __init__(self, master, dm: DataManager, on_success):
        super().__init__(master)
        self.title("Đăng nhập hệ thống")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_APP)
        self.dm = dm
        self.on_success = on_success

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.grab_set()
        center_window(self, 400, 480)

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg=COLOR_BG_CARD, padx=20, pady=16, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header.pack(fill="x")

        logo_lbl = tk.Label(
            header,
            text="🧭 TÌM ĐƯỜNG TRÊN LƯỚI",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=COLOR_BG_CARD
        )
        logo_lbl.pack()

        sub_lbl = tk.Label(
            header,
            text="Hệ thống mô phỏng tìm đường trên lưới",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG_CARD
        )
        sub_lbl.pack(pady=(2, 0))

        # 2. Body Form Card
        card = tk.Frame(self, bg=COLOR_BG_CARD, padx=24, pady=20, bd=1, relief="solid")
        card.configure(highlightbackground=COLOR_BORDER_LIGHT)
        card.pack(fill="both", expand=True, padx=20, pady=16)

        title_lbl = tk.Label(card, text="ĐĂNG NHẬP", font=FONT_SUBTITLE, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD)
        title_lbl.pack(anchor="w", pady=(0, 14))

        # Input: Username
        tk.Label(card, text="👤 Tên đăng nhập:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.username_entry = ttk.Entry(card, font=FONT_BODY)
        self.username_entry.pack(fill="x", pady=(4, 12))
        self.username_entry.focus()

        # Input: Password
        pwd_header = tk.Frame(card, bg=COLOR_BG_CARD)
        pwd_header.pack(fill="x")
        tk.Label(pwd_header, text="🔑 Mật khẩu:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(side="left")

        pwd_frame = tk.Frame(card, bg=COLOR_BG_CARD)
        pwd_frame.pack(fill="x", pady=(4, 16))
        self.password_entry = ttk.Entry(pwd_frame, show="•", font=FONT_BODY)
        self.password_entry.pack(side="left", fill="x", expand=True)

        self._show_pwd = False
        self.toggle_pwd_btn = tk.Button(
            pwd_frame, text="👁", font=FONT_TINY, relief="flat", bd=0,
            bg="#E2E8F0", cursor="hand2", command=self._toggle_password_visibility
        )
        self.toggle_pwd_btn.pack(side="right", padx=(4, 0))

        # Nút Đăng nhập (Primary)
        login_btn = ttk.Button(card, text="Đăng nhập ngay", style="Primary.TButton", command=self._login)
        login_btn.pack(fill="x", pady=(4, 10))

        # Liên kết Đăng ký & Quên mật khẩu
        footer_links = tk.Frame(card, bg=COLOR_BG_CARD)
        footer_links.pack(fill="x", pady=(6, 0))

        reg_btn = ttk.Button(footer_links, text="Tạo tài khoản", style="Secondary.TButton", command=self._open_register)
        reg_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        forgot_btn = ttk.Button(footer_links, text="Quên mật khẩu?", style="Secondary.TButton", command=self._open_forgot)
        forgot_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Enter để submit
        self.username_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.bind("<Return>", lambda e: self._login())

    def _toggle_password_visibility(self):
        self._show_pwd = not self._show_pwd
        self.password_entry.configure(show="" if self._show_pwd else "•")

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        ok, result = self.dm.authenticate_user(username, password)
        if not ok:
            messagebox.showerror("Đăng nhập thất bại", result)
            return
        user_info = {
            "username": result["username"],
            "email": result.get("email", ""),
            "phone": result.get("phone", ""),
            "role": result["role"],
        }
        self.destroy()
        self.on_success(user_info)

    def _open_register(self):
        RegisterDialog(self, self.dm)

    def _open_forgot(self):
        ForgotPasswordDialog(self, self.dm)


class RegisterDialog(tk.Toplevel):
    def __init__(self, master, dm: DataManager):
        super().__init__(master)
        self.title("Đăng ký tài khoản")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_APP)
        self.dm = dm

        self._build_ui()
        self.grab_set()
        center_window(self, 420, 550)

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_BG_CARD, padx=20, pady=12, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header.pack(fill="x")

        tk.Label(header, text="✨ TẠO TÀI KHOẢN MỚI", font=FONT_SUBTITLE, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack()

        # Body Card
        card = tk.Frame(self, bg=COLOR_BG_CARD, padx=24, pady=16, bd=1, relief="solid")
        card.configure(highlightbackground=COLOR_BORDER_LIGHT)
        card.pack(fill="both", expand=True, padx=20, pady=14)

        # Fields
        tk.Label(card, text="Tên tài khoản:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.username_entry = ttk.Entry(card, font=FONT_BODY)
        self.username_entry.pack(fill="x", pady=(2, 8))

        tk.Label(card, text="Email liên hệ:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.email_entry = ttk.Entry(card, font=FONT_BODY)
        self.email_entry.pack(fill="x", pady=(2, 8))

        tk.Label(card, text="Số điện thoại:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.phone_entry = ttk.Entry(card, font=FONT_BODY)
        self.phone_entry.pack(fill="x", pady=(2, 8))

        tk.Label(card, text="Mật khẩu:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.password_entry = ttk.Entry(card, show="•", font=FONT_BODY)
        self.password_entry.pack(fill="x", pady=(2, 6))

        # Ghi chú mật khẩu
        tip_box = tk.Frame(card, bg=COLOR_PRIMARY_LIGHT, padx=8, pady=6, bd=1, relief="solid")
        tip_box.configure(highlightbackground=COLOR_BORDER_LIGHT)
        tip_box.pack(fill="x", pady=(0, 14))
        tk.Label(
            tip_box,
            text="📌 Mật khẩu tối thiểu 8 ký tự, gồm cả chữ hoa,\nchữ thường, chữ số và ký tự đặc biệt.",
            font=FONT_TINY,
            fg=COLOR_PRIMARY,
            bg=COLOR_PRIMARY_LIGHT,
            justify="left"
        ).pack(anchor="w")

        # Nút xác nhận
        submit_btn = ttk.Button(card, text="Tạo tài khoản", style="Primary.TButton", command=self._on_register_clicked)
        submit_btn.pack(fill="x", pady=(4, 12))

    def _on_register_clicked(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        ok, msg, otp = self.dm.register_user(username, password, email, phone)
        if not ok:
            messagebox.showerror("Đăng ký thất bại", msg)
            return

        if "@" in email:
            try:
                send_otp_email(email, otp)
                messagebox.showinfo(
                    "Cần xác thực email",
                    f"{msg}\nMã xác nhận đã gửi tới {email}, hãy kiểm tra hộp thư."
                )
            except EmailServiceError as e:
                messagebox.showwarning(
                    "Không gửi được email",
                    f"{e}\n\nMã OTP: {otp}"
                )
        else:
            messagebox.showinfo("Cần xác thực email", f"{msg}\nMã OTP: {otp}")

        parent = self.master
        self.destroy()
        ConfirmEmailDialog(parent, self.dm, username)


class ConfirmEmailDialog(tk.Toplevel):
    def __init__(self, master, dm: DataManager, username: str):
        super().__init__(master)
        self.title("Xác thực email OTP")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_APP)
        self.dm = dm
        self.username = username

        self._build_ui()
        self.grab_set()
        center_window(self, 380, 260)

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_BG_CARD, padx=16, pady=10, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header.pack(fill="x")
        tk.Label(header, text="🔑 XÁC THỰC EMAIL", font=FONT_SUBTITLE, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack()

        card = tk.Frame(self, bg=COLOR_BG_CARD, padx=20, pady=16, bd=1, relief="solid")
        card.configure(highlightbackground=COLOR_BORDER_LIGHT)
        card.pack(fill="both", expand=True, padx=16, pady=14)

        tk.Label(
            card,
            text=f"Nhập mã OTP đã gửi cho tài khoản '{self.username}':",
            font=FONT_BODY,
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_BG_CARD,
            wraplength=320
        ).pack(anchor="w", pady=(0, 8))

        self.otp_entry = ttk.Entry(card, font=("Segoe UI", 14, "bold"), justify="center")
        self.otp_entry.pack(fill="x", pady=(0, 14))
        self.otp_entry.focus()

        confirm_btn = ttk.Button(card, text="Xác thực ngay", style="Primary.TButton", command=self._confirm)
        confirm_btn.pack(fill="x")

        self.otp_entry.bind("<Return>", lambda e: self._confirm())

    def _confirm(self):
        otp = self.otp_entry.get().strip()
        ok, msg = self.dm.confirm_email_otp(self.username, otp)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return
        messagebox.showinfo("Thành công", msg)
        self.destroy()


class ForgotPasswordDialog(tk.Toplevel):
    def __init__(self, master, dm: DataManager):
        super().__init__(master)
        self.title("Khôi phục mật khẩu")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG_APP)
        self.dm = dm

        self._build_ui()
        self.grab_set()
        center_window(self, 430, 570)

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_BG_CARD, padx=16, pady=12, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER_LIGHT)
        header.pack(fill="x")
        tk.Label(header, text="🔒 QUÊN MẬT KHẨU", font=FONT_SUBTITLE, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack()

        card = tk.Frame(self, bg=COLOR_BG_CARD, padx=20, pady=16, bd=1, relief="solid")
        card.configure(highlightbackground=COLOR_BORDER_LIGHT)
        card.pack(fill="both", expand=True, padx=16, pady=12)

        # Bước 1: Gửi OTP
        tk.Label(card, text="1. Nhập thông tin tài khoản:", font=FONT_BODY_BOLD, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack(anchor="w")

        tk.Label(card, text="Tên tài khoản:", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w", pady=(4, 0))
        self.username_entry = ttk.Entry(card, font=FONT_BODY)
        self.username_entry.pack(fill="x", pady=(2, 6))

        tk.Label(card, text="Email hoặc SĐT đã đăng ký:", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.contact_entry = ttk.Entry(card, font=FONT_BODY)
        self.contact_entry.pack(fill="x", pady=(2, 6))

        send_otp_btn = ttk.Button(card, text="Gửi mã xác nhận OTP", style="Secondary.TButton", command=self._request_otp)
        send_otp_btn.pack(fill="x", pady=(4, 10))

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=6)

        # Bước 2: Nhập OTP và mật khẩu mới
        tk.Label(card, text="2. Đặt lại mật khẩu mới:", font=FONT_BODY_BOLD, fg=COLOR_PRIMARY, bg=COLOR_BG_CARD).pack(anchor="w")

        tk.Label(card, text="Mã OTP:", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w", pady=(4, 0))
        self.otp_entry = ttk.Entry(card, font=FONT_BODY)
        self.otp_entry.pack(fill="x", pady=(2, 6))

        tk.Label(card, text="Mật khẩu mới:", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_BG_CARD).pack(anchor="w")
        self.new_password_entry = ttk.Entry(card, show="•", font=FONT_BODY)
        self.new_password_entry.pack(fill="x", pady=(2, 12))

        reset_btn = ttk.Button(card, text="Đặt lại mật khẩu", style="Primary.TButton", command=self._reset_password)
        reset_btn.pack(fill="x", pady=(8, 12))

    def _request_otp(self):
        username = self.username_entry.get().strip()
        contact = self.contact_entry.get().strip()
        ok, msg, otp = self.dm.request_password_reset(username, contact)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return

        if "@" in contact:
            try:
                send_otp_email(contact, otp)
                messagebox.showinfo("Đã gửi mã", f"Mã OTP đã được gửi tới {contact}, kiểm tra hộp thư.")
            except EmailServiceError as e:
                messagebox.showwarning(
                    "Không gửi được email",
                    f"{e}\n\nMã OTP (hiển thị tạm để bạn vẫn dùng được): {otp}"
                )
        else:
            messagebox.showinfo(
                "Đã sinh mã (demo)",
                f"Chưa hỗ trợ gửi SMS thật, hiển thị trực tiếp để demo.\nMã OTP: {otp}"
            )

    def _reset_password(self):
        username = self.username_entry.get().strip()
        otp = self.otp_entry.get().strip()
        new_password = self.new_password_entry.get()
        ok, msg = self.dm.verify_otp_and_reset_password(username, otp, new_password)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return
        messagebox.showinfo("Thành công", msg)
        self.destroy()