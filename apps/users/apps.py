# Khai báo "ứng dụng" users

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'  
    # Chú ý: Phải có 'apps.' ở đầu vì app users nằm trong thư mục apps để Django nhận diện đường dẫn 
    # 1 package trong python dùng dấu . để phân cấp thư mục
    # Trường name được Django dùng để import models, urls; load signals, migrations
