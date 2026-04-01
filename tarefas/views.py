from django.contrib import messages
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views import View

from core.mixins import ProfessorRequiredMixin
from turmas.models import Matricula, Turma

from .models import RealizacaoTarefa, Tarefa


class TarefasGradeView(ProfessorRequiredMixin, View):
    template_name = "tarefas/grade.html"

    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefas = list(Tarefa.objects.filter(turma=turma))
        matriculas = (
            Matricula.objects.filter(turma=turma, ativa=True)
            .select_related("aluno")
            .order_by("aluno__nome")
        )

        linhas = []
        totais = {tarefa.pk: 0 for tarefa in tarefas}

        for matricula in matriculas:
            aluno = matricula.aluno
            realizacoes = []

            for tarefa in tarefas:
                realizacao, _ = RealizacaoTarefa.objects.get_or_create(
                    tarefa=tarefa,
                    aluno=aluno,
                )
                realizacoes.append(realizacao)
                if realizacao.realizada:
                    totais[tarefa.pk] += 1

            linhas.append({"aluno": aluno, "realizacoes": realizacoes})

        context = {
            "turma": turma,
            "tarefas": tarefas,
            "linhas": linhas,
            "totais_linha": [totais[tarefa.pk] for tarefa in tarefas],
        }
        return render(request, self.template_name, context)


class TarefaToggleView(ProfessorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(Tarefa, pk=kwargs["tarefa_pk"], turma=turma)
        matricula = get_object_or_404(
            Matricula.objects.select_related("aluno"),
            turma=turma,
            aluno_id=kwargs["aluno_pk"],
            ativa=True,
        )
        aluno = matricula.aluno

        realizacao, _ = RealizacaoTarefa.objects.get_or_create(
            tarefa=tarefa,
            aluno=aluno,
        )
        realizacao.realizada = not realizacao.realizada
        realizacao.save(update_fields=["realizada", "atualizado_em"])

        return render(
            request,
            "tarefas/_checkbox.html",
            {
                "turma": turma,
                "tarefa": tarefa,
                "aluno": aluno,
                "realizacao": realizacao,
            },
        )


class TarefaCriarView(ProfessorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        nome = request.POST.get("nome", "").strip()
        data_raw = request.POST.get("data", "").strip()
        data = parse_date(data_raw) if data_raw else None
        is_htmx = bool(getattr(request, "htmx", False))

        if not nome:
            messages.error(request, "Informe o nome da tarefa.")
            return self._redirect(turma, is_htmx)

        max_ordem = Tarefa.objects.filter(turma=turma).aggregate(max_ordem=Max("ordem"))[
            "max_ordem"
        ]
        ordem = 0 if max_ordem is None else max_ordem + 1

        tarefa = Tarefa.objects.create(
            turma=turma,
            nome=nome,
            data=data,
            ordem=ordem,
        )

        matriculas = Matricula.objects.filter(turma=turma, ativa=True).select_related(
            "aluno"
        )
        RealizacaoTarefa.objects.bulk_create(
            [
                RealizacaoTarefa(tarefa=tarefa, aluno=matricula.aluno)
                for matricula in matriculas
            ]
        )

        messages.success(request, f'Tarefa "{tarefa.nome}" adicionada com sucesso.')
        return self._redirect(turma, is_htmx)

    def _redirect(self, turma, is_htmx):
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        if is_htmx:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = url
            return response
        return redirect("turmas:tarefas_grade", pk=turma.pk)


class TarefaExcluirView(ProfessorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(Tarefa, pk=kwargs["tarefa_pk"], turma=turma)
        is_htmx = bool(getattr(request, "htmx", False))

        nome_tarefa = tarefa.nome
        tarefa.delete()
        messages.success(request, f'Tarefa "{nome_tarefa}" excluida.')

        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        if is_htmx:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = url
            return response
        return redirect("turmas:tarefas_grade", pk=turma.pk)
