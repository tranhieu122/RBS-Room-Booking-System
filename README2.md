# 📖 Hướng Dẫn Chi Tiết Hệ Thống RBS (Titanium Elite)

Tài liệu này cung cấp cái nhìn sâu sắc về kiến trúc, luồng xử lý và các tính năng kỹ thuật của hệ thống **Room Booking System (RBS)**.

---

## 1. Kiến Trúc Hệ Thống (Architecture)

Ứng dụng được xây dựng theo mô hình **MVC (Model-View-Controller)** kết hợp với **DAO (Data Access Object)** để đảm bảo tính mở rộng và dễ bảo trì.

### 🧩 Các thành phần chính:
*   **Models (`src/back end/models/`)**: Định nghĩa cấu trúc dữ liệu (User, Room, Booking, ScheduleRule). Sử dụng `dataclasses` để quản lý dữ liệu nhẹ nhàng.
*   **DAO (`src/back end/dao/`)**: Lớp duy nhất tương tác trực tiếp với SQLite. Chứa các câu lệnh SQL để CRUD dữ liệu. Điều này giúp tách biệt logic nghiệp vụ khỏi các truy vấn DB.
*   **Controllers (`src/back end/controllers/`)**: Trái tim của ứng dụng. Đây là nơi chứa logic nghiệp vụ (Business Logic):
    *   `AuthController`: Xử lý đăng nhập, đăng ký, băm mật khẩu (SHA-256/PBKDF2) và phân quyền.
    *   `BookingController`: Xử lý đặt phòng, kiểm tra xung đột (Conflict Detection), tính toán lịch dạy chu kỳ.
    *   `ReportController`: Thu thập và xử lý dữ liệu thống kê cho Dashboard.
*   **Views (GUI) (`src/font-end/gui/`)**: Xây dựng bằng Tkinter. Sử dụng hệ thống **Titanium Elite Theme** để tạo giao diện hiện đại.

---

## 2. Cơ Sở Dữ Liệu (Database Schema)

Hệ thống sử dụng SQLite với các bảng chính sau:

*   **`users`**: Lưu thông tin người dùng, vai trò (Admin, Giang vien, Sinh vien) và mật khẩu đã băm.
*   **`rooms`**: Thông tin phòng học, sức chứa và danh sách thiết bị.
*   **`bookings`**: Lưu các đơn đặt phòng đơn lẻ (One-off bookings).
*   **`schedule_rules`**: Lưu cấu hình lịch dạy chu kỳ (ví dụ: Thứ 2, 4 hàng tuần từ ngày A đến ngày B).
*   **`schedule_occurrences`**: (Bảng dẫn xuất) Lưu từng buổi học cụ thể được sinh ra từ `schedule_rules` để dễ dàng quản lý trạng thái từng buổi.
*   **`equipment_reports`**: Lưu các báo cáo hư hỏng thiết bị từ người dùng.

---

## 3. Luồng Xử Lý Chính (Workflows)

### 🛡️ Kiểm tra xung đột (Conflict Detection)
Khi một người dùng đặt phòng, hệ thống sẽ thực hiện các bước kiểm tra:
1.  Kiểm tra trong bảng `bookings` xem có đơn nào đã duyệt (`Da duyet`) trùng Phòng + Ngày + Ca học hay không.
2.  Kiểm tra trong bảng `schedule_rules` (thông qua `occurrences`) xem có lịch dạy cố định nào tại đó không.
3.  Nếu là đặt lịch chu kỳ, hệ thống sẽ quét toàn bộ các ngày trong khoảng thời gian yêu cầu để đảm bảo **tất cả** các buổi đều trống.

### 📈 Dashboard & Thống kê
Dashboard sử dụng `Canvas` để vẽ biểu đồ và hiệu ứng động:
*   **Mesh Animation**: Tạo hiệu ứng mạng lưới chuyển động ở phần đầu trang (Hero section), tối ưu hóa bằng cách tách lớp tĩnh và lớp động để không gây lag.
*   **Thống kê thời gian thực**: Tổng hợp dữ liệu từ cả `bookings` và `schedule_rules` để đưa ra con số chính xác về tần suất sử dụng phòng.

---

## 4. Các Kỹ Thuật UI Nâng Cao (Titanium UX)

Để Tkinter trông hiện đại như ứng dụng Web, chúng tôi áp dụng:
*   **Height Locking**: Khi cập nhật giao diện (ví dụ: gợi ý phòng), hệ thống sẽ khóa chiều cao khung hình tạm thời để tránh tình trạng màn hình bị "nhảy" khi cuộn.
*   **Debouncing**: Khi bạn nhập sức chứa để lọc phòng, hệ thống sẽ đợi 300ms sau khi bạn ngừng gõ mới thực hiện truy vấn, giúp ứng dụng không bị khựng.
*   **Card-based UI**: Các phòng được hiển thị dưới dạng thẻ (Card) có hiệu ứng đổ bóng và hover, tạo cảm giác phân cấp thông tin rõ ràng.
*   **Responsive Scrolling**: Sử dụng Canvas kết hợp với Mousewheel binding để hỗ trợ cuộn mượt mà trên Windows.

---

## 5. Hướng Dẫn Phát Triển (For Developers)

*   **Thêm màn hình mới**: Tạo file trong `src/font-end/gui/`, kế thừa `tk.Frame` và đăng ký key trong `main.py` (hàm `_navigate`).
*   **Thay đổi màu sắc**: Cập nhật các biến `C_PRIMARY`, `C_BG`, `C_SURFACE` trong `src/font-end/gui/theme.py`.
*   **Kiểm thử**: Chạy `pytest tests/` để đảm bảo logic backend (đặc biệt là phần kiểm tra trùng lịch) không bị lỗi sau khi sửa đổi.

---
*Tài liệu này giúp bạn hiểu rõ "linh hồn" của ứng dụng RBS. Chúc bạn có trải nghiệm tuyệt vời với Titanium Elite!*
