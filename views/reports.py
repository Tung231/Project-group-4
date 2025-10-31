import streamlit as st
import datetime as dt
import pandas as pd
import altair as alt
import io
import sys
sys.path.append(".")

import database as db
from utils import format_transactions_df_for_display
from ui_components import render_table

def render_page(user_id):
    st.title("📈 Báo cáo")

    today = dt.date.today()
    default_start = st.session_state.get("filter_start", today.replace(day=1))
    default_end = st.session_state.get("filter_end", today)
    date_range = st.date_input("Theo ngày", value=(default_start, default_end))

    start_date, end_date = date_range if isinstance(date_range, (list, tuple)) and len(date_range) == 2 else (default_start, default_end)
    st.session_state.filter_start, st.session_state.filter_end = start_date, end_date

    st.markdown("#### Top danh mục chi")
    group_by_parent = st.toggle("Gộp theo danh mục cha", value=True, key="rep_group_parent")
    if group_by_parent:
        query = """SELECT COALESCE(cp.name, c.name) AS category_name, SUM(t.amount) AS total_expense
                 FROM transactions t
                 LEFT JOIN categories c ON c.id=t.category_id LEFT JOIN categories cp ON cp.id=c.parent_id
                 WHERE t.user_id=? AND t.type='expense' AND date(t.occurred_at) BETWEEN date(?) AND date(?)
                 GROUP BY category_name HAVING total_expense>0 ORDER BY total_expense DESC LIMIT 10"""
    else:
        query = """SELECT COALESCE(c.name,'(Không danh mục)') AS category_name, SUM(t.amount) AS total_expense
                 FROM transactions t LEFT JOIN categories c ON c.id=t.category_id
                 WHERE t.user_id=? AND t.type='expense' AND date(t.occurred_at) BETWEEN date(?) AND date(?)
                 GROUP BY category_name HAVING total_expense>0 ORDER BY total_expense DESC LIMIT 10"""
    top_df = db.get_df(query, (user_id, str(start_date), str(end_date)))

    if top_df.empty:
        st.info("Chưa có dữ liệu chi tiêu trong khoảng thời gian này.")
    else:
        chart = alt.Chart(top_df).mark_bar().encode(
            x=alt.X("total_expense:Q", title="Chi tiêu (VND)"),
            y=alt.Y("category_name:N", sort='-x', title="Danh mục"),
            color=alt.Color("category_name:N", legend=None, scale=alt.Scale(scheme="tableau10")),
            tooltip=[alt.Tooltip("category_name:N", title="Danh mục"), alt.Tooltip("total_expense:Q", format=",.0f", title="Chi tiêu")]
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

    st.markdown("#### 📊 Danh sách giao dịch")
    raw_df = db.get_transactions(user_id, start_date, end_date)
    display_df = format_transactions_df_for_display(raw_df)
    if display_df is not None and not display_df.empty and "Loại" in display_df.columns:
        display_df["Loại"] = display_df["Loại"].map({"Thu nhập":"🟢 Thu nhập", "Chi tiêu":"🔴 Chi tiêu"}).fillna(display_df["Loại"])
    render_table(display_df, default_sort_col="Thời điểm", default_asc=False, height=380, key_suffix="report_tx")

    st.divider()
    st.markdown("#### 📥 Xuất dữ liệu")
    if raw_df is None or raw_df.empty:
        st.caption("Không có dữ liệu để xuất.")
    else:
        export_df = raw_df.rename(columns={
            "occurred_at":"Ngày giao dịch", "account":"Ví / Tài khoản", "category":"Danh mục",
            "amount":"Số tiền (VND)", "currency":"Tiền tệ", "notes":"Ghi chú",
            "tags":"Thẻ", "merchant":"Nơi chi tiêu"
        })
        column_order = ["Ngày giao dịch","Ví / Tài khoản","Danh mục","Số tiền (VND)","Tiền tệ","Ghi chú","Thẻ","Nơi chi tiêu"]
        export_df = export_df[[c for c in column_order if c in export_df.columns]]

        csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Tải transactions.csv", csv_bytes, file_name="transactions.csv", mime="text/csv")

        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, index=False, sheet_name="transactions")
            workbook, worksheet = writer.book, writer.sheets["transactions"]
            header_format = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "bg_color": "#EEEEEE", "border": 1})
            money_format = workbook.add_format({"num_format": "#,##0", "align": "right"})
            datetime_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm", "align": "center"})
            for i, col in enumerate(export_df.columns):
                worksheet.write(0, i, col, header_format)
                width = max(len(col) + 2, export_df[col].astype(str).str.len().max() + 2)
                if "Số tiền" in col: worksheet.set_column(i, i, width, money_format)
                elif "Ngày giao dịch" in col: worksheet.set_column(i, i, width, datetime_format)
                else: worksheet.set_column(i, i, width)
            worksheet.freeze_panes(1, 0)
        st.download_button("Tải transactions.xlsx", output_buffer.getvalue(), file_name="transactions.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")