# Xử lí đăng kí & đăng nhập, trả về Token

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserRegistrationSerializer

# API Đăng ký
class RegisterView(generics.CreateAPIView):
    """Frontend gửi:
    {
        "username": "testuser",
        "email": "a@b.com",
        "password": "123456",
        "display_name": "Nguyễn Văn A"
    }
    """
    permission_classes = [permissions.AllowAny] # Ai cũng gọi được, không cần log in
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Nếu đúng -> vào create() trong serializer: 
                                                  # tạo user trong database, nếu sai -> trả lỗi 400
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user) # Nếu user mới -> tạo token mới
                                                          # Nếu không -> lấy token cũ
        return Response({
            "user_id": user.pk,
            "token": token.key,
            "message": "User created successfully"
        }, status=status.HTTP_201_CREATED)
    """Response trả về:
    {
        "token": "...",
        "user_id": 5,
        "username": "testuser",
        "display_name": "Nguyễn Văn A"
    }"""

# API Đăng nhập (Custom lại để trả về thêm user_id, display_name)
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'display_name': user.display_name
        })