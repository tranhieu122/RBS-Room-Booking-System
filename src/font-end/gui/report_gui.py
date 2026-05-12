# report_gui.py  –  statistics / report screen  (v2.1 – date filter)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any
from gui.theme import (C_BG, C_DARK, C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED,
                       F_SECTION, F_BODY_B, F_TITLE, make_tree, fill_tree, with_scrollbar,
                       page_header, confirm_dialog, make_card)

from tkcalendar import DateEntry  # type: ignore[import-untyped]

CARD_PALETTE = [
    ("#eef2ff", "#4f46e5", "📚"),   # Indigo
    ("#dcfce7", "#16a34a", "📅"),   # Green
    ("#fef3c7", "#b45309", "📋"),   # Amber
    ("#fdf2f8", "#db2777", "🚫"),   # Red
    ("#e0f2fe", "#0369a1", "👤"),   # Sky
    ("#ede9fe", "#6d28d9", "🛠"),   # Violet
]

BAR_COLORS = [
    "#4f46e5", "#6366f1", "#16a34a", "#f59e0b",
    "#9333ea", "#06b6d4", "#ec4899", "#84cc16",
]


class ReportFrame(tk.Frame):
    def __init__(self, master: tk.Misc, report_controller: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.report_ctrl = report_controller
        # Date filter state
        self._date_from = tk.StringVar()
        self._date_to   = tk.StringVar()
        self._body_ref: tk.Frame | None = None
        self._build()

    def _build(self) -> None:
        # ── Header + export toolbar ───────────────────────────────────────────
        hdr_row = tk.Frame(self, bg="#f8fafc")
        hdr_row.pack(fill="x")
        page_header(hdr_row, "Bao cao thong ke", "📊").pack(
            side="left", fill="x", expand=True)

        toolbar = tk.Frame(hdr_row, bg="#f8fafc")
        toolbar.pack(side="right", padx=16, pady=10)

        xlsx_btn = tk.Button(
            toolbar, text="📥  Xuat Excel",
            bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_excel,
        )
        xlsx_btn.pack(side="left", padx=(0, 8))

        pdf_btn = tk.Button(
            toolbar, text="📄  Xuat PDF",
            bg="#db2777", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_pdf,
        )
        pdf_btn.pack(side="left")

        # ── Date range filter panel ───────────────────────────────────────────
        filter_panel = tk.Frame(self, bg="#f1f5f9", padx=16, pady=12)
        filter_panel.pack(fill="x", padx=0, pady=(0, 0)) # Full width

        tk.Label(filter_panel, text="🗓  Loc theo khoang thoi gian:",
                 bg="#eef2ff", fg="#4f46e5",
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        from gui.date_picker_fixed import DatePickerWithLabel
        
        def _date_entry(parent: tk.Frame, var: tk.StringVar) -> tk.Widget:
            # Use the fixed date picker for better UX and consistency
            picker = DatePickerWithLabel(parent, var)
            picker.pack(side="left", padx=(8, 0))
            return picker._date_entry

        tk.Label(filter_panel, text="Tu:", bg="#eef2ff", fg="#4f46e5",
                 font=F_BODY_B).pack(side="left", padx=(10, 0))
        self._from_entry = _date_entry(filter_panel, self._date_from)
        tk.Label(filter_panel, text="Den:", bg="#eef2ff", fg="#4f46e5",
                 font=F_BODY_B).pack(side="left", padx=(8, 0))
        self._to_entry = _date_entry(filter_panel, self._date_to)

        loc_btn = tk.Button(
            filter_panel, text="🔍  Loc",
            bg=C_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._apply_filter,
        )
        loc_btn.pack(side="left", padx=(12, 0))
        loc_btn.bind("<Enter>", lambda _: loc_btn.config(bg="#4338ca"))
        loc_btn.bind("<Leave>", lambda _: loc_btn.config(bg=C_PRIMARY))

        reset_btn = tk.Button(
            filter_panel, text="✖  Xoa loc",
            bg="#f1f5f9", fg="#475569", font=("Segoe UI", 9),
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._reset_filter,
        )
        reset_btn.pack(side="left", padx=(6, 0))

        self._filter_info = tk.Label(filter_panel, text="",
                                     bg="#eef2ff", fg="#6d28d9",
                                     font=("Segoe UI", 8, "bold"))
        self._filter_info.pack(side="right", padx=8)

        # ── Scrollable body ──────────────────────────────────────────────────
        self._canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical",
                            command=self._canvas.yview)  # type: ignore[arg-type]
        self._body_ref = tk.Frame(self._canvas, bg=C_BG)
        self._body_ref.bind(
            "<Configure>",
            lambda _e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ENSURE BODY FILLS CANVAS WIDTH (Fixes right-side whitespace)
        def _on_canvas_config(e):
            self._canvas.itemconfig(canvas_win, width=e.width)
        canvas_win = self._canvas.create_window((0, 0), window=self._body_ref, anchor="nw")
        self._canvas.bind("<Configure>", _on_canvas_config)

        self._render_body()

    def _apply_mousewheel_binding(self, widget: tk.Widget) -> None:
        """Recursively bind mouse wheel to all children to ensure scrolling works everywhere."""
        widget.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))
        for child in widget.winfo_children():
            self._apply_mousewheel_binding(child)


    def _apply_filter(self) -> None:
        from_val = self._from_entry.get().strip()
        to_val   = self._to_entry.get().strip()
        placeholder = "YYYY-MM-DD"
        df = from_val if from_val != placeholder else ""
        dt_ = to_val  if to_val   != placeholder else ""
        # Validate
        for v, label in ((df, "Tu ngay"), (dt_, "Den ngay")):
            if v:
                try:
                    dt.date.fromisoformat(v)
                except ValueError:
                    confirm_dialog(self, "Ngày không hợp lệ", f"{label} phai theo dinh dang YYYY-MM-DD.", 
                                   kind="danger", cancel_text=None)
                    return
        self._date_from.set(df)
        self._date_to.set(dt_)
        if df or dt_:
            label_parts = []
            if df:
                label_parts.append(f"Tu {df}")
            if dt_:
                label_parts.append(f"Den {dt_}")
            self._filter_info.config(text="  🔵 " + "  –  ".join(label_parts))
        else:
            self._filter_info.config(text="")
        self._render_body()

    def _reset_filter(self) -> None:
        today = dt.date.today().isoformat()
        self._date_from.set(today)
        self._date_to.set(today)
        self._from_entry.set_date(dt.date.today())
        self._to_entry.set_date(dt.date.today())
        self._filter_info.config(text="")
        self._render_body()

    def _render_body(self) -> None:
        """Clear and redraw the scrollable body with current filter."""
        if self._body_ref is None:
            return
        for w in self._body_ref.winfo_children():
            w.destroy()
        df = self._date_from.get()
        dt_ = self._date_to.get()
        self._draw_stat_cards(self._body_ref, df, dt_)
        self._draw_detail_section(self._body_ref, df, dt_)
        self._apply_mousewheel_binding(self._body_ref)


    # ── Export helpers ────────────────────────────────────────────────────────

    def _export_excel(self) -> None:
        from utils.export_excel import export_rows_to_excel  # type: ignore[import-not-found]
        path = filedialog.asksaveasfilename(
            title="Luu file Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"BaoCao_{dt.date.today()}.xlsx",
        )
        if not path:
            return
        rows: list[tuple[object, object, object, object, object]] = self.report_ctrl.room_stats_table(
            date_from=self._date_from.get(), date_to=self._date_to.get())
        try:
            export_rows_to_excel(
                headers=["Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD (%)"],
                rows=rows,
                output_path=path,
            )
            confirm_dialog(self, "Xuất Excel thành công", f"Da luu tai:\n{path}", 
                           kind="primary", cancel_text=None)
        except Exception as exc:
            confirm_dialog(self, "Lỗi xuất Excel", str(exc), kind="danger", cancel_text=None)

    def _export_pdf(self) -> None:
        try:
            from utils.export_pdf import export_report_pdf  # type: ignore[import-not-found]
        except ImportError:
            confirm_dialog(self, "Thiếu thư viện", "Chua cai fpdf2.\nChay lenh:  pip install fpdf2", 
                           kind="danger", cancel_text=None)
            return
        path = filedialog.asksaveasfilename(
            title="Luu file PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"BaoCao_{dt.date.today()}.pdf",
        )
        if not path:
            return
        try:
            export_report_pdf(
                output_path=path,
                title="BAO CAO SU DUNG PHONG HOC",
                stat_rows=self.report_ctrl.room_stats_table(
                    date_from=self._date_from.get(),
                    date_to=self._date_to.get()),
                summary=self.report_ctrl.build_dashboard(
                    date_from=self._date_from.get(),
                    date_to=self._date_to.get()),
            )
            confirm_dialog(self, "Xuất PDF thành công", f"Da luu tai:\n{path}", 
                           kind="primary", cancel_text=None)
        except Exception as exc:
            confirm_dialog(self, "Lỗi xuất PDF", str(exc), kind="danger", cancel_text=None)

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _draw_stat_cards(self, body: tk.Frame,
                         date_from: str = "", date_to: str = "") -> None:
        panel = tk.Frame(body, bg=C_BG)
        panel.pack(fill="x", padx=0, pady=(10, 5)) # Full width
        summary: dict[str, object] = self.report_ctrl.build_dashboard(
            date_from=date_from, date_to=date_to)
        for idx, (label, value) in enumerate(summary.items()):
            bg, fg, icon = CARD_PALETTE[idx % len(CARD_PALETTE)]

            outer, chip = make_card(panel, padx=20, pady=18, shadow=True)
            outer.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=10, pady=10)
            
            # Left icon badge with glow
            badge = tk.Frame(chip, bg="#f8fafc", padx=12, pady=10)
            badge.pack(side="left", padx=(0, 20))
            tk.Label(badge, text=icon, bg="#f8fafc", font=("Segoe UI", 24)).pack()
            
            txt_f = tk.Frame(chip, bg=C_SURFACE)
            txt_f.pack(side="left", fill="both", expand=True)
            
            val_lbl = tk.Label(txt_f, text=str(value), bg=C_SURFACE, fg=fg, 
                               font=("Segoe UI", 28, "bold"))
            val_lbl.pack(anchor="w")
            
            tk.Label(txt_f, text=label.upper(), bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")

            # Hover Interaction
            outer.config(highlightthickness=2, highlightbackground=C_BORDER)
            def _on_enter(e, o=outer, c=fg): o.config(highlightbackground=c)
            def _on_leave(e, o=outer): o.config(highlightbackground=C_BORDER)
            chip.bind("<Enter>", _on_enter)
            chip.bind("<Leave>", _on_leave)
        for col in range(3):
            panel.grid_columnconfigure(col, weight=1, uniform="card")

    # ── Detail section (table + chart) ───────────────────────────────────────

    def _draw_detail_section(self, body: tk.Frame,
                             date_from: str = "", date_to: str = "") -> None:
        tk.Label(body, text="Tan suat su dung phong",
                 bg=C_BG, fg=C_DARK, font=F_SECTION).pack(
            anchor="w", padx=20, pady=(12, 6))

        row_data: list[tuple[object, object, object, object, str]] = self.report_ctrl.room_stats_table(
            date_from=date_from, date_to=date_to)

        # Two-column layout
        two_col = tk.Frame(body, bg=C_BG)
        two_col.pack(fill="x", padx=10, pady=(0, 16))
        two_col.columnconfigure(0, weight=5) # Table gets more width
        two_col.columnconfigure(1, weight=4) # Chart gets less width

        # ── Left: summary table ─────────────────────────────────────────────
        left_outer, left = make_card(two_col, padx=15, pady=15, shadow=True)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="Tong hop theo phong",
                 bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        rows: list[tuple[object, object, object, object, str]] = [(r[0], r[1], r[2], r[3], r[4]) for r in row_data]
        dynamic_h = max(6, min(12, len(rows))) # Professional min height of 6

        tree = make_tree(
            left,
            ("phong", "tong", "duyet", "tuchoi", "tyle"),
            ("Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD"),
            (80, 100, 100, 100, 100),
            height=dynamic_h,
        )
        with_scrollbar(left, tree)
        fill_tree(tree, rows)

        # ── Right: bar chart (usage rate %) ─────────────────────────────────
        right_outer, right = make_card(two_col, padx=15, pady=15, shadow=True)
        right_outer.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Bieu do tỷ lệ sử dụng (%)",
                 bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 12))

        chart_h = 220 if row_data else 60 # Collapse if no data
        self._chart_canvas = tk.Canvas(right, bg="#f8fafc", height=chart_h,
                                       highlightthickness=0)
        self._chart_canvas.pack(fill="x", expand=True)
        right.after(60, lambda: self._draw_bar_chart(row_data))

        # plain usage count bar (secondary)
        tk.Label(body, text="So lan dat phong (tong hop)",
                 bg=C_BG, fg=C_DARK, font=F_SECTION).pack(
            anchor="w", padx=20, pady=(8, 6))
        wrap2_outer, wrap2 = make_card(body, padx=18, pady=18, shadow=True)
        wrap2_outer.pack(fill="x", padx=20, pady=(0, 20))
        
        usage_rows: list[tuple[object, object]] = [(rid, cnt)
                                                   for rid, cnt in self.report_ctrl.room_usage_rows()
                                                   if cnt > 0]
        dynamic_h2 = max(4, min(8, len(usage_rows)))

        tree2 = make_tree(wrap2, ("room", "count"),
                          ("Phong", "So lan dat"), (240, 200), height=dynamic_h2)
        with_scrollbar(wrap2, tree2)
        fill_tree(tree2, usage_rows)

    def _draw_bar_chart(self, row_data: list[tuple[object, object, object, object, str]]) -> None:
        c = self._chart_canvas
        c.update_idletasks()
        W = c.winfo_width() or 420
        H = 200
        ml, mr, mb, mt = 40, 12, 38, 16

        if not row_data:
            c.create_text(W // 2, H // 2, text="Chua co du lieu",
                          font=("Segoe UI", 11), fill="#94a3b8")
            return

        n = len(row_data)
        gap = 8
        bar_area = W - ml - mr
        bar_w = max(20, (bar_area - gap * (n + 1)) // n)

        # axes
        c.create_line(ml, mt, ml, H - mb, fill="#d1d5db", width=1)
        c.create_line(ml, H - mb, W - mr, H - mb, fill="#d1d5db", width=1)

        for v in range(0, 101, 25):
            y = H - mb - int((H - mt - mb) * v / 100)
            c.create_line(ml - 4, y, W - mr, y, fill="#e5e7eb", dash=(3, 2))
            c.create_text(ml - 6, y, text=str(v),
                          font=("Segoe UI", 7), fill="#9ca3af", anchor="e")

        for idx, (room_id, _total, _approved, _rejected, rate_str) in enumerate(row_data):
            pct = int(rate_str.replace("%", "")) if rate_str.replace("%", "").isdigit() else 0
            color = BAR_COLORS[idx % len(BAR_COLORS)]
            x0 = ml + gap + idx * (bar_w + gap)
            bh = int((H - mt - mb) * pct / 100) if pct > 0 else 2
            y0 = H - mb - bh
            y1 = H - mb
            # bar with rounded-top illusion
            c.create_rectangle(x0, y0, x0 + bar_w, y1, fill=color, outline="")
            # value label
            c.create_text(x0 + bar_w // 2, y0 - 8,
                          text=rate_str,
                          font=("Segoe UI", 8, "bold"), fill=C_DARK)
            # room label
            c.create_text(x0 + bar_w // 2, H - mb + 14,
                          text=str(room_id), font=("Segoe UI", 8), fill="#374151")

