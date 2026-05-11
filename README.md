<div align="center">
  <h1>🏫 Hệ Thống Quản Lý Đặt Phòng Học</h1>
  <p><strong>(Classroom Booking Management System)</strong></p>
  <p><i>Bài tập lớn môn Phát triển ứng dụng Desktop — Nhóm 24</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Tkinter-GUI-orange.svg" alt="Tkinter">
    <img src="https://img.shields.io/badge/SQLite-Database-lightgrey.svg?logo=sqlite&logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/Architecture-MVC-brightgreen.svg" alt="MVC Architecture">
  </p>
</div>

---

## 📝 Giới thiệu

Hệ thống **Quản lý đặt phòng học** là một ứng dụng desktop mạnh mẽ được xây dựng bằng **Python** và **Tkinter**, tuân thủ nghiêm ngặt kiến trúc **MVC (Model – View – Controller)**. 

Dự án cung cấp giải pháp chuyển đổi số toàn diện cho quy trình quản lý, theo dõi và đặt phòng học trong môi trường giáo dục (Đại học/Cao đẳng). Hệ thống giúp tối ưu hóa việc sử dụng cơ sở vật chất, tự động hóa quy trình phê duyệt, và nâng cao trải nghiệm của Giảng viên cũng như Sinh viên.

---

## ✨ Tính năng nổi bật

Ứng dụng phân quyền mạnh mẽ với 3 vai trò chính:

### 🛠️ Quản trị viên (Admin)
- **Quản lý toàn diện:** Thêm, sửa, xóa, và phân quyền người dùng.
- **Quản lý cơ sở vật chất:** Quản lý thông tin phòng học, sức chứa, thiết bị, và trạng thái bảo trì.
- **Xử lý yêu cầu:** Phê duyệt hoặc từ chối yêu cầu đặt phòng với hệ thống thông báo Email tự động.
- **Thống kê & Báo cáo:** Cung cấp Dashboard trực quan, hỗ trợ xuất báo cáo ra **Excel** và **PDF**.
- **Quản lý phản hồi:** Theo dõi đánh giá và xử lý các sự cố được báo cáo từ người dùng.

### 👨‍🏫 Giảng viên
- **Đặt phòng nhanh chóng:** Tìm kiếm phòng trống và đặt phòng theo lịch trình.
- **Theo dõi lịch biểu:** Xem lịch sử dụng phòng trực quan theo tuần.
- **Tương tác:** Đánh giá chất lượng phòng học (1-5 sao) và báo cáo sự cố hư hỏng thiết bị.

### 🎓 Sinh viên
- **Yêu cầu mượn phòng:** Gửi yêu cầu sử dụng phòng phục vụ học tập/hoạt động ngoại khóa (cần Admin phê duyệt).
- **Quản lý cá nhân:** Xem lịch sử đặt phòng của bản thân.
- **Tương tác:** Tham gia đánh giá và báo lỗi cơ sở vật chất.

---

## 🛠️ Công nghệ & Thư viện

| Thành phần | Công nghệ / Thư viện | Ghi chú |
| :--- | :--- | :--- |
| **Ngôn ngữ** | `Python 3.10+` | |
| **Giao diện (GUI)**| `Tkinter`, `ttk` | Hệ thống helper UI nâng cao, custom theme |
| **Cơ sở dữ liệu** | `SQLite` | Tự động khởi tạo (`classroom_booking.db`), không cần setup server |
| **Bảo mật** | `hashlib` | PBKDF2-HMAC-SHA256 (100,000 iterations) với Random Salt |
| **Email** | `smtplib` | Gửi email thông báo tự động qua SMTP (Gmail) |
| **Xuất báo cáo** | `openpyxl`, `fpdf2` | Hỗ trợ xuất dữ liệu ra Excel và PDF |
| **Lịch (Calendar)**| `tkcalendar` | UI chọn ngày tháng trực quan |
| **Kiểm thử (Test)**| `pytest` | Bộ 75+ test cases đảm bảo độ ổn định |
| **Logging** | `logging` | Ghi log hệ thống xoay vòng (Rotating File Handler) |

---

## 🏗️ Kiến trúc hệ thống

Dự án áp dụng mô hình **MVC** kết hợp **DAO (Data Access Object)** giúp tách biệt logic, giao diện và dữ liệu:

```mermaid
graph TD
    GUI[GUI / View\n(Tkinter)] <-->|Tương tác| CTRL[Controller\n(Xử lý Logic)]
    CTRL <-->|Gọi hàm| DAO[DAO\n(Thao tác CSDL)]
    DAO <-->|Truy vấn| DB[(SQLite Database)]
    DAO -->|Tạo đối tượng| MODEL[Model\n(Dataclasses)]
    CTRL -.->|Sử dụng| MODEL
```

> **Chi tiết thiết kế:** Xem thêm tài liệu giải thích UML và ERD tại `Docs/readme9.md` và thư mục `Docs/Design/`.

---

## 📂 Cấu trúc thư mục

```text
BTL-nhom24/
├── main.py                  # Điểm khởi chạy ứng dụng (Root launcher)
├── requirements.txt         # Danh sách thư viện phụ thuộc
├── setup.bat                # Script cài đặt nhanh (Windows)
├── src/
│   ├── back end/            # Xử lý Logic & Database
│   │   ├── controllers/     # Controller (Auth, Booking, Room, User...)
│   │   ├── dao/             # Thao tác CSDL (RoomDAO, UserDAO...)
│   │   ├── database/        # Schema SQL & Dữ liệu mẫu (Seed data)
│   │   ├── models/          # Các thực thể dữ liệu (User, Room, Booking...)
│   │   ├── utils/           # Tiện ích (Hash, Email, Export, Logger)
│   │   └── main.py          # Entry point của Tkinter
│   └── font-end/
│       └── gui/             # Các màn hình Giao diện Tkinter
├── tests/                   # Thư mục chứa các Unit tests (Pytest)
└── Docs/                    # Tài liệu đặc tả, thiết kế, UML, ERD
```

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### 1. Chuẩn bị mã nguồn

```bash
git clone https://github.com/tranhieu122/BTL-nhom24.git
cd BTL-nhom24
```

### 2. Thiết lập môi trường

Khuyến nghị sử dụng **Virtual Environment (venv)**:

```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate
# Kích hoạt (Linux/macOS)
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

*(Lưu ý đối với người dùng Windows: Bạn có thể chạy trực tiếp file `setup.bat` để tự động hóa bước cài đặt).*

### 3. Cấu hình tính năng Email (Tùy chọn)

Để ứng dụng có thể gửi Email tự động khi duyệt/từ chối phòng, tạo file `.env` ở thư mục gốc:

```env
EMAIL_ENABLED=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```
*(Cần sử dụng App Password của Gmail, không dùng mật khẩu gốc).*

### 4. Khởi chạy ứng dụng

```bash
python main.py
```

> 💡 **Tip:** Ở lần chạy đầu tiên, ứng dụng sẽ tự động tạo cơ sở dữ liệu `classroom_booking.db` và nạp sẵn (seed) các dữ liệu mẫu để bạn trải nghiệm ngay.

### 5. Tài khoản dùng thử

Sử dụng các tài khoản sau để đăng nhập vào các phân hệ tương ứng:

| Vai trò | Tên đăng nhập | Mật khẩu |
| :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123` |
| **Giảng viên** | `gv01` | `gv123` |
| **Sinh viên** | `sv01` | `sv123` |

### 6. Chạy Kiểm thử (Unit Tests)

Để chạy bộ kiểm thử hệ thống:

```bash
python -m pytest tests/ -v
```

---

## 🔒 Tính năng Bảo mật

- **Mã hóa Mật khẩu:** Sử dụng thuật toán `PBKDF2-HMAC-SHA256` với Salt ngẫu nhiên 16 byte và 100,000 vòng lặp (iterations). Hỗ trợ nâng cấp tự động từ hash chuẩn SHA-256 cũ.
- **Phòng chống SQL Injection:** Toàn bộ truy vấn CSDL đều sử dụng Parameterized Queries (`?`).
- **Phân quyền truy cập:** Ràng buộc chặt chẽ các chức năng theo 3 cấp độ tài khoản.
- **Audit Logging:** Ghi nhận mọi hoạt động quan trọng vào file `logs/app.log` (Hỗ trợ xoay vòng file log tối đa 2MB, lưu 3 bản backup).

---

## 👥 Nhóm phát triển (Nhóm 24)

| STT | Họ và Tên | Vai trò |
|:---:|:---|:---|
| 1 | **Trần Trung Hiếu** | Trưởng nhóm / Full-stack |
| 2 | **Nguyễn Huy Hải** | Thành viên |
| 3 | **Nguyễn Tuấn Minh** | Thành viên |

---
*Dự án được phát triển với niềm đam mê ❤️ và sự nghiêm túc.*
