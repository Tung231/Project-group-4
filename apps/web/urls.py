from django.urls import path
from . import views

urlpatterns = [
    path('landing/', views.landing_page_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.dashboard_view, name='dashboard'),
    
    # --- THÊM 3 DÒNG NÀY ---
    path('accounts/', views.accounts_view, name='accounts'),
    path('categories/', views.categories_view, name='categories'),
    path('budgets/', views.budgets_view, name='budgets'),
]