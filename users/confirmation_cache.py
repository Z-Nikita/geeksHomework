from django.core.cache import cache

CONFIRMATION_CODE_TTL_SECONDS = 5 * 60


def build_confirmation_code_key(user_id: int) -> str:
    return f"confirmation_code:{user_id}"


def set_confirmation_code(user_id: int, code: str) -> None:
    cache.set(build_confirmation_code_key(user_id), code, timeout=CONFIRMATION_CODE_TTL_SECONDS)


def get_confirmation_code(user_id: int):
    return cache.get(build_confirmation_code_key(user_id))


def delete_confirmation_code(user_id: int) -> None:
    cache.delete(build_confirmation_code_key(user_id))
