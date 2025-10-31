import streamlit as st
import datetime as dt
import pandas as pd
import sys
sys.path.append(".")

import database as db
from utils import money_input, show_toast, format_vnd
from ui_components import render_table

def render_page(user_id):
    st.title("🎯 Ngân sách")
    st.caption("Đặt hạn mức chi tiêu theo khoảng ngày cho từng danh mục Chi tiêu.")

    categories_df = db.get_categories(user_id, "expense")
    if categories_df.empty:
        st.info("Chưa có danh mục Chi tiêu để đặt ngân sách."); st.stop()

    selected_category = st.selectbox("Danh mục", categories_df["name"])
    category_id = int(categories_df[categories_df["name"]==selected_category]["id"].iloc[0])
    start_date = st.date_input("Từ ngày", value=dt.date.today().replace(day=1))
    end_date = st.date_input("Đến ngày", value=dt.date.today())
    amount = money_input("Hạn mức (VND)", key="budget_amount", placeholder="VD: 2.500.000")

    col1, col2 = st.columns([1,1])
    if col1.button("Lưu hạn mức", type="primary"):
        db.execute_query("INSERT INTO budgets(user_id,category_id,amount,start_date,end_date) VALUES(?,?,?,?,?)", (user_id, category_id, float(amount), str(start_date), str(end_date)))
        show_toast("Đã lưu hạn mức!")
        if "budget_amount__ui" in st.session_state:
            del st.session_state["budget_amount__ui"]
        st.rerun()

    with col2.popover("🗑️ Xoá hạn mức", use_container_width=True):
        budgets_df = db.get_df("SELECT b.id, c.name AS category, b.start_date, b.end_date, b.amount FROM budgets b JOIN categories c ON c.id=b.category_id WHERE b.user_id=? ORDER BY b.start_date DESC", (user_id,))
        if budgets_df.empty:
            st.caption("Chưa có hạn mức để xoá.")
        else:
            options = [f"{r['category']} ({r['start_date']}→{r['end_date']}) - {format_vnd(r['amount'])} VND" for _,r in budgets_df.iterrows()]
            selection = st.selectbox("Chọn hạn mức", options)
            selected_index = options.index(selection)
            budget_id_to_delete = int(budgets_df.iloc[selected_index]["id"])
            if st.button("Xác nhận xoá", type="secondary"):
                db.delete_budget(user_id, budget_id_to_delete)
                show_toast("Đã xoá hạn mức.")
                st.rerun()

    st.divider()
    st.markdown("#### Hạn mức hiện có (kèm số đã dùng & %)")
    all_budgets_df = db.get_all_budgets_with_progress(user_id)
    if all_budgets_df is None or all_budgets_df.empty:
        st.info("Chưa có hạn mức.")
    else:
        today = dt.date.today()
        active_budgets_df = all_budgets_df[pd.to_datetime(all_budgets_df["Đến ngày"]).dt.date >= today]
        
        if active_budgets_df.empty:
            st.info("Không có hạn mức đang diễn ra.")
        else:
            def get_status_cell(percent: float) -> str:
                if percent < 70: return "🟢 Dưới 70%"
                if percent < 90: return "🟠 70–89%"
                if percent <= 100: return "🔴 90–100% ⚠️"
                return "🔴 Vượt hạn ⚠️"

            display_df = active_budgets_df.copy()
            display_df["Đã dùng (VND)"] = display_df["Đã dùng"].map(format_vnd)
            display_df["Hạn mức (VND)"] = display_df["Hạn mức"].map(format_vnd)
            display_df["%"] = pd.to_numeric(display_df["%"], errors="coerce").fillna(0.0).round(0)
            display_df["Cảnh báo"] = display_df["%"].apply(lambda x: get_status_cell(float(x)))
            display_df = display_df[["Cảnh báo", "Danh mục", "Từ ngày", "Đến ngày", "Đã dùng (VND)", "Hạn mức (VND)", "%"]]

            render_table(display_df, default_sort_col="%", default_asc=False, key_suffix="budgets_progress", show_type_filters=False)

            over_budget_df = active_budgets_df[active_budgets_df["%"] >= 100]
            if not over_budget_df.empty:
                names = " · ".join(over_budget_df["Danh mục"].astype(str).tolist()[:8])
                extra = "" if len(over_budget_df) <= 8 else f" (+{len(over_budget_df)-8})"
                st.error(f"⚠ Có {len(over_budget_df)} danh mục **vượt hạn mức**: {names}{extra}")