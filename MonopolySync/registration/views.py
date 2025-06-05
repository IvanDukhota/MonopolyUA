from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
import requests
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail
import random
import string

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data["username"])

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": response.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({"error": "Неправильні дані"}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginRedirectView(APIView):
    def get(self, request):
        client_id = settings.CLIENT_ID
        redirect_uri = settings.REDIRECT_URI
        scope = 'openid email profile'
        response_type = 'code'

        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type={response_type}"
            f"&scope={scope}"
        )
        return redirect(auth_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=400)

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': code,
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'redirect_uri': settings.REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            return Response({'error': 'Failed to get token'}, status=400)

        tokens = token_res.json()
        id_token = tokens.get('id_token')

        user_info = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}").json()
        print(user_info)
        email = user_info.get('email')
        name = user_info.get('name')

        if not email:
            return Response({'error': 'Пошту не знайдено'}, status=400)

        user, _ = User.objects.get_or_create(email=email, defaults={'username': name})
        refresh = RefreshToken.for_user(user)

        redirect_url = f"{settings.CLIENT_URI}/google-success.html?access={refresh.access_token}&refresh={refresh}"
        return redirect(redirect_url)


class ForgotPasswordView(APIView):
    def post(self,request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        new_password = generate_password()

        user.set_password(new_password)
        user.save()
        send_mail(
            subject="Відновлення пароля",
            message=f"Ваш новий пароль: {new_password}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Новий пароль надіслано на вашу пошту"}, status=status.HTTP_200_OK)


def generate_password(length=8):
    required = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*")
    ]
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    remaining = random.choices(all_chars, k=length - 4)
    password = ''.join(random.sample(required + remaining, length))
    return password
