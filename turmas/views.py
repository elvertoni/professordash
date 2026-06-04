import csv
import logging
from decimal import Decimal
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from core.auth import is_google_oauth_configured
from core.mixins import AlunoAutenticadoMixin, ProfessorRequiredMixin, TurmaPublicaMixin

from .forms import TurmaForm
from .models import Matricula, Turma

logger = logging.getLogger(__name__)


def _percentual_conclusao(parte, total):
    if not total:
        return 0
    return round((parte / total) * 100)


class TurmaListView(ProfessorRequiredMixin, ListView):
    """Lista todas as turmas do professor, separando ativas de arquivadas."""

    model = Turma
    template_name = "turmas/lista.html"
    context_object_name = "turmas"

    def get_queryset(self):
        return Turma.objects.prefetch_related("matriculas", "aulas")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = list(self.get_queryset())
        ctx["turmas_ativas"] = [t for t in qs if t.ativa]
        ctx["turmas_arquivadas"] = [t for t in qs if not t.ativa]
        return ctx


class TurmaCreateView(ProfessorRequiredMixin, CreateView):
    """Cria uma nova turma."""

    model = Turma
    form_class = TurmaForm
    template_name = "turmas/form.html"
    success_url = reverse_lazy("turmas:lista")

    def form_valid(self, form):
        logger.info(f"Criando turma: {form.cleaned_data.get('nome')}")
        response = super().form_valid(form)
        messages.success(
            self.request, f'Turma "{self.object.nome}" criada com sucesso.'
        )
        return response


class TurmaDetailView(ProfessorRequiredMixin, DetailView):
    """Exibe os detalhes de uma turma com suas aulas e alunos matriculados."""

    model = Turma
    template_name = "turmas/detalhe.html"
    context_object_name = "turma"

    def get_queryset(self):
        return Turma.objects.prefetch_related(
            Prefetch(
                "matriculas",
                queryset=Matricula.objects.select_related("aluno").order_by(
                    "aluno__nome"
                ),
            ),
            "aulas",
            "materiais",
            "atividades",
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        matriculas_todas = list(self.object.matriculas.all())
        matriculas_ativas = [
            matricula
            for matricula in matriculas_todas
            if matricula.ativa and matricula.aluno.ativo
        ]
        matriculas_inativas = [
            matricula
            for matricula in matriculas_todas
            if not matricula.ativa or not matricula.aluno.ativo
        ]

        ctx["matriculas"] = matriculas_ativas
        ctx["aulas"] = self.object.aulas.all()
        ctx["materiais"] = self.object.materiais.all()
        ctx["atividades"] = self.object.atividades.all().order_by("-prazo")
        total_alunos_ativos = len(matriculas_ativas)
        tarefas = list(
            self.object.tarefas.annotate(
                total_realizadas=Count(
                    "realizacoes",
                    filter=Q(realizacoes__realizada=True),
                )
            )
            .order_by("ordem", "criado_em")
        )
        for tarefa in tarefas:
            tarefa.percentual = _percentual_conclusao(
                tarefa.total_realizadas,
                total_alunos_ativos,
            )
        ctx["tarefas"] = tarefas
        ctx["total_alunos_ativos"] = total_alunos_ativos
        ctx["total_alunos_inativos"] = len(matriculas_inativas)
        return ctx


class TurmaUpdateView(ProfessorRequiredMixin, UpdateView):
    """Edita os dados de uma turma existente."""

    model = Turma
    form_class = TurmaForm
    template_name = "turmas/form.html"
    context_object_name = "turma"

    def form_valid(self, form):
        logger.info(f"Atualizando turma pk={self.object.pk}")
        response = super().form_valid(form)
        messages.success(self.request, f'Turma "{self.object.nome}" atualizada.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:detalhe", kwargs={"pk": self.object.pk})


class TurmaArquivarView(ProfessorRequiredMixin, View):
    """Alterna o estado ativo/arquivado de uma turma via POST."""

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        turma.ativa = not turma.ativa
        turma.save()
        status = "ativada" if turma.ativa else "arquivada"
        logger.info(f"Turma pk={pk} {status}")
        messages.success(request, f'Turma "{turma.nome}" {status}.')
        return redirect("turmas:lista")


class TurmaDeleteView(ProfessorRequiredMixin, View):
    """Exclui permanentemente uma turma via POST."""

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        nome = turma.nome
        turma.delete()
        logger.info(f"Turma pk={pk} excluida")
        messages.success(request, f'Turma "{nome}" excluida permanentemente.')
        return redirect("turmas:lista")


class TurmaPortalPublicoView(TurmaPublicaMixin, TemplateView):
    """Portal publico da turma acessivel via token UUID."""

    template_name = "turmas/portal.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["aulas"] = self.turma.aulas.filter(status="publicada").order_by(
            "ordem", "numero"
        )
        return ctx


class TurmaEntrarView(TurmaPublicaMixin, View):
    """Mantem o fluxo de entrada da turma sem iniciar OAuth automaticamente."""

    def get(self, request, token):
        request.session["turma_token"] = str(token)
        default_next = reverse("turmas:portal_minha_area", kwargs={"token": token})
        next_url = request.GET.get("next", default_next)
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = default_next

        if request.GET.get("oauth") == "1":
            if not is_google_oauth_configured():
                messages.error(
                    request,
                    "Nao foi possivel entrar com Google agora. "
                    "Tente novamente mais tarde ou avise o professor.",
                )
                return redirect("turmas:portal", token=token)

            return redirect(
                f"{reverse('google_oauth_start')}?{urlencode({'next': next_url})}"
            )

        portal_url = reverse("turmas:portal", kwargs={"token": token})
        if next_url != default_next:
            portal_url = f"{portal_url}?{urlencode({'next': next_url})}"
        return redirect(portal_url)


class TarefasGradePublicaView(TurmaPublicaMixin, TemplateView):
    """Exibe a grade de tarefas da turma em modo somente leitura."""

    template_name = "tarefas/grade_publica.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from tarefas.views import _build_grade_context

        ctx.update(_build_grade_context(self.turma, criar_faltantes=False))
        return ctx


class BoletimTurmaView(ProfessorRequiredMixin, DetailView):
    """View para o boletim geral da turma com as notas."""

    model = Turma
    template_name = "avaliacoes/boletim.html"
    context_object_name = "turma"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turma = self.object

        atividades = turma.atividades.filter(
            publicada=True, valor_pontos__gt=0
        ).order_by("prazo")
        alunos = (
            turma.alunos.filter(matriculas__turma=turma, matriculas__ativa=True)
            .distinct()
            .order_by("nome")
        )

        grid = []
        from atividades.models import Entrega

        entregas = Entrega.objects.filter(atividade__turma=turma).select_related(
            "aluno", "atividade"
        )
        entrega_map = {(e.aluno_id, e.atividade_id): e.nota for e in entregas}

        for aluno in alunos:
            soma_notas = Decimal("0")
            soma_pesos = Decimal("0")
            linha_notas = []
            for ativ in atividades:
                nota = entrega_map.get((aluno.id, ativ.id))
                linha_notas.append({"atividade": ativ, "nota": nota})
                if nota is not None:
                    soma_notas += nota
                soma_pesos += ativ.valor_pontos

            media = Decimal("0")
            if soma_pesos > 0:
                media = (soma_notas / soma_pesos) * 100

            grid.append(
                {
                    "aluno": aluno,
                    "notas": linha_notas,
                    "media": media,
                    "total": soma_notas,
                }
            )

        context["atividades"] = atividades
        context["grid"] = grid
        return context


class ExportarBoletimCSVView(ProfessorRequiredMixin, View):
    """Exporta o boletim da turma em CSV."""

    def get(self, request, pk, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=pk)

        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        safe_codigo = slugify(turma.codigo)
        response["Content-Disposition"] = (
            f'attachment; filename="boletim_{safe_codigo}.csv"'
        )
        response.write("\ufeff")

        writer = csv.writer(response)

        atividades = turma.atividades.filter(
            publicada=True, valor_pontos__gt=0
        ).order_by("prazo")

        header = ["Aluno", "Matricula"]
        for ativ in atividades:
            header.append(f"{ativ.titulo} (Max: {ativ.valor_pontos})")
        header.extend(["Total", "Media (%)"])
        writer.writerow(header)

        from atividades.models import Entrega

        alunos = (
            turma.alunos.filter(matriculas__turma=turma, matriculas__ativa=True)
            .distinct()
            .order_by("nome")
        )
        entregas = Entrega.objects.filter(atividade__turma=turma).select_related(
            "aluno", "atividade"
        )
        entrega_map = {(e.aluno_id, e.atividade_id): e.nota for e in entregas}

        for aluno in alunos:
            linha = [aluno.nome, aluno.matricula]
            soma_notas = Decimal("0")
            soma_pesos = Decimal("0")
            for ativ in atividades:
                nota = entrega_map.get((aluno.id, ativ.id))
                linha.append(nota if nota is not None else "-")
                if nota is not None:
                    soma_notas += nota
                soma_pesos += ativ.valor_pontos

            linha.append(soma_notas)
            media = (soma_notas / soma_pesos * 100) if soma_pesos > 0 else 0
            linha.append(f"{media:.1f}%")
            writer.writerow(linha)
        return response


class ExportarBoletimPDFView(ProfessorRequiredMixin, DetailView):
    """Exporta o boletim da turma em PDF."""

    model = Turma

    def get(self, request, *args, **kwargs):
        turma = self.get_object()

        atividades = turma.atividades.filter(
            publicada=True, valor_pontos__gt=0
        ).order_by("prazo")
        alunos = (
            turma.alunos.filter(matriculas__turma=turma, matriculas__ativa=True)
            .distinct()
            .order_by("nome")
        )

        grid = []
        from atividades.models import Entrega

        entregas = Entrega.objects.filter(atividade__turma=turma).select_related(
            "aluno", "atividade"
        )
        entrega_map = {(e.aluno_id, e.atividade_id): e.nota for e in entregas}

        for aluno in alunos:
            soma_notas = Decimal("0")
            soma_pesos = Decimal("0")
            linha_notas = []
            for ativ in atividades:
                nota = entrega_map.get((aluno.id, ativ.id))
                linha_notas.append({"atividade": ativ, "nota": nota})
                if nota is not None:
                    soma_notas += nota
                soma_pesos += ativ.valor_pontos

            media = Decimal("0")
            if soma_pesos > 0:
                media = (soma_notas / soma_pesos) * 100

            grid.append(
                {
                    "aluno": aluno,
                    "notas": linha_notas,
                    "media": media,
                    "total": soma_notas,
                }
            )

        context = {"turma": turma, "atividades": atividades, "grid": grid}

        html_string = render_to_string(
            "avaliacoes/boletim_pdf.html", context, request=request
        )
        import weasyprint

        pdf_file = weasyprint.HTML(
            string=html_string, base_url=request.build_absolute_uri("/")
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="boletim_{turma.codigo}.pdf"'
        )
        return response


class MinhasNotasView(AlunoAutenticadoMixin, TemplateView):
    """Exibe notas e feedbacks das atividades para aluno logado na area publica."""

    template_name = "avaliacoes/minhas_notas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        turma = self.turma
        aluno = self.matricula.aluno
        ctx["turma"] = turma

        atividades = turma.atividades.filter(publicada=True).order_by("prazo")

        from atividades.models import Entrega

        entregas = Entrega.objects.filter(
            atividade__turma=turma, aluno=aluno
        ).select_related("atividade")
        entrega_map = {e.atividade_id: e for e in entregas}

        minhas_notas = []
        soma_notas = Decimal("0")
        soma_pesos = Decimal("0")

        for ativ in atividades:
            entrega = entrega_map.get(ativ.id)
            nota = entrega.nota if entrega else None
            feedback = entrega.feedback if entrega else ""

            minhas_notas.append(
                {
                    "atividade": ativ,
                    "entrega": entrega,
                    "nota": nota,
                    "feedback": feedback,
                }
            )

            if nota is not None:
                soma_notas += nota
            soma_pesos += ativ.valor_pontos

        media = Decimal("0")
        if soma_pesos > 0:
            media = (soma_notas / soma_pesos) * 100

        ctx["minhas_notas"] = minhas_notas
        ctx["total_notas"] = soma_notas
        ctx["total_pesos"] = soma_pesos
        ctx["media_percent"] = media
        return ctx
