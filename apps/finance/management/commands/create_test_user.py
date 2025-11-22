from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.finance.models import Account, Category, Transaction, Budget
from django.utils import timezone
import random
import datetime
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo user taikhoantest với dữ liệu 2 năm + BUDGET ĐẦY ĐỦ'

    def handle(self, *args, **kwargs):
        self.stdout.write("Dang khoi tao du lieu 'taikhoantest'...")

        # 1. RESET
        user, _ = User.objects.get_or_create(username='taikhoantest')
        user.set_password('1')
        user.display_name = "Tester Đại Gia"
        user.email = "test@expense.local"
        user.save()
        
        Transaction.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        Category.objects.filter(user=user).delete()
        Account.objects.filter(user=user).delete()

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
        
        for i in range(24):
            Transaction.objects.create(user=user, account=bank, category=c_salary, type='income', amount=25000000, notes=f"Lương tháng", occurred_at=today - datetime.timedelta(days=i*30))

        for i in range(300):
            days_ago = random.randint(0, 700)
            fake_date = today - datetime.timedelta(days=days_ago)
            if random.random() > 0.2:
                Transaction.objects.create(user=user, account=random.choice(accounts), category=random.choice(all_expense_cats), type='expense', amount=Decimal(random.randint(3, 50) * 10000), notes=f"Chi tiêu {i}", occurred_at=fake_date)
            else:
                Transaction.objects.create(user=user, account=bank, category=c_bonus, type='income', amount=Decimal(random.randint(5, 20) * 100000), notes="Thưởng", occurred_at=fake_date)

        self.stdout.write(self.style.SUCCESS(f"✅ XONG! Đã có Budget và Giao dịch."))