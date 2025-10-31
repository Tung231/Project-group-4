import streamlit as st
import sys
sys.path.append(".")

import database as db
from utils import build_category_tree, show_toast, show_ephemeral_notice

def render_category_management_tab(user_id, tab, category_type_display, category_type):
    with tab:
        parents = build_category_tree(user_id, category_type, db.get_df)
        if not parents:
            st.info("Chưa có danh mục.")
        else:
            for parent in parents:
                with st.expander(f"🏷️ {parent['name']}"):
                    children = parent.get("children", [])
                    if not children:
                        st.caption("— (Chưa có danh mục con)")
                    else:
                        for child in children:
                            st.markdown(f"- 🏷️ **{child['name']}**")

        st.markdown("##### Thêm danh mục")
        category_name = st.text_input(f"Tên danh mục ({category_type_display})", key=f"cat_name_{category_type}")
        
        all_parents_df = db.get_df("SELECT id, name FROM categories WHERE user_id=? AND type=? AND parent_id IS NULL ORDER BY name", (user_id, category_type))
        parent_options = ["(Không)"] + all_parents_df["name"].tolist()
        parent_pick = st.selectbox("Thuộc danh mục cha (tuỳ chọn)", parent_options, key=f"cat_parent_{category_type}")
        parent_id = None
        if parent_pick != "(Không)":
            parent_id = int(all_parents_df.loc[all_parents_df["name"]==parent_pick, "id"].iloc[0])

        add_col, del_col = st.columns([1,1])
        if add_col.button("Thêm danh mục", key=f"btn_add_cat_{category_type}"):
            if category_name.strip():
                db.add_category(user_id, category_name.strip(), category_type, parent_id)
                show_toast("Đã thêm danh mục!")
                st.rerun()
            else:
                show_ephemeral_notice("Tên danh mục không được để trống.", "error"); st.rerun()

        with del_col.popover("🗑️ Xoá danh mục", use_container_width=True):
            all_cats_df = db.get_df("SELECT id, name FROM categories WHERE user_id=? AND type=? ORDER BY name",(user_id, category_type))
            if all_cats_df.empty:
                st.caption("Chưa có danh mục để xoá.")
            else:
                to_delete_name = st.selectbox("Chọn danh mục", all_cats_df["name"].tolist(), key=f"del_{category_type}")
                to_delete_id = int(all_cats_df.loc[all_cats_df["name"]==to_delete_name, "id"].iloc[0])
                st.caption("• Xoá sẽ: xoá budgets liên quan, bỏ liên kết giao dịch và các danh mục con.")
                if st.button("Xác nhận xoá", type="secondary", key=f"do_del_{category_type}"):
                    db.delete_category(user_id, to_delete_id)
                    show_toast("Đã xoá danh mục.")
                    st.rerun()

def render_page(user_id):
    st.title("🏷️ Danh mục")
    expense_tab, income_tab = st.tabs(["Chi tiêu", "Thu nhập"])
    render_category_management_tab(user_id, expense_tab, "Chi tiêu", "expense")
    render_category_management_tab(user_id, income_tab, "Thu nhập", "income")