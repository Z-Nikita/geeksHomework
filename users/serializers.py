from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .confirmation_cache import delete_confirmation_code, get_confirmation_code, set_confirmation_code
from .models import generate_confirmation_code

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['birthdate'] = user.birthdate.isoformat() if user.birthdate else None
        return token


def build_jwt_tokens_for_user(user):
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=30)
    birthdate = serializers.DateField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return value

    def validate_phone_number(self, value):
        if value is None:
            return ''
        return value.strip()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        phone_number = validated_data.get('phone_number', '')
        birthdate = validated_data.get('birthdate')
        user = User.objects.create_user(
            email=email,
            password=password,
            phone_number=phone_number or '',
            birthdate=birthdate,
            is_active=False,
        )
        code = generate_confirmation_code()
        set_confirmation_code(user.id, code)
        user._confirmation_code = code
        return user

    def to_representation(self, instance):
        phone_number = instance.phone_number if instance.phone_number else ''
        return {
            'id': instance.id,
            'email': instance.email,
            'phone_number': phone_number,
            'birthdate': instance.birthdate.isoformat() if instance.birthdate else None,
            'is_active': instance.is_active,
            'confirmation_code': getattr(instance, '_confirmation_code', None),
            'message': 'User registered successfully. Confirm the account with the 6-digit code.',
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if user is None:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

        if user is None:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User is not confirmed.'})

        attrs['user'] = user
        return attrs


class ConfirmUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        code = attrs.get('code', '').strip()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User not found.'})

        if user.is_active:
            raise serializers.ValidationError({'detail': 'User is already confirmed.'})

        cached_code = get_confirmation_code(user.id)
        if not cached_code:
            raise serializers.ValidationError({'code': 'Confirmation code not found or expired.'})

        if cached_code != code:
            raise serializers.ValidationError({'code': 'Invalid confirmation code.'})

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.is_active = True
        user.save(update_fields=['is_active'])
        delete_confirmation_code(user.id)
        token, _ = Token.objects.get_or_create(user=user)
        return user, token


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField()