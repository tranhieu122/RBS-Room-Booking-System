# Tài Liệu Cơ Sở Dữ Liệu (Database Document)
## Hệ Thống Quản Lý Đặt Phòng Học — Nhóm 24

---

## 1. Tổng Quan

| Mục | Chi tiết |
|-----|----------|
| **Hệ quản trị CSDL** | SQLite 3 |
| **File CSDL** | `src/back end/database/sqlite_db.py` → tạo file `.db` tại runtime |
| **Schema SQL** | `src/back end/database/init_db.sql` |
| **Kết nối** | `db_config.py` → `sqlite_db.py` → `get_connection()` |
| **Số bảng** | 7 bảng |
| **Encoding** | UTF-8 |

---

## 2. Sơ Đồ Kiến Trúc Dữ Liệu

```
┌─────────────────────────────────────────────────────────┐
│                  GUI (Tkinter Frontend)                  │
└────────────────────────┬────────────────────────────────┘
                         │ gọi phương thức
┌────────────────────────▼────────────────────────────────┐
│            Controllers (Business Logic)                  │
│  AuthController | BookingController | RoomController     │
│  EquipmentController | RoomFeedbackController            │
│  UserController | ReportController                       │
└────────────────────────┬────────────────────────────────┘
                         │ truy vấn dữ liệu
┌────────────────────────▼────────────────────────────────┐
│                DAOs (Repository Pattern)                 │
│  UserDAO | RoomDAO | BookingDAO | EquipmentDAO           │
│  ScheduleDAO | RoomFeedbackDAO                           │
└────────────────────────┬────────────────────────────────┘
                         │ ánh xạ row → object
┌────────────────────────▼────────────────────────────────┐
│              Models (Python Dataclasses)                 │
│  User | Room | Booking | Equipment | Schedule            │
└────────────────────────┬────────────────────────────────┘
                         │ SQL (INSERT/SELECT/UPDATE/DELETE)
┌────────────────────────▼────────────────────────────────┐
│                  SQLite Database                         │
│  users | rooms | bookings | equipment | schedules        │
│  room_ratings | room_issues                              │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Mô Tả Chi Tiết Các Bảng

### 3.1 Bảng `users` — Người Dùng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | TEXT | PRIMARY KEY | UUID sinh ngẫu nhiên (`uuid4`) |
| `username` | TEXT | NOT NULL, UNIQUE | Tên đăng nhập (duy nhất) |
| `full_name` | TEXT | NOT NULL | Họ và tên đầy đủ |
| `role` | TEXT | NOT NULL | Vai trò: `'Sinh vien'`, `'Giang vien'`, `'Admin'` |
| `email` | TEXT | NOT NULL, UNIQUE | Địa chỉ email (duy nhất) |
| `phone` | TEXT | NOT NULL | Số điện thoại |
| `password_hash` | TEXT | NOT NULL | Mật khẩu đã hash (PBKDF2 hoặc SHA-256 legacy) |
| `status` | TEXT | NOT NULL, DEFAULT `'Hoat dong'` | Trạng thái: `'Hoat dong'`, `'Bi khoa'` |

**Model Python:** `User` (dataclass) — `src/back end/models/user.py`  
**DAO:** `UserDAO` — `list_all()`, `find_by_id()`, `find_by_username()`, `save()`, `update()`, `delete()`

---

### 3.2 Bảng `rooms` — Phòng Học

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | TEXT | PRIMARY KEY | UUID sinh ngẫu nhiên |
| `name` | TEXT | NOT NULL, UNIQUE | Tên phòng (ví dụ: `'A101'`) |
| `capacity` | INTEGER | NOT NULL | Sức chứa (số chỗ ngồi) |
| `room_type` | TEXT | NOT NULL | Loại phòng: `'Phong hoc'`, `'Hoi truong'`, v.v. |
| `equipment` | TEXT | NOT NULL, DEFAULT `''` | Danh sách thiết bị (chuỗi mô tả) |
| `status` | TEXT | NOT NULL, DEFAULT `'Hoat dong'` | Trạng thái: `'Hoat dong'`, `'Bao tri'`, `'Dong cua'` |

**Model Python:** `Room` (dataclass) — `src/back end/models/room.py`  
**DAO:** `RoomDAO` — `list_all()`, `find_by_id()`, `save()`, `update()`, `delete()`

---

### 3.3 Bảng `bookings` — Đặt Phòng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | TEXT | PRIMARY KEY | UUID sinh ngẫu nhiên |
| `user_id` | TEXT | NOT NULL, FK → `users.id` | Người đặt phòng |
| `user_name` | TEXT | NOT NULL | Tên người đặt (denormalized cache) |
| `room_id` | TEXT | NOT NULL, FK → `rooms.id` | Phòng được đặt |
| `booking_date` | TEXT | NOT NULL | Ngày đặt (định dạng `YYYY-MM-DD`) |
| `slot` | TEXT | NOT NULL | Tiết học: `'Tiet 1-3'`, `'Tiet 4-6'`, `'Tiet 7-9'`, `'Tiet 10-12'` |
| `purpose` | TEXT | NOT NULL | Mục đích sử dụng |
| `status` | TEXT | NOT NULL, DEFAULT `'Cho duyet'` | Trạng thái: `'Cho duyet'`, `'Da duyet'`, `'Tu choi'`, `'Da huy'` |
| `rejection_reason` | TEXT | NOT NULL, DEFAULT `''` | Lý do từ chối (nếu có) |

**Foreign Keys:** `user_id` → `users(id)` (N:1) · `room_id` → `rooms(id)` (N:1)  
**Model Python:** `Booking` (dataclass) — `src/back end/models/booking.py`  
**DAO:** `BookingDAO` — `list_all()`, `find_by_id()`, `find_by_user()`, `find_by_room()`, `save()`, `update_status()`

---

### 3.4 Bảng `equipment` — Thiết Bị

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | TEXT | PRIMARY KEY | UUID sinh ngẫu nhiên |
| `name` | TEXT | NOT NULL | Tên thiết bị |
| `equipment_type` | TEXT | NOT NULL | Loại: `'May chieu'`, `'May tinh'`, `'Dieu hoa'`, v.v. |
| `room_id` | TEXT | NOT NULL, FK → `rooms.id` | Phòng chứa thiết bị |
| `status` | TEXT | NOT NULL | Trạng thái: `'Hoat dong'`, `'Bao tri'`, `'Hong'` |
| `purchase_date` | TEXT | NOT NULL | Ngày mua (`YYYY-MM-DD`) |

**Foreign Key:** `room_id` → `rooms(id)` (N:1)  
**Model Python:** `Equipment` (dataclass) — `src/back end/models/equipment.py`  
**DAO:** `EquipmentDAO` — `list_all()`, `find_by_id()`, `find_by_room()`, `save()`, `update()`, `delete()`

---

### 3.5 Bảng `schedules` — Lịch Phòng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Khóa tự tăng |
| `room_id` | TEXT | NOT NULL, FK → `rooms.id` | Phòng áp dụng lịch |
| `weekday` | TEXT | NOT NULL | Thứ: `'Thu 2'` … `'Thu 7'`, `'Chu nhat'` |
| `slot` | TEXT | NOT NULL | Tiết: `'Tiet 1-3'`, `'Tiet 4-6'`, `'Tiet 7-9'`, `'Tiet 10-12'` |
| `label` | TEXT | NOT NULL, DEFAULT `''` | Nhãn (tên lớp/sự kiện chiếm slot) |
| `status` | TEXT | NOT NULL, DEFAULT `'Trong'` | `'Trong'` (trống) hoặc `'Co lich'` (đã có lịch) |

**Ràng buộc UNIQUE:** `(room_id, weekday, slot)` — không cho phép trùng lịch  
**Foreign Key:** `room_id` → `rooms(id)` (N:1)  
**Model Python:** `Schedule` (dataclass) — `src/back end/models/schedule.py`  
**DAO:** `ScheduleDAO` — `find_by_room()`, `upsert()`, `clear_room()`

---

### 3.6 Bảng `room_ratings` — Đánh Giá Phòng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Khóa tự tăng |
| `room_id` | TEXT | NOT NULL, FK → `rooms.id` | Phòng được đánh giá |
| `user_id` | TEXT | NOT NULL, FK → `users.id` | Người đánh giá |
| `user_name` | TEXT | NOT NULL | Tên người đánh giá (cache) |
| `stars` | INTEGER | NOT NULL, CHECK(1–5) | Số sao đánh giá (1 đến 5) |
| `comment` | TEXT | NOT NULL, DEFAULT `''` | Nhận xét (tùy chọn) |
| `created_at` | TEXT | NOT NULL, DEFAULT `datetime('now')` | Thời điểm đánh giá |

**Foreign Keys:** `room_id` → `rooms(id)` · `user_id` → `users(id)`  
**DAO:** `RoomFeedbackDAO` — `list_ratings()`, `add_rating()`, `avg_stars()`

---

### 3.7 Bảng `room_issues` — Sự Cố Phòng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Khóa tự tăng |
| `room_id` | TEXT | NOT NULL, FK → `rooms.id` | Phòng xảy ra sự cố |
| `user_id` | TEXT | NOT NULL, FK → `users.id` | Người báo cáo |
| `user_name` | TEXT | NOT NULL | Tên người báo cáo (cache) |
| `description` | TEXT | NOT NULL | Mô tả sự cố |
| `status` | TEXT | NOT NULL, DEFAULT `'Chua xu ly'` | `'Chua xu ly'`, `'Dang xu ly'`, `'Da xu ly'` |
| `notes` | TEXT | NOT NULL, DEFAULT `''` | Ghi chú của Admin khi xử lý |
| `created_at` | TEXT | NOT NULL, DEFAULT `datetime('now')` | Thời điểm báo cáo |

**Foreign Keys:** `room_id` → `rooms(id)` · `user_id` → `users(id)`  
**DAO:** `RoomFeedbackDAO` — `list_issues()`, `add_issue()`, `update_issue()`

---

## 4. Sơ Đồ Quan Hệ Thực Thể

### Tóm Tắt Các Quan Hệ

| Bảng con | Cột FK | → Bảng cha | Cardinality |
|----------|--------|------------|-------------|
| `bookings` | `user_id` | `users` | N : 1 |
| `bookings` | `room_id` | `rooms` | N : 1 |
| `equipment` | `room_id` | `rooms` | N : 1 |
| `schedules` | `room_id` | `rooms` | N : 1 |
| `room_ratings` | `room_id` | `rooms` | N : 1 |
| `room_ratings` | `user_id` | `users` | N : 1 |
| `room_issues` | `room_id` | `rooms` | N : 1 |
| `room_issues` | `user_id` | `users` | N : 1 |

> Xem sơ đồ đầy đủ tại: `Docs/Design/Diagram/database_erd.drawio`

---

## 5. Relational Model

```
users(id, username*, full_name, role, email*, phone, password_hash, status)
rooms(id, name*, capacity, room_type, equipment, status)
bookings(id, user_id→users, room_id→rooms, user_name, booking_date, slot, purpose, status, rejection_reason)
equipment(id, name, equipment_type, room_id→rooms, status, purchase_date)
schedules(id, room_id→rooms, weekday, slot, label, status)   UNIQUE(room_id, weekday, slot)
room_ratings(id, room_id→rooms, user_id→users, user_name, stars, comment, created_at)
room_issues(id, room_id→rooms, user_id→users, user_name, description, status, notes, created_at)
```

> **Ký hiệu:** `id` = Primary Key · `attr*` = UNIQUE · `→bảng` = Foreign Key

---

## 6. Chỉ Mục (Indexes)

| Bảng | Cột | Loại | Mục đích |
|------|-----|------|----------|
| `users` | `username` | UNIQUE | Tìm kiếm nhanh khi đăng nhập |
| `users` | `email` | UNIQUE | Kiểm tra trùng email |
| `rooms` | `name` | UNIQUE | Tìm phòng theo tên |
| `schedules` | `(room_id, weekday, slot)` | UNIQUE | Ngăn trùng slot lịch |

---

## 7. Business Rules & Ràng Buộc

| Quy tắc | Được thực thi ở |
|---------|-----------------|
| Mật khẩu hash bằng PBKDF2 (nâng cấp tự động từ SHA-256) | `AuthController`, `password_hash.py` |
| Email và số điện thoại phải hợp lệ | `validators.py`, `AuthController` |
| Một slot (phòng + ngày + tiết) chỉ được đặt 1 lần | `BookingController.create_booking()` |
| Đánh giá sao từ 1 đến 5 | `CHECK` constraint trong DB |
| Người dùng bị khóa không thể đăng nhập | `AuthController.authenticate()` |
| Chỉ Admin mới duyệt/từ chối booking | `BookingController` (kiểm tra role) |

---

## 8. Các Trạng Thái Dữ Liệu

### `users.status`
```
Hoat dong  ──→  Bi khoa
Bi khoa    ──→  Hoat dong  (Admin mở khóa)
```

### `bookings.status`
```
Cho duyet ──→ Da duyet (Admin duyệt)
          └→ Tu choi  (Admin từ chối, kèm rejection_reason)
Da duyet  ──→ Da huy   (User hủy trước ngày)
```

### `room_issues.status`
```
Chua xu ly ──→ Dang xu ly ──→ Da xu ly
```

### `rooms.status` / `equipment.status`
```
Hoat dong ──→ Bao tri ──→ Hoat dong
          └→ Dong cua (rooms) / Hong (equipment)
```

---

## 9. Kết Nối & Cấu Hình

```python
# db_config.py
DB_PATH = "path/to/booking_system.db"

# sqlite_db.py
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # truy cập cột theo tên
    conn.execute("PRAGMA foreign_keys = ON")  # bật FK constraints
    return conn
```

---

## 10. Tệp Liên Quan

| Tệp | Mô tả |
|-----|-------|
| `src/back end/database/init_db.sql` | Schema SQL tham chiếu (CREATE TABLE) |
| `src/back end/database/sqlite_db.py` | Quản lý kết nối, khởi tạo schema |
| `src/back end/config/db_config.py` | Đường dẫn file DB |
| `src/back end/dao/*.py` | Repository Pattern truy cập DB |
| `src/back end/models/*.py` | Python dataclasses ánh xạ từ bảng |
| `Docs/Design/Diagram/database_erd.drawio` | Sơ đồ ERD (Crow's Foot) + Relational Model |
| `Docs/Design/Diagram/architecture_layers.drawio` | Sơ đồ kiến trúc phân tầng |
