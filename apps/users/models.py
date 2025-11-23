from django.contrib.auth.models import AbstractUser # Import lớp cơ sở: lấy lớp AbstractUser từ Django
# Lớp này chứa sẵn tất cả các trường mặc định của User (username, password, email, first_name, last_name, v.v...)
from django.db import models # Import thư viện model, định nghĩa các trường fields và tạo ra các mô hình sẽ chuyển thành bảng trong database

class User(AbstractUser): # Định nghĩa mô hình User mới, kế thừa tất cả các tính năng và trường dữ liệu từ Abstract User, giúp tùy chỉnh mô hình User mà ko làm mất các chức năng cốt lõi của Django
    # Thêm trường tên hiển thị (VD: "Nguyễn Văn A")
    display_name = models.CharField(max_length=100, blank=True, null=True)
    # Định nghĩa 1 trường mới có tên display_name (tên hiển thị) để lưu trữ tên người dùng có thể tùy chỉnh
    # Giới hạn độ dài tối đa 100 ký tự, cho phép trường này TRỐNG khi nhập liệu qua form và có giá trị NULL trong database
    def __str__(self): # đặc trưng cách hiển thị đối tượng dưới dạng chuỗi (string)
        return self.username # trả về, hiển thị = giá trị của trường username (taikhoantest)
    
    # Ý nghĩa của file: 
    # Cung cấp khả năng mở rộng mô hình User mặc định.
    # Mô hình này là khóa chính để liên kết tất cả các bảng tài chính (account, category, transaction, budget)
    # Mô hình này được sử dụng trong phần users/serializers.py, users/views.py để xử lý logic đăng ký/đăng nhập và cấp token