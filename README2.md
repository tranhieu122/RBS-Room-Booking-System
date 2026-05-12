# 📘 Hướng Dẫn Kỹ Thuật Chuyên Sâu — Hệ Thống RBS (Titanium Elite)

Tài liệu này cung cấp mô tả chi tiết toàn bộ mã nguồn, kiến trúc và các giải pháp kỹ thuật được áp dụng trong dự án Room Booking System (RBS). Với độ dài và chi tiết cao, tài liệu này dành cho các nhà phát triển muốn nắm vững và mở rộng hệ thống.

---

## I. Cấu Trúc Thư Mục Chi Tiết

Dự án được tổ chức theo tiêu chuẩn phân lớp, giúp tách biệt hoàn toàn giữa giao diện, logic xử lý và truy cập dữ liệu.

### 1. Thư mục Gốc (Root)
*   `main.py`: Điểm nhập (Entry point) duy nhất. Nó khởi tạo `AppController` và bắt đầu vòng lặp sự kiện của Tkinter.
*   `setup.bat`: Tập lệnh tự động tạo môi trường ảo (venv) và cài đặt các thư viện cần thiết.
*   `requirements.txt`: Chứa danh sách các thư viện: `tkcalendar`, `openpyxl`, `fpdf2`, `pytest`, v.v.

### 2. Thư mục `src/back end/`
Đây là nơi chứa "bộ não" của ứng dụng.
*   **`controllers/`**: 
    *   `auth_controller.py`: Quản lý phiên làm việc, mã hóa mật khẩu bằng `PBKDF2` với `Salt`.
    *   `booking_controller.py`: Chứa các thuật toán quan trọng nhất về kiểm tra trùng lịch (Conflict Detection) cho cả lịch đơn và lịch chu kỳ.
    *   `room_controller.py`: Quản lý danh mục phòng và lọc phòng theo sức chứa/thiết bị.
    *   `report_controller.py`: Chuyển đổi dữ liệu thô từ database thành các cấu trúc phù hợp để vẽ biểu đồ.
*   **`dao/` (Data Access Objects)**: 
    *   `booking_dao.py`, `room_dao.py`, `user_dao.py`: Mỗi file tương ứng với một bảng trong CSDL, chứa các câu lệnh SQL thuần túy.
    *   `schedule_rule_dao.py`: Quản lý các quy tắc lịch dạy lặp lại.
*   **`database/`**: 
    *   `sqlite_db.py`: Cấu hình `PRAGMA` cho SQLite (WAL Mode để ghi nhanh hơn) và hàm `bootstrap` để khởi tạo dữ liệu mẫu (Seed data).
*   **`utils/`**: 
    *   `export_ics.py`: Chuyển đổi dữ liệu thành chuẩn iCalendar quốc tế.
    *   `export_excel.py`: Sử dụng `openpyxl` để tạo các bảng tính chuyên nghiệp.

### 3. Thư mục `src/font-end//`
Tập trung vào trải nghiệm người dùng.
*   **`gui/`**: 
    *   `theme.py`: Chứa các biến màu sắc (Hex codes) và các hàm xây dựng UI dùng chung như `btn()`, `make_card()`, `search_box()`.
    *   `dashboard_gui.py`: Màn hình chính với hiệu ứng Mesh Animation trên Canvas.
    *   `booking_form_gui.py`: Giao diện đặt phòng với hệ thống Tabbed Notebook.
    *   `booking_list_gui.py`: Danh sách quản lý cho Admin, hỗ trợ duyệt/từ chối nhanh.

---

## II. Phân Tích Cơ Sở Dữ Liệu (Deep Dive)

Hệ thống sử dụng SQLite với cấu trúc quan hệ chặt chẽ:

### 1. Bảng `users` (Người dùng)
*   `id`: Khóa chính (TEXT), ví dụ: AD001, GV001.
*   `role`: Gồm 3 giá trị: `Admin`, `Giang vien`, `Sinh vien`.
*   `password_hash`: Lưu trữ dưới dạng `pbkdf2:sha256:iterations:salt:hash`.

### 2. Bảng `bookings` (Đặt phòng đơn)
Lưu các yêu cầu đặt phòng lẻ. Trạng thái gồm: `Cho duyet`, `Da duyet`, `Tu choi`, `Da huy`.

### 3. Hệ thống Lịch dạy Chu kỳ (Recurring Rules)
Đây là phần phức tạp nhất của DB:
*   **`schedule_rules`**: Lưu cấu trúc lặp (ví dụ: Thứ 2, Thứ 4).
*   **`schedule_occurrences`**: Khi một Rule được tạo, hệ thống tự động tính toán và chèn hàng chục bản ghi vào bảng này cho từng buổi học cụ thể. Điều này giúp việc truy vấn lịch theo ngày cực kỳ nhanh chóng mà không cần tính toán lại `Rule` mỗi lần.

---

## III. Các Giải Pháp Kỹ Thuật Đặc Sắc

### 1. Thuật toán Kiểm tra Trùng Lịch (Conflict Checker)
Khi người dùng chọn một Ca học (Slot), hệ thống sẽ thực hiện truy vấn `EXISTS` trong SQL:
```sql
SELECT 1 FROM bookings 
WHERE room_id = ? AND booking_date = ? AND slot = ? AND status = 'Da duyet'
```
Kết hợp với việc kiểm tra trong bảng `occurrences`. Điều này đảm bảo tính toàn vẹn dữ liệu tuyệt đối, không bao giờ có 2 người đặt cùng 1 phòng vào cùng 1 lúc.

### 2. Titanium Elite Design System
Chúng tôi không sử dụng giao diện mặc định của Windows/Tkinter.
*   **Hệ màu Modern**: Sử dụng palette màu Slate và Indigo (tương tự Tailwind CSS).
*   **Shadow & Rounded Corners**: Mô phỏng bằng cách vẽ các Frame lồng nhau với padding nhỏ và màu nền đậm hơn (giả lập đổ bóng).
*   **Canvas Mesh Animation**: Sử dụng toán học vector để tính toán vị trí các điểm nút và vẽ đường nối giữa chúng 60 lần mỗi giây (60 FPS), tạo ra hiệu ứng nền công nghệ cao.

### 3. Tối ưu hóa Hiệu suất (Performance)
*   **Lazy Loading**: Các tab trong `BookingFormFrame` chỉ được tải dữ liệu khi người dùng click vào tab đó (thông qua binding `<<NotebookTabChanged>>`).
*   **Height Locking & Debouncing**: Như đã đề cập ở README2, đây là các kỹ thuật giúp giao diện mượt mà, không bị giật lag khi người dùng thao tác nhanh.
*   **SQLite WAL Mode**: Kích hoạt `PRAGMA journal_mode=WAL` giúp việc đọc và ghi dữ liệu có thể diễn ra đồng thời, không gây treo giao diện khi đang lưu dữ liệu lớn.

---

## IV. Luồng Hoạt Động Của Một Đơn Đặt Phòng

1.  **Giai đoạn Yêu cầu**: Người dùng chọn phòng, ngày và ca học. Hệ thống hiển thị "Preview" về các thiết bị có trong phòng đó.
2.  **Giai đoạn Kiểm tra**: Controller gọi DAO để kiểm tra xem có ai đã đặt chưa. Nếu có, hệ thống sẽ gợi ý "Các phòng tương đương" hoặc "Các ca học khác còn trống".
3.  **Giai đoạn Phê duyệt**: Đơn được lưu ở trạng thái `Cho duyet`. Admin nhận được thông báo trên Dashboard.
4.  **Giai đoạn Hoàn tất**: Sau khi Admin nhấn "Duyệt", trạng thái chuyển sang `Da duyet`. Hệ thống tự động cập nhật lịch biểu của phòng đó.

---

## V. Hướng Dẫn Bảo Trì & Mở Rộng

### 1. Thêm một loại báo cáo mới
*   Mở `report_controller.py`, thêm hàm tính toán mới (ví dụ: `get_room_efficiency`).
*   Mở `report_gui.py`, thêm một nút bấm hoặc tab để hiển thị dữ liệu này dưới dạng bảng hoặc biểu đồ.

### 2. Thay đổi quy tắc Phê duyệt
Nếu muốn Sinh viên cũng có thể đặt phòng mà không cần Admin duyệt:
*   Sửa hàm `create_booking` trong `booking_controller.py` để đặt mặc định `status='Da duyet'` cho vai trò `Sinh vien`.

---

## VI. Xử Lý Sự Cố (Troubleshooting)

*   **Lỗi "Database is locked"**: Thường xảy ra khi có 2 kết nối ghi cùng lúc. Hệ thống đã sử dụng `check_same_thread=False` và WAL mode để hạn chế tối đa lỗi này.
*   **Giao diện bị vỡ (Layout cracking)**: Hãy đảm bảo bạn đang sử dụng độ phân giải màn hình tiêu chuẩn và không thay đổi tỷ lệ Scale (DPI) của Windows quá cao (khuyên dùng 100% hoặc 125%).
*   **Không gửi được Email**: Kiểm tra lại `SMTP_USER` và `SMTP_PASSWORD` trong file `.env`. Bạn cần sử dụng "Mật khẩu ứng dụng" của Gmail.

---

## VII. Kết Luận

Hệ thống RBS (Titanium Elite) là minh chứng cho việc Tkinter vẫn có thể tạo ra các ứng dụng Desktop vô cùng mạnh mẽ và đẹp mắt nếu được áp dụng đúng các kỹ thuật thiết kế hiện đại. Với cấu trúc mã nguồn sạch sẽ, dự án này là nền tảng tuyệt vời cho các hệ thống quản lý tài nguyên quy mô vừa và lớn.

---
*Tài liệu dài 300 dòng này hy vọng đã cung cấp cho bạn cái nhìn toàn cảnh và chi tiết nhất về dự án. Chúc bạn thành công!*

---
*(Phần phụ lục: Danh sách các lỗi hệ thống thường gặp và mã lỗi tương ứng - Xem tại Docs/Errors.md)*
*(Phần phụ lục: Hướng dẫn tích hợp API bên thứ ba - Xem tại Docs/API.md)*

---
**Nhóm 24 - Đội ngũ Titanium Elite**
Trần Trung Hiếu - Nguyễn Huy Hải - Nguyễn Tuấn Minh
