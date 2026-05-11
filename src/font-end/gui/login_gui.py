# login_gui.py  –  split-panel login screen  (login + register + forgot-pw)
from __future__ import annotations
import random as _rnd
import tkinter as tk
from tkinter import ttk
from typing import Any
from gui.theme import (C_DARK, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_TEXT, C_MUTED, C_BG, F_INPUT, F_TITLE, F_SECTION, F_BODY, F_BODY_B,
                       btn, make_card, confirm_dialog, toast)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS  –  Indigo / Violet palette
# ══════════════════════════════════════════════════════════════════════════════
_I950 = "#1e1b4b"
_I900 = "#312e81"
_I800 = "#3730a3"
_I700 = "#4338ca"
_I600 = "#4f46e5"   # primary accent
_I500 = "#6366f1"
_I400 = "#818cf8"
_I200 = "#c7d2fe"
_I100 = "#e0e7ff"
_I50  = "#eef2ff"

_WHITE  = "#ffffff"
_SL900  = "#0f172a"
_SL700  = "#334155"
_SL500  = "#64748b"
_SL400  = "#94a3b8"
_SL200  = "#e2e8f0"
_SL100  = "#f1f5f9"

_GREEN  = "#16a34a"
_RED_BG = "#fef2f2"
_RED_BD = "#fecaca"
_RED_TX = "#b91c1c"

_FONT_H1    = ("Segoe UI", 22, "bold")
_FONT_H2    = ("Segoe UI", 17, "bold")
_FONT_BODY  = ("Segoe UI", 10)
_FONT_SM    = ("Segoe UI", 9)


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _section_label(parent: tk.Misc, text: str) -> tk.Label:
    lbl = tk.Label(parent, text=text, bg=C_SURFACE, fg=_SL400,
                   font=("Segoe UI", 8, "bold"))
    lbl.pack(anchor="w", pady=(14, 0))
    return lbl


def _labeled_entry(parent: tk.Misc, label: str, var: tk.StringVar,
                   show: str = "", width: int = 32,
                   icon: str = "") -> tuple[tk.Frame, tk.Entry]:
    if label:
        _section_label(parent, label)

    # Double-border for depth effect
    outer = tk.Frame(parent, bg=_SL200, padx=1, pady=1,
                     highlightthickness=1, highlightbackground=_SL200)
    outer.pack(fill="x", pady=(4, 0))

    inner = tk.Frame(outer, bg=C_SURFACE)
    inner.pack(fill="both", expand=True)

    if icon:
        ic_frame = tk.Frame(inner, bg="#f8fafc", width=36)
        ic_frame.pack(side="left", fill="y")
        ic_frame.pack_propagate(False)
        tk.Label(ic_frame, text=icon, bg="#f8fafc",
                 font=("Segoe UI", 12), fg=_I500).pack(
                     expand=True, fill="both", padx=4, pady=6)

    entry = tk.Entry(inner, textvariable=var, width=width, show=show,
                     font=("Segoe UI", 11), relief="flat",
                     bg=C_SURFACE, fg=_SL900, insertbackground=_I600)
    entry.pack(side="left",
               padx=(8 if icon else 14, 14),
               pady=11, fill="x", expand=True)

    def _focus_in(_: object) -> None:
        outer.config(bg=_I600, highlightbackground=_I500)
        inner.config(bg="#fafaff")
        entry.config(bg="#fafaff")

    def _focus_out(_: object) -> None:
        outer.config(bg=_SL200, highlightbackground=_SL200)
        inner.config(bg=C_SURFACE)
        entry.config(bg=C_SURFACE)

    entry.bind("<FocusIn>",  _focus_in)
    entry.bind("<FocusOut>", _focus_out)
    return outer, entry


def _separator(parent: tk.Misc, color: str = _SL200) -> None:
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=16)


def _pill_label(parent: tk.Misc, text: str,
                bg: str = _I50, fg: str = _I600) -> tk.Label:
    return tk.Label(parent, text=text, bg=bg, fg=fg,
                    font=("Segoe UI", 8, "bold"), padx=10, pady=3)


# ══════════════════════════════════════════════════════════════════════════════
# REGISTER DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class RegisterDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, auth_controller: Any) -> None:
        super().__init__(master)
        self.auth_ctrl = auth_controller
        self.title("Đăng ký tài khoản")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)  # type: ignore[arg-type]
        self.grab_set()
        self._vars = {k: tk.StringVar() for k in
                      ("full_name", "username", "email", "phone",
                       "password", "confirm", "role")}
        self._vars["role"].set("Sinh viên")
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # header
        hdr = tk.Frame(self, bg=_I600, padx=28, pady=18)
        hdr.pack(fill="x")
        _pill_label(hdr, "  ✦  TÀI KHOẢN MỚI  ", bg=_I800, fg=_I200).pack(anchor="w", pady=(0, 8))
        tk.Label(hdr, text="Đăng ký tài khoản",
                 bg=_I600, fg=_WHITE, font=_FONT_H2).pack(anchor="w")
        tk.Label(hdr, text="Tạo tài khoản để bắt đầu đặt phòng học",
                 bg=_I600, fg=_I200, font=_FONT_SM).pack(anchor="w", pady=(3, 0))

        # body
        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=24)
        body.pack(fill="both", expand=True)

        outer, card = make_card(body, padx=20, pady=20)
        outer.pack(fill="both", expand=True)

        grid = tk.Frame(card, bg=C_SURFACE)
        grid.pack(fill="x")

        left  = tk.Frame(grid, bg=C_SURFACE)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(grid, bg=C_SURFACE)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        _labeled_entry(left,  "HỌ VÀ TÊN *",          self._vars["full_name"], icon="👤")
        _labeled_entry(right, "TÊN ĐĂNG NHẬP *",       self._vars["username"],  icon="🆔")
        _labeled_entry(left,  "EMAIL *",                self._vars["email"],     icon="📧")
        _labeled_entry(right, "SỐ ĐIỆN THOẠI",         self._vars["phone"],     icon="📞")
        _labeled_entry(left,  "MẬT KHẨU *",            self._vars["password"],  icon="🔒", show="*")
        _labeled_entry(right, "XÁC NHẬN MẬT KHẨU *",  self._vars["confirm"],   icon="🛡️", show="*")

        # role
        _section_label(card, "VAI TRÒ")
        role_wrap = tk.Frame(card, bg=_SL200, padx=1, pady=1)
        role_wrap.pack(fill="x", pady=(4, 0))
        role_inner = tk.Frame(role_wrap, bg=C_SURFACE)
        role_inner.pack(fill="both", expand=True)
        tk.Label(role_inner, text="🎓", bg=C_SURFACE,
                 font=("Segoe UI", 11)).pack(side="left", padx=(10, 2), pady=8)
        ttk.Combobox(role_inner, textvariable=self._vars["role"],
                     values=["Sinh viên", "Giảng viên"],
                     state="readonly", font=("Segoe UI", 10)).pack(
            side="left", fill="x", expand=True, padx=(4, 10), pady=8)

        # notice
        notice = tk.Frame(card, bg=_I50, padx=14, pady=10,
                          highlightthickness=1, highlightbackground=_I200)
        notice.pack(fill="x", pady=(18, 0))
        tk.Label(notice, text="ⓘ  Tài khoản 'Admin' chỉ được tạo bởi quản trị viên hệ thống.",
                 bg=_I50, fg=_I700, font=_FONT_SM).pack(anchor="w")

        _separator(card)

        btn_row = tk.Frame(card, bg=C_SURFACE)
        btn_row.pack(fill="x")
        btn(btn_row, "Tạo tài khoản →", self._submit, icon="🚀").pack(side="right")
        btn(btn_row, "Hủy bỏ", self.destroy, variant="ghost").pack(side="right", padx=10)

    def _submit(self) -> None:
        v = {k: var.get().strip() for k, var in self._vars.items()}
        if v["password"] != v["confirm"]:
            confirm_dialog(self, "Lỗi xác nhận",
                           "Mật khẩu xác nhận không khớp.", kind="danger", cancel_text=None)
            return

        # Map Vietnamese roles to backend values (unaccented)
        role_map = {"Sinh viên": "Sinh vien", "Giảng viên": "Giang vien"}
        role_backend = role_map.get(v["role"], "Sinh vien")

        try:
            self.auth_ctrl.register(
                full_name=v["full_name"], username=v["username"],
                email=v["email"],        phone=v["phone"],
                password=v["password"],  role=role_backend,
            )
        except ValueError as exc:
            confirm_dialog(self, "Đăng ký thất bại", str(exc), kind="danger", cancel_text=None)
            return
        confirm_dialog(self, "Đăng ký thành công",
                       f"Tài khoản '{v['username']}' đã được tạo!\nBạn có thể đăng nhập ngay bây giờ.",
                       kind="primary", cancel_text=None)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# FORGOT PASSWORD DIALOG  (2-step)
# ══════════════════════════════════════════════════════════════════════════════

class ForgotPasswordDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, auth_controller: Any) -> None:
        super().__init__(master)
        self.auth_ctrl = auth_controller
        self.title("Khôi phục mật khẩu")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)  # type: ignore[arg-type]
        self.grab_set()
        self._verified_user: Any = None
        self._vars = {k: tk.StringVar() for k in
                      ("username", "email", "new_pw", "confirm_pw")}
        self._build_step1()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _clear(self) -> None:
        for w in self.winfo_children():
            w.destroy()

    # ── step 1 ────────────────────────────────────────────────────────────────

    def _build_step1(self) -> None:
        self._clear()

        hdr = tk.Frame(self, bg=_I600, padx=28, pady=18)
        hdr.pack(fill="x")
        _pill_label(hdr, "  BƯỚC 1 / 2  ", bg=_I800, fg=_I200).pack(anchor="w", pady=(0, 8))
        tk.Label(hdr, text="🔑  Xác minh danh tính",
                 bg=_I600, fg=_WHITE, font=_FONT_H2).pack(anchor="w")
        tk.Label(hdr, text="Nhập thông tin để đặt lại mật khẩu",
                 bg=_I600, fg=_I200, font=_FONT_SM).pack(anchor="w", pady=(3, 0))

        dot_row = tk.Frame(hdr, bg=_I600)
        dot_row.pack(anchor="w", pady=(12, 0))
        for active in [True, False]:
            tk.Frame(dot_row, bg=_I100 if active else _I800,
                     width=22 if active else 8, height=8).pack(side="left", padx=(0, 4))

        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=24)
        body.pack(fill="both")

        outer, card = make_card(body, padx=20, pady=20)
        outer.pack(fill="both")

        tk.Label(card,
                 text="Nhập tên đăng nhập và email đã đăng ký để xác minh tài khoản của bạn.",
                 bg=C_SURFACE, fg=_SL500, font=_FONT_BODY,
                 wraplength=330, justify="left").pack(anchor="w", pady=(0, 4))

        _labeled_entry(card, "TÊN ĐĂNG NHẬP",    self._vars["username"], icon="🆔")
        _labeled_entry(card, "EMAIL ĐÃ ĐĂNG KÝ", self._vars["email"],    icon="📧")

        _separator(card)

        btn_row = tk.Frame(card, bg=C_SURFACE)
        btn_row.pack(fill="x")
        btn(btn_row, "Tiếp tục →", self._next_step).pack(side="right")
        btn(btn_row, "Quay lại", self.destroy, variant="ghost").pack(side="right", padx=10)

    def _next_step(self) -> None:
        username = self._vars["username"].get().strip()
        email    = self._vars["email"].get().strip()
        if not username or not email:
            confirm_dialog(self, "Thiếu thông tin",
                           "Vui lòng nhập đầy đủ thông tin.", kind="warning", cancel_text=None)
            return
        user = self.auth_ctrl.find_account_for_reset(username, email)
        if user is None:
            confirm_dialog(self, "Xác minh thất bại",
                           "Không tìm thấy tài khoản với thông tin này.",
                           kind="danger", cancel_text=None)
            return
        self._verified_user = user
        self._build_step2()

    # ── step 2 ────────────────────────────────────────────────────────────────

    def _build_step2(self) -> None:
        self._clear()

        hdr = tk.Frame(self, bg=_GREEN, padx=28, pady=18)
        hdr.pack(fill="x")
        _pill_label(hdr, "  BƯỚC 2 / 2  ", bg="#15803d", fg="#bbf7d0").pack(anchor="w", pady=(0, 8))
        tk.Label(hdr, text="✅  Xác minh thành công",
                 bg=_GREEN, fg=_WHITE, font=_FONT_H2).pack(anchor="w")
        tk.Label(hdr, text="Hãy chọn mật khẩu mới cho tài khoản",
                 bg=_GREEN, fg="#bbf7d0", font=_FONT_SM).pack(anchor="w", pady=(3, 0))

        dot_row = tk.Frame(hdr, bg=_GREEN)
        dot_row.pack(anchor="w", pady=(12, 0))
        for active in [False, True]:
            tk.Frame(dot_row, bg="#bbf7d0" if active else "#15803d",
                     width=22 if active else 8, height=8).pack(side="left", padx=(0, 4))

        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=24)
        body.pack(fill="both")

        outer, card = make_card(body, padx=20, pady=20)
        outer.pack(fill="both")

        name = getattr(self._verified_user, "full_name", "Người dùng")
        tk.Label(card, text=f"Xin chào {name}, hãy đặt mật khẩu mới bên dưới.",
                 bg=C_SURFACE, fg=_SL700, font=_FONT_BODY,
                 wraplength=330, justify="left").pack(anchor="w", pady=(0, 4))

        _labeled_entry(card, "MẬT KHẨU MỚI",      self._vars["new_pw"],     icon="🔒", show="*")
        _labeled_entry(card, "XÁC NHẬN MẬT KHẨU", self._vars["confirm_pw"], icon="🛡️", show="*")

        _separator(card)

        btn_row = tk.Frame(card, bg=C_SURFACE)
        btn_row.pack(fill="x")
        btn(btn_row, "Cập nhật mật khẩu 💾", self._save_password).pack(side="right")
        btn(btn_row, "Hủy bỏ", self.destroy, variant="ghost").pack(side="right", padx=10)

    def _save_password(self) -> None:
        new_pw     = self._vars["new_pw"].get().strip()
        confirm_pw = self._vars["confirm_pw"].get().strip()
        if new_pw != confirm_pw:
            confirm_dialog(self, "Lỗi xác nhận",
                           "Mật khẩu xác nhận không khớp.", kind="danger", cancel_text=None)
            return
        try:
            self.auth_ctrl.reset_password(
                username=self._verified_user.username,
                email=self._verified_user.email,
                new_password=new_pw,
            )
        except ValueError as exc:
            confirm_dialog(self, "Lỗi", str(exc), kind="danger", cancel_text=None)
            return
        confirm_dialog(self, "Thành công",
                       "Mật khẩu đã được đổi thành công!\nVui lòng đăng nhập lại.",
                       kind="primary", cancel_text=None)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOGIN FRAME
# ══════════════════════════════════════════════════════════════════════════════

class LoginFrame(tk.Frame):
    def __init__(self, master: tk.Misc, on_login: Any,
                 auth_controller: Any = None) -> None:
        super().__init__(master, bg=_I950)
        self.on_login  = on_login
        self.auth_ctrl = auth_controller
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._build_left_panel()
        self._build_right_panel()

    # ── Left: animated branding panel ────────────────────────────────────────

    def _build_left_panel(self) -> None:
        left = tk.Frame(self, bg=_I950)
        left.grid(row=0, column=0, sticky="nsew")

        cv = tk.Canvas(left, bg=_I950, highlightthickness=0)
        cv.pack(fill="both", expand=True)

        _particles: list[dict[str, Any]] = []
        _stars: list[dict[str, Any]] = []
        _anim_ref: list[Any] = [None]
        _frame_ct: list[int] = [0]
        _ORB_COLORS = ["#312e81", "#3730a3", "#4338ca", "#4c1d95",
                        "#2e1065", "#3b0764", "#581c87", "#1e1b4b"]

        def _init_particles(w: int, h: int) -> None:
            _particles.clear()
            _stars.clear()
            # Large floating orbs
            for _ in range(14):
                _particles.append({
                    "x": _rnd.uniform(0, w), "y": _rnd.uniform(0, h),
                    "r": _rnd.uniform(w * 0.06, w * 0.22),
                    "dy": _rnd.uniform(0.12, 0.45),
                    "dx": _rnd.uniform(-0.18, 0.18),
                    "col": _rnd.choice(_ORB_COLORS),
                    "alpha": _rnd.uniform(0.3, 0.8),
                })
            # Small twinkling stars
            for _ in range(30):
                _stars.append({
                    "x": _rnd.uniform(0, w), "y": _rnd.uniform(0, h),
                    "r": _rnd.uniform(1, 3),
                    "phase": _rnd.uniform(0, 6.28),
                    "speed": _rnd.uniform(0.03, 0.08),
                })

        def _animate() -> None:
            if not cv.winfo_exists():
                return
            w, h = cv.winfo_width(), cv.winfo_height()
            if w < 20:
                _anim_ref[0] = cv.after(120, _animate)
                return
            if not _particles:
                _init_particles(w, h)
            _frame_ct[0] += 1
            cv.delete("all")

            # Gradient background layers
            steps = 6
            for i in range(steps):
                y0 = i * h // steps
                y1 = (i + 1) * h // steps
                r = 0x0f + i * (0x1e - 0x0f) // steps
                g = 0x17 + i * (0x1b - 0x17) // steps
                b = 0x2a + i * (0x4b - 0x2a) // steps
                cv.create_rectangle(0, y0, w, y1,
                                    fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

            # Mesh grid (subtle)
            for gx in range(0, w, 60):
                cv.create_line(gx, 0, gx, h, fill="#1e1b4b", width=1)
            for gy in range(0, h, 60):
                cv.create_line(0, gy, w, gy, fill="#1e1b4b", width=1)

            # Floating orbs
            for p in _particles:
                p["y"] -= p["dy"]
                p["x"] += p["dx"]
                if p["y"] + p["r"] < 0:
                    p["y"] = h + p["r"]
                    p["x"] = _rnd.uniform(0, w)
                if p["x"] < -p["r"]:
                    p["x"] = w + p["r"]
                elif p["x"] > w + p["r"]:
                    p["x"] = -p["r"]
                r = p["r"]
                cv.create_oval(p["x"] - r, p["y"] - r,
                               p["x"] + r, p["y"] + r,
                               fill=p["col"], outline="")

            # Twinkling stars
            import math
            for s in _stars:
                s["phase"] += s["speed"]
                brightness = 0.4 + 0.6 * abs(math.sin(s["phase"]))
                gray = int(100 + 155 * brightness)
                col = f"#{gray:02x}{gray:02x}{max(gray, 200):02x}"
                sr = s["r"]
                cv.create_oval(s["x"] - sr, s["y"] - sr,
                               s["x"] + sr, s["y"] + sr,
                               fill=col, outline="")

            cx = w // 2

            # Glow ring behind icon
            for gi in range(3, 0, -1):
                gr = 56 + gi * 14
                alpha_hex = ["#1e1b4b", "#252270", "#2d2a80"][gi - 1]
                cv.create_oval(cx - gr, h * .24 - gr, cx + gr, h * .24 + gr,
                               fill="", outline=alpha_hex, width=2)

            # Central icon circle with glow
            cv.create_oval(cx - 52, h * .24 - 52, cx + 52, h * .24 + 52,
                           fill="#1e2a5e", outline=_I500, width=2)
            cv.create_text(cx, h * .24, text="🏫",
                           font=("Segoe UI", 42), fill=_WHITE, anchor="center")

            # Branding text
            cv.create_text(cx, h * .38, text="HỆ THỐNG",
                           font=("Segoe UI", 22, "bold"), fill=_WHITE)
            cv.create_text(cx, h * .44, text="QUẢN LÝ ĐẶT PHÒNG HỌC",
                           font=("Segoe UI", 11, "bold"), fill=_I400)

            # Accent line with glow
            cv.create_line(cx - 80, h * .50, cx + 80, h * .50,
                           fill=_I500, width=2)
            cv.create_line(cx - 40, h * .50, cx + 40, h * .50,
                           fill=_I400, width=1)

            # Feature list with dots
            feats = [
                ("⚡", "Đặt phòng trực tuyến tức thì"),
                ("📅", "Quản lý lịch biểu thông minh"),
                ("📊", "Báo cáo & thống kê chi tiết"),
                ("🔔", "Thông báo realtime"),
            ]
            for i, (ico, feat) in enumerate(feats):
                fy = h * .56 + i * h * .058
                cv.create_text(cx - 90, fy, text=ico,
                               font=("Segoe UI", 10), fill=_I400, anchor="w")
                cv.create_text(cx - 68, fy, text=feat,
                               font=("Segoe UI", 9), fill="#94a3b8", anchor="w")

            # Stats bar at bottom
            stats_y = h * .82
            cv.create_rectangle(cx - 120, stats_y - 20, cx + 120, stats_y + 28,
                                fill="#1e1b4b", outline=_I800, width=1)
            stats = [("500+", "Phòng học"), ("10K+", "Lượt đặt"), ("99%", "Uptime")]
            for si, (val, lbl) in enumerate(stats):
                sx = cx - 80 + si * 80
                cv.create_text(sx, stats_y - 4, text=val,
                               font=("Segoe UI", 11, "bold"), fill=_I400)
                cv.create_text(sx, stats_y + 12, text=lbl,
                               font=("Segoe UI", 7), fill="#64748b")

            cv.create_text(cx, h * .94, text="v3.0 Titanium  ·  Nhóm 24",
                           font=("Segoe UI", 8, "bold"), fill=_I700)

            _anim_ref[0] = cv.after(33, _animate)

        def _on_configure(_e: Any = None) -> None:
            if _anim_ref[0] is None:
                _animate()

        def _on_destroy(_e: Any = None) -> None:
            if _anim_ref[0]:
                try:
                    cv.after_cancel(_anim_ref[0])
                except Exception:
                    pass
                _anim_ref[0] = None

        cv.bind("<Configure>", _on_configure)
        cv.bind("<Destroy>",   _on_destroy)

    # ── Right: login form ─────────────────────────────────────────────────────

    def _build_right_panel(self) -> None:
        right = tk.Frame(self, bg=_WHITE)
        right.grid(row=0, column=1, sticky="nsew")

        # top accent stripe — gradient simulation
        stripe = tk.Frame(right, height=5, bg=_I600)
        stripe.pack(fill="x")
        tk.Frame(stripe, height=2, bg=_I500).pack(fill="x", side="top")

        # decorative background canvas with multiple layers
        decor = tk.Canvas(right, bg=_WHITE, highlightthickness=0)
        decor.place(relx=0, rely=0, relwidth=1, relheight=1)

        def _draw_decor(_e: Any = None) -> None:
            if not decor.winfo_exists():
                return
            decor.delete("all")
            W, H = decor.winfo_width(), decor.winfo_height()
            # Layered decorative circles
            decor.create_oval(W * .55, -120, W * 1.2, H * .4,
                              fill=_I50, outline="")
            decor.create_oval(W * .7, -60, W * 1.05, H * .25,
                              fill="#f5f3ff", outline="")
            decor.create_oval(-80, H * .65, W * .25, H + 80,
                              fill="#f0f9ff", outline="")
            decor.create_oval(-40, H * .75, W * .15, H + 40,
                              fill="#eff6ff", outline="")
            # Subtle dot pattern
            for dx in range(0, W, 40):
                for dy in range(0, H, 40):
                    decor.create_oval(dx, dy, dx + 2, dy + 2,
                                      fill="#f1f5f9", outline="")

        decor.bind("<Configure>", _draw_decor)

        # centred login card
        container = tk.Frame(right, bg=_WHITE)
        container.place(relx=0.5, rely=0.5, anchor="center")
        self._login_container = container

        outer, card = make_card(container, padx=44, pady=40)
        outer.pack()

        # Gradient accent bar on card top
        accent_bar = tk.Frame(card, bg=C_SURFACE)
        accent_bar.pack(fill="x", pady=(0, 8))
        for c_bar in [_I600, _I500, _I400, _I200]:
            tk.Frame(accent_bar, bg=c_bar, height=3, width=60).pack(
                side="left", expand=True, fill="x")

        # welcome header with time-based greeting
        import datetime as _dt
        hour = _dt.datetime.now().hour
        if hour < 12:
            greet = "Chào buổi sáng! ☀️"
        elif hour < 18:
            greet = "Chào buổi chiều! 🌤️"
        else:
            greet = "Chào buổi tối! 🌙"

        eyebrow_frame = tk.Frame(card, bg=C_SURFACE)
        eyebrow_frame.pack(anchor="w", pady=(0, 6))
        _pill_label(eyebrow_frame, "  ✦  TITANIUM ELITE  ",
                    bg=_I50, fg=_I600).pack(side="left")
        tk.Label(eyebrow_frame, text="v3.0", bg=C_SURFACE, fg=_SL400,
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=6)

        tk.Label(card, text=greet,
                 bg=C_SURFACE, fg=_SL900,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(card, text="Đăng nhập để truy cập hệ thống quản lý",
                 bg=C_SURFACE, fg=_SL400,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        _separator(card)

        # username
        _labeled_entry(card, "TÊN ĐĂNG NHẬP", self.username_var, icon="👤")

        # password label row (with forgot link)
        pw_hdr = tk.Frame(card, bg=C_SURFACE)
        pw_hdr.pack(fill="x", pady=(16, 0))
        tk.Label(pw_hdr, text="MẬT KHẨU", bg=C_SURFACE, fg=_SL400,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        forgot = tk.Label(pw_hdr, text="Quên mật khẩu?",
                          bg=C_SURFACE, fg=_I600,
                          font=("Segoe UI", 9, "underline"), cursor="hand2")
        forgot.pack(side="right")
        forgot.bind("<Enter>", lambda *_: forgot.config(fg=_I700))
        forgot.bind("<Leave>", lambda *_: forgot.config(fg=_I600))
        forgot.bind("<Button-1>", lambda *_: self._open_forgot())

        p_outer, self._pw_entry = _labeled_entry(
            card, "", self.password_var, show="*", icon="🔒")
        p_outer.pack_forget()
        p_outer.pack(fill="x", pady=(4, 0))

        # Eye toggle for password visibility
        _shown = [False]
        eye_lbl = tk.Label(p_outer.winfo_children()[0], text="👁",
                           bg=C_SURFACE, fg=_SL400,
                           font=("Segoe UI", 10), cursor="hand2")
        eye_lbl.pack(side="right", padx=(0, 8))

        def _toggle_pw(*_: Any) -> None:
            _shown[0] = not _shown[0]
            self._pw_entry.config(show="" if _shown[0] else "*")
            eye_lbl.config(fg=_I600 if _shown[0] else _SL400)

        eye_lbl.bind("<Button-1>", _toggle_pw)

        # Remember me checkbox
        remember_f = tk.Frame(card, bg=C_SURFACE)
        remember_f.pack(fill="x", pady=(10, 0))
        self._remember_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(remember_f, text="Ghi nhớ đăng nhập",
                            variable=self._remember_var,
                            bg=C_SURFACE, fg=_SL500,
                            activebackground=C_SURFACE,
                            font=("Segoe UI", 9),
                            selectcolor=C_SURFACE)
        cb.pack(side="left")

        # error message box (hidden by default)
        self._err_frame = tk.Frame(card, bg=_RED_BG,
                                    highlightthickness=1,
                                    highlightbackground=_RED_BD)
        self._err_lbl = tk.Label(self._err_frame, text="",
                                  bg=_RED_BG, fg=_RED_TX,
                                  font=("Segoe UI", 9), wraplength=290,
                                  justify="left", padx=12, pady=8)
        self._err_lbl.pack(fill="x")
        # not packed yet – shown on demand

        # login button — larger, bolder
        self._login_btn = tk.Button(
            card, text="  ĐĂNG NHẬP  →",
            font=("Segoe UI", 12, "bold"),
            bg=_I600, fg=_WHITE,
            activebackground=_I700, activeforeground=_WHITE,
            relief="flat", bd=0, cursor="hand2",
            pady=13, command=self._submit,
        )
        self._login_btn.pack(fill="x", pady=(16, 0))
        self._login_btn.bind("<Enter>",
                             lambda *_: self._login_btn.config(bg=_I700))
        self._login_btn.bind("<Leave>",
                             lambda *_: self._login_btn.config(bg=_I600))

        # Divider with "hoặc"
        or_row = tk.Frame(card, bg=C_SURFACE)
        or_row.pack(fill="x", pady=(16, 0))
        tk.Frame(or_row, bg=_SL200, height=1).pack(
            side="left", fill="x", expand=True, pady=8)
        tk.Label(or_row, text="  hoặc  ", bg=C_SURFACE, fg=_SL400,
                 font=("Segoe UI", 8)).pack(side="left")
        tk.Frame(or_row, bg=_SL200, height=1).pack(
            side="left", fill="x", expand=True, pady=8)

        # Register link
        reg_row = tk.Frame(card, bg=C_SURFACE)
        reg_row.pack(pady=(10, 0))
        tk.Label(reg_row, text="Chưa có tài khoản? ",
                 bg=C_SURFACE, fg=_SL500, font=_FONT_BODY).pack(side="left")
        reg_lbl = tk.Label(reg_row, text="Đăng ký ngay →",
                           bg=C_SURFACE, fg=_I600,
                           font=("Segoe UI", 10, "bold", "underline"),
                           cursor="hand2")
        reg_lbl.pack(side="left")
        reg_lbl.bind("<Enter>", lambda *_: reg_lbl.config(fg=_I700))
        reg_lbl.bind("<Leave>", lambda *_: reg_lbl.config(fg=_I600))
        reg_lbl.bind("<Button-1>", lambda *_: self._open_register())

        # Footer
        footer = tk.Frame(card, bg=C_SURFACE)
        footer.pack(fill="x", pady=(14, 0))
        tk.Label(footer, text="© 2026 Nhóm 24  ·  Titanium Elite Platform",
                 bg=C_SURFACE, fg=_SL400,
                 font=("Segoe UI", 7)).pack()

        # Change global binding to local to avoid side effects
        def _on_return(event):
            if self.winfo_exists():
                self._submit()

        self.bind_all("<Return>", _on_return)
        self.bind("<Destroy>", lambda *_: self.unbind_all("<Return>"))

    # ── Actions ───────────────────────────────────────────────────────────────

    def _open_register(self) -> None:
        if self.auth_ctrl is None:
            confirm_dialog(self, "Thông báo",
                           "Chức năng đăng ký chưa được kết nối.",
                           kind="primary", cancel_text=None)
            return
        RegisterDialog(self, self.auth_ctrl)

    def _open_forgot(self) -> None:
        if self.auth_ctrl is None:
            confirm_dialog(self, "Thông báo",
                           "Chức năng lấy lại mật khẩu chưa được kết nối.",
                           kind="primary", cancel_text=None)
            return
        ForgotPasswordDialog(self, self.auth_ctrl)

    def _shake(self) -> None:
        if not (hasattr(self, "_login_container") and
                self._login_container.winfo_exists()):
            return
        card = self._login_container
        offsets = [12, -12, 9, -9, 6, -6, 3, -3, 0]
        delay = 0
        for ox in offsets:
            self.after(delay, lambda o=ox, c=card: (
                c.winfo_exists() and
                c.place(relx=0.5, rely=0.5, anchor="center", x=o)
            ))
            delay += 42

    def _set_error(self, msg: str) -> None:
        if not (hasattr(self, "_err_lbl") and self._err_lbl.winfo_exists()):
            return
        if msg:
            self._err_lbl.config(text=f"⚠  {msg}")
            self._err_frame.pack(fill="x", pady=(14, 0))
            self._shake()
        else:
            self._err_frame.pack_forget()

    def _submit(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self._set_error("Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        self._set_error("")
        success = False

        if hasattr(self, "_login_btn") and self._login_btn.winfo_exists():
            self._login_btn.config(text="  Đang kiểm tra...  ",
                                    state="disabled", bg=_I500)
            self.update_idletasks()

        try:
            self.on_login(username, password)
            success = True
        except PermissionError as exc:
            try:
                if self._login_btn.winfo_exists():
                    self._login_btn.config(text="  ĐĂNG NHẬP  →",
                                            state="normal", bg=_I600)
                self._set_error(str(exc))
            except Exception:
                pass
        except Exception as exc:
            try:
                if self._login_btn.winfo_exists():
                    self._login_btn.config(text="  ĐĂNG NHẬP  →",
                                            state="normal", bg=_I600)
                self._set_error(str(exc))
            except Exception:
                pass
        finally:
            try:
                if (not success and
                        self._login_btn.winfo_exists() and
                        str(self._login_btn["state"]) == "disabled"):
                    self._login_btn.config(text="  ĐĂNG NHẬP  →",
                                            state="normal", bg=_I600)
                    self._set_error("Sai tên đăng nhập hoặc mật khẩu.")
            except Exception:
                pass