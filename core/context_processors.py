import os

from django.db.utils import OperationalError, ProgrammingError


def auth_flags(request):
    google_oauth_configured = bool(
        os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        and os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    )

    if not google_oauth_configured:
        try:
            from allauth.socialaccount.models import SocialApp

            google_oauth_configured = SocialApp.objects.filter(provider="google").exists()
        except (OperationalError, ProgrammingError):
            google_oauth_configured = False

    return {"google_oauth_configured": google_oauth_configured}
