from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from alunos.models import Aluno
from tarefas.models import RealizacaoTarefa, Tarefa
from turmas.models import Matricula

User = get_user_model()


@pytest.fixture
def tarefa_base(db, turma):
    return Tarefa.objects.create(
        turma=turma,
        nome="Caderno IA 1",
        data=date(2026, 3, 28),
        ordem=0,
    )


@pytest.fixture
def segundo_aluno(db, turma):
    user = User.objects.create_user(
        username="ana.aluna",
        email="ana@escola.pr.gov.br",
        password="senha123!",
        is_active=True,
    )
    aluno = Aluno.objects.create(
        user=user,
        nome="Ana Souza",
        email="ana@escola.pr.gov.br",
        matricula="2024002",
    )
    Matricula.objects.create(aluno=aluno, turma=turma, ativa=True)
    return aluno


@pytest.mark.django_db
class TestTarefasGradeView:
    def test_grade_renderiza_e_cria_realizacoes_faltantes(
        self, client_professor, turma, aluno, matricula, segundo_aluno, tarefa_base
    ):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})

        response = client_professor.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert "Checklist de tarefas da turma" in html
        assert "Caderno IA 1" in html
        assert RealizacaoTarefa.objects.filter(tarefa=tarefa_base).count() == 2

    def test_aluno_nao_acessa_grade(self, client_aluno, turma):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})

        response = client_aluno.get(url)

        assert response.status_code == 403


@pytest.mark.django_db
class TestTarefaCriarView:
    def test_criacao_gera_realizacoes_apenas_para_matriculas_ativas(
        self, client_professor, turma, aluno, matricula
    ):
        aluno_inativo = Aluno.objects.create(
            nome="Aluno Inativo",
            email="inativo@escola.pr.gov.br",
            matricula="2024998",
        )
        Matricula.objects.create(aluno=aluno_inativo, turma=turma, ativa=False)

        response = client_professor.post(
            reverse("turmas:tarefas_criar", kwargs={"pk": turma.pk}),
            {"nome": "Ativ. 09", "data": "2026-04-01"},
        )

        tarefa = Tarefa.objects.get(nome="Ativ. 09")

        assert response.status_code == 302
        assert tarefa.turma == turma
        assert RealizacaoTarefa.objects.filter(tarefa=tarefa).count() == 1
        assert RealizacaoTarefa.objects.filter(tarefa=tarefa, aluno=aluno).exists()
        assert not RealizacaoTarefa.objects.filter(
            tarefa=tarefa, aluno=aluno_inativo
        ).exists()


@pytest.mark.django_db
class TestTarefaToggleView:
    def test_toggle_alterna_status_da_realizacao(
        self, client_professor, turma, aluno, matricula, tarefa_base
    ):
        url = reverse(
            "turmas:tarefas_toggle",
            kwargs={
                "pk": turma.pk,
                "tarefa_pk": tarefa_base.pk,
                "aluno_pk": aluno.pk,
            },
        )

        response = client_professor.post(url, HTTP_HX_REQUEST="true")

        realizacao = RealizacaoTarefa.objects.get(tarefa=tarefa_base, aluno=aluno)

        assert response.status_code == 200
        assert realizacao.realizada is True
        assert "Marcar como pendente" in response.content.decode()


@pytest.mark.django_db
class TestTurmaDetalheComTarefas:
    def test_detalhe_exibe_aba_e_resumo_de_tarefas(
        self, client_professor, turma, aluno, matricula, tarefa_base
    ):
        RealizacaoTarefa.objects.create(
            tarefa=tarefa_base,
            aluno=aluno,
            realizada=True,
        )

        url = reverse("turmas:detalhe", kwargs={"pk": turma.pk}) + "?tab=tarefas"

        response = client_professor.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert "Checklist de tarefas" in html
        assert "Abrir grade" in html
        assert "Caderno IA 1" in html
        assert "1 / 1 alunos" in html
