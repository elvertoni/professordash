import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_cta_de_login_da_lista_publica_dispara_oauth(client, turma, atividade_aberta):
    url = reverse(
        "turmas:portal_atividades_lista",
        kwargs={"token": turma.token_publico},
    )
    response = client.get(url)
    entrar_url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    assert response.status_code == 200
    assert f"{entrar_url}?oauth=1" in response.content.decode()


@pytest.mark.django_db
def test_cta_de_login_no_detalhe_publico_dispara_oauth(client, turma, atividade_aberta):
    url = reverse(
        "turmas:portal_atividade_detalhe",
        kwargs={
            "token": turma.token_publico,
            "atividade_id": atividade_aberta.pk,
        },
    )
    response = client.get(url)
    entrar_url = reverse("turmas:entrar", kwargs={"token": turma.token_publico})

    assert response.status_code == 200
    assert f"{entrar_url}?oauth=1" in response.content.decode()


@pytest.mark.django_db
def test_cta_publica_exibe_indisponivel_sem_oauth(client, turma, atividade_aberta, settings):
    settings.GOOGLE_CLIENT_ID = ""
    settings.GOOGLE_CLIENT_SECRET = ""
    url = reverse(
        "turmas:portal_atividades_lista",
        kwargs={"token": turma.token_publico},
    )

    response = client.get(url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Login Google indisponivel" in content
    assert "?oauth=1" not in content
