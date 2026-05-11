# He Thong Quan Ly Dat Phong Hoc — Nhom 24

---

## Thanh vien nhom
| Ho ten | Vai tro |
|---|---|
| Tran Trung Hieu | Backend + GUI |
| Nguyen Huy Hai | Backend + Database |
| Nguyen Tuan Minh | GUI + Testing |

---

## Cong nghe su dung
- **Python 3.11+** — ngon ngu chinh
- **Tkinter / ttk** — giao dien do hoa desktop
- **SQLite** — co so du lieu noi bo
- **PBKDF2-HMAC-SHA256** — bam mat khau an toan
- **smtplib** — gui thong bao email (background thread)

---

## Kien truc he thong (MVC)

```
src/
├── back end/
│   ├── controllers/   # Logic nghiep vu (RoomController, BookingController, ...)
│   ├── dao/           # Truy cap du lieu (RoomDAO, BookingDAO, ...)
│   ├── models/        # Data classes (Room, Booking, User, Equipment, ...)
│   ├── database/      # SQLite singleton, schema, migrations
│   └── utils/         # Validators, logger, password_hash, export, email
└── font-end/
    └── gui/           # Tat ca cac man hinh Tkinter
```

**Entry point:** `src/back end/main.py` — Khoi tao `App(tk.Tk)` voi `MainShell` chua sidebar + topbar + vung noi dung.

---

## Cach chay ung dung

```bash
# 1. Kich hoat moi truong ao
.venv\Scripts\activate          # Windows
# hoac: source .venv/bin/activate   (Linux/macOS)

# 2. Cai dat thu vien (neu chua co)
pip install -r requirements.txt

# 3. Chay ung dung
python main.py
```

---

## Cai tien giao dien (UI Upgrades)

### 1. Treeview & bang du lieu
- Mau nen hang xen ke (`ROW_ODD=#f1f5f9`, `ROW_EVEN=#f8fafc`) — de phan biet cac dong
- Hang "Khong co du lieu" hien thi khi bang rong — tranh de trong trang
- `fieldbackground` cua Treeview khop voi nen ung dung — khong con vung trang xuat hien

### 2. Man hinh dang nhap (login_gui.py)
- Panel phai co canvas trang tri voi hinh tron mem (mau indigo / sky nhat)
- Hieu ung rung (`_shake`) khi nhap sai mat khau, co kiem tra widget con ton tai truoc khi chay animation
- Thong bao loi hien thi ro rang duoi o nhap

### 3. Form dat phong (booking_form_gui.py)
- O xem truoc phong thay the bang Canvas co hinh trang tri nhe nhang thay vi trang trang

### 4. Lich hoc (schedule_gui.py)
- Sua loi khoang trang phia duoi luoi lich: `stats_bar` duoc pack `side="bottom"` truoc, canvas luoi pack `side="top"`
- Hang tong ket (tally row) hien thi so slot da dung / con trong o cuoi luoi
- Thanh thong ke 5 chip (Tong, Da duyet, Cho duyet, Tu choi, Trong) + dong goi y
- Tooltip tren o lich duoc huy chinh xac khi widget bi destroy (`<Destroy>` bind)

### 5. Quan ly nguoi dung (user_gui.py)
- 5 chip thong ke (Tong, Admin, GV, SV, Bi khoa) cap nhat theo thoi gian thuc
- Nhan trang thai (status bar) ben phai toolbar
- `UserDialog` co header toi mau indigo dam `#1e1b4b` voi duong vien accent 3px
- Dialog tu dong can giua man hinh

### 6. Quan ly thiet bi (equipment_gui.py)
- 5 chip thong ke (Tong, Hoat dong, Bao tri, Hong, Phong co TB)
- Nhan trang thai ben phai toolbar
- `EquipmentDialog` co header toi + subtitle

---

## Bug da sua

### Bug nghiem trong — Trung lap phuong thuc (Duplicate Methods)

| File | Mo ta | Hau qua neu khong sua |
|---|---|---|
| `room_controller.py` | Toan bo lop bi dinh nghia 2 lan: `__init__`, `list_rooms`, `get_room`, `save_room`, `delete_room`, `get_available_rooms` | Phien ban don gian cuoi ghi de phien ban day du; `list_rooms` mat bo loc `room_type`/`status`; `save_room`/`delete_room` khong ghi log |
| `booking_controller.py` | Toan bo class body bi dinh nghia 2 lan (291 dong thu thua) | `create_booking` khong gui email cho admin, `update_booking` khong ghi log, `list_bookings` mat pagination, `update_status` mat `_fire_email` |

**Giai phap:** Xoa toan bo khoi thu hai (~200 dong du thua) tu moi file, giu lai phien ban day du tinh nang.

---

### Bug logic — Dat phong

| # | File | Mo ta | Giai phap |
|---|---|---|---|
| 1 | `booking_controller.py` | `update_booking` khong kiem tra ngay qua khu — nguoi dung co the chuyen lich ve ngay cu | Them kiem tra `update_dt < today` (ngoai tru Admin) |
| 2 | `booking_controller.py` | `create_booking` va `update_booking` khong kiem tra trang thai phong — co the dat phong cho phong "Bao tri"/"Khoa" | Them kiem tra `room_obj.status != "Hoat dong"` truoc khi tao/sua lich |

---

### Bug trang thai thiet bi

| # | File | Mo ta | Giai phap |
|---|---|---|---|
| 3 | `equipment_controller.py` | `VALID_STATUSES` thieu `"Bao tri"` — GUI gui trang thai nay nhung controller luon bao loi `ValueError` | Them `"Bao tri"` vao tap hop `VALID_STATUSES` |

---

### Bug giao dien & ung xu

| # | File | Mo ta | Giai phap |
|---|---|---|---|
| 4 | `notification_gui.py` | Su kien `<Double-1>` goi mark_read roi van tiep tuc lan vao Treeview | `_mark_read` tra ve `"break"` de dung truyen event |
| 5 | `login_gui.py` | `_shake()` goi `after()` callback sau khi widget bi huy — gay loi `TclError` | Them kiem tra `c.winfo_exists()` truoc moi buoc animation |
| 6 | `booking_list_gui.py` | Ham sap xep cot crash khi co gia tri `None` trong cot ngay | Ep kieu `str(t[0] or "").lower()` va bat `TypeError` |
| 7 | `password_hash.py` | `_verify_pbkdf2` chap nhan so vong lap = 0 — tao loi tinh toan | Kiem tra `10_000 <= iterations <= 10_000_000` |
| 8 | `dashboard_gui.py` | `list_bookings()` co the tra ve `None` — lam crash vong lap `for` | Them `or []` fallback |
| 9 | `schedule_gui.py` | Tooltip khong bi huy khi o lich bi destroy — gây rò ri bo nho | Bind `<Destroy>` de goi `tooltip.destroy()` |

---

## Tinh nang chinh cua he thong

- **Dang nhap / phan quyen**: Admin, Giang vien, Sinh vien
- **Dat phong**: Tao, sua, xoa, duyet/tu choi; kiem tra trung lich real-time
- **Quan ly phong**: CRUD day du, loc theo loai/trang thai
- **Quan ly thiet bi**: CRUD, loc theo phong/loai/trang thai
- **Lich hoc tuan**: Luoi 5x7 (slot x ngay), chuyen tuan, tooltip, thong ke
- **Bao cao & thong ke**: Xu huong theo ngay/thang, phong duoc dat nhieu nhat, ty le duyet
- **Thong bao**: Gui theo ca nhan / theo vai tro / toan bo, danh dau da doc
- **Xuat file**: Excel va PDF cho bao cao

---

## Cau truc co so du lieu (SQLite)

| Bang | Mo ta |
|---|---|
| `users` | Nguoi dung: username, full_name, role, email, phone, password_hash, status |
| `rooms` | Phong hoc: id, name, capacity, room_type, equipment, status |
| `bookings` | Yeu cau dat phong: user_id, room_id, booking_date, slot, purpose, status |
| `equipment` | Thiet bi: name, equipment_type, room_id, status, purchase_date |
| `notifications` | Thong bao: sender_id, recipient_id, title, message, is_read, created_at |
| `schedule` | Lich hoc co dinh (ngoai dat phong) |

---


