import streamlit as st
import datetime as dt
import sys
sys.path.append(".")

import database as db
from utils import money_input, join_date_time, show_toast, show_ephemeral_notice

def render_page(user_id):
    st.title("🧾 Thêm giao dịch mới")

    accounts = db.get_accounts(user_id)
    if accounts.empty:
        st.warning("⚠️ Vui lòng tạo ít nhất 1 tài khoản trước khi thêm giao dịch.")
        st.stop()

    transaction_type_display = st.radio("Loại giao dịch", ["Chi tiêu", "Thu nhập"], horizontal=True)
    transaction_type = "expense" if transaction_type_display == "Chi tiêu" else "income"

    all_categories = db.get_categories(user_id, transaction_type)
    if all_categories.empty:
        st.warning("⚠️ Chưa có danh mục phù hợp. Hãy tạo danh mục ở trang 'Danh mục' trước.")
        st.stop()

    parent_categories = all_categories[all_categories["parent_id"].isna()].copy().sort_values("name")
    parent_name = st.selectbox("Danh mục", parent_categories["name"])
    parent_id = int(parent_categories.loc[parent_categories["name"] == parent_name, "id"].iloc[0])

    child_categories = all_categories[all_categories["parent_id"] == parent_id].copy().sort_values("name")
    child_options = ["(Không)"] + (child_categories["name"].tolist() if not child_categories.empty else [])
    child_name = st.selectbox("Danh mục con (nếu có)", child_options, index=0)

    category_id = parent_id if (child_name == "(Không)" or child_categories.empty) else int(child_categories.loc[child_categories["name"] == child_name, "id"].iloc[0])

    account_name = st.selectbox("Chọn ví/tài khoản", accounts["name"])
    account_id = int(accounts.loc[accounts["name"] == account_name, "id"].iloc[0])

    amount = money_input("💰 Số tiền (VND)", key="add_tx_amount", placeholder="VD: 5.000.000")
    notes = st.text_input("📝 Ghi chú (tùy chọn)")

    use_current_time = st.checkbox("Dùng thời gian hiện tại", value=True)
    if use_current_time:
        occurred_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        transaction_date = st.date_input("Ngày giao dịch", value=dt.date.today())
        transaction_time = st.time_input("Giờ giao dịch", value=dt.datetime.now().time().replace(second=0, microsecond=0))
        occurred_datetime = join_date_time(transaction_date, transaction_time)

    if st.button("💾 Lưu giao dịch", type="primary", use_container_width=True):
        try:
            if amount <= 0:
                show_ephemeral_notice("Số tiền phải lớn hơn 0.", "error")
                st.stop()
            db.add_transaction(user_id, account_id, transaction_type, category_id, amount, notes, occurred_datetime)
            show_toast("Đã thêm giao dịch thành công")
            if "add_tx_amount__ui" in st.session_state:
                del st.session_state["add_tx_amount__ui"]
            st.rerun()
        except Exception as e:
            show_ephemeral_notice(f"Lưu thất bại. Vui lòng kiểm tra lại dữ liệu. ({e})", "error")