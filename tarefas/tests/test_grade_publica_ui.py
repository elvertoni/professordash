import pytest
from django.urls import reverse

from tarefas.models import RealizacaoTarefa, Tarefa


@pytest.mark.django_db
class TestGradePublicaUI:
    def test_grade_publica_exibe_bloco_mobile_e_grade_completa(
        self, client, turma, matricula
    ):
        tarefa_1 = Tarefa.objects.create(turma=turma, nome="Caderno 1", ordem=0)
        tarefa_2 = Tarefa.objects.create(turma=turma, nome="Lista final", ordem=1)
        RealizacaoTarefa.objects.create(
            tarefa=tarefa_1, aluno=matricula.aluno, realizada=True
        )
        RealizacaoTarefa.objects.create(
            tarefa=tarefa_2, aluno=matricula.aluno, realizada=False
        )

        response = client.get(
            reverse("turmas:portal_tarefas_grade", kwargs={"token": turma.token_publico})
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "Painel publico" in content
        assert "Mapa rapido das tarefas" in content
        assert "Resumo por aluno" in content
        assert "Grade completa" in content
        assert "Caderno 1" in content
        assert "Lista final" in content
        assert matricula.aluno.nome in content

    def test_grade_publica_nao_renderiza_controles_de_edicao_ou_toggle(
        self, client, turma, matricula
    ):
        tarefa = Tarefa.objects.create(turma=turma, nome="Projeto", ordem=0)
        RealizacaoTarefa.objects.create(
            tarefa=tarefa, aluno=matricula.aluno, realizada=True
        )

        response = client.get(
            reverse("turmas:portal_tarefas_grade", kwargs={"token": turma.token_publico})
        )

        assert response.status_code == 200
        content = response.content.decode()
        toggle_url = reverse(
            "turmas:tarefas_toggle",
            kwargs={
                "pk": turma.pk,
                "tarefa_pk": tarefa.pk,
                "aluno_pk": matricula.aluno.pk,
            },
        )
        editar_url = reverse(
            "turmas:tarefas_editar",
            kwargs={"pk": turma.pk, "tarefa_pk": tarefa.pk},
        )

        assert "Somente leitura" in content
        assert toggle_url not in content
        assert editar_url not in content
        assert "hx-post" not in content
