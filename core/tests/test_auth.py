import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.models import SocialAccount, SocialLogin

from core.adapters import SocialAccountAdapter
from core.auth import has_valid_google_oauth_env


@pytest.mark.django_db
def test_has_valid_google_oauth_env_considera_settings(settings, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    settings.GOOGLE_CLIENT_ID = "client-id-valido"
    settings.GOOGLE_CLIENT_SECRET = "client-secret-valido"

    assert has_valid_google_oauth_env() is True


# ---- Domain validation tests ----


def _make_request():
    """Cria um request com session e messages middleware."""
    rf = RequestFactory()
    request = rf.get("/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    return request


def _make_sociallogin(email):
    """Cria um SocialLogin com o email especificado."""
    sociallogin = SocialLogin()
    sociallogin.account = SocialAccount()
    sociallogin.account.extra_data = {"email": email}
    sociallogin.user = type("FakeUser", (), {"email": email, "pk": None})()
    return sociallogin


@pytest.mark.django_db
def test_pre_social_login_bloqueia_dominio_externo(settings):
    """E-mail fora do domínio permitido deve ser bloqueado com redirect."""
    settings.GOOGLE_ALLOWED_DOMAINS = ["escola.pr.gov.br"]

    request = _make_request()
    sociallogin = _make_sociallogin("aluno@gmail.com")

    adapter = SocialAccountAdapter()

    with pytest.raises(ImmediateHttpResponse) as excinfo:
        adapter.pre_social_login(request, sociallogin)

    response = excinfo.value.response
    assert response.status_code == 302


@pytest.mark.django_db
def test_pre_social_login_aceita_dominio_permitido(settings):
    """E-mail do domínio permitido deve passar sem erros."""
    settings.GOOGLE_ALLOWED_DOMAINS = ["escola.pr.gov.br"]

    request = _make_request()
    sociallogin = _make_sociallogin("aluno@escola.pr.gov.br")

    adapter = SocialAccountAdapter()

    # Não deve levantar ImmediateHttpResponse
    try:
        adapter.pre_social_login(request, sociallogin)
    except ImmediateHttpResponse:
        pytest.fail("pre_social_login levantou ImmediateHttpResponse para domínio permitido")


@pytest.mark.django_db
def test_pre_social_login_multiplos_dominios(settings):
    """Múltiplos domínios configurados devem ser aceitos."""
    settings.GOOGLE_ALLOWED_DOMAINS = ["escola.pr.gov.br", "seed.pr.gov.br"]

    adapter = SocialAccountAdapter()

    for dominio in ["escola.pr.gov.br", "seed.pr.gov.br"]:
        request = _make_request()
        sociallogin = _make_sociallogin(f"aluno@{dominio}")
        try:
            adapter.pre_social_login(request, sociallogin)
        except ImmediateHttpResponse:
            pytest.fail(f"pre_social_login bloqueou domínio válido: @{dominio}")


@pytest.mark.django_db
def test_pre_social_login_bloqueia_sem_email(settings):
    """Login sem email deve ser bloqueado."""
    settings.GOOGLE_ALLOWED_DOMAINS = ["escola.pr.gov.br"]

    request = _make_request()
    sociallogin = _make_sociallogin("")
    sociallogin.account.extra_data = {}

    adapter = SocialAccountAdapter()

    with pytest.raises(ImmediateHttpResponse) as excinfo:
        adapter.pre_social_login(request, sociallogin)

    response = excinfo.value.response
    assert response.status_code == 302


@pytest.mark.django_db
def test_pre_social_login_mensagem_erro_menciona_dominio(settings):
    """Mensagem de erro deve mencionar o domínio permitido."""
    settings.GOOGLE_ALLOWED_DOMAINS = ["escola.pr.gov.br"]

    request = _make_request()
    sociallogin = _make_sociallogin("aluno@gmail.com")

    adapter = SocialAccountAdapter()

    with pytest.raises(ImmediateHttpResponse):
        adapter.pre_social_login(request, sociallogin)

    # Verificar que a mensagem foi adicionada
    messages = list(request._messages)
    assert len(messages) == 1
    assert "escola.pr.gov.br" in str(messages[0])
    assert "gmail.com" in str(messages[0])

