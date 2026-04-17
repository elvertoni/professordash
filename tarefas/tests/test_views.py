"""
Testes para as views do app tarefas.

Views testadas:
- TarefasGradePublicaView  (portal público, sem login)
- TarefasGradeView         (painel professor)
- TarefaToggleView         (toggle checkbox, professor)
"""
import pytest
from django.urls import reverse

from tarefas.models import RealizacaoTarefa, Tarefa


# ---------------------------------------------------------------------------
# Fixtures auxiliares
# ---------------------------------------------------------------------------


@pytest.fixture
def tarefa(db, turma, matricula):
    """Tarefa na turma com RealizacaoTarefa já criada para o aluno matriculado."""
    t = Tarefa.objects.create(turma=turma, nome="Tarefa 1", ordem=0)
    RealizacaoTarefa.objects.create(tarefa=t, aluno=matricula.aluno, realizada=False)
    return t


# ---------------------------------------------------------------------------
# TarefasGradePublicaView — acesso público (sem login)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTarefasGradePublicaView:
    def test_acesso_publico_sem_login_retorna_200(self, client, turma):
        url = reverse("turmas:portal_tarefas_grade", kwargs={"token": turma.token_publico})
        response = client.get(url)
        assert response.status_code == 200

    def test_acesso_publico_token_invalido_retorna_404(self, client):
        import uuid

        url = reverse(
            "turmas:portal_tarefas_grade",
            kwargs={"token": uuid.uuid4()},
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_acesso_publico_exibe_turma_no_contexto(self, client, turma):
        url = reverse("turmas:portal_tarefas_grade", kwargs={"token": turma.token_publico})
        response = client.get(url)
        assert response.context["turma"] == turma


# ---------------------------------------------------------------------------
# TarefasGradeView — painel do professor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTarefasGradeView:
    def test_professor_acessa_grade_retorna_200(self, client_professor, turma):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.status_code == 200

    def test_aluno_acessa_grade_e_recebe_redirect(self, client_aluno, turma):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        response = client_aluno.get(url)
        # ProfessorRequiredMixin redireciona não-staff (ou lança PermissionDenied)
        assert response.status_code in (302, 403)

    def test_anonimo_acessa_grade_e_recebe_redirect(self, client, turma):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_grade_exibe_turma_no_contexto(self, client_professor, turma):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.context["turma"] == turma


# ---------------------------------------------------------------------------
# TarefaToggleView — toggle de checkbox pelo professor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTarefaToggleView:
    def _url(self, turma, tarefa, aluno):
        return reverse(
            "turmas:tarefas_toggle",
            kwargs={
                "pk": turma.pk,
                "tarefa_pk": tarefa.pk,
                "aluno_pk": aluno.pk,
            },
        )

    def test_professor_toggle_cria_realizacao_como_true(
        self, client_professor, turma, tarefa, matricula
    ):
        # Garante estado inicial falso
        RealizacaoTarefa.objects.filter(tarefa=tarefa, aluno=matricula.aluno).update(
            realizada=False
        )
        url = self._url(turma, tarefa, matricula.aluno)
        response = client_professor.post(url)
        assert response.status_code == 200
        realizacao = RealizacaoTarefa.objects.get(tarefa=tarefa, aluno=matricula.aluno)
        assert realizacao.realizada is True

    def test_professor_toggle_segundo_post_inverte_para_false(
        self, client_professor, turma, tarefa, matricula
    ):
        # Primeiro toggle → True
        url = self._url(turma, tarefa, matricula.aluno)
        client_professor.post(url)
        # Segundo toggle → False
        client_professor.post(url)
        realizacao = RealizacaoTarefa.objects.get(tarefa=tarefa, aluno=matricula.aluno)
        assert realizacao.realizada is False

    def test_professor_toggle_idempotencia_terceiro_post(
        self, client_professor, turma, tarefa, matricula
    ):
        url = self._url(turma, tarefa, matricula.aluno)
        client_professor.post(url)  # False → True
        client_professor.post(url)  # True  → False
        client_professor.post(url)  # False → True
        realizacao = RealizacaoTarefa.objects.get(tarefa=tarefa, aluno=matricula.aluno)
        assert realizacao.realizada is True

    def test_aluno_nao_pode_fazer_toggle(
        self, client_aluno, turma, tarefa, matricula
    ):
        url = self._url(turma, tarefa, matricula.aluno)
        response = client_aluno.post(url)
        assert response.status_code in (302, 403)

    def test_anonimo_nao_pode_fazer_toggle(self, client, turma, tarefa, matricula):
        url = self._url(turma, tarefa, matricula.aluno)
        response = client.post(url)
        assert response.status_code == 302

    def test_toggle_cria_registro_se_nao_existia(
        self, client_professor, turma, matricula
    ):
        """Testa get_or_create: tarefa sem RealizacaoTarefa prévia."""
        tarefa_nova = Tarefa.objects.create(turma=turma, nome="Tarefa Nova", ordem=1)
        url = self._url(turma, tarefa_nova, matricula.aluno)
        response = client_professor.post(url)
        assert response.status_code == 200
        assert RealizacaoTarefa.objects.filter(
            tarefa=tarefa_nova, aluno=matricula.aluno
        ).exists()
