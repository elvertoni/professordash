import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin

from .forms import TurmaForm
from .models import Turma

logger = logging.getLogger(__name__)


class TurmaListView(ProfessorRequiredMixin, ListView):
    """Lista todas as turmas do professor, separando ativas de arquivadas."""

    model = Turma
    template_name = "turmas/lista.html"
    context_object_name = "turmas"

    def get_queryset(self):
        return Turma.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turmas_ativas"] = Turma.objects.filter(ativa=True)
        ctx["turmas_arquivadas"] = Turma.objects.filter(ativa=False)
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
        messages.success(self.request, f'Turma "{self.object.nome}" criada com sucesso.')
        return response


class TurmaDetailView(ProfessorRequiredMixin, DetailView):
    """Exibe os detalhes de uma turma com suas aulas e alunos matriculados."""

    model = Turma
    template_name = "turmas/detalhe.html"
    context_object_name = "turma"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["matriculas"] = self.object.matriculas.filter(ativa=True).select_related("aluno")
        ctx["aulas"] = self.object.aulas.all()
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
        turma.save(update_fields=["ativa", "atualizado_em"])
        status = "ativada" if turma.ativa else "arquivada"
        logger.info(f"Turma pk={pk} {status}")
        messages.success(request, f'Turma "{turma.nome}" {status}.')
        return redirect("turmas:lista")


class TurmaPortalPublicoView(TurmaPublicaMixin, TemplateView):
    """Portal público da turma acessível via token UUID."""

    template_name = "turmas/portal.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["aulas"] = self.turma.aulas.filter(realizada=True).order_by("ordem", "numero")
        return ctx


class TurmaEntrarView(TurmaPublicaMixin, View):
    """Redireciona para o Google OAuth, mantendo o token da turma na sessão."""

    def get(self, request, token):
        request.session["turma_token"] = str(token)
        next_url = f"/turma/{token}/minha-area/"
        return redirect(reverse("google_login") + f"?next={next_url}")
