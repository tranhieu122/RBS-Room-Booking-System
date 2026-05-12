# advance_booking_calendar.py  –  30-day availability calendar view
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Callable

from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_TEXT, C_MUTED, C_PRIMARY,
                       C_SUCCESS, C_SUCCESS_BG, C_WARNING, C_WARNING_BG, 
                       C_DANGER, C_DANGER_BG,
                       page_header, btn, make_card, toast)

class AdvanceCalendarFrame(tk.Frame):
    def __init__(self, master: tk.Misc, room_controller: Any, 
                 booking_controller: Any, current_user: Any,
                 on_date_selected: Optional[Callable[[str], None]] = None) -> None:
        super().__init__(master, bg=C_BG)
        self.room_ctrl = room_controller
        self.booking_ctrl = booking_controller
        self.current_user = current_user
        self.on_date_selected = on_date_selected
        
        self.room_var = tk.StringVar()
        self._cells: list[tk.Frame] = []
        
        self._build()
        self._refresh_calendar()

    def _build(self) -> None:
        # Header
        page_header(self, "📅 Lịch đặt phòng 30 ngày", 
                   subtitle="Xem nhanh độ trống của phòng học trong tháng tới",
                   icon="📆")
        
        # ── Controls ──────────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=C_BG)
        ctrl.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(ctrl, text="Chọn phòng:", bg=C_BG, 
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        
        rooms = self.room_ctrl.list_rooms()
        self.room_options = [f"{r.room_id} – {r.name}" for r in rooms]
        
        self.room_cb = ttk.Combobox(
            ctrl, 
            textvariable=self.room_var,
            values=self.room_options,
            width=35,
            state="readonly"
        )
        self.room_cb.pack(side="left")
        if self.room_options:
            self.room_var.set(self.room_options[0])
        self.room_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_calendar())
        
        btn(ctrl, "Làm mới", self._refresh_calendar, variant="ghost", icon="🔄").pack(side="left", padx=15)

        # ── Legend ────────────────────────────────────────────────────────────
        legend = tk.Frame(ctrl, bg=C_BG)
        legend.pack(side="right")
        
        def _leg(color: str, text: str):
            f = tk.Frame(legend, bg=C_BG)
            f.pack(side="left", padx=10)
            tk.Frame(f, bg=color, width=12, height=12, highlightthickness=1, 
                     highlightbackground=C_BORDER).pack(side="left", padx=4)
            tk.Label(f, text=text, bg=C_BG, fg=C_MUTED, font=("Segoe UI", 9)).pack(side="left")

        _leg("#dcfce7", "Trống nhiều (>=3 ca)")
        _leg("#fef3c7", "Trống ít (1-2 ca)")
        _leg("#fee2e2", "Hết chỗ (0 ca)")

        # ── Calendar Grid ─────────────────────────────────────────────────────
        # Main container with scrollbar
        self.container = tk.Frame(self, bg=C_BG)
        self.container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(self.container, bg=C_SURFACE, highlightthickness=1, 
                                highlightbackground=C_BORDER)
        self.vsb = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=C_SURFACE)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda *_: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        
        # Mousewheel
        def _on_mousewheel(e: tk.Event):
            if self.winfo_exists():
                self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        
        self.canvas.bind("<Enter>", lambda _: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas.bind("<Leave>", lambda _: self.canvas.unbind_all("<MouseWheel>"))
        
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))

        # Grid header (Days of week)
        self.grid_header = tk.Frame(self.scrollable_frame, bg="#f1f5f9")
        self.grid_header.pack(fill="x")
        
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        for i, day in enumerate(days):
            tk.Label(self.grid_header, text=day, bg="#f1f5f9", fg=C_TEXT,
                     font=("Segoe UI", 10, "bold"), pady=10).place(relx=i/7, relwidth=1/7)
        self.grid_header.config(height=40)
        self.grid_header.pack_propagate(False)

        # Grid Body
        self.grid_body = tk.Frame(self.scrollable_frame, bg=C_SURFACE)
        self.grid_body.pack(fill="both", expand=True)
        
        # Configure columns
        for i in range(7):
            self.grid_body.columnconfigure(i, weight=1, uniform="cal")

    def _refresh_calendar(self) -> None:
        """Draw/Redraw the 30-day grid."""
        # Clear old cells
        for cell in self._cells:
            cell.destroy()
        self._cells.clear()
        
        display = self.room_var.get()
        room_id = display.split(" – ")[0] if display else ""
        if not room_id: return
        
        today = dt.date.today()
        # Start from Monday of current week
        start_date = today - dt.timedelta(days=today.weekday())
        
        current = start_date
        for row in range(6): # 5-6 weeks
            for col in range(7):
                self._draw_cell(current, row, col, room_id, today)
                current += dt.timedelta(days=1)
                if (current - today).days > 35: # Show a bit more than 30 days to fill grid
                    break

    def _draw_cell(self, date: dt.date, row: int, col: int, room_id: str, today: dt.date) -> None:
        is_today = (date == today)
        is_past = (date < today)
        
        # Cell Container
        cell = tk.Frame(self.grid_body, bg=C_SURFACE, highlightthickness=1, 
                        highlightbackground=C_BORDER)
        cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
        self.grid_body.rowconfigure(row, weight=1, minsize=100)
        self._cells.append(cell)
        
        # Date Number
        lbl_date = tk.Label(cell, text=date.strftime("%d"), 
                           bg=C_SURFACE, fg=C_TEXT if not is_past else C_MUTED,
                           font=("Segoe UI", 11, "bold" if is_today else "normal"))
        lbl_date.pack(anchor="nw", padx=8, pady=4)
        
        if is_today:
            tk.Label(cell, text="Hôm nay", bg=C_PRIMARY, fg="white", 
                     font=("Segoe UI", 7, "bold"), padx=4).place(relx=1.0, x=-5, y=8, anchor="ne")

        if is_past:
            return # Don't show availability for past dates
            
        # Get availability
        try:
            free_slots = self.booking_ctrl.available_slots(room_id, date.isoformat())
            count = len(free_slots)
        except Exception:
            count = 0
            
        # Color logic
        if count >= 3:
            bg, fg, tag = "#dcfce7", "#166534", f"Trống {count} ca"
        elif count >= 1:
            bg, fg, tag = "#fef3c7", "#92400e", f"Còn {count} ca"
        else:
            bg, fg, tag = "#fee2e2", "#991b1b", "Hết chỗ"
            
        badge = tk.Label(cell, text=tag, bg=bg, fg=fg, 
                        font=("Segoe UI", 9, "bold"), pady=4)
        badge.pack(fill="x", side="bottom", padx=4, pady=4)
        
        # Click event to jump to booking form
        def _on_click(_: Any):
            if self.on_date_selected:
                self.on_date_selected(date.isoformat())
            else:
                toast(self, f"Ngày chọn: {date.isoformat()}")
        
        # Binding
        for w in (cell, lbl_date, badge):
            w.bind("<Button-1>", _on_click)
            w.config(cursor="hand2")
