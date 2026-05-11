# 📊 Giải Thích Các Biểu Đồ Thiết Kế (Design Diagrams)

**Hệ thống Quản lý Đặt Phòng Học — Nhóm 24**

Thư mục `Docs/Design/Bieu do/` chứa **2 biểu đồ** mô tả toàn bộ kiến trúc và cơ sở dữ liệu của hệ thống:

| # | Tên biểu đồ | File | Mục đích |
|---|-------------|------|----------|
| 1 | Biểu đồ lớp (Class Diagram) | `Biểu đồ lớp.png` | Mô tả cấu trúc các lớp, thuộc tính, phương thức và mối quan hệ giữa chúng |
| 2 | Sơ đồ quan hệ thực thể (ERD) | `Sơ Đồ Quan Hệ.png` | Mô tả cấu trúc các bảng trong CSDL và mối quan hệ giữa các thực thể |

---

## 1. 🏗️ Biểu Đồ Lớp (Class Diagram — UML)

### 1.1. Tổng quan

Biểu đồ lớp thể hiện kiến trúc phần mềm theo mô hình **MVC (Model – View – Controller)** kết hợp **DAO (Data Access Object)**. Hệ thống được chia thành **4 tầng chính**:

```
┌──────────────────────────────────┐
│     Controller (Điều khiển)      │  ← Xử lý logic nghiệp vụ
├──────────────────────────────────┤
│        DAO (Truy cập dữ liệu)   │  ← Thao tác CRUD với CSDL
├──────────────────────────────────┤
│        Model (Thực thể)         │  ← Định nghĩa cấu trúc dữ liệu
├──────────────────────────────────┤
│     GUI / View (Giao diện)       │  ← Hiển thị và tương tác người dùng
└──────────────────────────────────┘
```

---

### 1.2. Chi tiết các lớp

#### 🟡 Tầng Model (Thực thể dữ liệu) — *Màu vàng trên biểu đồ*

Các lớp Model là **dataclass** Python, đại diện cho các bảng trong CSDL:

| Lớp | Thuộc tính | Mô tả |
|-----|-----------|-------|
| **NguoiDung** (User) | `user_id`, `username`, `full_name`, `role`, `email`, `phone`, `password_hash`, `status` | Thông tin tài khoản người dùng (Admin, Giảng viên, Sinh viên) |
| **PhongHoc** (Room) | `room_id`, `name`, `capacity`, `room_type`, `equipment`, `status` | Thông tin phòng học (tên, sức chứa, loại phòng, trạng thái) |
| **DatPhong** (Booking) | `booking_id`, `user_name`, `room_id`, `booking_date`, `slot`, `purpose`, `status` | Yêu cầu đặt phòng của người dùng |
| **ThietBi** (Equipment) | `equipment_id`, `name`, `equipment_type`, `room_id`, `status`, `purchase_date` | Thiết bị gắn với từng phòng học |
| **LichPhong** (Schedule) | `room_id`, `weekday`, `slot`, `label`, `status` | Lịch sử dụng phòng theo tuần |
| **DanhGiaPhong** (RoomRating) | `id`, `room_id`, `user_id`, `user_name`, `stars`, `comment`, `created_at` | Đánh giá chất lượng phòng (1–5 sao) |
| **SuCoPhong** (RoomIssue) | `id`, `room_id`, `user_id`, `description`, `status`, `notes`, `created_at` | Báo cáo sự cố/hỏng hóc trong phòng |

---

#### 🟢 Tầng DAO (Data Access Object) — *Màu xanh lá trên biểu đồ*

Mỗi lớp DAO chịu trách nhiệm **truy vấn và thao tác CSDL** cho một Model tương ứng:

| Lớp DAO | Model tương ứng | Phương thức chính |
|---------|-----------------|-------------------|
| **NguoiDung** (UserDAO) | NguoiDung | `list_all()`, `find_by_id()`, `find_by_username()`, `find_by_email()`, `save()`, `delete()` |
| **PhongHoc** (RoomDAO) | PhongHoc | `list_rooms()`, `find_by_id()`, `get_room()`, `save_room()`, `delete_room()`, `get_available_rooms()` |
| **DatPhong** (BookingDAO) | DatPhong | `list_all()`, `find_by_id()`, `find_by_user()`, `save()`, `delete()` |
| **ThietBi** (EquipmentDAO) | ThietBi | `list_all()`, `find_by_id()`, `save()`, `delete()` |
| **LichPhong** (ScheduleDAO) | LichPhong | `list_by_room()`, `save()`, `delete()`, `clear_room()` |
| **DanhGiaPhong** (RatingDAO) | DanhGiaPhong | `add()`, `list_by_room()`, `average_stars()` |
| **SuCoPhong** (IssueDAO) | SuCoPhong | `report()`, `list_all()`, `update_status()` |

> **Quan hệ «uses»**: Mỗi DAO **sử dụng** (dependency) Model tương ứng để tạo và trả về các đối tượng dữ liệu.

---

#### 🟠 Tầng Controller (Điều khiển) — *Màu cam trên biểu đồ*

Mỗi Controller xử lý **logic nghiệp vụ** và làm cầu nối giữa GUI và DAO:

| Lớp Controller | DAO được sử dụng | Chức năng chính |
|----------------|-------------------|-----------------|
| **DieuKhienXacThuc** (AuthController) | NguoiDungDAO | Đăng nhập, đăng ký, đổi mật khẩu, quên mật khẩu. Kiểm tra hash mật khẩu (PBKDF2). |
| **DieuKhienNguoiDung** (UserController) | NguoiDungDAO | Quản lý danh sách người dùng (CRUD), tìm kiếm, xóa tài khoản. |
| **DieuKhienPhong** (RoomController) | PhongHocDAO | Quản lý phòng học: thêm/sửa/xóa phòng, tra cứu phòng trống theo ngày và ca. |
| **DieuKhienThietBi** (EquipmentController) | ThietBiDAO | Quản lý thiết bị: liệt kê theo phòng, thêm/xóa thiết bị. |
| **DieuKhienDatPhong** (BookingController) | DatPhongDAO | Tạo yêu cầu đặt phòng, kiểm tra slot trống, cập nhật trạng thái (duyệt/từ chối/hủy). |
| **DieuKhienLich** (ScheduleController) | LichPhongDAO | Quản lý lịch biểu phòng theo tuần: thêm/xóa/cập nhật slot. |
| **DieuKhienPhanHoiPhong** (FeedbackController) | DanhGiaPhongDAO, SuCoPhongDAO | Xử lý đánh giá sao, báo cáo sự cố, và giải quyết issue. |
| **DieuKhienBaoCao** (ReportController) — *«facade»* | Nhiều Controller | Tổng hợp dữ liệu thống kê: dashboard, biểu đồ sử dụng, xuất báo cáo Excel/PDF. |

---

### 1.3. Các loại quan hệ UML trong biểu đồ

Biểu đồ sử dụng **5 loại quan hệ UML chuẩn**, được ghi chú ở phần **Chú Giải Quan Hệ** phía dưới biểu đồ:

| Ký hiệu | Loại quan hệ | Ý nghĩa | Ví dụ |
|----------|-------------|----------|-------|
| `- - -▷` (nét đứt) | **Dependency «uses»** | DAO tạo / trả về Model | `PhongHocDAO` «uses» `PhongHoc` |
| `──────` (nét liền, `*` ↔ `1`) | **Association 1-N** | Booking/Rating/Issue tham chiếu User hoặc Room (FK) | `DatPhong` N ↔ 1 `NguoiDung` |
| `◇──────` (kim cương rỗng) | **Aggregation 1-N** | Room "chứa" Equipment / Schedule / Rating / Issue | `PhongHoc` 1 ◇── N `ThietBi` |
| `◆──────` (kim cương đặc) | **Composition** | Controller **sở hữu** và quản lý vòng đời DAO | `DieuKhienPhong` ◆── `PhongHocDAO` |
| `◇──────` (kim cương rỗng, phía Controller) | **Aggregation (lỏng)** | ReportController dùng qua injection, không sở hữu lifecycle | `DieuKhienBaoCao` ◇── `DieuKhienDatPhong` |

---

### 1.4. Luồng hoạt động tổng quát

```
Người dùng → GUI (View) → Controller → DAO → SQLite Database
                ↑                                    │
                └────────── Kết quả trả về ──────────┘
```

1. **Người dùng** tương tác với giao diện (nhấn nút, nhập dữ liệu).
2. **GUI** gọi phương thức của **Controller** tương ứng.
3. **Controller** kiểm tra logic (validation), rồi gọi **DAO** để thao tác CSDL.
4. **DAO** thực thi câu lệnh SQL, ánh xạ kết quả sang **Model** (dataclass).
5. **Kết quả** được trả ngược về GUI để hiển thị.

---

## 2. 🗄️ Sơ Đồ Quan Hệ Thực Thể (Entity-Relationship Diagram — ERD)

### 2.1. Tổng quan

Sơ đồ ERD mô tả **cấu trúc cơ sở dữ liệu SQLite** của hệ thống với **7 bảng** và các mối quan hệ giữa chúng. Biểu đồ sử dụng ký pháp **Crow's Foot** (chân quạ) để thể hiện cardinality.

---

### 2.2. Danh sách các bảng

| # | Bảng | Màu nền | Số cột | Mô tả |
|---|------|---------|--------|-------|
| 1 | **users** | 🟦 Xanh dương | 8 | Tài khoản người dùng hệ thống |
| 2 | **rooms** | 🟧 Cam | 6 | Thông tin phòng học |
| 3 | **bookings** | 🟨 Vàng | 9 | Yêu cầu đặt phòng |
| 4 | **equipment** | 🟧 Cam nhạt | 6 | Thiết bị trong phòng |
| 5 | **schedules** | 🟥 Đỏ | 6 | Lịch sử dụng phòng theo tuần |
| 6 | **room_ratings** | 🟩 Hồng | 7 | Đánh giá chất lượng phòng |
| 7 | **room_issues** | ⬜ Trắng | 8 | Báo cáo sự cố phòng |

---

### 2.3. Ký hiệu trên biểu đồ

| Ký hiệu | Ý nghĩa |
|----------|----------|
| **PK** | Primary Key — Khóa chính, định danh duy nhất mỗi bản ghi |
| **FK** | Foreign Key — Khóa ngoại, tham chiếu đến bảng khác (hiển thị nền màu) |
| `──‖` (nét kép) | Phía "1" — Một bản ghi duy nhất |
| `──>‖` (chân quạ) | Phía "N" — Nhiều bản ghi liên kết |
| **N : 1** | Quan hệ Nhiều-Một |
| **UNIQUE** | Ràng buộc giá trị duy nhất |
| **DEFAULT** | Giá trị mặc định khi không truyền vào |
| **CHECK** | Ràng buộc kiểm tra điều kiện (ví dụ: `stars` từ 1–5) |
| **AUTOINCREMENT** | Khóa chính tự tăng (dùng cho `schedules`, `room_ratings`, `room_issues`) |

---

### 2.4. Các mối quan hệ (Relationships)

Bảng trung tâm của hệ thống là **`rooms`** và **`users`**, từ đó các bảng con liên kết qua khóa ngoại:

```
                          users
                         /  |  \
                        /   |   \
                bookings  room_ratings  room_issues
                  |          |              |
                  └──────── rooms ──────────┘
                           / \
                          /   \
                   equipment  schedules
```

#### Chi tiết từng quan hệ:

| Quan hệ | Cardinality | Mô tả |
|---------|-------------|-------|
| `users` → `bookings` | **1 : N** | Một người dùng có thể tạo **nhiều** yêu cầu đặt phòng |
| `rooms` → `bookings` | **1 : N** | Một phòng có thể được đặt **nhiều** lần (khác ngày/ca) |
| `rooms` → `equipment` | **1 : N** | Một phòng **chứa** nhiều thiết bị |
| `rooms` → `schedules` | **1 : N** | Một phòng có **nhiều** slot lịch (UNIQUE trên `room_id + weekday + slot`) |
| `rooms` → `room_ratings` | **1 : N** | Một phòng có thể nhận **nhiều** đánh giá từ các user khác nhau |
| `users` → `room_ratings` | **1 : N** | Một người dùng có thể đánh giá **nhiều** phòng |
| `rooms` → `room_issues` | **1 : N** | Một phòng có thể có **nhiều** sự cố được báo cáo |
| `users` → `room_issues` | **1 : N** | Một người dùng có thể báo cáo **nhiều** sự cố |

> **Tất cả các quan hệ đều là N : 1** (Nhiều bản ghi ở bảng con → 1 bản ghi ở bảng cha).

---

### 2.5. Ràng buộc đặc biệt

| Bảng | Ràng buộc | Chi tiết |
|------|-----------|----------|
| `users` | `username UNIQUE` | Không cho phép trùng tên đăng nhập |
| `users` | `email UNIQUE` | Không cho phép trùng email |
| `rooms` | `name UNIQUE` | Không cho phép trùng tên phòng |
| `schedules` | `UNIQUE(room_id, weekday, slot)` | Mỗi phòng chỉ có **1 slot duy nhất** cho mỗi thứ trong tuần |
| `room_ratings` | `CHECK(stars >= 1 AND stars <= 5)` | Số sao đánh giá phải từ **1 đến 5** |
| `bookings` | `status DEFAULT 'Cho duyet'` | Yêu cầu mới tạo sẽ ở trạng thái **Chờ duyệt** |
| `rooms` | `status DEFAULT 'Hoat dong'` | Phòng mới thêm mặc định **Hoạt động** |
| `room_issues` | `status DEFAULT 'Chua xu ly'` | Sự cố mới báo mặc định **Chưa xử lý** |

---

## 3. 🔗 Mối Liên Hệ Giữa Hai Biểu Đồ

Hai biểu đồ bổ trợ cho nhau để mô tả hệ thống từ **hai góc nhìn khác nhau**:

| Góc nhìn | Biểu đồ Lớp (Class Diagram) | Sơ đồ ERD |
|----------|------------------------------|-----------|
| **Mục đích** | Thiết kế **phần mềm** (code) | Thiết kế **cơ sở dữ liệu** |
| **Đối tượng** | Các lớp Python (Controller, DAO, Model) | Các bảng SQLite |
| **Quan hệ** | Dependency, Association, Aggregation, Composition | Foreign Key, Cardinality (N:1) |
| **Ánh xạ** | Mỗi **Model** ↔ một **bảng** trong ERD | Mỗi **bảng** ↔ một **Model** trong Class Diagram |
| **Bổ sung** | Thêm tầng Controller và DAO (không có trong ERD) | Thêm chi tiết kiểu dữ liệu, ràng buộc SQL (không có trong Class Diagram) |

### Ví dụ ánh xạ:

```
Class Diagram                    ERD
─────────────                    ───
NguoiDung (Model)       ↔       users (Table)
PhongHoc (Model)        ↔       rooms (Table)
DatPhong (Model)        ↔       bookings (Table)
ThietBi (Model)         ↔       equipment (Table)
LichPhong (Model)       ↔       schedules (Table)
DanhGiaPhong (Model)    ↔       room_ratings (Table)
SuCoPhong (Model)       ↔       room_issues (Table)
```

---

## 4. 📍 Vị Trí File Biểu Đồ

```
Docs/
└── Design/
    ├── Bieu do/
    │   ├── Biểu đồ lớp.png          ← Biểu đồ lớp UML
    │   └── Sơ Đồ Quan Hệ.png       ← Sơ đồ ERD
    └── Giao dien/
        ├── Trang Đăng Nhập.jpg
        ├── Trang Đăng Ký.jpg
        ├── Trang Chủ admin.jpg
        ├── Quản Lý Người Dùng.jpg
        ├── Quản Lý Phòng.jpg
        ├── Quản Lý Thiết bị.jpg
        ├── Đặt Phòng Học.jpg
        ├── Danh sách đặt phòng.jpg
        ├── Lịch Biểu.jpg
        ├── Báo Cáo Thống kê.jpg
        └── Quên Mật Khẩu.jpg
```

---

*Tài liệu thuộc Nhóm 24 — Hệ thống Quản lý Đặt Phòng Học.*
