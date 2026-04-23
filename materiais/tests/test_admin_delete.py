import pytest
from django.urls import reverse

from materiais.models import Material, TipoMaterial
from turmas.models import Turma


@pytest.mark.django_db
def test_professor_abre_confirmacao_de_exclusao_de_material(client_professor, turma):
    material = Material.objects.create(
        turma=turma,
        titulo="Material para excluir",
        tipo=TipoMaterial.LINK,
        url_externa="https://example.com/material",
    )
    url = reverse(
        "turmas:materiais_excluir",
        kwargs={"pk": turma.pk, "material_pk": material.pk},
    )

    response = client_professor.get(url)

    assert response.status_code == 200
    assert response.context["material"] == material
    assert "Material para excluir" in response.content.decode()


@pytest.mark.django_db
def test_professor_exclui_material_por_post(client_professor, turma):
    material = Material.objects.create(
        turma=turma,
        titulo="Material para excluir",
        tipo=TipoMaterial.LINK,
        url_externa="https://example.com/material",
    )
    url = reverse(
        "turmas:materiais_excluir",
        kwargs={"pk": turma.pk, "material_pk": material.pk},
    )

    response = client_professor.post(url)

    assert response.status_code == 302
    assert response.url == reverse("turmas:materiais_lista", kwargs={"pk": turma.pk})
    assert not Material.objects.filter(pk=material.pk).exists()


@pytest.mark.django_db
def test_exclusao_usa_turma_real_do_material_quando_url_tem_pk_defasado(
    client_professor, turma
):
    outra_turma = Turma.objects.create(
        nome="Outra turma",
        codigo="OUT-2024",
        periodo="1",
        ano_letivo=2024,
    )
    material = Material.objects.create(
        turma=outra_turma,
        titulo="Material em outra turma",
        tipo=TipoMaterial.LINK,
        url_externa="https://example.com/material",
    )
    url = reverse(
        "turmas:materiais_excluir",
        kwargs={"pk": turma.pk, "material_pk": material.pk},
    )

    response = client_professor.post(url)

    assert response.status_code == 302
    assert response.url == reverse(
        "turmas:materiais_lista", kwargs={"pk": outra_turma.pk}
    )
    assert not Material.objects.filter(pk=material.pk).exists()
