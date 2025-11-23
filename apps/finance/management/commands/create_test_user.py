from django.core.management.base import BaseCommand # Import thư viên: Lớp cơ sở tạo các lệnh tùy chỉnh, ví dụ file này sẽ được chạy = lệnh: python manage.py create_test_user
from django.contrib.auth import get_user_model # Import các tiện ích để lấy mô hình User tùy chỉnh hiện tại
from apps.finance.models import Account, Category, Transaction, Budget # Import các mô hình cần thiết từ ứng dụng tài chính (finance)
from django.utils import timezone # Import cung cấp các hàm liên quan đến múi giờ
import random
import datetime
from decimal import Decimal
# Import các thư viện cần thiết để tạo dữ liệu ngẫu nhiên, xử lý số thập phân chính xác
User = get_user_model() # Gán mô hình User vào biến User để sử dụng dễ dàng hơn trong lớp Command

class Command(BaseCommand): # Khai báo lớp command, bắt buộc phải kế thừa từ BaseCommand để Django nhận diện đây là 1 lệnh quản lý
    help = 'Tạo user taikhoantest với dữ liệu 2 năm + BUDGET ĐẦY ĐỦ'
# Mô tả ngắn gọn về chức năng của lệnh này, sẽ hiển thị khi chạy lệnh python manage.py help create_test_user
    def handle(self, *args, **kwargs): # Hàm BẮT BUỘC phải có trong lớp Command, nơi chứa logic chính của lệnh
        self.stdout.write("Dang khoi tao du lieu 'taikhoantest'...") # In ra thông báo khi bắt đầu quá trình tạo dữ liệu (terminal)

        # 1. RESET
        user, _ = User.objects.get_or_create(username='taikhoantest') # Tìm user với username = taikhoantest, nếu không có thì tạo mới, biến user lưu trữ đối tượng user đó
        user.set_password('1') # Đặt mật khẩu 
        user.display_name = "Tester Đại Gia" # Thiết lập tên hiển thị 
        user.email = "test@expense.local" # Thiết lập email
        user.save() # Lưu các thay đổi vào cơ sở dữ liệu
        
        Transaction.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        Category.objects.filter(user=user).delete()
        Account.objects.filter(user=user).delete()
# Xóa tất cả giao dịch, ngân sách, danh mục và tài khoản liên quan đến user này để tránh trùng lặp dữ liệu khi chạy lệnh nhiều lần
        # 2. DANH MỤC
        c_food = Category.objects.create(user=user, name="Ăn uống", type="expense")
        Category.objects.create(user=user, name="Ăn sáng", type="expense", parent=c_food)
        Category.objects.create(user=user, name="Cà phê", type="expense", parent=c_food)
        c_move = Category.objects.create(user=user, name="Di chuyển", type="expense")
        Category.objects.create(user=user, name="Xăng xe", type="expense", parent=c_move)
        c_shop = Category.objects.create(user=user, name="Mua sắm", type="expense")
        c_bill = Category.objects.create(user=user, name="Hóa đơn", type="expense")
        c_salary = Category.objects.create(user=user, name="Lương cứng", type="income")
        c_bonus = Category.objects.create(user=user, name="Thưởng", type="income")

        # 3. TẠO NGÂN SÁCH (PHẦN MỚI THÊM)
        self.stdout.write("--- Dang tao Budget ---")
        Budget.objects.create(user=user, category=c_food, amount=6000000, period='monthly')
        Budget.objects.create(user=user, category=c_move, amount=2000000, period='monthly')
        Budget.objects.create(user=user, category=c_shop, amount=1000000, period='weekly') # Ngân sách tuần

        # 4. VÍ
        cash = Account.objects.create(user=user, name="Ví Tiền mặt", type='cash', initial_balance=10000000)
        bank = Account.objects.create(user=user, name="TPBank", type='bank', initial_balance=100000000)
        accounts = [cash, bank]

        # 5. GIAO DỊCH 2 NĂM
        today = timezone.now()
        all_expense_cats = [c_food, c_move, c_shop, c_bill]
        
        for i in range(24): # Vòng lặp tạo 24 giao dịch 
            Transaction.objects.create(user=user, account=bank, category=c_salary, type='income', amount=25000000, notes=f"Lương tháng", occurred_at=today - datetime.timedelta(days=i*30))
        # Tạo các giao dịch income cố định (lương 25 triệu), đặt ngày xảy ra là lùi về quá khứ theo mỗi lần lặp
        for i in range(300): # Vòng lặp tạo 300 giao dịch ngẫu nhiên
            days_ago = random.randint(0, 700) # Taoj 1 ngày ngẫu nhiên trong 700 ngày qua
            fake_date = today - datetime.timedelta(days=days_ago)
            if random.random() > 0.2: # 80% giao dịch là chi tiêu với số tiền nhỏ từ 30-500k, 20% còn lại là thu nhập với số tiền lớn hơn
                Transaction.objects.create(user=user, account=random.choice(accounts), category=random.choice(all_expense_cats), type='expense', amount=Decimal(random.randint(3, 50) * 10000), notes=f"Chi tiêu {i}", occurred_at=fake_date)
            else:
                Transaction.objects.create(user=user, account=bank, category=c_bonus, type='income', amount=Decimal(random.randint(5, 20) * 100000), notes="Thưởng", occurred_at=fake_date)

        self.stdout.write(self.style.SUCCESS(f"✅ XONG! Đã có Budget và Giao dịch."))

        # File này tạo môi trường thử nghiệm cho toàn đội phát triển: giúp mọi người hiểu qua về các chức năng của app, giúp có sẵn các dữ liệu thực tế để kiểm tra các hàm tính toán xem chuẩn chưa. Đảm bảo web chạy và test các tính năng 1 cách hiệu quả