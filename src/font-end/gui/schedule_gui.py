# schedule_gui.py  –  schedule view (7-day × 5-shift visual grid)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_DARK, C_TEXT, C_PRIMARY, C_PRIMARY_H, C_MUTED,
                       F_TITLE, F_SECTION, F_BODY_B, page_header, btn, make_card)
from gui.class_student_list_gui import ClassStudentListDialog


# Fallback constants if not imported
if 'C_DARK' not in globals(): C_DARK = "#0f172a"
if 'C_TEXT' not in globals(): C_TEXT = "#1e293b"

# Unified naming for consistency
MIN_SLOT_H = 95
COL_WIDTH = 135

DAYS      = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
SLOTS_LBL = [
    "Ca 1\n07:00-09:30",
    "Ca 2\n09:35-12:00",
    "Ca 3\n13:00-15:30",
    "Ca 4\n15:35-18:00",
    "Ca 5\n18:15-20:45",
]
SLOT_KEYS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

# Modern palette with higher contrast
CELL_COLORS = {
    "Da duyet":  ("#dcfce7", "#15803d"),
    "Cho duyet": ("#fef3c7", "#b45309"),
    "Tu choi":   ("#fdf2f8", "#db2777"),
    "Lich day":  ("#e0f2fe", "#0369a1"),
}
CELL_ACCENT = {
    "Da duyet":  "#16a34a",
    "Cho duyet": "#f59e0b",
    "Tu choi":   "#ec4899",
}

LEGEND = [
    ("Đã duyệt",  "#dcfce7", "#15803d"),
    ("Chờ duyệt", "#fef3c7", "#b45309"),
    ("Từ chối",   "#fdf2f8", "#db2777"),
    ("Lịch dạy",  "#e0f2fe", "#0369a1"),
    ("Trống",     "#ffffff", "#94a3b8"),
]

# Subtle grid border color
GRID_BORDER = "#e2e8f0" 

def _cell_tooltip(cell: tk.Widget, entries: "list[tuple[str, str]]",
                   date_str: str, slot_key: str) -> None:
    """Attach a rich hover tooltip to a busy schedule cell."""
    tip: list[tk.Toplevel | None] = [None]

    def _show(_: object = None) -> None:
        if tip[0] or not cell.winfo_exists():
            return
        x = cell.winfo_rootx() + cell.winfo_width() + 4
        y = cell.winfo_rooty()
        popup = tk.Toplevel(cell)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)  # type: ignore[arg-type]
        popup.configure(bg="#1e1b4b")

        frame = tk.Frame(popup, bg="#1e1b4b", padx=12, pady=10,
                         highlightthickness=1, highlightbackground="#4f46e5")
        frame.pack()

        tk.Label(frame, text=f"📅  {date_str}  •  {slot_key}",
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        STATUS_CHIP: dict[str, tuple[str, str]] = {
            "Da duyet":  ("#dcfce7", "#15803d"),
            "Cho duyet": ("#fef3c7", "#b45309"),
            "Tu choi":   ("#fdf2f8", "#db2777"),
            "Lich day":  ("#e0f2fe", "#0369a1"),
        }
        for label, status, is_mine, source_id in entries[:5]:

            chip_bg, chip_fg = STATUS_CHIP.get(status, ("#f1f5f9", "#475569"))
            if is_mine: chip_bg, chip_fg = ("#4f46e5", "white")
            
            row_f = tk.Frame(frame, bg="#272165")
            row_f.pack(fill="x", pady=1)
            
            prefix = "⭐ " if is_mine else "  "
            tk.Label(row_f, text=f"{prefix}{label[:28]}",
                     bg="#272165", fg="#e0e7ff",
                     font=("Segoe UI", 9, "bold" if is_mine else "normal")).pack(side="left")
            tk.Label(row_f, text=f"  {'CỦA TÔI' if is_mine else status}  ",
                     bg=chip_bg, fg=chip_fg,
                     font=("Segoe UI", 7, "bold")).pack(side="right", padx=4)

        if len(entries) > 5:
            tk.Label(frame, text=f"  + {len(entries) - 5} lich khac...",
                     bg="#1e1b4b", fg="#6366f1",
                     font=("Segoe UI", 7, "italic")).pack(anchor="w", pady=(4, 0))

        popup.update_idletasks()
        pw = popup.winfo_width()
        try:
            sw = cell.winfo_screenwidth()
            if x + pw > sw - 10:
                x = cell.winfo_rootx() - pw - 4
        except Exception:
            pass
        popup.geometry(f"+{x}+{y}")
        tip[0] = popup

    def _hide(_: object = None) -> None:
        if tip[0]:
            try:
                tip[0].destroy()
            except Exception:
                pass
            tip[0] = None

    cell.bind("<Enter>", _show, add="+")
    cell.bind("<Leave>", _hide, add="+")
    cell.bind("<Destroy>", _hide, add="+")

VN_MONTHS = ["", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5",
             "Tháng 6", "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10",
             "Tháng 11", "Tháng 12"]


class ScheduleFrame(tk.Frame):
    def __init__(self, master, booking_controller, room_controller, current_user=None): # type: ignore
        super().__init__(master, bg=C_BG) # type: ignore
        self.booking_ctrl  = booking_controller
        self.room_ctrl     = room_controller
        self.current_user  = current_user
        self._week_offset  = 0
        self._week_lbl_var = tk.StringVar()
        self._v_search     = tk.StringVar()
        self._compact_mode = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        # ── Page Header
        header = page_header(self, "Lịch biểu phòng học", "📆")
        header.pack(fill="x")
        
        # ── Toolbar: Navigation + Actions
        toolbar_outer, toolbar = make_card(self, padx=16, pady=6, shadow=True)
        toolbar_outer.pack(fill="x", padx=20, pady=(0, 10))

        # Left: Navigation
        nav_f = tk.Frame(toolbar, bg=C_SURFACE)
        nav_f.pack(side="left")
        
        btn(nav_f, "«", self._prev_week, variant="ghost", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 2))
        tk.Label(nav_f, textvariable=self._week_lbl_var, bg=C_SURFACE,
                 fg=C_DARK, font=("Segoe UI", 10, "bold"),
                 width=22, anchor="center").pack(side="left")
        btn(nav_f, "»", self._next_week, variant="ghost", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(2, 10))
        
        btn(nav_f, "Hôm nay", self._go_today, variant="primary", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        
        self._offset_badge = tk.Label(nav_f, text="", bg="#eef2ff",
                                      fg=C_PRIMARY, font=("Segoe UI", 8, "bold"),
                                      padx=8, pady=1)
        self._offset_badge.pack(side="left", padx=5)

        # Right: Filters
        filter_f = tk.Frame(toolbar, bg=C_SURFACE)
        filter_f.pack(side="right")

        # 🔍 Search Bar
        from gui.theme import search_box
        s_box = search_box(filter_f, self._v_search, placeholder="Tìm môn, giảng viên...", 
                           width=18, on_type=self._refresh)
        s_box.pack(side="left", padx=(0, 12))
        
        # 📏 Compact Toggle
        ct = ttk.Checkbutton(filter_f, text="Gọn", variable=self._compact_mode, 
                             command=self._refresh)
        ct.pack(side="left", padx=(0, 10))

        tk.Label(filter_f, text="Phòng:", bg=C_SURFACE, fg=C_TEXT, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))
        self._v_room = tk.StringVar(value="Tất cả phòng")
        rooms = ["Tất cả phòng"] + [r.room_id for r in self.room_ctrl.list_rooms()]
        cb = ttk.Combobox(filter_f, textvariable=self._v_room, values=rooms,
                          state="readonly", font=("Segoe UI", 9), width=14)
        cb.pack(side="left", padx=(0, 8))
        cb.bind("<<ComboboxSelected>>", lambda _: self._refresh())
        
        btn(filter_f, "", self._refresh, variant="ghost", icon="🔄").pack(side="left")

            
        # ── Week summary stats bar (Fixed at bottom)
        self._stats_bar = tk.Frame(self, bg=C_SURFACE)
        self._stats_bar.pack(side="bottom", fill="x", padx=20, pady=(0, 10))




        # ── Scrollable grid canvas: well-defined frame
        grid_outer, grid_content = make_card(self, padx=0, pady=0, shadow=True)
        grid_outer.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 15))

        canvas = tk.Canvas(grid_content, bg=C_BG, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        grid_content.grid_rowconfigure(0, weight=1)
        grid_content.grid_columnconfigure(0, weight=1)
        
        self._grid_frame = tk.Frame(canvas, bg=C_BG)
        self._canvas_win = canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")

        # ── Scroll & Pan Logic
        def _on_mousewheel(e):
            canvas.yview_scroll(-1*(e.delta//120), "units")

        def _get_canvas_pos(e):
            cx = e.x_root - canvas.winfo_rootx()
            cy = e.y_root - canvas.winfo_rooty()
            return cx, cy

        def _on_pan_start(e):
            cx, cy = _get_canvas_pos(e)
            canvas.scan_mark(cx, cy)
            canvas.config(cursor="fleur")

        def _on_pan_move(e):
            cx, cy = _get_canvas_pos(e)
            canvas.scan_dragto(cx, cy, gain=1)

        def _on_pan_stop(e):
            canvas.config(cursor="")

        def _bind_controls(widget):
            # Bind to this widget
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            widget.bind("<ButtonPress-1>", _on_pan_start, add="+")
            widget.bind("<B1-Motion>", _on_pan_move, add="+")
            widget.bind("<ButtonRelease-1>", _on_pan_stop, add="+")
            # Bind to children recursively
            for child in widget.winfo_children():
                _bind_controls(child)

        def _on_canvas_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if canvas.winfo_width() > self._grid_frame.winfo_reqwidth():
                canvas.itemconfig(self._canvas_win, width=canvas.winfo_width())

        self._grid_frame.bind("<Configure>", _on_canvas_cfg)
        canvas.bind("<Configure>", _on_canvas_cfg)
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self._refresh()
        
        # Apply recursive binding to everything in the grid
        self.after(150, lambda: _bind_controls(self._grid_frame))
        # Also bind to the canvas itself
        _bind_controls(canvas)

    def _prev_week(self):
        self._week_offset -= 1
        self._refresh()

    def _next_week(self):
        self._week_offset += 1
        self._refresh()

    def _go_today(self):
        self._week_offset = 0
        self._refresh()

    def _update_week_label(self):
        mon, sun = self.booking_ctrl.week_date_range(self._week_offset) # type: ignore
        m1, m2 = VN_MONTHS[mon.month], VN_MONTHS[sun.month] # type: ignore
        if mon.month == sun.month: # type: ignore
            label = f"Tuần  {mon.day} - {sun.day}  {m1}  {mon.year}" # type: ignore
        else:
            label = f"{mon.day} {m1} - {sun.day} {m2}  {mon.year}" # type: ignore
        self._week_lbl_var.set(label)
        if self._week_offset == 0:
            self._offset_badge.config(text="* Tuần này", bg="#dcfce7", fg="#15803d")
        elif self._week_offset == -1:
            self._offset_badge.config(text="Tuần trước", bg="#fef3c7", fg="#b45309")
        elif self._week_offset == 1:
            self._offset_badge.config(text="Tuần sau", bg="#dbeafe", fg="#1d4ed8")
        elif self._week_offset < 0:
            self._offset_badge.config(text=f"{abs(self._week_offset)} tuần trước",
                                      bg="#fef3c7", fg="#b45309")
        else:
            self._offset_badge.config(text=f"+{self._week_offset} tuần",
                                      bg="#dbeafe", fg="#1d4ed8")

    def _show_class_student_list(self, date_str: str, day_name: str, 
                                 slot_key: str, class_id: str) -> None:
        """
        Show student list for clicked class/booking.
        Called when user clicks on a schedule cell.
        """
        try:
            # Get class details from controller
            class_obj = self.booking_ctrl.get_class(class_id)
            if not class_obj:
                return
            
            # Get enrollment list
            students = self.booking_ctrl.get_enrollment_list(class_id)
            
            # Prepare class info dict
            class_info = {
                "class_id": class_id,
                "name": getattr(class_obj, 'name', getattr(class_obj, 'purpose', 'Lớp học')),
                "time": f"{slot_key} ({getattr(class_obj, 'time_range', '')})",
                "room": getattr(class_obj, 'room_id', '')
            }
            
            # Show dialog
            ClassStudentListDialog(
                self,
                class_info=class_info,
                students=students,
                on_student_select=self._on_student_selected
            )
        except Exception as e:
            print(f"Error showing class details: {e}")
            import traceback
            traceback.print_exc()

    def _on_student_selected(self, student: dict[str, str]) -> None:
        """Called when a student is selected from the list."""
        print(f"Selected: {student.get('ho_dem', '')} {student.get('ten', '')} "
              f"({student.get('ma_so', '')})")


    def _show_cell_detail(self, entries: "list[tuple[str, str]]", date_str: str,
                          day_name: str, slot_label: str) -> None:
        """Show a popup with booking details for a clicked schedule cell."""
        import tkinter as tk
        root = self.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.title(f"Chi tiết lịch – {day_name}  {slot_label.split(chr(10))[0]}")
        dlg.resizable(False, False)
        dlg.configure(bg="#f8fafc")
        dlg.transient(root)  # type: ignore
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#1e1b4b", padx=20, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text=f"📆  {day_name}  –  {slot_label.split(chr(10))[0]}",
                 bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(hdr, text=f"Ngày: {date_str}",
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(dlg, bg="#f8fafc", padx=18, pady=14)
        body.pack(fill="x")

        STATUS_COLORS = {
            "Da duyet":  ("#dcfce7", "#15803d"),
            "Cho duyet": ("#fef3c7", "#b45309"),
            "Tu choi":   ("#fdf2f8", "#db2777"),
            "Lich day":  ("#e0f2fe", "#0369a1"),
        }
        for label, status, is_mine, source_id in entries:

            sbg, sfg = STATUS_COLORS.get(status, ("#f1f5f9", "#475569"))
            if is_mine: sbg, sfg = ("#4f46e5", "white")
            
            row = tk.Frame(body, bg="#ffffff",
                           highlightthickness=1, highlightbackground="#4f46e5" if is_mine else "#e2e8f0")
            row.pack(fill="x", pady=4)
            
            prefix = "⭐ [Của tôi] " if is_mine else ""
            tk.Label(row, text=f"  {prefix}{label}", bg="#ffffff", fg="#1e1b4b" if is_mine else "#1e293b",
                     font=("Segoe UI", 10, "bold" if is_mine else "normal"), anchor="w").pack(
                side="left", padx=8, pady=8, fill="x", expand=True)
            tk.Label(row, text=f"  {'SỞ HỮU' if is_mine else status}  ",
                     bg=sbg, fg=sfg,
                     font=("Segoe UI", 8, "bold")).pack(
                side="right", padx=8, pady=8)

        tk.Button(dlg, text="  Đóng  ", bg="#4f46e5", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", padx=12, pady=6,
                  activebackground="#4338ca",
                  command=dlg.destroy).pack(pady=(0, 14))

        dlg.update_idletasks()
        rx = root.winfo_x() + root.winfo_width() // 2
        ry = root.winfo_y() + root.winfo_height() // 2
        dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")

    def _refresh(self):
        self._update_week_label()
        for w in self._grid_frame.winfo_children():
            if w != getattr(self, "_stats_bar", None):
                w.destroy()
        
        room_filter = self._v_room.get()
        from gui.theme import get_q
        search_q = get_q(self._v_search, "Tìm môn, giảng viên...")

        
        is_compact = self._compact_mode.get()
        cell_min_h = 85 if is_compact else 125
        col_min_w = 145 if is_compact else 170

        schedule_rows = self.booking_ctrl.build_schedule(self._week_offset) # type: ignore

        today = dt.date.today()
        mon, _ = self.booking_ctrl.week_date_range(self._week_offset) # type: ignore
        today_col = None
        if mon <= today <= mon + dt.timedelta(days=6):
            today_col = today.weekday()

        # Detect current slot highlight
        now_time = dt.datetime.now().strftime("%H:%M")
        SLOT_TIME_RANGES = {
            "Ca 1": ("07:00", "09:30"), "Ca 2": ("09:35", "12:00"),
            "Ca 3": ("13:00", "15:30"), "Ca 4": ("15:35", "18:00"),
            "Ca 5": ("18:15", "20:45"),
        }
        active_slot_key = None
        if self._week_offset == 0:
            for k, (st, en) in SLOT_TIME_RANGES.items():
                if st <= now_time <= en:
                    active_slot_key = k
                    break

        lookup = {}
        for s in schedule_rows: # type: ignore
            if room_filter != "Tất cả phòng" and s.room_id != room_filter: # type: ignore
                continue
            if search_q and search_q not in s.label.lower() and search_q not in s.room_id.lower():
                continue
            key = (s.weekday, s.slot) # type: ignore
            is_mine = (self.current_user and s.user_id == self.current_user.user_id)
            lookup.setdefault(key, []).append((s.label, s.status, is_mine, s.source_id)) # type: ignore



        gf = self._grid_frame
        gf.configure(padx=10, pady=10)

        # ── Corner cell (Balanced size)
        tk.Label(gf, text="CA / NGÀY", bg="#1e293b", fg="#64748b",
                 font=("Segoe UI", 9 if is_compact else 10, "bold"),
                 width=12 if is_compact else 16, height=3 if is_compact else 4, 
                 relief="flat").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        # ── Day Headers
        for ci, day in enumerate(DAYS):
            date_for_col = mon + dt.timedelta(days=ci) # type: ignore
            date_str = f"{date_for_col.day}/{date_for_col.month}" # type: ignore
            is_today = (ci == today_col)
            
            hdr_bg = "#4f46e5" if is_today else "#1e293b"
            accent_fg = "#c7d2fe" if is_today else "#94a3b8"
            
            hdr_f = tk.Frame(gf, bg=hdr_bg, padx=8, pady=8 if is_compact else 12)
            hdr_f.grid(row=0, column=ci + 1, sticky="nsew", padx=1, pady=1)
            gf.columnconfigure(ci + 1, minsize=col_min_w, weight=1)

            tk.Label(hdr_f, text=day.upper(), bg=hdr_bg, fg=accent_fg,
                     font=("Segoe UI", 7 if is_compact else 8, "bold")).pack()
            tk.Label(hdr_f, text=date_str, bg=hdr_bg, fg="white",
                     font=("Segoe UI", 14 if is_compact else 18, "bold")).pack()

        # ── Time Slots & Grid Cells
        for ri, (shift_lbl, slot_key) in enumerate(zip(SLOTS_LBL, SLOT_KEYS)):
            # Row header
            is_active_slot = (slot_key == active_slot_key)
            row_bg = "#4f46e5" if is_active_slot else "#1e293b"
            
            side_f = tk.Frame(gf, bg=row_bg, padx=8, pady=8 if is_compact else 12)
            side_f.grid(row=ri + 1, column=0, sticky="nsew", padx=1, pady=1)
            gf.rowconfigure(ri + 1, minsize=cell_min_h, weight=1)

            tk.Label(side_f, text=shift_lbl.split("\n")[0], bg=row_bg, fg="white",
                     font=("Segoe UI", 9 if is_compact else 10, "bold")).pack()
            tk.Label(side_f, text=shift_lbl.split("\n")[1], bg=row_bg, fg="#94a3b8" if not is_active_slot else "#c7d2fe",
                     font=("Segoe UI", 7 if is_compact else 8)).pack()

            for ci, day in enumerate(DAYS):
                entries = lookup.get((day, slot_key), []) # type: ignore
                is_today_col = (ci == today_col)
                is_current_cell = (is_today_col and is_active_slot)
                date_for_cell = mon + dt.timedelta(days=ci) # type: ignore
                date_iso = date_for_cell.isoformat() # type: ignore
                
                # Cell container
                border_c = "#4f46e5" if is_current_cell else GRID_BORDER
                cell_outer = tk.Frame(gf, bg=border_c, padx=2 if is_current_cell else 1, pady=2 if is_current_cell else 1)
                cell_outer.grid(row=ri + 1, column=ci + 1, sticky="nsew", padx=1, pady=1)
                
                bg = "#fefce8" if is_today_col else "white"
                cell = tk.Frame(cell_outer, bg=bg, cursor="hand2" if entries else "")
                cell.pack(fill="both", expand=True)
                
                if entries:
                    main_label, main_status, is_mine, source_id = entries[0]

                    s_bg, s_fg = CELL_COLORS.get(main_status, ("#f1f5f9", "#475569"))
                    if is_mine:
                        s_bg, s_fg = ("#eef2ff", "#4f46e5") # Indigo theme for mine
                    accent = "#4f46e5" if is_mine else CELL_ACCENT.get(main_status, "#cbd5e1")
                    
                    # High-end card design
                    tk.Frame(cell, bg=accent, width=4 if not is_mine else 6).pack(side="left", fill="y")
                    
                    inner = tk.Frame(cell, bg=bg, padx=8 if is_compact else 12, pady=6 if is_compact else 10)
                    inner.pack(fill="both", expand=True)
                    
                    # Status Badge (Pill style)
                    badge_f = tk.Frame(inner, bg=bg)
                    badge_f.pack(anchor="nw", fill="x")
                    
                    badge = tk.Frame(badge_f, bg=s_bg, padx=4, pady=1)
                    badge.pack(side="left")
                    tk.Label(badge, text=main_status.upper(), bg=s_bg, fg=s_fg,
                             font=("Segoe UI", 6 if is_compact else 7, "bold")).pack()
                    
                    if is_mine:
                        my_b = tk.Frame(badge_f, bg="#4f46e5", padx=4, pady=1)
                        my_b.pack(side="left", padx=4)
                        tk.Label(my_b, text="CỦA TÔI", bg="#4f46e5", fg="white",
                                 font=("Segoe UI", 6 if is_compact else 7, "bold")).pack()
                    
                    # Subject / Label
                    tk.Label(inner, text=main_label, bg=bg, fg="#1e1b4b" if is_mine else "#1e293b",
                             font=("Segoe UI", 9 if is_compact else 10, "bold"), justify="left", anchor="nw",
                             wraplength=120 if is_compact else 140).pack(fill="both", expand=True, pady=(2, 0))
                    
                    if len(entries) > 1:
                        tk.Label(inner, text=f"+ {len(entries)-1} lịch khác...",
                                 bg=bg, fg="#6366f1", font=("Segoe UI", 8, "italic")).pack(anchor="sw")

                    # Tooltip & Detail
                    _cell_tooltip(cell, entries, date_iso, slot_key)
                    
                    def _show_detail(e: object, ents=list(entries), ds=date_iso, dn=day, sk=slot_key) -> None:
                        # Extract class_id from first entry
                        class_id = ents[0][3] if ents and len(ents[0]) > 3 else ""
                        if class_id:
                            self._show_class_student_list(ds, dn, sk, class_id)
                        else:
                            # Fallback to old behavior if no source_id
                            self._show_cell_detail(ents, ds, dn, sk)
                            
                    cell.bind("<Button-1>", _show_detail)


                    # Interactions for occupied cells
                    def _on_cell_enter(e, w=cell, b=bg): 
                        if entries: w.config(bg="#f1f5f9")
                    def _on_cell_leave(e, w=cell, b=bg): w.config(bg=b)
                    
                    cell.bind("<Enter>", _on_cell_enter, add="+")
                    cell.bind("<Leave>", _on_cell_leave, add="+")
                else:
                    # Today column highlight in grid
                    bg = "#fefce8" if is_today_col else "#ffffff"
                    inner_cell = tk.Frame(cell_outer, bg=bg)
                    inner_cell.pack(fill="both", expand=True)
                    
                    lbl = tk.Label(inner_cell, text="Trống", bg=bg, fg="#cbd5e1",
                                   font=("Segoe UI", 10, "italic"), pady=20)
                    lbl.pack(fill="both", expand=True)
                    
                    # Enhanced Hover for empty cells
                    def _on_ent_empty(e, f=inner_cell, l=lbl): 
                        f.config(bg="#f8fafc")
                        l.config(fg="#4f46e5")
                    def _on_lev_empty(e, f=inner_cell, l=lbl, b=bg): 
                        f.config(bg=b)
                        l.config(fg="#94a3b8")
                    
                    inner_cell.bind("<Enter>", _on_ent_empty)
                    inner_cell.bind("<Leave>", _on_lev_empty)

        # ── Tally row at bottom
        tk.Label(gf, text="TỔNG / NGÀY", bg="#1e293b", fg="#94a3b8",
                 font=("Segoe UI", 8, "bold"),
                 width=13, height=2).grid(row=len(SLOT_KEYS) + 1, column=0, sticky="nsew", padx=1, pady=1)
        
        for ci, day in enumerate(DAYS):
            day_total = sum(1 for (d, _s), entries in lookup.items() if d == day and entries) # type: ignore
            is_active = day_total > 0
            bg = "#1e1b4b" if is_active else "#f8fafc"
            fg = "#818cf8" if is_active else "#94a3b8"
            
            f = tk.Frame(gf, bg=GRID_BORDER, padx=1, pady=1)
            f.grid(row=len(SLOT_KEYS) + 1, column=ci + 1, sticky="nsew", padx=1, pady=1)
            tk.Label(f, text=f"{day_total} LỊCH" if is_active else "–",
                     bg=bg, fg=fg, font=("Segoe UI", 8, "bold")).pack(fill="both", expand=True)

        # ── Update Stats Bar (Fixed area)

        total_bookings = sum(len(v) for v in lookup.values())
        approved  = sum(1 for v in lookup.values() for entry in v if len(entry) >= 2 and entry[1] == "Da duyet")
        pending   = sum(1 for v in lookup.values() for entry in v if len(entry) >= 2 and entry[1] == "Cho duyet")
        rejected  = sum(1 for v in lookup.values() for entry in v if len(entry) >= 2 and entry[1] == "Tu choi")
        busy_cells = sum(1 for v in lookup.values() if v)
        total_cells = len(DAYS) * len(SLOT_KEYS)
        rate = int(busy_cells * 100 / total_cells) if total_cells else 0

        # ── Update Stats Bar (Ultra Compact)
        for w in self._stats_bar.winfo_children():
            w.destroy()

        # Simple light header
        header_f = tk.Frame(self._stats_bar, bg=C_SURFACE)
        header_f.pack(fill="x", pady=(0, 2))
        tk.Label(header_f, text="THỐNG KÊ TUẦN NÀY",
                 bg=C_SURFACE, fg="#64748b",
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        chips_outer, chips_f = make_card(self._stats_bar, padx=10, pady=6, shadow=False)
        chips_outer.pack(fill="both", expand=True)

        def _stat_chip(parent: tk.Frame, icon: str, label: str, value: str,
                       bg: str, fg: str, col: int, bar_color: str | None = None) -> None:
            chip_outer, chip = make_card(parent, padx=14, pady=10, shadow=True)
            chip_outer.grid(row=0, column=col, sticky="nsew", padx=6, pady=4)
            parent.columnconfigure(col, weight=1)
            
            top_f = tk.Frame(chip, bg="#f8fafc")
            top_f.pack(anchor="w")
            tk.Label(top_f, text=icon, bg="#f8fafc",
                     font=("Segoe UI", 18)).pack(side="left", padx=(0, 6))
            tk.Label(top_f, text=value, bg="#f8fafc", fg=fg,
                     font=("Segoe UI", 18, "bold")).pack(side="left")
            tk.Label(chip, text=label, bg="#f8fafc", fg="#64748b",
                     font=("Segoe UI", 9)).pack(anchor="w")
            if bar_color and total_bookings > 0:
                cnt_int = int(value) if value.isdigit() else 0
                bar_frame = tk.Frame(chip, bg="#e2e8f0", height=3)
                bar_frame.pack(fill="x", pady=(4, 0))
                fill_pct = cnt_int / max(total_bookings, 1)
                if fill_pct > 0:
                    tk.Frame(chip, bg=bar_color, height=3).place(
                        relx=0, rely=0, relwidth=fill_pct)

        _stat_chip(chips_f, "📅", "Tổng số lịch",  str(total_bookings), "#eef2ff", "#4f46e5", 0)
        _stat_chip(chips_f, "✅", "Đã duyệt",       str(approved),       "#dcfce7", "#15803d", 1, "#16a34a")
        _stat_chip(chips_f, "⏳", "Chờ duyệt",      str(pending),        "#fef3c7", "#b45309", 2, "#f59e0b")
        _stat_chip(chips_f, "❌", "Từ chối",        str(rejected),       "#fdf2f8", "#db2777", 3, "#ec4899")
        _stat_chip(chips_f, "📈", "Tỷ lệ sử dụng",  f"{rate}%",          "#f0f9ff", "#0369a1", 4)

    def _show_class_student_list(self, date_iso: str, day_name: str, slot: str, class_id: str) -> None:
        """Fetch class info and student list, then show the dialog."""
        class_obj = self.booking_ctrl.get_class_info(class_id)
        if not class_obj:
            messagebox.showerror("Lỗi", f"Không tìm thấy thông tin cho lớp học {class_id}")
            return
            
        students = self.booking_ctrl.get_enrollment_list(class_id)
        
        info = {
            "class_id": class_id,
            "name": getattr(class_obj, "name", "N/A"),
            "time": f"{day_name} - {slot}",
            "room": getattr(class_obj, "room_id", "N/A")
        }
        
        from gui.class_student_list_gui import ClassStudentListDialog
        ClassStudentListDialog(self, info, students)