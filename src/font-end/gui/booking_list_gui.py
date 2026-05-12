# booking_list_gui.py  –  booking list screen
from __future__ import annotations
import csv
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any
from utils.export_excel import export_rows_to_excel  # type: ignore[import-untyped]
from utils.export_ics import export_bookings_to_ics  # type: ignore[import-untyped]
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_MUTED,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box, get_q,
                       toast, confirm_dialog)

from tkcalendar import DateEntry  # type: ignore[import-untyped]


class BookingListFrame(tk.Frame):
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 current_user: Any,
                 room_controller: Any = None,
                 schedule_ctrl: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self.schedule_ctrl = schedule_ctrl
        self.current_user = current_user
        self.status_var   = tk.StringVar()
        self.search_var   = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._sort_col: str = ""
        self._sort_rev: bool = False
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Removed header for stability

        # ── Search bar ───────────────────────────────────────────────────────
        search_bar = tk.Frame(self, bg=C_BG)
        search_bar.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(search_bar, text="Tìm kiếm:", bg=C_BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))
        search_box(search_bar, self.search_var, width=32,
                   placeholder="Tìm kiếm lịch đặt...",
                   on_type=self.refresh).pack(side="left")
        tk.Label(search_bar, text="(Theo tên người đặt, mã phòng, mục đích)",
                 bg=C_BG, fg=C_MUTED, font=("Segoe UI", 8)).pack(
            side="left", padx=4)

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(toolbar, text="Trạng thái:", bg=C_BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 4))
        ttk.Combobox(toolbar, textvariable=self.status_var,
                     values=["", "Cho duyet", "Da duyet", "Tu choi"],
                     width=16, state="readonly").pack(side="left")
        btn(toolbar, "Lọc", self.refresh,
            variant="ghost", icon="🔍").pack(side="left", padx=(8, 10))
        
        # Action group separator
        tk.Frame(toolbar, bg=C_BORDER, width=1, height=24).pack(side="left", padx=10)

        btn(toolbar, "Sửa lịch", self._edit_booking,
            variant="outline", icon="✏️").pack(side="left", padx=4)
        btn(toolbar, "Xóa lịch", self._delete_booking,
            variant="danger", icon="🗑").pack(side="left", padx=4)

        if self.current_user.role == "Admin":
            tk.Frame(toolbar, bg=C_BORDER, width=1, height=24).pack(side="left", padx=10)
            btn(toolbar, "Duyệt",
                lambda: self._set_status("Da duyet"),
                variant="success", icon="✔").pack(side="left", padx=4)
            btn(toolbar, "Từ chối",
                lambda: self._set_status("Tu choi"),
                variant="danger",  icon="✖").pack(side="left", padx=4)

        # Right side exports
        export_f = tk.Frame(toolbar, bg=C_BG)
        export_f.pack(side="right")
        btn(export_f, "Excel", self._export,
            variant="ghost", icon="📊").pack(side="left", padx=2)
        if self.current_user.role in ("Admin", "Giang vien"):
            btn(export_f, "CSV", self._export_csv,
                variant="ghost", icon="📎").pack(side="left", padx=2)
        btn(export_f, "ICS", self._export_ics,
            variant="ghost", icon="📅").pack(side="left", padx=2)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "nguoi_dat", "phong", "ngay", "ca", "muc_dich", "trang_thai")
        hdrs = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai")
        wids = (90, 150, 90, 110, 80, 240, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # Sortable headers
        self._make_sortable(self.tree, list(cols))

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda _: self._edit_booking())

    def _make_sortable(self, tree: ttk.Treeview, columns: list[str]) -> None:
        """Make all column headers sortable on click; shows ▲/▼ indicator."""
        for col in columns:
            tree.heading(col, command=lambda c=col: self._sort_by(c))

    def _sort_by(self, col: str) -> None:
        assert self.tree is not None
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_rev)
        except (ValueError, TypeError):
            items.sort(key=lambda t: str(t[0] or "").lower(), reverse=self._sort_rev)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        arrow = " ▲" if not self._sort_rev else " ▼"
        # Reset all headers then set arrow on active column
        cols = ("ma", "nguoi_dat", "phong", "ngay", "ca", "muc_dich", "trang_thai")
        hdrs = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai")
        for c, h in zip(cols, hdrs):
            lbl = h + (arrow if c == col else "")
            self.tree.heading(c, text=lbl)

    def refresh(self) -> None:
        q = get_q(self.search_var, "Tìm kiếm lịch đặt...")
        bookings = self.booking_ctrl.list_bookings(
            current_user=self.current_user,
            status=self.status_var.get().strip(),
            from_today=False)
        all_rows = [
            (b.booking_id, b.user_name, b.room_id,
             b.booking_date, b.slot, b.purpose, b.status)
            for b in bookings
        ]
        if q:
            all_rows = [
                r for r in all_rows
                if q in str(r[1]).lower()   # user_name
                or q in str(r[2]).lower()   # room_id
                or q in str(r[5]).lower()   # purpose
                or q in str(r[0]).lower()   # booking_id
            ]

        assert self.tree is not None
        fill_tree(self.tree, all_rows)


    def _selected_id(self) -> str | None:
        assert self.tree is not None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _set_status(self, new_status: str) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chua chon yeu cau", "Hay chon mot ban ghi.")
            return
        
        # Handle recurring rule
        if bid.startswith("RULE-"):
            if not self.schedule_ctrl: return
            rule_id = int(bid.replace("RULE-", ""))
            # Map status: "Da duyet" -> "Hoat dong", "Tu choi" -> "Huy"
            s_map = {"Da duyet": "Hoat dong", "Tu choi": "Huy"}
            mapped_status = s_map.get(new_status, new_status)
            self.schedule_ctrl.update_rule_status(rule_id, mapped_status)
        else:
            self.booking_ctrl.update_status(bid, new_status)
            
        self.refresh()
        kind = "success" if new_status == "Da duyet" else "error"
        toast(self, f"Da cap nhat trang thai: {new_status}", kind=kind)

    def _export(self) -> None:
        assert self.tree is not None
        rows = [list(self.tree.item(item, "values"))
                for item in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Khong co du lieu", "Khong co ban ghi de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile=f"DanhSachDat_{dt.date.today()}.xlsx")
        if not path:
            return
        export_rows_to_excel(
            headers=["Ma", "Nguoi dat", "Phong", "Ngay", "Ca",
                     "Muc dich", "Trang thai"],
            rows=rows, output_path=path)
        messagebox.showinfo("Thanh cong", "Da xuat file Excel.")

    def _export_ics(self) -> None:
        bookings = getattr(self, "_last_bookings", None)
        if not bookings:
            messagebox.showinfo("Khong co du lieu", "Khong co lich dat de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar file", "*.ics")],
            initialfile=f"LichDatPhong_{dt.date.today()}.ics")
        if not path:
            return
        try:
            export_bookings_to_ics(bookings, path)
            messagebox.showinfo("Thanh cong", "Da xuat file ICS.\n"
                                "Ban co the mo bang Google Calendar, Outlook...")
        except OSError as e:
            messagebox.showerror("Loi", str(e))

    def _export_csv(self) -> None:
        assert self.tree is not None
        rows = [list(self.tree.item(item, "values"))
                for item in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Khong co du lieu", "Khong co ban ghi de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile=f"DanhSachDat_{dt.date.today()}.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Ma", "Nguoi dat", "Phong", "Ngay", "Ca",
                                  "Muc dich", "Trang thai"])
                writer.writerows(rows)
            confirm_dialog(self, "Thành công", "Đã xuất file CSV.", kind="info", cancel_text=None)
        except OSError as e:
            confirm_dialog(self, "Lỗi", str(e), kind="error", cancel_text=None)

    def _delete_booking(self) -> None:
        bid = self._selected_id()
        if bid is None:
            confirm_dialog(self, "Chưa chọn", "Hãy chọn một bản ghi.", kind="warning", cancel_text=None)
            return
        if not confirm_dialog(self, "Xác nhận xóa",
                               f"Bạn chắc chắn muốn xóa mục [{bid}]?\n"
                               "Thao tác này không thể hoàn tác.",
                               ok_text="Xóa", kind="danger"):
            return
        try:
            if bid.startswith("RULE-"):
                if not self.schedule_ctrl: return
                rule_id = int(bid.replace("RULE-", ""))
                self.schedule_ctrl.delete_rule(rule_id)
                toast(self, "Đã xóa lịch dạy chu kỳ.", kind="success")
            else:
                self.booking_ctrl.delete_booking(bid, self.current_user)
                toast(self, "Đã xóa lịch đặt phòng.", kind="success")
            self.refresh()
        except (ValueError, PermissionError) as e:
            confirm_dialog(self, "Lỗi", str(e), kind="error", cancel_text=None)

    def _edit_booking(self) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chưa chọn", "Hãy chọn một bản ghi.")
            return
        
        # Check if it's a recurring rule
        if bid.startswith("RULE-"):
            confirm_dialog(self, "Tính năng", 
                           "Để chỉnh sửa Lịch dạy chu kỳ, vui lòng truy cập mục 'Lịch dạy chu kỳ' để có đầy đủ công cụ quản lý cấu hình.",
                           kind="info", cancel_text=None)
            return

        booking = self.booking_ctrl.get_booking(bid)
        if booking is None:
            messagebox.showerror("Lỗi", "Không tìm thấy bản ghi.")
            return
        if (self.current_user.role != "Admin"
                and booking.user_id != self.current_user.user_id):
            messagebox.showerror("Không có quyền", "Bạn chỉ có thể sửa lịch của chính mình.")
            return
        _EditBookingDialog(self, booking, self.booking_ctrl,
                           self.room_ctrl, self.current_user,
                           on_done=self.refresh)


class _EditBookingDialog(tk.Toplevel):
    """Modal dialog to edit an existing booking."""

    def __init__(self, parent: tk.Misc, booking: Any, booking_ctrl: Any,
                 room_ctrl: Any, current_user: Any, on_done: Any = None):
        super().__init__(parent)
        self.title("Sua lich dat phong")
        self.resizable(False, False)
        self.grab_set()
        self.booking    = booking
        self.booking_ctrl = booking_ctrl
        self.room_ctrl  = room_ctrl
        self.current_user = current_user
        self.on_done    = on_done

        from gui.theme import C_BG, F_INPUT, btn as theme_btn # type: ignore

        self.configure(bg=C_BG)

        tk.Label(self, text="Sua lich dat phong", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(16, 8))

        def lbl(row: int, text: str) -> None:
            tk.Label(self, text=text, bg=C_BG,
                     font=("Segoe UI", 9, "bold"), anchor="w").grid(
                row=row, column=0, sticky="w", padx=20, pady=(8, 0))

        # Room
        lbl(1, "PHONG HOC")
        rooms: list[Any] = room_ctrl.list_rooms() if room_ctrl else []
        room_values = [f"{r.room_id} – {r.name}" for r in rooms if r.status == "Hoat dong"]
        self._room_map: dict[str, Any] = {f"{r.room_id} – {r.name}": r.room_id for r in rooms}
        self.room_var = tk.StringVar(value=next(
            (k for k, v in self._room_map.items() if v == booking.room_id), booking.room_id))
        ttk.Combobox(self, textvariable=self.room_var,
                     values=room_values, state="readonly", width=34).grid(
            row=2, column=0, columnspan=2, padx=20, pady=6)

        # Fixed Date picker integration
        from gui.date_picker_fixed import DatePickerWithLabel
        lbl(3, "NGAY DAT")
        self.date_var = tk.StringVar(value=booking.booking_date)
        
        # Use DatePickerWithLabel for consistent premium feel and fixed bug
        picker_frame = tk.Frame(self, bg=C_BG)
        picker_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=6, sticky="ew")
        
        self.date_picker = DatePickerWithLabel(picker_frame, self.date_var)
        self.date_picker.pack(fill="x", expand=True)
        # Store internal reference for potential direct access
        self._date_entry = self.date_picker._date_entry

        # Slot
        lbl(5, "CA HOC")
        self.slot_var = tk.StringVar(value=booking.slot)
        ttk.Combobox(self, textvariable=self.slot_var,
                     values=booking_ctrl.SLOT_OPTIONS,
                     state="readonly", width=34).grid(
            row=6, column=0, columnspan=2, padx=20, pady=6)

        # Purpose
        lbl(7, "MUC DICH SU DUNG")
        self.purpose_text = tk.Text(self, width=38, height=4,
                                    relief="solid", bd=1,
                                    font=("Segoe UI", 10))
        self.purpose_text.insert("1.0", booking.purpose)
        self.purpose_text.grid(row=8, column=0, columnspan=2, padx=20, pady=6)

        # Buttons
        btn_f = tk.Frame(self, bg=C_BG)
        btn_f.grid(row=9, column=0, columnspan=2, pady=16)
        theme_btn(btn_f, "Luu thay doi", self._save).pack(side="left", padx=6)
        theme_btn(btn_f, "Huy", self.destroy, variant="ghost").pack(side="left", padx=6)

    def _save(self) -> None:
        room_display = self.room_var.get()
        room_id = self._room_map.get(room_display, room_display.split(" – ")[0])
        date    = self.date_var.get().strip()
        slot    = self.slot_var.get()
        purpose = self.purpose_text.get("1.0", "end-1c").strip()
        try:
            self.booking_ctrl.update_booking(
                self.booking.booking_id, self.current_user,
                room_id, date, slot, purpose)
            if self.on_done:
                self.on_done()
            messagebox.showinfo("Thanh cong", "Da cap nhat lich dat phong.")
            self.destroy()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Loi", str(e))
