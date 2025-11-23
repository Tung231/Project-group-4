from django.db import models
from django.conf import settings # tham chiếu đến AUTH_USER_MODEL (apps.users.Users)
from django.utils import timezone # thời gian
from decimal import Decimal # xử lí tiền tệ chuẩn xác

# --- Abstract Logic (Dùng chung cho các bảng cần xoá mềm) ---
class SoftDeleteModel(models.Model): # Lớp trừu tượng cho xoá mềm (soft delete)
    is_active = models.BooleanField(default=True) #  Thêm trường boolean để đánh dấu đối tượng còn hoạt động
    class Meta:
        abstract = True # Lớp này không tạo thành bảng riêng trong DB, mà chỉ dùng để truyền thừa các trường is_active và phương thức delete cho các lớp kế thừa
    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save() # Thay vì xóa đối tượng khỏi DB, nó chỉ đơn giản đặt is_active = False và lưu lại. 

# --- Model: Ví/Tài khoản ---
class Account(SoftDeleteModel): # Kế thừa từ SoftDeleteModel, bảng Account có tính năng xóa mềm 
    TYPE_CHOICES = [('cash', 'Cash'), ('bank', 'Bank Account'), ('e-wallet', 'E-Wallet')] # Lựa chọn loại tài khoản
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts') # Liên kết mỗi ví với 1 User cụ thể, models.CASCADE là khi user bị xóa, tất cả Ví của họ cũng bị xóa 
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES) # Định nghĩa loại ví (tiền măt, ngân hàng, ví điện tử) = choices để giới hạn dữ liệu nhập vào, đảm bảo tính nhất quán
    currency = models.CharField(max_length=10, default='VND')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=0, default=0) # Lưu số dư ban đầu của ví, tối đa 15 chữ số, không có chữ số thập phân
    created_at = models.DateTimeField(auto_now_add=True)

    # Tính toán số dư thực tế (Initial + Thu - Chi)
    @property # Field ảo: không lưu trong DB, mà tính toán khi truy cập 
    def current_balance(self):
        income = self.transactions_received.filter(type__in=['income', 'transfer']).aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)
        expense = self.transactions_sent.filter(type__in=['expense', 'transfer']).aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)
        # sử dụng related_name được định nghĩa trong mô hình Transaction để lọc các giao dịch Thu/Chi liên quan đến ví này, dùng aggregate(Sum) để tính tổng tiền
        return self.initial_balance + income - expense
    # Tính toán số dư hiện tại, Số dư = ban đầu + thu nhập (tới ví) - chi tiêu (từ ví)
    def __str__(self):
        return self.name

# --- Model: Danh mục ---
class Category(SoftDeleteModel): # Danh mục hỗ trợ xóa mềm
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100) 
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)  # Phân loại danh mục là Chi tiêu hay thu nhập
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children') # Tạo cấu trúc danh mục Cha-Con, parent trỏ đến chính mô hình Category (self). null = true, blank = true cho phép danh mục là cấp cao nhất

    def __str__(self):
        return self.name

# --- Model: Giao dịch ---
class Transaction(models.Model): # Không kế thừa Soft Delete, giao dịch bị xóa vĩnh viễn nếu cần 
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income'), ('transfer', 'Transfer')] # Khai báo 3 loại giao dịch: chi, thu, chuyển khoản
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Ví nguồn (Ví bị trừ tiền), ví phát sinh giao dịch, bị trừ tiền đối với expense và transfer. related_name này dùng để tính toán current_balance trong mô hình Account
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_sent')
    
    # Ví đích (Chỉ dùng khi chuyển khoản), chỉ dùng cho giao dịch transfer
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_received') # on_delete=models.SET_NULL giúp giữ lại giao dịch ngay cả khi ví đích bị xóa, related name tính current balance
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions') # account, destination, category liên kết giao dịch với ví và danh mục
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    notes = models.TextField(blank=True, null=True)
    occurred_at = models.DateTimeField(default=timezone.now) # Ngày xảy ra giao dịch, mặc định là thời gian hiện tại
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at'] # Sắp xếp giao dịch theo ngày xảy ra, mới nhất lên đầu

# --- Model: Ngân sách ---
class Budget(models.Model):
    PERIOD_CHOICES = [('weekly', 'Weekly'), ('monthly', 'Monthly')] # Định nghĩa chu kỳ ngân sách có thể là tuần hoặc tháng 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    # Tìm dòng category cũ và thay bằng dòng này:
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets') # Foreign key đến danh mục: liên kết Ngân sách với Danh mục mà người dùng uốn đặt giới hạn chi tiêu
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly') # Lưu trữ chu kỳ đã chọn, mặc định là hàng tháng
    created_at = models.DateTimeField(auto_now_add=True)

# Ý nghĩa của file: file này là xương sống của toàn bộ ứng dụng
# Mọi đối tượng được liên kết chặt chẽ với 1 user
# Logic current_balance trong mô hình Account là nền tảng đề member 4 tính toán các báo cáo và KPI chính xác
# Hỗ trợ tính năng xóa mềm (cho Ví và danh mục) và cấu trúc Cha-con cho danh mục
# Hỗ trợ API và FE, giúp mem 4 viết serializers và viewsets, cũng giúp mem6 thiết kế giao diện như accounts.html và transactions.html
