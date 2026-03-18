import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from aulas.models import Aula
from materiais.forms import MaterialForm
from materiais.models import Material, TipoMaterial, VisibilidadeMaterial

PDF_BYTES = b"%PDF-1.4 fake content for testing"


@pytest.fixture
def aula_material(db, turma):
    """Aula associada à turma para escolher no formulário de material."""
    return Aula.objects.create(
        turma=turma,
        titulo="Aula Base",
        numero=1,
        conteudo="Conteudo base",
        ordem=1,
    )


@pytest.fixture
def material_publico(db, turma, aula_material):
    """Material público usado nos testes de listagem."""
    return Material.objects.create(
        turma=turma,
        aula=aula_material,
        titulo="Slide Público",
        descricao="Para todos.",
        tipo=TipoMaterial.PDF,
        visibilidade=VisibilidadeMaterial.PUBLICO,
        ordem=1,
    )


@pytest.fixture
def material_restrito(db, turma, aula_material):
    """Material restrito usado nos testes de listagem."""
    return Material.objects.create(
        turma=turma,
        aula=aula_material,
        titulo="Slide Restrito",
        descricao="Só para alunos logados.",
        tipo=TipoMaterial.PDF,
        visibilidade=VisibilidadeMaterial.RESTRITO,
        ordem=2,
    )


@pytest.mark.django_db
class TestMaterialModel:
    def test_str_retorna_titulo(self, material_publico):
        assert str(material_publico) == "Slide Público"


@pytest.mark.django_db
class TestMaterialForm:
    def test_material_form_aceita_pdf_para_material_do_tipo_pdf(
        self, turma, aula_material
    ):
        arquivo = SimpleUploadedFile(
            "apostila.pdf",
            PDF_BYTES,
            content_type="application/pdf",
        )
        form = MaterialForm(
            data={
                "turma": turma.pk,
                "aula": aula_material.pk,
                "titulo": "Apostila",
                "descricao": "Material de apoio",
                "tipo": TipoMaterial.PDF,
                "visibilidade": VisibilidadeMaterial.PUBLICO,
                "ordem": 1,
            },
            files={"arquivo": arquivo},
            turma=turma,
        )

        assert form.is_valid(), form.errors

    def test_material_form_exige_url_para_tipo_link(self, turma, aula_material):
        form = MaterialForm(
            data={
                "turma": turma.pk,
                "aula": aula_material.pk,
                "titulo": "Link",
                "descricao": "",
                "tipo": TipoMaterial.LINK,
                "visibilidade": VisibilidadeMaterial.PUBLICO,
                "ordem": 1,
            },
            turma=turma,
        )

        assert not form.is_valid()
        assert "url_externa" in form.errors


@pytest.mark.django_db
class TestMaterialListaPublicaView:
    def test_visitante_ve_apenas_materiais_publicos(
        self, client, turma, material_publico, material_restrito
    ):
        url = reverse(
            "turmas:portal_materiais_lista", kwargs={"token": turma.token_publico}
        )

        response = client.get(url)

        assert response.status_code == 200
        assert list(response.context["materiais"]) == [material_publico]

    def test_aluno_matriculado_ve_materiais_publicos_e_restritos(
        self, client, turma, aluno, matricula, material_publico, material_restrito
    ):
        url = reverse(
            "turmas:portal_materiais_lista", kwargs={"token": turma.token_publico}
        )

        client.force_login(aluno.user)
        response = client.get(url)

        assert response.status_code == 200
        assert list(response.context["materiais"]) == [
            material_publico,
            material_restrito,
        ]
