from django.apps import AppConfig 
# Import lớp cơ sở, lấy lớp AppConfig từ Django, đây là lớp mà mọi cấu hình
# ứng dụng phải kế thừa

class UsersConfig(AppConfig): # Tạo 1 lớp cấu hình cho ứng dụng users
    default_auto_field = 'django.db.models.BigAutoField' # Đặt kiểu dữ liệu mặc định cho các trường khóa chính (primary key) trong mô hình của ứng dụng này
    name = 'apps.users'  # Chú ý: Phải có chữ 'apps.' ở đầu
    # Khai báo đầy đủ full path của ứng dụng con 
    # File này biến thư mục finance/ và users/ thành các ứng dụng Django chính thức có thể cài đặt
    # Cấu hình ID model đặt chuẩn về kiểu dữ liệu khóa chính
    # Tổ chức modular