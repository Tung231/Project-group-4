# Bộ lọc & tạo user khi đăng ký

from rest_framework import serializers
"""Serializers là công cụ chuyển đổi kiểu dữ liệu phức tạp của Django (model, QuerySet)
thành định dạng dữ liệu JSON mà API có thể hiểu và ngược lại"""
from django.contrib.auth import get_user_model

User = get_user_model()
# Lấy đúng model User custom trong models.py

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Serializer dùng password mà frontend gửi để tạo user nhưng không trả lại password cho client 

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'display_name']
        # Quy định những trường API cho phép nhận/ trả

    def create(self, validated_data):
        """ Dùng User.objects.create_user(...) thay vì User(...) vì create_user sẽ tự
        hash password (chuyển password từ text thành dạng chuỗi không thể đảo ngược, 
        chuỗi luôn khác dù password có giống nhau) → bảo mật hơn nếu database bị hack 
        & backend không đọc được password thật và Django bắt password phải được hash"""
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data.get('email', ''),
            password = validated_data['password'],
            display_name = validated_data.get('display_name', '')
        )
        """
        def create_user(self, username, email=None, password=None, **extra_fields):
            user = self.model(username=username, email=email, **extra_fields)
            user.set_password(password)   # <--- HASH xảy ra ở đây!
            user.save()
            return user
        def set_password(self, raw_password):
            self.password = make_password(raw_password) # Hàm tạo hash
        """
        return user # Trả về user mới -> view sẽ dùng để tạo token -> trả JSON
                    # View là nơi xử lý request và trả response (RegisterView trong views.py)
    