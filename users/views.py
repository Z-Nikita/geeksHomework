from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConfirmUserSerializer, LoginSerializer, RegisterSerializer


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
            },
            status=status.HTTP_200_OK,
        )


class ConfirmUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ConfirmUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        return Response(
            {
                'message': 'User confirmed successfully.',
                'user_id': user.id,
                'username': user.username,
                'token': token.key,
            },
            status=status.HTTP_200_OK,
        )
