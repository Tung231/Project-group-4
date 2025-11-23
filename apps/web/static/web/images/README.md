# Hướng dẫn thêm ảnh background

Để sử dụng ảnh background cho phần nút đăng nhập/đăng ký trên landing page:

1. Đặt ảnh của bạn vào thư mục này với tên: `background-gradient.jpg`
2. Hoặc bạn có thể đổi tên ảnh và cập nhật đường dẫn trong file `landingpage.html`

Đường dẫn ảnh trong code: `/static/web/images/background-gradient.jpg`

**Lưu ý:** Sau khi thêm ảnh, bạn cần chạy lệnh sau để Django collect static files:
```bash
python manage.py collectstatic --noinput
```

Hoặc trong development mode, Django sẽ tự động serve static files từ thư mục `static/`.

