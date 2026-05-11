"""PDF report export using fpdf2.

Su dung: pip install fpdf2
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path

try:
    from fpdf import FPDF
    _HAS_FPDF = True
except ImportError:
    _HAS_FPDF = False
    FPDF = object  # type: ignore[assignment,misc]


class _ReportPDF(FPDF):  # type: ignore[misc]
    """PDF voi header / footer tuy chinh."""

    def __init__(self, title: str):
        super().__init__()
        self._title = title

    def header(self) -> None:
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(26, 47, 94)          # #1a2f5e
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, self._title, ln=True, align="C", fill=True)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(
            0, 6,
            f"He Thong Quan Ly Dat Phong Hoc – Nhom 24  |  "
            f"Xuat ngay {dt.date.today().strftime('%d/%m/%Y')}",
            ln=True, align="C",
        )
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, f"Trang {self.page_no()}", align="C")


def export_report_pdf(
    output_path: str,
    title: str,
    stat_rows: list[tuple],          # (phong, tong, duyet, tuchoi, tyle%)
    summary: dict[str, int] | None = None,
) -> Path:
    """Xuat bao cao su dung phong ra file PDF.

    Args:
        output_path:  Duong dan file dau ra (*.pdf).
        title:        Tieu de bao cao.
        stat_rows:    Danh sach hang du lieu: [(room_id, total, approved, rejected, rate_pct), ...].
        summary:      Dict tong hop tu build_dashboard() (tuy chon).

    Returns:
        Path den file PDF da tao.
    Raises:
        ImportError: Neu thu vien fpdf2 chua duoc cai dat.
    """
    if not _HAS_FPDF:
        raise ImportError(
            "Chua cai dat fpdf2. Chay lenh: pip install fpdf2"
        )

    pdf = _ReportPDF(title)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)

    # ── Tong hop (neu co) ─────────────────────────────────────────────────────
    if summary:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(26, 47, 94)
        pdf.cell(0, 8, "Tong hop chung", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)

        col_w = 90
        items = list(summary.items())
        for i in range(0, len(items), 2):
            label_a, val_a = items[i]
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(col_w, 7, f"  {label_a}: {val_a}", border=1, fill=True)
            if i + 1 < len(items):
                label_b, val_b = items[i + 1]
                pdf.cell(col_w, 7, f"  {label_b}: {val_b}", border=1, fill=True)
            pdf.ln()
        pdf.ln(6)

    # ── Bang chi tiet ─────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 47, 94)
    pdf.cell(0, 8, "Chi tiet su dung tung phong", ln=True)
    pdf.set_text_color(0, 0, 0)

    headers = ["Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD (%)"]
    col_ws  = [38, 32, 32, 32, 40]

    # Header row
    pdf.set_fill_color(34, 85, 164)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    for h, w in zip(headers, col_ws):
        pdf.cell(w, 8, h, border=1, fill=True, align="C")
    pdf.ln()

    # Data rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for idx, row in enumerate(stat_rows):
        fill = idx % 2 == 0
        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        for val, w in zip(row, col_ws):
            txt = str(val) if not isinstance(val, float) else f"{val:.1f}"
            pdf.cell(w, 7, txt, border=1, fill=fill, align="C")
        pdf.ln()

    pdf.ln(10)

    # ── Chu thich ─────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(
        0, 6,
        "* Ty le SD = So lan dat duoc duyet / Tong so lan dat x 100%",
        ln=True,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def export_booking_list_pdf(
    output_path: str,
    bookings: list,       # list[Booking]
) -> Path:
    """Xuat danh sach dat phong ra PDF."""
    if not _HAS_FPDF:
        raise ImportError("Chua cai dat fpdf2. Chay lenh: pip install fpdf2")

    pdf = _ReportPDF("Danh Sach Dat Phong")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page("L")   # Landscape for wider table
    pdf.set_font("Helvetica", "", 9)

    headers = ["Ma dat", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai"]
    col_ws  = [28, 42, 20, 28, 18, 60, 28]

    # Header
    pdf.set_fill_color(34, 85, 164)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(headers, col_ws):
        pdf.cell(w, 8, h, border=1, fill=True, align="C")
    pdf.ln()

    # Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    for idx, b in enumerate(bookings):
        alt = (241, 245, 249) if idx % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*alt)
        vals = [b.booking_id, b.user_name, b.room_id,
                b.booking_date, b.slot,
                (b.purpose[:35] + "...") if len(b.purpose) > 35 else b.purpose,
                b.status]
        for val, w in zip(vals, col_ws):
            pdf.cell(w, 7, str(val), border=1, fill=True, align="C")
        pdf.ln()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path
