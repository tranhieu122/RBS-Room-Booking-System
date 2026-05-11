"""Excel export helper."""
from __future__ import annotations
from pathlib import Path
from openpyxl import Workbook

def export_rows_to_excel(headers: list, rows: list, output_path: str) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
