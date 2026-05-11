# user_gui.py  –  user management screen
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED,
                       make_tree, fill_tree, with_scrollbar,
                        page_header, btn, search_box, get_q,
                        labeled_entry, eye_toggle, confirm_dialog,
                        animate_count)


class UserDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, user: Optional['User'] = None) -> None: # type: ignore
        super().__init__(master)
        self._is_edit = user is not None
        self.title("Chinh sua nguoi dung" if self._is_edit else "Them nguoi dung moi")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.result = None
        self.vars = {
            "user_id":   tk.StringVar(value=user.user_id if user else ""), # type: ignore
            "username":  tk.StringVar(value=user.username if user else ""), # type: ignore
            "full_name": tk.StringVar(value=user.full_name if user else ""), # type: ignore
            "role":      tk.StringVar(value=user.role if user else "Giang vien"), # type: ignore
            "email":     tk.StringVar(value=user.email if user else ""), # type: ignore
            "phone":     tk.StringVar(value=user.phone if user else ""), # type: ignore
            "password":  tk.StringVar(),
            "status":    tk.StringVar(value=user.status if user else "Hoat dong"), # type: ignore
        }
        self._build()
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.transient(master)
        self.grab_set()
        self.after(80, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        self.geometry(f"+{pw - self.winfo_width()//2}+{ph - self.winfo_height()//2}")

    def _build(self) -> None:
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#1e1b4b")
        hdr.pack(fill="x")
        tk.Frame(hdr, bg="#4f46e5", height=3).pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg="#1e1b4b", padx=22, pady=14)
        hdr_inner.pack(fill="x")
        icon_lbl = tk.Label(hdr_inner,
                            text="✏️" if self._is_edit else "➕",
                            bg="#1e1b4b", font=("Segoe UI", 18))
        icon_lbl.pack(side="left", padx=(0, 12))
        title_f = tk.Frame(hdr_inner, bg="#1e1b4b")
        title_f.pack(side="left")
        tk.Label(title_f,
                 text="Chinh sua nguoi dung" if self._is_edit else "Them nguoi dung moi",
                 bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_f,
                 text="Cap nhat thong tin tai khoan" if self._is_edit
                      else "Dien day du thong tin nguoi dung moi",
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 9)).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=24, pady=20)
        frm.pack()

        # --- styled labeled entries ---
        icons = {"user_id": "🔑", "username": "👤", "full_name": "📛",
                 "email": "📧", "phone": "📱", "password": "🔒"}
        labels = {"user_id": "MA NGUOI DUNG", "username": "TEN DANG NHAP",
                  "full_name": "HO VA TEN", "email": "EMAIL",
                  "phone": "SO DIEN THOAI",
                  "password": "MAT KHAU MOI (BO TRONG NEU KHONG DOI)"}
        for key in ("user_id", "username", "full_name", "email", "phone", "password"):
            show = "*" if key == "password" else ""
            _outer, entry = labeled_entry(
                frm, labels[key], self.vars[key],
                icon=icons[key], show=show, width=32)
            if key == "password":
                eye_toggle(entry.master, entry, bg=C_SURFACE).pack(
                    side="right", padx=(0, 6))

        tk.Label(frm, text="VAI TRO", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["role"],
                     values=["Admin", "Giang vien", "Sinh vien"],
                     state="readonly", width=33).pack(fill="x")

        tk.Label(frm, text="TRANG THAI", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Khoa"],
                     state="readonly", width=33).pack(fill="x")

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(20, 0))
        # Left: hint
        tk.Label(btn_row, text="* De trong mat khau de giu nguyen",
                 bg=C_SURFACE, fg="#94a3b8",
                 font=("Segoe UI", 8, "italic")).pack(side="left")
        # Right: action buttons
        btn(btn_row, "Luu lai", self._save,
            icon="💾").pack(side="right", padx=(6, 0))
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="right")

    def _save(self) -> None:
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        self.destroy()


class UserManagementFrame(tk.Frame):
    def __init__(self, master: tk.Misc, user_controller: 'UserController') -> None: # type: ignore
        super().__init__(master, bg=C_BG)
        self.user_ctrl: 'user_controller' = user_controller # type: ignore
        self.search_var = tk.StringVar()
        self.tree: Optional[ttk.Treeview] = None
        self._stat_labels: dict[str, tk.Label] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Removed header for stability

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(self, bg=C_BG, padx=20, pady=10)
        stats_outer.pack(fill="x", pady=(0, 5))
        for i in range(5): stats_outer.columnconfigure(i, weight=1)

        stat_defs = [
            ("total",    "👥", "Tổng cộng",    "#eff6ff", "#2563eb"),
            ("admin",    "🛡️", "Quản trị",     "#faf5ff", "#7c3aed"),
            ("gv",       "🎓", "Giảng viên",    "#ecfdf5", "#059669"),
            ("sv",       "🧑‍🎓","Sinh viên",    "#fffbeb", "#d97706"),
            ("locked",   "🔒", "Bị khóa",      "#fff1f2", "#e11d48"),
        ]
        
        from gui.theme import make_card
        for i, (key, icon, label, bg, fg) in enumerate(stat_defs):
            outer, chip = make_card(stats_outer, padx=15, pady=12, shadow=False)
            outer.config(highlightthickness=1, highlightbackground="#e2e8f0")
            outer.grid(row=0, column=i, sticky="nsew", padx=4)
            chip.config(bg=bg)
            
            top_f = tk.Frame(chip, bg=bg)
            top_f.pack(fill="x")
            tk.Label(top_f, text=icon, bg=bg, font=("Segoe UI", 16)).pack(side="left")
            
            val_lbl = tk.Label(top_f, text="0", bg=bg, fg=fg, font=("Segoe UI", 18, "bold"))
            val_lbl.pack(side="right")
            self._stat_labels[key] = val_lbl
            
            tk.Label(chip, text=label.upper(), bg=bg, fg="#64748b",
                     font=("Segoe UI", 8, "bold")).pack(anchor="e", pady=(4,0))

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 15))
        
        search_box(toolbar, self.search_var, placeholder="Tìm kiếm người dùng...",
                   on_type=self.refresh, width=35).pack(side="left")
        
        tk.Frame(toolbar, bg=C_BORDER, width=1).pack(side="left", fill="y", padx=15)
        
        btn(toolbar, "Thêm Mới",  self._add, variant="primary", icon="+").pack(side="left")
        btn(toolbar, "Chỉnh Sửa", self._edit, variant="outline", icon="✏️").pack(side="left", padx=10)
        
        # Status Label
        self._status_lbl = tk.Label(toolbar, text="", bg=C_BG, fg="#64748b",
                                    font=("Segoe UI", 9))
        self._status_lbl.pack(side="right", padx=8)
        
        btn(toolbar, "Xóa Bỏ",   self._delete, variant="danger", icon="🗑️").pack(side="right")

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "username", "ten", "vai_tro", "email", "phone", "trang_thai")
        hdrs = ("Ma", "Username", "Ho ten", "Vai tro", "Email", "SDT", "Trang thai")
        wids = (80, 110, 160, 110, 180, 120, 110)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

    def refresh(self) -> None:
        q = get_q(self.search_var, "Tìm kiếm người dùng...")
        users = self.user_ctrl.list_users(q) # type: ignore
        rows = [(u.user_id, u.username, u.full_name, u.role, u.email, u.phone, u.status) for u in users] # type: ignore
        if self.tree is not None:
            fill_tree(self.tree, rows) # type: ignore

        # Update stat chips
        all_users = self.user_ctrl.list_users("") # type: ignore
        total   = len(all_users)
        admins  = sum(1 for u in all_users if u.role == "Admin")
        gv      = sum(1 for u in all_users if u.role == "Giang vien")
        sv      = sum(1 for u in all_users if u.role == "Sinh vien")
        locked  = sum(1 for u in all_users if u.status == "Khoa")
        for key, val in (("total", total), ("admin", admins),
                         ("gv", gv), ("sv", sv), ("locked", locked)):
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

        shown = len(rows)
        self._status_lbl.config(
            text=f"Hien thi {shown}/{total} nguoi dung"
            if shown < total else f"Tong: {total} nguoi dung")

    def _selected_user_id(self) -> Optional[str]:
        if self.tree is None:
            return None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _get_user(self) -> Optional['User']: # type: ignore
        uid = self._selected_user_id()
        if uid is None:
            return None
        for u in self.user_ctrl.list_users(): # type: ignore
            if u.user_id == uid: # type: ignore
                return u # type: ignore
        return None

    def _add(self) -> None:
        dlg = UserDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result) # type: ignore
        except Exception as err:
            confirm_dialog(self, "Lỗi dữ liệu", str(err), kind="danger", cancel_text=None)
            return
        self.refresh()

    def _edit(self) -> None:
        user = self._get_user() # type: ignore
        if user is None:
            confirm_dialog(self, "Chưa chọn", "Hay chon nguoi dung de sua.", kind="warning", cancel_text=None)
            return
        dlg = UserDialog(self, user=user) # type: ignore
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result) # type: ignore
        except Exception as err:
            confirm_dialog(self, "Lỗi dữ liệu", str(err), kind="danger", cancel_text=None)
            return
        self.refresh()

    def _delete(self) -> None:
        uid = self._selected_user_id()
        if uid is None:
            confirm_dialog(self, "Chưa chọn", "Hay chon nguoi dung de xoa.", kind="warning", cancel_text=None)
            return
        if not confirm_dialog(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn xóa người dùng {uid}?", kind="danger"):
            return
        try:
            self.user_ctrl.delete_user(uid) # type: ignore
        except Exception as err:
            confirm_dialog(self, "Lỗi khi xóa", str(err), kind="danger", cancel_text=None)
            return
        self.refresh()
