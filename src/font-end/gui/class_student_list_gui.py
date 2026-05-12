# class_student_list_gui.py – dialog showing students enrolled in a class
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
import csv
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_DARK, C_TEXT, C_PRIMARY, C_MUTED,
                       F_BODY, F_BODY_B, F_SECTION, btn, make_card, page_header,
                       ScrimmedDialog, dialog_header)

class ClassStudentListDialog(ScrimmedDialog):
    """Titanium Elite – Danh sách sinh viên theo lớp học."""

    def __init__(self, parent: tk.Misc, class_info: dict[str, str], 
                 students: list[dict[str, Any]], 
                 on_student_select: Any = None) -> None:
        super().__init__(parent, title=f"Danh sách sinh viên - {class_info.get('name', 'Lớp học')}")
        self.geometry("800x650")
        
        self.class_info = class_info
        self.students = students
        self.on_student_select = on_student_select
        
        self.configure(bg=C_BG)
        self._build()
        self.center_on_parent()

    def _build(self) -> None:
        # ── Header ────────────────────────────────────────────────────────────
        hdr = dialog_header(
            self, 
            title="DANH SÁCH SINH VIÊN", 
            subtitle=self.class_info.get("name", "Lớp học").upper(),
            variant="primary",
            icon="👨‍🎓"
        )
        hdr.pack(fill="x")


        # ── Info Bar ──────────────────────────────────────────────────────────
        info_bar = tk.Frame(self, bg=C_SURFACE, padx=24, pady=12, 
                            highlightthickness=1, highlightbackground=C_BORDER)
        info_bar.pack(fill="x")
        
        details = [
            ("Mã lớp:", self.class_info.get("class_id", "N/A")),
            ("Thời gian:", self.class_info.get("time", "N/A")),
            ("Phòng:", self.class_info.get("room", "N/A")),
            ("Sĩ số:", f"{len(self.students)} sinh viên")
        ]
        
        for lbl, val in details:
            f = tk.Frame(info_bar, bg=C_SURFACE)
            f.pack(side="left", padx=(0, 30))
            tk.Label(f, text=lbl, bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8, "bold")).pack(side="left")
            tk.Label(f, text=f" {val}", bg=C_SURFACE, fg=C_DARK, font=("Segoe UI", 9, "bold")).pack(side="left")

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=C_BG, padx=24, pady=20)
        body.pack(fill="both", expand=True)
        
        # Table Wrap
        table_outer, table_f = make_card(body, padx=0, pady=0, shadow=True)
        table_outer.pack(fill="both", expand=True)
        
        cols = ("stt", "ma_so", "ho_dem", "ten", "email", "phone")
        hdrs = ("STT", "Mã số SV", "Họ đệm", "Tên", "Email", "Số điện thoại")
        wids = (50, 100, 180, 120, 200, 120)
        
        self.tree = ttk.Treeview(table_f, columns=cols, show="headings", height=15)
        for c, h, w in zip(cols, hdrs, wids):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c in ("stt", "ma_so") else "w")
        
        vsb = ttk.Scrollbar(table_f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Populate
        for s in self.students:
            self.tree.insert("", "end", values=(
                s.get("stt", ""),
                s.get("ma_so", ""),
                s.get("ho_dem", ""),
                s.get("ten", ""),
                s.get("email", ""),
                s.get("phone", "")
            ))

        # ── Footer ────────────────────────────────────────────────────────────
        footer = tk.Frame(self, bg=C_BG, padx=24, pady=16)
        footer.pack(fill="x")
        
        btn(footer, "Xuất danh sách (CSV)", self.export_to_csv, 
            variant="outline", icon="📤").pack(side="left")
        
        btn(footer, "Đóng cửa sổ", self.destroy, 
            variant="primary").pack(side="right")

    def export_to_csv(self) -> None:
        """Export student list to a CSV file."""
        if not self.students:
            messagebox.showwarning("Thông báo", "Không có dữ liệu để xuất.")
            return
            
        import datetime
        filename = f"DanhSachSinhVien_{self.class_info.get('class_id', 'Unknown')}_{datetime.date.today().isoformat()}.csv"
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["stt", "ma_so", "ho_dem", "ten", "email", "phone"])
                writer.writeheader()
                writer.writerows(self.students)
            messagebox.showinfo("Thành công", f"Đã xuất danh sách sinh viên ra file:\n{filename}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")

    def _on_click(self, event: Any) -> None:
        if not self.on_student_select:
            return
        item = self.tree.identify_row(event.y)
        if item:
            vals = self.tree.item(item, "values")
            # Map back to dict
            student = {
                "ma_so": vals[1],
                "ho_dem": vals[2],
                "ten": vals[3]
            }
            self.on_student_select(student)
