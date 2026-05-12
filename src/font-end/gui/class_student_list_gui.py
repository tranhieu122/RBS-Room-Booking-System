# class_student_list_gui.py - attendance-style student list popup
from __future__ import annotations

import csv
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from gui.theme import C_BG, C_BORDER, C_MUTED, C_SURFACE, C_TEXT, btn


class ClassStudentListDialog(tk.Toplevel):
    """Non-modal attendance popup for a clicked schedule cell."""

    def __init__(
        self,
        parent: tk.Misc,
        class_info: dict[str, str],
        students: list[dict[str, Any]],
        on_student_select: Any = None,
    ) -> None:
        super().__init__(parent)
        self.title(f"Danh sach sinh vien - {class_info.get('name', 'Lop hoc')}")
        self.geometry("1040x680")
        self.minsize(860, 520)
        self.transient(parent.winfo_toplevel())

        self.class_info = class_info
        self.students = students
        self.on_student_select = on_student_select
        self.keyword_var = tk.StringVar()

        self.configure(bg=C_BG)
        self._build()
        self.center_on_parent()

    def center_on_parent(self) -> None:
        self.update_idletasks()
        root = self.master.winfo_toplevel() if self.master else self
        x = root.winfo_rootx() + (root.winfo_width() - self.winfo_width()) // 2
        y = root.winfo_rooty() + (root.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _build(self) -> None:
        header = tk.Frame(self, bg="#1a73e8", padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"Hoc phan: {self.class_info.get('name', 'Lop hoc')}",
            bg="#1a73e8",
            fg="white",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text=f" - {self.class_info.get('time', '')}",
            bg="#1a73e8",
            fg="#fff200",
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=(16, 0))
        tk.Label(
            header,
            text=f"Co mat({len(self.students)})",
            bg="#1a73e8",
            fg="#fff200",
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=(28, 0))
        tk.Button(
            header,
            text="X",
            command=self.destroy,
            bg="#1a73e8",
            fg="#0f172a",
            activebackground="#1a73e8",
            activeforeground="#0f172a",
            relief="flat",
            bd=0,
            font=("Segoe UI", 13, "bold"),
            cursor="hand2",
        ).pack(side="right")

        top = tk.Frame(self, bg=C_BG, padx=20, pady=18)
        top.pack(fill="x")

        left = tk.Frame(top, bg=C_BG)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(
            left,
            text=f"Lop: {self.class_info.get('class_id', 'N/A')}",
            bg=C_BG,
            fg=C_TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(left, text="Co mat", bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(8, 0)
        )
        tk.Label(
            left,
            text=f"(Phong hoc: {self.class_info.get('room', 'N/A')})",
            bg=C_BG,
            fg=C_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 0))

        right = tk.Frame(top, bg=C_BG)
        right.pack(side="right")
        tk.Label(right, text="Tu khoa diem danh", bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10)).pack(
            side="left", padx=(0, 12)
        )
        tk.Entry(
            right,
            textvariable=self.keyword_var,
            width=22,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10),
            fg=C_TEXT,
        ).pack(side="left", ipady=8)
        btn(right, "Luu", self._save_attendance_keyword, variant="primary", icon="💾").pack(
            side="left", padx=(12, 0)
        )

        body = tk.Frame(self, bg=C_BG, padx=20, pady=0)
        body.pack(fill="both", expand=True, pady=(0, 12))

        table = tk.Frame(body, bg=C_SURFACE, highlightthickness=1, highlightbackground=C_BORDER)
        table.pack(fill="both", expand=True)

        cols = ("stt", "ma_so", "ho_dem", "ten")
        headers = ("STT", "Ma so", "Ho dem", "Ten")
        widths = (60, 160, 520, 220)
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=18)
        for col, header, width in zip(cols, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center" if col in ("stt", "ma_so") else "w")

        vsb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        if self.students:
            for student in self.students:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        student.get("stt", ""),
                        student.get("ma_so", ""),
                        student.get("ho_dem", ""),
                        student.get("ten", ""),
                    ),
                )
        else:
            self.tree.insert("", "end", values=("", "", "Chua co sinh vien trong lop nay", ""))
        self.tree.bind("<Double-1>", self._on_click)

        footer = tk.Frame(self, bg=C_BG, padx=20, pady=0)
        footer.pack(fill="x", pady=(0, 14))
        btn(footer, "Xuat CSV", self.export_to_csv, variant="outline", icon="📤").pack(side="left")
        tk.Label(
            footer,
            text="Cua so nay khong khoa ung dung. Dong bang nut X neu khong can xem nua.",
            bg=C_BG,
            fg=C_MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

    def _save_attendance_keyword(self) -> None:
        messagebox.showinfo("Da luu", "Da luu tu khoa diem danh.")

    def export_to_csv(self) -> None:
        if not self.students:
            messagebox.showwarning("Thong bao", "Khong co du lieu de xuat.")
            return

        filename = (
            f"DanhSachSinhVien_{self.class_info.get('class_id', 'Unknown')}_"
            f"{datetime.date.today().isoformat()}.csv"
        )
        try:
            with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["stt", "ma_so", "ho_dem", "ten", "email", "phone"])
                writer.writeheader()
                writer.writerows(self.students)
            messagebox.showinfo("Thanh cong", f"Da xuat danh sach sinh vien ra file:\n{filename}")
        except OSError as exc:
            messagebox.showerror("Loi", f"Khong the xuat file: {exc}")

    def _on_click(self, event: Any) -> None:
        if not self.on_student_select:
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        vals = self.tree.item(item, "values")
        if not vals or not vals[1]:
            return
        self.on_student_select({"ma_so": vals[1], "ho_dem": vals[2], "ten": vals[3]})
