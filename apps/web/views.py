from django.shortcuts import render

def login_view(request):
    return render(request, 'web/login.html')

def register_view(request):
    return render(request, 'web/register.html')

def dashboard_view(request):
    return render(request, 'web/dashboard.html')

# --- THÊM 3 HÀM NÀY VÀO CUỐI FILE ---
def accounts_view(request):
    return render(request, 'web/accounts.html')

def categories_view(request):
    return render(request, 'web/categories.html')

def budgets_view(request):
    return render(request, 'web/budgets.html')

def landing_page_view(request):
    return render(request, 'web/landingpage.html')

# ...
def transactions_view(request):
    return render(request, 'web/transactions.html')
# ...