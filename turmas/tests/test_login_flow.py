import pytest
from django.urls import reverse
from urllib.parse import urlencode


@pytest.mark.django_db
def test_portal_cta_de_login_dispara_oauth(client, turma):
    url = reverse("turmas:portal", kwargs={"token": turma.token_publico})
    response = client.get(url)
    entrar_url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    assert response.status_code == 200
    assert f"{entrar_url}?oauth=1" in response.content.decode()


@pytest.mark.django_db
def test_entrar_com_oauth_redireciona_para_inicio_google(client, turma, settings):
    settings.GOOGLE_CLIENT_ID = "client-id-valido"
    settings.GOOGLE_CLIENT_SECRET = "client-secret-valido"
    url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    response = client.get(f"{url}?oauth=1")

    expected_next = reverse(
        "turmas:portal_minha_area", kwargs={"token": turma.token_publico}
    )
    assert response.status_code == 302
    assert response.url == (
        f"{reverse('google_oauth_start')}?{urlencode({'next': expected_next})}"
    )
    assert client.session["turma_token"] == str(turma.token_publico)


@pytest.mark.django_db
def test_entrar_descarta_next_externo(client, turma, settings):
    settings.GOOGLE_CLIENT_ID = "client-id-valido"
    settings.GOOGLE_CLIENT_SECRET = "client-secret-valido"
    url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    response = client.get(f"{url}?oauth=1&next=https://malicioso.example")

    expected_next = reverse(
        "turmas:portal_minha_area", kwargs={"token": turma.token_publico}
    )
    assert response.status_code == 302
    assert response.url == (
        f"{reverse('google_oauth_start')}?{urlencode({'next': expected_next})}"
    )


@pytest.mark.django_db
def test_portal_exibe_login_indisponivel_sem_oauth(client, turma, settings):
    settings.GOOGLE_CLIENT_ID = ""
    settings.GOOGLE_CLIENT_SECRET = ""

    response = client.get(reverse("turmas:portal", kwargs={"token": turma.token_publico}))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Login Google indisponivel" in content
    assert "?oauth=1" not in content


@pytest.mark.django_db
def test_entrar_com_oauth_indisponivel_volta_para_portal_com_erro(client, turma, settings):
    settings.GOOGLE_CLIENT_ID = ""
    settings.GOOGLE_CLIENT_SECRET = ""
    url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    response = client.get(f"{url}?oauth=1", follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith(
        reverse("turmas:portal", kwargs={"token": turma.token_publico})
    )
    assert "nao foi possivel entrar com google agora" in response.content.decode().lower()
