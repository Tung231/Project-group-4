from django.apps import AppConfig # Import lớp cơ sở: lấy lớp AppConfig từ Django, mọi ứng dụng đều phải tạo 1 lớp kế thừa từ AppConfig để tùy chỉnh cấu hình

class FinanceConfig(AppConfig): # Tạo lớp cấu hình riêng cho module nghiệp vụ tài chính, tên lớp theo quy ước là TênAppConfig
    default_auto_field = 'django.db.models.BigAutoField' 
    # Thiết lập kiểu dữ liệu cho khóa chính tự tăng của tất cả các mô hình trong ứng dụng này (account, transactio, budget) 
    name = 'apps.finance' # Phải có 'apps.'
    # Định nghĩa tên đầy đủ của ứng dụng này là app.finance
    # File này giúp nhận diện module, nhờ dòng name = 'apps.finance', thành viên 1 có thể dễ dàng cài đặt module vào hệ thống trong file config/settings.py
    # File này đảm bảo các mô hình trong phần models của finance luôn sử dụng kiểu ID hiện đại (BigAutoField)
    # Giúp khẳng định finance là module độc lập, tách biệt khỉ các module khác