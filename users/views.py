from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    ConfirmUserSerializer,
    CustomTokenObtainPairSerializer,
    DelayTaskSerializer,
    EmailTaskSerializer,
    LoginSerializer,
    RegisterSerializer,
    build_jwt_tokens_for_user,
)
from .tasks import create_delay_demo_log, send_demo_email_task


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        jwt_tokens = build_jwt_tokens_for_user(user)
        return Response(
            {
                'token': token.key,
                'refresh': jwt_tokens['refresh'],
                'access': jwt_tokens['access'],
                'user_id': user.id,
                'email': user.email,
                'birthdate': user.birthdate.isoformat() if user.birthdate else None,
            },
            status=status.HTTP_200_OK,
        )


class ConfirmUserAPIView(generics.GenericAPIView):
    serializer_class = ConfirmUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        jwt_tokens = build_jwt_tokens_for_user(user)
        return Response(
            {
                'message': 'User confirmed successfully.',
                'user_id': user.id,
                'email': user.email,
                'token': token.key,
                'refresh': jwt_tokens['refresh'],
                'access': jwt_tokens['access'],
            },
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class DelayDemoTaskAPIView(generics.GenericAPIView):
    serializer_class = DelayTaskSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        async_result = create_delay_demo_log.delay(serializer.validated_data.get('note', ''))
        return Response(
            {
                'message': 'Delay task started successfully.',
                'task_id': async_result.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class SendEmailTaskAPIView(generics.GenericAPIView):
    serializer_class = EmailTaskSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        async_result = send_demo_email_task.delay(
            serializer.validated_data['recipient_email'],
            serializer.validated_data.get('subject', ''),
            serializer.validated_data.get('body', ''),
        )
        return Response(
            {
                'message': 'SMTP task started successfully.',
                'task_id': async_result.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
