from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import ConfirmationCode, generate_confirmation_code

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Username cannot be empty.')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('User with this username already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        user = User.objects.create_user(username=username, password=password, is_active=False)
        code = generate_confirmation_code()
        while ConfirmationCode.objects.filter(code=code).exists():
            code = generate_confirmation_code()
        ConfirmationCode.objects.create(user=user, code=code)
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'is_active': instance.is_active,
            'confirmation_code': instance.confirmation_code.code,
            'message': 'User registered successfully. Confirm the account with the 6-digit code.',
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password')
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid username or password.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Invalid username or password.'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User is not confirmed.'})

        attrs['user'] = user
        return attrs


class ConfirmUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        code = attrs.get('code', '').strip()
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'username': 'User not found.'})

        if user.is_active:
            raise serializers.ValidationError({'detail': 'User is already confirmed.'})

        try:
            confirmation = user.confirmation_code
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError({'code': 'Confirmation code not found.'})
        if confirmation.code != code:
            raise serializers.ValidationError({'code': 'Invalid confirmation code.'})
        attrs['user'] = user
        attrs['confirmation'] = confirmation
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        confirmation = self.validated_data['confirmation']
        user.is_active = True
        user.save(update_fields=['is_active'])
        confirmation.delete()
        token, _ = Token.objects.get_or_create(user=user)
        return user, token
