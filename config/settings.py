import os
from pathlib import Path

# BASE_DIR: Đường dẫn gốc của thư mục dự án trên máy tính.
# Giúp Django biết file db.sqlite3 hay folder templates nằm ở đâu.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: Chìa khóa mật mã để mã hóa session và password.
# Khi đưa lên mạng (deploy), tuyệt đối không được để lộ chuỗi này.
SECRET_KEY = 'django-insecure-YOUR-SECRET-KEY-HERE'

# DEBUG: Chế độ gỡ lỗi.
# True = Đang code (Nếu lỗi sẽ hiện thông báo chi tiết màu vàng để sửa).
# False = Chạy thật (Ẩn lỗi đi để hacker không biết cấu trúc web).
DEBUG = True

# ALLOWED_HOSTS: Danh sách tên miền được phép truy cập web này.
# '*' nghĩa là cho phép tất cả (dùng khi đang test trên máy cá nhân).
ALLOWED_HOSTS = ['*']

# --- 1. APPS CONFIGURATION (Cấu hình Ứng dụng) ---
# Đây là nơi khai báo "Nhà mình có những phòng ban nào".
INSTALLED_APPS = [
    # --- Các app mặc định của Django (Quản trị, Xác thực, Session...) ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Thư viện cài thêm (Third-party) ---
    'rest_framework',           # Bộ công cụ làm API
    'rest_framework.authtoken', # Cơ chế đăng nhập bằng Token (Chìa khóa số)
    'corsheaders',              # Cơ chế cho phép Frontend gọi Backend

    # --- Local Apps (Các module do nhóm tự code) ---
    # QUAN TRỌNG: Phải khai báo ở đây thì Django mới nhận diện được code của các bạn.
    'apps.users',    # Module Quản lý người dùng (User)
    'apps.finance',  # Module Tài chính (Transaction, Budget...)
    'apps.web',      # Module Giao diện (HTML/JS)
]

# MIDDLEWARE: Các lớp bảo vệ trung gian.
# Mọi yêu cầu (Request) từ người dùng phải đi qua các lớp cửa này trước khi vào nhà.
MIDDLEWARE = [
    # QUAN TRỌNG: corsheaders phải đặt lên ĐẦU TIÊN để xử lý kết nối ngay lập tức.
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Chỉ định file điều hướng tổng (File bản đồ chỉ đường)
ROOT_URLCONF = 'config.urls'

# Cấu hình Giao diện (Template HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Django sẽ tự tìm file HTML trong thư mục 'templates' của từng App.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# File chạy server khi đưa lên môi trường thật (Deploy)
WSGI_APPLICATION = 'config.wsgi.application'

# --- 2. DATABASE (Cấu hình Kho dữ liệu) ---
# Hiện tại dùng SQLite (file db.sqlite3) vì nó gọn nhẹ, không cần cài đặt server database phức tạp.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- 3. CUSTOM USER MODEL ---
# Dòng này cực quan trọng!
# Nó bảo Django: "Đừng dùng bảng User mặc định nữa. Hãy dùng bảng 'User' mà nhóm tôi tự thiết kế trong app 'users'".
# Giúp ta thêm được các trường như: Tên hiển thị, Avatar...
AUTH_USER_MODEL = 'users.User'

# --- 4. DRF CONFIG (Luật chơi của API) ---
REST_FRAMEWORK = {
    # Xác thực: Chấp nhận đăng nhập bằng Token (cho App/Frontend) hoặc Session (cho Admin).
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Phân quyền: Mặc định là phải Đăng nhập mới được gọi API (IsAuthenticated).
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Phân trang: Mỗi trang danh sách chỉ trả về 20 kết quả (để tránh lag khi dữ liệu nhiều).
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# --- 5. CORS CONFIG (Giấy phép thông hành) ---
# True = Cho phép mọi nguồn (Web nào cũng gọi được API này).
# Dùng khi đang phát triển. Khi chạy thật sẽ giới hạn lại domain cụ thể.
CORS_ALLOW_ALL_ORIGINS = True

# Cài đặt Ngôn ngữ và Múi giờ
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh' # Giờ Việt Nam
USE_I18N = True
USE_TZ = True

# Cấu hình File tĩnh (CSS, JavaScript, Ảnh)
STATIC_URL = 'static/'
# Nơi chứa file tĩnh riêng của App Web
STATICFILES_DIRS = [
    BASE_DIR / 'apps' / 'web' / 'static',
]
# Nơi gom toàn bộ file tĩnh về một chỗ khi đưa lên server (Deploy)
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'