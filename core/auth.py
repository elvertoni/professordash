import os

from django.db.utils import OperationalError, ProgrammingError


def is_google_oauth_configured() -> bool:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        return True

    try:
        from allauth.socialaccount.models import SocialApp

        return SocialApp.objects.filter(provider="google").exists()
    except (OperationalError, ProgrammingError):
        return False
