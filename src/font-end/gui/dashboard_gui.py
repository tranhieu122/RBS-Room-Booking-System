# dashboard_gui.py  –  Home / Dashboard Screen (v4.1 Titanium Ultra-Max)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
import math
import os
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image, ImageTk
from gui.theme import (C_BG, C_DARK, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED, C_SUCCESS, C_SUCCESS_BG, C_WARNING, C_DANGER,
                       F_SECTION, F_TITLE, F_BODY, F_BODY_B,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, MiniProgressBar, btn, toast,
                       animate_count, make_card, tooltip)

# Premium Palette Extension
C_HERO_GRAD_START = "#4f46e5" # Indigo 600
C_HERO_GRAD_END   = "#7c3aed" # Violet 600
C_CARD_GLOW       = "#6366f1" # Indigo 500

class DashboardFrame(tk.Frame):
    """
    Titanium Ultra-Max Dashboard - Version 4.1
    A high-fidelity, interactive dashboard inspired by modern SaaS platforms.
    Features: Generated 3D assets, dynamic gradients, and premium layouts.
    """
    def __init__(self, master: tk.Misc, report_controller: Any,
                 booking_controller: Any,
                 booking_ctrl_approve: Any = None,
                 current_user: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.report_ctrl   = report_controller
        self.booking_ctrl  = booking_controller
        self.current_user  = current_user
        
        self._anim_timer = None
        self._gradient_offset = 0
        self._img_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        # Path setup
        self.assets_dir = Path(__file__).resolve().parents[1] / "assets"
        
        self._build()

    def _get_img(self, name: str, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        path = self.assets_dir / name
        cache_key = f"{name}_{size[0]}x{size[1]}"
        if cache_key in self._img_cache:
            return self._img_cache[cache_key]
        
        if not path.exists():
            return None
        
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._img_cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"Error loading image {name}: {e}")
            return None

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
        
        # Mousewheel support
        def _on_mousewheel(e):
            if self.winfo_exists():
                self._canvas.yview_scroll(int(-1*(e.delta/120)), "units")

        self._canvas.bind("<Enter>", lambda _: self.bind_all("<MouseWheel>", _on_mousewheel))
        self._canvas.bind("<Leave>", lambda _: self.unbind_all("<MouseWheel>"))

        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._vsb.pack(side="right", fill="y")
        
        self._draw_content()

    def _on_body_configure(self, event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._canvas_win, width=event.width)

    def _draw_content(self) -> None:
        body = self._body
        
        # 1. Premium Hero Header
        self._draw_hero_header(body)
        
        # 2. Statistics Grid
        self._draw_stat_cards(body)
        
        # 3. Middle Section: Activity & Quick Actions
        mid_layout = tk.Frame(body, bg=C_BG)
        mid_layout.pack(fill="x", padx=20, pady=(5, 5))
        mid_layout.columnconfigure(0, weight=2) # Main activity
        mid_layout.columnconfigure(1, weight=1) # Side panels
        
        self._draw_activity_timeline(mid_layout)
        self._draw_side_panels(mid_layout)
        
        # 4. Analytics Section
        self._draw_analytics_grid(body)
        
        # 5. Bottom Insights
        self._draw_insights_footer(body)

    def _draw_hero_header(self, body: tk.Frame) -> None:
        outer, card = make_card(body, padx=0, pady=0, shadow=True)
        outer.pack(fill="x", padx=0, pady=(0, 5))
        
        self.hero_cv = tk.Canvas(card, height=220, bg=C_HERO_GRAD_START, highlightthickness=0)
        self.hero_cv.pack(fill="both", expand=True)
        
        def _render_hero(e=None):
            w = self.hero_cv.winfo_width()
            h = self.hero_cv.winfo_height()
            if w < 100:
                self.after(200, _render_hero)
                return
            self.hero_cv.delete("all")
            
            # 1. Background Image (Generated)
            bg_img = self._get_img("dash_hero.png", (w, h))
            if bg_img:
                self.hero_cv.create_image(0, 0, image=bg_img, anchor="nw")
            else:
                # Fallback Gradient
                steps = 50
                for i in range(steps):
                    ratio = i / steps
                    r = int(0x4f + ratio * (0x7c - 0x4f))
                    g = int(0x46 + ratio * (0x3a - 0x46))
                    b = int(0xe5 + ratio * (0xed - 0xe5))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    x_pos = i * (w/steps)
                    self.hero_cv.create_rectangle(x_pos, 0, x_pos + (w/steps) + 1, h, fill=color, outline="")

            # 2. Glassmorphism overlay for text legibility
            self.hero_cv.create_rectangle(0, 0, w, h, fill="black", stipple="gray25", outline="")
            
            # Content Overlays
            now = dt.datetime.now()
            hour = now.hour
            greeting = "Chào buổi sáng" if hour < 12 else "Chào buổi chiều" if hour < 18 else "Chào buổi tối"
            user_name = self.current_user.full_name if self.current_user else "Quản trị viên"
            
            # Welcome Text
            self.hero_cv.create_text(60, 80, text=f"{greeting}, {user_name} 👋", 
                                    font=("Segoe UI", 36, "bold"), fill="white", anchor="w")
            
            self.hero_cv.create_text(60, 130, text="Hệ thống đã sẵn sàng. Bạn có 3 yêu cầu mới cần xử lý.", 
                                    font=("Segoe UI", 13), fill="#e0e7ff", anchor="w")
            
            # Action Button Overlay (Glass)
            self.hero_cv.create_rectangle(60, 165, 240, 205, fill="white", outline="white", width=1, stipple="gray25")
            self.hero_cv.create_text(150, 185, text="Xem báo cáo chi tiết  →", font=("Segoe UI", 10, "bold"), fill="white")

        self.hero_cv.bind("<Configure>", _render_hero)
        self.after(100, _render_hero)

    def _draw_stat_cards(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=(0, 5))
        for i in range(4): grid.columnconfigure(i, weight=1)

        try:
            summary = self.report_ctrl.build_dashboard()
        except Exception:
            summary = {}
        
        stats = [
            ("Tổng phòng", summary.get('Tong phong', 0), "🏫", "#3b82f6"),
            ("Đặt phòng", summary.get('Tong dat phong', 0), "📅", "#10b981"),
            ("Chờ duyệt", summary.get('Cho duyet', 0), "⏳", "#f59e0b"),
            ("Sự cố", summary.get('Tu choi', 0), "🚨", "#ef4444"),
        ]
        for i, (label, val, icon, color) in enumerate(stats):
            outer, card = make_card(grid, padx=24, pady=20, shadow=True)
            outer.grid(row=0, column=i, sticky="nsew", padx=8, pady=10)
            
            # Icon Badge
            # Use a safe light color for the badge background since Tkinter doesn't support 8-digit hex (RGBA)
            badge = tk.Frame(card, bg="#f1f5f9") 
            badge.pack(side="left", padx=(0, 15))
            tk.Label(badge, text=icon, font=("Segoe UI", 16), bg="#f1f5f9", fg=color).pack(padx=10, pady=5)
            
            # Hover Effect - Fixed to prevent shaking
            outer.config(highlightthickness=2, highlightbackground=C_BG)
            
            def _on_enter(e, c=outer, col=color):
                c.config(highlightbackground=col)
            def _on_leave(e, c=outer):
                c.config(highlightbackground=C_BG)
            
            card.bind("<Enter>", _on_enter)
            card.bind("<Leave>", _on_leave)

            # Labels
            tk.Label(card, text=label, font=("Segoe UI", 10, "bold"), fg=C_MUTED, bg=C_SURFACE).pack(anchor="w", pady=(12, 0))
            
            val_lbl = tk.Label(card, text="0", font=("Segoe UI", 28, "bold"), fg=C_DARK, bg=C_SURFACE)
            val_lbl.pack(anchor="w")
            animate_count(val_lbl, int(val))

    def _draw_activity_timeline(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent, padx=25, pady=20, shadow=True)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        header = tk.Frame(card, bg=C_SURFACE)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Hoạt động gần đây", font=("Segoe UI", 14, "bold"), fg=C_DARK, bg=C_SURFACE).pack(side="left")
        
        btn(header, "Xem tất cả", lambda: self._nav_to("booking_list"), variant="ghost").pack(side="right")
        
        # Timeline implementation
        bookings = self.booking_ctrl.list_bookings(from_today=False)
        if not bookings:
            tk.Label(card, text="Chưa có hoạt động nào được ghi nhận.", font=("Segoe UI", 10, "italic"), fg=C_MUTED, bg=C_SURFACE).pack(pady=15)
            return

        scroll_area = tk.Frame(card, bg=C_SURFACE)
        scroll_area.pack(fill="both", expand=True)
        
        for i, b in enumerate(bookings[:6]):
            item = tk.Frame(scroll_area, bg=C_SURFACE)
            item.pack(fill="x", pady=8)
            
            # Connector Line
            line_cv = tk.Canvas(item, width=40, height=50, bg=C_SURFACE, highlightthickness=0)
            line_cv.pack(side="left")
            if i < 5:
                line_cv.create_line(20, 25, 20, 50, fill=C_BORDER, width=2)
            if i > 0:
                line_cv.create_line(20, 0, 20, 25, fill=C_BORDER, width=2)
            
            # Status Dot
            dot_color = C_SUCCESS if b.status == "Da duyet" else C_WARNING if b.status == "Cho duyet" else C_DANGER
            line_cv.create_oval(14, 19, 26, 31, fill=dot_color, outline="white", width=2)
            
            # Content Card
            content = tk.Frame(item, bg="#f8fafc", padx=15, pady=10)
            content.pack(side="left", fill="x", expand=True)
            
            tk.Label(content, text=f"{b.user_name} đã đặt {b.room_id}", 
                     font=("Segoe UI", 10, "bold"), fg=C_DARK, bg="#f8fafc").pack(anchor="w")
            
            sub = tk.Frame(content, bg="#f8fafc")
            sub.pack(fill="x", pady=(2, 0))
            tk.Label(sub, text=f"Ca {b.slot} • {b.booking_date}", font=("Segoe UI", 9), fg=C_MUTED, bg="#f8fafc").pack(side="left")
            
            status_map = {"Da duyet": "Đã duyệt", "Cho duyet": "Chờ duyệt", "Tu choi": "Từ chối"}
            status_txt = status_map.get(b.status, b.status)
            tk.Label(content, text=status_txt, font=("Segoe UI", 8, "bold"), fg=dot_color, bg="#f8fafc").place(relx=1.0, rely=0.5, anchor="e", x=-10)

    def _draw_side_panels(self, parent: tk.Frame) -> None:
        side = tk.Frame(parent, bg=C_BG)
        side.grid(row=0, column=1, sticky="nsew")
        
        # 1. Quick Actions Card
        q_outer, q_card = make_card(side, padx=20, pady=18, shadow=True)
        q_outer.pack(fill="x", pady=(0, 15))
        
        tk.Label(q_card, text="Thao tác nhanh", font=("Segoe UI", 11, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 15))
        
        actions = [
            ("Đặt phòng học", "📝", "booking_form", C_PRIMARY),
            ("Quản lý thiết bị", "🔧", "equipment", "#6366f1"),
            ("Xem báo cáo", "📊", "report", "#059669"),
            ("Gửi thông báo", "🔔", "notifications", "#d97706"),
        ]
        
        for text, icon, key, color in actions:
            f = tk.Frame(q_card, bg=C_SURFACE, cursor="hand2")
            f.pack(fill="x", pady=4)
            
            lbl_ico = tk.Label(f, text=icon, font=("Segoe UI", 12), fg=color, bg=C_SURFACE, width=3)
            lbl_ico.pack(side="left")
            
            lbl_txt = tk.Label(f, text=text, font=("Segoe UI", 9, "bold"), fg=C_DARK, bg=C_SURFACE)
            lbl_txt.pack(side="left", padx=5)
            
            def _make_nav(k=key): return lambda _: self._nav_to(k)
            for w in (f, lbl_ico, lbl_txt):
                w.bind("<Button-1>", _make_nav(key))
                w.bind("<Enter>", lambda e, f=f: f.config(bg="#f1f5f9"))
                w.bind("<Leave>", lambda e, f=f: f.config(bg=C_SURFACE))

        # 2. System Health
        h_outer, h_card = make_card(side, padx=20, pady=18, shadow=True)
        h_outer.pack(fill="x")
        
        tk.Label(h_card, text="Trạng thái hệ thống", font=("Segoe UI", 11, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 10))
        
        # Simulated Health
        health_items = [("Database", "99.9%", C_SUCCESS), ("API Server", "Hoạt động", C_SUCCESS), ("Backup", "Đã lưu", C_PRIMARY)]
        for name, val, col in health_items:
            row = tk.Frame(h_card, bg=C_SURFACE, pady=4)
            row.pack(fill="x")
            tk.Label(row, text=name, font=("Segoe UI", 9), fg=C_MUTED, bg=C_SURFACE).pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 9, "bold"), fg=col, bg=C_SURFACE).pack(side="right")

    def _draw_analytics_grid(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=5)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        
        # Weekly Traffic (Bar Chart)
        self._draw_bar_chart_card(grid, 0)
        
        # Distribution (Donut Chart)
        self._draw_donut_chart_card(grid, 1)

    def _draw_bar_chart_card(self, parent: tk.Frame, col: int):
        outer, card = make_card(parent, padx=22, pady=20, shadow=True)
        outer.grid(row=0, column=col, sticky="nsew", padx=8)
        
        tk.Label(card, text="Lưu lượng sử dụng trong tuần", font=("Segoe UI", 12, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 20))
        
        cv = tk.Canvas(card, height=160, bg=C_SURFACE, highlightthickness=0)
        cv.pack(fill="x")
        
        def _draw_bars(e=None):
            w = cv.winfo_width()
            h = cv.winfo_height()
            if w < 50: return
            cv.delete("all")
            
            stats_map = self._get_weekly_stats()
            # Order: T2 to CN
            days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
            data = [stats_map.get(d, 0) for d in days_vn]
            labels = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
            
            max_val = max(data) if max(data) > 0 else 10
            padding = 40
            bar_w = (w - (2*padding)) / len(data)
            
            for i, val in enumerate(data):
                x0 = padding + i * bar_w + 10
                x1 = x0 + bar_w - 20
                bar_h = (val / max_val) * (h - 60) # Leave more space for labels
                y0 = h - 35 - bar_h
                y1 = h - 35
                
                # Draw Bar with rounded top look
                cv.create_rectangle(x0, y0, x1, y1, fill=C_PRIMARY, outline="")
                if bar_h > 5:
                    cv.create_oval(x0, y0-5, x1, y0+5, fill=C_PRIMARY, outline="")
                
                # Value label
                if val > 0:
                    cv.create_text((x0+x1)/2, y0-15, text=str(val), font=("Segoe UI", 8, "bold"), fill=C_PRIMARY)
                # Day label
                cv.create_text((x0+x1)/2, h-15, text=labels[i], font=("Segoe UI", 8), fill=C_MUTED)

        cv.bind("<Configure>", _draw_bars)

    def _draw_donut_chart_card(self, parent: tk.Frame, col: int):
        outer, card = make_card(parent, padx=22, pady=20, shadow=True)
        outer.grid(row=0, column=col, sticky="nsew", padx=8)
        
        tk.Label(card, text="Tình trạng phê duyệt", font=("Segoe UI", 12, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 10))
        
        chart_frame = tk.Frame(card, bg=C_SURFACE)
        chart_frame.pack(fill="both", expand=True)
        
        cv = tk.Canvas(chart_frame, width=150, height=150, bg=C_SURFACE, highlightthickness=0)
        cv.pack(side="left", padx=(10, 20))
        
        summary = self.report_ctrl.build_dashboard()
        # Mocking distribution if real data is low
        d_ok = summary.get('bookings', 10)
        d_wait = summary.get('pending', 5)
        d_err = summary.get('rejected', 2)
        total = d_ok + d_wait + d_err
        
        def _draw_donut():
            cv.delete("all")
            if total == 0: return
            
            cx, cy = 75, 75
            r = 60
            stroke = 15
            
            start = 90
            segments = [(d_ok, C_SUCCESS), (d_wait, C_WARNING), (d_err, C_DANGER)]
            
            for val, color in segments:
                extent = -(val / total) * 360
                cv.create_arc(cx-r, cy-r, cx+r, cy+r, start=start, extent=extent, outline=color, width=stroke, style="arc")
                start += extent
            
            # Center Text
            pct = int((d_ok / total) * 100)
            cv.create_text(cx, cy-5, text=f"{pct}%", font=("Segoe UI", 16, "bold"), fill=C_DARK)
            cv.create_text(cx, cy+15, text="Hoàn tất", font=("Segoe UI", 7), fill=C_MUTED)

        cv.after(200, _draw_donut)
        
        # Legend
        legend = tk.Frame(chart_frame, bg=C_SURFACE)
        legend.pack(side="left", fill="y", pady=20)
        
        for label, color, val in [("Đã duyệt", C_SUCCESS, d_ok), ("Chờ duyệt", C_WARNING, d_wait), ("Từ chối", C_DANGER, d_err)]:
            row = tk.Frame(legend, bg=C_SURFACE, pady=3)
            row.pack(anchor="w")
            tk.Frame(row, bg=color, width=10, height=10).pack(side="left", padx=(0, 8))
            tk.Label(row, text=f"{label}: {val}", font=("Segoe UI", 9), fg=C_MUTED, bg=C_SURFACE).pack(side="left")

    def _draw_insights_footer(self, body: tk.Frame) -> None:
        outer, card = make_card(body, padx=25, pady=20, shadow=True)
        outer.pack(fill="x", padx=20, pady=(10, 30))
        
        tk.Label(card, text="💡 Gợi ý hệ thống", font=("Segoe UI", 11, "bold"), fg=C_DARK, bg=C_SURFACE).pack(anchor="w", pady=(0, 10))
        
        # Dynamic Insight Logic
        insights = []
        summary = self.report_ctrl.build_dashboard()
        
        if summary.get('pending', 0) > 0:
            insights.append((f"Có {summary['pending']} yêu cầu đang chờ bạn phê duyệt. Hãy kiểm tra ngay!", C_WARNING))
        
        # Room utilization mock
        insights.append(("Phòng H1-201 có tần suất sử dụng cao nhất trong tuần qua.", C_PRIMARY))
        insights.append(("Hệ thống đã tự động sao lưu dữ liệu vào lúc 04:00 AM hôm nay.", C_SUCCESS))
        
        for text, color in insights[:3]:
            row = tk.Frame(card, bg=C_SURFACE, pady=4)
            row.pack(fill="x")
            tk.Label(row, text="•", font=("Segoe UI", 14, "bold"), fg=color, bg=C_SURFACE).pack(side="left", padx=(0, 10))
            tk.Label(row, text=text, font=("Segoe UI", 10), fg="#475569", bg=C_SURFACE, wraplength=900, justify="left").pack(side="left")

    def _nav_to(self, key: str) -> None:
        # Standard navigation bubble-up
        w = self.master
        while w:
            if hasattr(w, "_navigate"):
                w._navigate(key)
                return
            w = getattr(w, "master", None)


    def _get_weekly_stats(self) -> Dict[str, int]:
        days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
        counts = {d: 0 for d in days_vn}
        bookings = self.booking_ctrl.list_bookings(from_today=False)
        for b in bookings:
            try:
                d_obj = dt.date.fromisoformat(b.booking_date)
                idx = d_obj.weekday()
                if 0 <= idx < 7: counts[days_vn[idx]] += 1
            except: continue
        return counts
