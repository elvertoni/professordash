import os

from django.db.utils import OperationalError, ProgrammingError


_GOOGLE_OAUTH_PLACEHOLDERS = {
    "",
    "COLOQUE_SEU_GOOGLE_CLIENT_ID",
    "COLOQUE_SEU_GOOGLE_CLIENT_SECRET",
    "your-google-client-id",
    "your-google-client-secret",
}


def _is_valid_google_oauth_value(value: str) -> bool:
    return value.strip() not in _GOOGLE_OAUTH_PLACEHOLDERS


def has_valid_google_oauth_env() -> bool:
    return _is_valid_google_oauth_value(
        os.environ.get("GOOGLE_CLIENT_ID", "")
    ) and _is_valid_google_oauth_value(os.environ.get("GOOGLE_CLIENT_SECRET", ""))


def is_google_oauth_configured() -> bool:
    if has_valid_google_oauth_env():
        return True

    try:
        from allauth.socialaccount.models import SocialApp

        return SocialApp.objects.filter(provider="google").exists()
    except (OperationalError, ProgrammingError):
        return False
