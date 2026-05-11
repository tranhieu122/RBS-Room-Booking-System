# recurring_schedule_gui.py – Giao diện quản lý lịch dạy chu kỳ (định kỳ theo tuần)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from tkcalendar import DateEntry  # type: ignore[import-untyped]

from gui.theme import (
    C_BG, C_SURFACE, C_BORDER, C_PRIMARY, C_PRIMARY_H,
    C_MUTED, C_TEXT, C_SUCCESS, C_SUCCESS_BG, C_DANGER, C_DANGER_BG,
    C_WARNING, C_WARNING_BG, C_DARK,
    F_BODY, F_BODY_B, F_SECTION, F_SMALL, F_BTN,
    page_header, btn, make_tree, fill_tree, with_scrollbar, toast,
    confirm_dialog, make_card, search_box, labeled_entry, status_badge, get_q,
    animate_count
)

# ── Constants ────────────────────────────────────────────────────────────────
WEEKDAYS = [
    (1, "Thu 2 (Mon)"),
    (2, "Thu 3 (Tue)"),
    (3, "Thu 4 (Wed)"),
    (4, "Thu 5 (Thu)"),
    (5, "Thu 6 (Fri)"),
    (6, "Thu 7 (Sat)"),
    (7, "Chu nhat (Sun)"),
]
SHORT_DAY = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}

SLOT_PRESETS = [
    ("Ca 1  (07:00 – 09:30)", "07:00", "09:30"),
    ("Ca 2  (09:35 – 12:00)", "09:35", "12:00"),
    ("Ca 3  (13:00 – 15:30)", "13:00", "15:30"),
    ("Ca 4  (15:35 – 18:00)", "15:35", "18:00"),
    ("Ca 5  (18:15 – 20:45)", "18:15", "20:45"),
    ("Tuy chinh",              "",      ""),
]

STATUS_CHIP: dict[str, tuple[str, str]] = {
    "Cho duyet":   (C_WARNING_BG, C_WARNING),
    "Hoat dong": (C_SUCCESS_BG, C_SUCCESS),
    "Da xong":   ("#e0e7ff",    "#4f46e5"),
    "Huy":       (C_DANGER_BG,  C_DANGER),
    "Du kien":   ("#fef3c7",    C_WARNING),
    "Da dien ra":(C_SUCCESS_BG, C_SUCCESS),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _chip(parent: tk.Widget, text: str, bg: str, fg: str) -> tk.Label:
    return tk.Label(parent, text=f"  {text}  ", bg=bg, fg=fg,
                    font=F_SMALL, relief="flat")


def _section(parent: tk.Widget, title: str) -> tk.Frame:
    wrapper = tk.Frame(parent, bg=C_SURFACE)
    wrapper.pack(fill="x", padx=20, pady=(12, 4))
    tk.Frame(wrapper, bg=C_BORDER, height=1).pack(fill="x")
    tk.Label(wrapper, text=title, bg=C_SURFACE, fg=C_MUTED,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))
    return wrapper


def _field_row(parent: tk.Widget, label: str,
               widget_fn) -> tk.Frame:
    row = tk.Frame(parent, bg=C_SURFACE)
    row.pack(fill="x", padx=20, pady=3)
    tk.Label(row, text=label, bg=C_SURFACE, fg=C_TEXT,
             font=F_BODY, width=22, anchor="w").pack(side="left")
    widget_fn(row)
    return row


# ═══════════════════════════════════════════════════════════════════════════════
#  Main Frame
# ═══════════════════════════════════════════════════════════════════════════════

class RecurringScheduleFrame(tk.Frame):
    """Khung giao diện quản lý lịch dạy cố định cho giảng viên (lặp lại hàng tuần)."""
    """Page: Tao lich day theo chu ky tuan."""

    def __init__(self, master: tk.Misc,
                 schedule_rule_controller: Any,
                 room_controller: Any,
                 user_controller: Any,
                 current_user: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.ctrl       = schedule_rule_controller
        self.room_ctrl  = room_controller
        self.user_ctrl  = user_controller
        self.current_user = current_user
        self._selected_rule_id: int | None = None
        self._v_subject = tk.StringVar()
        self._build()

    # ── Build layout ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Header section
        page_header(self, "Quản lý Lịch dạy Chu kỳ", "🔁").pack(fill="x")
        
        # ── Dashboard Stats Section ──────────────────────────────────────────
        self._stats_container = tk.Frame(self, bg=C_BG)
        self._stats_container.pack(fill="x", padx=0, pady=(10, 0)) # Full width
        self._build_stats_bar()

        # ── Main Content Area ────────────────────────────────────────────────
        pane = tk.Frame(self, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=0, pady=(0, 0)) # Full width
        pane.columnconfigure(0, weight=4)
        pane.columnconfigure(1, weight=6)
        pane.rowconfigure(0, weight=1)

        self._build_form(pane)
        self._build_list(pane)
        self._refresh_list()

    def _build_stats_bar(self) -> None:
        for w in self._stats_container.winfo_children(): w.destroy()
        
        # Grid for stat cards
        grid = tk.Frame(self._stats_container, bg=C_BG)
        grid.pack(fill="x", pady=10, padx=20) # Keep internal padding for cards
        for i in range(4): grid.columnconfigure(i, weight=1)

        def _stat_card(col, icon, label, val_var_name, color):
            outer, card = make_card(grid, padx=18, pady=15, shadow=True)
            outer.grid(row=0, column=col, sticky="nsew", padx=8)
            
            # Left icon with glow effect
            badge = tk.Frame(card, bg="#f8fafc", padx=10, pady=8)
            badge.pack(side="left", padx=(0, 15))
            tk.Label(badge, text=icon, font=("Segoe UI", 20), bg="#f8fafc", fg=color).pack()
            
            txt_f = tk.Frame(card, bg=C_SURFACE)
            txt_f.pack(side="left", fill="both", expand=True)
            
            lbl_val = tk.Label(txt_f, text="0", font=("Segoe UI", 18, "bold"), 
                              fg=C_DARK, bg=C_SURFACE)
            lbl_val.pack(anchor="w")
            setattr(self, val_var_name, lbl_val)
            
            tk.Label(txt_f, text=label.upper(), font=("Segoe UI", 8, "bold"), 
                     fg=C_MUTED, bg=C_SURFACE).pack(anchor="w")

            # Hover interaction
            outer.config(highlightthickness=1, highlightbackground=C_BORDER)
            def _on_enter(e): outer.config(highlightbackground=color, highlightthickness=2)
            def _on_leave(e): outer.config(highlightbackground=C_BORDER, highlightthickness=1)
            card.bind("<Enter>", _on_enter)
            card.bind("<Leave>", _on_leave)

        _stat_card(0, "📅", "Tổng quy tắc", "_lbl_total_rules", C_PRIMARY)
        _stat_card(1, "🟢", "Đang hoạt động", "_lbl_active_rules", C_SUCCESS)
        _stat_card(2, "📚", "Số buổi học", "_lbl_total_occs", "#8b5cf6")
        _stat_card(3, "⚠️", "Đã hủy/Xong", "_lbl_ended_rules", C_DANGER)

    # ── LEFT: Form ────────────────────────────────────────────────────────────

    def _build_form(self, parent: tk.Frame) -> None:
        left_outer = tk.Frame(parent, bg=C_BG)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        
        outer, card = make_card(left_outer, padx=0, pady=0)
        outer.pack(fill="both", expand=True)

        # Header with accent and Premium Title
        f_hdr = tk.Frame(card, bg="#f8fafc", pady=15, padx=20)
        f_hdr.pack(fill="x")
        tk.Label(f_hdr, text="TẠO MỚI LỊCH CHU KỲ", bg="#f8fafc",
                 fg=C_PRIMARY, font=("Segoe UI", 11, "bold")).pack(side="left")
        
        # Status Badge in header
        status_f = tk.Frame(f_hdr, bg="#eef2ff", padx=8, pady=2)
        status_f.pack(side="right")
        tk.Label(status_f, text="TIÊU CHUẨN", bg="#eef2ff", fg=C_PRIMARY,
                 font=("Segoe UI", 7, "bold")).pack()
        
        tk.Frame(card, bg=C_BORDER, height=1).pack(fill="x")

        # Scrollable form body
        canvas = tk.Canvas(card, bg=C_SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)  # type: ignore
        canvas.configure(yscrollcommand=vsb.set)
        body = tk.Frame(canvas, bg=C_SURFACE)
        
        # Crucial fix: Make body expand to canvas width
        canvas_win = canvas.create_window((0, 0), window=body, anchor="nw")
        
        def _on_mousewheel(e):
            canvas.yview_scroll(-1*(e.delta//120), "units")

        def _bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            for child in widget.winfo_children():
                _bind_mousewheel(child)

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_win, width=e.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        body.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", _on_canvas_configure)
        
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Recursive binding after build
        self.after(200, lambda: _bind_mousewheel(body))

        self._form_body = body
        self._build_form_fields(body)

    def _build_form_fields(self, body: tk.Frame) -> None:
        # ── Section 1: Subject ───────────────────────────────────
        labeled_entry(body, "Tên môn / buổi dạy *", self._v_subject, icon="📚", padx=20)

        # Row: Lecturer & Room
        f_row1 = tk.Frame(body, bg=C_SURFACE, padx=20, pady=10)
        f_row1.pack(fill="x")
        f_row1.columnconfigure(0, weight=1); f_row1.columnconfigure(1, weight=1)
        
        # Lecturer
        f_l = tk.Frame(f_row1, bg=C_SURFACE)
        f_l.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(f_l, text="GIẢNG VIÊN *", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        inner_l = tk.Frame(f_l, bg=C_BORDER, padx=1, pady=1); inner_l.pack(fill="x", pady=(4,0))
        self._v_lecturer = tk.StringVar()
        if self.current_user: self._v_lecturer.set(self.current_user.full_name)
        lect_vals = self._lecturer_options()
        self._cb_lecturer = ttk.Combobox(inner_l, textvariable=self._v_lecturer, values=lect_vals, font=("Segoe UI", 10), state="readonly" if lect_vals else "normal")
        self._cb_lecturer.pack(fill="x")

        # Room
        f_r = tk.Frame(f_row1, bg=C_SURFACE)
        f_r.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(f_r, text="PHÒNG HỌC *", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        inner_r = tk.Frame(f_r, bg=C_BORDER, padx=1, pady=1); inner_r.pack(fill="x", pady=(4,0))
        self._v_room = tk.StringVar()
        rooms = self.room_ctrl.list_rooms()
        room_vals = [f"{r.room_id} - {r.name}" for r in rooms]
        self._cb_room = ttk.Combobox(inner_r, textvariable=self._v_room, values=room_vals, font=("Segoe UI", 10), state="readonly")
        self._cb_room.pack(fill="x")

        # ── Section 2: Days of Week (Visual Selector) ───────────────────────
        tk.Label(body, text="THỨ TRONG TUẦN *", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        
        day_box = tk.Frame(body, bg=C_SURFACE, padx=20, pady=5)
        day_box.pack(fill="x")
        
        self._day_vars: dict[int, tk.BooleanVar] = {}
        self._day_btns: dict[int, tk.Button] = {}

        for i, (iso_wd, label) in enumerate(WEEKDAYS):
            v = tk.BooleanVar(value=False)
            self._day_vars[iso_wd] = v
            
            # Container for the chip look
            f = tk.Frame(day_box, bg=C_SURFACE, padx=1, pady=1)
            f.grid(row=0, column=i, padx=3)
            
            b = tk.Button(f, text=SHORT_DAY[iso_wd], font=("Segoe UI", 9, "bold"),
                          bg="#f1f5f9", fg=C_MUTED, relief="flat", cursor="hand2",
                          padx=0, pady=10, bd=0, width=6)
            b.pack()
            self._day_btns[iso_wd] = b
            
            def _toggle(wd=iso_wd):
                val = not self._day_vars[wd].get()
                self._day_vars[wd].set(val)
                self._update_day_btn(wd)
                self._update_preview()
            b.config(command=_toggle)

        # Quick Select buttons
        f_quick = tk.Frame(body, bg=C_SURFACE, padx=20)
        f_quick.pack(fill="x", pady=(5, 10))
        def _quick_sel(kind):
            target = {1,2,3,4,5} if kind=="week" else {6,7}
            for d, var in self._day_vars.items():
                var.set(d in target)
                self._update_day_btn(d)
            self._update_preview()
        
        btn(f_quick, "T2 - T6", lambda: _quick_sel("week"), variant="ghost", font=("Segoe UI", 8)).pack(side="left")
        btn(f_quick, "Cuối tuần", lambda: _quick_sel("end"), variant="ghost", font=("Segoe UI", 8)).pack(side="left", padx=10)

        # ── Section 3: Time ─────────────────────────────────────────
        tk.Label(body, text="KHUNG GIỜ & THỜI GIAN", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        
        f_time_wrap = tk.Frame(body, bg=C_SURFACE, padx=20)
        f_time_wrap.pack(fill="x")

        # Time preset
        self._v_slot = tk.StringVar(value=SLOT_PRESETS[0][0])
        cb_slot = ttk.Combobox(f_time_wrap, textvariable=self._v_slot, values=[s[0] for s in SLOT_PRESETS], font=("Segoe UI", 10), state="readonly")
        cb_slot.pack(fill="x", pady=(0, 10))
        cb_slot.bind("<<ComboboxSelected>>", self._on_slot_preset)

        # Exact times row (Hidden to keep UI clean, controlled by presets)
        self._v_start_time = tk.StringVar(value="07:00")
        self._v_end_time = tk.StringVar(value="09:30")

        # ── Section 4: Effective Dates ──────────────────────────────────────
        tk.Label(body, text="HIỆU LỰC TỪ - ĐẾN", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        f_dates = tk.Frame(body, bg=C_SURFACE, padx=20, pady=5)
        f_dates.pack(fill="x")
        f_dates.columnconfigure(0, weight=1); f_dates.columnconfigure(1, weight=1)

        f_d1 = tk.Frame(f_dates, bg=C_SURFACE); f_d1.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self._de_start = DateEntry(f_d1, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd", 
                                   background=C_PRIMARY, foreground="white", borderwidth=0,
                                   state="readonly")
        self._de_start.set_date(dt.date.today())
        self._de_start.pack(fill="x", ipady=3)

        f_d2 = tk.Frame(f_dates, bg=C_SURFACE); f_d2.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self._de_end = DateEntry(f_d2, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd",
                                 background=C_PRIMARY, foreground="white", borderwidth=0,
                                 state="readonly")
        self._de_end.set_date(dt.date.today() + dt.timedelta(weeks=16))
        self._de_end.pack(fill="x", ipady=3)

        # ── Preview Card ────────────────────────────────────────────────────
        self._preview_outer, self._preview_inner = make_card(body, padx=16, pady=12, shadow=False)
        self._preview_outer.config(highlightthickness=1, highlightbackground="#e0e7ff")
        self._preview_outer.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(self._preview_inner, text="✨ XEM TRƯỚC LỊCH TRÌNH", bg=C_SURFACE, 
                 fg="#4f46e5", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        # Visual Weekly Grid
        self._preview_cv = tk.Canvas(self._preview_inner, height=36, bg=C_SURFACE, highlightthickness=0)
        self._preview_cv.pack(fill="x", pady=(10, 0))
        
        self._preview_lbl = tk.Label(
            self._preview_inner, text="Chọn các thông tin bên trên để bắt đầu...", bg=C_SURFACE, fg=C_TEXT,
            font=("Segoe UI", 10), anchor="w", wraplength=320, justify="left"
        )
        self._preview_lbl.pack(fill="x", pady=(8, 0))

        # Footer Actions
        btn_row = tk.Frame(body, bg=C_SURFACE, padx=20, pady=20)
        btn_row.pack(fill="x")
        
        self._btn_save = btn(btn_row, "Lưu Lịch Chu Kỳ", self._submit, variant="primary", icon="💾")
        self._btn_save.pack(side="left", fill="x", expand=True)
        
        btn(btn_row, "Hủy", self._clear_form, variant="ghost", icon="🧹").pack(side="left", padx=(10, 0))

        # Bindings for automatic preview update
        self._de_start.bind("<<DateEntrySelected>>", lambda _: self._update_preview())
        self._de_end.bind("<<DateEntrySelected>>", lambda _: self._update_preview())
        self._v_subject.trace_add("write", lambda *_: self._update_preview())

    def _update_day_btn(self, wd: int) -> None:
        btn_obj = self._day_btns.get(wd)
        if not btn_obj: return
        if self._day_vars[wd].get():
            btn_obj.config(bg=C_PRIMARY, fg="white")
            btn_obj.master.config(bg=C_PRIMARY) # Highlight border
        else:
            btn_obj.config(bg="#f1f5f9", fg=C_MUTED)
            btn_obj.master.config(bg=C_SURFACE)

    # ── RIGHT: List of rules ──────────────────────────────────────────────────

    def _build_list(self, parent: tk.Frame) -> None:
        right_outer = tk.Frame(parent, bg=C_BG)
        right_outer.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        
        outer, card = make_card(right_outer, padx=0, pady=0)
        outer.pack(fill="both", expand=True)

        hdr = tk.Frame(card, bg=C_SURFACE, padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Danh sach lich day chu ky", bg=C_SURFACE,
                 fg=C_DARK, font=F_SECTION).pack(side="left")
        btn(hdr, "Lam moi", self._refresh_list,
            variant="ghost", icon="🔄").pack(side="right")

        # Filter & Search bar
        fbar = tk.Frame(card, bg=C_SURFACE, padx=16, pady=5)
        fbar.pack(fill="x")
        
        # Search box (integrated debounced search)
        self._v_search = tk.StringVar()
        search_box(fbar, self._v_search, placeholder="Tìm môn, giảng viên, phòng...", 
                  on_type=self._refresh_list, width=32).pack(side="left")

        tk.Label(fbar, text="Trạng thái:", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(16, 0))
        self._v_filter = tk.StringVar(value="Tất cả")
        cb_filter = ttk.Combobox(
            fbar, textvariable=self._v_filter,
            values=["Tất cả", "Cho duyet", "Hoat dong", "Da xong", "Huy"],
            state="readonly", font=("Segoe UI", 9), width=12,
        )
        cb_filter.pack(side="left", padx=(6, 0))
        self._v_filter.trace_add("write", lambda *_: self._refresh_list())

        # Treeview: rules
        cols = ("id", "subject", "days", "time", "date_range", "room", "count", "status")
        heads = ("Ma", "Mon hoc", "Thu trong tuan", "Khung gio",
                 "Khoang thoi gian", "Phong", "So buoi", "Trang thai")
        widths = (40, 150, 120, 100, 160, 60, 60, 80)

        tree_frame = tk.Frame(card, bg=C_SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 6))

        self._tree = ttk.Treeview(  # type: ignore
            tree_frame, columns=cols, show="headings",
            style="TV.Treeview", selectmode="browse",
        )
        for col, head, w in zip(cols, heads, widths):
            self._tree.heading(col, text=head)
            # Make subject and date_range stretch more than others to fill space
            is_stretch = col in ("subject", "days", "date_range")
            self._tree.column(col, width=w, minwidth=50, anchor="w", stretch=is_stretch)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",  # type: ignore
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_rule_select)
        
        # Hover effect on tree rows (simulated)
        def _on_motion(e):
            item = self._tree.identify_row(e.y)
            if item:
                self._tree.tk.call(self._tree, "tag", "remove", "hover")
                self._tree.item(item, tags=(self._tree.item(item, "tags") + ("hover",)))
        self._tree.bind("<Motion>", _on_motion) # Added binding for motion
        
        self._tree.tag_configure("hover", background="#eef2ff")

        # Action bar
        act = tk.Frame(card, bg="#f8fafc", padx=16, pady=15)
        act.pack(fill="x")
        
        left_act = tk.Frame(act, bg="#f8fafc")
        left_act.pack(side="left")
        
        btn(left_act, "Xem Chi Tiết", self._view_occurrences,
            variant="primary", icon="📋").pack(side="left")
        btn(left_act, "Đổi Trạng Thái", self._change_status,
            variant="outline", icon="✏️").pack(side="left", padx=10)
        
        right_act = tk.Frame(act, bg="#f8fafc")
        right_act.pack(side="right")
        
        btn(right_act, "Xóa Lịch", self._delete_rule,
            variant="danger", icon="🗑️").pack(side="right")
        
        tk.Label(right_act, text="Cẩn thận khi xóa  ", bg="#f8fafc", fg=C_MUTED,
                 font=("Segoe UI", 8, "italic")).pack(side="right")

        # Occurrence detail panel (hidden by default)
        self._occ_panel = tk.Frame(right_outer, bg=C_BG,
                                   highlightthickness=1,
                                   highlightbackground=C_BORDER)
        # Not packed yet — shown on demand

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_slot_preset(self, _event: Any = None) -> None:
        val = self._v_slot.get()
        for name, st, et in SLOT_PRESETS:
            if val == name:
                if st:
                    self._v_start_time.set(st)
                    self._v_end_time.set(et)
                return

    @staticmethod
    def _parse_date_input(s: str) -> dt.date:
        """Parse DD/MM/YYYY → date. Raises ValueError on bad input."""
        return dt.datetime.strptime(s.strip(), "%d/%m/%Y").date()

    def _update_preview(self) -> None:
        try:
            d_start = self._de_start.get_date()
            d_end   = self._de_end.get_date()
        except Exception:
            self._preview_lbl.config(
                text="⚠  Ngay khong hop le.",
                bg="#fdf2f8", fg="#db2777")
            return

        selected_days = [d for d, v in self._day_vars.items() if v.get()]
        if not selected_days:
            self._preview_lbl.config(
                text="ℹ  Chon thu trong tuan de xem uoc tinh so buoi.",
                bg="#eef2ff", fg="#4f46e5")
            return

        # Count occurrences
        count = 0
        cur = d_start
        day_set = set(selected_days)
        while cur <= d_end:
            if cur.isoweekday() in day_set:
                count += 1
            cur += dt.timedelta(days=1)

        days_str = ", ".join(SHORT_DAY.get(d, str(d)) for d in sorted(selected_days))
        weeks = (d_end - d_start).days // 7 + 1
        
        subj = self._v_subject.get() or "(Chưa đặt tên)"
        msg = (f"📅 Môn: {subj}\n"
               f"✨ Dự kiến sinh {count} buổi học trong ~{weeks} tuần.\n"
               f"🕒 Thời gian: {self._v_start_time.get()} – {self._v_end_time.get()}")
        
        self._preview_lbl.config(text=msg, fg=C_SUCCESS if count > 0 else C_TEXT)
        self._preview_outer.config(highlightbackground=C_SUCCESS if count > 0 else "#e0e7ff")
        self._draw_preview_grid(selected_days)

    def _draw_preview_grid(self, selected_days: list[int]) -> None:
        cv = self._preview_cv
        cv.delete("all")
        w = cv.winfo_width() or 320
        h = 36
        cell_w = 32
        gap = 6
        total_w = (cell_w + gap) * 7 - gap
        start_x = 0 # Align left
        
        day_set = set(selected_days)
        for i, (iso_wd, _) in enumerate(WEEKDAYS):
            x0 = start_x + i * (cell_w + gap)
            x1 = x0 + cell_w
            is_sel = iso_wd in day_set
            bg = C_PRIMARY if is_sel else "#f1f5f9"
            fg = "white" if is_sel else C_MUTED
            
            # Rounded box
            cv.create_rectangle(x0, 2, x1, h-2, fill=bg, outline="", width=0)
            cv.create_text((x0+x1)/2, h/2, text=SHORT_DAY[iso_wd], 
                          font=("Segoe UI", 8, "bold"), fill=fg)

    def _submit(self) -> None:
        """Xử lý việc lưu lịch dạy chu kỳ mới và tạo các buổi học lẻ."""
        days = [d for d, v in self._day_vars.items() if v.get()]
        # Resolve lecturer id/name
        lect_text = self._v_lecturer.get().strip()
        lect_id = ""
        lect_name = lect_text
        if self.current_user:
            # Try to match by name from combobox
            try:
                all_users = self.user_ctrl.list_users()
                match = next(
                    (u for u in all_users if u.full_name == lect_text), None)
                if match:
                    lect_id = match.user_id
                    lect_name = match.full_name
                else:
                    lect_id = self.current_user.user_id
                    lect_name = lect_text or self.current_user.full_name
            except Exception:
                lect_id = getattr(self.current_user, "user_id", "")
                lect_name = lect_text

        # Read dates from DateEntry widgets (always valid ISO format)
        start_iso = self._de_start.get_date().isoformat()
        end_iso   = self._de_end.get_date().isoformat()
        
        # Room ID parsing (if using "ID - Name" format)
        rid = self._v_room.get()
        if " - " in rid: rid = rid.split(" - ")[0]

        payload = {
            "subject":      self._v_subject.get(),
            "days_of_week": days,
            "start_time":   self._v_start_time.get(),
            "end_time":     self._v_end_time.get(),
            "start_date":   start_iso,
            "end_date":     end_iso,
            "room_id":      rid,
            "lecturer_id":  lect_id or "unknown",
            "lecturer_name": lect_name,
        }
        
        # If Admin, can create as Active immediately
        if self.current_user and self.current_user.role == "Admin":
            payload["status"] = "Hoat dong"
        else:
            payload["status"] = "Cho duyet"

        try:
            rule = self.ctrl.create_rule(payload)
        except ValueError as exc:
            confirm_dialog(self, "Loi nhap lieu", str(exc), kind="warning", cancel_text=None)
            return
        except Exception as exc:
            confirm_dialog(self, "Loi he thong", str(exc), kind="danger", cancel_text=None)
            return

        n_occ = self.ctrl.count_occurrences(rule.rule_id)
        toast(self, f"✅ Da tao lich #{rule.rule_id} — {n_occ} buoi hoc duoc sinh ra!")
        self._clear_form()
        self._refresh_list()

    def _on_save(self) -> None:
        """Xử lý việc lưu lịch dạy chu kỳ mới và tạo các buổi học lẻ."""
        subject = self._v_subj.get().strip()
        for v in self._day_vars.values():
            v.set(False)
        self._v_slot.set(SLOT_PRESETS[0][0])
        self._v_start_time.set("07:00")
        self._v_end_time.set("09:30")

    def _clear_form(self) -> None:
        self._v_subject.set("")
        for v in self._day_vars.values():
            v.set(False)
        self._v_slot.set(SLOT_PRESETS[0][0])
        self._v_start_time.set("07:00")
        self._v_end_time.set("09:30")
        self._de_start.set_date(dt.date.today())
        self._de_end.set_date(dt.date.today() + dt.timedelta(weeks=16))
        
        # Reset visual day selector
        for wd in self._day_btns:
            self._update_day_btn(wd)
            
        self._update_preview()

    def _refresh_list(self) -> None:
        q = get_q(self._v_search, "Tìm môn, giảng viên, phòng...")
        rules = self.ctrl.list_rules(q)
        f_status = self._v_filter.get()

        # Update stats overview with animations
        n_total  = len(rules)
        n_active = sum(1 for r in rules if r.status == "Hoat dong")
        n_ended  = n_total - n_active
        n_occs   = sum(self.ctrl.count_occurrences(r.rule_id) for r in rules)

        if hasattr(self, "_lbl_total_rules"):
            animate_count(self._lbl_total_rules, n_total)
            animate_count(self._lbl_active_rules, n_active)
            animate_count(self._lbl_total_occs, n_occs)
            animate_count(self._lbl_ended_rules, n_ended)

        rows = []
        for r in rules:
            if f_status != "Tất cả" and r.status != f_status:
                continue
            if q:
                if q not in r.subject.lower() and q not in r.room_id.lower():
                    continue

            days_lbl = ", ".join(
                SHORT_DAY.get(d, str(d)) for d in sorted(r.days_of_week))
            time_lbl = f"{r.start_time} – {r.end_time}"
            date_lbl = (f"{r.start_date[8:]}/{r.start_date[5:7]}/{r.start_date[:4]}"
                        f" → {r.end_date[8:]}/{r.end_date[5:7]}/{r.end_date[:4]}")
            n = self.ctrl.count_occurrences(r.rule_id)
            rows.append((
                str(r.rule_id), r.subject, days_lbl, time_lbl, date_lbl, r.room_id, str(n), r.status
            ))

        fill_tree(self._tree, rows)
        # Color rows by status
        for item in self._tree.get_children():
            vals = self._tree.item(item, "values")
            status = vals[7] if len(vals) > 7 else ""
            idx = self._tree.index(item)
            base_tag = "odd" if idx % 2 == 0 else "even"
            
            tags = [base_tag]
            if status == "Cho duyet": tags.append("pending_row")
            elif status == "Huy": tags.append("huy_row")
            elif status == "Da xong": tags.append("done_row")
            elif status == "Hoat dong": tags.append("active_row")
            
            self._tree.item(item, tags=tuple(tags))

        self._tree.tag_configure("pending_row", background="#fffbeb", foreground="#b45309")
        self._tree.tag_configure("active_row",  background="#f0fdf4", foreground="#15803d")
        self._tree.tag_configure("huy_row",      background="#fff1f2", foreground="#e11d48")
        self._tree.tag_configure("done_row",     background="#f8fafc", foreground="#64748b")

    def _on_rule_select(self, _event: Any = None) -> None:
        sel = self._tree.selection()
        if sel:
            self._selected_rule_id = int(self._tree.item(sel[0], "values")[0])
        else:
            self._selected_rule_id = None

    def _view_occurrences(self) -> None:
        if self._selected_rule_id is None:
            confirm_dialog(self, "Thong bao", "Hay chon mot lich de xem chi tiet.", 
                           kind="primary", cancel_text=None)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            confirm_dialog(self, "Loi", "Khong tim thay lich.", 
                           kind="danger", cancel_text=None)
            return
        occurrences = self.ctrl.list_occurrences(self._selected_rule_id)
        _OccurrenceDialog(self, rule, occurrences, self.ctrl)

    def _change_status(self) -> None:
        if self._selected_rule_id is None:
            messagebox.showinfo("Thong bao", "Hay chon mot lich.",
                                parent=self)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            return
        _ChangeStatusDialog(self, rule, self.ctrl,
                            on_done=self._refresh_list)

    def _delete_rule(self) -> None:
        if self._selected_rule_id is None:
            confirm_dialog(self, "Thong bao", "Hay chon mot lich de xoa.", 
                           kind="primary", cancel_text=None)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            return
        n = self.ctrl.count_occurrences(self._selected_rule_id)
        confirm = confirm_dialog(
            self, "Xac nhan xoa",
            f"Xoa lich '{rule.subject}'?\n"
            f"Se xoa toan bo {n} buoi hoc da sinh ra.\n"
            "Hanh dong nay khong the hoan tac.",
            kind="danger"
        )
        if not confirm:
            return
        self.ctrl.delete_rule(self._selected_rule_id)
        self._selected_rule_id = None
        toast(self, "🗑️ Da xoa lich va toan bo cac buoi hoc.")
        self._refresh_list()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _lecturer_options(self) -> list[str]:
        try:
            users = self.user_ctrl.list_users()
            return [u.full_name for u in users
                    if getattr(u, "role", "") in ("Admin", "Giang vien")]
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
#  Dialog: xem danh sach cac buoi hoc
# ═══════════════════════════════════════════════════════════════════════════════

class _OccurrenceDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, rule: Any,
                 occurrences: list, ctrl: Any) -> None:
        super().__init__(parent)
        self.ctrl = ctrl
        self.title(f"Cac buoi hoc — {rule.subject}")
        self.resizable(True, True)
        self.geometry("820x560")
        self.configure(bg=C_BG)
        self.transient(parent)
        self.grab_set()

        # Header
        hdr = tk.Frame(self, bg=C_DARK, padx=24, pady=20)
        hdr.pack(fill="x")
        
        title_f = tk.Frame(hdr, bg=C_DARK)
        title_f.pack(fill="x")
        tk.Label(title_f, text="🗓️", bg=C_DARK, fg=C_PRIMARY, font=("Segoe UI", 24)).pack(side="left", padx=(0, 15))
        
        txt_f = tk.Frame(title_f, bg=C_DARK)
        txt_f.pack(side="left")
        tk.Label(txt_f, text=rule.subject.upper(), bg=C_DARK, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        
        info_str = f"Phòng: {rule.room_id}  •  Giờ: {rule.start_time} – {rule.end_time}"
        tk.Label(txt_f, text=info_str, bg=C_DARK, fg="#94a3b8",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 0))

        # Detail Row
        detail_f = tk.Frame(hdr, bg="#1e293b", padx=15, pady=8)
        detail_f.pack(fill="x", pady=(15, 0))
        tk.Label(detail_f, text=f"👤 Giảng viên: {rule.lecturer_name}",
                 bg="#1e293b", fg=C_LIGHT, font=("Segoe UI", 9, "bold")).pack(side="left")
        
        days_str = " • ".join(SHORT_DAY.get(d, str(d)) for d in sorted(rule.days_of_week))
        tk.Label(detail_f, text=f"📅 Định kỳ: {days_str}",
                 bg="#1e293b", fg="#cbd5e1", font=("Segoe UI", 9)).pack(side="right")

        # Stats bar
        n_total  = len(occurrences)
        n_done   = sum(1 for o in occurrences if o.status == "Da dien ra")
        n_cancel = sum(1 for o in occurrences if o.status == "Huy")
        n_plan   = n_total - n_done - n_cancel

        sbar = tk.Frame(self, bg="#f8fafc", pady=10, highlightthickness=1, highlightbackground=C_BORDER)
        sbar.pack(fill="x")
        for label, val, fg in [
            ("TỔNG SỐ BUỔI:", n_total, C_DARK),
            ("DỰ KIẾN:", n_plan, C_WARNING),
            ("ĐÃ DIỄN RA:", n_done, C_SUCCESS),
            ("HỦY:", n_cancel, C_DANGER),
        ]:
            tk.Label(sbar, text=f"{label} {val}", bg="#f8fafc", fg=fg,
                     font=("Segoe UI", 9, "bold")).pack(side="left", padx=16)

        # Filter
        fbar = tk.Frame(self, bg=C_BG)
        fbar.pack(fill="x", padx=16, pady=(6, 2))
        tk.Label(fbar, text="Loc:", bg=C_BG, fg=C_MUTED,
                 font=F_SMALL).pack(side="left")
        self._v_occ_filter = tk.StringVar(value="Tat ca")
        ttk.Combobox(
            fbar, textvariable=self._v_occ_filter,
            values=["Tat ca", "Du kien", "Da dien ra", "Huy"],
            state="readonly", font=("Segoe UI", 9), width=14,
        ).pack(side="left", padx=(6, 0))
        self._v_occ_filter.trace_add(
            "write", lambda *_: self._fill(occurrences))

        # Treeview
        cols = ("occ_id", "date", "weekday", "time", "room", "status")
        heads = ("#", "Ngay", "Thu", "Khung gio", "Phong", "Trang thai")
        widths = (40, 110, 80, 120, 70, 100)

        tf = tk.Frame(self, bg=C_BG)
        tf.pack(fill="both", expand=True, padx=16, pady=4)

        self._tree = ttk.Treeview(  # type: ignore
            tf, columns=cols, show="headings",
            style="TV.Treeview", selectmode="browse",
        )
        for col, head, w in zip(cols, heads, widths):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(tf, orient="vertical",  # type: ignore
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._all_occs = occurrences
        self._fill(occurrences)

        # Action row
        act = tk.Frame(self, bg=C_BG)
        act.pack(fill="x", padx=16, pady=(4, 12))
        btn(act, "✏️ Doi trang thai buoi", self._change_occ_status,
            variant="secondary").pack(side="left")
        btn(act, "Dong", self.destroy, variant="primary").pack(side="right")

    def _fill(self, occurrences: list) -> None:
        fval = self._v_occ_filter.get()
        for item in self._tree.get_children():
            self._tree.delete(item)
        WD_VN = {1: "Thu 2", 2: "Thu 3", 3: "Thu 4",
                 4: "Thu 5", 5: "Thu 6", 6: "Thu 7", 7: "CN"}
        for idx, o in enumerate(occurrences):
            if fval != "Tat ca" and o.status != fval:
                continue
            d = o.occurrence_date
            date_disp = f"{d[8:]}/{d[5:7]}/{d[:4]}"
            wd_disp = WD_VN.get(o.day_of_week, str(o.day_of_week))
            time_disp = f"{o.start_time} – {o.end_time}"
            tag = "odd" if idx % 2 == 0 else "even"
            self._tree.insert(
                "", "end", iid=str(o.occ_id),
                values=(o.occ_id, date_disp, wd_disp,
                        time_disp, o.room_id, o.status),
                tags=(tag,),
            )
        self._tree.tag_configure("odd",  background="#f1f5f9")
        self._tree.tag_configure("even", background="#ffffff")

    def _change_occ_status(self) -> None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Thong bao", "Hay chon mot buoi hoc.",
                                parent=self)
            return
        occ_id = int(sel[0])
        new_status = _ask_occ_status(self)
        if not new_status:
            return
        try:
            self.ctrl.update_occurrence_status(occ_id, new_status)
        except ValueError as exc:
            confirm_dialog(self, "Loi", str(exc), kind="danger", cancel_text=None)
            return
        # Refresh
        for o in self._all_occs:
            if o.occ_id == occ_id:
                o.status = new_status
        self._fill(self._all_occs)


def _ask_occ_status(parent: tk.Widget) -> str | None:
    dlg = tk.Toplevel(parent)
    dlg.title("Chon trang thai")
    dlg.configure(bg=C_BG)
    dlg.resizable(False, False)
    dlg.transient(parent)
    dlg.grab_set()
    result: list[str] = []

    tk.Label(dlg, text="Chon trang thai moi cho buoi hoc:",
             bg=C_BG, fg=C_TEXT, font=F_BODY,
             padx=20, pady=12).pack()

    v = tk.StringVar(value="Da dien ra")
    for s in ("Du kien", "Da dien ra", "Huy"):
        tk.Radiobutton(dlg, text=s, variable=v, value=s,
                       bg=C_BG, fg=C_TEXT, font=F_BODY,
                       selectcolor=C_SURFACE, activebackground=C_BG,
                       cursor="hand2").pack(anchor="w", padx=30)

    def _ok():
        result.append(v.get())
        dlg.destroy()

    btn_r = tk.Frame(dlg, bg=C_BG)
    btn_r.pack(pady=(10, 14), padx=20, fill="x")
    btn(btn_r, "Xac nhan", _ok, variant="primary").pack(side="left")
    btn(btn_r, "Huy bo", dlg.destroy, variant="secondary").pack(side="left", padx=(8, 0))

    dlg.wait_window()
    return result[0] if result else None


# ═══════════════════════════════════════════════════════════════════════════════
#  Dialog: change rule status
# ═══════════════════════════════════════════════════════════════════════════════

class _ChangeStatusDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, rule: Any,
                 ctrl: Any, on_done) -> None:
        super().__init__(parent)
        self.title("Doi trang thai lich")
        self.configure(bg=C_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.ctrl = ctrl
        self.rule = rule
        self._on_done = on_done

        tk.Label(self,
                 text=f"Lich: {rule.subject}  (hien tai: {rule.status})",
                 bg=C_BG, fg=C_TEXT, font=F_BODY_B,
                 padx=20, pady=12).pack()

        self._v = tk.StringVar(value=rule.status)
        statuses = ["Cho duyet", "Hoat dong", "Da xong", "Huy"]
        for s in statuses:
            tk.Radiobutton(self, text=s, variable=self._v, value=s,
                           bg=C_BG, fg=C_TEXT, font=F_BODY,
                           selectcolor=C_SURFACE, activebackground=C_BG,
                           cursor="hand2").pack(anchor="w", padx=30)

        btn_r = tk.Frame(self, bg=C_BG)
        btn_r.pack(pady=(10, 14), padx=20, fill="x")
        btn(btn_r, "Luu", self._save, variant="primary").pack(side="left")
        btn(btn_r, "Huy", self.destroy, variant="secondary").pack(
            side="left", padx=(8, 0))

    def _save(self) -> None:
        try:
            self.ctrl.update_rule_status(self.rule.rule_id, self._v.get())
        except ValueError as exc:
            confirm_dialog(self, "Loi", str(exc), kind="danger", cancel_text=None)
            return
        self.destroy()
        self._on_done()
