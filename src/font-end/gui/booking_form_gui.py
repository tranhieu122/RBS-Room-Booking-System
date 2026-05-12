# booking_form_gui.py  –  Giao diện đặt phòng học (v3.0 - lọc sức chứa + báo cáo thiết bị)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED, C_DARK, C_TEXT, C_SUCCESS, C_SUCCESS_BG,
                       C_DANGER, C_DANGER_BG, C_WARNING, C_WARNING_BG,
                       page_header, btn, make_card, confirm_dialog)

from tkcalendar import DateEntry  # type: ignore[import-untyped]
from gui.date_picker_fixed import DatePickerWithLabel
from gui.booking_history_gui import BookingHistoryFrame
from gui.advance_booking_calendar import AdvanceCalendarFrame



class BookingFormFrame(tk.Frame):
    """Khung giao diện chính cho việc đặt phòng học cá nhân."""
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 room_controller: Any, current_user: Any,
                 on_booking_created: Any = None,
                 on_navigate_to_rooms: Any = None,
                 equipment_controller: Any = None,
                 feedback_controller: Any = None,
                 initial_date: Optional[str] = None) -> None:
        super().__init__(master, bg=C_BG)
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self.current_user = current_user
        self.on_booking_created = on_booking_created
        self.on_navigate_to_rooms = on_navigate_to_rooms
        self.equip_ctrl   = equipment_controller
        self.feedback_ctrl = feedback_controller
        self.room_var     = tk.StringVar()
        self.date_var     = tk.StringVar(value=initial_date or dt.date.today().isoformat())
        self.slot_var     = tk.StringVar()
        self.avail_var    = tk.StringVar(value="Vui long chon phong va ca...")
        self.capacity_var = tk.StringVar(value="0")
        self.room_type_var = tk.StringVar(value="Tat ca")
        self.summary_room_var = tk.StringVar(value="Chua chon phong")
        self.summary_date_var = tk.StringVar(value=self.date_var.get())
        self.summary_slot_var = tk.StringVar(value="Ca 1")
        self.summary_status_var = tk.StringVar(value="Dang kiem tra lich trong")
        self._room_suggestion_limit = 6
        self._suppress_suggestion_limit_reset = False

        # Trạng thái Đặt phòng lặp lại (Recurring)
        self.recurring_type = tk.StringVar(value="once") # once | weekly
        self.recur_days = {
            0: tk.BooleanVar(value=False), # Thứ 2
            1: tk.BooleanVar(value=False), # Thứ 3
            2: tk.BooleanVar(value=False), # Thứ 4
            3: tk.BooleanVar(value=False), # Thứ 5
            4: tk.BooleanVar(value=False), # Thứ 6
            5: tk.BooleanVar(value=False), # Thứ 7
        }
        self.recur_end_type = tk.StringVar(value="date") # Theo ngày | Theo tuần
        self.recur_end_date = tk.StringVar(value=(dt.date.today() + dt.timedelta(weeks=4)).isoformat())
        self.recur_num_weeks = tk.StringVar(value="4")

        self._setup_scrolling()
        self._build_tabs()
        self._refresh_slots()
        self._setup_traces()


    def _setup_traces(self) -> None:
        self._debounce_timer: str | None = None
        
        def _on_change(*_: Any) -> None:
            if self._debounce_timer:
                self.after_cancel(self._debounce_timer)
            if not self._suppress_suggestion_limit_reset:
                self._room_suggestion_limit = 6
            # Cập nhật danh sách phòng gợi ý tự động sau một khoảng thời gian ngắn (debounce)
            self._debounce_timer = self.after(300, self._refresh_room_suggestions)

        self.date_var.trace_add("write", _on_change)
        self.slot_var.trace_add("write", _on_change)
        self.capacity_var.trace_add("write", _on_change)
        self.room_type_var.trace_add("write", _on_change)

    def _setup_scrolling(self) -> None:
        self._canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._scrollable_frame = tk.Frame(self._canvas, bg=C_BG)

        self._scrollable_frame.bind(
            "<Configure>",
            lambda *_: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._canvas_win = self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        self.bind("<Configure>", self._on_frame_configure)
        
        # Ràng buộc cuộn chuột chỉ khi chuột nằm trên canvas
        self._canvas.bind("<Enter>", lambda _: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda _: self._canvas.unbind_all("<MouseWheel>"))

    def _on_frame_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._canvas_win, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        # Chỉ cuộn nếu khung hình này đang hiển thị và tồn tại
        try:
            if self.winfo_exists() and self.winfo_ismapped():
                self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    def _build_tabs(self) -> None:
        """Tạo giao diện dạng tab cho Biểu mẫu, Lịch sử và Lịch biểu."""
        style = ttk.Style()
        style.configure("Titanium.TNotebook", background=C_BG)
        style.configure("Titanium.TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[15, 5])
        
        self.notebook = ttk.Notebook(self._scrollable_frame, style="Titanium.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        
        # 1. Booking Form Tab
        self.form_tab = tk.Frame(self.notebook, bg=C_BG)
        self.notebook.add(self.form_tab, text=" 📝 Đặt phòng mới ")
        self._build_form(self.form_tab)
        
        # 2. History Tab
        self.history_tab = BookingHistoryFrame(
            self.notebook, self.booking_ctrl, self.current_user
        )
        self.notebook.add(self.history_tab, text=" 📋 Lịch sử của tôi ")
        
        # 3. Advance Calendar Tab
        self.calendar_tab = AdvanceCalendarFrame(
            self.notebook, self.room_ctrl, self.booking_ctrl, self.current_user,
            on_date_selected=self._on_calendar_date_selected
        )
        self.notebook.add(self.calendar_tab, text=" 📅 Lịch trống 30 ngày ")

        # Làm mới các tab khi được chọn
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event: Any = None) -> None:
        selected = self.notebook.select()
        if not selected: return
        tab = self.notebook.nametowidget(selected)
        # Lấy widget từ id của tab
        if tab == getattr(self, "history_tab", None):
            self.history_tab.refresh()
        elif tab == getattr(self, "calendar_tab", None):
            if hasattr(self.calendar_tab, "_refresh_calendar"):
                self.calendar_tab._refresh_calendar()


    def _on_calendar_date_selected(self, date_str: str) -> None:
        """Handle date selection from the advance calendar tab."""
        self.date_var.set(date_str)
        try:
            self._date_entry.set_date(dt.date.fromisoformat(date_str))
        except Exception: pass
        self.notebook.select(self.form_tab)
        self._refresh_slots()

    def _build_form(self, container: tk.Frame) -> None:
        # Move original _build logic here, but targeting 'container'

        # User info banner - Compact & Modern
        info = tk.Frame(container, bg="#ffffff", highlightthickness=1,
                        highlightbackground="#e2e8f0")
        info.pack(fill="x", padx=20, pady=(15, 12))
        
        l_side = tk.Frame(info, bg="#ffffff")
        l_side.pack(side="left", padx=16, pady=10)
        tk.Label(l_side, text="👤", bg="#ffffff", fg="#6366f1", font=("Segoe UI", 12)).pack(side="left")
        tk.Label(l_side, text=self.current_user.full_name, bg="#ffffff", fg="#1e293b", 
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
        tk.Label(l_side, text=f"({self.current_user.role})", bg="#ffffff", fg="#64748b", 
                 font=("Segoe UI", 9)).pack(side="left")

        r_side = tk.Frame(info, bg="#ffffff", padx=12, pady=6)
        r_side.pack(side="right", padx=10, pady=6)
        tk.Label(r_side, text="📌 Yêu cầu sẽ được kiểm duyệt bởi Quản trị viên",
                 bg="#ffffff", fg=C_PRIMARY, font=("Segoe UI", 8, "bold")).pack()

        # Quick Wins: Deadline & Conflict warnings
        self.warning_f = tk.Frame(container, bg=C_BG)
        self.warning_f.pack(fill="x", padx=20, pady=(0, 10))
        self.warning_f.pack_forget() # Hidden by default

        self._build_summary_bar(container)

        # Main form + room info card side by side
        body = tk.Frame(container, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        body.columnconfigure(0, weight=3, minsize=600)
        body.columnconfigure(1, weight=2, minsize=320)
        body.rowconfigure(0, weight=1)

        # ── Left: form ────────────────────────────────────────────────────────
        left_outer = tk.Frame(body, bg=C_BG)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        outer, card = make_card(left_outer, padx=24, pady=20)
        outer.pack(fill="both", expand=True)
        
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1, minsize=200)

        def lbl(row: int, col: int, text: str, py: tuple[int, int] = (8, 2)) -> None:
            tk.Label(card, text=text, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 8, "bold")).grid(
                row=row, column=col, sticky="w", pady=py)

        lbl(0, 0, "PHONG HOC")
        lbl(0, 1, "NGAY DAT")

        all_rooms = self.room_ctrl.list_rooms()
        self._all_rooms = all_rooms
        room_values = [f"{r.room_id} - {r.name} (SC: {r.capacity})"
                       for r in all_rooms
                       if r.status == "Hoat dong"]
        self._room_display_map: dict[str, Any] = {}
        for r in all_rooms:
            key = f"{r.room_id} - {r.name} (SC: {r.capacity})"
            self._room_display_map[key] = r.room_id

        room_cb = ttk.Combobox(card, textvariable=self.room_var,
                               values=room_values, state="readonly", width=28)
        room_cb.grid(row=1, column=0, sticky="w")
        room_cb.bind("<<ComboboxSelected>>", self._on_room_selected)  # type: ignore[arg-type]

        # Fixed Date picker integration - Using Custom for better positioning
        from gui.date_picker_fixed import DatePickerCustom
        
        date_frame = tk.Frame(card, bg=C_SURFACE)
        date_frame.grid(row=1, column=1, sticky="ew", padx=(12, 0))
        
        self.date_picker = DatePickerCustom(
            date_frame,
            self.date_var,
            on_change=self._refresh_slots
        )
        self.date_picker.pack(fill="x", expand=True)

        # Keep internal reference for set_date/get_date compatibility
        self._date_entry = self.date_picker._date_entry

        # ── Capacity filter row ───────────────────────────────────────────────
        lbl(2, 0, "SO NGUOI DU KIEN (de loc phong)")
        cap_frame = tk.Frame(card, bg=C_SURFACE)
        cap_frame.grid(row=3, column=0, sticky="w", pady=(0, 4))
        tk.Label(cap_frame, text="Toi thieu:", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        cap_spin = tk.Spinbox(cap_frame, from_=0, to=500, increment=5,
                              textvariable=self.capacity_var,
                              width=6, font=("Segoe UI", 10),
                              relief="solid", bd=1)
        cap_spin.pack(side="left", padx=6)
        cap_spin.bind("<FocusOut>", lambda *_: self._refresh_room_suggestions())
        cap_spin.bind("<Return>", lambda *_: self._refresh_room_suggestions())
        cap_spin.bind("<ButtonRelease-1>", lambda *_: self.after(50, self._refresh_room_suggestions))
        cap_spin.bind("<<Increment>>", lambda *_: self.after(50, self._refresh_room_suggestions))
        cap_spin.bind("<<Decrement>>", lambda *_: self.after(50, self._refresh_room_suggestions))
        tk.Label(cap_frame, text="nguoi  (0 = hien thi tat ca)",
                 bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8)).pack(side="left")

        lbl(2, 1, "LOAI PHONG")
        room_types = sorted({str(r.room_type) for r in all_rooms if getattr(r, "status", "") == "Hoat dong"})
        type_cb = ttk.Combobox(
            card,
            textvariable=self.room_type_var,
            values=["Tat ca", *room_types],
            state="readonly",
            width=20,
        )
        type_cb.grid(row=3, column=1, sticky="w", padx=(12, 0), pady=(0, 4))
        type_cb.bind("<<ComboboxSelected>>", lambda *_: self._reset_room_suggestion_limit())

        lbl(4, 0, "CA HOC  (click de chon)")
        lbl(4, 1, "CA CON TRONG")

        # ── Visual slot picker ──────────────────────────────────────────────
        self._slot_btns: dict[str, tk.Button] = {}
        slot_grid = tk.Frame(card, bg=C_SURFACE)
        slot_grid.grid(row=5, column=0, sticky="ew")
        for c in range(3):
            slot_grid.columnconfigure(c, weight=1, uniform="slot")

        SLOT_INFO = [
            ("Ca 1", "7:00-9:30"),
            ("Ca 2", "9:35-12:00"),
            ("Ca 3", "13:00-15:30"),
            ("Ca 4", "15:35-18:00"),
            ("Ca 5", "18:15-20:45"),
        ]

        def _select_slot(slot_name: str) -> None:
            if self.slot_var.get() != slot_name:
                self.slot_var.set(slot_name)
            for sn, sb in self._slot_btns.items():
                if sn == slot_name:
                    sb.config(bg=C_PRIMARY, fg="white", highlightbackground=C_PRIMARY,
                              relief="flat", font=("Segoe UI", 9, "bold"))
                else:
                    sb.config(bg="#ffffff", fg="#64748b", highlightbackground="#e2e8f0",
                              relief="flat", font=("Segoe UI", 9))
            self._refresh_room_suggestions()
            self._update_summary()

        self._select_slot = _select_slot

        for i, (slot_name, slot_time) in enumerate(SLOT_INFO):
            row, col = divmod(i, 3)
            sb = tk.Button(
                slot_grid,
                text=f"{slot_name}\n{slot_time}",
                bg="#ffffff", fg="#64748b",
                font=("Segoe UI", 9), relief="flat",
                highlightthickness=1, highlightbackground="#e2e8f0",
                cursor="hand2", padx=6, pady=8, bd=0,
                activebackground="#f5f3ff", activeforeground="#4f46e5",
                command=lambda s=slot_name: _select_slot(s))
            sb.grid(row=row, column=col, sticky="ew", padx=3, pady=3)
            self._slot_btns[slot_name] = sb
            
            def _on_ent(e, b=sb):
                if b.cget("bg") != C_PRIMARY:
                    b.config(bg="#f5f3ff", highlightbackground="#c7d2fe", fg="#4f46e5")
            def _on_lev(e, b=sb):
                if b.cget("bg") != C_PRIMARY:
                    b.config(bg="#ffffff", highlightbackground="#e2e8f0", fg="#64748b")
            
            sb.bind("<Enter>", _on_ent)
            sb.bind("<Leave>", _on_lev)

        avail_lbl = tk.Label(card, textvariable=self.avail_var, bg=C_SUCCESS_BG,
                             fg=C_SUCCESS, font=("Segoe UI", 9, "bold"), width=32,
                             anchor="w", relief="solid", bd=1,
                             wraplength=300)
        avail_lbl.grid(row=5, column=1, sticky="w", padx=(12, 0))
        self._avail_lbl = avail_lbl

        # ── Panel goi y phong con trong chu dong (hien khi chon ngay & ca) ───
        self._room_suggest_frame = tk.Frame(card, bg=C_SURFACE)
        self._room_suggest_frame.grid(row=6, column=0, columnspan=2,
                                      sticky="ew", pady=(6, 0))
        self._room_suggest_frame.grid_remove()  # hidden until date+slot selected

        # ── Suggestion panel (shown when selected room is fully booked) ────────
        self._suggest_outer = tk.Frame(card, bg=C_SURFACE)
        self._suggest_outer.grid(row=7, column=0, columnspan=2,
                                 sticky="ew", pady=(10, 0))
        self._suggest_outer.grid_remove()   # hidden by default

        # Select default slot (must be after _room_suggest_frame is created)
        _select_slot("Ca 1")

        lbl(8, 0, "MUC DICH SU DUNG")
        self.purpose_text = tk.Text(card, width=64, height=4,
                                    relief="solid", bd=1,
                                    font=("Segoe UI", 10))
        self.purpose_text.grid(row=9, column=0, columnspan=2,
                               sticky="ew", pady=(0, 10))

        # ── Recurring Booking Section ─────────────────────────────────────────
        lbl(11, 0, "CHE DO DAT PHONG")
        mode_f = tk.Frame(card, bg=C_SURFACE)
        mode_f.grid(row=12, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Radiobutton(mode_f, text="Dat mot lan", variable=self.recurring_type, 
                        value="once", command=self._toggle_recur_ui).pack(side="left")
        ttk.Radiobutton(mode_f, text="Lap lai hang tuan", variable=self.recurring_type, 
                        value="weekly", command=self._toggle_recur_ui).pack(side="left", padx=20)
        
        self.recur_container = tk.Frame(card, bg="#ffffff", padx=15, pady=15,
                                       highlightthickness=1, highlightbackground=C_BORDER)
        self.recur_container.grid(row=13, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.recur_container.grid_remove() # Hidden by default
        
        # Days selection
        tk.Label(self.recur_container, text="Chon cac thu trong tuan:", bg="#ffffff",
                 font=("Segoe UI", 9, "bold"), fg=C_PRIMARY).pack(anchor="w")
        
        days_f = tk.Frame(self.recur_container, bg="#ffffff")
        days_f.pack(fill="x", pady=(5, 15))
        
        day_names = ["T2", "T3", "T4", "T5", "T6", "T7"]
        for i, name in enumerate(day_names):
            ttk.Checkbutton(days_f, text=name, variable=self.recur_days[i]).pack(side="left", padx=(0, 12))
            
        # Duration
        tk.Label(self.recur_container, text="Thoi han lap lai:", bg="#ffffff",
                 font=("Segoe UI", 9, "bold"), fg=C_PRIMARY).pack(anchor="w")
        
        dur_f = tk.Frame(self.recur_container, bg="#ffffff")
        dur_f.pack(fill="x", pady=5)
        
        ttk.Radiobutton(dur_f, text="Den ngay:", variable=self.recur_end_type, value="date").pack(side="left")
        
        self.recur_end_picker = DatePickerWithLabel(dur_f, self.recur_end_date)
        self.recur_end_picker.pack(side="left", padx=10)
        
        ttk.Radiobutton(dur_f, text="Hoac sau:", variable=self.recur_end_type, value="weeks").pack(side="left", padx=(10, 0))
        tk.Spinbox(dur_f, from_=1, to=24, width=4, textvariable=self.recur_num_weeks,
                   font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=5)
        tk.Label(dur_f, text="tuan", bg="#ffffff", font=("Segoe UI", 9)).pack(side="left")

        btn_f = tk.Frame(card, bg=C_SURFACE)
        btn_f.grid(row=30, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        btn(btn_f, "🚀  Gửi yêu cầu đặt phòng ngay", self._on_submit).pack(fill="x", ipady=4)

        # ── Right: room info card ─────────────────────────────────────────────
        right_outer = tk.Frame(body, bg=C_BG)
        right_outer.grid(row=0, column=1, sticky="nsew")
        
        r_outer, r_card = make_card(right_outer, padx=18, pady=18)
        r_outer.pack(fill="both", expand=True)
        
        self._room_info_frame = r_card
        self._draw_room_placeholder()

    def _build_summary_bar(self, container: tk.Frame) -> None:
        outer = tk.Frame(container, bg=C_BG)
        outer.pack(fill="x", padx=20, pady=(0, 12))

        bar = tk.Frame(outer, bg="#eef2ff", highlightthickness=1,
                       highlightbackground="#c7d2fe", padx=14, pady=10)
        bar.pack(fill="x")
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=1)
        bar.columnconfigure(2, weight=1)
        bar.columnconfigure(3, weight=2)

        def item(col: int, title: str, var: tk.StringVar, fg: str = C_TEXT) -> None:
            cell = tk.Frame(bar, bg="#eef2ff")
            cell.grid(row=0, column=col, sticky="ew", padx=(0, 12))
            tk.Label(cell, text=title.upper(), bg="#eef2ff", fg=C_MUTED,
                     font=("Segoe UI", 7, "bold")).pack(anchor="w")
            tk.Label(cell, textvariable=var, bg="#eef2ff", fg=fg,
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")

        item(0, "Phong", self.summary_room_var)
        item(1, "Ngay", self.summary_date_var)
        item(2, "Ca", self.summary_slot_var)
        item(3, "Trang thai", self.summary_status_var, C_PRIMARY)

    def _update_summary(self, status_text: str | None = None) -> None:
        display = self.room_var.get().strip()
        room_id = self._room_id_from_display(display)
        self.summary_room_var.set(room_id or "Chua chon phong")
        self.summary_date_var.set(self.date_var.get().strip() or "Chua chon ngay")
        self.summary_slot_var.set(self.slot_var.get().strip() or "Chua chon ca")
        if status_text is not None:
            self.summary_status_var.set(status_text)

    def _room_id_from_display(self, display: str) -> str:
        display = display.strip()
        if not display:
            return ""
        if display in self._room_display_map:
            return str(self._room_display_map[display])
        for sep in (" - ", " – ", " â€“ "):
            if sep in display:
                return display.split(sep)[0].strip()
        return display.split()[0].strip()

    def _toggle_recur_ui(self) -> None:
        if self.recurring_type.get() == "weekly":
            self.recur_container.grid()
        else:
            self.recur_container.grid_remove()

    def _draw_room_placeholder(self) -> None:
        for w in self._room_info_frame.winfo_children():
            w.destroy()
        # Subtle canvas background for the placeholder area
        cv = tk.Canvas(self._room_info_frame, bg="#ffffff",
                       highlightthickness=0, height=200)
        cv.pack(fill="both", expand=True)

        def _draw(_e: Any = None) -> None:
            if not cv.winfo_exists():
                return
            cv.delete("all")
            W = cv.winfo_width() or 260
            H = cv.winfo_height() or 200
            cv.create_oval(W - 80, -30, W + 20, 70, fill="#eef2ff", outline="")
            cv.create_oval(-20, H - 70, 60, H + 10, fill="#f0f9ff", outline="")
            # Icon circle
            cx, cy = W // 2, H // 2 - 20
            cv.create_oval(cx - 36, cy - 36, cx + 36, cy + 36,
                           fill="#e0e7ff", outline="#c7d2fe", width=1)
            cv.create_text(cx, cy, text="🏫",
                           font=("Segoe UI", 22))
            cv.create_text(W // 2, cy + 54,
                           text="Chon phong hoc",
                           font=("Segoe UI", 11, "bold"),
                           fill="#4f46e5")
            cv.create_text(W // 2, cy + 76,
                           text="de xem thong tin chi tiet",
                           font=("Segoe UI", 9),
                           fill="#94a3b8")

        cv.bind("<Configure>", _draw)
        cv.after(30, _draw)

    def _draw_room_info(self, room: Any) -> None:
        for w in self._room_info_frame.winfo_children():
            w.destroy()

        # Status badge color
        status_bg = "#ecfdf5" if room.status == "Hoat dong" else "#fff1f2"
        status_fg = "#059669" if room.status == "Hoat dong" else "#e11d48"

        hdr = tk.Frame(self._room_info_frame, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text="🏠", bg=C_SURFACE, font=("Segoe UI", 16)).pack(side="left")
        tk.Label(hdr, text="Thông tin phòng",
                 bg=C_SURFACE, fg=C_TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)

        def info_row(icon: str, label: str, value: str,
                     val_color: str = C_TEXT) -> None:
            row = tk.Frame(self._room_info_frame, bg=C_SURFACE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=icon, bg=C_SURFACE,
                     font=("Segoe UI", 13), width=2).pack(side="left")
            tk.Label(row, text=f"{label}: ", bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row, text=value, bg=C_SURFACE, fg=val_color,
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        info_row("🔑", "Ma phong",  room.room_id)
        info_row("📛", "Ten phong",  room.name)
        info_row("👥", "Suc chua",   f"{room.capacity} nguoi")
        info_row("📚", "Loai phong", room.room_type)

        # Status badge
        status_row = tk.Frame(self._room_info_frame, bg=C_SURFACE)
        status_row.pack(fill="x", pady=4)
        tk.Label(status_row, text="⚡", bg=C_SURFACE,
                 font=("Segoe UI", 13), width=2).pack(side="left")
        tk.Label(status_row, text="Trang thai: ", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(status_row, text=f"  {room.status}  ",
                 bg=status_bg, fg=status_fg,
                 font=("Segoe UI", 9, "bold")).pack(side="left")

        tk.Frame(self._room_info_frame, bg=C_BORDER, height=1).pack(fill="x", pady=8)

        # ── Real equipment list from database ────────────────────────────────
        eq_hdr = tk.Frame(self._room_info_frame, bg=C_SURFACE)
        eq_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(eq_hdr, text="🔧  Thiet bi trong phong:",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", anchor="w")

        # Fetch real equipment list
        equip_items: list[Any] = []
        if self.equip_ctrl is not None:
            try:
                equip_items = self.equip_ctrl.list_equipment(room_id=room.room_id)
            except Exception:
                equip_items = []

        STATUS_ICON = {
            "Hoat dong": ("✅", "#15803d"),
            "Bao tri":   ("⚠️", "#b45309"),
            "Hong":      ("❌", "#db2777"),
            "Dang sua":  ("🔨", "#0369a1"),
            "Da thanh ly": ("🗑", "#64748b"),
        }

        if equip_items:
            eq_scroll = tk.Frame(self._room_info_frame, bg="#ffffff",
                                 highlightthickness=1,
                                 highlightbackground=C_BORDER)
            eq_scroll.pack(fill="x", pady=(0, 6), ipadx=4, ipady=2)
            for eq in equip_items:
                icon, fg = STATUS_ICON.get(eq.status, ("•", "#64748b"))
                eq_row = tk.Frame(eq_scroll, bg="#ffffff")
                eq_row.pack(fill="x", padx=6, pady=1)
                tk.Label(eq_row, text=icon, bg="#ffffff",
                         font=("Segoe UI", 10), width=2).pack(side="left")
                tk.Label(eq_row, text=eq.name,
                         bg="#ffffff", fg=C_TEXT,
                         font=("Segoe UI", 9)).pack(side="left")
                tk.Label(eq_row, text=f"  [{eq.equipment_type}]",
                         bg="#ffffff", fg="#94a3b8",
                         font=("Segoe UI", 8)).pack(side="left")
                tk.Label(eq_row, text=eq.status,
                         bg="#ffffff", fg=fg,
                         font=("Segoe UI", 8, "bold")).pack(side="right", padx=4)
        elif room.equipment:
            # Modernized Fallback: show the text description as styled chips
            eq_scroll = tk.Frame(self._room_info_frame, bg="#ffffff",
                                 highlightthickness=1,
                                 highlightbackground=C_BORDER)
            eq_scroll.pack(fill="x", pady=(0, 6), ipadx=4, ipady=2)
            # Split by comma and clean up
            legacy_items = [i.strip() for i in room.equipment.split(",") if i.strip()]
            for item in legacy_items:
                eq_row = tk.Frame(eq_scroll, bg="#ffffff")
                eq_row.pack(fill="x", padx=6, pady=1)
                tk.Label(eq_row, text="🔹", bg="#ffffff",
                         font=("Segoe UI", 10), width=2).pack(side="left")
                tk.Label(eq_row, text=item,
                         bg="#ffffff", fg="#334155",
                         font=("Segoe UI", 9)).pack(side="left")
                tk.Label(eq_row, text="Hoat dong",
                         bg="#ffffff", fg="#15803d",
                         font=("Segoe UI", 8, "bold")).pack(side="right", padx=4)
        else:
            tk.Label(self._room_info_frame, text="(Chua co thiet bi nao duoc dang ky)",
                     bg=C_SURFACE, fg="#94a3b8", font=("Segoe UI", 9)).pack(anchor="w")

        # ── Action buttons for reporting ─────────────────────────────────────
        if self.equip_ctrl is not None or self.feedback_ctrl is not None:
            tk.Frame(self._room_info_frame, bg=C_BORDER, height=1).pack(fill="x", pady=(8, 4))
            
            # Row for buttons
            btn_f = tk.Frame(self._room_info_frame, bg=C_SURFACE)
            btn_f.pack(fill="x", pady=(0, 4))
            
            if self.on_navigate_to_rooms:
                tk.Button(
                    btn_f, text="🏫  Quan ly phong",
                    bg="#f1f5f9", fg="#4f46e5",
                    font=("Segoe UI", 8, "bold"),
                    relief="flat", bd=0, cursor="hand2",
                    command=self.on_navigate_to_rooms).pack(fill="x", expand=True, ipady=4)

    def _on_room_selected(self, _event: Any = None) -> None:
        display = self.room_var.get()
        room_id = self._room_id_from_display(display)
        room = self.room_ctrl.get_room(room_id)
        if room:
            self._draw_room_info(room)
        self._refresh_slots()

    def _refresh_slots(self) -> None:
        display = self.room_var.get().strip()
        room_id = self._room_id_from_display(display)
        date    = self.date_var.get().strip()

        # Hide suggestion panel until we know we need it
        self._suggest_outer.grid_remove()
        self._refresh_room_suggestions()
        self._check_warnings()

        if not room_id or not date:

            self.avail_var.set("Chon phong va ngay de xem")
            self._update_summary("Chua du thong tin")
            return

        slots = self.booking_ctrl.available_slots(room_id, date)
        selected_slot = self.slot_var.get().strip()
        self._paint_slot_buttons(slots)
        if slots:
            if selected_slot and selected_slot in slots:
                self.avail_var.set(f"San sang: {selected_slot}")
                self._update_summary("Phong dang trong")
            else:
                self.avail_var.set(f"Con trong: {', '.join(slots)}")
                self._update_summary("Hay chon ca con trong")
            self._avail_lbl.config(bg=C_SUCCESS_BG, fg=C_SUCCESS)
        else:
            self.avail_var.set("❌  Phong da duoc dat kin ca nay")
            self._update_summary("Phong da kin")
            self._avail_lbl.config(bg=C_DANGER_BG, fg=C_DANGER)

            # Build and show suggestions
            all_room_ids = [r.room_id for r in self.room_ctrl.list_rooms()
                            if r.status == "Hoat dong"]
            suggestions = self.booking_ctrl.suggest_alternatives(
                room_id=room_id,
                booking_date=date,
                slot=self.slot_var.get().strip(),
                all_room_ids=all_room_ids,
                days_ahead=7,
            )
            self._build_suggestion_panel(suggestions, date)

    # ── Suggestion panel builder ──────────────────────────────────────────────
    def _paint_slot_buttons(self, available_slots: list[str]) -> None:
        selected_slot = self.slot_var.get().strip()
        for slot_name, button in self._slot_btns.items():
            is_available = slot_name in available_slots
            is_selected = slot_name == selected_slot
            if is_selected and is_available:
                button.config(text=f"{slot_name}\nDang chon")
                button.config(bg=C_PRIMARY, fg="white", highlightbackground=C_PRIMARY,
                              activebackground=C_PRIMARY,
                              font=("Segoe UI", 9, "bold"))
            elif is_available:
                button.config(text=f"{slot_name}\nTrong")
                button.config(bg="#ffffff", fg=C_TEXT, highlightbackground=C_BORDER,
                              activebackground="#eef2ff",
                              font=("Segoe UI", 9))
            else:
                button.config(text=f"{slot_name}\nDa kin")
                button.config(bg="#ffffff", fg="#94a3b8", highlightbackground=C_BORDER,
                              activebackground="#ffffff",
                              font=("Segoe UI", 9))

    def _reset_room_suggestion_limit(self) -> None:
        self._room_suggestion_limit = 6
        self._refresh_room_suggestions()

    def _more_room_suggestions(self, total: int) -> None:
        scroll_y = self._current_scroll_y()
        self._room_suggestion_limit = min(total, self._room_suggestion_limit + 6)
        self._refresh_room_suggestions()
        self._restore_scroll_y(scroll_y)

    def _current_scroll_y(self) -> float:
        try:
            return float(self._canvas.yview()[0])
        except Exception:
            return 0.0

    def _restore_scroll_y(self, y: float) -> None:
        def _restore() -> None:
            try:
                self.update_idletasks()
                self._canvas.yview_moveto(y)
            except Exception:
                pass

        self.after_idle(_restore)
        self.after(50, _restore)

    def _rank_available_rooms(self, rooms: list[Any], min_cap: int) -> list[Any]:
        selected_type = self.room_type_var.get().strip()
        if selected_type and selected_type != "Tat ca":
            rooms = [r for r in rooms if str(getattr(r, "room_type", "")) == selected_type]

        target = max(0, min_cap)
        if target > 0:
            return sorted(rooms, key=lambda r: (abs(int(r.capacity) - target), int(r.capacity), str(r.room_id)))
        return sorted(rooms, key=lambda r: (int(r.capacity), str(r.room_id)))

    def _build_suggestion_panel(self, suggestions: dict[str, Any], base_date: str) -> None:
        """Rebuild and show the suggestion panel inside _suggest_outer."""
        outer = self._suggest_outer
        outer.config(height=220)
        outer.grid_propagate(False)
        for w in outer.winfo_children():
            w.destroy()

        other_rooms  = suggestions.get("other_rooms",  [])
        other_slots  = suggestions.get("other_slots",  [])
        other_rooms = other_rooms[:6]

        if not other_rooms and not other_slots:
            # Nothing to suggest at all
            tk.Label(outer,
                     text="⚠  Khong tim thay phong trong trong 7 ngay toi. "
                          "Vui long thu lai sau.",
                     bg="#fef9c3", fg="#92400e",
                     font=("Segoe UI", 9), wraplength=560,
                     relief="solid", bd=1).pack(fill="x", ipadx=10, ipady=6)
            outer.grid()
            return

        # Container card
        card = tk.Frame(outer, bg="#eff6ff",
                        highlightthickness=1,
                        highlightbackground="#bfdbfe")
        card.pack(fill="x", ipadx=4, ipady=4)

        # Header
        hdr = tk.Frame(card, bg="#eff6ff")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(hdr, text="💡  Goi y phong / lich con trong",
                 bg="#eff6ff", fg="#1d4ed8",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="(Click de tu dong dien vao form)",
                 bg="#eff6ff", fg="#60a5fa",
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

        # ── Section 1: other rooms same date+slot ─────────────────────────────
        if other_rooms:
            sec1 = tk.Frame(card, bg="#eff6ff")
            sec1.pack(fill="x", padx=12, pady=(0, 8))
            tk.Label(sec1,
                     text=f"🏫  Phong khac con trong vao {base_date}  "
                          f"{self.slot_var.get()}:",
                     bg="#eff6ff", fg="#1e40af",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

            chips = tk.Frame(sec1, bg="#eff6ff")
            chips.pack(fill="x")
            for c in range(3):
                chips.columnconfigure(c, weight=1, uniform="alt_room")
            for idx, (room_id, slot) in enumerate(other_rooms):
                # Look up display name
                display_name = next(
                    (k for k, v in self._room_display_map.items()
                     if v == room_id), room_id)
                room_obj = self.room_ctrl.get_room(room_id)
                room_meta = ""
                if room_obj:
                    room_meta = f" | {room_obj.capacity} cho | {room_obj.room_type}"

                chip = tk.Button(
                    chips,
                    text=f"{room_id}{room_meta}",
                    bg="#dbeafe", fg="#1d4ed8",
                    font=("Segoe UI", 8, "bold"),
                    relief="flat", bd=0, cursor="hand2",
                    activebackground="#bfdbfe",
                    command=lambda rid=room_id, dn=display_name, s=slot:
                        self._apply_suggestion(dn, None, s),
                    anchor="w",
                    padx=8,
                    pady=4,
                )
                r_idx, c_idx = divmod(idx, 3)
                chip.grid(row=r_idx, column=c_idx, sticky="ew", padx=3, pady=3)

        # ── Divider ───────────────────────────────────────────────────────────
        if other_rooms and other_slots:
            tk.Frame(card, bg="#bfdbfe", height=1).pack(
                fill="x", padx=12, pady=4)

        # ── Section 2: same room, other dates/slots ───────────────────────────
        if other_slots:
            sec2 = tk.Frame(card, bg="#eff6ff")
            sec2.pack(fill="x", padx=12, pady=(0, 10))
            tk.Label(sec2,
                     text=f"📅  Phong nay ({self._room_id_from_display(self.room_var.get())}) "
                          f"con trong vao:",
                     bg="#eff6ff", fg="#1e40af",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

            # Group by date for readability
            from collections import defaultdict
            by_date: dict[str, list[str]] = defaultdict(list)
            for date_str, s in other_slots:   # tat ca slot con trong
                by_date[date_str].append(s)

            grid_f = tk.Frame(sec2, bg="#eff6ff")
            grid_f.pack(anchor="w")
            for col, (date_str, slots_list) in enumerate(
                    sorted(by_date.items())[:5]):
                try:
                    d = dt.date.fromisoformat(date_str)
                    day_label = d.strftime("%d/%m\n%a").replace(
                        "Mon","T2").replace("Tue","T3").replace(
                        "Wed","T4").replace("Thu","T5").replace(
                        "Fri","T6").replace("Sat","T7").replace("Sun","CN")
                except Exception:
                    day_label = date_str

                day_col = tk.Frame(grid_f, bg="#eff6ff")
                day_col.grid(row=0, column=col, padx=(0, 10), pady=2,
                             sticky="n")

                tk.Label(day_col, text=day_label,
                         bg="#dbeafe", fg="#1d4ed8",
                         font=("Segoe UI", 8, "bold"),
                         width=7, relief="flat",
                         anchor="center").pack(pady=(0, 3))

                for s in slots_list:
                    display = self.room_var.get()
                    tk.Button(
                        day_col,
                        text=s,
                        bg="#f0fdf4", fg="#15803d",
                        font=("Segoe UI", 8),
                        relief="flat", bd=0,
                        width=7, cursor="hand2",
                        activebackground="#dcfce7",
                        command=lambda ds=date_str, sl=s, dp=display:
                            self._apply_suggestion(dp, ds, sl),
                    ).pack(pady=1)

        outer.grid()

    def _refresh_room_suggestions(self) -> None:
        """Hien thi tat ca phong con trong theo ngay, ca hoc & suc chua toi thieu."""
        if not hasattr(self, '_room_suggest_frame'):
            return
        frame = self._room_suggest_frame
        
        frame.config(height=260)
        frame.grid_propagate(False)
        
        for w in frame.winfo_children():
            w.destroy()

        date = self.date_var.get().strip()
        slot = self.slot_var.get().strip()

        if not date or not slot:
            frame.grid_remove()
            return
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            frame.grid_remove()
            return

        try:
            min_cap = int(self.capacity_var.get() or "0")
        except ValueError:
            min_cap = 0

        free_rooms = self.room_ctrl.get_available_rooms_by_capacity(
            self.booking_ctrl, date, slot, min_capacity=min_cap
        )
        free_rooms = self._rank_available_rooms(free_rooms, min_cap)

        if not free_rooms:
            notice = tk.Frame(frame, bg="#fdf2f8", highlightthickness=1,
                              highlightbackground="#fbcfe8")
            notice.pack(fill="x", pady=(4, 0))
            cap_msg = f"  (suc chua ≥ {min_cap})" if min_cap > 0 else ""
            tk.Label(notice,
                     text=f"⚠️  Khong co phong trong nao vao {date}  –  {slot}{cap_msg}",
                     bg="#fdf2f8", fg="#db2777",
                     font=("Segoe UI", 9, "bold")).pack(padx=12, pady=7)
            frame.grid()
            return

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(frame, bg="#eff6ff", highlightthickness=1,
                       highlightbackground="#bfdbfe")
        hdr.pack(fill="x", pady=(4, 0))

        hdr_left = tk.Frame(hdr, bg="#eff6ff")
        hdr_left.pack(side="left", padx=12, pady=3)
        tk.Label(hdr_left, text="🟢  Phong con trong:",
                 bg="#eff6ff", fg="#1d4ed8",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(hdr_left, text=f"  {date}  –  {slot}",
                 bg="#eff6ff", fg="#2563eb",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        if min_cap > 0:
            tk.Label(hdr_left, text=f"  •  suc chua ≥ {min_cap} nguoi",
                     bg="#eff6ff", fg="#7c3aed",
                     font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(hdr, text=f"✅ {len(free_rooms)} phong  •  Click de chon nhanh",
                 bg="#eff6ff", fg="#60a5fa",
                 font=("Segoe UI", 8)).pack(side="right", padx=12)

        # ── Chips grid (prevents horizontal expansion squeezing right sidebar) ──
        visible_rooms = free_rooms[:self._room_suggestion_limit]
        hidden_count = max(0, len(free_rooms) - len(visible_rooms))

        chips_outer = tk.Frame(frame, bg="#ffffff", highlightthickness=1,
                               highlightbackground="#e2e8f0", height=210)
        chips_outer.pack(fill="both", expand=True)
        chips_outer.pack_propagate(False)

        chips_canvas = tk.Canvas(chips_outer, bg="#ffffff", highlightthickness=0)
        chips_scroll = ttk.Scrollbar(chips_outer, orient="vertical", command=chips_canvas.yview)
        chips_canvas.configure(yscrollcommand=chips_scroll.set)
        chips_canvas.pack(side="left", fill="both", expand=True)
        chips_scroll.pack(side="right", fill="y")

        grid_f = tk.Frame(chips_canvas, bg="#ffffff", padx=10, pady=8)
        grid_window = chips_canvas.create_window((0, 0), window=grid_f, anchor="nw")

        def _sync_chips_scroll(_event: Any = None) -> None:
            chips_canvas.configure(scrollregion=chips_canvas.bbox("all"))
            chips_canvas.itemconfig(grid_window, width=chips_canvas.winfo_width())

        grid_f.bind("<Configure>", _sync_chips_scroll)
        chips_canvas.bind("<Configure>", _sync_chips_scroll)

        def _wheel_chips(event: tk.Event) -> str:
            chips_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        chips_canvas.bind("<Enter>", lambda *_: chips_canvas.bind_all("<MouseWheel>", _wheel_chips))
        chips_canvas.bind("<Leave>", lambda *_: chips_canvas.unbind_all("<MouseWheel>"))
        
        MAX_COLS = 3
        for i in range(MAX_COLS):
            grid_f.columnconfigure(i, weight=1, uniform="chip")
            
        for idx, r in enumerate(visible_rooms):
            display = f"{r.room_id} - {r.name} (SC: {r.capacity})"
            row, col = divmod(idx, MAX_COLS)
            main_equipment = str(getattr(r, "equipment", "")).split(",")[0].strip() or "Thiet bi co ban"

            chip = tk.Button(
                grid_f,
                text=f"{r.room_id} | {r.capacity} cho | {r.room_type}\n{main_equipment}",
                bg="#ffffff", fg="#1d4ed8",
                font=("Segoe UI", 8, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground="#dbeafe", activeforeground="#1d4ed8",
                command=lambda dn=display, s=slot: self._apply_suggestion(dn, None, s),
                justify="left", anchor="w", padx=10, pady=5,
                height=2,
            )
            chip.grid(row=row, column=col, sticky="ew", padx=4, pady=3)
            chip.bind("<Enter>", lambda _e, b=chip: b.config(bg="#dbeafe"))
            chip.bind("<Leave>", lambda _e, b=chip: b.config(bg="#ffffff"))

        next_row = (len(visible_rooms) + MAX_COLS - 1) // MAX_COLS
        if hidden_count:
            tk.Button(
                grid_f,
                text=f"Xem them {min(6, hidden_count)} phong ({hidden_count} con lai)",
                bg="#eef2ff", fg=C_PRIMARY,
                font=("Segoe UI", 8, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground="#e0e7ff", activeforeground=C_PRIMARY,
                command=lambda total=len(free_rooms): self._more_room_suggestions(total),
                padx=10, pady=5,
            ).grid(row=next_row, column=0, columnspan=MAX_COLS, pady=(8, 0), sticky="ew")

        frame.grid()

    def _check_warnings(self) -> None:
        """Check for deadline and conflict warnings."""
        if not hasattr(self, 'warning_f'): return
        
        for w in self.warning_f.winfo_children():
            w.destroy()
        
        date_str = self.date_var.get().strip()
        slot = self.slot_var.get().strip()
        has_warning = False
        
        try:
            today = dt.date.today()
            target = dt.date.fromisoformat(date_str)
            days_diff = (target - today).days
            
            # 1. Deadline warning (Friendly Note)
            if 0 <= days_diff < 3:
                f = tk.Frame(self.warning_f, bg="#eff6ff", highlightthickness=1, highlightbackground="#bfdbfe")
                f.pack(fill="x", pady=2)
                tk.Label(f, text="ℹ️ Lưu ý: Booking trong vòng 3 ngày có thể không được phê duyệt kịp!",
                         bg="#eff6ff", fg="#1e40af", font=("Segoe UI", 9, "bold"),
                         anchor="w", justify="left", wraplength=1200).pack(fill="x", padx=10, pady=5)
                has_warning = True

                
            # 2. Conflict warning (Quick Win 4)
            if slot:
                conflict = self.booking_ctrl.check_user_conflict(self.current_user.user_id, date_str, slot)
                if conflict:
                    f = tk.Frame(self.warning_f, bg="#fef2f2", highlightthickness=1, highlightbackground="#fecaca")
                    f.pack(fill="x", pady=2)
                    tk.Label(f, text=f"🔴 Chú ý: Bạn đã có lịch vào ca này ({conflict.room_id} - {conflict.purpose[:30]}...)",
                             bg="#fef2f2", fg="#dc2626", font=("Segoe UI", 9, "bold"),
                             anchor="w", justify="left", wraplength=1200).pack(fill="x", padx=10, pady=5)
                    has_warning = True
        except Exception:
            pass
            
        if has_warning:
            self.warning_f.pack(fill="x", padx=20, pady=(0, 10))
        else:
            self.warning_f.pack_forget()

    def _apply_suggestion(self, room_display: str,

                          date_str: str | None, slot: str) -> None:
        """Auto-fill form fields from a suggestion chip click."""
        scroll_y = self._current_scroll_y()
        opened_limit = self._room_suggestion_limit
        old_slot = self.slot_var.get()

        self._suppress_suggestion_limit_reset = True
        try:
            if room_display and self.room_var.get() != room_display:
                self.room_var.set(room_display)
                # Update room info card
                room_id = self._room_display_map.get(
                    room_display, self._room_id_from_display(room_display))
                room = self.room_ctrl.get_room(room_id)
                if room:
                    self._draw_room_info(room)
            if date_str and self.date_var.get() != date_str:
                self.date_var.set(date_str)
                try:
                    self._date_entry.set_date(dt.date.fromisoformat(date_str))  # type: ignore[attr-defined]
                except Exception:
                    pass
            if slot:
                if hasattr(self, "_select_slot"):
                    self._select_slot(slot)
                elif self.slot_var.get() != slot:
                    self.slot_var.set(slot)
        finally:
            self._suppress_suggestion_limit_reset = False

        self._room_suggestion_limit = max(opened_limit, self._room_suggestion_limit)
        self._refresh_slots()
        if slot == old_slot and date_str is None:
            self._room_suggestion_limit = max(opened_limit, self._room_suggestion_limit)
            self._refresh_room_suggestions()
        self._restore_scroll_y(scroll_y)

    def _on_submit(self) -> None:
        """Xử lý sự kiện khi người dùng nhấn nút Đặt phòng."""
        display = self.room_var.get().strip()
        room_id = self._room_id_from_display(display)
        if not room_id:
            confirm_dialog(self, "Lỗi", "Hãy chọn phòng học.", kind="danger", cancel_text=None)
            return

        purpose = self.purpose_text.get("1.0", "end").strip()
        if not purpose:
            confirm_dialog(self, "Lỗi", "Hãy nhập mục đích sử dụng.", kind="danger", cancel_text=None)
            return

        slot = self.slot_var.get().strip()
        if not slot:
            confirm_dialog(self, "Lỗi", "Hãy chọn ca học.", kind="danger", cancel_text=None)
            return

        try:
            if self.recurring_type.get() == "once":
                # Single booking
                booking_date = self.date_var.get().strip()
                self.booking_ctrl.create_booking(
                    self.current_user, room_id, booking_date, slot, purpose
                )
                msg = f"Yêu cầu đặt phòng {room_id} đã được gửi thành công."
            else:
                # Recurring booking
                selected_days = [d for d, var in self.recur_days.items() if var.get()]
                if not selected_days:
                    confirm_dialog(self, "Lỗi", "Hãy chọn ít nhất một thứ trong tuần.", kind="danger", cancel_text=None)
                    return
                
                end_date = self.recur_end_date.get() if self.recur_end_type.get() == "date" else ""
                num_weeks = int(self.recur_num_weeks.get()) if self.recur_end_type.get() == "weeks" else 0
                
                ids = self.booking_ctrl.create_recurring_booking(
                    user=self.current_user,
                    room_id=room_id,
                    initial_date=self.date_var.get(),
                    slot=slot,
                    days_of_week=selected_days,
                    end_date=end_date,
                    num_weeks=num_weeks,
                    purpose=purpose
                )

                msg = f"Đã gửi thành công {len(ids)} yêu cầu đặt phòng theo chu kỳ."

            confirm_dialog(self, "Thành công", msg, kind="primary", cancel_text=None)
            
            # Reset form
            self.purpose_text.delete("1.0", "end")
            
            # Refresh other tabs
            if hasattr(self, 'history_tab'):
                self.history_tab.refresh()
            if hasattr(self, 'calendar_tab'):
                self.calendar_tab._refresh_calendar()

            if self.on_booking_created:
                self.on_booking_created()

                
        except Exception as e:
            confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)
