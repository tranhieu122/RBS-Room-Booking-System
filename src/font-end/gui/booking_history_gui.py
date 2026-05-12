# booking_history_gui.py  –  User's booking history screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Callable

from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_MUTED, C_TEXT, C_PRIMARY,
                       C_SUCCESS, C_SUCCESS_BG, C_WARNING, C_WARNING_BG, 
                       C_DANGER, C_DANGER_BG,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box, get_q, confirm_dialog, toast,
                       make_card, status_badge)

class BookingHistoryFrame(tk.Frame):
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 current_user: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.booking_ctrl = booking_controller
        self.current_user = current_user
        
        self.status_var = tk.StringVar(value="Tất cả")
        self.search_var = tk.StringVar()
        self.search_placeholder = "Tìm theo phòng, mục đích..."
        self.tree: Optional[ttk.Treeview] = None
        
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Header
        page_header(self, "📋 Lịch sử đặt phòng của tôi", 
                   subtitle="Xem và quản lý các yêu cầu đặt phòng bạn đã gửi",
                   icon="📅")
        
        # ── Toolbar / Filters ────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        
        # Status Filter
        tk.Label(toolbar, text="Trạng thái:", bg=C_BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))
        
        status_cb = ttk.Combobox(
            toolbar, 
            textvariable=self.status_var,
            values=["Tất cả", "Cho duyet", "Da duyet", "Tu choi", "Da huy"],
            width=15,
            state="readonly"
        )
        status_cb.pack(side="left")
        status_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        
        # Search Box
        tk.Label(toolbar, text="Tìm kiếm:", bg=C_BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(20, 6))
        
        s_box = search_box(
            toolbar, 
            self.search_var, 
            placeholder=self.search_placeholder,
            width=30,
            on_type=self.refresh
        )
        s_box.pack(side="left")

        # Refresh Button
        btn(toolbar, "Làm mới", self.refresh, variant="ghost", icon="🔄").pack(side="right")

        # ── Main Content Area (Treeview) ─────────────────────────────────────
        content_wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                                highlightbackground=C_BORDER, padx=14, pady=14)
        content_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ID, Ngày, Ca, Phòng, Mục đích, Trạng thái
        cols = ("id", "ngay", "ca", "phong", "muc_dich", "trang_thai")
        hdrs = ("Mã đặt", "Ngày đặt", "Ca", "Phòng", "Mục đích", "Trạng thái")
        wids = (100, 110, 80, 100, 300, 120)
        
        self.tree = make_tree(content_wrap, cols, hdrs, wids)
        with_scrollbar(content_wrap, self.tree)
        
        # Bind double-click or selection to show details
        self.tree.bind("<<TreeviewSelect>>", lambda _: self._on_row_selected())
        self.tree.bind("<Double-1>", lambda _: self._show_details_dialog())

        # ── Bottom Action Bar ────────────────────────────────────────────────
        self.actions_f = tk.Frame(self, bg=C_BG)
        self.actions_f.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_cancel = btn(self.actions_f, "Hủy yêu cầu", self._cancel_selected,
                            variant="danger", icon="✖")
        self.btn_cancel.pack(side="left", padx=5)
        self.btn_cancel.inner_btn.config(state="disabled")

        self.btn_details = btn(self.actions_f, "Xem chi tiết", self._show_details_dialog,
                             variant="outline", icon="ℹ")
        self.btn_details.pack(side="left", padx=5)
        self.btn_details.inner_btn.config(state="disabled")

    def refresh(self) -> None:
        """Fetch data and update tree."""
        if not self.tree: return
        
        status = self.status_var.get()
        if status == "Tất cả":
            status = ""
            
        # Use the correct method name 'list_bookings' from BookingController
        bookings = self.booking_ctrl.list_bookings(
            user_id=self.current_user.user_id,
            current_user=self.current_user,
            status=status,
            keyword=get_q(self.search_var, self.search_placeholder),
            from_today=False # Show past history too
        )
        
        # Sort by date descending
        bookings.sort(key=lambda x: x.booking_date, reverse=True)

        rows = [
            (b.booking_id, b.booking_date, b.slot, b.room_id, 
             b.purpose or "-", b.status)
            for b in bookings
        ]
        
        empty_msg = "Không tìm thấy dữ liệu."
        if not rows and self.current_user.role == "Admin":
            empty_msg = "Lịch sử cá nhân trống. (Xem 'Danh sách đặt' để quản lý tất cả đơn)"
            
        fill_tree(self.tree, rows, empty_msg=empty_msg)
        
        # Reset selection
        self.btn_cancel.inner_btn.config(state="disabled")
        self.btn_details.inner_btn.config(state="disabled")
        
        self._on_row_selected() # Update button states

    def _on_row_selected(self) -> None:
        """Enable/disable action buttons based on selected row."""
        if not self.tree: return
        selected = self.tree.selection()
        if not selected:
            self.btn_cancel.inner_btn.config(state="disabled")
            self.btn_details.inner_btn.config(state="disabled")
            return
            
        self.btn_details.inner_btn.config(state="normal")
        
        # Get status of first selected item
        values = self.tree.item(selected[0], "values")
        if values:
            status = values[-1]
            if status == "Cho duyet":
                self.btn_cancel.inner_btn.config(state="normal")
            else:
                self.btn_cancel.inner_btn.config(state="disabled")

    def _cancel_selected(self) -> None:
        """Cancel the selected pending booking."""
        if not self.tree: return
        selected = self.tree.selection()
        if not selected: return
        
        booking_id = self.tree.item(selected[0], "values")[0]
        
        if confirm_dialog(self, "Xác nhận hủy", 
                        f"Bạn có chắc muốn hủy yêu cầu đặt phòng {booking_id}?",
                        kind="warning"):
            try:
                self.booking_ctrl.cancel_booking(booking_id, self.current_user)
                toast(self, "Đã hủy yêu cầu thành công")
                self.refresh()
            except Exception as e:
                confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)

    def _show_details_dialog(self) -> None:
        """Show full details of the selected booking."""
        if not self.tree: return
        selected = self.tree.selection()
        if not selected: return
        
        booking_id = self.tree.item(selected[0], "values")[0]
        booking = self.booking_ctrl.get_booking(booking_id)
        if not booking: return
        
        from gui.theme import ScrimmedDialog, dialog_header
        dlg = ScrimmedDialog(self, title=f"Chi tiết đặt phòng {booking_id}")
        dlg.geometry("550x550")

        
        # Header
        hdr = dialog_header(dlg, title="CHI TIẾT ĐẶT PHÒNG", 
                           subtitle=f"Mã đặt phòng: {booking.booking_id}",
                           variant="primary", icon="ℹ️")
        hdr.pack(fill="x")
        
        body = tk.Frame(dlg, bg=C_SURFACE, padx=30, pady=25)
        body.pack(fill="both", expand=True)


        
        def _row(label: str, value: str, color: str = C_TEXT):
            f = tk.Frame(body, bg=C_SURFACE, pady=6)
            f.pack(fill="x")
            tk.Label(f, text=label, bg=C_SURFACE, fg=C_MUTED, width=15, anchor="w",
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(f, text=value, bg=C_SURFACE, fg=color, anchor="w",
                     font=("Segoe UI", 10, "bold"), wraplength=280, justify="left").pack(side="left", fill="x")

        _row("Mã đặt phòng:", booking.booking_id)
        _row("Phòng:", booking.room_id)
        _row("Ngày đặt:", booking.booking_date)
        _row("Ca học:", booking.slot)
        
        # Status Badge Row
        f_st = tk.Frame(body, bg=C_SURFACE, pady=6)
        f_st.pack(fill="x")
        tk.Label(f_st, text="Trạng thái:", bg=C_SURFACE, fg=C_MUTED, width=15, anchor="w",
                 font=("Segoe UI", 10)).pack(side="left")
        status_badge(f_st, booking.status).pack(side="left")
        
        _row("Mục đích:", booking.purpose)
        
        if booking.status == "Tu choi" and booking.rejection_reason:
            _row("Lý do từ chối:", booking.rejection_reason, color=C_DANGER)
            
        # Action Button
        btn_f = tk.Frame(body, bg=C_SURFACE, pady=20)
        btn_f.pack(fill="x", side="bottom")
        
        if booking.status == "Cho duyet":
            def _cancel_and_close():
                self._cancel_selected()
                dlg.destroy()
            btn(btn_f, "Hủy yêu cầu này", _cancel_and_close, variant="danger").pack(side="left")
            
        btn(btn_f, "Đóng", dlg.destroy, variant="outline").pack(side="right")
        
        dlg.center_on_parent()

# Add helper for centering
def _center_on_parent(dlg: tk.Toplevel) -> None:
    dlg.update_idletasks()
    parent = dlg.master
    if parent:
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (dlg.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (dlg.winfo_height() // 2)
        dlg.geometry(f"+{max(0, x)}+{max(0, y)}")

tk.Toplevel.center_on_parent = _center_on_parent # type: ignore
