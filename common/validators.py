from datetime import date

from rest_framework.exceptions import ValidationError


def validate_age_for_product_creation(request):
    token = getattr(request, 'auth', None)
    birthdate_value = None

    if token is not None and hasattr(token, 'get'):
        birthdate_value = token.get('birthdate')

    if not birthdate_value:
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

    try:
        birthdate = date.fromisoformat(str(birthdate_value))
    except (TypeError, ValueError):
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError('Вам должно быть 18 лет, чтобы создать продукт.')
