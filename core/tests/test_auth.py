import pytest

from core.auth import has_valid_google_oauth_env


@pytest.mark.django_db
def test_has_valid_google_oauth_env_considera_settings(settings, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    settings.GOOGLE_CLIENT_ID = "client-id-valido"
    settings.GOOGLE_CLIENT_SECRET = "client-secret-valido"

    assert has_valid_google_oauth_env() is True
