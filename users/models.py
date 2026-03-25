import random

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager


def generate_confirmation_code() -> str:
    return f"{random.randint(0, 999999):06d}"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self) -> str:
        return self.email


class ConfirmationCode(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='confirmation_code',
    )
    code = models.CharField(max_length=6, unique=True, default=generate_confirmation_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_confirmation_code()
        while ConfirmationCode.objects.exclude(pk=self.pk).filter(code=self.code).exists():
            self.code = generate_confirmation_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Confirmation code for {self.user.email}"
