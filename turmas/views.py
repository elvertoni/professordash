import logging
import csv
from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
import weasyprint

from core.mixins import AlunoAutenticadoMixin, ProfessorRequiredMixin, TurmaPublicaMixin

from .forms import TurmaForm
from .models import Turma

logger = logging.getLogger(__name__)


class TurmaListView(ProfessorRequiredMixin, ListView):
    """Lista todas as turmas do professor, separando ativas de arquivadas."""

    model = Turma
    template_name = "turmas/lista.html"
    context_object_name = "turmas"

    def get_queryset(self):
        return Turma.objects.prefetch_related("matriculas", "aulas")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turmas_ativas"] = Turma.objects.filter(ativa=True).prefetch_related(
            "matriculas", "aulas"
        )
        ctx["turmas_arquivadas"] = Turma.objects.filter(ativa=False).prefetch_related(
            "matriculas", "aulas"
        )
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["matriculas"] = self.object.matriculas.filter(ativa=True).select_related(
            "aluno"
        )
        ctx["aulas"] = self.object.aulas.all()
        ctx["materiais"] = self.object.materiais.all()
        ctx["atividades"] = self.object.atividades.all().order_by("-prazo")
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
        logger.info(f"Turma pk={pk} excluída")
        messages.success(request, f'Turma "{nome}" excluída permanentemente.')
        return redirect("turmas:lista")


class TurmaPortalPublicoView(TurmaPublicaMixin, TemplateView):
    """Portal público da turma acessível via token UUID."""

    template_name = "turmas/portal.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["aulas"] = self.turma.aulas.filter(realizada=True).order_by(
            "ordem", "numero"
        )
        return ctx


class TurmaEntrarView(TurmaPublicaMixin, View):
    """Redireciona para o Google OAuth, mantendo o token da turma na sessão."""

    def get(self, request, token):
        request.session["turma_token"] = str(token)
        next_url = f"/turma/{token}/minha-area/"
        return redirect(reverse("google_login") + f"?next={next_url}")


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

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="boletim_{turma.codigo}.csv"'
        )

        writer = csv.writer(response)

        atividades = turma.atividades.filter(
            publicada=True, valor_pontos__gt=0
        ).order_by("prazo")

        header = ["Aluno", "Matrícula"]
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
        pdf_file = weasyprint.HTML(
            string=html_string, base_url=request.build_absolute_uri("/")
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="boletim_{turma.codigo}.pdf"'
        )
        return response


class MinhasNotasView(AlunoAutenticadoMixin, TemplateView):
    """Exibe as notas e feedbacks das atividades de uma turma para o aluno logado na área pública."""

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
