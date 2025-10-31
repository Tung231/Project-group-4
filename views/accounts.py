import streamlit as st
import pandas as pd
import sys
sys.path.append(".")

import database as db
from utils import format_vnd, money_input, show_toast
from ui_components import render_table

def render_page(user_id):
    st.title("👛 Ví / Tài khoản")

    accounts_df = db.get_accounts_with_balance(user_id)

    if accounts_df.empty:
        st.info("Chưa có ví nào.")
    else:
        display_df = pd.DataFrame({
            "Tên": accounts_df["name"],
            "Loại": accounts_df["type"].map({"cash":"Tiền mặt","bank":"Tài khoản ngân hàng","card":"Thẻ"}),
            "Tiền tệ": accounts_df["currency"],
            "Số dư hiện tại": accounts_df["balance"].map(format_vnd)
        })
        render_table(display_df, default_sort_col="Số dư hiện tại", default_asc=False, key_suffix="accounts",
                     show_type_filters=False, show_sort_controls=True)

    st.markdown("#### Thêm ví mới")
    account_name = st.text_input("Tên ví (tuỳ chọn)")
    account_type = st.selectbox("Loại",["cash","bank","card"], format_func=lambda x: {"cash":"Tiền mặt","bank":"Tài khoản ngân hàng","card":"Thẻ"}[x])
    opening_balance = money_input("Số dư ban đầu (VND)", key="open_balance", placeholder="VD: 2.000.000")

    if st.button("Thêm ví", type="primary"):
        default_name = {"cash":"Tiền mặt","bank":"Tài khoản ngân hàng","card":"Thẻ"}[account_type]
        db.add_account(user_id, account_name or default_name, account_type, opening_balance)
        show_toast("Đã thêm ví mới!")
        if "open_balance__ui" in st.session_state:
            del st.session_state["open_balance__ui"]
        st.rerun()