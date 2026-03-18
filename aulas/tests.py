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
        assert aula_base.realizada is True
