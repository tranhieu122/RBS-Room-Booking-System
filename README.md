<div align="center">
  <h1>💎 RBS — Titanium Elite Edition</h1>
  <p><strong>Hệ Thống Quản Lý Đặt Phòng Học Cao Cấp</strong></p>
  <p><i>Phát triển bởi Nhóm 24 — High-Fidelity Desktop Application</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/UI--UX-Titanium_Elite-6366f1.svg" alt="Titanium Elite">
    <img src="https://img.shields.io/badge/SQLite-Database-lightgrey.svg?logo=sqlite&logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/Architecture-MVC-brightgreen.svg" alt="MVC Architecture">
  </p>
</div>

---

## 📝 Giới thiệu

**RBS (Room Booking System) — Titanium Elite** là phiên bản nâng cấp toàn diện của hệ thống quản lý phòng học, tập trung vào trải nghiệm người dùng cao cấp (UX) và giao diện hiện đại (UI). Ứng dụng được xây dựng trên nền tảng **Python & Tkinter** nhưng được tối ưu hóa với các kỹ thuật đồ họa Canvas nâng cao, mang lại cảm giác mượt mà như một ứng dụng web hiện đại.

Hệ thống giải quyết triệt để bài toán quản lý tài nguyên phòng học, từ việc đặt chỗ đơn lẻ cho sinh viên đến việc quản lý lịch dạy chu kỳ (recurring schedule) phức tạp cho giảng viên.

---

## ✨ Tính năng "Titanium Elite"

Hệ thống vượt xa các ứng dụng quản lý thông thường với bộ tính năng chuyên sâu:

### 🚀 Giao diện Titanium Elite
- **Dashboard Executive:** Tổng quan dữ liệu trực quan với các biểu đồ Canvas động, hiệu ứng mesh animation và thống kê thời gian thực.
- **Smart Calendar:** Lịch biểu thông minh hỗ trợ xem theo tuần, theo phòng và xem trước 30 ngày với mã màu phân loại trạng thái.
- **Micro-interactions:** Hiệu ứng hover, transition mượt mà và hệ thống thông báo Toast cao cấp.

### 📅 Quản lý Đặt phòng Thông minh
- **Lịch dạy Chu kỳ (Recurring):** Hỗ trợ giảng viên thiết lập lịch lặp lại (ví dụ: thứ 2, thứ 4 hàng tuần) trong cả học kỳ chỉ với một thao tác.
- **Xử lý xung đột:** Thuật toán phát hiện trùng lịch thông minh, gợi ý các phòng thay thế dựa trên sức chứa và thiết bị.
- **Phê duyệt đa luồng:** Admin có thể duyệt nhanh hàng loạt yêu cầu, từ chối kèm lý do và tự động gửi thông báo.

### 📊 Thống kê & Xuất bản
- **Báo cáo chuyên sâu:** Thống kê tần suất sử dụng phòng, tỷ lệ phê duyệt và xu hướng đặt phòng theo tháng.
- **Đa dạng định dạng:** Xuất dữ liệu ra **Excel**, **CSV** và đặc biệt là tệp **iCalendar (.ics)** để đồng bộ với Google Calendar/Outlook.

---

## 🛠️ Công nghệ & Kiến trúc

| Thành phần | Công nghệ / Thư viện | Ghi chú |
| :--- | :--- | :--- |
| **Giao diện** | `Tkinter` + `Canvas API` | Thiết kế theo hệ thống Titanium Design System |
| **Logic** | `Python 3.10+` | Kiến trúc MVC tách biệt hoàn toàn Logic và View |
| **Dữ liệu** | `SQLite 3` | Hiệu suất cao với WAL mode và Parameterized Queries |
| **Tiện ích** | `tkcalendar`, `openpyxl` | Hỗ trợ chọn ngày và xuất bản dữ liệu chuyên nghiệp |
| **Lịch biểu** | `iCalendar` | Hỗ trợ chuẩn .ics quốc tế |

---

## 📂 Cấu trúc dự án

```text
RBS-Titanium/
├── main.py                  # Entry point (Khởi chạy ứng dụng)
├── src/
│   ├── back end/            # Core Engine & Business Logic
│   │   ├── controllers/     # Điều phối dữ liệu (Booking, Room, Report...)
│   │   ├── dao/             # Data Access Objects (Truy vấn SQLite)
│   │   ├── database/        # Cấu trúc CSDL & Seed data
│   │   └── utils/           # Export ICS/Excel, Hash mật khẩu, Logger
│   └── font-end/
│       └── gui/             # Titanium Elite UI Components
│           ├── theme.py     # Hệ thống Design Tokens (Màu sắc, Font, Button)
│           ├── dashboard_gui.py # Executive Dashboard
│           └── booking_form_gui.py # Smart Booking Interface
└── tests/                   # Kiểm thử hệ thống (Pytest)
```

---

## 🚀 Cài đặt nhanh

1. **Yêu cầu:** Máy tính đã cài đặt Python 3.10 trở lên.
2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Khởi chạy:**
   ```bash
   python main.py
   ```

---

## 🔐 Tài khoản dùng thử

| Vai trò | Tài khoản | Mật khẩu |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Giảng viên** | `teacher1` | `teacher123` |
| **Sinh viên** | `student1` | `student123` |

---

## 👥 Nhóm phát triển (Nhóm 24)

| STT | Họ và Tên | Vai trò |
|:---:|:---|:---|
| 1 | **Trần Trung Hiếu** | Trưởng nhóm / Full-stack Developer |
| 2 | **Nguyễn Huy Hải** | UI Design / Testing |
| 3 | **Nguyễn Tuấn Minh** | Backend Logic / Data Architecture |

---
<div align="center">
  <p><i>Dự án được hoàn thiện với tiêu chuẩn Titanium Elite — Sang trọng, Mạnh mẽ và Tin cậy.</i></p>
</div>
