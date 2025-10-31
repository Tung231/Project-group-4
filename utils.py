# ==========================================
# File: utils.py
# Sửa Fix #5: Thông báo 3 giây
# ==========================================
import streamlit as st
import re, unicodedata
import datetime as dt
import pandas as pd

# ---------- Currency / Time Helpers (Không đổi) ----------
def format_vnd(number):
    try: return f"{float(number):,.0f}".replace(",", ".")
    except (ValueError, TypeError): return str(number)

def parse_vnd_string(s):
    if s is None: return 0.0
    digits = re.sub(r"[^\d-]", "", str(s))
    try: return float(digits) if digits else 0.0
    except ValueError: return 0.0

def join_date_time(d: dt.date, t: dt.time) -> str:
    return dt.datetime.combine(d, t.replace(second=0, microsecond=0)).strftime("%Y-%m-%d %H:%M")

def strip_accents_and_lower(s):
    if s is None: return ""
    s = unicodedata.normalize("NFD", str(s))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()

def get_start_date_months_back(end_date: dt.date, months: int) -> dt.date:
    idx = end_date.year * 12 + (end_date.month - 1) - (months - 1)
    year, month = divmod(idx, 12)
    return dt.date(year, month + 1, 1)

def get_year_window(end_date: dt.date, years: int):
    end_year = end_date.year; start_year = end_year - (years - 1)
    return dt.date(start_year, 1, 1), dt.date(end_year, 12, 31)

def get_start_date_weeks_back(end_date: dt.date, weeks: int) -> dt.date:
    return end_date - dt.timedelta(days=7*(weeks-1))


# ---------- UI Notice Helpers (ĐÃ SỬA FIX #5) ----------
def show_ephemeral_notice(message: str, level: str = "success"):
    """Lưu thông báo vào session_state VÀ hiển thị toast 3 giây."""
    # 1. Lưu thông báo để hiển thị vĩnh viễn (st.error, st.success)
    st.session_state["__inline_notice__"] = (message, level)
    
    # 2. (FIX #5) Hiển thị toast 3 giây cho MỌI LOẠI thông báo
    icon = "✅" if level == "success" else ("ℹ️" if level == "info" else "❌")
    try:
        # Dùng icon và message
        st.toast(f"{icon} {message}", duration=3000)
    except Exception:
        try:
            # Fallback nếu phiên bản Streamlit cũ
            st.toast(message, duration=3000)
        except Exception:
            pass # Bỏ qua nếu toast lỗi

def render_ephemeral_notice():
    """Hiển thị thông báo (st.error, st.success) nếu có."""
    notice = st.session_state.pop("__inline_notice__", None)
    if notice:
        message, level = notice
        if level == "error": st.error(message, icon="❌")
        elif level == "info": st.info(message, icon="ℹ️")
        else: st.success(message, icon="✅")

def show_toast(message: str):
    """Alias để gọi một thông báo thành công."""
    # Logic toast đã được chuyển vào show_ephemeral_notice
    show_ephemeral_notice(message, "success")

# ---------- UI Widget Helpers (Không đổi) ----------
def money_input(label: str, key: str, placeholder: str = "VD: 5.000.000"):
    ui_key = f"{key}__ui"
    previous_value = st.session_state.get(ui_key, "")
    cleaned_value = re.sub(r"[^\d-]", "", str(previous_value or ""))
    pretty_value = f"{int(cleaned_value):,}".replace(",", ".") if cleaned_value not in ("", "-",) else previous_value
    input_value = st.text_input(label, value=pretty_value, key=ui_key, placeholder=placeholder)
    return parse_vnd_string(input_value)

# ---------- Data Processing Helpers (Không đổi) ----------
def format_transactions_df_for_display(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty: return df
    column_map = {
        "id": "ID", "occurred_at": "Thời điểm", "type": "Loại", "amount": "Số tiền",
        "currency": "Tiền tệ", "account": "Ví / Tài khoản", "category": "Danh mục",
        "notes": "Ghi chú", "tags": "Thẻ", "merchant": "Nơi chi tiêu"
    }
    df_display = df.rename(columns={k:v for k,v in column_map.items() if k in df.columns}).copy()
    if "Loại" in df_display.columns:
        df_display["Loại"] = df_display["Loại"].map({"expense":"Chi tiêu","income":"Thu nhập"}).fillna(df_display["Loại"])
    if "Số tiền" in df_display.columns:
        df_display["Số tiền"] = df_display["Số tiền"].map(format_vnd)
    return df_display

def build_category_tree(user_id:int, category_type:str, db_get_df_func):
    df = db_get_df_func("SELECT id,name,parent_id FROM categories WHERE user_id=? AND type=? ORDER BY name",(user_id, category_type))
    by_parent = {}
    for _, row in df.iterrows():
        pid = int(row["parent_id"]) if pd.notna(row["parent_id"]) else None
        by_parent.setdefault(pid, []).append({"id": int(row["id"]), "name": row["name"]})
    parents = by_parent.get(None, [])
    for p in parents:
        p["children"] = sorted(by_parent.get(p["id"], []), key=lambda x: strip_accents_and_lower(x["name"]))
    return parents

# ---------- Constants (Không đổi) ----------
COLOR_INCOME = "#2ecc71"
COLOR_EXPENSE = "#ff6b6b"
COLOR_NET = "#06b6d4"
METADATA_COLUMNS_TO_DROP = {"id", "user_id", "parent_id", "ID"}