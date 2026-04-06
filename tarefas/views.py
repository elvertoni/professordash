from django.contrib import messages
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views import View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Matricula, Turma

from .models import RealizacaoTarefa, Tarefa


def _is_htmx(request):
    return request.META.get("HTTP_HX_REQUEST") == "true"


def _htmx_redirect(url):
    response = HttpResponse(status=204)
    response["HX-Redirect"] = url
    return response


def _percentual(parte, total):
    if not total:
        return 0
    return round((parte / total) * 100)


def _get_tarefa_resumo(tarefa, total_alunos=None):
    if total_alunos is None:
        total_alunos = Matricula.objects.filter(turma=tarefa.turma, ativa=True).count()

    total_realizadas = (
        RealizacaoTarefa.objects.filter(
            tarefa=tarefa,
            realizada=True,
            aluno__matriculas__turma=tarefa.turma,
            aluno__matriculas__ativa=True,
        )
        .distinct()
        .count()
    )

    return {
        "obj": tarefa,
        "total_realizadas": total_realizadas,
        "percentual": _percentual(total_realizadas, total_alunos),
    }


def _render_tarefa_header(request, turma, tarefa):
    total_alunos = Matricula.objects.filter(turma=turma, ativa=True).count()
    return render(
        request,
        "tarefas/_tarefa_header.html",
        {
            "turma": turma,
            "tarefa": _get_tarefa_resumo(tarefa, total_alunos=total_alunos),
            "total_alunos": total_alunos,
        },
    )


def _build_grade_context(turma, *, criar_faltantes=False):
    tarefas_base = list(Tarefa.objects.filter(turma=turma).select_related("turma"))
    matriculas = list(
        Matricula.objects.filter(turma=turma, ativa=True)
        .select_related("aluno", "turma")
        .order_by("aluno__nome")
    )

    realizacoes_map = {}
    if tarefas_base and matriculas:
        alunos = [matricula.aluno for matricula in matriculas]
        realizacoes_existentes = list(
            RealizacaoTarefa.objects.filter(tarefa__in=tarefas_base, aluno__in=alunos)
            .select_related("tarefa", "aluno")
            .order_by("tarefa_id", "aluno_id")
        )
        realizacoes_map = {
            (realizacao.tarefa_id, realizacao.aluno_id): realizacao
            for realizacao in realizacoes_existentes
        }

        if criar_faltantes:
            realizacoes_faltantes = []
            for tarefa in tarefas_base:
                for matricula in matriculas:
                    chave = (tarefa.pk, matricula.aluno_id)
                    if chave in realizacoes_map:
                        continue
                    realizacao = RealizacaoTarefa(tarefa=tarefa, aluno=matricula.aluno)
                    realizacoes_faltantes.append(realizacao)
                    realizacoes_map[chave] = realizacao

            if realizacoes_faltantes:
                RealizacaoTarefa.objects.bulk_create(realizacoes_faltantes)

    realizacoes = {tarefa.pk: set() for tarefa in tarefas_base}
    for realizacao in realizacoes_map.values():
        if realizacao.realizada:
            realizacoes[realizacao.tarefa_id].add(realizacao.aluno_id)

    total_alunos = len(matriculas)
    tarefas = []
    for tarefa in tarefas_base:
        total_realizadas = len(realizacoes[tarefa.pk])
        tarefas.append(
            {
                "obj": tarefa,
                "total_realizadas": total_realizadas,
                "percentual": _percentual(total_realizadas, total_alunos),
                "realizados_alunos": realizacoes[tarefa.pk],
            }
        )

    alunos = []
    for matricula in matriculas:
        aluno = matricula.aluno
        total_realizadas_aluno = 0
        celulas = []

        for tarefa in tarefas_base:
            realizou = aluno.pk in realizacoes[tarefa.pk]
            if realizou:
                total_realizadas_aluno += 1

            celula = {
                "tarefa": tarefa,
                "aluno": aluno,
                "realizada": realizou,
            }
            if criar_faltantes:
                celula["realizacao"] = realizacoes_map[(tarefa.pk, aluno.pk)]
            celulas.append(celula)

        alunos.append(
            {
                "matricula": matricula,
                "aluno": aluno,
                "celulas": celulas,
                "total_realizadas": total_realizadas_aluno,
                "percentual": _percentual(total_realizadas_aluno, len(tarefas_base)),
            }
        )

    checks_realizados = sum(tarefa["total_realizadas"] for tarefa in tarefas)
    total_checks = len(tarefas_base) * total_alunos

    return {
        "turma": turma,
        "tarefas": tarefas,
        "alunos": alunos,
        "linhas": alunos,
        "realizacoes": realizacoes,
        "total_alunos": total_alunos,
        "checks_realizados": checks_realizados,
        "checks_pendentes": max(total_checks - checks_realizados, 0),
        "percentual_geral": _percentual(checks_realizados, total_checks),
    }


class TarefasGradeView(ProfessorRequiredMixin, View):
    template_name = "tarefas/grade.html"

    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        context = _build_grade_context(turma, criar_faltantes=True)
        return render(request, self.template_name, context)


class TarefasGradePublicaView(TurmaPublicaMixin, View):
    template_name = "tarefas/grade_publica.html"

    def get(self, request, *args, **kwargs):
        context = _build_grade_context(self.turma, criar_faltantes=False)
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


class TarefaCabecalhoView(ProfessorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        tarefa = get_object_or_404(
            Tarefa.objects.select_related("turma"),
            pk=kwargs["tarefa_pk"],
            turma=turma,
        )
        return _render_tarefa_header(request, turma, tarefa)


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
            return _render_tarefa_header(request, turma, tarefa)
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
