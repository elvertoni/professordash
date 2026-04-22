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


def _build_grade_highlights(tarefas, alunos, total_alunos):
    tarefas_com_data = [tarefa for tarefa in tarefas if tarefa["obj"].data]
    tarefas_ordenadas = sorted(
        tarefas_com_data,
        key=lambda tarefa: (tarefa["obj"].data, tarefa["obj"].ordem, tarefa["obj"].pk),
    )
    tarefas_maior_adesao = sorted(
        tarefas,
        key=lambda tarefa: (
            -tarefa["percentual"],
            tarefa["obj"].ordem,
            tarefa["obj"].nome.lower(),
        ),
    )
    tarefas_menor_adesao = sorted(
        tarefas,
        key=lambda tarefa: (
            tarefa["percentual"],
            tarefa["obj"].ordem,
            tarefa["obj"].nome.lower(),
        ),
    )
    alunos_ranking = sorted(
        alunos,
        key=lambda linha: (
            -linha["percentual"],
            -linha["total_realizadas"],
            linha["aluno"].nome.lower(),
        ),
    )
    alunos_alerta = sorted(
        alunos,
        key=lambda linha: (
            linha["percentual"],
            linha["total_realizadas"],
            linha["aluno"].nome.lower(),
        ),
    )

    tarefas_concluidas = sum(1 for tarefa in tarefas if tarefa["percentual"] == 100)
    tarefas_sem_data = sum(1 for tarefa in tarefas if not tarefa["obj"].data)
    alunos_zerados = sum(1 for linha in alunos if linha["total_realizadas"] == 0)

    return {
        "proximas_tarefas": tarefas_ordenadas[:4],
        "tarefas_maior_adesao": tarefas_maior_adesao[:3],
        "tarefas_menor_adesao": tarefas_menor_adesao[:3],
        "alunos_destaque": alunos_ranking[:4],
        "alunos_alerta": alunos_alerta[:4],
        "tarefas_concluidas": tarefas_concluidas,
        "tarefas_sem_data": tarefas_sem_data,
        "alunos_zerados": alunos_zerados,
        "media_checks_por_aluno": round(
            sum(linha["total_realizadas"] for linha in alunos) / total_alunos, 1
        )
        if total_alunos
        else 0,
    }


def _get_tarefa_resumo(tarefa, total_alunos=None):
    if total_alunos is None:
        total_alunos = Matricula.objects.filter(
            turma=tarefa.turma,
            ativa=True,
            aluno__ativo=True,
        ).count()

    total_realizadas = (
        RealizacaoTarefa.objects.filter(
            tarefa=tarefa,
            realizada=True,
            aluno__matriculas__turma=tarefa.turma,
            aluno__matriculas__ativa=True,
            aluno__ativo=True,
        )
        .distinct()
        .count()
    )

    return {
        "obj": tarefa,
        "total_realizadas": total_realizadas,
        "total_pendentes": max(total_alunos - total_realizadas, 0),
        "percentual": _percentual(total_realizadas, total_alunos),
        "esta_concluida": total_alunos > 0 and total_realizadas == total_alunos,
        "esta_critica": total_alunos > 0 and _percentual(total_realizadas, total_alunos) <= 35,
        "sem_data": tarefa.data is None,
    }


def _render_tarefa_header(request, turma, tarefa):
    total_alunos = Matricula.objects.filter(
        turma=turma,
        ativa=True,
        aluno__ativo=True,
    ).count()
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
        Matricula.objects.filter(turma=turma, ativa=True, aluno__ativo=True)
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
                RealizacaoTarefa.objects.bulk_create(realizacoes_faltantes, ignore_conflicts=True)

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
                "total_pendentes": max(total_alunos - total_realizadas, 0),
                "percentual": _percentual(total_realizadas, total_alunos),
                "realizados_alunos": realizacoes[tarefa.pk],
                "esta_concluida": total_alunos > 0 and total_realizadas == total_alunos,
                "esta_critica": total_alunos > 0 and _percentual(total_realizadas, total_alunos) <= 35,
                "sem_data": tarefa.data is None,
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
                "total_pendentes": max(len(tarefas_base) - total_realizadas_aluno, 0),
                "percentual": _percentual(total_realizadas_aluno, len(tarefas_base)),
                "tarefas_pendentes": [
                    tarefa["obj"] for tarefa in tarefas if aluno.pk not in tarefa["realizados_alunos"]
                ],
            }
        )

    checks_realizados = sum(tarefa["total_realizadas"] for tarefa in tarefas)
    total_checks = len(tarefas_base) * total_alunos
    highlights = _build_grade_highlights(tarefas, alunos, total_alunos)

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
        "proximas_tarefas": highlights["proximas_tarefas"],
        "tarefas_maior_adesao": highlights["tarefas_maior_adesao"],
        "tarefas_menor_adesao": highlights["tarefas_menor_adesao"],
        "alunos_destaque": highlights["alunos_destaque"],
        "alunos_alerta": highlights["alunos_alerta"],
        "tarefas_concluidas": highlights["tarefas_concluidas"],
        "tarefas_sem_data": highlights["tarefas_sem_data"],
        "alunos_zerados": highlights["alunos_zerados"],
        "media_checks_por_aluno": highlights["media_checks_por_aluno"],
    }


class TarefasGradeView(ProfessorRequiredMixin, View):
    template_name = "tarefas/grade.html"

    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs["pk"])
        context = _build_grade_context(turma, criar_faltantes=False)
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
            aluno__ativo=True,
        )
        aluno = matricula.aluno

        realizacao, _ = RealizacaoTarefa.objects.get_or_create(
            tarefa=tarefa,
            aluno=aluno,
        )
        realizacao.realizada = not realizacao.realizada
        realizacao.save(update_fields=["realizada", "atualizado_em"])

        grade_context = _build_grade_context(turma, criar_faltantes=False)
        tarefa_resumo = next(
            item for item in grade_context["tarefas"] if item["obj"].pk == tarefa.pk
        )
        linha_resumo = next(
            item for item in grade_context["linhas"] if item["aluno"].pk == aluno.pk
        )

        return render(
            request,
            "tarefas/_toggle_response.html",
            {
                "turma": turma,
                "tarefa": tarefa,
                "aluno": aluno,
                "realizacao": realizacao,
                "tarefa_resumo": tarefa_resumo,
                "linha_resumo": linha_resumo,
                "tarefas": grade_context["tarefas"],
                "total_alunos": grade_context["total_alunos"],
                "checks_realizados": grade_context["checks_realizados"],
                "checks_pendentes": grade_context["checks_pendentes"],
                "percentual_geral": grade_context["percentual_geral"],
                "proximas_tarefas": grade_context["proximas_tarefas"],
                "tarefas_maior_adesao": grade_context["tarefas_maior_adesao"],
                "tarefas_menor_adesao": grade_context["tarefas_menor_adesao"],
                "alunos_destaque": grade_context["alunos_destaque"],
                "alunos_alerta": grade_context["alunos_alerta"],
                "tarefas_concluidas": grade_context["tarefas_concluidas"],
                "tarefas_sem_data": grade_context["tarefas_sem_data"],
                "alunos_zerados": grade_context["alunos_zerados"],
                "media_checks_por_aluno": grade_context["media_checks_por_aluno"],
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

        matriculas = Matricula.objects.filter(
            turma=turma,
            ativa=True,
            aluno__ativo=True,
        ).select_related("aluno")
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
