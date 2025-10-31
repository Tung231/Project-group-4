# Ứng dụng Quản lý Chi tiêu (Expense Manager)
Đây là project môn học [Tên môn học của bạn], thực hiện bởi Nhóm 4. Ứng dụng được xây dựng bằng **Python (Streamlit)** và **SQLite** để quản lý thu chi cá nhân.

---

## 1. Các tính năng chính
* **Xác thực người dùng:** Đăng nhập, đăng ký và quy trình onboarding (thiết lập ban đầu).
* **Quản lý giao dịch:** Thêm, xem, lọc các khoản thu/chi.
* **Dashboard (Trang chủ):**
    * Hiển thị KPI (Tổng thu, Tổng chi, Chênh lệch) so với kỳ trước.
    * Biểu đồ chi tiêu theo Ngày, Tháng, Năm (với các ngày 0 đồng được lấp đầy).
    * Biểu đồ tròn cơ cấu chi tiêu (có hiển thị %).
* **Danh mục Cha/Con:** Cho phép tạo danh mục (VD: "Ăn uống") và danh mục con (VD: "Ăn trưa"), báo cáo tự động gộp nhóm.
* **Ngân sách (Hạn mức):**
    * Đặt hạn mức chi tiêu cho từng danh mục.
    * Cảnh báo trực quan (Xanh, Vàng, Đỏ) khi sắp vượt hoặc đã vượt hạn mức.
* **Báo cáo & Xuất file:** Xem top chi tiêu và xuất dữ liệu ra file `.csv` hoặc `.xlsx`.

---

## 2. Cấu trúc Project (Yêu cầu 2)
Project được tổ chức theo mô hình module để đảm bảo tính **rõ ràng** và **dễ bảo trì**:

---

## 3. Phân công nhiệm vụ (Yêu cầu 3)
Dưới đây là bảng phân công nhiệm vụ của các thành viên trong nhóm:

| STT | Họ và Tên | MSSV | Nhiệm vụ chính | Module chịu trách nhiệm |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **(Tên thành viên 1)** | (MSSV) | (VD: Nhóm trưởng, Thiết kế CSDL) | `database.py`, `auth.py` |
| 2 | **(Tên thành viên 2)** | (MSSV) | (VD: Phát triển Giao diện chính) | `views/home.py`, `ui_components.py` |
| 3 | **(Tên thành viên 3)** | (MSSV) | (VD: Phát triển các tính năng) | `views/transactions.py`, `views/budgets.py` |
| 4 | **(Tên thành viên 4)** | (MSSV) | (VD: Xử lý logic chung & báo cáo) | `app.py`, `utils.py`, `views/reports.py` |

*(Bạn hãy tự sửa lại bảng trên cho đúng với nhóm của mình nhé)*

---


