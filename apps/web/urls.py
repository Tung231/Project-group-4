from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ là Landing Page
    path('', views.landing_page_view, name='landing'),
    
    # Dashboard chuyển sang đường dẫn riêng
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('categories/', views.categories_view, name='categories'),
    path('budgets/', views.budgets_view, name='budgets'),
]