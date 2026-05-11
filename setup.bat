@echo off
chcp 65001 >nul
echo =============================================================
echo  HE THONG QUAN LY DAT PHONG HOC – Nhom 24
echo  Script cai dat tu dong (Windows)
echo =============================================================
echo.

:: ── Kiem tra Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Chua cai Python. Vui long tai ve tu https://python.org
    pause & exit /b 1
)
echo [OK] Python da san sang.

:: ── Tao virtual environment ───────────────────────────────────────────────────
if not exist ".venv" (
    echo [INFO] Tao virtual environment .venv ...
    python -m venv .venv
)
echo [OK] Virtual environment san sang.

:: ── Kich hoat venv ────────────────────────────────────────────────────────────
call .venv\Scripts\activate.bat

:: ── Nang cap pip ─────────────────────────────────────────────────────────────
echo [INFO] Nang cap pip ...
python -m pip install --upgrade pip --quiet

:: ── Cai thu vien runtime ──────────────────────────────────────────────────────
echo [INFO] Cai dat cac thu vien can thiet ...
pip install mysql-connector-python==9.6.0 openpyxl==3.1.5 tkcalendar==1.6.1 Pillow==12.2.0 python-dotenv fpdf2 --quiet
if errorlevel 1 (
    echo [CANH BAO] Mot so thu vien co the khong cai duoc.
    echo           He thong van chay duoc voi SQLite.
)
echo [OK] Cac thu vien da duoc cai dat.

:: ── Cai cong cu phat trien (tuy chon) ────────────────────────────────────────
echo [INFO] Cai dat cong cu test / lint (pytest, ruff, black) ...
pip install pytest ruff black --quiet
echo [OK] Cong cu phat trien san sang.

:: ── Sao chep .env neu chua co ─────────────────────────────────────────────────
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [INFO] Da tao file .env tu .env.example.
        echo        Vui long mo file .env va dien cau hinh SMTP neu muon gui email.
    )
)

:: ── Khoi tao co so du lieu (bao gom migrations) ──────────────────────────────
echo [INFO] Khoi tao co so du lieu SQLite va chay migrations ...
python -c "import sys; sys.path.insert(0,'src/back end'); from database.sqlite_db import bootstrap; bootstrap()"
if errorlevel 1 (
    echo [LOI] Khoi tao co so du lieu that bai. Kiem tra loi phia tren.
    pause & exit /b 1
)
echo [OK] Co so du lieu san sang.

echo.
echo =============================================================
echo  CAI DAT HOAN TAT!
echo.
echo  Chay ung dung:  python main.py
echo  Chay tests:     python -m pytest tests/ -v
echo  Kiem tra lint:  ruff check "src/back end" tests
echo.
echo  Tai khoan mac dinh:
echo    admin / admin123   (quan tri vien)
echo    gv01  / gv123      (giang vien)
echo    sv01  / sv123      (sinh vien)
echo =============================================================
echo.
pause
