from django.urls import path
from .views import (
    ApiGuideView, RegisterView, BasicProfileView, SessionProfileView,
    TokenLoginView, TokenProfileView, TokenLogoutView, JWTProfileView,
)
urlpatterns = [
    path('', ApiGuideView.as_view(), name='api-guide'),
    path('register/', RegisterView.as_view(), name='register'),
    path('basic/me/', BasicProfileView.as_view(), name='basic-me'),
    path('session/me/', SessionProfileView.as_view(), name='session-me'),
    path('token/login/', TokenLoginView.as_view(), name='token-login'),
    path('token/me/', TokenProfileView.as_view(), name='token-me'),
    path('token/logout/', TokenLogoutView.as_view(), name='token-logout'),
    path('jwt/me/', JWTProfileView.as_view(), name='jwt-me'),
]
