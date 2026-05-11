# profile_gui.py  –  user profile dialog with password change  (v2.1)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from gui.theme import (C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED, btn,
                       labeled_entry, pw_strength_bar, eye_toggle, status_badge)


class ProfileDialog(tk.Toplevel):
    """Shows current user profile and allows password change in a dialog."""
    def __init__(self, master, current_user, auth_controller) -> None:
        super().__init__(master)
        self.user      = current_user
        self.auth_ctrl = auth_controller
        self.title("Thông tin cá nhân")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)
        self.grab_set()
        
        # We reuse the same UI builder in a frame
        self.content = ProfileFrame(self, current_user, auth_controller)
        self.content.pack(fill="both", expand=True)
        # Overwrite the Close button to destroy dialog
        self.content.close_btn.config(command=self.destroy)
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")


class ProfileFrame(tk.Frame):
    """Integrated Profile page for the main dashboard area."""
    def __init__(self, master, current_user, auth_controller) -> None:
        super().__init__(master, bg=C_SURFACE)
        self.user = current_user
        self.auth_ctrl = auth_controller
        self._build()

    def _build(self) -> None:
        role_colors = {
            "Admin":      ("#4f46e5", "#eef2ff"),
            "Giang vien": ("#15803d", "#dcfce7"),
            "Sinh vien":  ("#854d0e", "#fef9c3"),
        }
        fg, bg = role_colors.get(self.user.role, ("#475569", "#f1f5f9"))

        # Header
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=30, pady=25)
        hdr.pack(fill="x")

        av_c = tk.Canvas(hdr, width=70, height=70, bg=C_PRIMARY, highlightthickness=0)
        av_c.pack(side="left", padx=(0, 20))
        av_c.create_oval(2, 2, 68, 68, fill="#4f46e5", outline="#c7d2fe", width=2)
        initials = "".join(p[0] for p in self.user.full_name.split()[:2]).upper()
        av_c.create_text(35, 35, text=initials, fill="white", font=("Segoe UI", 22, "bold"))

        info = tk.Frame(hdr, bg=C_PRIMARY)
        info.pack(side="left", fill="both")
        tk.Label(info, text=self.user.full_name, bg=C_PRIMARY, fg="white", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(info, text=f"@{self.user.username}  •  ID: {self.user.user_id}", bg=C_PRIMARY, fg="#c7d2fe", font=("Segoe UI", 10)).pack(anchor="w")
        
        badge_f = tk.Frame(info, bg=bg, padx=12, pady=4)
        badge_f.pack(anchor="w", pady=(8, 0))
        tk.Label(badge_f, text=self.user.role.upper(), bg=bg, fg=fg, font=("Segoe UI", 7, "bold")).pack()

        # Body
        body = tk.Frame(self, bg=C_SURFACE, padx=40, pady=30)
        body.pack(fill="both", expand=True)

        left_col = tk.Frame(body, bg=C_SURFACE)
        left_col.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_col, text="THÔNG TIN TÀI KHOẢN", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 20))

        def info_row(parent, icon, label, value):
            row = tk.Frame(parent, bg=C_SURFACE, pady=10)
            row.pack(fill="x")
            tk.Label(row, text=icon, bg=C_SURFACE, font=("Segoe UI", 14), width=3).pack(side="left")
            tk.Label(row, text=f"{label}:", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 10), width=15, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=C_SURFACE, fg="#1e293b", font=("Segoe UI", 10, "bold")).pack(side="left")

        info_row(left_col, "📧", "Email", self.user.email)
        info_row(left_col, "📱", "Số điện thoại", self.user.phone)
        info_row(left_col, "🔒", "Trạng thái", self.user.status)

        # Password Section (Right Column)
        tk.Frame(body, bg=C_BORDER, width=1).pack(side="left", fill="y", padx=40)
        
        right_col = tk.Frame(body, bg=C_SURFACE)
        right_col.pack(side="left", fill="both", expand=True)
        
        tk.Label(right_col, text="BẢO MẬT & ĐỔI MẬT KHẨU", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 20))

        self._old_pw = tk.StringVar(); self._new_pw = tk.StringVar(); self._conf_pw = tk.StringVar()
        
        labeled_entry(right_col, "Mật khẩu hiện tại", self._old_pw, icon="🔒", show="*", width=35)
        labeled_entry(right_col, "Mật khẩu mới", self._new_pw, icon="🔑", show="*", width=35)
        pw_strength_bar(right_col, self._new_pw, bg=C_SURFACE).pack(fill="x", pady=(2, 10))
        labeled_entry(right_col, "Xác nhận mật khẩu", self._conf_pw, icon="✅", show="*", width=35)

        btns = tk.Frame(right_col, bg=C_SURFACE, pady=20)
        btns.pack(fill="x")
        btn(btns, "Cập nhật mật khẩu", self._change_pw, variant="primary", icon="💾").pack(side="left")
        self.close_btn = btn(btns, "Quay lại", None, variant="ghost") # For dialog usage
        
    def _change_pw(self) -> None:
        old, new, conf = self._old_pw.get().strip(), self._new_pw.get().strip(), self._conf_pw.get().strip()
        if not old or not new or not conf:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường mật khẩu.")
            return
        if new != conf:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        if len(new) < 6:
            messagebox.showwarning("Quá ngắn", "Mật khẩu mới phải có ít nhất 6 ký tự.")
            return

        try:
            self.auth_ctrl.change_password(username=self.user.username, old_password=old, new_password=new)
            messagebox.showinfo("Thành công", "Mật khẩu đã được đổi thành công!")
            self._old_pw.set(""); self._new_pw.set(""); self._conf_pw.set("")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
