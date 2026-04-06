import requests
from django.conf import settings
from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import CustomTokenObtainPairSerializer, GoogleAuthSerializer


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=GoogleAuthSerializer,
        responses={200: "OK", 400: "Bad Request"},
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        token_response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )

        try:
            token_data = token_response.json()
        except ValueError:
            token_data = {}

        if token_response.status_code != 200:
            return Response(
                {
                    "detail": "Failed to get token from Google.",
                    "google_response": token_data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_data.get("access_token")
        if not access_token:
            return Response(
                {"detail": "Google did not return access_token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        userinfo_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )

        try:
            userinfo = userinfo_response.json()
        except ValueError:
            userinfo = {}

        if userinfo_response.status_code != 200:
            return Response(
                {
                    "detail": "Failed to get user info from Google.",
                    "google_response": userinfo,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = userinfo.get("email")
        given_name = userinfo.get("given_name", "")
        family_name = userinfo.get("family_name", "")

        if not email:
            return Response(
                {"detail": "Google did not return user email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "is_active": True,
                "first_name": given_name,
                "last_name": family_name,
                "registration_source": "google",
            },
        )

        if created:
            user.set_unusable_password()

        user.first_name = given_name or user.first_name
        user.last_name = family_name or user.last_name
        user.is_active = True
        user.registration_source = "google"
        user.save()

        update_last_login(None, user)

        refresh = CustomTokenObtainPairSerializer.get_token(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "last_login": user.last_login,
                    "registration_source": user.registration_source,
                },
            },
            status=status.HTTP_200_OK,
        )