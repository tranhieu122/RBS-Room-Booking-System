# room_gui.py  –  room management screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from tkcalendar import DateEntry  # type: ignore[import-untyped]
from gui.room_detail_gui import RoomDetailDialog
from gui.room_feedback_gui import (
    RoomRatingDialog, RoomIssueDialog, EquipmentReportDialog
)
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_PRIMARY,
                       C_TEXT, C_MUTED, F_BODY_B,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box, get_q,
                       toast, confirm_dialog, animate_count)


class RoomManagementFrame(tk.Frame):
    SLOT_OPTIONS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

    def __init__(self, master: tk.Misc, room_controller: Any, booking_controller: Any = None,
                 feedback_ctrl: Any = None, current_user: Any = None,
                 equipment_ctrl: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.room_ctrl     = room_controller
        self.booking_ctrl  = booking_controller
        self.feedback_ctrl = feedback_ctrl
        self.current_user  = current_user
        self.equip_ctrl    = equipment_ctrl
        self.search_var   = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._suggest_tree: ttk.Treeview | None = None
        self._date_var = tk.StringVar(value=dt.date.today().isoformat())
        self._slot_var = tk.StringVar(value="Ca 1")
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Removed header for stability
        
        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(self, bg=C_BG)
        stats_outer.pack(fill="x", padx=0, pady=(10, 5)) # Full width
        for i in range(4): stats_outer.columnconfigure(i, weight=1)
        
        from gui.theme import make_card
        self._stat_labels = {}
        stat_defs = [
            ("total",   "🏫", "Tổng số phòng",  "#eff6ff", "#2563eb"),
            ("avail",   "✅", "Đang trống",     "#ecfdf5", "#059669"),
            ("booked",  "📅", "Đã đặt",        "#fffbeb", "#d97706"),
            ("issue",   "⚠️", "Cần bảo trì",    "#fff1f2", "#e11d48"),
        ]
        
        for i, (key, icon, label, bg, fg) in enumerate(stat_defs):
            outer, chip = make_card(stats_outer, padx=15, pady=15, shadow=True)
            outer.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            
            # Left icon badge with glow
            badge = tk.Frame(chip, bg="#f8fafc", padx=10, pady=8)
            badge.pack(side="left", padx=(0, 15))
            tk.Label(badge, text=icon, bg="#f8fafc", font=("Segoe UI", 20)).pack()
            
            txt_f = tk.Frame(chip, bg=C_SURFACE)
            txt_f.pack(side="left", fill="both", expand=True)
            
            val_lbl = tk.Label(txt_f, text="0", bg=C_SURFACE, fg=fg, font=("Segoe UI", 20, "bold"))
            val_lbl.pack(anchor="w")
            self._stat_labels[key] = val_lbl
            
            tk.Label(txt_f, text=label.upper(), bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")

            # Hover Interaction
            outer.config(highlightthickness=2, highlightbackground=C_BORDER)
            def _on_enter(e, o=outer, c=fg): o.config(highlightbackground=c)
            def _on_leave(e, o=outer): o.config(highlightbackground=C_BORDER)
            chip.bind("<Enter>", _on_enter)
            chip.bind("<Leave>", _on_leave)

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=10, pady=(10, 15))
        search_box(toolbar, self.search_var, placeholder="Tìm kiếm phòng học...", 
                   on_type=self.refresh, width=40).pack(side="left", padx=10)

        is_admin = (self.current_user is not None
                    and getattr(self.current_user, "role", "") == "Admin")
        
        if is_admin:
            tk.Frame(toolbar, bg=C_BORDER, width=1).pack(side="left", fill="y", padx=15)
            btn(toolbar, "Thêm Phòng", self._add, variant="primary", icon="+").pack(side="left")
            btn(toolbar, "Sửa", self._edit, variant="outline", icon="✏️").pack(side="left", padx=(8, 0))
            btn(toolbar, "Xóa", self._delete, variant="danger", icon="🗑️").pack(side="left", padx=(8, 0))
            btn(toolbar, "Thiết bị", self._manage_equipment, variant="ghost", icon="🔧").pack(side="left", padx=8)

        # Action panel for all users
        action_bar = tk.Frame(toolbar, bg=C_BG)
        action_bar.pack(side="right")
        
        btn(action_bar, "Đánh giá", self._rate_room, variant="accent", icon="⭐").pack(side="left", padx=4)
        btn(action_bar, "Báo lỗi", self._report_issue, variant="outline", icon="🚨").pack(side="left", padx=4)
        btn(action_bar, "Báo hỏng", self._report_equipment, variant="warning", icon="🔧").pack(side="left", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE)
        wrap.pack(fill="both", expand=True, padx=0, pady=(0, 0)) # Full width

        cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi", "danh_gia", "trang_thai")
        hdrs = ("Mã phòng", "Tên phòng", "Sức chứa", "Loại phòng",
                "Trang thiết bị", "Đánh giá", "Trạng thái")
        wids = (100, 160, 90, 140, 300, 90, 110)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # ── Panel gợi ý phòng còn trống ─────────────────────────────────────
        suggest_outer = tk.Frame(self, bg=C_BG)
        suggest_outer.pack(fill="x", padx=0, pady=(10, 0)) # Full width

        suggest_wrap = tk.Frame(suggest_outer, bg=C_SURFACE)
        suggest_wrap.pack(fill="both", expand=True)

        # Header bar – gradient xanh
        header_bar = tk.Frame(suggest_wrap, bg=C_PRIMARY, pady=0)
        header_bar.pack(fill="x")

        # Accent stripe on header: Indigo 400
        tk.Frame(header_bar, bg="#818cf8", height=3).pack(fill="x")

        header_content = tk.Frame(header_bar, bg=C_PRIMARY, padx=16, pady=10)
        header_content.pack(fill="x")
        tk.Label(header_content, text="💡", bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 15)).pack(side="left")
        tk.Label(header_content, text="  Goi y phong con trong",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(header_content,
                 text="Chon ngay va ca hoc de tim phong trong nhanh",
                 bg=C_PRIMARY, fg="#c7d2fe",
                 font=("Segoe UI", 9)).pack(side="right")

        # Body
        body = tk.Frame(suggest_wrap, bg=C_SURFACE, padx=16, pady=14)
        body.pack(fill="both", expand=True)

        # ── Controls row ──────────────────────────────────────────────────────
        ctrl_row = tk.Frame(body, bg=C_SURFACE)
        ctrl_row.pack(fill="x", pady=(0, 12))

        # Ngay label + entry với viền focus
        tk.Label(ctrl_row, text="📅  Ngay:", bg=C_SURFACE,
                 fg=C_TEXT, font=F_BODY_B).pack(side="left")

        date_frame = tk.Frame(ctrl_row, bg=C_SURFACE, highlightthickness=1,
                              highlightbackground=C_BORDER)
        date_frame.pack(side="left", padx=(6, 18))
        date_entry = DateEntry(  # type: ignore[possibly-unbound]
            date_frame, textvariable=self._date_var,
            width=12, date_pattern="yyyy-mm-dd",
            background=C_PRIMARY, foreground="white",
            weekendbackground="white", weekendforeground="black",
            state="readonly",
            borderwidth=1, font=("Segoe UI", 11),
        )
        date_entry.pack(padx=4, pady=4)
        date_entry.bind("<<DateEntrySelected>>",  # type: ignore[attr-defined]
            lambda *_: self.after(100, self._show_available))

        # Ca hoc label + combobox
        tk.Label(ctrl_row, text="🕐  Ca hoc:", bg=C_SURFACE,
                 fg=C_TEXT, font=F_BODY_B).pack(side="left")
        slot_cb = ttk.Combobox(ctrl_row, textvariable=self._slot_var,
                               values=self.SLOT_OPTIONS, state="readonly",
                               width=9, font=("Segoe UI", 11))
        slot_cb.pack(side="left", padx=(6, 18), ipady=4)

        btn(ctrl_row, "Xem phong trong", self._show_available,
            variant="primary", icon="🔍").pack(side="left")

        self._suggest_status = tk.Label(ctrl_row, text="", bg=C_SURFACE,
                                        fg=C_MUTED, font=("Segoe UI", 9, "italic"))
        self._suggest_status.pack(side="left", padx=(14, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        tk.Frame(body, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 10))

        # ── Result treeview (chiều cao cố định 7 dòng) ────────────────────────
        s_cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi")
        s_hdrs = ("Ma phong", "Ten phong", "Suc chua", "Loai phong", "Trang thiet bi")
        s_wids = (110, 180, 90, 160, 280)
        self._suggest_tree = make_tree(body, s_cols, s_hdrs, s_wids, height=7)
        with_scrollbar(body, self._suggest_tree)

    def refresh(self) -> None:
        rows = []
        q = get_q(self.search_var, "Tìm kiếm phòng học...")
        all_rooms = self.room_ctrl.list_rooms("")
        filtered = self.room_ctrl.list_rooms(q)
        
        for r in filtered:
            rating = "N/A"
            if self.feedback_ctrl:
                avg = self.feedback_ctrl.rating_dao.average_stars(r.room_id)
                rating = f"{avg} ⭐" if avg > 0 else "Chưa có"
            rows.append((r.room_id, r.name, r.capacity,
                         r.room_type, r.equipment, rating, r.status))
        assert self.tree is not None
        fill_tree(self.tree, rows)
        
        # Update Stats
        n_total = len(all_rooms)
        n_avail = sum(1 for r in all_rooms if r.status == "Hoat dong") # simplistic
        n_issue = sum(1 for r in all_rooms if r.status == "Bao tri")
        n_booked = n_total - n_avail # simplistic
        
        if hasattr(self, "_stat_labels"):
            animate_count(self._stat_labels["total"], n_total)
            animate_count(self._stat_labels["avail"], n_avail)
            animate_count(self._stat_labels["booked"], n_booked)
            animate_count(self._stat_labels["issue"], n_issue)

    def _selected_room_id(self) -> str | None:
        assert self.tree is not None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _add(self) -> None:
        dlg = RoomDetailDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.room_ctrl.save_room(dlg.result)
        except ValueError as err:
            confirm_dialog(self, "Lỗi dữ liệu", str(err), kind="danger", cancel_text=None)
            return
        self.refresh()
        toast(self, "Da them phong hoc moi.", kind="success")

    def _edit(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong can sua.", 
                           kind="warning", cancel_text=None)
            return
        dlg = RoomDetailDialog(self, room=self.room_ctrl.get_room(rid))
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.room_ctrl.save_room(dlg.result)
        except ValueError as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()
        toast(self, "Da cap nhat thong tin phong.", kind="success")

    def _delete(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong can xoa.", 
                           kind="warning", cancel_text=None)
            return
        if not confirm_dialog(self, "Xac nhan xoa", f"Ban co chac muon xoa phong '{rid}'?", kind="danger"):
            return
        self.room_ctrl.delete_room(rid)
        self.refresh()
        toast(self, "Da xoa phong hoc.", kind="info")

    def _manage_equipment(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong de quan ly thiet bi.", 
                           kind="warning", cancel_text=None)
            return
            
        from gui.equipment_gui import EquipmentDialog
        dlg = EquipmentDialog(self, self.room_ctrl)
        # Pre-select the current room
        rooms = self.room_ctrl.list_rooms()
        for r2 in rooms:
            if r2.room_id == rid:
                dlg._room_selector.set(f"{r2.room_id} - {r2.name}")
                break
        
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.equip_ctrl.save_equipment(dlg.result)
                self.refresh()
                toast(self, f"Da lien ket thiet bi voi phong {rid}.", kind="success")
            except Exception as e:
                confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)

    def _get_selected_room(self) -> tuple[str | None, str | None]:
        """Return (room_id, room_name) of selected row, or (None, None)."""
        rid = self._selected_room_id()
        if rid is None:
            return None, None
        rooms: dict[str, Any] = {r.room_id: r for r in self.room_ctrl.list_rooms()}
        room = rooms.get(rid)
        name: str = str(room.name) if room else rid
        return rid, name

    def _rate_room(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong can danh gia.", 
                           kind="warning", cancel_text=None)
            return
        assert name is not None
        if self.feedback_ctrl is None or self.current_user is None:
            confirm_dialog(self, "Chưa sẵn sàng", "Tinh nang chua duoc ket noi.", 
                           kind="primary", cancel_text=None)
            return
        RoomRatingDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _report_issue(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong can bao loi.", 
                           kind="warning", cancel_text=None)
            return
        assert name is not None
        if self.feedback_ctrl is None or self.current_user is None:
            confirm_dialog(self, "Chưa sẵn sàng", "Tinh nang chua duoc ket noi.", 
                           kind="primary", cancel_text=None)
            return
        RoomIssueDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _report_equipment(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            confirm_dialog(self, "Chưa chọn phòng", "Hay chon phong can bao hong thiet bi.", 
                           kind="warning", cancel_text=None)
            return
        if self.equip_ctrl is None:
            confirm_dialog(self, "Chưa sẵn sàng", "Tinh nang chua duoc ket noi.", 
                           kind="primary", cancel_text=None)
            return
        EquipmentReportDialog(self, rid, name or rid, self.current_user, 
                              self.equip_ctrl, self.feedback_ctrl,
                              on_done=self.refresh)

    def _show_available(self) -> None:
        if self.booking_ctrl is None:
            confirm_dialog(self, "Chưa sẵn sàng", "Tinh nang goi y chua duoc ket noi.", 
                           kind="primary", cancel_text=None)
            return
        date_text = self._date_var.get().strip()
        slot = self._slot_var.get()
        try:
            dt.date.fromisoformat(date_text)
        except ValueError:
            messagebox.showerror("Ngay khong hop le",
                                 "Vui long nhap ngay theo dinh dang YYYY-MM-DD.")
            return
        rooms = self.room_ctrl.get_available_rooms(
            self.booking_ctrl, date_text, slot)
        rows = [(r.room_id, r.name, r.capacity, r.room_type, r.equipment)
                for r in rooms]
        assert self._suggest_tree is not None
        fill_tree(self._suggest_tree, rows)
        count = len(rows)
        if count:
            self._suggest_status.config(
                text=f"✅  Tim thay {count} phong trong  |  {date_text}  –  {slot}",
                fg="#16a34a")
        else:
            self._suggest_status.config(
                text=f"⚠️  Khong co phong trong  |  {date_text}  –  {slot}",
                fg="#db2777")
