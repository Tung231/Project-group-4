# Định nghĩa bảng User trong database

from django.contrib.auth.models import AbstractUser
# Tạo User model custom, kế thừa AbstractUser của Django nên có đủ các trường user (username, password, email,..)
from django.db import models

class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    # Thêm trường mới là tên hiển thị (VD: "Nguyễn Văn A")
    
    def __str__(self):
        return self.username
    # Hiển thị user trong admin
    # Khi frontend gọi API login/register, token trả về gắn với User này
    # Khi chỗ khác dùng get_user_model() sẽ nhận được đúng model User này, chứ không phải auth.User mặc định
