import random

from django.conf import settings
from django.db import models


def generate_confirmation_code() -> str:
    return f"{random.randint(0, 999999):06d}"


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
        return f"Confirmation code for {self.user.username}"
