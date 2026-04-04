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


def _is_htmx(request):
    return request.META.get("HTTP_HX_REQUEST") == "true"


def _htmx_redirect(url):
    response = HttpResponse(status=204)
    response["HX-Redirect"] = url
    return response


class TarefasGradeView(ProfessorRequiredMixin, View):
    template_name = "tarefas/grade.html"

    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefas = list(Tarefa.objects.filter(turma=turma))
        matriculas = list(
            Matricula.objects.filter(turma=turma, ativa=True)
            .select_related("aluno")
            .order_by("aluno__nome")
        )
        alunos = [matricula.aluno for matricula in matriculas]

        realizacoes_map = {}
        if tarefas and alunos:
            realizacoes_existentes = list(
                RealizacaoTarefa.objects.filter(tarefa__in=tarefas, aluno__in=alunos)
                .select_related("tarefa", "aluno")
                .order_by("tarefa_id", "aluno_id")
            )
            realizacoes_map = {
                (realizacao.tarefa_id, realizacao.aluno_id): realizacao
                for realizacao in realizacoes_existentes
            }

            realizacoes_faltantes = []
            for tarefa in tarefas:
                for aluno in alunos:
                    chave = (tarefa.pk, aluno.pk)
                    if chave in realizacoes_map:
                        continue
                    realizacao = RealizacaoTarefa(tarefa=tarefa, aluno=aluno)
                    realizacoes_faltantes.append(realizacao)
                    realizacoes_map[chave] = realizacao

            if realizacoes_faltantes:
                RealizacaoTarefa.objects.bulk_create(realizacoes_faltantes)

        linhas = []
        totais_por_tarefa = {tarefa.pk: 0 for tarefa in tarefas}

        for matricula in matriculas:
            aluno = matricula.aluno
            realizacoes = []
            total_realizadas_aluno = 0

            for tarefa in tarefas:
                realizacao = realizacoes_map[(tarefa.pk, aluno.pk)]
                realizacoes.append(realizacao)
                if realizacao.realizada:
                    totais_por_tarefa[tarefa.pk] += 1
                    total_realizadas_aluno += 1

            linhas.append(
                {
                    "aluno": aluno,
                    "realizacoes": realizacoes,
                    "total_realizadas": total_realizadas_aluno,
                    "percentual": self._percentual(total_realizadas_aluno, len(tarefas)),
                }
            )

        total_checks = len(tarefas) * len(matriculas)
        checks_realizados = sum(totais_por_tarefa.values())
        tarefas_com_resumo = [
            {
                "obj": tarefa,
                "total_realizadas": totais_por_tarefa[tarefa.pk],
                "percentual": self._percentual(totais_por_tarefa[tarefa.pk], len(matriculas)),
            }
            for tarefa in tarefas
        ]

        context = {
            "turma": turma,
            "tarefas": tarefas_com_resumo,
            "linhas": linhas,
            "total_alunos": len(matriculas),
            "checks_realizados": checks_realizados,
            "checks_pendentes": max(total_checks - checks_realizados, 0),
            "percentual_geral": self._percentual(checks_realizados, total_checks),
        }
        return render(request, self.template_name, context)

    @staticmethod
    def _percentual(parte, total):
        if not total:
            return 0
        return round((parte / total) * 100)


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
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})

        if not nome:
            messages.error(request, "Informe o nome da tarefa.")
            if _is_htmx(request):
                return _htmx_redirect(url)
            return redirect(url)

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
        if _is_htmx(request):
            return _htmx_redirect(url)
        return redirect(url)


class TarefaEditarView(ProfessorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(Tarefa, pk=kwargs["tarefa_pk"], turma=turma)
        return render(
            request,
            "tarefas/_editar_form.html",
            {"turma": turma, "tarefa": tarefa},
        )

    def post(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(Tarefa, pk=kwargs["tarefa_pk"], turma=turma)
        nome = request.POST.get("nome", "").strip()
        data_raw = request.POST.get("data", "").strip()
        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})

        if not nome:
            messages.error(request, "Informe o nome da tarefa.")
            if _is_htmx(request):
                return _htmx_redirect(url)
            return redirect(url)

        tarefa.nome = nome
        tarefa.data = parse_date(data_raw) if data_raw else None
        tarefa.save(update_fields=["nome", "data", "atualizado_em"])

        messages.success(request, f'Tarefa "{tarefa.nome}" atualizada.')
        if _is_htmx(request):
            return _htmx_redirect(url)
        return redirect(url)


class TarefaExcluirView(ProfessorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(Tarefa, pk=kwargs["tarefa_pk"], turma=turma)

        nome_tarefa = tarefa.nome
        tarefa.delete()
        messages.success(request, f'Tarefa "{nome_tarefa}" excluida.')

        url = reverse("turmas:tarefas_grade", kwargs={"pk": turma.pk})
        if _is_htmx(request):
            return _htmx_redirect(url)
        return redirect(url)
