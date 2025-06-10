# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import CustomUser


User = get_user_model()

# ユーザー登録
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "メールとパスワードは必須です"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "このメールアドレスは既に登録されています"}, status=400)

        user = User.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        return Response({"message": "登録成功！"}, status=status.HTTP_201_CREATED)
    
    
# ログアウト
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "refreshトークンが必要です"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # ← blacklistに登録して無効化

            return Response({"message": "ログアウトしました（トークン無効化）"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ログインユーザーの確認
class CurrentUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        })

# アカウント削除
class DeleteUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "アカウントを削除しました"}, status=status.HTTP_200_OK)