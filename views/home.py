import streamlit as st
import datetime as dt
import pandas as pd
import sys
sys.path.append(".") 

import database as db
import ui_components as ui
from utils import (
    get_start_date_months_back, get_year_window,
    format_transactions_df_for_display, METADATA_COLUMNS_TO_DROP
)

def render_page(user_id):
    st.title("🏠 Trang chủ")

    # --- Date Range Filter ---
    today = dt.date.today()
    if "filter_start" not in st.session_state: st.session_state.filter_start = today.replace(day=1)
    if "filter_end" not in st.session_state: st.session_state.filter_end = today

    col1, col2 = st.columns(2)
    st.session_state.filter_start = col1.date_input("Từ ngày", st.session_state.filter_start)
    st.session_state.filter_end = col2.date_input("Đến ngày", st.session_state.filter_end)

    current_start, current_end = st.session_state.filter_start, st.session_state.filter_end

    if "home_mode" not in st.session_state: st.session_state.home_mode = "day"

    # --- KPIs ---
    ui.render_kpi_metrics(user_id, current_start, current_end, st.session_state.home_mode)
    st.divider()

    # <<< THÊM DÒNG NÀY >>>
    st.markdown("## Biểu đồ chi tiêu")
    # <<< ------------------ >>>

    # --- Chart Controls (ĐÃ BỎ "TUẦN") ---
    ctl1, ctl2, _ = st.columns([1.2, 1.0, 2])
    
    mode_display = ctl1.radio(
        "Chế độ hiển thị", 
        ["Ngày", "Tháng", "Năm"], # Chỉ còn 3 lựa chọn
        horizontal=True, 
        index=["day", "month", "year"].index(st.session_state.home_mode)
    )
    mode_key = {"Ngày": "day", "Tháng": "month", "Năm": "year"}[mode_display] # Bỏ "Tuần"
    st.session_state.home_mode = mode_key
    chart_type = ctl2.radio("Kiểu biểu đồ", ["Cột", "Đường"], horizontal=True, index=0)

    # --- SỬA LOGIC KHOẢNG NGÀY CHO BIỂU ĐỒ ---
    anchor_date = current_end

    if mode_key == "day":
        chart_d1 = anchor_date.replace(day=1)
        next_month_start = (chart_d1 + dt.timedelta(days=32)).replace(day=1)
        chart_d2 = next_month_start - dt.timedelta(days=1)
    elif mode_key == "month": 
        chart_d1 = get_start_date_months_back(anchor_date, 12)
        chart_d2 = anchor_date
    elif mode_key == "year": 
        chart_d1, chart_d2 = get_year_window(anchor_date, 5)
    else:
        chart_d1, chart_d2 = current_start, current_end
    # -------------------------------------------

    # --- Charts ---
    colA, colB = st.columns([2, 1])
    with colA:
        st.markdown(f"#### Biểu đồ theo {mode_display.lower()}")
        ui.render_spending_chart(user_id, chart_d1, chart_d2, mode_key, chart_type, db.query_expense_aggregation)
        st.caption(f"Khoảng hiển thị: {chart_d1} → {chart_d2}")
    with colB:
        st.markdown("#### Cơ cấu theo danh mục")
        group_by_parent = st.toggle("Gộp theo danh mục cha", value=True, key="home_group_parent")
        ui.render_pie_chart_by_category(user_id, current_start, current_end, group_by_parent, db.get_df)

    # --- Budget Alerts ---
    st.divider()
    st.markdown("#### 🚨 Cảnh báo các hạn mức")
    budget_alerts_df = db.get_budget_progress_df(user_id, current_start, current_end)
    if budget_alerts_df is None or budget_alerts_df.empty:
        st.success("🎉 Chưa có danh mục nào gần chạm hoặc vượt hạn mức.")
    else:
        top_5_alerts = budget_alerts_df.sort_values("%", ascending=False).head(5)
        ui.render_budget_progress_chart(top_5_alerts, title="")

    # --- Recent Transactions ---
    st.divider()
    st.markdown("#### Giao dịch gần đây")
    recent_trans_raw = db.get_transactions(user_id, today - dt.timedelta(days=7), today)
    recent_trans_df = format_transactions_df_for_display(recent_trans_raw)
    if recent_trans_df is None or recent_trans_df.empty:
        st.info("Chưa có giao dịch tuần này.")
    else:
        if "Loại" in recent_trans_df.columns:
            recent_trans_df["Loại"] = recent_trans_df["Loại"].map({"Thu nhập": "🟢 Thu nhập", "Chi tiêu": "🔴 Chi tiêu"}).fillna(recent_trans_df["Loại"])
        
        recent_trans_df = recent_trans_df.drop(columns=[c for c in recent_trans_df.columns if c in METADATA_COLUMNS_TO_DROP], errors="ignore")
        recent_trans_df.insert(0, "STT", range(1, len(recent_trans_df) + 1))
        st.dataframe(recent_trans_df.head(10), use_container_width=True, height=260, hide_index=True)