import pytest
from django.urls import reverse

from tarefas.models import RealizacaoTarefa, Tarefa


@pytest.mark.django_db
class TestGradeProfessorUI:
    def test_grade_professor_exibe_radar_e_grade_acionavel(
        self, client_professor, turma, matricula
    ):
        tarefa_1 = Tarefa.objects.create(turma=turma, nome="Mapa mental", ordem=0)
        tarefa_2 = Tarefa.objects.create(turma=turma, nome="Apresentacao", ordem=1)
        RealizacaoTarefa.objects.create(
            tarefa=tarefa_1, aluno=matricula.aluno, realizada=True
        )
        RealizacaoTarefa.objects.create(
            tarefa=tarefa_2, aluno=matricula.aluno, realizada=False
        )

        response = client_professor.get(
            reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Dashboard operacional da turma." in content
        assert "Radar da turma" in content
        assert "Proximas tarefas" in content
        assert "Alunos pedindo atencao" in content
        assert "Grade acionavel" in content

    def test_toggle_htmx_retorna_updates_oob(self, client_professor, turma, matricula):
        tarefa = Tarefa.objects.create(turma=turma, nome="Podcast", ordem=0)
        url = reverse(
            "turmas:tarefas_toggle",
            kwargs={
                "pk": turma.pk,
                "tarefa_pk": tarefa.pk,
                "aluno_pk": matricula.aluno.pk,
            },
        )

        response = client_professor.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        content = response.content.decode()
        assert 'id="tarefas-overview"' in content
        assert 'hx-swap-oob="outerHTML"' in content
        assert f'id="tarefa-header-{tarefa.pk}"' in content
        assert f'id="linha-resumo-{matricula.aluno.pk}"' in content

    def test_grade_ignora_aluno_inativo_e_realizacao_faltante(
        self, client_professor, turma, aluno
    ):
        tarefa = Tarefa.objects.create(turma=turma, nome="Sem backfill", ordem=0)
        turma.matriculas.create(aluno=aluno, ativa=True)
        aluno.ativo = False
        aluno.save(update_fields=["ativo"])

        response = client_professor.get(
            reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Sem backfill" in content
        assert aluno.nome not in content
