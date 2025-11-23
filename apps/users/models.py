from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Thêm trường tên hiển thị (VD: "Nguyễn Văn A")
    display_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.username