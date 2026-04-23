import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from materiais.models import Material, TipoMaterial, VisibilidadeMaterial


@pytest.mark.django_db
def test_lista_publica_exibe_material_restrito_sem_login(client, turma):
    material = Material.objects.create(
        turma=turma,
        titulo="Apostila restrita",
        tipo=TipoMaterial.HTML,
        visibilidade=VisibilidadeMaterial.RESTRITO,
        conteudo_html="<h1>Apostila</h1>",
    )
    url = reverse("turmas:portal_materiais_lista", kwargs={"token": turma.token_publico})

    response = client.get(url)

    assert response.status_code == 200
    assert material in list(response.context["materiais"])
    assert "Apostila restrita" in response.content.decode()
    assert reverse(
        "turmas:portal_materiais_html",
        kwargs={"token": turma.token_publico, "material_pk": material.pk},
    ) in response.content.decode()


@pytest.mark.django_db
def test_html_publico_abre_material_restrito_sem_login(client, turma):
    material = Material.objects.create(
        turma=turma,
        titulo="Pagina HTML",
        tipo=TipoMaterial.HTML,
        visibilidade=VisibilidadeMaterial.RESTRITO,
        conteudo_html="<h1>Conteudo liberado pelo token</h1>",
    )
    url = reverse(
        "turmas:portal_materiais_html",
        kwargs={"token": turma.token_publico, "material_pk": material.pk},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "text/html; charset=utf-8"
    assert "Conteudo liberado pelo token" in response.content.decode()


@pytest.mark.django_db
def test_download_publico_baixa_material_restrito_sem_login(client, turma, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    material = Material.objects.create(
        turma=turma,
        titulo="Arquivo restrito",
        tipo=TipoMaterial.ARQUIVO,
        visibilidade=VisibilidadeMaterial.RESTRITO,
        arquivo=SimpleUploadedFile("arquivo.txt", b"conteudo do arquivo"),
    )
    url = reverse(
        "turmas:portal_materiais_download",
        kwargs={"token": turma.token_publico, "material_pk": material.pk},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith('attachment; filename="arquivo')
