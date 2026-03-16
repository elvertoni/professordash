import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Matricula, Turma

from .forms import MaterialForm
from .models import Material, VisibilidadeMaterial

logger = logging.getLogger(__name__)


class MaterialMixin:
    """Resolve self.turma a partir do pk na URL para views admin de material."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, pk=kwargs["pk"])


class MaterialListView(ProfessorRequiredMixin, MaterialMixin, ListView):
    template_name = "materiais/lista.html"
    context_object_name = "materiais"

    def get_queryset(self):
        return Material.objects.filter(turma=self.turma).select_related("aula").order_by("ordem", "criado_em")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class MaterialCreateView(ProfessorRequiredMixin, MaterialMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "materiais/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["turma"] = self.turma
        return kwargs

    def form_valid(self, form):
        form.instance.turma = self.turma
        logger.info(f"Criando material '{form.cleaned_data.get('titulo')}' na turma pk={self.turma.pk}")
        response = super().form_valid(form)
        messages.success(self.request, f'Material "{self.object.titulo}" criado com sucesso.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:materiais_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class MaterialUpdateView(ProfessorRequiredMixin, MaterialMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = "materiais/form.html"
    context_object_name = "material"
    pk_url_kwarg = "material_pk"

    def get_object(self):
        return get_object_or_404(Material, pk=self.kwargs["material_pk"], turma=self.turma)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["turma"] = self.turma
        return kwargs

    def form_valid(self, form):
        logger.info(f"Atualizando material pk={self.kwargs['material_pk']}")
        response = super().form_valid(form)
        messages.success(self.request, f'Material "{self.object.titulo}" atualizado.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:materiais_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class MaterialDeleteView(ProfessorRequiredMixin, MaterialMixin, DeleteView):
    model = Material
    template_name = "materiais/confirmar_exclusao.html"
    context_object_name = "material"
    pk_url_kwarg = "material_pk"

    def get_object(self):
        return get_object_or_404(Material, pk=self.kwargs["material_pk"], turma=self.turma)

    def form_valid(self, form):
        logger.info(f"Excluindo material pk={self.kwargs['material_pk']}")
        messages.success(self.request, "Material excluído.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("turmas:materiais_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


# ---------------------------------------------------------------------------
# Views públicas (portal do aluno)
# ---------------------------------------------------------------------------


class MaterialListaPublicaView(TurmaPublicaMixin, ListView):
    template_name = "materiais/lista_publica.html"
    context_object_name = "materiais"

    def get_queryset(self):
        qs = Material.objects.filter(turma=self.turma).select_related("aula").order_by("ordem", "criado_em")

        user = self.request.user

        # Se for admin, vê todos
        if user.is_authenticated and user.is_staff:
            return qs

        # Se for aluno, verifica matrícula
        if user.is_authenticated:
            try:
                Matricula.objects.get(aluno__user=user, turma=self.turma, ativa=True)
                return qs  # Aluno ativo na turma vê tudo
            except Matricula.DoesNotExist:
                pass

        # Caso contrário, apenas públicos
        return qs.filter(visibilidade=VisibilidadeMaterial.PUBLICO)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx
