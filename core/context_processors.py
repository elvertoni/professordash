from .auth import is_google_oauth_configured


def auth_flags(request):
    return {"google_oauth_configured": is_google_oauth_configured()}
