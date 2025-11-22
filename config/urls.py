from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/finance/', include('apps.finance.urls')),
    
    # Frontend Web URLs (Để ở cuối cùng)
    path('', include('apps.web.urls')),
]