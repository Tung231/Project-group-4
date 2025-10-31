import streamlit as st
import sys
sys.path.append(".")

def render_page(user_id):
    st.title("ℹ️ Giới thiệu")
    st.markdown("""
    **Expense Manager** là ứng dụng quản lý thu chi cá nhân viết bằng **Python + Streamlit**, lưu trữ bằng **SQLite**.

    ### Tính năng nổi bật
    - **Theo dõi thu/chi** theo **ngày–tuần–tháng–năm** với **KPI** và so sánh **kỳ trước**
    - **Biểu đồ** chi tiêu dạng **Cột/Đường**; **Pie chart** theo danh mục (mặc định **gộp theo danh mục cha**)
    - **Danh mục cha–con** (tạo/sửa/xoá); thêm giao dịch theo **cha** hoặc **con**
    - **Hạn mức (Ngân sách) theo danh mục**: đặt mục tiêu, xem tiến độ, cảnh báo vượt mức
    - **Báo cáo**: Top danh mục chi, danh sách giao dịch, **xuất CSV/XLSX**
    - **Quản lý ví/Tài khoản** và tính **số dư hiện tại**
    - **Xoá an toàn**: giao dịch, hạn mức, danh mục (tự xử lý ràng buộc liên quan)

    > Mặc định mọi thống kê đều **gộp theo danhMục cha**; bạn có thể tắt để xem theo danh mục con khi cần.
    """)