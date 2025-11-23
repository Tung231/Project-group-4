import os
from pathlib import Path

# 1. BASE_DIR: Đây là đường dẫn gốc tới thư mục dự án. 
# Giúp Django biết tìm file db.sqlite3 hay các folder khác ở đâu.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECRET_KEY: Chìa khóa bảo mật dùng để mã hóa session, password.
# Khi deploy lên mạng, tuyệt đối không được lộ cái này.
SECRET_KEY = 'django-insecure-YOUR-SECRET-KEY-HERE'

# 3. DEBUG: 
# True = Chế độ phát triển (hiện lỗi chi tiết màu vàng khi code sai).
# False = Chế độ chạy thật (ẩn lỗi để hacker không xem được).
DEBUG = True

# 4. ALLOWED_HOSTS: Danh sách các tên miền được phép truy cập web này.
# '*' nghĩa là cho phép tất cả (dùng khi dev). Khi deploy sẽ điền domain thật.
ALLOWED_HOSTS = ['*']

# 5. INSTALLED_APPS: Khai báo các "mảnh ghép" (Module) của dự án.
INSTALLED_APPS = [
    # --- Mặc định của Django (Quản trị, Xác thực, Session...) ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Thư viện cài thêm (Của Người số 1 quản lý) ---
    'rest_framework',           # Giúp xây dựng API (cho Người 2, 4 dùng)
    'rest_framework.authtoken', # Cơ chế đăng nhập bằng Token (cho Người 2 dùng)
    'corsheaders',              # Cho phép Frontend gọi API (Rất quan trọng!)

    # --- Apps tự code (Các module của nhóm) ---
    'apps.users',    # Module Người dùng (Người 2 làm)
    'apps.finance',  # Module Tài chính (Người 3, 4 làm)
    'apps.web',      # Module Giao diện (Người 5, 6 làm)
]

# 6. MIDDLEWARE: Các lớp bảo vệ trung gian. Request đi vào phải qua các lớp này.
MIDDLEWARE = [
    # QUAN TRỌNG: corsheaders phải đặt lên đầu để xử lý kết nối trước tiên.
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# File điều hướng tổng (Cổng chào của web)
ROOT_URLCONF = 'config.urls'

# Cấu hình Giao diện (Template HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Nơi chứa file HTML (Django tự tìm trong folder templates của từng app)
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

# File chạy server (dùng khi deploy lên mạng)
WSGI_APPLICATION = 'config.wsgi.application'

# 7. DATABASES: Cấu hình kho chứa dữ liệu.
# Hiện tại dùng SQLite (file db.sqlite3) cho đơn giản.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 8. AUTH_USER_MODEL: Chỉ định bảng User tùy chỉnh.
# Thay vì dùng bảng User mặc định, ta bảo Django dùng bảng 'User' trong app 'apps.users'.
AUTH_USER_MODEL = 'users.User'

# 9. REST_FRAMEWORK: Cấu hình cho API (Luật chơi của API).
REST_FRAMEWORK = {
    # Xác thực: Chấp nhận đăng nhập bằng Token hoặc Session.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Phân quyền: Mặc định phải Đăng nhập mới được gọi API (IsAuthenticated).
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Phân trang: Mỗi trang danh sách trả về 20 kết quả.
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# 10. CORS CONFIG: Cấu hình cho phép Frontend gọi Backend.
# True = Cho phép mọi nguồn (dùng khi dev).
CORS_ALLOW_ALL_ORIGINS = True

# Ngôn ngữ và Múi giờ
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh' # Giờ Việt Nam
USE_I18N = True
USE_TZ = True

# File tĩnh (CSS, JS, Ảnh)
STATIC_URL = 'static/'
# Dòng này giúp gom file tĩnh lại một chỗ khi deploy
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'