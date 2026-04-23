import logging
import os

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Turma

from .forms import MaterialForm
from .models import Material

logger = logging.getLogger(__name__)


def _token_publico_pode_acessar_material(turma, material):
    return material.turma_id == turma.pk


class MaterialMixin:
    """Resolve self.turma a partir do pk na URL para views admin de material."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.material = None
        material_pk = kwargs.get("material_pk")

        if material_pk is not None:
            self.material = get_object_or_404(
                Material.objects.select_related("turma", "aula"),
                pk=material_pk,
            )
            self.turma = self.material.turma
            return

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
        return self.material

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
        return self.material

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
        return (
            Material.objects.filter(turma=self.turma)
            .select_related("aula")
            .order_by("ordem", "criado_em")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class MaterialDownloadAdminView(ProfessorRequiredMixin, MaterialMixin, View):
    """Download autenticado de material pelo professor."""

    def get(self, request, *args, **kwargs):
        material = self.material
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

        if not _token_publico_pode_acessar_material(self.turma, material):
            raise PermissionDenied

        return FileResponse(
            material.arquivo.open("rb"),
            as_attachment=True,
            filename=os.path.basename(material.arquivo.name),
        )


class MaterialHTMLAdminView(ProfessorRequiredMixin, MaterialMixin, View):
    """Serve o HTML estático de uma apostila para o professor."""

    def get(self, request, *args, **kwargs):
        material = get_object_or_404(
            Material.objects.select_related("turma", "aula"),
            pk=self.kwargs["material_pk"],
            turma=self.turma,
        )
        if material.arquivo:
            conteudo = material.arquivo.read().decode("utf-8", errors="replace")
        elif material.conteudo_html:
            conteudo = material.conteudo_html
        else:
            raise Http404("Material sem arquivo.")
        return HttpResponse(conteudo, content_type="text/html; charset=utf-8")


class MateriaisSincronizarGithubView(ProfessorRequiredMixin, MaterialMixin, View):
    """Sincroniza os materiais HTML de uma turma com o repositório GitHub ProfToniCoimbra."""

    def post(self, request, pk):
        from aulas.github_sync import get_subject_from_codigo
        from .github_sync import build_materials_index, fetch_tree, sync_turma

        subject = get_subject_from_codigo(self.turma.codigo)
        if not subject:
            messages.error(
                request,
                f"A turma {self.turma.codigo} não tem mapeamento no GitHub. "
                "Verifique o código da turma.",
            )
            return redirect("turmas:materiais_lista", pk=self.turma.pk)

        try:
            tree = fetch_tree()
            materials_index = build_materials_index(tree)
            resultado = sync_turma(self.turma, materials_index)
        except Exception as exc:
            logger.exception(
                "Falha ao sincronizar materiais turma pk=%s codigo=%s subject=%s",
                self.turma.pk,
                self.turma.codigo,
                subject,
            )
            messages.error(
                request,
                f"Erro durante a sincronização ({type(exc).__name__}): {exc}",
            )
            return redirect("turmas:materiais_lista", pk=self.turma.pk)

        messages.success(
            request,
            "Sincronização concluída: "
            f"{resultado['criadas']} materiais novos, "
            f"{resultado['atualizadas']} atualizados, "
            f"{resultado['erros']} erros.",
        )
        return redirect("turmas:materiais_lista", pk=self.turma.pk)


class MaterialHTMLPublicaView(TurmaPublicaMixin, View):
    """Serve o HTML estático de uma apostila respeitando visibilidade."""

    def get(self, request, *args, **kwargs):
        material = get_object_or_404(
            Material.objects.select_related("turma", "aula"),
            pk=self.kwargs["material_pk"],
            turma=self.turma,
        )
        if material.arquivo:
            conteudo = material.arquivo.read().decode("utf-8", errors="replace")
        elif material.conteudo_html:
            conteudo = material.conteudo_html
        else:
            raise Http404("Material sem arquivo.")

        if not _token_publico_pode_acessar_material(self.turma, material):
            raise PermissionDenied

        return HttpResponse(conteudo, content_type="text/html; charset=utf-8")
