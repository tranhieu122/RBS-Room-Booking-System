# room_detail_gui.py  –  room add/edit dialog  (v2.0 – styled inputs + validation)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from gui.theme import (C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED, C_DANGER, F_INPUT, btn, labeled_entry, confirm_dialog)


class RoomDetailDialog(tk.Toplevel):
    def __init__(self, master, room=None) -> None:
        super().__init__(master)
        self._is_edit = room is not None
        self.title("Sua thong tin phong" if self._is_edit else "Them phong hoc moi")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.result = None
        self.vars = {
            "room_id":   tk.StringVar(value=getattr(room, "room_id",   "")),
            "name":      tk.StringVar(value=getattr(room, "name",      "")),
            "capacity":  tk.StringVar(value=str(getattr(room, "capacity", ""))),
            "room_type": tk.StringVar(value=getattr(room, "room_type", "Phong hoc")),
            "equipment": tk.StringVar(value=getattr(room, "equipment", "")),
            "status":    tk.StringVar(value=getattr(room, "status",    "Hoat dong")),
        }
        self._build()
        self.transient(master)
        self.grab_set()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=20, pady=14)
        hdr.pack(fill="x")
        icon = "✏️" if self._is_edit else "➕"
        tk.Label(hdr, text=f"{icon}  {'Sua thong tin phong' if self._is_edit else 'Them phong hoc moi'}",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(hdr,
                 text="Cap nhat thong tin phong hoc trong he thong",
                 bg=C_PRIMARY, fg="#c7d2fe",
                 font=("Segoe UI", 9)).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=20)
        frm.pack(fill="both", expand=True)

        # ── Styled entries ───────────────────────────────────────────────────
        field_defs = [
            ("room_id",   "MA PHONG *",              "🔑"),
            ("name",      "TEN PHONG *",             "📛"),
            ("capacity",  "SUC CHUA (NGUOI) *",      "👥"),
            ("room_type", "LOAI PHONG",               "📚"),
            ("equipment", "TRANG THIET BI",           "🔧"),
        ]
        for key, label, icon in field_defs:
            outer, _ = labeled_entry(frm, label, self.vars[key],
                                     icon=icon, width=34)
            outer.pack(fill="x", pady=(6, 0))

        # Lock room_id when editing
        if self._is_edit:
            # Find the entry inside the outer frame and disable it
            self.after(10, self._lock_room_id)

        # ── Status ───────────────────────────────────────────────────────────
        tk.Label(frm, text="TRANG THAI", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 2))
        status_wrap = tk.Frame(frm, bg=C_SURFACE, highlightthickness=1,
                               highlightbackground=C_BORDER)
        status_wrap.pack(fill="x")
        ttk.Combobox(status_wrap, textvariable=self.vars["status"],
                     values=["Hoat dong", "Bao tri"],
                     state="readonly", width=33,
                     font=("Segoe UI", 10)).pack(padx=6, pady=6)

        # ── Hint line ────────────────────────────────────────────────────────
        hint = tk.Frame(frm, bg="#eef2ff", highlightthickness=1,
                        highlightbackground="#c7d2fe")
        hint.pack(fill="x", pady=(14, 0))
        tk.Label(hint,
                 text="ⓘ  Cac truong co dau * la bat buoc. Ma phong la duy nhat.",
                 bg="#eef2ff", fg="#4f46e5",
                 font=("Segoe UI", 8), anchor="w").pack(
            fill="x", padx=10, pady=6)

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=C_SURFACE, padx=26)
        btn_row.pack(fill="x", pady=(0, 20))
        btn(btn_row, "Luu lai", self._save, icon="💾").pack(side="left", padx=(0, 8))
        btn(btn_row, "Huy", self.destroy, variant="ghost").pack(side="left")

    def _lock_room_id(self) -> None:
        """Disable room_id entry when editing (cannot change primary key)."""
        for widget in self.winfo_children():
            self._find_and_disable(widget)

    def _find_and_disable(self, widget: tk.Misc) -> None:
        for child in widget.winfo_children():
            if isinstance(child, tk.Entry) and child.cget("textvariable") == str(self.vars["room_id"]):
                child.config(state="disabled", fg="#94a3b8", disabledforeground="#94a3b8")
                return
            self._find_and_disable(child)

    def _save(self) -> None:
        v = {k: var.get().strip() for k, var in self.vars.items()}
        # Validation
        if not v["room_id"]:
            confirm_dialog(self, "Thiếu thông tin", "Ma phong khong duoc de trong.", 
                           kind="warning", cancel_text=None)
            return
        if not v["name"]:
            confirm_dialog(self, "Thiếu thông tin", "Ten phong khong duoc de trong.", 
                           kind="warning", cancel_text=None)
            return
        if not v["capacity"]:
            confirm_dialog(self, "Thiếu thông tin", "Suc chua khong duoc de trong.", 
                           kind="warning", cancel_text=None)
            return
        try:
            cap = int(v["capacity"])
            if cap <= 0:
                raise ValueError
        except ValueError:
            confirm_dialog(self, "Dữ liệu không hợp lệ", "Suc chua phai la so nguyen duong.", 
                           kind="danger", cancel_text=None)
            return
        self.result = v
        self.destroy()
