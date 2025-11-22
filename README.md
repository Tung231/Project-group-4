# Cách chạy app từ terminal của VScode nhé

# 1. Vào thư mục dự án (Sửa lại đường dẫn này theo máy của bạn)
cd "Đường\Dẫn\Tới\Thu_Muc\ExpenseManager"

# 2. Tạo môi trường ảo (Chỉ chạy 1 lần đầu tiên)
python -m venv venv

# 3. Kích hoạt môi trường ảo
.\venv\Scripts\activate

# 4. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 5. Khởi tạo Database (Quan trọng: Tạo bảng & Cấu trúc)
python manage.py makemigrations users finance
python manage.py migrate

# 6. Tạo tài khoản Demo (User: taikhoantest / Pass: 1)
python manage.py create_test_user

# 7. Bật Web lên
python manage.py runserver

# 8. Xong mọi người copy cái link http://127.0.0.1:8000/ toàn số mà nó hiện ra ntn vào chrome là chạy nhé
