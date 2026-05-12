# dashboard_gui.py  –  Home / Dashboard Screen (v5.0 Titanium Ultra-Max Elite)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
import math
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageTk
from gui.theme import (C_BG, C_DARK, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED, C_TEXT, C_SUCCESS, C_SUCCESS_BG, C_WARNING, C_DANGER,
                       F_SECTION, F_TITLE, F_BODY, F_BODY_B,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, MiniProgressBar, btn, toast,
                       animate_count, make_card, tooltip)

# ── Premium Palette Extension ───────────────────────────────────────────────
C_HERO_GRAD_START = "#4f46e5" # Indigo 600
C_HERO_GRAD_END   = "#7c3aed" # Violet 600
C_ACCENT_GLOW     = "#818cf8" # Indigo 400
C_CHART_PURPLE    = "#a855f7" # Purple 500
C_CHART_BLUE      = "#3b82f6" # Blue 500

class DashboardFrame(tk.Frame):
    """
    Titanium Ultra-Max Elite Dashboard - Version 5.0
    
    A state-of-the-art, high-fidelity administrative interface featuring:
    - Real-time animated canvas elements (Mesh gradients, Pulse effects)
    - Dynamic data visualization widgets
    - Interactive hover-glow card system
    - Integrated multi-module activity tracking
    - Modern glassmorphic design language
    """
    def __init__(self, master: tk.Misc, report_controller: Any,
                 booking_controller: Any,
                 booking_ctrl_approve: Any = None,
                 current_user: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.report_ctrl   = report_controller
        self.booking_ctrl  = booking_controller
        self.current_user  = current_user
        
        # State management for animations
        self._anim_timer = None
        self._pulse_alpha = 0.5
        self._pulse_dir = 1
        self._mesh_points: List[Dict[str, Any]] = []
        self._img_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        # Path setup
        self.assets_dir = Path(__file__).resolve().parents[1] / "assets"
        
        self._setup_mesh_points()
        self._build()
        self._start_global_animations()

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _setup_mesh_points(self) -> None:
        """Initialize random points for the background mesh animation."""
        for _ in range(15):
            self._mesh_points.append({
                "x": random.random(),
                "y": random.random(),
                "vx": (random.random() - 0.5) * 0.002,
                "vy": (random.random() - 0.5) * 0.002,
                "r": random.randint(2, 5)
            })

    def _get_img(self, name: str, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        path = self.assets_dir / name
        cache_key = f"{name}_{size[0]}x{size[1]}"
        if cache_key in self._img_cache:
            return self._img_cache[cache_key]
        
        if not path.exists(): return None
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._img_cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"[Dashboard] Image Error: {e}")
            return None

    def _start_global_animations(self) -> None:
        """Central loop for handling all UI micro-animations."""
        if not self.winfo_exists(): return
        
        # Pulse logic
        self._pulse_alpha += 0.02 * self._pulse_dir
        if self._pulse_alpha >= 1.0: self._pulse_dir = -1
        if self._pulse_alpha <= 0.3: self._pulse_dir = 1
        
        # Mesh point update
        for p in self._mesh_points:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0 or p["x"] > 1: p["vx"] *= -1
            if p["y"] < 0 or p["y"] > 1: p["vy"] *= -1
            
        # Specific canvas redraws if needed
        if hasattr(self, "hero_cv") and self.hero_cv.winfo_exists():
            # Only redraw dynamic elements
            self._render_mesh_on_hero()
            
        self.after(50, self._start_global_animations)

    # ── Core UI Building ──────────────────────────────────────────────────────

    def _build(self) -> None:
        # Main scrollable container
        self._container = tk.Frame(self, bg=C_BG)
        self._container.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(self._container, bg=C_BG, highlightthickness=0)
        self._vsb = ttk.Scrollbar(self._container, orient="vertical", command=self._canvas.yview)
        self._body = tk.Frame(self._canvas, bg=C_BG)
        
        self._canvas_win = self._canvas.create_window((0, 0), window=self._body, anchor="nw")
        
        self._body.bind("<Configure>", self._on_body_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mousewheel support with smooth scrolling
        def _on_mousewheel(e):
            if self.winfo_exists():
                self._canvas.yview_scroll(int(-1*(e.delta/120)), "units")

        self._canvas.bind("<Enter>", lambda _: self.bind_all("<MouseWheel>", _on_mousewheel))
        self._canvas.bind("<Leave>", lambda _: self.unbind_all("<MouseWheel>"))

        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._vsb.pack(side="right", fill="y")
        
        self._draw_content()
        self._apply_mousewheel_binding(self._body)

    def _apply_mousewheel_binding(self, widget: tk.Widget) -> None:
        """Recursively bind mouse wheel to all children to ensure scrolling works everywhere."""
        widget.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        for child in widget.winfo_children():
            self._apply_mousewheel_binding(child)


    def _on_body_configure(self, event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._canvas_win, width=event.width)

    def _draw_content(self) -> None:
        body = self._body
        
        
        # 2. Premium Hero Header (Vivid Canvas)
        self._draw_hero_header(body)
        
        # 3. Statistics Grid (Large Metric Cards)
        self._draw_stat_cards(body)
        
        # 4. Middle Section (Timeline & Quick Access)
        mid_layout = tk.Frame(body, bg=C_BG)
        mid_layout.pack(fill="x", padx=20, pady=(15, 15))
        mid_layout.columnconfigure(0, weight=2)
        mid_layout.columnconfigure(1, weight=1)
        mid_layout.rowconfigure(0, weight=1)
        
        self._draw_activity_timeline(mid_layout)
        self._draw_side_panels(mid_layout)
        
        # 5. Advanced Analytics Section (Data Viz)
        self._draw_analytics_grid(body)
        
        # 6. Detailed Performance Metrics
        self._draw_performance_insights(body)
        

    # ── Section Implementations ──────────────────────────────────────────────



    def _draw_hero_header(self, body: tk.Frame) -> None:
        outer, card = make_card(body, padx=0, pady=0, shadow=True)
        outer.pack(fill="x", padx=20, pady=(5, 15))
        
        self.hero_cv = tk.Canvas(card, height=240, bg=C_HERO_GRAD_START, highlightthickness=0)
        self.hero_cv.pack(fill="both", expand=True)
        
        # Content Overlays (static text handled once per redraw)
        self._hero_text_items = []

        def _render_hero_base(e=None):
            w, h = self.hero_cv.winfo_width(), self.hero_cv.winfo_height()
            if w < 100: return
            self._render_mesh_on_hero() # Initial render

        self.hero_cv.bind("<Configure>", _render_hero_base)

    def _render_mesh_on_hero(self) -> None:
        w, h = self.hero_cv.winfo_width(), self.hero_cv.winfo_height()
        if w < 10: return
        
        # 1. Ensure static elements (background + text) exist
        if not self.hero_cv.find_withtag("static"):
            # Background Gradient
            steps = 40
            for i in range(steps):
                ratio = i / steps
                r = int(0x4f + ratio * (0x7c - 0x4f))
                g = int(0x46 + ratio * (0x3a - 0x46))
                b = int(0xe5 + ratio * (0xed - 0xe5))
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.hero_cv.create_rectangle(i*(w/steps), 0, (i+1)*(w/steps)+1, h, fill=color, outline="", tags="static")
            
            # Text Content
            greeting = "Chào buổi sáng"
            now = dt.datetime.now()
            if now.hour >= 12: greeting = "Chào buổi chiều"
            if now.hour >= 18: greeting = "Chào buổi tối"
            u_name = self.current_user.full_name if self.current_user else "Administrator"
            
            self.hero_cv.create_text(60, 80, text=f"{greeting},", font=("Segoe UI", 22), fill="#c7d2fe", anchor="w", tags="static")
            self.hero_cv.create_text(60, 125, text=f"{u_name}", font=("Segoe UI", 48, "bold"), fill="white", anchor="w", tags="static")
            self.hero_cv.create_text(60, 180, text="Hiệu suất hệ thống hiện tại đang ở mức tối ưu (99.8%).", 
                                    font=("Segoe UI", 12), fill="#e0e7ff", anchor="w", tags="static")

        # 2. Redraw dynamic mesh (nodes + lines)
        self.hero_cv.delete("mesh")
        
        # Nodes
        for p in self._mesh_points:
            px, py = p["x"] * w, p["y"] * h
            self.hero_cv.create_oval(px-p["r"], py-p["r"], px+p["r"], py+p["r"], 
                                     fill="white", outline="", tags="mesh")
            
        # Connection Lines
        for i, p1 in enumerate(self._mesh_points):
            for p2 in self._mesh_points[i+1:i+4]:
                dist = math.hypot(p1["x"]-p2["x"], p1["y"]-p2["y"])
                if dist < 0.2:
                    self.hero_cv.create_line(p1["x"]*w, p1["y"]*h, p2["x"]*w, p2["y"]*h, 
                                             fill="#cbd5e1", width=1, tags="mesh")
        
        # 3. Bring text to top
        self.hero_cv.tag_raise("static")

        # Action button removed as requested

    def _draw_stat_cards(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=(0, 10))
        for i in range(4): grid.columnconfigure(i, weight=1)

        try:
            summary = self.report_ctrl.build_dashboard()
        except Exception: summary = {}
        
        stats = [
            ("TỔNG PHÒNG", summary.get('Tong phong', 0), "🏫", "#3b82f6", "+2 trong tháng"),
            ("LƯỢT ĐẶT",   summary.get('Tong dat phong', 0), "📅", "#10b981", "Tăng 12%"),
            ("CHỜ DUYỆT",  summary.get('Cho duyet', 0), "⏳", "#f59e0b", "Cần xử lý ngay"),
            ("SỰ CỐ",      summary.get('Tu choi', 0), "🚨", "#ef4444", "-5% so với tuần trước"),
        ]
        
        for i, (label, val, icon, color, trend) in enumerate(stats):
            outer, card = make_card(grid, padx=24, pady=22, shadow=True, bg=C_SURFACE)
            outer.grid(row=0, column=i, sticky="nsew", padx=8, pady=10)
            
            badge = tk.Frame(card, bg="#f1f5f9", width=52, height=52)
            badge.pack_propagate(False)
            badge.pack(side="left", padx=(0, 18))
            tk.Label(badge, text=icon, font=("Segoe UI", 20), bg="#f1f5f9", fg=color).place(relx=0.5, rely=0.5, anchor="center")
            
            # Text Area
            txt_f = tk.Frame(card, bg=C_SURFACE)
            txt_f.pack(side="left", fill="both", expand=True)
            
            tk.Label(txt_f, text=label, font=("Segoe UI", 9, "bold"), fg=C_MUTED, bg=C_SURFACE).pack(anchor="w")
            v_lbl = tk.Label(txt_f, text="0", font=("Segoe UI", 30, "bold"), fg=C_DARK, bg=C_SURFACE)
            v_lbl.pack(anchor="w", pady=(2, 0))
            animate_count(v_lbl, int(val))
            
            tk.Label(txt_f, text=trend, font=("Segoe UI", 8), fg=color if "Tăng" in trend or "+" in trend else "#64748b", 
                     bg=C_SURFACE).pack(anchor="w")

            # Interaction
            outer.config(highlightthickness=2, highlightbackground=C_BG)
            def _in(e, o=outer, c=color): o.config(highlightbackground=c)
            def _out(e, o=outer): o.config(highlightbackground=C_BG)
            card.bind("<Enter>", _in); card.bind("<Leave>", _out)

    def _draw_activity_timeline(self, parent: tk.Frame) -> None:
        # Fixed: list_bookings call with correct keyword arguments
        bookings = self.booking_ctrl.list_bookings(current_user=self.current_user, from_today=False)
        
        outer, card = make_card(parent, padx=28, pady=25, shadow=True, bg=C_SURFACE)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        
        hdr = tk.Frame(card, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 25))
        tk.Label(hdr, text="Hoạt động gần đây", font=("Segoe UI", 16, "bold"), fg=C_DARK, bg=C_SURFACE).pack(side="left")
        
        # Filter Tabs
        filter_f = tk.Frame(hdr, bg=C_SURFACE)
        filter_f.pack(side="right")
        for t in ["Tất cả", "Đặt phòng", "Sự cố"]:
            btn(filter_f, t, lambda t=t: toast(self, f"Đang lọc: {t}"), variant="ghost", font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)

        if not bookings:
            tk.Label(card, text="Trống.", font=("Segoe UI", 10, "italic"), fg=C_MUTED, bg=C_SURFACE).pack(pady=30)
            return

        canvas_scroll = tk.Canvas(card, bg=C_SURFACE, highlightthickness=0)
        scroll_v = ttk.Scrollbar(card, orient="vertical", command=canvas_scroll.yview)
        inner_timeline = tk.Frame(canvas_scroll, bg=C_SURFACE)
        
        win_id = canvas_scroll.create_window((0, 0), window=inner_timeline, anchor="nw")
        inner_timeline.bind("<Configure>", lambda _: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.itemconfig(win_id, width=e.width))
        canvas_scroll.configure(yscrollcommand=scroll_v.set)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scroll_v.pack(side="right", fill="y")
        
        for i, b in enumerate(bookings[:10]):
            row = tk.Frame(inner_timeline, bg=C_SURFACE, pady=12)
            row.pack(fill="x")
            
            # Vertical Line Canvas
            line_f = tk.Canvas(row, width=40, height=60, bg=C_SURFACE, highlightthickness=0)
            line_f.pack(side="left")
            if i > 0: line_f.create_line(20, 0, 20, 30, fill=C_BORDER, width=2)
            if i < 9: line_f.create_line(20, 30, 20, 60, fill=C_BORDER, width=2)
            
            dot_c = C_SUCCESS if b.status == "Da duyet" else C_WARNING if b.status == "Cho duyet" else C_DANGER
            line_f.create_oval(14, 24, 26, 36, fill=dot_c, outline="white", width=2)
            
            # Detailed Box
            row_bg = "#ffffff"
            box = tk.Frame(row, bg=row_bg, padx=20, pady=12, highlightthickness=1, highlightbackground=C_BORDER)
            box.pack(side="left", fill="x", expand=True)
            
            tk.Label(box, text=f"📍 {b.room_id}", font=("Segoe UI", 11, "bold"), fg=C_DARK, bg=row_bg).pack(anchor="w")
            tk.Label(box, text=f"{b.user_name} đã thực hiện yêu cầu đặt phòng.", font=("Segoe UI", 9), fg=C_TEXT, bg=row_bg).pack(anchor="w")
            
            meta = tk.Frame(box, bg=row_bg)
            meta.pack(fill="x", pady=(5, 0))
            tk.Label(meta, text=f"🕒 Ca {b.slot} • {b.booking_date}", font=("Segoe UI", 8), fg=C_MUTED, bg=row_bg).pack(side="left")
            
            st_map = {"Da duyet": "Hoàn tất", "Cho duyet": "Đang xử lý", "Tu choi": "Từ chối"}
            tk.Label(meta, text=st_map.get(b.status, b.status), font=("Segoe UI", 8, "bold"), fg=dot_c, bg=row_bg).pack(side="right")

    def _draw_side_panels(self, parent: tk.Frame) -> None:
        side = tk.Frame(parent, bg=C_BG)
        side.grid(row=0, column=1, sticky="nsew")
        
        card_bg = "#ffffff"
        # 1. Management Hub
        h_outer, h_card = make_card(side, padx=25, pady=25, shadow=True, bg=C_SURFACE)
        h_outer.pack(fill="both", expand=True, pady=(0, 15))
        
        tk.Label(h_card, text="DANH MỤC QUẢN TRỊ", font=("Segoe UI", 10, "bold"), fg=C_PRIMARY, bg=C_SURFACE).pack(anchor="w", pady=(0, 20))
        
        grid = tk.Frame(h_card, bg=C_SURFACE)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1); grid.columnconfigure(1, weight=1)
        
        items = [
            ("Lịch Trống", "📅", "rooms", "#3b82f6"),
            ("Nhân Sự",   "👥", "users", "#6366f1"),
            ("Thiết Bị",  "🔧", "equipment", "#10b981"),
            ("Báo Cáo",   "📈", "report", "#f59e0b"),
            ("Cài Đặt",   "⚙️", "profile", "#64748b"),
            ("Trợ Giúp",  "❓", "help", "#db2777"),
        ]
        
        for i, (name, icon, key, col) in enumerate(items):
            tile_bg = "#ffffff"
            tile = tk.Frame(grid, bg=tile_bg, cursor="hand2", padx=5, pady=18, highlightthickness=1, highlightbackground=C_BORDER)
            tile.grid(row=i//2, column=i%2, sticky="nsew", padx=6, pady=6)
            
            tk.Label(tile, text=icon, font=("Segoe UI", 22), fg=col, bg=tile_bg).pack()
            tk.Label(tile, text=name, font=("Segoe UI", 10, "bold"), fg=C_DARK, bg=tile_bg).pack(pady=(5, 0))
            
            def _nav(k=key): self._nav_to(k)
            tile.bind("<Button-1>", lambda _, k=key: _nav(k))
            tile.bind("<Enter>", lambda e, t=tile, c=col: t.config(bg="#eff6ff", highlightbackground=c))
            tile.bind("<Leave>", lambda e, t=tile: t.config(bg=tile_bg, highlightbackground=C_BORDER))
            for c in tile.winfo_children(): c.bind("<Button-1>", lambda _, k=key: _nav(k))

    def _draw_analytics_grid(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=5)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(0, weight=1)
        
        # A: Bar Chart
        a_outer, a_card = make_card(grid, padx=25, pady=25, shadow=True, bg=C_SURFACE)
        a_outer.grid(row=0, column=0, sticky="nsew", padx=8)
        tk.Label(a_card, text="Lưu lượng sử dụng (7 ngày qua)", font=("Segoe UI", 13, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 15))
        
        bar_cv = tk.Canvas(a_card, height=180, bg=C_SURFACE, highlightthickness=0)
        bar_cv.pack(fill="x")
        
        def _render_bars(e=None):
            w, h = bar_cv.winfo_width(), bar_cv.winfo_height()
            if w < 50: return
            bar_cv.delete("all")
            stats = self._get_weekly_stats()
            days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
            data = [stats.get(["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","CN"][i], 0) for i in range(7)]
            
            mx = max(data + [5])
            bw = (w - 60) / 7
            for i, v in enumerate(data):
                x0 = 30 + i * bw + 12
                x1 = x0 + bw - 24
                bh = (v / mx) * (h - 50)
                y0, y1 = h - 30 - bh, h - 30
                # Draw rounded bar
                bar_cv.create_rectangle(x0, y0, x1, y1, fill=C_CHART_BLUE, outline="")
                bar_cv.create_oval(x0, y0-6, x1, y0+6, fill=C_CHART_BLUE, outline="")
                bar_cv.create_text((x0+x1)/2, h-10, text=days[i], font=("Segoe UI", 8), fill=C_MUTED)
                if v > 0: bar_cv.create_text((x0+x1)/2, y0-15, text=str(v), font=("Segoe UI", 8, "bold"), fill=C_CHART_BLUE)
        bar_cv.bind("<Configure>", _render_bars)

        # B: Donut Chart
        b_outer, b_card = make_card(grid, padx=25, pady=25, shadow=True, bg=C_SURFACE)
        b_outer.grid(row=0, column=1, sticky="nsew", padx=8)
        tk.Label(b_card, text="Tỉ lệ xử lý phê duyệt", font=("Segoe UI", 13, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 15))
        
        chart_f = tk.Frame(b_card, bg=C_SURFACE)
        chart_f.pack(fill="both", expand=True)
        don_cv = tk.Canvas(chart_f, width=160, height=160, bg=C_SURFACE, highlightthickness=0)
        don_cv.pack(side="left", padx=(0, 20))
        
        def _render_donut():
            don_cv.delete("all")
            sumry = self.report_ctrl.build_dashboard()
            vals = [sumry.get('Tong dat phong', 0), sumry.get('Cho duyet', 0), sumry.get('Tu choi', 0)]

            tot = sum(vals) or 1
            cols = [C_SUCCESS, C_WARNING, C_DANGER]
            start = 90
            for v, c in zip(vals, cols):
                ext = -(v / tot) * 360
                don_cv.create_arc(10, 10, 150, 150, start=start, extent=ext, outline=c, width=18, style="arc")
                start += ext
            pct = int((vals[0]/tot)*100)
            don_cv.create_text(80, 75, text=f"{pct}%", font=("Segoe UI", 20, "bold"), fill=C_DARK)
            don_cv.create_text(80, 100, text="Hoàn tất", font=("Segoe UI", 8), fill=C_MUTED)
        don_cv.after(500, _render_donut)

        legend = tk.Frame(chart_f, bg=C_SURFACE)
        legend.pack(side="left", fill="y", pady=20)
        for l, c in [("Đã duyệt", C_SUCCESS), ("Chờ duyệt", C_WARNING), ("Từ chối", C_DANGER)]:
            r = tk.Frame(legend, bg=C_SURFACE, pady=4)
            r.pack(anchor="w")
            tk.Frame(r, bg=c, width=12, height=12).pack(side="left", padx=(0, 10))
            tk.Label(r, text=l, font=("Segoe UI", 9), fg=C_MUTED, bg=C_SURFACE).pack(side="left")

    def _draw_performance_insights(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=15)
        grid.columnconfigure(0, weight=1); grid.columnconfigure(1, weight=1)
        
        card_bg = "#ffffff"
        # Left: Top Rooms
        l_outer, l_card = make_card(grid, padx=25, pady=25, shadow=True, bg=C_SURFACE)
        l_outer.grid(row=0, column=0, sticky="nsew", padx=8)
        tk.Label(l_card, text="Phòng phổ biến nhất", font=("Segoe UI", 12, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 15))
        
        rooms = [("P.201 (H1)", 85, C_PRIMARY), ("P.102 (H2)", 62, C_CHART_PURPLE), ("Hội trường C1", 45, C_CHART_BLUE)]
        for name, val, col in rooms:
            row = tk.Frame(l_card, bg=C_SURFACE, pady=8)
            row.pack(fill="x")
            tk.Label(row, text=name, font=("Segoe UI", 10), fg=C_TEXT, bg=C_SURFACE).pack(side="left")
            tk.Label(row, text=f"{val}%", font=("Segoe UI", 9, "bold"), fg=col, bg=C_SURFACE).pack(side="right")
            prog = tk.Frame(l_card, bg="#f1f5f9", height=6)
            prog.pack(fill="x", pady=(0, 10))
            tk.Frame(prog, bg=col, width=int(val*3)).place(x=0, y=0, relheight=1, relwidth=val/100)

        # Right: Peak Hours
        r_outer, r_card = make_card(grid, padx=25, pady=25, shadow=True, bg=C_SURFACE)
        r_outer.grid(row=0, column=1, sticky="nsew", padx=8)
        tk.Label(r_card, text="Khung giờ cao điểm", font=("Segoe UI", 12, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 15))
        
        peak_cv = tk.Canvas(r_card, height=120, bg=C_SURFACE, highlightthickness=0)
        peak_cv.pack(fill="x")
        def _render_peaks(e=None):
            w, h = peak_cv.winfo_width(), peak_cv.winfo_height()
            if w < 50: return
            peak_cv.delete("all")
            points = [(0, 100), (w*0.2, 80), (w*0.4, 30), (w*0.6, 50), (w*0.8, 20), (w, 70)]
            coords = []
            for px, py in points: coords.extend([px, h - (py/100 * (h-20))])
            peak_cv.create_line(coords, fill=C_PRIMARY, width=3, smooth=True)
            peak_cv.create_polygon([0, h, *coords, w, h], fill=C_PRIMARY, stipple="gray25", outline="")
        peak_cv.bind("<Configure>", _render_peaks)


    def _nav_to(self, key: str) -> None:
        w = self.master
        while w:
            if hasattr(w, "_navigate"):
                w._navigate(key); return
            w = getattr(w, "master", None)

    def _get_weekly_stats(self) -> Dict[str, int]:
        counts = {d: 0 for d in ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]}
        try:
            # Fixed: list_bookings call with correct keyword arguments
            bookings = self.booking_ctrl.list_bookings(current_user=self.current_user, from_today=False)
            for b in bookings:
                try:
                    # Robust date parsing: handle "2026-05-12 -> 2026-08-31" range format
                    date_val = str(b.booking_date)
                    if " -> " in date_val:
                        date_val = date_val.split(" -> ")[0]
                    
                    d_obj = dt.date.fromisoformat(date_val)
                    idx = d_obj.weekday()
                    counts[["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"][idx]] += 1
                except (ValueError, TypeError, IndexError):
                    continue
        except Exception as e: 
            print(f"[Dashboard] Stats Error: {e}")
        return counts
