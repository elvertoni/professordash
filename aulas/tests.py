import json

import pytest
from django.urls import reverse

from aulas.forms import AulaForm
from aulas.models import Aula


@pytest.fixture
def aula_base(db, turma):
    """Aula base para os testes."""
    return Aula.objects.create(
        turma=turma,
        titulo="Introdução",
        numero=1,
        conteudo="Conteudo inicial",
        realizada=True,
        ordem=1,
    )


@pytest.fixture
def aula_segunda(db, turma):
    """Segunda aula para testar reorder."""
    return Aula.objects.create(
        turma=turma,
        titulo="Variaveis",
        numero=2,
        conteudo="Conteudo secundario",
        ordem=2,
    )


@pytest.mark.django_db
class TestAulaModel:
    def test_str_retorna_numero_e_titulo(self, aula_base):
        assert str(aula_base) == "Aula 1 — Introdução"


@pytest.mark.django_db
class TestAulaForm:
    def test_form_accepta_conteudo_markdown(self, turma):
        form = AulaForm(
            data={
                "titulo": "Aula Markdown",
                "numero": 3,
                "data": "2026-03-18",
                "conteudo": "# Titulo\n\nTexto",
                "ordem": 3,
            }
        )

        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestAulasViews:
    def test_lista_publica_eh_acessivel_por_token(self, client, turma, aula_base):
        url = reverse(
            "turmas:portal_aulas_lista", kwargs={"token": turma.token_publico}
        )

        response = client.get(url)

        assert response.status_code == 200
        assert list(response.context["aulas"]) == [aula_base]

    def test_lista_publica_exibe_aulas_futuras_como_em_breve(self, client, turma):
        rascunho = Aula.objects.create(
            turma=turma,
            titulo="Rascunho",
            numero=3,
            conteudo="Ainda não liberada",
            realizada=False,
            ordem=3,
        )
        url = reverse(
            "turmas:portal_aulas_lista", kwargs={"token": turma.token_publico}
        )

        response = client.get(url)
        content = response.content.decode()

        assert response.status_code == 200
        assert list(response.context["aulas"]) == [rascunho]
        assert response.context["total_aulas"] == 1
        assert response.context["aulas_realizadas"] == 0
        assert response.context["proxima_aula_pk"] == rascunho.pk
        assert "Em breve" in content

    def test_lista_publica_calcula_progresso_com_aulas_liberadas_e_futuras(
        self, client, turma, aula_base
    ):
        proxima = Aula.objects.create(
            turma=turma,
            titulo="Próxima Aula",
            numero=2,
            conteudo="Conteúdo futuro",
            realizada=False,
            ordem=2,
        )
        url = reverse(
            "turmas:portal_aulas_lista", kwargs={"token": turma.token_publico}
        )

        response = client.get(url)
        content = response.content.decode()

        assert response.status_code == 200
        assert list(response.context["aulas"]) == [aula_base, proxima]
        assert response.context["total_aulas"] == 2
        assert response.context["aulas_realizadas"] == 1
        assert response.context["proxima_aula_pk"] == proxima.pk
        assert "1 de 2 aula" in content
        assert "Em breve" in content

    def test_detalhe_publico_bloqueia_aula_nao_realizada(self, client, turma):
        aula = Aula.objects.create(
            turma=turma,
            titulo="Privada",
            numero=4,
            conteudo="Nao deveria aparecer",
            realizada=False,
            ordem=4,
        )
        url = reverse(
            "turmas:portal_aulas_detalhe",
            kwargs={"token": turma.token_publico, "aula_pk": aula.pk},
        )

        response = client.get(url)

        assert response.status_code == 404

    def test_detalhe_publico_usa_links_publicos_e_nao_vaza_rascunhos(
        self, client, turma, aula_base
    ):
        Aula.objects.create(
            turma=turma,
            titulo="Rascunho Interno",
            numero=2,
            conteudo="Nao deveria aparecer para alunos",
            realizada=False,
            ordem=2,
        )
        url = reverse(
            "turmas:portal_aulas_detalhe",
            kwargs={"token": turma.token_publico, "aula_pk": aula_base.pk},
        )

        response = client.get(url)
        content = response.content.decode()

        assert response.status_code == 200
        assert "Rascunho Interno" not in content
        assert reverse(
            "turmas:portal_aulas_detalhe",
            kwargs={"token": turma.token_publico, "aula_pk": aula_base.pk},
        ) in content
        assert response.context["atividades_url"] == reverse(
            "turmas:portal_atividades_lista",
            kwargs={"token": turma.token_publico},
        )
        assert reverse(
            "turmas:aulas_detalhe",
            kwargs={"pk": turma.pk, "aula_pk": aula_base.pk},
        ) not in content

    def test_importar_markdown_define_numero_sequencial(self, client_professor, turma):
        url = reverse("turmas:aulas_importar_md", kwargs={"pk": turma.pk})
        arquivo = b"# Aula Nova\n\nConteudo"

        from django.core.files.uploadedfile import SimpleUploadedFile

        response = client_professor.post(
            url,
            {"arquivo": SimpleUploadedFile("nova.md", arquivo, content_type="text/markdown")},
        )

        assert response.status_code == 302
        aula = Aula.objects.get(titulo="Aula Nova")
        assert aula.numero == 1

    def test_reordenar_aulas_atualiza_ordem(
        self, client_professor, turma, aula_base, aula_segunda
    ):
        url = reverse("turmas:aulas_reordenar", kwargs={"pk": turma.pk})

        response = client_professor.post(
            url,
            data=json.dumps({"ids": [aula_segunda.pk, aula_base.pk]}),
            content_type="application/json",
        )

        assert response.status_code == 200
        aula_base.refresh_from_db()
        aula_segunda.refresh_from_db()
        assert aula_segunda.ordem == 0
        assert aula_base.ordem == 1

    def test_marcar_realizada_alterna_estado(self, client_professor, turma, aula_base):
        url = reverse(
            "turmas:aulas_realizada",
            kwargs={"pk": turma.pk, "aula_pk": aula_base.pk},
        )

        response = client_professor.post(url)

        assert response.status_code == 200
        aula_base.refresh_from_db()
        assert aula_base.realizada is False
