from django.contrib import admin
from django.urls import path, include

# urlpatterns: Danh sách các con đường trong hệ thống
urlpatterns = [
    # 1. Đường dẫn vào trang Quản trị viên (Có sẵn của Django)
    # Truy cập: domain.com/admin/
    path('admin/', admin.site.urls),
    
    # 2. Đường dẫn API cho Người dùng (Đăng nhập/Đăng ký)
    # Nếu khách gọi 'api/auth/...', chuyển tiếp cho file urls.py trong app 'users' xử lý.
    path('api/auth/', include('apps.users.urls')),
    
    # 3. Đường dẫn API Tài chính (Ví, Giao dịch, Ngân sách...)
    # Nếu khách gọi 'api/finance/...', chuyển tiếp cho file urls.py trong app 'finance' xử lý.
    path('api/finance/', include('apps.finance.urls')),
    
    # 4. Đường dẫn Giao diện Web (Frontend)
    # Nếu đường dẫn không khớp các cái trên (trống rỗng hoặc các trang con khác),
    # chuyển cho app 'web' xử lý hiển thị giao diện HTML.
    # LƯU Ý: Phải đặt cái này ở CUỐI CÙNG để nó hứng tất cả các trường hợp còn lại.
    path('', include('apps.web.urls')),
]