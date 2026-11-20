from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RegisterSerializer, UserSerializer


def home(request):
    return JsonResponse({'project': 'DRF Authentication Lab', 'documentation': '/api/', 'login_page': '/accounts/login/'})


class ApiGuideView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'register': 'POST /api/register/',
            'basic': 'GET /api/basic/me/ (Authorization: Basic base64(username:password))',
            'session': 'GET /api/session/me/ (login: /accounts/login/)',
            'token_login': 'POST /api/token/login/',
            'token_profile': 'GET /api/token/me/ (Authorization: Token <token>)',
            'token_logout': 'POST /api/token/logout/ (Authorization: Token <token>)',
            'jwt_login': 'POST /api/jwt/login/',
            'jwt_refresh': 'POST /api/jwt/refresh/',
            'jwt_profile': 'GET /api/jwt/me/ (Authorization: Bearer <access>)',
            'jwt_logout': 'POST /api/jwt/logout/ (refresh token body)',
            'notes': 'GET/POST /api/notes/ (Bearer JWT)',
        })


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class BasicProfileView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'method': 'Basic', 'user': UserSerializer(request.user).data})


class SessionProfileView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'method': 'Session', 'user': UserSerializer(request.user).data})


class TokenLoginView(ObtainAuthToken):
    # DRF ObtainAuthToken ichida login ma'lumotlari tekshiriladi.
    # Dars uchun bazadagi yagona Token qayta ishlatiladi.
    throttle_classes = [AnonRateThrottle]  # O'quv namunasi uchun oddiy so'rov limiti.

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class TokenProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'method': 'Token', 'user': UserSerializer(request.user).data})


class TokenLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response({'detail': 'Token bekor qilindi.'})


class JWTProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'method': 'JWT', 'user': UserSerializer(request.user).data})
