# room_feedback_gui.py – dialogs and admin page for room ratings & issue reports
from __future__ import annotations
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, cast
from gui.theme import (
    C_BG, C_SURFACE, C_BORDER, C_MUTED,
    C_SUCCESS_BG,
    C_DANGER_BG, F_BODY, F_BODY_B, F_INPUT, F_SMALL, C_PRIMARY, C_DARK,
    make_tree, fill_tree, with_scrollbar, page_header, btn, confirm_dialog, make_card, status_badge, toast
)


# ─────────────────────────────────────────────────────────────────────────────
# RoomRatingDialog – mọi người dùng đều có thể đánh giá phòng
# ─────────────────────────────────────────────────────────────────────────────

class RoomRatingDialog(tk.Toplevel):
    """Modal: chọn số sao (1-5) và nhập nhận xét cho một phòng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, feedback_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Đánh giá phòng – {room_name}")
        self.resizable(False, False)
        self.grab_set()
        self.room_id        = room_id
        self.current_user   = current_user
        self.feedback_ctrl  = feedback_ctrl
        self.on_done        = on_done
        self._stars         = tk.IntVar(value=0)
        self.configure(bg=C_BG)
        self._build(room_name)
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self, room_name: str) -> None:
        # Header - Titanium Dark Style
        hdr = tk.Frame(self, bg=C_DARK, padx=24, pady=24)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=C_PRIMARY, height=3).pack(fill="x", side="top", pady=(0, 15))
        
        title_f = tk.Frame(hdr, bg=C_DARK)
        title_f.pack(fill="x")
        tk.Label(title_f, text="⭐", bg=C_DARK, fg=C_PRIMARY, font=("Segoe UI", 24)).pack(side="left", padx=(0, 15))
        
        txt_f = tk.Frame(title_f, bg=C_DARK)
        txt_f.pack(side="left")
        tk.Label(txt_f, text="ĐÁNH GIÁ PHÒNG", bg=C_DARK, fg="#94a3b8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(txt_f, text=room_name.upper(), bg=C_DARK, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")

        # Body
        body = tk.Frame(self, bg=C_SURFACE, padx=24, pady=24)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Mức độ hài lòng của bạn:", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w")

        # ── star buttons ──────────────────────────────────────────────────────
        star_row = tk.Frame(body, bg=C_SURFACE)
        star_row.pack(pady=(10, 5), anchor="w")
        self._star_btns: list[tk.Label] = []
        for i in range(1, 6):
            lbl = tk.Label(star_row, text="☆", bg=C_SURFACE,
                           font=("Segoe UI", 36), cursor="hand2", fg="#fbbf24")
            lbl.pack(side="left", padx=3)
            lbl.bind("<Button-1>", lambda e, v=i: self._set_stars(v))
            lbl.bind("<Enter>",    lambda e, v=i: self._hover_stars(v))
            lbl.bind("<Leave>",    lambda e: self._render_stars(self._stars.get()))
            self._star_btns.append(lbl)

        self._rating_label = tk.Label(body, text="Chưa chọn sao", bg=C_SURFACE,
                                      fg=C_PRIMARY, font=("Segoe UI", 10, "bold"))
        self._rating_label.pack(pady=(0, 20), anchor="w")

        # ── comment ───────────────────────────────────────────────────────────
        tk.Label(body, text="Nhận xét chi tiết:", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w")
        
        # Styled Text Container
        txt_border = tk.Frame(body, bg=C_BORDER, padx=1, pady=1)
        txt_border.pack(fill="x", pady=(8, 20))
        self._comment = tk.Text(txt_border, width=42, height=4, font=F_INPUT,
                                bg="white", relief="flat", padx=10, pady=8, wrap="word")
        self._comment.pack(fill="x")

        # ── existing rating hint ──────────────────────────────────────────────
        existing = self.feedback_ctrl.get_user_rating(
            self.room_id, self.current_user.user_id)
        if existing:
            self._set_stars(existing.stars)
            self._comment.insert("1.0", existing.comment)
            tk.Label(body, text="💡 Bạn đang cập nhật đánh giá cũ",
                     bg=C_SURFACE, fg=C_MUTED, font=F_SMALL).pack(anchor="w", pady=(0, 10))

        # ── buttons ───────────────────────────────────────────────────────────
        bf = tk.Frame(body, bg=C_SURFACE)
        bf.pack(fill="x", pady=(10, 0))
        btn(bf, "Gửi đánh giá", self._submit,
            variant="primary", icon="✨").pack(side="right")
        btn(bf, "Hủy", self.destroy,
            variant="ghost").pack(side="right", padx=12)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _set_stars(self, v: int) -> None:
        self._stars.set(v)
        self._render_stars(v)
        self._update_rating_label(v)

    def _hover_stars(self, v: int) -> None:
        self._render_stars(v)
        self._update_rating_label(v)

    def _render_stars(self, n: int) -> None:
        for i, lbl in enumerate(self._star_btns):
            lbl.config(text="★" if i < n else "☆")

    def _update_rating_label(self, stars: int) -> None:
        labels = ["", "Rất tệ", "Tệ", "Bình thường", "Tốt", "Rất tốt"]
        self._rating_label.config(text=labels[stars] if stars > 0 else "Chưa chọn sao")

    def _submit(self) -> None:
        stars = self._stars.get()
        if stars == 0:
            confirm_dialog(self, "Chưa chọn sao", "Vui long chon so sao (1-5).", 
                           kind="warning", cancel_text=None)
            return
        comment = self._comment.get("1.0", "end-1c").strip()
        try:
            self.feedback_ctrl.add_rating(
                self.room_id, self.current_user, stars, comment)
            confirm_dialog(self, "Thành công", "Cam on ban da danh gia phong!", 
                           kind="primary", cancel_text=None)
            if self.on_done:
                self.on_done()
            self.destroy()
        except ValueError as e:
            confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)


# ─────────────────────────────────────────────────────────────────────────────
# RoomIssueDialog – mọi người dùng đều có thể báo lỗi phòng
# ─────────────────────────────────────────────────────────────────────────────

class RoomIssueDialog(tk.Toplevel):
    """Modal: nhập mô tả sự cố/lỗi của một phòng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, feedback_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Báo lỗi phòng – {room_name}")
        self.resizable(False, False)
        self.grab_set()
        self.room_id       = room_id
        self.current_user  = current_user
        self.feedback_ctrl = feedback_ctrl
        self.on_done       = on_done
        self.configure(bg=C_BG)
        self._build(room_name)
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self, room_name: str) -> None:
        # Header - Danger Style
        hdr = tk.Frame(self, bg=C_DARK, padx=24, pady=24)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg="#ef4444", height=3).pack(fill="x", side="top", pady=(0, 15))
        
        title_f = tk.Frame(hdr, bg=C_DARK)
        title_f.pack(fill="x")
        tk.Label(title_f, text="🚨", bg=C_DARK, fg="#ef4444", font=("Segoe UI", 24)).pack(side="left", padx=(0, 15))
        
        txt_f = tk.Frame(title_f, bg=C_DARK)
        txt_f.pack(side="left")
        tk.Label(txt_f, text="BÁO LỖI PHÒNG HỌC", bg=C_DARK, fg="#94a3b8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(txt_f, text=room_name.upper(), bg=C_DARK, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")

        # Body
        body = tk.Frame(self, bg=C_SURFACE, padx=24, pady=24)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Mô tả sự cố / lỗi gặp phải:", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w")
        
        # Styled Text Container
        txt_border = tk.Frame(body, bg="#fee2e2", padx=1, pady=1) # Red tint border
        txt_border.pack(fill="x", pady=(10, 15))
        
        self._desc = tk.Text(txt_border, width=44, height=6, font=F_INPUT,
                             bg="white", relief="flat", padx=12, pady=10)
        self._desc.pack(fill="x")

        hint_f = tk.Frame(body, bg="#fef2f2", padx=12, pady=10)
        hint_f.pack(fill="x", pady=(0, 20))
        tk.Label(hint_f,
                 text="Báo cáo sẽ được gửi tới bộ phận kỹ thuật để xử lý sớm nhất. Vui lòng mô tả chi tiết để chúng tôi hỗ trợ tốt hơn.",
                 bg="#fef2f2", fg="#991b1b", font=F_SMALL, justify="left", wraplength=340).pack(anchor="w")

        bf = tk.Frame(body, bg=C_SURFACE)
        bf.pack(fill="x")
        btn(bf, "Gửi báo cáo", self._submit,
            variant="danger", icon="📤").pack(side="right")
        btn(bf, "Hủy bỏ", self.destroy,
            variant="ghost").pack(side="right", padx=12)

    def _submit(self) -> None:
        desc = self._desc.get("1.0", "end-1c").strip()
        if not desc:
            confirm_dialog(self, "Thiếu thông tin", "Vui long mo ta su co.", 
                           kind="warning", cancel_text=None)
            return
        try:
            self.feedback_ctrl.report_issue(
                self.room_id, self.current_user, desc)
            toast(self, "✅ Da gui bao cao! Admin se kiem tra som.")
            if self.on_done:
                self.on_done()
            self.destroy()
        except ValueError as e:
            confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)


def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"

# ─────────────────────────────────────────────────────────────────────────────
# RoomIssueManagementFrame – trang Admin: xem & giải quyết sự cố
# ─────────────────────────────────────────────────────────────────────────────

class RoomIssueManagementFrame(tk.Frame):
    """Titanium Elite – Quản lý sự cố phòng học (Responsive)."""

    def __init__(self, master: tk.Misc, feedback_ctrl: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.feedback_ctrl = feedback_ctrl
        self.filter_var    = tk.StringVar(value="Tat ca")
        self._wrap_labels: list[tk.Label] = []
        
        self._setup_layout()
        self.refresh()

    def _setup_layout(self) -> None:
        page_header(self, "Báo cáo sự cố phòng học", "🚨").pack(fill="x")

        # Stats Bar
        self.stats_f = tk.Frame(self, bg=C_BG, pady=10)
        self.stats_f.pack(fill="x", padx=20)
        self._render_stats()

        # Toolbar
        tb = tk.Frame(self, bg=C_BG, padx=20, pady=5)
        tb.pack(fill="x")
        tk.Label(tb, text="Trạng thái:", bg=C_BG, fg=C_MUTED, font=F_SMALL).pack(side="left")
        cb = ttk.Combobox(tb, textvariable=self.filter_var,
                          values=["Tat ca", "Chua xu ly", "Da xu ly"],
                          width=15, state="readonly")
        cb.pack(side="left", padx=10)
        self.filter_var.trace_add("write", lambda *_: self.refresh())
        btn(tb, "Làm mới", self.refresh, variant="ghost", icon="🔄").pack(side="right")

        # Main List
        wrap = tk.Frame(self, bg=C_BG)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.canvas = tk.Canvas(wrap, bg=C_BG, highlightthickness=0)
        self.vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=C_BG)
        
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw", tags="win")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        
        def _on_cfg(e):
            w = e.width
            self.canvas.itemconfig("win", width=w)
            # Update all wrapped labels
            for lbl in self._wrap_labels:
                if lbl.winfo_exists():
                    lbl.configure(wraplength=max(200, w - 100))
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        self.canvas.bind("<Configure>", _on_cfg)
        
        def _on_mw(e): self.canvas.yview_scroll(int(-1*(e.delta/60)), "units")
        self.canvas.bind("<Enter>", lambda _: self.bind_all("<MouseWheel>", _on_mw))
        self.canvas.bind("<Leave>", lambda _: self.unbind_all("<MouseWheel>"))

    def _render_stats(self) -> None:
        for w in self.stats_f.winfo_children(): w.destroy()
        issues = self.feedback_ctrl.get_issues()
        p = len([i for i in issues if i.status == "Chua xu ly"])
        
        for l, v, c in [("Tổng số", len(issues), "#64748b"), ("Chờ xử lý", p, "#ef4444"), ("Hoàn thành", len(issues)-p, "#10b981")]:
            f = tk.Frame(self.stats_f, bg=C_SURFACE, padx=15, pady=8, highlightthickness=1, highlightbackground=C_BORDER)
            f.pack(side="left", padx=(0, 10))
            tk.Label(f, text=str(v), bg=C_SURFACE, fg=c, font=("Segoe UI", 12, "bold")).pack()
            tk.Label(f, text=l.upper(), bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 7, "bold")).pack()

    def refresh(self) -> None:
        self._render_stats()
        for w in self.list_frame.winfo_children(): w.destroy()
        self._wrap_labels.clear()
        
        issues = self.feedback_ctrl.get_issues()
        f = self.filter_var.get()
        if f != "Tat ca": issues = [i for i in issues if i.status == f]
        
        if not issues:
            tk.Label(self.list_frame, text="Không có báo cáo nào.", bg=C_BG, fg=C_MUTED, font=F_BODY, pady=40).pack()
            return
            
        for i in issues: self._issue_card(i)

    def _issue_card(self, issue: Any) -> None:
        p = (issue.status == "Chua xu ly")
        outer = tk.Frame(self.list_frame, bg=C_BG, pady=6)
        outer.pack(fill="x")
        card = tk.Frame(outer, bg=C_SURFACE, padx=16, pady=16, highlightthickness=1, highlightbackground=C_BORDER)
        card.pack(fill="x")
        tk.Frame(card, bg=("#ef4444" if p else "#10b981"), width=4).place(relx=0, rely=0, relheight=1)
        
        h = tk.Frame(card, bg=C_SURFACE); h.pack(fill="x")
        tk.Label(h, text=f"📍 {issue.room_id}", bg=C_SURFACE, fg=C_DARK, font=F_BODY_B).pack(side="left")
        
        st_bg, st_fg = ("#fef2f2", "#ef4444") if p else ("#ecfdf5", "#10b981")
        st_f = tk.Frame(h, bg=st_bg, padx=8, pady=2); st_f.pack(side="right")
        tk.Label(st_f, text=("MỚI" if p else "ĐÃ XỬ LÝ"), bg=st_bg, fg=st_fg, font=("Segoe UI", 7, "bold")).pack()
        
        tk.Label(card, text=f"Báo bởi: {issue.user_name}  •  {issue.created_at}", bg=C_SURFACE, fg=C_MUTED, font=F_SMALL).pack(anchor="w", pady=(2, 8))
        
        df = tk.Frame(card, bg="#f8fafc", padx=12, pady=10); df.pack(fill="x")
        lbl = tk.Label(df, text=issue.description, bg="#f8fafc", fg="#334155", font=F_BODY, justify="left", anchor="w")
        lbl.pack(fill="x")
        self._wrap_labels.append(lbl)
        
        if p:
            f = tk.Frame(card, bg=C_SURFACE, pady=(10, 0)); f.pack(fill="x")
            btn(f, "Giải quyết", lambda: self._do_resolve(issue.issue_id), variant="success", icon="✔").pack(side="right")
        
        self._prop_mw(card)

    def _prop_mw(self, w: tk.Widget) -> None:
        def _mw(e): self.canvas.yview_scroll(int(-1*(e.delta/60)), "units")
        w.bind("<MouseWheel>", _mw, add="+")
        for c in w.winfo_children(): self._prop_mw(c)

    def _do_resolve(self, iid: int) -> None:
        if confirm_dialog(self, "Xác nhận", f"Đã xử lý sự cố #{iid}?"):
            self.feedback_ctrl.resolve_issue(iid)
            self.refresh()


class RoomRatingManagementFrame(tk.Frame):
    """Titanium Elite – Phân tích & Đánh giá phòng học (Luxury Version)."""

    def __init__(self, master: tk.Misc, feedback_ctrl: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.feedback_ctrl = feedback_ctrl
        self.star_var = tk.StringVar(value="Tất cả")
        self._wrap_labels: list[tk.Label] = []
        
        self._setup_layout()
        self.refresh()

    def _setup_layout(self) -> None:
        # ── Luxury Executive Header ──────────────────────────────────────────
        self.top_h = tk.Frame(self, bg=C_BG, pady=25)
        self.top_h.pack(fill="x", padx=30)
        
        # Left: Breadcrumbs + Title
        title_area = tk.Frame(self.top_h, bg=C_BG)
        title_area.pack(side="left")
        
        # Breadcrumbs
        tk.Label(title_area, text="Hệ thống  /  Quản trị viên  /  Phòng học", 
                 bg=C_BG, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        
        # Main Title & Subtitle
        tk.Label(title_area, text="Phân tích & Đánh giá", 
                 bg=C_BG, fg=C_DARK, font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(title_area, text="Theo dõi và đánh giá chất lượng dịch vụ phòng học từ phản hồi người dùng.", 
                 bg=C_BG, fg=C_MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        # Right: Quick Actions
        actions = tk.Frame(self.top_h, bg=C_BG)
        actions.pack(side="right", pady=(10, 0))
        
        btn(actions, "Xuất báo cáo", lambda: None, variant="primary", icon="📤").pack(side="right")
        btn(actions, "Tổng quan", lambda: None, variant="ghost", icon="🏛️").pack(side="right", padx=10)

        # Subtle Divider Line
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x", padx=30)

        # ── Top Stats Area ───────────────────────────────────────────────────
        self.header_f = tk.Frame(self, bg=C_BG, pady=20)
        self.header_f.pack(fill="x", padx=30)
        
        # Left: Main Stats Cards
        self.stats_left = tk.Frame(self.header_f, bg=C_BG)
        self.stats_left.pack(side="left", fill="y")
        
        # Right: Distribution Chart (Modern Card)
        self.dist_f = tk.Frame(self.header_f, bg=C_SURFACE, padx=25, pady=20, 
                               highlightthickness=1, highlightbackground=C_BORDER)
        self.dist_f.pack(side="right", fill="y", padx=(30, 0))
        tk.Label(self.dist_f, text="BIỂU ĐỒ PHÂN BỔ", bg=C_SURFACE, fg=C_PRIMARY, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 15))

        # ── Toolbar ─────────────────────────────────────────────────────────
        tb = tk.Frame(self, bg=C_BG, padx=30, pady=10)
        tb.pack(fill="x")
        
        f_box = tk.Frame(tb, bg=C_SURFACE, padx=15, pady=8, highlightthickness=1, highlightbackground=C_BORDER)
        f_box.pack(side="left")
        tk.Label(f_box, text="Lọc theo sao:", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 9)).pack(side="left")
        
        style = ttk.Style()
        style.configure("Luxury.TCombobox", padding=5)
        cb = ttk.Combobox(f_box, textvariable=self.star_var, values=["Tất cả", "5 ★", "4 ★", "3 ★", "2 ★", "1 ★"], 
                          width=12, state="readonly", style="Luxury.TCombobox")
        cb.pack(side="left", padx=(12, 0))
        self.star_var.trace_add("write", lambda *_: self.refresh())
        
        btn(tb, "Làm mới dữ liệu", self.refresh, variant="ghost", icon="🔄").pack(side="right")

        # ── Main List ───────────────────────────────────────────────────────
        wrap = tk.Frame(self, bg=C_BG)
        wrap.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        self.canvas = tk.Canvas(wrap, bg=C_BG, highlightthickness=0)
        self.vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=C_BG)
        
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw", tags="win")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        
        def _on_cfg(e):
            w = e.width
            self.canvas.itemconfig("win", width=w)
            for lbl in self._wrap_labels:
                if lbl.winfo_exists(): lbl.configure(wraplength=max(200, w - 180))
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", _on_cfg)
        
        def _on_mw(e): self.canvas.yview_scroll(int(-1*(e.delta/60)), "units")
        self.canvas.bind("<Enter>", lambda _: self.bind_all("<MouseWheel>", _on_mw))
        self.canvas.bind("<Leave>", lambda _: self.unbind_all("<MouseWheel>"))

    def refresh(self) -> None:
        from database.sqlite_db import get_connection
        conn = get_connection()
        
        # 1. Update Main Stats
        for w in self.stats_left.winfo_children(): w.destroy()
        s = conn.execute("SELECT AVG(stars), COUNT(*) FROM room_ratings").fetchone()
        avg, count = round(s[0] or 0, 1), s[1]
        
        best = conn.execute("SELECT room_id, AVG(stars) as a FROM room_ratings GROUP BY room_id ORDER BY a DESC LIMIT 1").fetchone()
        best_name = str(best[0]) if best else "N/A"
        
        for l, v, c, i in [
            ("Điểm trung bình", f"{avg} / 5.0", "#f59e0b", "⭐"),
            ("Tổng đánh giá", str(count), "#6366f1", "📊"),
            ("Phòng yêu thích", best_name, "#10b981", "💎")
        ]:
            f = tk.Frame(self.stats_left, bg=C_SURFACE, padx=25, pady=20, highlightthickness=1, highlightbackground=C_BORDER)
            f.pack(side="left", padx=(0, 20), fill="y")
            tk.Label(f, text=f"{i} {v}", bg=C_SURFACE, fg=c, font=("Segoe UI", 18, "bold")).pack(anchor="w")
            tk.Label(f, text=l.upper(), bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 0))

        # 2. Update Distribution Chart
        for w in self.dist_f.winfo_children(): 
            if isinstance(w, tk.Frame) and w != self.dist_f: w.destroy()
        
        counts = {i: 0 for i in range(1, 6)}
        raw_counts = conn.execute("SELECT stars, COUNT(*) FROM room_ratings GROUP BY stars").fetchall()
        for star, cnt in raw_counts: counts[star] = cnt
        
        for i in range(5, 0, -1):
            row = tk.Frame(self.dist_f, bg=C_SURFACE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{i} ★", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 9, "bold"), width=4).pack(side="left")
            
            # Rounded Progress Bar (Simulated with Canvas)
            bar_c = tk.Canvas(row, bg=C_SURFACE, width=180, height=12, highlightthickness=0)
            bar_c.pack(side="left", padx=15)
            
            # Background
            bar_c.create_rectangle(0, 2, 180, 10, fill="#f1f5f9", outline="", width=0)
            if count > 0:
                pct = counts[i] / count
                # Gold bar
                bar_c.create_rectangle(0, 2, int(180 * pct), 10, fill="#f59e0b", outline="", width=0)
            
            tk.Label(row, text=f"{counts[i]}", bg=C_SURFACE, fg=C_DARK, font=("Segoe UI", 9, "bold"), width=3).pack(side="left")

        # 3. Update Cards
        for w in self.list_frame.winfo_children(): w.destroy()
        self._wrap_labels.clear()
        
        query = "SELECT room_id, user_name, stars, comment, created_at FROM room_ratings"
        params = []
        sv = self.star_var.get()
        if "★" in sv:
            query += " WHERE stars = ?"; params.append(int(sv.split()[0]))
        query += " ORDER BY created_at DESC"
        
        rows = conn.execute(query, params).fetchall()
        if not rows:
            tk.Label(self.list_frame, text="Chưa có dữ liệu đánh giá nào cho bộ lọc này.", 
                     bg=C_BG, fg=C_MUTED, font=("Segoe UI", 11), pady=100).pack()
            return
            
        for r in rows: self._luxury_card(r)

    def _luxury_card(self, d: tuple) -> None:
        rid, unm, sts, cmt, cat = d
        outer = tk.Frame(self.list_frame, bg=C_BG, pady=10); outer.pack(fill="x")
        
        card = tk.Frame(outer, bg=C_SURFACE, padx=25, pady=25, highlightthickness=1, highlightbackground=C_BORDER)
        card.pack(fill="x")
        
        # Hover
        def _on_ent(e): card.configure(highlightbackground=C_PRIMARY, highlightthickness=1.5)
        def _on_lv(e): card.configure(highlightbackground=C_BORDER, highlightthickness=1)
        card.bind("<Enter>", _on_ent); card.bind("<Leave>", _on_lv)
        
        # Sentiment Side Indicator
        clr = "#ef4444" if sts <= 2 else "#f59e0b" if sts <= 3 else "#10b981"
        tk.Frame(card, bg=clr, width=6).place(relx=0, rely=0, relheight=1)
        
        # Header Row
        head = tk.Frame(card, bg=C_SURFACE)
        head.pack(fill="x")
        
        # Circular Avatar (Canvas)
        av_c = tk.Canvas(head, bg=C_SURFACE, width=50, height=50, highlightthickness=0)
        av_c.pack(side="left", padx=(0, 20))
        av_c.create_oval(2, 2, 48, 48, fill=clr, outline="")
        av_c.create_text(25, 25, text=_initials(unm), fill="white", font=("Segoe UI", 12, "bold"))
        
        # User Info
        uinfo = tk.Frame(head, bg=C_SURFACE)
        uinfo.pack(side="left")
        tk.Label(uinfo, text=unm, bg=C_SURFACE, fg=C_DARK, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        meta = tk.Frame(uinfo, bg=C_SURFACE)
        meta.pack(anchor="w", pady=(4, 0))
        
        # Room Badge
        rb = tk.Frame(meta, bg="#eff6ff", padx=10, pady=2)
        rb.pack(side="left")
        tk.Label(rb, text=f"🏠 {rid}", bg="#eff6ff", fg="#3b82f6", font=("Segoe UI", 8, "bold")).pack()
        
        # Time Badge
        tb = tk.Frame(meta, bg="#f8fafc", padx=10, pady=2)
        tb.pack(side="left", padx=10)
        tk.Label(tb, text=f"🕒 {cat}", bg="#f8fafc", fg=C_MUTED, font=("Segoe UI", 8)).pack()
        
        # Stars (Right)
        star_str = "★" * sts + "☆" * (5 - sts)
        tk.Label(head, text=star_str, bg=C_SURFACE, fg="#f59e0b", font=("Segoe UI", 16, "bold")).pack(side="right")
        
        # Comment with "Quote" style
        if cmt and cmt.strip():
            df = tk.Frame(card, bg="#f8fafc", padx=20, pady=15, highlightthickness=1, highlightbackground="#f1f5f9")
            df.pack(fill="x", pady=(20, 0))
            lbl = tk.Label(df, text=f"{cmt}", bg="#f8fafc", fg="#334155", font=("Segoe UI", 10, "italic"), justify="left", anchor="w")
            lbl.pack(fill="x")
            self._wrap_labels.append(lbl)
            
        self._prop_mw(card)


    def _prop_mw(self, w: tk.Widget) -> None:
        def _mw(e): self.canvas.yview_scroll(int(-1*(e.delta/60)), "units")
        w.bind("<MouseWheel>", _mw, add="+")
        for c in w.winfo_children(): self._prop_mw(c)






# ─────────────────────────────────────────────────────────────────────────────
# EquipmentReportDialog – báo hỏng thiết bị trong phòng
# ─────────────────────────────────────────────────────────────────────────────

class EquipmentReportDialog(tk.Toplevel):
    """Modal: hiển thị danh sách thiết bị của phòng, cho phép đánh dấu hỏng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, equipment_ctrl: Any, feedback_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Báo hỏng thiết bị – {room_name}")
        self.geometry("560x520")
        self.resizable(False, False)
        self.grab_set()
        self.room_id        = room_id
        self.room_name      = room_name
        self.current_user   = current_user
        self.equipment_ctrl = equipment_ctrl
        self.feedback_ctrl  = feedback_ctrl
        self.on_done        = on_done
        self.configure(bg=C_BG)
        self._check_vars: dict[str, tk.BooleanVar] = {}
        self._desc_vars:  dict[str, tk.StringVar]  = {}
        self._desc_widgets: dict[str, tk.Entry] = {}
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # Header - Warning/Equipment Style
        hdr = tk.Frame(self, bg=C_DARK, padx=24, pady=24)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg="#fbbf24", height=3).pack(fill="x", side="top", pady=(0, 15))
        
        title_f = tk.Frame(hdr, bg=C_DARK)
        title_f.pack(fill="x")
        tk.Label(title_f, text="🔧", bg=C_DARK, fg="#fbbf24", font=("Segoe UI", 24)).pack(side="left", padx=(0, 15))
        
        txt_f = tk.Frame(title_f, bg=C_DARK)
        txt_f.pack(side="left")
        tk.Label(txt_f, text="BÁO HỎNG THIẾT BỊ", bg=C_DARK, fg="#94a3b8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(txt_f, text=self.room_name.upper(), bg=C_DARK, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")

        # Body
        body = tk.Frame(self, bg=C_SURFACE, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body,
                 text="Chọn thiết bị bị hỏng và nhập mô tả chi tiết phía dưới:",
                 bg=C_SURFACE, fg=C_DARK, font=F_BODY_B, padx=8, pady=8).pack(anchor="w")

        # Scrollable equipment list
        list_frame = tk.Frame(body, bg=C_SURFACE)
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        canvas = tk.Canvas(list_frame, bg=C_SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)  # type: ignore[arg-type]
        scroll_body = tk.Frame(canvas, bg=C_SURFACE)
        scroll_body.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_body, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        equipment_list = self.equipment_ctrl.list_equipment(room_id=self.room_id)
        if not equipment_list:
            # Try to sync from rooms if empty (might have legacy data)
            # We need a room_controller for this. Let's try to get it from parent.
            if hasattr(self.master, "room_ctrl"):
                self.equipment_ctrl.sync_from_rooms(self.master.room_ctrl)
                equipment_list = self.equipment_ctrl.list_equipment(room_id=self.room_id)

        if not equipment_list:
            tk.Label(scroll_body,
                     text="ℹ  Phong nay chua co thiet bi nao duoc dang ky chi tiet.",
                     bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 10, "italic")).pack(pady=(40, 10))
            
            tk.Label(scroll_body,
                     text="Vui long lien he Admin de cap nhat danh sach thiet bi.",
                     bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 9)).pack()
        else:
            # Status colour map
            STATUS_BG = {
                "Hoat dong": "#dcfce7", "Bao tri": "#fef3c7",
                "Hong": "#fdf2f8", "Dang sua": "#e0f2fe", "Da thanh ly": "#f1f5f9",
            }
            STATUS_FG = {
                "Hoat dong": "#15803d", "Bao tri": "#b45309",
                "Hong": "#db2777", "Dang sua": "#0369a1", "Da thanh ly": "#64748b",
            }
            for equip in equipment_list:
                row_bg = "#fffbeb" if equip.status != "Hoat dong" else C_SURFACE
                row = tk.Frame(scroll_body, bg=row_bg, highlightthickness=1,
                               highlightbackground=C_BORDER)
                row.pack(fill="x", pady=2, padx=12, ipadx=6, ipady=4)

                # Checkbox
                var = tk.BooleanVar(value=False)
                self._check_vars[equip.equipment_id] = var
                cb = tk.Checkbutton(row, variable=var, bg=row_bg,
                                    activebackground=row_bg,
                                    selectcolor="white",
                                    command=lambda eid=equip.equipment_id:
                                        self._toggle_desc(eid))
                cb.pack(side="left", padx=(4, 0))

                # Equipment info
                info_col = tk.Frame(row, bg=row_bg)
                info_col.pack(side="left", fill="x", expand=True, padx=6)

                top_row = tk.Frame(info_col, bg=row_bg)
                top_row.pack(fill="x")
                tk.Label(top_row, text=equip.name,
                         bg=row_bg, fg="#1e293b",
                         font=F_BODY_B).pack(side="left")
                tk.Label(top_row, text=f"  [{equip.equipment_type}]",
                         bg=row_bg, fg=C_MUTED, font=F_SMALL).pack(side="left")
                tk.Label(top_row,
                         text=f"  {equip.status}  ",
                         bg=STATUS_BG.get(equip.status, "#f1f5f9"),
                         fg=STATUS_FG.get(equip.status, "#64748b"),
                         font=F_SMALL).pack(side="right", padx=(0, 4))

                # Description entry (initially hidden, shown when checkbox ticked)
                desc_var = tk.StringVar()
                self._desc_vars[equip.equipment_id] = desc_var
                desc_entry = tk.Entry(info_col, textvariable=desc_var,
                                      font=F_INPUT, relief="solid", bd=1,
                                      bg="white", fg="#1e293b")
                self._desc_widgets[equip.equipment_id] = desc_entry
                # Don't pack yet — shown only when checkbox is ticked

        # Footer buttons
        footer = tk.Frame(body, bg="#f8fafc", padx=16, pady=12)
        footer.pack(fill="x")
        btn(footer, "Gui bao cao hong", self._submit,
            variant="danger", icon="📤").pack(side="right")
        btn(footer, "Huy", self.destroy,
            variant="ghost").pack(side="right", padx=8)
        tk.Label(footer,
                 text="* Thiet bi duoc chon se tu dong chuyen sang trang thai 'Bao tri'",
                 bg=C_BG, fg=C_MUTED, font=F_SMALL, wraplength=300).pack(
            side="left")

    def _open_general_issue(self) -> None:
        """Fallback to the general room issue dialog."""
        self.destroy()
        RoomIssueDialog(
            self.master,
            room_id=self.room_id,
            room_name=self.room_name,
            current_user=self.current_user,
            feedback_ctrl=self.feedback_ctrl,
            on_done=self.on_done
        )

    def _toggle_desc(self, equipment_id: str) -> None:
        """Show/hide description entry when checkbox is toggled."""
        widget = self._desc_widgets.get(equipment_id)
        if widget is None:
            return
        if self._check_vars[equipment_id].get():
            widget.pack(fill="x", pady=(3, 0))
            # Placeholder behaviour
            if not widget.get():
                widget.insert(0, "Mo ta su co...")
                widget.config(fg="#94a3b8")
            def _on_focus_in(e: Any, w: tk.Entry = widget) -> None:
                if w.get() == "Mo ta su co...":
                    w.delete(0, "end")
                    w.config(fg="#1e293b")
            def _on_focus_out(e: Any, w: tk.Entry = widget) -> None:
                if not w.get().strip():
                    w.insert(0, "Mo ta su co...")
                    w.config(fg="#94a3b8")
            widget.bind("<FocusIn>", _on_focus_in)
            widget.bind("<FocusOut>", _on_focus_out)
        else:
            widget.pack_forget()

    def _submit(self) -> None:
        selected = [eid for eid, var in self._check_vars.items() if var.get()]
        if not selected:
            confirm_dialog(self, "Chưa chọn thiết bị", "Vui long chon it nhat mot thiet bi bi hong.", 
                           kind="warning", cancel_text=None)
            return

        errors: list[str] = []
        success_count = 0
        equipment_list = self.equipment_ctrl.list_equipment(room_id=self.room_id)
        equip_map = {e.equipment_id: e for e in equipment_list}

        for eid in selected:
            desc = ""
            widget = self._desc_widgets.get(eid)
            if widget:
                raw = widget.get().strip()
                desc = raw if raw and raw != "Mo ta su co..." else "Không có mô tả chi tiết."
            
            # Detailed description for the Room Issue log
            e_name = equip_map[eid].name if eid in equip_map else eid
            full_desc = f"[Hỏng thiết bị] {e_name}: {desc}"
            
            try:
                # 1. Report to equipment system
                self.equipment_ctrl.report_broken(eid, self.current_user, desc)
                
                # 2. ALSO report to general room issues system
                if self.feedback_ctrl:
                    self.feedback_ctrl.report_issue(self.room_id, self.current_user, full_desc)
                
                success_count += 1
            except ValueError as e:
                errors.append(str(e))

        if errors:
            confirm_dialog(self, "Có lỗi xảy ra", "\n".join(errors), 
                           kind="danger", cancel_text=None)
        if success_count:
            confirm_dialog(self, "Báo cáo thành công", 
                           f"Da gui {success_count} bao cao hong thiet bi.\nBo phan ky thuat se xu ly som.",
                           kind="primary", cancel_text=None)
            if self.on_done:
                self.on_done()
            self.destroy()
