# 💰 Python Project Group 7: Expense Manager

## 🎯 Introduction

The **Expense Manager** is a powerful and user-friendly web application built with a **Modular Monolith architecture**, using **Python/Django** and **Django REST Framework (DRF)**.  
Its purpose is to help users track, control, and analyze their personal spending habits effectively—reducing financial uncertainty and enabling clear insights into income, expenses, and budgeting.

The system provides a highly structured and intuitive interface, along with a robust backend that ensures data integrity, real-time balance calculation, and interactive financial visualization through charts and KPIs.

Here is the link for our website: https://tunglam021006.pythonanywhere.com/

---

## 1. Project Overview & Key Features

The Expense Manager delivers a complete finance-management solution through an intuitive interface and robust backend design.

### **Key Features**

---

### **🏦 Wallet Management**
- Create, edit, and soft-delete wallets/accounts (Cash, Bank, E-Wallet).
- Real-time calculation of **current_balance**, dynamically updated based on:
  - Income transactions  
  - Expense transactions  
  - Transfer transactions  
- Soft Delete ensures historical transaction data is preserved even if a wallet becomes inactive.

---

### **💳 Transaction Tracking**
- Record three types of transactions:
  - Income  
  - Expense  
  - Transfer (requires both a source and destination wallet)
- Validation rules ensure:
  - Source and destination wallets must not be the same.
  - Transfer transactions must have a target wallet.
- View detailed transaction history with filtering by:
  - Type (Income/Expense)
  - Date range

---

### **📁 Category Management**
- Create hierarchical categories (Parent → Child).  
  Example: “Food” → “Breakfast”, “Lunch”
- Helps users categorize spending more precisely.
- Soft Delete applied to both parent and child categories.

---

### **📊 Dashboard & KPIs**
- Displays essential financial indicators:
  - Total Income  
  - Total Expense  
  - Net Balance
- Visual analytics powered by **Chart.js**:
  - Time-series spending charts (Daily / Monthly / Yearly)
  - Expense distribution by Category (Pie Chart)
- Efficient backend aggregation (Django ORM + DRF) for fast real-time analytics.

---

### **💡 Budgeting**
- Set **Weekly** or **Monthly** budgets for each Expense Category.
- System compares actual spending vs. limits and highlights overspending.

---

## 2. Team Members

### **Team Roles & Responsibilities**

| Role | Member Name | Student ID | Responsibilities | % Contribution |
|------|-------------|------------|------------------|----------------|
| Leader & DevOps (Mem 1) | Trần Tùng Lâm | 11245891 | Core configuration (settings.py), environment setup, Git/Deployment | 18% |
| Backend Authentication (Mem 2) | Đỗ Nhật Hoa Nguyên | 11245918 | User management, Register/Login API, Token Authentication | 16% |
| Backend Data Architect (Mem 3) | Bùi Sơn Tùng | 11245948 | Database design (Models), Soft Delete logic, Data seeding | 17% |
| Backend Logic & API (Mem 4) | Đỗ Minh Thành | 11245932 | API logic (CRUD), Validation, KPI calculations, Chart data aggregation | 16% |
| Frontend Core & Auth (Mem 5) | Lê Vân Anh | 11245834 | Base UI (base.html), Login/Register UI, Navigation menu | 17% |
| Frontend Features & Charts (Mem 6) | Ngô Thị Tuyết Mai | 11245903 | Feature pages (Dashboard, Wallet, Transaction), Chart.js integration | 16% |

---

## 3. Technologies Used

### **Technology Stack**

| Component | Technology | Purpose |
|----------|------------|---------|
| Programming Language | Python 3.x | Backend development |
| Web Framework | Django 5.x | URL routing, Views, Models |
| API Framework | Django REST Framework (DRF) | Build RESTful API for Frontend |
| Development Database | SQLite3 | Default local development database |
| Frontend Core | HTML, Django Templates, JavaScript | UI structure & interactive logic |
| Styling / UI | Tailwind CSS or custom CSS | Responsive and modern UI |
| Charts | Chart.js | Visualization on Dashboard |
| Environment Management | Virtualenv (venv) | Project dependency isolation |

---

## 4. Installation & Setup (Terminal/ VS Code)

Below are the basic steps to install and run the application for the first time.

### **Run the app using VSCode Terminal**

1. Navigate to the project directory (change the path accordingly):
   - `cd Path\To\Your\ExpenseManager`

2. Create a virtual environment (run once):
   - `python -m venv venv`

3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install required dependencies:
   - `pip install -r requirements.txt`

5. Initialize the Database (Create tables & schema):
   - `python manage.py makemigrations users finance`
   - `python manage.py migrate`

6. Create Demo Account (User: taikhoantest / Pass: 1):
   - `python manage.py create_test_user`

7. Run the Web Server:
   - `python manage.py runserver`

---

## 5. Basic User Guide

### 🧭 Workflow Overview

This guide helps users interact with the Expense Manager system, from registration to managing expenses and budgets.

---

#### 1️⃣ Register / Login

- Go to: `/register/` or `/login/`
- Demo Account (for quick testing):
  - **Username:** taikhoantest
  - **Password:** 1

> After successful login, users will be redirected to the Dashboard.

---

#### 2️⃣ Dashboard

- View an overview of personal finances:
  - **Total Income** – Total income
  - **Total Expense** – Total expenses
  - **Net Balance** – Net balance
- Visual data analysis:
  - **Spending trends** – Time-series charts (Daily / Monthly / Yearly)
  - **Category distribution** – Expense distribution by category

> The Dashboard provides quick insights into financial status and helps users evaluate spending efficiency.

---

#### 3️⃣ Wallet Management (`/accounts`)

- Create a new **Wallet/Account**:
  - Enter the **initial_balance** accurately
  - Select type: Cash / Bank / E-Wallet
- Edit wallet information as needed
- Soft Delete wallets:
  - Deleted wallets will no longer appear but **historical data is preserved**
  - Ensures all previous transactions remain intact

---

#### 4️⃣ Transaction Tracking (`/transactions`)

- Add new transactions:
  - Select transaction type: **Income**, **Expense**, **Transfer**
- Important notes:
  - For **Transfer**, both **source wallet** and **destination wallet** must be selected
  - Source and destination wallets must not be the same
- Filter and view transaction history:
  - By type (Income/Expense)
  - By date range

> Transaction Tracking allows daily spending monitoring and accurate reporting.

---

#### 5️⃣ Category Management (`/categories`)

- Add **Parent Category**:
  - Only the name is required, e.g., “Food”, “Transport”
- Add **Child Category**:
  - Select the corresponding Parent, e.g., “Food” → “Breakfast”
- Organize expenses in a hierarchical structure for detailed classification
- Soft Delete applies to both Parent and Child categories

---

#### 6️⃣ Budgeting (`/budgets`)

- Select an **Expense Category** to create a budget
- Set **Weekly** or **Monthly budget**
- The system automatically compares:
  - **Actual spending vs. Budget limit**
  - Highlights overspending

> Budgeting helps users control expenses, avoid waste, and plan finances effectively.
