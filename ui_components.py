# ==========================================
# File: ui_components.py
# Standardized Version
# ==========================================
import streamlit as st
import pandas as pd
import altair as alt
import datetime as dt
import math
from typing import Tuple

# Import helpers from our own modules
from utils import strip_accents_and_lower, format_vnd, COLOR_INCOME, COLOR_EXPENSE, COLOR_NET, METADATA_COLUMNS_TO_DROP
from database import fetch_one

# ---------- Table Rendering ----------
def _detect_column_sort_type(df: pd.DataFrame, col_name: str) -> str:
    """Detects the data type of a column for appropriate sorting."""
    if col_name == "Loại": return "type"
    if col_name in ("Thời điểm", "Ngày giao dịch", "Từ ngày", "Đến ngày"): return "time"
    numeric_cols = ("%", "Đã dùng", "Đã dùng (VND)", "Hạn mức", "Hạn mức (VND)", "Số tiền", "Số dư hiện tại")
    if col_name in numeric_cols: return "number"
    return "text"

def _get_type_sort_key(series: pd.Series) -> pd.Series:
    """Provides a numeric key for sorting transaction types ('Chi tiêu' < 'Thu nhập')."""
    def to_key(x: str) -> int:
        normalized = strip_accents_and_lower(str(x))
        if "chi tieu" in normalized: return 0
        if "thu nhap" in normalized: return 1
        return 2
    return series.astype(str).map(to_key)

def sort_dataframe(df: pd.DataFrame, sort_col: str, ascending: bool):
    """Sorts a DataFrame based on a column and its detected type."""
    if df is None or df.empty or sort_col not in df.columns: return df
    
    sort_type = _detect_column_sort_type(df, sort_col)
    
    if sort_type == "type":
        key_func = _get_type_sort_key
        ascending = True # Fixed order
    elif sort_type == "time":
        key_func = lambda s: pd.to_datetime(s, errors="coerce")
    elif sort_type == "number":
        key_func = lambda s: pd.to_numeric(
            s.astype(str).str.replace(r'[.,\s%]', '', regex=True),
            errors="coerce").fillna(0.0)
    else: # text
        key_func = lambda s: s.astype(str).map(strip_accents_and_lower)
        
    return df.sort_values(by=sort_col, ascending=ascending, key=key_func, kind="mergesort")

def render_table(df: pd.DataFrame, default_sort_col: str | None = None, default_asc: bool = False, height: int = 320, key_suffix: str = "", show_type_filters: bool = True, show_sort_controls: bool = True):
    """Renders a configurable, sortable, and filterable DataFrame."""
    if df is None or df.empty:
        st.info("Chưa có dữ liệu."); return
        
    df = df.drop(columns=[c for c in df.columns if c in METADATA_COLUMNS_TO_DROP], errors="ignore").copy()
    
    # Type filters (Expense/Income)
    if show_type_filters and ("Loại" in df.columns):
        filter_key = f"filter_{key_suffix}"
        if filter_key not in st.session_state: st.session_state[filter_key] = "Tất cả"
        
        b_all, b_exp, b_inc = st.columns([1, 1, 1])
        if b_all.button("⚪ Tất cả", key=f"all_{key_suffix}"): st.session_state[filter_key] = "Tất cả"
        if b_exp.button("🔴 Chỉ Chi tiêu", key=f"exp_{key_suffix}"): st.session_state[filter_key] = "Chi tiêu"
        if b_inc.button("🟢 Chỉ Thu nhập", key=f"inc_{key_suffix}"): st.session_state[filter_key] = "Thu nhập"
        
        selected_filter = st.session_state[filter_key]
        if selected_filter != "Tất cả":
            df = df[df["Loại"].astype(str).str.contains(selected_filter, case=False, na=False)]

    # Display without sort controls
    if not show_sort_controls:
        df.insert(0, "STT", range(1, len(df) + 1))
        st.dataframe(df, use_container_width=True, height=height, hide_index=True); return

    sortable_cols = df.columns.tolist()
    if not sortable_cols:
        st.dataframe(df, use_container_width=True, height=height, hide_index=True); return
        
    # Sort controls
    c1, c2, _ = st.columns([1.6, 1.2, 2])
    idx = sortable_cols.index(default_sort_col) if default_sort_col in sortable_cols else 0
    sort_col = c1.selectbox("Sắp xếp theo", sortable_cols, index=idx, key=f"sort_{key_suffix}")
    sort_type = _detect_column_sort_type(df, sort_col)

    if sort_type == "type":
        st.caption("Thứ tự 'Loại' cố định: Chi tiêu → Thu nhập")
        ascending = True
    else:
        if sort_type == "time": labels = ["Mới nhất", "Cũ nhất"]
        elif sort_type == "number": labels = ["Cao → Thấp", "Thấp → Cao"]
        else: labels = ["A → Z", "Z → A"]
        
        direction_pick = c2.radio("Thứ tự", labels, horizontal=True, key=f"order_{key_suffix}")
        ascending = (labels.index(direction_pick) == 1)

    df_sorted = sort_dataframe(df, sort_col, ascending)
    df_sorted.insert(0, "STT", range(1, len(df_sorted) + 1))
    st.dataframe(df_sorted, use_container_width=True, height=height, hide_index=True)

# ---------- KPI Rendering ----------
def _get_period_summary(user_id:int, start_date:dt.date, end_date:dt.date) -> Tuple[float,float,float]:
    """Calculates total income, expense, and net for a given period."""
    row = fetch_one("""
        SELECT COALESCE(SUM(CASE WHEN type='income' THEN amount END),0) AS income,
               COALESCE(SUM(CASE WHEN type='expense' THEN amount END),0) AS expense
        FROM transactions WHERE user_id=? AND date(occurred_at) BETWEEN date(?) AND date(?)""",
        (user_id, str(start_date), str(end_date)))
    income, expense = float(row["income"] or 0), float(row["expense"] or 0)
    return income, expense, (income - expense)

def _get_previous_period(start_date:dt.date, end_date:dt.date, mode:str) -> Tuple[dt.date,dt.date]:
    """Calculates the date range for the period immediately preceding the given one."""
    if mode == "day":
        span = (end_date - start_date).days + 1
        return start_date - dt.timedelta(days=span), end_date - dt.timedelta(days=span)
    if mode == "week":
        return start_date - dt.timedelta(days=7), end_date - dt.timedelta(days=7)
    if mode == "month":
        first_day_current_month = start_date.replace(day=1)
        last_day_prev_month = first_day_current_month - dt.timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        return first_day_prev_month, last_day_prev_month
    # mode == "year"
    return dt.date(start_date.year - 1, 1, 1), dt.date(start_date.year - 1, 12, 31)

def render_kpi_metrics(user_id: int, start_date: dt.date, end_date: dt.date, mode: str):
    """Renders the main KPI metrics with comparison to the previous period."""
    income, expense, net = _get_period_summary(user_id, start_date, end_date)
    
    prev_start, prev_end = _get_previous_period(start_date, end_date, mode)
    prev_income, prev_expense, prev_net = _get_period_summary(user_id, prev_start, prev_end)

    def format_delta(current, previous):
        delta = current - previous
        arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
        return f"{arrow} {format_vnd(abs(delta))} VND so với kỳ trước"

    c1, c2, c3 = st.columns(3)
    c1.metric(label="Tổng thu", value=f"{format_vnd(income)} VND", delta=format_delta(income, prev_income), delta_color="normal")
    c2.metric(label="Tổng chi", value=f"{format_vnd(expense)} VND", delta=format_delta(expense, prev_expense), delta_color="inverse")
    c3.metric(label="Chênh lệch (thu - chi)", value=f"{format_vnd(net)} VND", delta=format_delta(net, prev_net), delta_color="normal")


# ---------- Chart Rendering ----------
def render_budget_progress_chart(df, title: str = "Tiến độ hạn mức", green_threshold: float = 70.0, yellow_threshold: float = 100.0):
    """Renders a horizontal bar chart for budget progress."""
    if df is None or df.empty:
        st.info("Chưa có hạn mức."); return
        
    data = df.copy()
    data["%"] = pd.to_numeric(data["%"], errors="coerce").fillna(0.0)
    
    domain_max = int(math.ceil(max(100.0, float(data["%"].max())) / 10.0) * 10)

    color_condition = f"datum['%'] < {green_threshold} ? '#22c55e' : (datum['%'] < {yellow_threshold} ? '#f59e0b' : '#ef4444')"
    
    base = alt.Chart(data).encode(
        y=alt.Y("Danh mục:N", sort='-x', title=None)
    ).transform_calculate(color=color_condition)

    bars = base.mark_bar(size=22).encode(
        x=alt.X("%:Q", title="Đã dùng (%)", scale=alt.Scale(domain=[0, domain_max], nice=False)),
        color=alt.Color("color:N", legend=None, scale=None),
        tooltip=[alt.Tooltip("Danh mục:N"), alt.Tooltip("%:Q", format=".0f", title="Đã dùng (%)"),
                 alt.Tooltip("Đã dùng:Q", format=",.0f"), alt.Tooltip("Hạn mức:Q", format=",.0f")])

    text_labels = base.mark_text(align="left", dx=4).encode(
        x=alt.X("%:Q"),
        text=alt.Text("%:Q", format=".0f"))
        
    if title: st.markdown(f"#### {title}")
    st.altair_chart((bars + text_labels).properties(height=max(220, 28 * len(data))), use_container_width=True)

def render_spending_chart(user_id, start_date, end_date, mode, chart_type: str, db_query_func):
    """Renders a bar or line chart for spending over time."""
    df, label, x_axis_type = db_query_func(user_id, start_date, end_date, mode)

    if mode == "day":
        # (Logic lấp đầy ngày 0 đồng)
        all_days_in_range = pd.date_range(start_date, end_date)
        all_days_df = pd.DataFrame(all_days_in_range, columns=['date_obj'])
        all_days_df[label] = all_days_df['date_obj'].dt.strftime('%Y-%m-%d')
        if df.empty:
            df = all_days_df[[label]]
            df['Chi_tieu'] = 0.0
        else:
            df_merged = pd.merge(all_days_df[[label]], df, on=label, how='left')
            df_merged['Chi_tieu'] = df_merged['Chi_tieu'].fillna(0.0)
            df = df_merged
    
    # Bỏ logic "elif mode == 'week'"

    if df.empty:
        st.info("Chưa có dữ liệu."); return

    base_chart = alt.Chart(df)
    mark = base_chart.mark_bar(color=COLOR_EXPENSE) if chart_type == "Cột" else base_chart.mark_line(point=True, color=COLOR_EXPENSE)
    
    chart = mark.encode(
        x=alt.X(f"{label}:{x_axis_type}", title=label), # Bỏ sort=None
        y=alt.Y("Chi_tieu:Q", title="Chi tiêu (VND)"),
        tooltip=[label, alt.Tooltip("Chi_tieu:Q", format=",.0f", title="Chi tiêu")]
    ).properties(height=260)
    st.altair_chart(chart, use_container_width=True)

def render_pie_chart_by_category(user_id, start_date, end_date, group_by_parent, db_get_df_func):
    """Renders a pie chart of expenses by category."""
    if group_by_parent:
        query = """
            SELECT COALESCE(cp.name, c.name) AS category_name, SUM(t.amount) AS total_expense
            FROM transactions t
            LEFT JOIN categories c ON c.id=t.category_id LEFT JOIN categories cp ON cp.id=c.parent_id
            WHERE t.user_id=? AND t.type='expense' AND date(t.occurred_at) BETWEEN date(?) AND date(?)
            GROUP BY category_name HAVING total_expense > 0 ORDER BY total_expense DESC
        """
    else:
        query = """
            SELECT COALESCE(c.name,'(Không danh mục)') AS category_name, SUM(t.amount) AS total_expense
            FROM transactions t LEFT JOIN categories c ON c.id=t.category_id
            WHERE t.user_id=? AND t.type='expense' AND date(t.occurred_at) BETWEEN date(?) AND date(?)
            GROUP BY category_name HAVING total_expense > 0 ORDER BY total_expense DESC
        """
    df = db_get_df_func(query, (user_id, str(start_date), str(end_date)))
    if df.empty:
        st.info("Chưa có chi tiêu theo danh mục."); return
        
    # <<< SỬA 1: Thêm dòng này để tính toán % >>>
    df['percent'] = (df['total_expense'] / df['total_expense'].sum())

    chart = alt.Chart(df).mark_arc(outerRadius=120).encode( # Thêm outerRadius=120 để biểu đồ lớn hơn
        theta=alt.Theta(field="total_expense", type="quantitative"),
        color=alt.Color(field="category_name", type="nominal", legend=None, scale=alt.Scale(scheme="tableau10")),
        
        # <<< SỬA 2: Thêm "percent" vào tooltip >>>
        tooltip=[
            alt.Tooltip("category_name", title="Danh mục"), 
            alt.Tooltip("total_expense:Q", format=",.0f", title="Chi tiêu"),
            alt.Tooltip("percent:Q", format=".1%", title="Tỷ lệ") # <-- Dòng mới
        ]
    ).properties(height=260)
    st.altair_chart(chart, use_container_width=True)