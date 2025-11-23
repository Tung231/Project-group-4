from django.contrib import admin
from django.urls import path, include

# Đây là bản đồ chỉ đường của toàn bộ website
urlpatterns = [
    # 1. Đường dẫn vào trang quản trị Admin (có sẵn của Django)
    path('admin/', admin.site.urls),
    
    # 2. Đường dẫn API Xác thực (Đăng nhập, Đăng ký)
    # Nếu user gọi vào 'api/auth/...', chuyển tiếp cho file urls.py trong app 'users' xử lý.
    path('api/auth/', include('apps.users.urls')),
    
    # 3. Đường dẫn API Tài chính (Ví, Giao dịch...)
    # Nếu user gọi vào 'api/finance/...', chuyển tiếp cho app 'finance' xử lý.
    path('api/finance/', include('apps.finance.urls')),
    
    # 4. Đường dẫn Giao diện (Trang chủ, HTML)
    # Nếu không phải các đường dẫn trên (đường dẫn trống ''), chuyển cho app 'web' xử lý hiển thị.
    path('', include('apps.web.urls')),
]