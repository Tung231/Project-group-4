# ==========================================
# File: app.py (Main Shell)
# PHIÊN BẢN SỬA LỖI
# ==========================================
import streamlit as st
import datetime as dt

# Import các module
import database
import auth
from utils import show_toast, render_ephemeral_notice

# Import các "trang" từ thư mục 'views'
from views import home, transactions, accounts, categories, budgets, reports, about

st.set_page_config(page_title="Expense Manager", page_icon="💸", layout="wide")

def main_app(user_id, user_data):
    """
    Hiển thị ứng dụng chính sau khi đăng nhập.
    Đây là nơi xử lý Fix #1, #3, #4.
    """
    
    # (FIX #1 và #4) Sidebar được vẽ ở đây, TRÊN CÙNG
    with st.sidebar:
        st.markdown("### 💶 Expense Manager")
        st.write(f"👤 **{user_data['display_name'] or user_data['email']}**")
        st.caption(dt.date.today().strftime("%d/%m/%Y"))
        st.write("---")
        
        # (FIX #4) Tên trang Tiếng Việt
        page_options = [
            "🏠 Trang chủ",
            "🧾 Giao dịch",
            "👛 Ví/Tài khoản",
            "🏷️ Danh mục",
            "🎯 Ngân sách",
            "📈 Báo cáo",
            "ℹ️ Giới thiệu"
        ]
        
        # (FIX #3) Mặc định chọn "Trang chủ"
        if "navigation" not in st.session_state:
            st.session_state.navigation = page_options[0]

        # st.radio để điều hướng
        page = st.radio("Điều hướng", page_options, key="navigation", label_visibility="collapsed")
        
        st.write("---")
        if st.button("Đăng xuất", use_container_width=True):
            st.session_state.clear()
            show_toast("Đã đăng xuất")
            st.rerun()

    # Render nội dung trang chính
    # (FIX #3) Bỏ trang "Chào mừng", render trang được chọn
    render_ephemeral_notice() # Hiển thị thông báo (nếu có)
    
    if page == "🏠 Trang chủ":
        home.render_page(user_id)
    elif page == "🧾 Giao dịch":
        transactions.render_page(user_id)
    elif page == "👛 Ví/Tài khoản":
        accounts.render_page(user_id)
    elif page == "🏷️ Danh mục":
        categories.render_page(user_id)
    elif page == "🎯 Ngân sách":
        budgets.render_page(user_id)
    elif page == "📈 Báo cáo":
        reports.render_page(user_id)
    elif page == "ℹ️ Giới thiệu":
        about.render_page(user_id)

def main():
    database.init_db()

    # --- USER AUTHENTICATION ---
    # (FIX #2) Ẩn sidebar khi đăng nhập
    if "user_id" not in st.session_state:
        auth.render_login_screen() # Trang này không vẽ sidebar
        return

    uid = st.session_state.user_id
    user_data = database.get_user(uid)
    if not user_data:
        st.session_state.clear()
        auth.render_login_screen()
        return

    # --- ONBOARDING WIZARD ---
    # (FIX #2) Ẩn sidebar khi onboarding
    if int(user_data["onboarded"] or 0) == 0:
        auth.render_onboarding_wizard(uid) # Trang này cũng không vẽ sidebar
        return
        
    # --- Đã đăng nhập và onboarding ---
    main_app(uid, user_data)


if __name__ == "__main__":
    main()