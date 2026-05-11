# 🛠️ Đặc tả Kỹ thuật (Technical Specifications)

Hệ thống Quản lý Đặt Phòng Học – Nhóm 24

## 1. Công nghệ (Tech Stack)
Ứng dụng được xây dựng trên nền tảng Python Desktop.

- **Ngôn ngữ**: Python 3.8+
- **Giao diện (UI)**: 
    - `Tkinter` (Thư viện chuẩn)
    - `CustomTkinter` (Giao diện hiện đại)
    - `Pillow` (Xử lý hình ảnh & Icons)
- **Cơ sở dữ liệu**:
    - **Development**: SQLite (Lưu trữ file `.db` cục bộ)
    - **Production**: MySQL (Kết nối qua Server)

## 2. Thư viện phụ thuộc (Dependencies)
Danh sách các thư viện chính được sử dụng (chi tiết tại `requirements.txt`):
- `mysql-connector-python`: Kết nối và truy vấn cơ sở dữ liệu MySQL.
- `openpyxl`: Xử lý đọc/ghi file Excel để xuất báo cáo.
- `tkcalendar`: Widget chọn ngày tháng chuyên dụng cho Tkinter.
- `Pillow (PIL)`: Thao tác hình ảnh, bo góc, thay đổi kích thước icon.

## 3. Kiến trúc Phần mềm (Software Architecture)
Hệ thống áp dụng mô hình **MVC (Model-View-Controller)**:
- **Model**: Định nghĩa cấu trúc dữ liệu và thực thể (User, Room, Booking).
- **View**: Các lớp giao diện Tkinter nằm trong thư mục `gui/`.
- **Controller**: Xử lý logic nghiệp vụ và điều phối dữ liệu giữa View và Model.
- **DAO (Data Access Object)**: Lớp trung gian thực hiện các câu lệnh SQL.

## 4. Đặc tả Dữ liệu (Data Specifications)

### 4.1. Thực thể Người dùng (User)
- `id`: Mã định danh duy nhất (Primary Key).
- `username`: Tên đăng nhập (Unique).
- `full_name`: Họ và tên đầy đủ.
- `password_hash`: Mật khẩu được mã hóa SHA-256.
- `role`: Phân quyền (Admin, Giang vien, Sinh vien).

### 4.2. Thực thể Phòng học (Room)
- `id`: Mã phòng (Ví dụ: P101).
- `name`: Tên hiển thị của phòng.
- `capacity`: Sức chứa tối đa.
- `room_type`: Loại phòng (Phòng học, Phòng máy, Hội trường).
- `status`: Trạng thái (Hoạt động, Bảo trì).

### 4.3. Thực thể Đặt phòng (Booking)
- `id`: Mã yêu cầu đặt phòng.
- `user_id`: ID người đặt.
- `room_id`: ID phòng được đặt.
- `booking_date`: Ngày đặt phòng.
- `slot`: Ca học (Ca 1 đến Ca 5).
- `purpose`: Mục đích sử dụng.
- `status`: Trạng thái phê duyệt (Cho duyet, Da duyet, Tu choi).

## 5. Tiêu chuẩn Mã nguồn (Coding Standards)
- Tuân thủ chuẩn **PEP 8** cho ngôn ngữ Python.
- Đặt tên biến và hàm theo kiểu `snake_case`.
- Đặt tên lớp theo kiểu `PascalCase`.
- Tài liệu hóa mã nguồn bằng Docstrings cho tất cả các Controller và DAO quan trọng.

---

