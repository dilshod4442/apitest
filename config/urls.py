from django.contrib import admin
from django.contrib.auth import views as django_auth_views
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView
)
from accounts.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/login/', django_auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', django_auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include('accounts.urls')),
    path('api/notes/', include('notes.urls')),
    path('api/jwt/login/', TokenObtainPairView.as_view(), name='jwt-login'),
    path('api/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('api/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    path('api/jwt/logout/', TokenBlacklistView.as_view(), name='jwt-logout'),
]
