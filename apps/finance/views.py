from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, Coalesce
from django.db import transaction
import datetime
from decimal import Decimal  # <--- ĐÂY LÀ THƯ VIỆN QUAN TRỌNG VỪA BỊ THIẾU

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
        today = datetime.date.today()
        
        # Logic: Tính tổng tiền chi tiêu trong THÁNG NAY và tổng BUDGET
        return Category.objects.filter(user=self.request.user, is_active=True).annotate(
            # SỬA LỖI: Dùng 'transactions' (số nhiều, đúng với related_name vừa sửa)
            month_spent=Coalesce(Sum(
                'transactions__amount', 
                filter=Q(
                    transactions__occurred_at__year=today.year, 
                    transactions__occurred_at__month=today.month,
                    transactions__type='expense'
                )
            ), Decimal(0)),
            
            # SỬA LỖI: Dùng 'budgets' (số nhiều)
            budget_limit=Coalesce(Sum('budgets__amount'), Decimal(0))
        )

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
        # --- LOGIC LỌC DANH SÁCH (FILTER) ---
        qs = Transaction.objects.filter(user=self.request.user)
        
        # Lọc theo loại
        tx_type = self.request.query_params.get('type')
        if tx_type:
            qs = qs.filter(type=tx_type)
            
        # Sắp xếp
        sort_by = self.request.query_params.get('sort', '-occurred_at')
        qs = qs.order_by(sort_by)
        
        return qs
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def kpi(self, request):
        today = datetime.date.today()
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

    @action(detail=False, methods=['get'])
    def charts(self, request):
        mode = request.query_params.get('mode', 'day') # day, month, year
        today = datetime.date.today()
        
        qs = Transaction.objects.filter(user=request.user, type='expense')

        if mode == 'year':
            start_date = today - datetime.timedelta(days=365*5)
            qs = qs.filter(occurred_at__date__gte=start_date)
            daily_stats = qs.annotate(date=TruncYear('occurred_at')).values('date').annotate(total=Sum('amount')).order_by('date')
            
        elif mode == 'month':
            start_date = today - datetime.timedelta(days=365)
            qs = qs.filter(occurred_at__date__gte=start_date)
            daily_stats = qs.annotate(date=TruncMonth('occurred_at')).values('date').annotate(total=Sum('amount')).order_by('date')
            
        else: 
            start_date = today - datetime.timedelta(days=30)
            qs = qs.filter(occurred_at__date__gte=start_date)
            daily_stats = qs.annotate(date=TruncDate('occurred_at')).values('date').annotate(total=Sum('amount')).order_by('date')

        category_stats = qs.values('category__name').annotate(total=Sum('amount')).order_by('-total')

        return Response({
            "timeline": list(daily_stats),
            "category": list(category_stats)
        })