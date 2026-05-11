#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
He Thong Quan Ly Dat Phong Hoc - BTL Nhom 24
Root launcher: runs src/back end/main.py as the application entry point.
"""
import runpy
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "src" / "back end"
FRONTEND_DIR = Path(__file__).resolve().parent / "src" / "font-end"

for d in (str(BACKEND_DIR), str(FRONTEND_DIR)):
    if d not in sys.path:
        sys.path.insert(0, d)

BACKEND_MAIN = BACKEND_DIR / "main.py"
runpy.run_path(str(BACKEND_MAIN), run_name="__main__")

