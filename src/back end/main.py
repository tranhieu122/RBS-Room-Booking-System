#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
He Thong Quan Ly Phong Hoc - Nhom 24
Thanh vien: Tran Trung Hieu · Nguyen Huy Hai · Nguyen Tuan Minh
Entry point: khoi dong ung dung va day du toan bo module.
"""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# ── Load .env file (python-dotenv) ─────────────────────────────────────────
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_ENV_FILE, override=False)
except ImportError:
    pass   # python-dotenv not installed → fall back to os.environ / defaults

# Make `src/font-end` importable so `gui.*` modules can be loaded.
ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "font-end"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
from controllers.equipment_controller import EquipmentController
from controllers.notification_controller import NotificationController
from controllers.report_controller import ReportController
from controllers.room_controller import RoomController
from controllers.room_feedback_controller import RoomFeedbackController
from controllers.schedule_rule_controller import ScheduleRuleController
from controllers.user_controller import UserController

from gui.theme import (
    apply_theme, C_PRIMARY, C_DARK, C_MUTED, C_BG, C_BORDER,
    btn, confirm_dialog, page_header
)
from gui.profile_gui import ProfileDialog, ProfileFrame
from gui.booking_form_gui import BookingFormFrame
from gui.booking_list_gui import BookingListFrame
from gui.dashboard_gui import DashboardFrame
from gui.equipment_gui import EquipmentManagementFrame
from gui.login_gui import LoginFrame
from gui.notification_gui import NotificationFrame
from gui.report_gui import ReportFrame
from gui.room_feedback_gui import RoomIssueManagementFrame, RoomRatingManagementFrame
from gui.room_gui import RoomManagementFrame
from gui.schedule_gui import ScheduleFrame
from gui.recurring_schedule_gui import RecurringScheduleFrame
from gui.user_gui import UserManagementFrame

# ── Layout ───────────────────────────────────────────────────────────────────
SIDEBAR_W = 260
SIDEBAR_W_COLLAPSED = 72
TOPBAR_H  = 72

# ── Sidebar palette — Premium Snow White ───────────────────────────────────
SB_BG     = "#ffffff"    # Pure White
SB_HOVER  = "#f1f5f9"    # Slate 100
SB_ACTIVE = "#eff6ff"    # Blue 50
SB_ACCENT = "#4f46e5"    # Indigo 600
SB_TEXT   = "#475569"    # Slate 600
SB_TEXT_ACTIVE = "#4f46e5"
SB_MUTED  = "#94a3b8"
SB_SECT   = "#f8fafc"

# ── Top-bar palette — Clean Glass ───────────────────────────────────────────
TP_BG     = "#ffffff"
TP_BORDER = "#f1f5f9"
TP_TEXT   = "#0f172a"
TP_MUTED  = "#64748b"
C_BG      = "#f8fafc"    # Slate 50
C_SURFACE = "#ffffff"
C_BORDER  = "#e2e8f0"

# ── Role colours ─────────────────────────────────────────────────────────────
ROLE_CHIP = {
    "Admin":      ("#eef2ff", "#4f46e5"),   # Indigo chip
    "Giang vien": ("#dcfce7", "#15803d"),
    "Sinh vien":  ("#fef9c3", "#854d0e"),
}
ROLE_AVATAR = {
    "Admin":      "#4f46e5",   # Indigo 600
    "Giang vien": "#16a34a",
    "Sinh vien":  "#b45309",
}

# ── Nav: (label, key, icon).  key=="---" → section header ────────────────────
NAV_ALL = [
    ("Trang chủ",       "dashboard",           "🏠"),
    ("Đặt phòng",       "booking_form",        "📅"),
    ("Danh sách đặt",   "booking_list",        "📋"),
    ("Lịch biểu",       "schedule",            "📆"),
    ("Lịch dạy chu kỳ", "recurring_schedule",  "🔄"),
    ("Thông báo",       "notifications",       "📩"),
    ("QUẢN TRỊ",        "---",                 None),
    ("Quản lý phòng",   "rooms",               "🏫"),
    ("Người dùng",      "users",               "👥"),
    ("Thiết bị",        "equipment",           "🔧"),
    ("Báo cáo",         "report",              "📈"),
    ("Báo lỗi phòng",   "room_issues",         "⚠️"),
    ("Quản lý đánh giá", "room_ratings",        "⭐"),
]

NAV_GV_SV = [
    ("Trang chủ",       "dashboard",           "🏠"),
    ("Đặt phòng",       "booking_form",        "📅"),
    ("Lịch sử đặt",     "booking_list",        "📋"),
    ("Lịch biểu",       "schedule",            "📆"),
    ("Lịch dạy chu kỳ", "recurring_schedule",  "🔄"),
    ("Thông báo",       "notifications",       "📩"),
    ("Phòng học",       "rooms",               "🏫"),
]

PAGE_TITLES = {
    "dashboard":           "Trang chủ",
    "rooms":               "Quản lý phòng học",
    "booking_form":        "Đặt phòng học",
    "booking_list":        "Danh sách đặt phòng",
    "users":               "Quản lý người dùng",
    "equipment":           "Quản lý thiết bị",
    "report":              "Báo cáo thống kê",
    "schedule":            "Lịch biểu phòng học",
    "recurring_schedule":  "Lịch dạy theo chu kỳ tuần",
    "room_issues":         "Báo cáo sự cố phòng",
    "notifications":       "Thông báo nội bộ",
    "room_ratings":        "Quản lý đánh giá người dùng",
    "profile":             "Hồ sơ người dùng",
}


def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"


# ── App root ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("He Thong Quan Ly Phong Hoc")
        self.geometry("1280x780")
        self.minsize(960, 600)
        self.configure(bg=C_BG)
        apply_theme(ttk.Style())
        self._center()

        # ── Controllers (shared singletons) ───────────────────────────────────
        self.auth_ctrl   = AuthController()
        self.room_ctrl   = RoomController()
        self.booking_ctrl = BookingController()
        self.user_ctrl   = UserController()
        self.equip_ctrl  = EquipmentController()
        self.feedback_ctrl = RoomFeedbackController()
        self.report_ctrl = ReportController(
            self.room_ctrl, self.booking_ctrl,
            self.user_ctrl, self.equip_ctrl)
        self.schedule_rule_ctrl = ScheduleRuleController()
        self.notif_ctrl = NotificationController()
        try:
            from database.sqlite_db import backup_database
            backup_database()
        except Exception:
            pass

        self.current_user = None
        self._show_login()

    def _center(self) -> None:
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"1280x780+{(sw-1280)//2}+{(sh-780)//2}")

    def _show_login(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login=self._do_login,
                   auth_controller=self.auth_ctrl).pack(fill="both", expand=True)

    def _do_login(self, username: str, password: str) -> None:
        user = self.auth_ctrl.authenticate(username, password)
        if user is None:
            raise ValueError("Sai tên đăng nhập hoặc mật khẩu.")
        self.current_user = user
        for w in self.winfo_children():
            w.destroy()
        try:
            shell = MainShell(self)
            shell.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi khởi tạo", f"Không thể khởi tạo giao diện chính:\n{str(e)}")

    def logout(self) -> None:
        self.current_user = None
        self._show_login()


# ── Main shell (TopBar + Sidebar + Content) ───────────────────────────────────

class MainShell(tk.Frame):
    def __init__(self, app: App) -> None:
        super().__init__(app, bg=C_BG)
        self.app = app
        self._nav_parts: dict[str, dict] = {}
        self._active_key = ""
        # Page Label removed
        self._badge_host: tk.Label | None = None
        self._badge_lbl: tk.Label | None = None
        self._notif_badge_host: tk.Label | None = None
        self._notif_badge_lbl: tk.Label | None = None
        self._content: tk.Frame | None = None
        self._content_frame: tk.Frame | None = None
        self._sb_collapsed: bool = False
        self._sb_frame: tk.Frame | None = None
        self._sb_toggle_btn: tk.Button | None = None
        self._nav_labels: list[tk.Label] = []
        self._sidebar_texts: list[tk.Widget] = [] # Labels to hide when collapsed
        self._logo_canvas: tk.Canvas | None = None
        self._build()
        self._bind_shortcuts()
        # Trì hoãn để đảm bảo window đã được pack và hiển thị
        self.after(100, lambda: self._navigate("dashboard"))

    # ── Build ──────────────────────────────────────────────────────────────────
    def _build(self) -> None:
        self._build_topbar()
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self._content_frame = tk.Frame(body, bg=C_BG)
        self._content_frame.pack(side="left", fill="both", expand=True)

    # ── TopBar ─────────────────────────────────────────────────────────────────
    def _build_topbar(self) -> None:
        # ── Premium Glass TopBar ──────────────────────────────────────────
        tb_wrap = tk.Frame(self, bg=C_BG)
        tb_wrap.pack(fill="x", pady=(0, 2), padx=0)
        
        tb = tk.Frame(tb_wrap, bg=TP_BG, height=TOPBAR_H)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tb.config(highlightthickness=1, highlightbackground=TP_BORDER)

        # ── Left: Brand & Toggle ──────────────────────────────────────────
        left = tk.Frame(tb, bg=TP_BG)
        left.pack(side="left", fill="y", padx=(20, 0))

        self._sb_toggle_btn = tk.Button(
            left, text="☰", bg=TP_BG, fg=C_PRIMARY,
            font=("Segoe UI", 16, "bold"), relief="flat", bd=0, cursor="hand2",
            activebackground=SB_HOVER, activeforeground=C_PRIMARY,
            command=self._toggle_sidebar)
        self._sb_toggle_btn.pack(side="left", padx=(0, 15))
        
        logo_f = tk.Frame(left, bg=TP_BG)
        logo_f.pack(side="left")
        tk.Label(logo_f, text="SMART", bg=TP_BG, fg=C_PRIMARY, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(logo_f, text="CAMPUS", bg=TP_BG, fg=C_DARK, font=("Segoe UI", 11, "bold")).pack(side="left", padx=(4, 0))

        # ── Center: Search ────────────────────────────────────────────────
        center = tk.Frame(tb, bg=TP_BG)
        center.pack(side="left", fill="both", expand=True, padx=40)
        
        s_wrap = tk.Frame(center, bg=TP_BG)
        s_wrap.pack(expand=True)
        search_f = tk.Frame(s_wrap, bg="#f1f5f9", padx=18, pady=8, highlightthickness=1, highlightbackground="#e2e8f0")
        search_f.pack(pady=10)
        tk.Label(search_f, text="🔍", bg="#f1f5f9", fg="#64748b", font=("Segoe UI", 11)).pack(side="left")
        self.search_ent = tk.Entry(search_f, bg="#f1f5f9", fg=C_DARK, font=("Segoe UI", 10), relief="flat", bd=0, width=48)
        self.search_ent.pack(side="left", padx=12)
        self.search_ent.insert(0, "Tìm nhanh...")
        
        def _on_focus(e, active):
            clr = "white" if active else "#f1f5f9"
            search_f.config(bg=clr, highlightbackground=C_PRIMARY if active else "#e2e8f0")
            self.search_ent.config(bg=clr)
            if active and self.search_ent.get() == "Tìm nhanh...": self.search_ent.delete(0, "end")
            if not active and not self.search_ent.get(): self.search_ent.insert(0, "Tìm nhanh...")
        self.search_ent.bind("<FocusIn>", lambda e: _on_focus(e, True))
        self.search_ent.bind("<FocusOut>", lambda e: _on_focus(e, False))

        # ── Right: User ──────────────────────────────────────────────────
        right = tk.Frame(tb, bg=TP_BG)
        right.pack(side="right", fill="y", padx=20)
        
        # Clock
        clock_f = tk.Frame(right, bg=TP_BG, padx=15)
        clock_f.pack(side="left")
        self._time_lbl = tk.Label(clock_f, text="--:--:--", bg=TP_BG, fg=C_DARK, font=("Segoe UI Semibold", 10), anchor="e")
        self._time_lbl.pack(fill="x")
        self._date_lbl = tk.Label(clock_f, text="--- --, ----", bg=TP_BG, fg=C_MUTED, font=("Segoe UI", 7, "bold"), anchor="e")
        self._date_lbl.pack(fill="x")
        self._update_clock()

        # Badges
        notif_f = tk.Frame(right, bg=TP_BG)
        notif_f.pack(side="left", padx=10)
        self._notif_badge_host = tk.Label(notif_f, text="📩", bg=TP_BG, font=("Segoe UI", 13), cursor="hand2")
        self._notif_badge_host.pack(side="left", padx=5)
        self._notif_badge_host.bind("<Button-1>", lambda *_: self._navigate("notifications"))
        
        if self.app.current_user.role == "Admin":
            self._badge_host = tk.Label(notif_f, text="🔔", bg=TP_BG, font=("Segoe UI", 13), cursor="hand2")
            self._badge_host.pack(side="left", padx=5)
            self._badge_host.bind("<Button-1>", lambda *_: self._navigate("booking_list"))
        
        self._refresh_notif_badge()
        if self.app.current_user.role == "Admin": self._refresh_pending_badge()

        # User Profile
        u = self.app.current_user
        u_f = tk.Frame(right, bg=TP_BG, cursor="hand2")
        u_f.pack(side="left", padx=(10, 0))
        u_info = tk.Frame(u_f, bg=TP_BG)
        u_info.pack(side="left", padx=(0, 12))
        tk.Label(u_info, text=u.full_name, bg=TP_BG, fg=C_DARK, font=("Segoe UI Semibold", 9), anchor="e").pack(anchor="e")
        tk.Label(u_info, text=u.role.upper(), bg=TP_BG, fg=C_PRIMARY, font=("Segoe UI", 7, "bold"), anchor="e").pack(anchor="e")

        av_c = tk.Canvas(u_f, bg=TP_BG, width=42, height=42, highlightthickness=0)
        av_c.pack(side="left")
        av_clr = ROLE_AVATAR.get(u.role, "#64748b")
        av_c.create_oval(2, 2, 40, 40, fill=av_clr, outline="")
        av_c.create_text(21, 21, text=_initials(u.full_name), fill="white", font=("Segoe UI", 11, "bold"))
        av_c.create_oval(30, 30, 40, 40, fill="#10b981", outline="white", width=2)
        
        def _bind_recursive(w):
            w.bind("<Button-1>", lambda e: self._show_user_menu(e))
            for child in w.winfo_children(): _bind_recursive(child)
        _bind_recursive(u_f)
        tk.Frame(tb, bg="#f1f5f9", height=1).pack(fill="x", side="bottom")


    def _show_user_menu(self, event: tk.Event) -> None:
        """Luxury internal SaaS-style dropdown menu."""
        if hasattr(self, "_u_menu") and self._u_menu.winfo_exists():
            self._u_menu.destroy()
            return

        menu = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#e2e8f0", padx=1, pady=1)
        self._u_menu = menu
        
        u = self.app.current_user
        
        # Header (User Info) - Premium Look
        head = tk.Frame(menu, bg="#f8fafc", padx=15, pady=12)
        head.pack(fill="x")
        tk.Label(head, text=u.full_name, bg="#f8fafc", fg=C_DARK, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(head, text=u.role.upper(), bg="#f8fafc", fg=C_PRIMARY, font=("Segoe UI", 7, "bold")).pack(anchor="w")
        
        tk.Frame(menu, bg="#f1f5f9", height=1).pack(fill="x")
        
        items = [
            ("👤  Hồ sơ tài khoản", lambda: self._navigate("profile")),
            ("🛡️  Bảo mật & Quyền", None),
            ("SEP", None),
            ("🚪  Đăng xuất hệ thống", self.app.logout),
        ]
        
        def _item(lbl, cmd):
            if lbl == "SEP":
                tk.Frame(menu, bg="#f1f5f9", height=1).pack(fill="x", pady=4)
                return
                
            btn = tk.Label(menu, text=lbl, bg="white", fg="#475569", 
                          font=("Segoe UI", 9), anchor="w", padx=15, pady=10, cursor="hand2")
            btn.pack(fill="x")
            
            def _h(e): btn.config(bg="#f8fafc", fg=C_PRIMARY)
            def _l(e): btn.config(bg="white", fg="#475569")
            btn.bind("<Enter>", _h); btn.bind("<Leave>", _l)
            
            if cmd:
                def _wrap(e):
                    menu.destroy()
                    cmd()
                btn.bind("<Button-1>", _wrap)
            else:
                btn.config(fg="#cbd5e1", cursor="")
        
        for lbl, cmd in items: _item(lbl, cmd)

        self.update_idletasks()
        # Position relative to TopBar User area
        mx = event.widget.winfo_rootx() - self.winfo_rootx()
        my = event.widget.winfo_rooty() - self.winfo_rooty() + event.widget.winfo_height() + 8
        
        menu_w = 210
        mx = mx + event.widget.winfo_width() - menu_w
        menu.place(x=mx, y=my, width=menu_w)
        
        # Click-away logic
        def _away(e):
            if not menu.winfo_exists(): return
            x, y = menu.winfo_rootx(), menu.winfo_rooty()
            w, h = menu.winfo_width(), menu.winfo_height()
            if not (x <= e.x_root <= x + w and y <= e.y_root <= y + h):
                menu.destroy()
                self.app.unbind_all("<Button-1>")
        self.app.bind_all("<Button-1>", _away)

    def _update_clock(self) -> None:
        """Luxury real-time clock update."""
        import datetime as _dt
        if not self.winfo_exists(): return
        now = _dt.datetime.now()
        self._time_lbl.config(text=now.strftime("%H:%M:%S"))
        # Luxury Format: 12 MAY, 2026
        self._date_lbl.config(text=now.strftime("%d %b, %Y").upper())
        self.after(1000, self._update_clock)


    def _pending_count(self) -> int:
        try:
            return len([
                b for b in self.app.booking_ctrl.list_bookings(from_today=False)
                if getattr(b, "status", "") == "Cho duyet"
            ])
        except Exception:
            return 0

    def _refresh_pending_badge(self) -> None:
        if self._badge_host is None:
            return
        pending_count = self._pending_count()

        if pending_count <= 0:
            if self._badge_lbl is not None:
                self._badge_lbl.destroy()
                self._badge_lbl = None
            return

        if self._badge_lbl is None:
            self._badge_lbl = tk.Label(
                self._badge_host.master,
                bg="#dc2626",
                fg="white",
                font=("Segoe UI", 7, "bold"),
                width=2,
            )
            self._badge_lbl.place(
                in_=self._badge_host,
                relx=1.0,
                rely=0.0,
                anchor="ne",
                x=4,
                y=-2,
            )

        self._badge_lbl.config(text=str(pending_count))

    def _refresh_notif_badge(self) -> None:
        """Update the 📩 bell badge with unread notification count."""
        if self._notif_badge_host is None or not self.app.current_user:
            return
        try:
            count = self.app.notif_ctrl.count_unread(
                self.app.current_user.user_id)
        except Exception:
            count = 0

        if count <= 0:
            if self._notif_badge_lbl is not None:
                self._notif_badge_lbl.destroy()
                self._notif_badge_lbl = None
            return

        if self._notif_badge_lbl is None:
            self._notif_badge_lbl = tk.Label(
                self._notif_badge_host.master,
                bg="#4f46e5", fg="white",
                font=("Segoe UI", 7, "bold"), width=2,
            )
            self._notif_badge_lbl.place(
                in_=self._notif_badge_host,
                relx=1.0, rely=0.0, anchor="ne", x=4, y=-2,
            )
        self._notif_badge_lbl.config(text=str(count))

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent: tk.Frame) -> None:
        sb = tk.Frame(parent, bg=SB_BG, width=SIDEBAR_W)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        self._sb_frame = sb  # save reference for collapse/expand

        # ── Premium Logo Header ──────────────────────────────────────────
        logo_container = tk.Frame(sb, bg=SB_BG, pady=15)
        logo_container.pack(fill="x")
        
        self._logo_canvas = tk.Canvas(logo_container, width=SIDEBAR_W, height=70,
                                     bg=SB_BG, highlightthickness=0)
        self._logo_canvas.pack(fill="x")

        def _draw_logo(e=None):
            cv = self._logo_canvas
            cv.delete("all")
            w = cv.winfo_width() or SIDEBAR_W
            
            # Elite Logo (Polygon style)
            cv.create_polygon([15,15, 45,10, 50,40, 20,45], fill=SB_ACCENT, outline="", tags="logo")
            cv.create_text(32, 28, text="S", font=("Segoe UI", 16, "bold"), fill="white")
            
            if not self._sb_collapsed:
                cv.create_text(65, 22, text="TITANIUM RBS", 
                              font=("Segoe UI", 13, "bold"), fill="#1e293b", anchor="w", tags="txt")
                cv.create_text(65, 42, text="Quản trị viên Hệ thống", 
                              font=("Segoe UI", 8), fill="#64748b", anchor="w", tags="txt")

        self._logo_canvas.bind("<Configure>", _draw_logo)

        # Divider - Subtle
        tk.Frame(sb, bg="#e2e8f0", height=1).pack(fill="x", padx=25, pady=(5, 15))

        # Scrollable area for nav items
        cv = tk.Canvas(sb, bg=SB_BG, highlightthickness=0)
        # We will pack this LATER at the end of _build_sidebar to ensure it fills middle space
        
        # Mousewheel binding logic
        def _on_mousewheel(event):
            if cv.winfo_exists():
                cv.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_mousewheel(child)

        cv.bind("<Enter>", lambda _: cv.bind_all("<MouseWheel>", _on_mousewheel))
        cv.bind("<Leave>", lambda _: cv.unbind_all("<MouseWheel>"))

        nav_container = tk.Frame(cv, bg=SB_BG)
        cv.create_window((0, 0), window=nav_container, anchor="nw", 
                         tags="nav_win", width=SIDEBAR_W)
        
        def _on_frame_configure(e):
            cv.configure(scrollregion=cv.bbox("all"))
        nav_container.bind("<Configure>", _on_frame_configure)
        
        # Build nav groups
        user = self.app.current_user
        nav_items = NAV_ALL if user.role == "Admin" else NAV_GV_SV
        
        # Initial Category
        self._section_header(nav_container, "DANH MỤC CHÍNH")
        
        for label, key, icon in nav_items:
            if key == "---":
                self._section_header(nav_container, label)
            else:
                self._nav_item(nav_container, label, key, icon or "•")

        # 1. User card at the VERY BOTTOM (Sticky)
        self._bottom_user_card(sb)

        # 2. Canvas for nav items takes ALL remaining middle space
        cv.pack(side="top", fill="both", expand=True)
        
        # After building everything, bind mousewheel to the whole nav_container tree
        _bind_mousewheel(nav_container)

    def _section_header(self, parent: tk.Frame, text: str) -> None:
        f = tk.Frame(parent, bg=SB_BG)
        f.pack(fill="x", pady=(10, 2)) # Compact headers
        lbl = tk.Label(f, text=text, bg=SB_BG, fg="#94a3b8",
                      font=("Segoe UI", 8, "bold"), anchor="w", padx=28)
        lbl.pack(fill="x")
        self._sidebar_texts.append(lbl)

    def _nav_item(self, parent: tk.Frame, label: str,
                  key: str, icon: str) -> None:
        # Outer container for padding
        wrap = tk.Frame(parent, bg=SB_BG, padx=0, pady=1) 
        wrap.pack(fill="x")
        
        # The actual row
        row = tk.Frame(wrap, bg=SB_BG, cursor="hand2")
        row.pack(fill="x")

        # Left active pill - Glow Effect
        accent = tk.Canvas(row, bg=SB_BG, width=4, height=36, highlightthickness=0)
        accent.pack(side="left", padx=(0, 4))
        
        inner = tk.Frame(row, bg=SB_BG, padx=12, pady=10)
        inner.pack(side="left", fill="x", expand=True)

        # Icon support
        tk.Label(inner, text=icon, bg=SB_BG, fg=SB_TEXT,
                 font=("Segoe UI", 12)).pack(side="left")
        
        txt = tk.Label(inner, text=label, bg=SB_BG, fg=SB_TEXT,
                       font=("Segoe UI", 12, "bold"), anchor="w")
        txt.pack(side="left", padx=(12, 0))
        self._nav_labels.append(txt)

        self._nav_parts[key] = {
            "wrap": wrap, "row": row, "inner": inner,
            "text": txt, "accent": accent,
        }

        def on_enter(_e, k=key):
            if k != self._active_key:
                row.config(bg=SB_HOVER)
                inner.config(bg=SB_HOVER)
                for w in inner.winfo_children(): 
                    if isinstance(w, tk.Label): w.config(bg=SB_HOVER, fg=SB_TEXT_ACTIVE)

        def on_leave(_e, k=key):
            if k == self._active_key: return
            row.config(bg=SB_BG)
            inner.config(bg=SB_BG)
            for w in inner.winfo_children(): 
                if isinstance(w, tk.Label): w.config(bg=SB_BG, fg=SB_TEXT)

        def on_click(_e, k=key):
            self._navigate(k)

        for w in (row, inner, txt, accent):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    def _bottom_user_card(self, parent: tk.Frame) -> None:
        user = self.app.current_user
        # High-fidelity user card
        wrap = tk.Frame(parent, bg=SB_BG, padx=12, pady=16)
        wrap.pack(side="bottom", fill="x")
        
        card = tk.Frame(wrap, bg="#f8fafc", padx=12, pady=12)
        card.pack(fill="x")
        card.config(highlightthickness=1, highlightbackground="#e2e8f0")
        
        # Avatar
        av_box = tk.Frame(card, bg=SB_BG)
        av_box.pack(side="left", padx=(0, 12))
        av = tk.Canvas(av_box, width=38, height=38, bg=SB_BG, highlightthickness=0)
        av.pack()
        av.create_oval(2, 2, 36, 36, fill=SB_HOVER, outline=SB_MUTED)
        av.create_text(19, 19, text=_initials(user.full_name), font=("Segoe UI", 9, "bold"), fill=SB_ACCENT)
        av.create_oval(26, 26, 34, 34, fill="#22c55e", outline=SB_BG, width=1)
        
        # Info
        info = tk.Frame(card, bg="#f8fafc")
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=user.full_name, bg="#f8fafc", fg="#1e293b", font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        tk.Label(info, text=user.role.upper(), bg="#f8fafc", fg="#64748b", font=("Segoe UI", 7, "bold"), anchor="w").pack(fill="x")

    # ── Sidebar toggle ────────────────────────────────────────────────────────
    def _toggle_sidebar(self) -> None:
        if self._sb_frame is None: return
        self._sb_collapsed = not self._sb_collapsed
        target_w = SIDEBAR_W_COLLAPSED if self._sb_collapsed else SIDEBAR_W
        if self._sb_collapsed:
            for lbl in self._nav_labels: lbl.pack_forget()
            for widget in self._sidebar_texts: widget.pack_forget()
            if self._logo_canvas: self._logo_canvas.itemconfigure("txt", state="hidden")
        self._animate_sidebar(target_w)


    def _animate_sidebar(self, target_w: int) -> None:
        if self._sb_frame is None: return
        current_w = self._sb_frame.winfo_width()
        step = 25
        if abs(current_w - target_w) <= step:
            self._sb_frame.config(width=target_w)
            if not self._sb_collapsed:
                for lbl in self._nav_labels: lbl.pack(side="left", fill="x")
                for widget in self._sidebar_texts: widget.pack(fill="x")
                if self._logo_canvas: self._logo_canvas.itemconfigure("txt", state="normal")
            return
        new_w = current_w + (step if target_w > current_w else -step)
        self._sb_frame.config(width=new_w)
        self.after(10, lambda: self._animate_sidebar(target_w))

    # ── Navigation ─────────────────────────────────────────────────────────────
    def _navigate(self, key: str) -> None:
        self._refresh_pending_badge()
        self._refresh_notif_badge()

        # Deactivate old
        if self._active_key in self._nav_parts:
            p = self._nav_parts[self._active_key]
            for w in (p["row"], p["inner"]): w.config(bg=SB_BG)
            for child in p["inner"].winfo_children():
                if isinstance(child, tk.Label): child.config(bg=SB_BG, fg=SB_TEXT)
            p["accent"].config(bg=SB_BG)
            p["accent"].delete("all")

        self._active_key = key

        # Activate new
        if key in self._nav_parts:
            p = self._nav_parts[key]
            active_bg = SB_ACTIVE
            for w in (p["row"], p["inner"]): w.config(bg=active_bg)
            for child in p["inner"].winfo_children():
                if isinstance(child, tk.Label): child.config(bg=active_bg, fg=SB_TEXT_ACTIVE)
            
            p["accent"].config(bg=active_bg)
            p["accent"].delete("all")
            # Premium Glow Pill
            p["accent"].create_rectangle(0, 4, 4, 32, fill=SB_ACCENT, outline="", width=0)

        # Breadcrumb update removed

        # Swap content
        if self._content is not None:
            self._content.destroy()

        app = self.app
        try:
            if key == "dashboard":
                frame = DashboardFrame(self._content_frame,
                                       app.report_ctrl, app.booking_ctrl,
                                       current_user=app.current_user)
            elif key == "rooms":
                frame = RoomManagementFrame(self._content_frame, app.room_ctrl,
                                            app.booking_ctrl, app.feedback_ctrl, 
                                            app.current_user, equipment_ctrl=app.equip_ctrl)
            elif key == "booking_form":
                frame = BookingFormFrame(
                    self._content_frame, app.booking_ctrl, app.room_ctrl,
                    app.current_user,
                    on_booking_created=lambda: self._navigate("booking_list"),
                    on_navigate_to_rooms=lambda: self._navigate("rooms"),
                    equipment_controller=app.equip_ctrl,
                    feedback_controller=app.feedback_ctrl)
            elif key in ("booking_list", "lich_su_dat"):
                frame = BookingListFrame(self._content_frame,
                                         app.booking_ctrl, app.current_user,
                                         room_controller=app.room_ctrl,
                                         schedule_ctrl=app.schedule_rule_ctrl)
            elif key == "users":
                frame = UserManagementFrame(self._content_frame, app.user_ctrl)
            elif key == "equipment":
                frame = EquipmentManagementFrame(self._content_frame,
                                                 app.equip_ctrl, app.room_ctrl)
            elif key == "report":
                frame = ReportFrame(self._content_frame, app.report_ctrl)
            elif key == "room_issues":
                frame = RoomIssueManagementFrame(self._content_frame, app.feedback_ctrl)
            elif key == "room_ratings":
                frame = RoomRatingManagementFrame(self._content_frame, app.feedback_ctrl)
            elif key == "notifications":
                frame = NotificationFrame(self._content_frame, app.notif_ctrl,
                                          app.current_user,
                                          user_controller=app.user_ctrl)
            elif key in ("schedule", "lich_bieu"):
                frame = ScheduleFrame(self._content_frame,
                                      app.booking_ctrl, app.room_ctrl, app.current_user)

            elif key == "recurring_schedule":
                frame = RecurringScheduleFrame(
                    self._content_frame,
                    app.schedule_rule_ctrl,
                    app.room_ctrl,
                    app.user_ctrl,
                    current_user=app.current_user,
                )
            elif key == "profile":
                frame = ProfileFrame(self._content_frame, app.current_user, app.auth_ctrl)
            else:
                frame = tk.Frame(self._content_frame, bg=C_BG)
                tk.Label(frame, text=f"Trang '{key}' dang phat trien.",
                         bg=C_BG, fg="#94a3b8",
                         font=("Segoe UI", 14)).pack(expand=True)
        except Exception:
            import traceback
            traceback.print_exc()
            frame = tk.Frame(self._content_frame, bg=C_BG)
            tk.Label(frame, text=f"Loi khi tai trang '{key}'.\nXem chi tiet trong terminal.",
                     bg=C_BG, fg="#dc2626",
                     font=("Segoe UI", 12)).pack(expand=True)

        frame.pack(fill="both", expand=True)
        self._content = frame

    # ── Keyboard shortcuts ────────────────────────────────────────────────────
    def _bind_shortcuts(self) -> None:
        app = self.app
        app.bind_all("<Control-Home>",  lambda _: self._navigate("dashboard"))
        app.bind_all("<F5>",            lambda _: self._navigate(self._active_key))
        app.bind_all("<Control-d>",     lambda _: self._navigate("dashboard"))
        app.bind_all("<Control-b>",     lambda _: self._navigate("booking_form"))
        app.bind_all("<Control-l>",     lambda _: self._navigate("booking_list"))
        app.bind_all("<Control-k>",     lambda _: self.search_ent.focus_set())
        app.bind_all("<Control-backslash>", lambda _: self._toggle_sidebar())
        app.bind_all("<F11>",
            lambda _: app.attributes("-fullscreen",
                                      not app.attributes("-fullscreen")))
        app.bind_all("<Escape>",
            lambda _: app.attributes("-fullscreen", False) \
                       if app.attributes("-fullscreen") else None)

        def _unbind_all(_e):
            for seq in ["<Control-Home>", "<F5>", "<Control-d>", "<Control-b>", 
                        "<Control-l>", "<Control-k>", "<Control-backslash>", "<F11>", "<Escape>"]:
                app.unbind_all(seq)

        self.bind("<Destroy>", _unbind_all)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from utils.logger import get_logger as _gl
    _log = _gl("main")
    _log.info("Application starting")
    try:
        App().mainloop()
        _log.info("Application exited normally")
    except Exception:
        _log.critical("Unhandled exception — application crashed", exc_info=True)
        from gui.theme import confirm_dialog
        import tkinter as tk
        # Try to show the styled error dialog
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            confirm_dialog(
                temp_root, "Lỗi hệ thống", 
                "Ung dung gap su co nghiem trong.\nChi tiet da duoc luu vao file logs/app.log.",
                kind="danger", cancel_text=None
            )
            temp_root.destroy()
        except Exception:
            # Final fallback if even themed dialog fails
            from tkinter import messagebox
            messagebox.showerror("Loi nghiem trong", "Ung dung gap su co va phai dong lai.")
        sys.exit(1)
