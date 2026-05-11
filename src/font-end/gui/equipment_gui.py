# equipment_gui.py  –  equipment management screen  (v2.0 - full CRUD)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from tkcalendar import DateEntry  # type: ignore[import-untyped]
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_MUTED,
                       F_INPUT, make_tree, fill_tree, with_scrollbar, # type: ignore
                       page_header, btn, search_box, labeled_entry, get_q,
                       animate_count)


class EquipmentDialog(tk.Toplevel):
    """Add / Edit equipment dialog."""

    def __init__(self, master: tk.Misc, room_controller: Any,
                 equipment: Any = None) -> None:
        super().__init__(master)  # type: ignore[arg-type]
        self.room_ctrl = room_controller
        self.result = None
        self.title("Them thiet bi" if equipment is None else "Sua thiet bi")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)  # type: ignore[arg-type]
        self.grab_set()

        self.vars = {
            "equipment_id":   tk.StringVar(value=getattr(equipment, "equipment_id",   "")),
            "name":           tk.StringVar(value=getattr(equipment, "name",           "")),
            "equipment_type": tk.StringVar(value=getattr(equipment, "equipment_type", "")),
            "room_id":        tk.StringVar(value=getattr(equipment, "room_id",        "")),
            "status":         tk.StringVar(value=getattr(equipment, "status",         "Hoat dong")),
            "purchase_date":  tk.StringVar(value=getattr(equipment, "purchase_date",  "")),
        }
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#1e1b4b")
        hdr.pack(fill="x")
        tk.Frame(hdr, bg="#4f46e5", height=3).pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg="#1e1b4b", padx=24, pady=18)
        hdr_inner.pack(fill="x")
        
        ic_bg = tk.Frame(hdr_inner, bg="#312e81", padx=10, pady=10)
        ic_bg.pack(side="left", padx=(0, 16))
        tk.Label(ic_bg, text="✏️" if "Sua" in self.title() else "➕",
                 bg="#312e81", font=("Segoe UI", 18)).pack()
                 
        title_f = tk.Frame(hdr_inner, bg="#1e1b4b")
        title_f.pack(side="left")
        tk.Label(title_f, text=self.title(),
                 bg="#1e1b4b", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(title_f,
                 text="Cập nhật chi tiết trang thiết bị hệ thống" if "Sua" in self.title()
                      else "Nhập thông tin chi tiết cho thiết bị mới",
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 9)).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        frm.pack()

        icons = {"equipment_id": "🔑", "name": "🔧",
                 "equipment_type": "📦"}
        labels_map = {"equipment_id": "MA THIET BI *", "name": "TEN THIET BI *",
                      "equipment_type": "LOAI THIET BI *"}
        for key in ("equipment_id", "name", "equipment_type"):
            labeled_entry(
                frm, labels_map[key], self.vars[key],
                icon=icons[key], width=32)

        # Date picker for purchase_date
        tk.Label(frm, text="NGAY MUA *", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 2))
        
        _init_date = self.vars["purchase_date"].get()
        try:
            _dt_val = dt.date.fromisoformat(_init_date) if _init_date else dt.date.today()
        except ValueError:
            _dt_val = dt.date.today()
        self._date_entry = DateEntry(
            frm, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd",
            background="#4f46e5", foreground="white", width=32)
        self._date_entry.set_date(_dt_val) # type: ignore
        self._date_entry.pack(fill="x", ipady=4) # type: ignore

        # Room combobox
        tk.Label(frm, text="PHONG *", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 2))
        
        # Show "RoomID - RoomName" for better selection
        rooms = self.room_ctrl.list_rooms()
        room_choices = [f"{r2.room_id} - {r2.name}" for r2 in rooms]
        
        # Determine initial value
        init_room = self.vars["room_id"].get()
        init_val = ""
        if init_room:
            for choice in room_choices:
                if choice.startswith(init_room + " -"):
                    init_val = choice
                    break
        
        self._room_selector = ttk.Combobox(frm, textvariable=self.vars["room_id"], 
                                           values=room_choices, state="readonly", width=33)
        if init_val:
            self._room_selector.set(init_val)
        self._room_selector.pack(fill="x")

        # Status combobox
        tk.Label(frm, text="TRANG THAI", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Bao tri", "Hong"],
                     state="readonly", width=33).pack(fill="x")

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(24, 0))
        
        btn(btn_row, "Lưu thông tin", self._save, variant="primary", icon="💾").pack(side="right", padx=(8, 0))
        btn(btn_row, "Hủy bỏ", self.destroy, variant="ghost").pack(side="right")

    def _save(self) -> None:
        v = {k: var.get().strip() for k, var in self.vars.items()}
        # Parse room_id from "ID - Name"
        sel_room = self._room_selector.get()
        v["room_id"] = sel_room.split(" - ")[0] if sel_room else ""
        
        # Read purchase_date from DateEntry widget
        v["purchase_date"] = self._date_entry.get_date().isoformat() # type: ignore
        if not all([v["equipment_id"], v["name"], v["equipment_type"],
                    v["room_id"], v["purchase_date"]]): # type: ignore
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long dien day du cac truong bat buoc (*).",
                                   parent=self)
            return
        self.result = v
        self.destroy()


class EquipmentManagementFrame(tk.Frame):
    def __init__(self, master: tk.Misc, equipment_controller: Any,
                 room_controller: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.equip_ctrl = equipment_controller
        self.room_ctrl  = room_controller
        self.room_var    = tk.StringVar()
        self.search_var  = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._stat_labels: dict[str, tk.Label] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Removed internal header to prevent shifting

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(self, bg=C_BG, padx=20, pady=10)
        stats_outer.pack(fill="x", pady=(0, 5))
        for i in range(5): stats_outer.columnconfigure(i, weight=1)

        stat_defs = [
            ("total",    "🔧", "TỔNG THIẾT BỊ",  "#eff6ff", "#2563eb"),
            ("active",   "✅", "ĐANG SỬ DỤNG",   "#ecfdf5", "#059669"),
            ("maintain", "⚙️", "ĐANG BẢO TRÌ",   "#fffbeb", "#d97706"),
            ("broken",   "❌", "NGỪNG HOẠT ĐỘNG", "#fff1f2", "#e11d48"),
            ("rooms",    "🏫", "PHÒNG CÓ TB",    "#f0f9ff", "#0369a1"),
        ]
        
        from gui.theme import make_card
        for i, (key, icon, label, bg, fg) in enumerate(stat_defs):
            outer, chip = make_card(stats_outer, padx=16, pady=14, shadow=False)
            outer.config(highlightthickness=1, highlightbackground="#e2e8f0")
            outer.grid(row=0, column=i, sticky="nsew", padx=6)
            chip.config(bg="white") # Keep card white, icon area colored
            
            # Icon Circle
            ic_f = tk.Frame(chip, bg=bg, width=40, height=40)
            ic_f.pack_propagate(False)
            ic_f.pack(side="left")
            tk.Label(ic_f, text=icon, bg=bg, font=("Segoe UI", 14)).pack(expand=True)
            
            # Info container
            info_f = tk.Frame(chip, bg="white")
            info_f.pack(side="left", fill="both", expand=True, padx=(12, 0))
            
            tk.Label(info_f, text=label, bg="white", fg="#94a3b8",
                     font=("Segoe UI", 7, "bold")).pack(anchor="w")
            
            val_lbl = tk.Label(info_f, text="0", bg="white", fg="#1e293b",
                               font=("Segoe UI", 16, "bold"))
            val_lbl.pack(anchor="w")
            self._stat_labels[key] = val_lbl

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 15))

        # Search box
        search_box(toolbar, self.search_var, placeholder="Tìm kiếm trang thiết bị...",
                   on_type=self.refresh, width=32).pack(side="left")

        # Room filter
        tk.Label(toolbar, text="Phòng:", bg=C_BG, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(15, 6))
        room_values = ["Tất cả"] + [r.room_id for r in self.room_ctrl.list_rooms()]
        self.room_var.set("Tất cả")
        self.room_cb = ttk.Combobox(toolbar, textvariable=self.room_var,
                                    values=room_values, state="readonly", width=14, font=("Segoe UI", 10))
        self.room_cb.pack(side="left")
        self.room_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        
        tk.Frame(toolbar, bg=C_BORDER, width=1).pack(side="left", fill="y", padx=15)

        # CRUD buttons
        btn(toolbar, "Thêm Thiết Bị", self._add, variant="primary", icon="➕").pack(side="left")
        btn(toolbar, "Đồng bộ Phòng", self._sync_rooms, variant="ghost", icon="🔄").pack(side="left", padx=8)
        btn(toolbar, "Chỉnh sửa",     self._edit, variant="outline", icon="✏️").pack(side="left", padx=(0, 10))
        
        btn(toolbar, "Xóa Thiết Bị",  self._delete, variant="danger", icon="🗑️").pack(side="right")

        # Status bar
        self._status_lbl = tk.Label(toolbar, text="", bg=C_BG, fg="#64748b",
                                    font=("Segoe UI", 9))
        self._status_lbl.pack(side="right", padx=8)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "ten", "loai", "phong", "trang_thai", "ngay_mua")
        hdrs = ("Ma TB", "Ten thiet bi", "Loai", "Phong", "Trang thai", "Ngay mua")
        wids = (90, 220, 140, 90, 120, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)
        
        # Configure status tags for visual cues
        self.tree.tag_configure("maintain", background="#fffbeb") # Light Amber
        self.tree.tag_configure("broken",   background="#fff1f2") # Light Rose
        self.tree.tag_configure("active",   background="white")

    def refresh(self) -> None:
        selected = self.room_var.get().strip()
        room_filter = "" if selected in ("Tất cả", "") else selected
        q = get_q(self.search_var, "Tìm kiếm trang thiết bị...")
        all_eq = self.equip_ctrl.list_equipment(room_filter)
        if q:
            all_eq = [e for e in all_eq
                      if q in e.name.lower() or q in e.equipment_id.lower()
                      or q in e.equipment_type.lower()]
        
        assert self.tree is not None
        # Clear and refill with tags
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for e in all_eq:
            tag = ""
            if e.status == "Bao tri": tag = "maintain"
            elif e.status == "Hong": tag = "broken"
            else: tag = "active"
            
            self.tree.insert("", "end", values=(
                e.equipment_id, e.name, e.equipment_type,
                e.room_id, e.status, e.purchase_date
            ), tags=(tag,))

        # Update stat chips (always from full dataset)
        all_eq_full = self.equip_ctrl.list_equipment("")
        total    = len(all_eq_full)
        active   = sum(1 for e in all_eq_full if e.status == "Hoat dong")
        maintain = sum(1 for e in all_eq_full if e.status == "Bao tri")
        broken   = sum(1 for e in all_eq_full if e.status == "Hong")
        rooms_with = len({e.room_id for e in all_eq_full if e.room_id})
        for key, val in (("total", total), ("active", active),
                         ("maintain", maintain), ("broken", broken),
                         ("rooms", rooms_with)):
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

        shown = len(all_eq)
        self._status_lbl.config(
            text=f"Hien thi {shown}/{total} thiet bi"
            if shown < total else f"Tong: {total} thiet bi")

    def _selected_id(self) -> str | None:
        assert self.tree is not None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _sync_rooms(self) -> None:
        count = self.equip_ctrl.sync_from_rooms(self.room_ctrl)
        self.refresh()
        if count > 0:
            messagebox.showinfo("Thành công", f"Đã đồng bộ {count} thiết bị mới từ dữ liệu phòng học.")
        else:
            messagebox.showinfo("Thông tin", "Tất cả thiết bị đã được đồng bộ.")

    def _add(self) -> None:
        dlg = EquipmentDialog(self, self.room_ctrl)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.equip_ctrl.save_equipment(dlg.result)
        except Exception as e:
            messagebox.showerror("Loi khi luu thiet bi", str(e))
            return
        # Reset filter to show all so the newly added item is visible
        self.room_var.set("Tất cả")
        self.refresh()
        messagebox.showinfo("Thanh cong",
                            f"Da them thiet bi '{dlg.result['name']}'.")

    def _edit(self) -> None:
        eid = self._selected_id()
        if eid is None:
            confirm_dialog(self, "Chưa chọn", "Hay chon thiet bi can sua.", 
                           kind="warning", cancel_text=None)
            return
        # Find the equipment object
        all_eq = self.equip_ctrl.list_equipment()
        equip  = next((e for e in all_eq if e.equipment_id == eid), None)
        dlg = EquipmentDialog(self, self.room_ctrl, equipment=equip)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.equip_ctrl.save_equipment(dlg.result)
        except Exception as e:
            confirm_dialog(self, "Loi khi cap nhat thiet bi", str(e), kind="danger", cancel_text=None)
            return
        self.refresh()

    def _delete(self) -> None:
        eid = self._selected_id()
        if eid is None:
            confirm_dialog(self, "Chua chon", "Hay chon thiet bi can xoa.", kind="warning", cancel_text=None)
            return
        if not confirm_dialog(self, "Xac nhan xoa", f"Xoa thiet bi '{eid}'?", kind="danger"):
            return
        self.equip_ctrl.delete_equipment(eid)
        self.refresh()
