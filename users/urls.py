from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .google_oauth import GoogleLoginAPIView
from .views import ConfirmUserAPIView, CustomTokenObtainPairView, LoginAPIView, RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='user-login'),
    path('confirm/', ConfirmUserAPIView.as_view(), name='user-confirm'),
    path('jwt/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('google-login/', GoogleLoginAPIView.as_view(), name='google-login'),
]
