# ==========================================
# File: auth.py
# Standardized Version
# ==========================================
import streamlit as st

# Import functions from our own modules
import database as db
from utils import show_ephemeral_notice, show_toast, parse_vnd_string, render_ephemeral_notice, money_input
from ui_components import render_table

def render_login_screen():
    """Renders the login and registration tabs."""
    st.title("💸 Expense Manager")
    st.caption("Quản lý chi tiêu cá nhân — Streamlit + SQLite")
    render_ephemeral_notice()
    
    login_tab, register_tab = st.tabs(["Đăng nhập", "Đăng ký"])
    
    with login_tab:
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập", type="primary", use_container_width=True):
            user_id = db.login_user(email, password)
            if user_id:
                st.session_state.user_id = int(user_id)
                show_toast("✅ Đăng nhập thành công")
                st.rerun()
            else:
                show_ephemeral_notice("❌ Sai email hoặc mật khẩu.", "error"); st.rerun()

    with register_tab:
        reg_email = st.text_input("Email đăng ký")
        reg_pw1 = st.text_input("Mật khẩu", type="password", key="reg_pw1")
        reg_pw2 = st.text_input("Nhập lại mật khẩu", type="password", key="reg_pw2")
        if st.button("Tạo tài khoản", use_container_width=True):
            if not reg_email or not reg_pw1:
                show_ephemeral_notice("❌ Vui lòng điền đầy đủ thông tin.", "error"); st.rerun()
            elif reg_pw1 != reg_pw2:
                show_ephemeral_notice("❌ Mật khẩu nhập lại không khớp.", "error"); st.rerun()
            else:
                is_success, message = db.create_user(reg_email, reg_pw1)
                if is_success:
                    show_toast(message); st.rerun()
                else:
                    show_ephemeral_notice(message, "error"); st.rerun()

def render_onboarding_wizard(user_id):
    """Renders the multi-step onboarding process for new users."""
    render_ephemeral_notice()
    st.title("🚀 Thiết lập lần đầu")
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

    # Step 1: Set display name
    if st.session_state.onboarding_step == 1:
        display_name = st.text_input("Tên hiển thị của bạn", "")
        if st.button("Tiếp tục ➜", type="primary", disabled=(not display_name.strip())):
            db.set_user_profile(user_id, display_name.strip())
            st.session_state.onboarding_step = 2
            st.rerun()

    # Step 2: Set initial balances
    elif st.session_state.onboarding_step == 2:
        st.write("Nhập số dư ban đầu cho ví (**số tiền thực tế bạn đang có**):")
        accounts_df = db.get_accounts(user_id)
        try:
            cash_account_id = int(accounts_df[accounts_df["type"]=="cash"]["id"].iloc[0])
            bank_account_id = int(accounts_df[accounts_df["type"]=="bank"]["id"].iloc[0])
        except (IndexError, ValueError):
            st.error("Không tìm thấy ví mặc định. Hãy đăng xuất và đăng ký lại."); return
        
        col1, col2 = st.columns(2)
        cash_balance_str = col1.text_input("Tiền mặt (VND)", placeholder="VD: 2.000.000", key="ob_cash")
        bank_balance_str = col2.text_input("Tài khoản ngân hàng (VND)", placeholder="VD: 8.000.000", key="ob_bank")
        
        if st.button("Lưu & tiếp tục ➜", type="primary"):
            db.execute_query("UPDATE accounts SET opening_balance=? WHERE id=?", (float(parse_vnd_string(cash_balance_str)), cash_account_id))
            db.execute_query("UPDATE accounts SET opening_balance=? WHERE id=?", (float(parse_vnd_string(bank_balance_str)), bank_account_id))
            st.session_state.onboarding_step = 3
            st.rerun()

    # Step 3: Create initial categories
    else:
        st.write("Tạo **ít nhất một danh mục Chi tiêu** và **một danh mục Thu nhập**.")
        all_categories = db.get_categories(user_id)
        
        col1, col2 = st.columns(2)
        with col1:
            expense_cat_name = st.text_input("Tên danh mục Chi tiêu", key="ob_expense")
            if st.button("Thêm danh mục Chi tiêu"):
                if expense_cat_name.strip(): db.add_category(user_id, expense_cat_name.strip(), "expense"); st.rerun()
        with col2:
            income_cat_name = st.text_input("Tên danh mục Thu nhập", key="ob_income")
            if st.button("Thêm danh mục Thu nhập"):
                if income_cat_name.strip(): db.add_category(user_id, income_cat_name.strip(), "income"); st.rerun()

        if not all_categories.empty:
            display_df = all_categories.rename(columns={"name":"Tên","type":"Loại"})[["Tên","Loại"]]
            render_table(display_df, height=220, key_suffix="ob_cats", show_type_filters=False, show_sort_controls=False)

        is_ready = (not db.get_categories(user_id, "expense").empty) and \
                   (not db.get_categories(user_id, "income").empty)
                   
        if st.button("Hoàn tất", type="primary", disabled=(not is_ready)):
            db.finish_onboarding(user_id)
            st.success("Xong! Bắt đầu dùng ứng dụng thôi 🎉")
            st.rerun()