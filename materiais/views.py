import logging
import os

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Matricula, Turma

from .forms import MaterialForm
from .models import Material, VisibilidadeMaterial

logger = logging.getLogger(__name__)


def _usuario_pode_acessar_material(request, turma, material):
    user = request.user
    if user.is_authenticated and user.is_staff:
        return True
    if material.visibilidade == VisibilidadeMaterial.PUBLICO:
        return True
    if (
        user.is_authenticated
        and Matricula.objects.filter(aluno__user=user, turma=turma, ativa=True).exists()
    ):
        return True
    return False


class MaterialMixin:
    """Resolve self.turma a partir do pk na URL para views admin de material."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, pk=kwargs["pk"])


class MaterialListView(ProfessorRequiredMixin, MaterialMixin, ListView):
    template_name = "materiais/lista.html"
    context_object_name = "materiais"

    def get_queryset(self):
        return (
            Material.objects.filter(turma=self.turma)
            .select_related("aula")
            .order_by("ordem", "criado_em")
        )

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
        logger.info(
            f"Criando material '{form.cleaned_data.get('titulo')}' na turma pk={self.turma.pk}"
        )
        response = super().form_valid(form)
        messages.success(
            self.request, f'Material "{self.object.titulo}" criado com sucesso.'
        )
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
        return get_object_or_404(
            Material, pk=self.kwargs["material_pk"], turma=self.turma
        )

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
        return get_object_or_404(
            Material, pk=self.kwargs["material_pk"], turma=self.turma
        )

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
        qs = (
            Material.objects.filter(turma=self.turma)
            .select_related("aula")
            .order_by("ordem", "criado_em")
        )

        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return qs

        if (
            user.is_authenticated
            and Matricula.objects.filter(
                aluno__user=user, turma=self.turma, ativa=True
            ).exists()
        ):
            return qs

        return qs.filter(visibilidade=VisibilidadeMaterial.PUBLICO)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class MaterialDownloadAdminView(ProfessorRequiredMixin, MaterialMixin, View):
    """Download autenticado de material pelo professor."""

    def get(self, request, *args, **kwargs):
        material = get_object_or_404(
            Material.objects.select_related("turma", "aula"),
            pk=self.kwargs["material_pk"],
            turma=self.turma,
        )
        if not material.arquivo:
            raise Http404("Material sem arquivo.")

        return FileResponse(
            material.arquivo.open("rb"),
            as_attachment=True,
            filename=os.path.basename(material.arquivo.name),
        )


class MaterialDownloadPublicoView(TurmaPublicaMixin, View):
    """Download de material respeitando visibilidade e matrícula."""

    def get(self, request, *args, **kwargs):
        material = get_object_or_404(
            Material.objects.select_related("turma", "aula"),
            pk=self.kwargs["material_pk"],
            turma=self.turma,
        )
        if not material.arquivo:
            raise Http404("Material sem arquivo.")

        if not _usuario_pode_acessar_material(request, self.turma, material):
            if (
                material.visibilidade == VisibilidadeMaterial.RESTRITO
                and not request.user.is_authenticated
            ):
                return redirect("turmas:entrar", token=self.turma.token_publico)
            raise PermissionDenied

        return FileResponse(
            material.arquivo.open("rb"),
            as_attachment=True,
            filename=os.path.basename(material.arquivo.name),
        )
