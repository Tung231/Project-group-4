from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.db import transaction
import datetime
from .models import Account, Category, Transaction, Budget
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user, is_active=True)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Lấy giao dịch của user hiện tại, sắp xếp mới nhất trước
        return Transaction.objects.filter(user=self.request.user).order_by('-occurred_at')
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # --- LOGIC 1: API KPI (Tổng thu/chi) ---
    @action(detail=False, methods=['get'])
    def kpi(self, request):
        today = datetime.date.today()
        # Mặc định lấy dữ liệu từ đầu tháng này
        start = request.query_params.get('start_date', today.replace(day=1))
        end = request.query_params.get('end_date', today)
        
        qs = self.get_queryset().filter(occurred_at__date__range=[start, end])
        
        income = qs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0
        expense = qs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0
        
        return Response({
            "income": income, 
            "expense": expense, 
            "net": income - expense
        })

    # --- LOGIC 2: API BIỂU ĐỒ (Charts) ---
    @action(detail=False, methods=['get'])
    def charts(self, request):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30) # 30 ngày gần nhất
        
        qs = self.get_queryset().filter(occurred_at__date__range=[start_date, today])

        # Chart 1: Chi tiêu theo ngày
        daily_stats = qs.filter(type='expense')\
            .annotate(date=TruncDate('occurred_at'))\
            .values('date')\
            .annotate(total=Sum('amount'))\
            .order_by('date')

        # Chart 2: Cơ cấu danh mục
        category_stats = qs.filter(type='expense')\
            .values('category__name')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')

        return Response({
            "daily": list(daily_stats),
            "category": list(category_stats)
        })