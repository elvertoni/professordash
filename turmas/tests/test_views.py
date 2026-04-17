"""
Testes para as views do app turmas.

Views testadas:
- TurmaListView           (painel professor)
- TurmaPortalPublicoView  (portal público, sem login)
- BoletimTurmaView        (painel professor)
"""
import uuid

import pytest
from django.urls import reverse


# ---------------------------------------------------------------------------
# TurmaListView — painel do professor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTurmaListView:
    def test_professor_acessa_lista_retorna_200(self, client_professor):
        url = reverse("turmas:lista")
        response = client_professor.get(url)
        assert response.status_code == 200

    def test_anonimo_acessa_lista_e_recebe_redirect(self, client):
        url = reverse("turmas:lista")
        response = client.get(url)
        assert response.status_code == 302

    def test_aluno_acessa_lista_e_recebe_403_ou_redirect(self, client_aluno):
        url = reverse("turmas:lista")
        response = client_aluno.get(url)
        # ProfessorRequiredMixin → PermissionDenied para usuário não-staff autenticado
        assert response.status_code in (302, 403)

    def test_lista_exibe_turmas_no_contexto(self, client_professor, turma):
        url = reverse("turmas:lista")
        response = client_professor.get(url)
        assert response.status_code == 200
        # A turma criada deve aparecer em turmas_ativas ou turmas
        turmas_ativas = list(response.context.get("turmas_ativas", []))
        ids_ativos = [t.pk for t in turmas_ativas]
        assert turma.pk in ids_ativos


# ---------------------------------------------------------------------------
# TurmaPortalPublicoView — portal público
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTurmaPortalPublicoView:
    def test_acesso_com_token_valido_retorna_200(self, client, turma):
        url = reverse("turmas:portal", kwargs={"token": turma.token_publico})
        response = client.get(url)
        assert response.status_code == 200

    def test_acesso_com_token_invalido_retorna_404(self, client):
        url = reverse("turmas:portal", kwargs={"token": uuid.uuid4()})
        response = client.get(url)
        assert response.status_code == 404

    def test_portal_exibe_turma_no_contexto(self, client, turma):
        url = reverse("turmas:portal", kwargs={"token": turma.token_publico})
        response = client.get(url)
        assert response.context["turma"] == turma

    def test_turma_inativa_nao_acessivel(self, client, db):
        from turmas.models import Turma

        turma_inativa = Turma.objects.create(
            nome="Turma Inativa",
            codigo="INF-INATIVA",
            periodo="2",
            ano_letivo=2023,
            ativa=False,
        )
        url = reverse("turmas:portal", kwargs={"token": turma_inativa.token_publico})
        response = client.get(url)
        # TurmaPublicaMixin filtra por ativa=True → 404
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# BoletimTurmaView — painel do professor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBoletimTurmaView:
    def test_professor_acessa_boletim_retorna_200(self, client_professor, turma):
        url = reverse("turmas:boletim_turma", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.status_code == 200

    def test_anonimo_acessa_boletim_e_recebe_redirect(self, client, turma):
        url = reverse("turmas:boletim_turma", kwargs={"pk": turma.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_aluno_acessa_boletim_e_recebe_403_ou_redirect(
        self, client_aluno, turma
    ):
        url = reverse("turmas:boletim_turma", kwargs={"pk": turma.pk})
        response = client_aluno.get(url)
        assert response.status_code in (302, 403)

    def test_boletim_exibe_contexto_esperado(self, client_professor, turma):
        url = reverse("turmas:boletim_turma", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert "turma" in response.context
        assert "atividades" in response.context
        assert "grid" in response.context
        assert response.context["turma"] == turma

    def test_turma_inexistente_retorna_404(self, client_professor):
        url = reverse("turmas:boletim_turma", kwargs={"pk": 999999})
        response = client_professor.get(url)
        assert response.status_code == 404
