import tkinter as tk
from tkinter import ttk, messagebox

from data_manager import DataManager
from email_service import send_otp_email, EmailServiceError


class LoginWindow(tk.Toplevel):
    def __init__(self, master, dm: DataManager, on_success):
        super().__init__(master)
        self.title("Đăng nhập")
        self.resizable(False, False)
        self.dm = dm
        self.on_success = on_success

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Tên đăng nhập:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Mật khẩu:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(btn_frame, text="Đăng nhập", command=self._login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Đăng ký", command=self._open_register).pack(side="left", padx=5)

        ttk.Button(frame, text="Quên mật khẩu?", command=self._open_forgot).grid(
            row=3, column=0, columnspan=2, pady=(10, 0))

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.grab_set()

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
        self.dm = dm

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Tên tài khoản:").grid(
            row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=28)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(frame, width=28)
        self.email_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Số điện thoại:").grid(row=2, column=0, sticky="w", pady=5)
        self.phone_entry = ttk.Entry(frame, width=28)
        self.phone_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Mật khẩu:").grid(row=3, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=28, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="Hoa, thường, số, ký tự đặc biệt, ≥8 ký tự",
                  foreground="#777777").grid(row=4, column=0, columnspan=2, sticky="w")

        ttk.Button(frame, text="Tạo tài khoản", command=self._on_register_clicked).grid(
            row=5, column=0, columnspan=2, pady=(15, 0))

        self.grab_set()

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
        self.title("Xác thực email")
        self.resizable(False, False)
        self.dm = dm
        self.username = username

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Nhập mã OTP đã gửi cho tài khoản '{username}':").grid(
            row=0, column=0, sticky="w", pady=5)
        self.otp_entry = ttk.Entry(frame, width=20)
        self.otp_entry.grid(row=1, column=0, pady=5)

        ttk.Button(frame, text="Xác thực", command=self._confirm).grid(
            row=2, column=0, pady=(15, 0))

        self.grab_set()

    def _confirm(self):
        otp = self.otp_entry.get().strip()
        ok, msg = self.dm.confirm_email_otp(self.username, otp)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return
        messagebox.showinfo("Thành công", msg)
        self.destroy()


class ForgotPasswordDialog(tk.Toplevel):
    """Demo quên mật khẩu bằng OTP: vì không có server gửi email/SMS thật,
    mã OTP được hiển thị trực tiếp trên giao diện để người dùng nhập lại bước 2."""

    def __init__(self, master, dm: DataManager):
        super().__init__(master)
        self.title("Quên mật khẩu")
        self.resizable(False, False)
        self.dm = dm

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Tên tài khoản:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=26)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Email hoặc SĐT đã đăng ký:").grid(
            row=1, column=0, sticky="w", pady=5)
        self.contact_entry = ttk.Entry(frame, width=26)
        self.contact_entry.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Gửi mã OTP", command=self._request_otp).grid(
            row=2, column=0, columnspan=2, pady=(10, 10))

        ttk.Separator(frame, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(frame, text="Mã OTP:").grid(row=4, column=0, sticky="w", pady=5)
        self.otp_entry = ttk.Entry(frame, width=26)
        self.otp_entry.grid(row=4, column=1, pady=5)

        ttk.Label(frame, text="Mật khẩu mới:").grid(row=5, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(frame, width=26, show="*")
        self.new_password_entry.grid(row=5, column=1, pady=5)

        ttk.Button(frame, text="Đặt lại mật khẩu", command=self._reset_password).grid(
            row=6, column=0, columnspan=2, pady=(10, 0))

        self.grab_set()

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