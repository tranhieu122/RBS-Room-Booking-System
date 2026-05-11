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
        # Header accent
        tk.Frame(self, bg=C_PRIMARY, height=4).pack(fill="x")
        
        container = tk.Frame(self, bg=C_BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        outer, card = make_card(container, padx=24, pady=20)
        outer.pack(fill="both", expand=True)

        tk.Label(card, text=f"Đánh giá phòng", bg=C_SURFACE,
                 fg=C_MUTED, font=F_SMALL).pack(anchor="w")
        tk.Label(card, text=room_name, bg=C_SURFACE,
                 fg=C_PRIMARY, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))

        tk.Label(card, text="Chon so sao:", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w", pady=(8, 4))

        # ── star buttons ──────────────────────────────────────────────────────
        star_row = tk.Frame(card, bg=C_SURFACE)
        star_row.pack(pady=(0, 4), anchor="w")
        self._star_btns: list[tk.Label] = []
        for i in range(1, 6):
            lbl = tk.Label(star_row, text="☆", bg=C_SURFACE,
                           font=("Segoe UI", 32), cursor="hand2", fg="#fbbf24")
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e, v=i: self._set_stars(v))
            lbl.bind("<Enter>",    lambda e, v=i: self._hover_stars(v))
            lbl.bind("<Leave>",    lambda e: self._render_stars(self._stars.get()))
            self._star_btns.append(lbl)

        self._rating_label = tk.Label(card, text="Chưa chọn sao", bg=C_SURFACE,
                                      fg=C_MUTED, font=F_BODY)
        self._rating_label.pack(pady=(0, 10), anchor="w")

        # ── comment ───────────────────────────────────────────────────────────
        tk.Label(card, text="Nhan xet (tuy chon):", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w", pady=(10, 4))
        self._comment = tk.Text(card, width=40, height=4, font=F_INPUT,
                                relief="solid", bd=1, wrap="word")
        self._comment.pack(fill="x", pady=(0, 12))

        # ── existing rating ───────────────────────────────────────────────────
        existing = self.feedback_ctrl.get_user_rating(
            self.room_id, self.current_user.user_id)
        if existing:
            self._set_stars(existing.stars)
            self._comment.insert("1.0", existing.comment)
            tk.Label(card, text="(Bạn đã đánh giá phòng này trước đó)",
                     bg=C_SURFACE, fg=C_MUTED, font=F_SMALL).pack(anchor="w")

        # ── buttons ───────────────────────────────────────────────────────────
        bf = tk.Frame(card, bg=C_SURFACE)
        bf.pack(fill="x", pady=(16, 0))
        btn(bf, "Gui danh gia", self._submit,
            variant="primary", icon="⭐").pack(side="right")
        btn(bf, "Huy", self.destroy,
            variant="ghost").pack(side="right", padx=8)

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
        # Header accent
        tk.Frame(self, bg="#dc2626", height=4).pack(fill="x")
        
        container = tk.Frame(self, bg=C_BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        outer, card = make_card(container, padx=24, pady=20)
        outer.pack(fill="both", expand=True)

        tk.Label(card, text="Báo lỗi phòng học", bg=C_SURFACE,
                 fg=C_MUTED, font=F_SMALL).pack(anchor="w")
        tk.Label(card, text=room_name, bg=C_SURFACE,
                 fg="#dc2626", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))

        tk.Label(card, text="Mo ta su co / loi:", bg=C_SURFACE,
                 fg=C_DARK, font=F_BODY_B).pack(anchor="w", pady=(8, 4))
        self._desc = tk.Text(card, width=44, height=5, font=F_INPUT,
                             relief="solid", bd=1, wrap="word")
        self._desc.pack(fill="x", pady=(0, 12))

        tk.Label(card,
                 text="Báo cáo sẽ được gửi tới Admin và đội kỹ thuật để xử lý sớm nhất.",
                 bg=C_SURFACE, fg=C_MUTED, font=F_SMALL, justify="left", wraplength=340).pack(anchor="w")

        bf = tk.Frame(card, bg=C_SURFACE)
        bf.pack(fill="x", pady=(16, 0))
        btn(bf, "Gui bao cao", self._submit,
            variant="danger", icon="🚨").pack(side="right")
        btn(bf, "Huy", self.destroy,
            variant="ghost").pack(side="right", padx=8)

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


# ─────────────────────────────────────────────────────────────────────────────
# RoomIssueManagementFrame – trang Admin: xem & giải quyết sự cố
# ─────────────────────────────────────────────────────────────────────────────

class RoomIssueManagementFrame(tk.Frame):
    """Admin page – danh sach bao cao su co phong."""

    def __init__(self, master: tk.Misc, feedback_ctrl: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.feedback_ctrl = feedback_ctrl
        self.filter_var    = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Bao cao su co phong hoc", "🚨").pack(fill="x")
        
        # Toolbar inside a card
        t_outer, toolbar = make_card(self, padx=16, pady=10, shadow=False)
        t_outer.pack(fill="x", padx=20, pady=(0, 12))

        tk.Label(toolbar, text="Loc theo trang thai:", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self.filter_var = tk.StringVar()
        cb = ttk.Combobox(toolbar, textvariable=self.filter_var,
                          values=["Tat ca", "Chua xu ly", "Da xu ly"],
                          width=16, state="readonly")
        cb.pack(side="left")
        self.filter_var.set("Tat ca")
        self.filter_var.trace_add("write", lambda *_: self.refresh())

        # Action group separator
        tk.Frame(toolbar, bg=C_BORDER, width=1, height=24).pack(side="left", padx=15)

        btn(toolbar, "Danh dau da xu ly", self._resolve,
            variant="success", icon="✔").pack(side="left", padx=4)
        btn(toolbar, "Lam moi", self.refresh,
            variant="ghost", icon="🔄").pack(side="right")

        # Main issues list card
        i_outer, wrap = make_card(self, padx=14, pady=14)
        i_outer.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("id", "phong", "nguoi_bao", "mo_ta", "trang_thai", "thoi_gian")
        hdrs = ("ID", "Phong", "Nguoi bao", "Mo ta su co", "Trang thai", "Thoi gian")
        wids = (50, 90, 130, 340, 110, 150)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # ── ratings summary panel ──────────────────────────────────────────────
        r_outer, rating_lbl_wrap = make_card(self, padx=14, pady=10)
        r_outer.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(rating_lbl_wrap, text="⭐  Danh sach danh gia gan nhat",
                 bg=C_SURFACE, font=F_BODY_B).pack(anchor="w")

        rating_cols = ("phong", "nguoi_dg", "sao", "nhan_xet", "thoi_gian")
        rating_hdrs = ("Phong", "Nguoi danh gia", "So sao", "Nhan xet", "Thoi gian")
        rating_wids = (90, 150, 70, 360, 150)
        self._rating_tree = make_tree(rating_lbl_wrap, rating_cols,
                                      rating_hdrs, rating_wids)
        with_scrollbar(rating_lbl_wrap, self._rating_tree)
        self._refresh_ratings()

    def refresh(self) -> None:
        issues = self.feedback_ctrl.get_issues()
        f = self.filter_var.get().strip()
        if f and f != "Tat ca":
            issues = [i for i in issues if i.status == f]
        rows = [(i.issue_id, i.room_id, i.user_name,
                 i.description, i.status, i.created_at)
                for i in issues]
        assert self.tree is not None
        fill_tree(self.tree, rows)

        # colour rows by status
        self.tree.tag_configure("pending", background=C_DANGER_BG)
        self.tree.tag_configure("done", background=C_SUCCESS_BG)

        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if not vals or vals[0] == "  Khong co du lieu": continue
            status = vals[4]
            if status == "Chua xu ly":
                self.tree.item(item, tags=("pending",))
            else:
                self.tree.item(item, tags=("done",))

    def _refresh_ratings(self) -> None:
        conn_rows: list[tuple[object, object, str, object, object]] = []
        from database.sqlite_db import get_connection  # type: ignore[import-not-found]
        conn: sqlite3.Connection = get_connection()  # type: ignore[assignment]
        raw_rows = conn.execute(  # type: ignore[reportUnknownMemberType]
            "SELECT room_id, user_name, stars, comment, created_at "
            "FROM room_ratings ORDER BY created_at DESC LIMIT 100"
        ).fetchall()  # type: ignore[reportUnknownMemberType]
        rows = cast(list[tuple[object, object, int, object, object]], raw_rows)
        for r in rows:
            stars = " ★ " * r[2] + " ☆ " * (5 - r[2])
            conn_rows.append((r[0], r[1], stars, r[3], r[4]))
        fill_tree(self._rating_tree, conn_rows)

    def _resolve(self) -> None:
        assert self.tree is not None
        sel = self.tree.selection()
        if not sel:
            confirm_dialog(self, "Chưa chọn", "Hay chon mot bao cao de danh dau da giai quyet.", 
                           kind="primary", cancel_text=None)
            return
        
        vals = self.tree.item(sel[0], "values")
        if vals[0] == "  Khong co du lieu": return
        
        issue_id = int(vals[0])
        if not confirm_dialog(self, "Xác nhận xử lý", f"Danh dau su co #{issue_id} da duoc giai quyet?", 
                               kind="primary"):
            return
        self.feedback_ctrl.resolve_issue(issue_id)
        self.refresh()
        toast(self, "✅ Da cap nhat trang thai 'Da xu ly'.")


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
        # Header accent
        tk.Frame(self, bg="#fbbf24", height=4).pack(fill="x")
        
        container = tk.Frame(self, bg=C_BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        outer, card = make_card(container, padx=0, pady=0)
        outer.pack(fill="both", expand=True)

        # Inner Header
        hdr = tk.Frame(card, bg="#fffbeb", padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🔧  Bao hong thiet bi",
                 bg="#fffbeb", fg="#92400e",
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(hdr, text=self.room_name,
                 bg="#fffbeb", fg="#b45309",
                 font=("Segoe UI", 9, "bold")).pack(side="right")

        tk.Label(card,
                 text="Chon thiet bi bi hong, sau do nhap mo ta su co.",
                 bg=C_SURFACE, fg=C_MUTED, font=F_SMALL, padx=16, pady=8).pack(anchor="w")

        # Scrollable equipment list
        list_frame = tk.Frame(card, bg=C_SURFACE)
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
        footer = tk.Frame(card, bg="#f8fafc", padx=16, pady=12)
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
