from django.urls import path

from .views import ConfirmUserAPIView, LoginAPIView, RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='user-login'),
    path('confirm/', ConfirmUserAPIView.as_view(), name='user-confirm'),
]
