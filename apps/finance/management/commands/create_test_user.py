from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.finance.models import Account, Category, Transaction, Budget
from django.utils import timezone
import random
import datetime
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo user taikhoantest với dữ liệu mẫu đẹp để test giao diện'

    def handle(self, *args, **kwargs):
        self.stdout.write("Dang khoi tao du lieu cho 'taikhoantest'...")

        # 1. TẠO USER (taikhoantest / 1)
        user, created = User.objects.get_or_create(username='taikhoantest')
        user.set_password('1') # Password là 1
        user.display_name = "Tester Đại Gia"
        user.email = "test@expense.local"
        user.save()
        
        # Xóa dữ liệu cũ của user này (nếu có) để tránh trùng lặp khi chạy lại
        Transaction.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        Category.objects.filter(user=user).delete()
        Account.objects.filter(user=user).delete()

        # 2. TẠO VÍ (Accounts)
        cash = Account.objects.create(user=user, name="Ví Tiền mặt", type='cash', initial_balance=5000000)
        bank = Account.objects.create(user=user, name="TPBank", type='bank', initial_balance=50000000)
        ewallet = Account.objects.create(user=user, name="MoMo", type='e-wallet', initial_balance=2000000)

        # 3. TẠO DANH MỤC (Categories - Có cha/con)
        # -- Chi tiêu --
        c_food = Category.objects.create(user=user, name="Ăn uống", type="expense")
        c_food_bf = Category.objects.create(user=user, name="Ăn sáng", type="expense", parent=c_food)
        c_food_cf = Category.objects.create(user=user, name="Cà phê", type="expense", parent=c_food)
        
        c_move = Category.objects.create(user=user, name="Di chuyển", type="expense")
        c_move_gas = Category.objects.create(user=user, name="Xăng xe", type="expense", parent=c_move)
        
        c_shopping = Category.objects.create(user=user, name="Mua sắm", type="expense")
        c_bill = Category.objects.create(user=user, name="Hóa đơn", type="expense")

        # -- Thu nhập --
        c_salary = Category.objects.create(user=user, name="Lương cứng", type="income")
        c_bonus = Category.objects.create(user=user, name="Thưởng nóng", type="income")

        # 4. TẠO NGÂN SÁCH (Budgets)
        # Ngân sách Ăn uống: 5 triệu/tháng
        Budget.objects.create(user=user, category=c_food, amount=5000000, period='monthly')
        # Ngân sách Di chuyển: 1 triệu/tháng
        Budget.objects.create(user=user, category=c_move, amount=1000000, period='monthly')

        # 5. TẠO GIAO DỊCH (Transactions) - Random 40 cái trong 30 ngày qua
        today = timezone.now()
        accounts = [cash, bank, ewallet]
        expenses = [c_food, c_food_bf, c_food_cf, c_move_gas, c_shopping, c_bill]
        
        # Tạo 1 giao dịch Lương đầu tháng
        Transaction.objects.create(
            user=user, account=bank, category=c_salary, type='income',
            amount=25000000, notes="Lương tháng này", occurred_at=today - datetime.timedelta(days=15)
        )

        # Random chi tiêu
        for i in range(40):
            days_ago = random.randint(0, 30)
            fake_date = today - datetime.timedelta(days=days_ago)
            
            # 80% là chi tiêu
            if random.random() > 0.2:
                cat = random.choice(expenses)
                # Random tiền từ 30k đến 500k
                amt = random.randint(3, 50) * 10000 
                acc = random.choice(accounts)
                
                Transaction.objects.create(
                    user=user, account=acc, category=cat, type='expense',
                    amount=amt, notes=f"Chi tiêu mẫu {i+1}", occurred_at=fake_date
                )
            # 20% là thu nhập thêm
            else:
                amt = random.randint(5, 20) * 100000
                Transaction.objects.create(
                    user=user, account=bank, category=c_bonus, type='income',
                    amount=amt, notes="Freelance job", occurred_at=fake_date
                )

        self.stdout.write(self.style.SUCCESS(f"✅ XONG! User: taikhoantest / Pass: 1"))