# profile_gui.py  –  user profile dialog with password change  (v2.1)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from gui.theme import (C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED, btn,
                       labeled_entry, pw_strength_bar, eye_toggle, status_badge)


class ProfileDialog(tk.Toplevel):
    """Shows current user profile and allows password change."""

    def __init__(self, master, current_user, auth_controller) -> None: # type: ignore
        super().__init__(master) # type: ignore
        self.user      = current_user
        self.auth_ctrl = auth_controller
        self.title("Thong tin ca nhan")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master) # type: ignore
        self.grab_set()
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # Role color
        role_colors = {
            "Admin":      ("#4f46e5", "#eef2ff"),   # Indigo 600
            "Giang vien": ("#15803d", "#dcfce7"),
            "Sinh vien":  ("#854d0e", "#fef9c3"),
        }
        fg, bg = role_colors.get(self.user.role, ("#475569", "#f1f5f9")) # type: ignore

        # Header with avatar
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=24, pady=18)
        hdr.pack(fill="x")

        av = tk.Canvas(hdr, width=60, height=60, bg=C_PRIMARY,
                       highlightthickness=0)
        av.pack(side="left", padx=(0, 14))
        av.create_oval(2, 2, 58, 58, fill="#4f46e5", outline="#c7d2fe", width=2)
        initials = "".join(p[0] for p in self.user.full_name.split()[:2]).upper() # type: ignore
        av.create_text(30, 30, text=initials, fill="white",
                       font=("Segoe UI", 20, "bold"))

        info = tk.Frame(hdr, bg=C_PRIMARY)
        info.pack(side="left", fill="x")
        tk.Label(info, text=self.user.full_name, bg=C_PRIMARY, fg="white", # type: ignore
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(info, text=f"@{self.user.username}", bg=C_PRIMARY, fg="#c7d2fe", # type: ignore
                 font=("Segoe UI", 10)).pack(anchor="w")
        badge = status_badge(info, self.user.role, bg=C_PRIMARY) # type: ignore
        badge.config(bg=bg, fg=fg)
        badge.pack(anchor="w", pady=(4, 0))

        # Profile info
        body = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        body.pack(fill="x")

        def info_row(icon, label, value): # type: ignore
            row = tk.Frame(body, bg=C_SURFACE)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=icon, bg=C_SURFACE, # type: ignore
                     font=("Segoe UI", 13), width=2).pack(side="left")
            tk.Label(row, text=f"{label}:", bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9), width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=C_SURFACE, fg="#1e293b", # type: ignore
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        info_row("🔑", "Ma tai khoan", self.user.user_id) # type: ignore
        info_row("👤", "Ten dang nhap", self.user.username) # type: ignore
        info_row("📛", "Ho va ten",    self.user.full_name) # type: ignore
        info_row("📧", "Email",        self.user.email) # type: ignore
        info_row("📱", "So dien thoai", self.user.phone) # type: ignore
        info_row("🔒", "Trang thai",   self.user.status) # type: ignore

        # Divider
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x", padx=24)

        # Change password section
        pw_frame = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        pw_frame.pack(fill="x")

        tk.Label(pw_frame, text="🔐  Doi mat khau",
                 bg=C_SURFACE, fg="#1e1b4b",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 12))

        self._old_pw  = tk.StringVar()
        self._new_pw  = tk.StringVar()
        self._conf_pw = tk.StringVar()

        # Old password
        _, e_old = labeled_entry(pw_frame, "MAT KHAU HIEN TAI",
                                 self._old_pw, icon="🔒", show="*", width=30)
        eye_toggle(e_old.master, e_old, bg=C_SURFACE).pack(side="right", padx=(0, 8))

        # New password + strength bar
        _, e_new = labeled_entry(pw_frame, "MAT KHAU MOI (min 6 ky tu)",
                                 self._new_pw, icon="🔑", show="*", width=30)
        eye_toggle(e_new.master, e_new, bg=C_SURFACE).pack(side="right", padx=(0, 8))
        pw_strength_bar(pw_frame, self._new_pw, bg=C_SURFACE).pack(
            fill="x", pady=(2, 0))

        # Confirm password
        _, e_conf = labeled_entry(pw_frame, "XAC NHAN MAT KHAU MOI",
                                  self._conf_pw, icon="✅", show="*", width=30)
        eye_toggle(e_conf.master, e_conf, bg=C_SURFACE).pack(side="right", padx=(0, 8))

        # Buttons
        btn_row = tk.Frame(self, bg=C_SURFACE, padx=26)
        btn_row.pack(fill="x", pady=(4, 20))
        btn(btn_row, "  Doi mat khau  ", self._change_pw,
            variant="primary", icon="💾").pack(side="left")
        btn(btn_row, "Dong", self.destroy,
            variant="ghost").pack(side="left", padx=10)

    def _change_pw(self) -> None:
        old   = self._old_pw.get().strip()
        new   = self._new_pw.get().strip()
        conf  = self._conf_pw.get().strip()

        if not old or not new or not conf:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long dien day du mat khau.",
                                   parent=self)
            return
        if new != conf:
            messagebox.showerror("Loi",
                                 "Mat khau xac nhan khong khop.",
                                 parent=self)
            return
        if len(new) < 6:
            messagebox.showwarning("Qua ngan",
                                   "Mat khau moi phai co it nhat 6 ky tu.",
                                   parent=self)
            return

        # Apply change via controller (verifies old password, logs action)
        try:
            self.auth_ctrl.change_password( # type: ignore
                username=self.user.username,  # type: ignore
                old_password=old,
                new_password=new,
            )
        except ValueError as exc:
            messagebox.showerror("Loi", str(exc), parent=self)
            return

        messagebox.showinfo("Thanh cong",
                            "Mat khau da duoc doi thanh cong!",
                            parent=self)
        self._old_pw.set("")
        self._new_pw.set("")
        self._conf_pw.set("")
