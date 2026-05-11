# 📑 Yêu cầu Chức năng (Functional Requirements)

Hệ thống Quản lý Đặt Phòng Học – Nhóm 24

## 1. Giới thiệu
Tài liệu này mô tả chi tiết các chức năng cần thiết mà hệ thống phải đáp ứng cho từng nhóm người dùng.

## 2. Các nhóm người dùng (User Roles)
Hệ thống phân chia thành 3 nhóm người dùng chính:
1.  **Quản trị viên (Admin)**
2.  **Giảng viên (Lecturer)**
3.  **Sinh viên (Student)**

---

## 3. Danh sách yêu cầu chức năng

### 3.1. Chức năng chung (Common Features)
| ID | Chức năng | Mô tả |
|---|---|---|
| F-01 | Đăng nhập | Cho phép người dùng đăng nhập vào hệ thống bằng Username và Password. |
| F-02 | Đổi mật khẩu | Cho phép người dùng cập nhật mật khẩu mới để bảo mật. |
| F-03 | Đăng xuất | Kết thúc phiên làm việc an toàn. |
| F-04 | Quản lý Hồ sơ | Xem và chỉnh sửa thông tin cá nhân (Họ tên, Email, SĐT). |

### 3.2. Dành cho Quản trị viên (Admin)
| ID | Chức năng | Mô tả |
|---|---|---|
| A-01 | Dashboard Thống kê | Xem tổng quan số lượng phòng, thiết bị, và các yêu cầu đang chờ. |
| A-02 | Quản lý Người dùng | Thêm, sửa, xóa và phân quyền tài khoản (Admin, Giảng viên, Sinh viên). |
| A-03 | Quản lý Phòng học | Quản lý thông tin phòng (Tên, Sức chứa, Loại phòng, Trạng thái). |
| A-04 | Quản lý Thiết bị | Theo dõi danh sách thiết bị theo từng phòng, tình trạng hỏng hóc/bảo trì. |
| A-05 | Phê duyệt Đặt phòng | Xét duyệt hoặc từ chối các yêu cầu đặt phòng từ Giảng viên/Sinh viên kèm lý do. |
| A-06 | Báo cáo Thống kê | Xuất dữ liệu đặt phòng và tình trạng sử dụng ra file Excel. |

### 3.3. Dành cho Giảng viên (Lecturer)
| ID | Chức năng | Mô tả |
|---|---|---|
| L-01 | Đăng ký Đặt phòng | Mượn phòng cho các ca dạy, bù giờ hoặc sự kiện đặc biệt. |
| L-02 | Tra cứu Phòng trống | Kiểm tra xem phòng nào còn trống theo ngày và ca học cụ thể. |
| L-03 | Quản lý Lịch mượn | Xem lịch sử các phòng đã mượn và trạng thái phê duyệt. |
| L-04 | Thông báo | Nhận thông báo khi yêu cầu đặt phòng được Admin phê duyệt hoặc từ chối. |

### 3.4. Dành cho Sinh viên (Student)
| ID | Chức năng | Mô tả |
|---|---|---|
| S-01 | Tra cứu Lịch phòng | Xem thông tin các phòng học đang được sử dụng hoặc trống. |
| S-02 | Yêu cầu Mượn phòng | Gửi yêu cầu mượn phòng cho các hoạt động ngoại khóa, câu lạc bộ. |
| S-03 | Quản lý Yêu cầu | Xem lại danh sách các yêu cầu đã gửi và kết quả phê duyệt. |

---

## 4. Yêu cầu phi chức năng (Non-functional Requirements)
- **Hiệu năng**: Hệ thống phản hồi nhanh (< 2 giây) cho các tác vụ tra cứu thông thường.
- **Bảo mật**: Mật khẩu phải được mã hóa (SHA-256) trước khi lưu vào cơ sở dữ liệu.
- **Giao diện**: Thân thiện, hiện đại, dễ sử dụng trên môi trường Windows Desktop.


