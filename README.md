# 💰 Python Project Group 7: Expense Manager

## 🎯 Ứng Dụng Quản Lý Chi Tiêu Cá Nhân (Expense Manager)

Ứng dụng **Expense Manager** là một nền tảng web được xây dựng bằng **Python/Django**, giúp người dùng theo dõi tài chính cá nhân, quản lý thu chi và thiết lập ngân sách một cách hiệu quả.

---

## 1. Giới Thiệu Dự Án và Các Chức Năng Chính

Expense Manager cung cấp giải pháp toàn diện để người dùng kiểm soát tài chính cá nhân thông qua giao diện trực quan và hệ thống báo cáo chi tiết.

### **Các Chức Năng Chính**

#### **Quản lý Ví (Wallet Management)**
- Tạo, chỉnh sửa, xóa mềm các Ví/Tài khoản (Tiền mặt, Ngân hàng, Ví điện tử).
- Tính toán số dư hiện tại (current_balance) theo thời gian thực dựa trên lịch sử giao dịch.

#### **Giao dịch Chi tiết (Transaction Tracking)**
- Ghi lại các giao dịch Thu nhập, Chi tiêu và Chuyển khoản (có validation kiểm tra Ví nguồn/đích).
- Xem lịch sử giao dịch chi tiết, hỗ trợ lọc và sắp xếp theo loại (Expense/Income) và ngày tháng.

#### **Danh mục và Phân cấp (Category Management)**
- Hỗ trợ tạo Danh mục có phân cấp (Cha - Con), ví dụ: "Ăn uống" > "Ăn sáng".
- Áp dụng cơ chế Xóa mềm (Soft Delete) cho Ví và Danh mục.

#### **Báo cáo & KPI (Dashboard)**
- Hiển thị các chỉ số KPI quan trọng: Tổng Thu nhập, Tổng Chi tiêu, Lợi nhuận Ròng (Net Balance).
- Biểu đồ chi tiêu theo thời gian (Ngày/Tháng/Năm).
- Biểu đồ phân bổ chi tiêu theo Danh mục (Pie Chart).

#### **Ngân sách (Budgeting)**
- Thiết lập Ngân sách theo tuần (Weekly) hoặc theo tháng (Monthly) cho từng Danh mục Chi tiêu.

---

## 2. Thành Viên Tham Gia

### **Bảng phân công nhiệm vụ**

| Vai trò | Tên Thành viên | MSV | Lĩnh vực chịu trách nhiệm |
|--------|----------------|-----------|---------------------------|
| Leader & DevOps (Mem 1) | Trần Tùng Lâm | 11245891 | Cấu hình lõi (settings.py), Môi trường, Git/Deploy |
| BE Authentication (Mem 2) | Đỗ Nhật Hoa Nguyên | 11245921 | Quản lý User, API Đăng ký/Đăng nhập, Token Auth |
| BE Data Architect (Mem 3) | Bùi Sơn Tùng | 11245948 | Thiết kế Database (Models), Logic Soft Delete, Data Seeding |
| BE Logic & API (Mem 4) | Đỗ Minh Thành | 11245932 | Logic API (CRUD), Validation, Tính toán KPI, Charts Aggregation |
| FE Core & Auth (Mem 5) | Lê Vân Anh | 11245834 | Khung sườn (base.html), UI Đăng nhập/Đăng ký, Menu |
| FE Features & Charts (Mem 6) | Ngô Thị Tuyết Mai | 11245903 | Giao diện chức năng (Dashboard, Wallet, Transaction), Triển khai Chart.js |

---

## 3. Công Nghệ Sử Dụng

### **Bảng công nghệ**

| Thành phần | Công nghệ | Mục đích sử dụng |
|------------|-----------|------------------|
| Ngôn ngữ chính | Python 3.x | Ngôn ngữ lập trình chính của Backend |
| Framework Web | Django 5.x | Quản lý URL, Views và Models |
| API Framework | Django REST Framework (DRF) | Xây dựng các API RESTful cho Frontend |
| Database (Dev) | SQLite3 | Database mặc định cho môi trường phát triển |
| Frontend Core | HTML, Django Templates, JavaScript | Cấu trúc giao diện và logic tương tác |
| Styling/UI | Tailwind CSS hoặc custom CSS | Đảm bảo giao diện đẹp, responsive |
| Biểu đồ | Chart.js | Vẽ biểu đồ trên Dashboard |
| Quản lý môi trường | Virtualenv (venv) | Tách biệt thư viện dự án |

---

## 4. Hướng Dẫn Cài Đặt và Khởi chạy (Terminal/VS Code)

Dưới đây là các bước cơ bản để cài đặt và khởi chạy ứng dụng lần đầu tiên:

### **Cách chạy app từ terminal của VSCode**

```bash
# 1. Vào thư mục dự án (Sửa lại đường dẫn này theo máy của bạn)
cd Đường\Dẫn\Tới\Thu_Muc\ExpenseManager

# 2. Tạo môi trường ảo (Chỉ chạy 1 lần đầu tiên)
python -m venv venv

# 3. Kích hoạt môi trường ảo
.\venv\Scripts\activate

# 4. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 5. Khởi tạo Database (Tạo bảng & Cấu trúc)
python manage.py makemigrations users finance
python manage.py migrate

# 6. Tạo tài khoản Demo (User: taikhoantest / Pass: 1)
python manage.py create_test_user

# 7. Bật Web
python manage.py runserver

