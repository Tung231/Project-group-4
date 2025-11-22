from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# --- Abstract Logic (Dùng chung cho các bảng cần xoá mềm) ---
class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)
    class Meta:
        abstract = True
    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()

# --- Model: Ví/Tài khoản ---
class Account(SoftDeleteModel):
    TYPE_CHOICES = [('cash', 'Cash'), ('bank', 'Bank Account'), ('e-wallet', 'E-Wallet')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=10, default='VND')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Tính toán số dư thực tế (Initial + Thu - Chi)
    @property
    def current_balance(self):
        income = self.transactions_received.filter(type__in=['income', 'transfer']).aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)
        expense = self.transactions_sent.filter(type__in=['expense', 'transfer']).aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)
        return self.initial_balance + income - expense

    def __str__(self):
        return self.name

# --- Model: Danh mục ---
class Category(SoftDeleteModel):
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

# --- Model: Giao dịch ---
class Transaction(models.Model):
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income'), ('transfer', 'Transfer')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Ví nguồn (Ví bị trừ tiền)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_sent')
    
    # Ví đích (Chỉ dùng khi chuyển khoản)
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_received')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    notes = models.TextField(blank=True, null=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']

# --- Model: Ngân sách ---
class Budget(models.Model):
    PERIOD_CHOICES = [('weekly', 'Weekly'), ('monthly', 'Monthly')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Tìm dòng category cũ và thay bằng dòng này:
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    created_at = models.DateTimeField(auto_now_add=True)