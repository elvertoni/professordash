import json
import logging
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Turma

from .forms import AulaForm
from .models import Aula

logger = logging.getLogger(__name__)


class AulaMixin:
    """Resolve self.turma a partir do pk na URL para views admin de aula."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, pk=kwargs["pk"])


class AulaListView(ProfessorRequiredMixin, AulaMixin, ListView):
    """Lista as aulas de uma turma com suporte a reordenação."""

    template_name = "aulas/lista.html"
    context_object_name = "aulas"

    def get_queryset(self):
        return Aula.objects.filter(turma=self.turma).order_by("ordem", "numero")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AulaNavMixin:
    """Adiciona navegação prev/next e links de volta ao contexto."""

    def get_nav_context(self, aula):
        aulas = list(
            Aula.objects.filter(turma=self.turma)
            .order_by("ordem", "numero")
            .values_list("pk", "titulo", "numero")
        )
        idx = next((i for i, a in enumerate(aulas) if a[0] == aula.pk), None)
        ctx = {}

        if idx is not None and idx > 0:
            prev = aulas[idx - 1]
            ctx["aula_anterior"] = {"titulo": prev[1], "numero": prev[2]}
            ctx["prev_url"] = self._build_aula_url(prev[0])

        if idx is not None and idx < len(aulas) - 1:
            nxt = aulas[idx + 1]
            ctx["aula_proxima"] = {"titulo": nxt[1], "numero": nxt[2]}
            ctx["next_url"] = self._build_aula_url(nxt[0])

        return ctx

    def _build_aula_url(self, aula_pk):
        raise NotImplementedError


class AulaDetailView(ProfessorRequiredMixin, AulaMixin, AulaNavMixin, DetailView):
    """Exibe os detalhes de uma aula com conteúdo Markdown renderizado."""

    template_name = "aulas/aula_detalhe.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(Aula, pk=self.kwargs["aula_pk"], turma=self.turma)

    def _build_aula_url(self, aula_pk):
        from django.urls import reverse

        return reverse("turmas:aulas_detalhe", kwargs={"pk": self.turma.pk, "aula_pk": aula_pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["back_url"] = reverse_lazy("turmas:aulas_lista", kwargs={"pk": self.turma.pk})
        ctx["back_label"] = "Aulas"
        ctx.update(self.get_nav_context(self.object))
        return ctx


class AulaCreateView(ProfessorRequiredMixin, AulaMixin, CreateView):
    """Cria uma nova aula dentro de uma turma."""

    model = Aula
    form_class = AulaForm
    template_name = "aulas/form.html"

    def form_valid(self, form):
        form.instance.turma = self.turma
        logger.info(f"Criando aula '{form.cleaned_data.get('titulo')}' na turma pk={self.turma.pk}")
        response = super().form_valid(form)
        messages.success(self.request, f'Aula "{self.object.titulo}" criada com sucesso.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:aulas_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AulaUpdateView(ProfessorRequiredMixin, AulaMixin, UpdateView):
    """Edita os dados de uma aula existente."""

    model = Aula
    form_class = AulaForm
    template_name = "aulas/form.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(Aula, pk=self.kwargs["aula_pk"], turma=self.turma)

    def form_valid(self, form):
        logger.info(f"Atualizando aula pk={self.kwargs['aula_pk']}")
        response = super().form_valid(form)
        messages.success(self.request, f'Aula "{self.object.titulo}" atualizada.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:aulas_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AulaDeleteView(ProfessorRequiredMixin, AulaMixin, DeleteView):
    """Remove uma aula após confirmação."""

    model = Aula
    template_name = "aulas/confirmar_exclusao.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(Aula, pk=self.kwargs["aula_pk"], turma=self.turma)

    def form_valid(self, form):
        logger.info(f"Excluindo aula pk={self.kwargs['aula_pk']}")
        messages.success(self.request, "Aula excluída.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("turmas:aulas_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AulaImportarMdView(ProfessorRequiredMixin, AulaMixin, View):
    """Importa um arquivo .md como uma nova Aula. O título vem do primeiro H1."""

    def get(self, request, pk):
        return render(request, "aulas/importar_md.html", {"turma": self.turma})

    def post(self, request, pk):
        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            messages.error(request, "Nenhum arquivo enviado.")
            return render(request, "aulas/importar_md.html", {"turma": self.turma})

        if not arquivo.name.endswith(".md"):
            messages.error(request, "Apenas arquivos .md são aceitos.")
            return render(request, "aulas/importar_md.html", {"turma": self.turma})

        conteudo = arquivo.read().decode("utf-8", errors="replace")

        # Extrair título do primeiro H1
        match = re.search(r"^#\s+(.+)$", conteudo, re.MULTILINE)
        if match:
            titulo = match.group(1).strip()
        else:
            titulo = arquivo.name.removesuffix(".md")

        aula = Aula.objects.create(turma=self.turma, titulo=titulo, conteudo=conteudo)
        logger.info(f"Aula importada de .md: '{titulo}' na turma pk={self.turma.pk}")
        messages.success(request, f'Aula "{titulo}" importada com sucesso.')
        return redirect("turmas:aulas_editar", pk=self.turma.pk, aula_pk=aula.pk)


class AulaReordenarView(ProfessorRequiredMixin, AulaMixin, View):
    """Recebe lista de IDs via JSON/POST e atualiza a ordem das aulas."""

    def post(self, request, pk):
        try:
            ids = json.loads(request.body).get("ids", [])
        except (json.JSONDecodeError, AttributeError):
            ids = request.POST.getlist("ids[]")

        for ordem, aula_id in enumerate(ids):
            Aula.objects.filter(pk=aula_id, turma=self.turma).update(ordem=ordem)

        logger.debug(f"Aulas reordenadas na turma pk={pk}: {ids}")
        return JsonResponse({"ok": True})


class AulaMarcarRealizadaView(ProfessorRequiredMixin, AulaMixin, View):
    """Alterna o estado realizada/não realizada de uma aula via POST."""

    def post(self, request, pk, aula_pk):
        aula = get_object_or_404(Aula, pk=aula_pk, turma=self.turma)
        aula.realizada = not aula.realizada
        aula.save(update_fields=["realizada", "atualizado_em"])
        logger.info(f"Aula pk={aula_pk} marcada como realizada={aula.realizada}")
        return JsonResponse({"realizada": aula.realizada})


# ---------------------------------------------------------------------------
# Views públicas (portal do aluno)
# ---------------------------------------------------------------------------


class AulaListaPublicaView(TurmaPublicaMixin, ListView):
    """Lista pública das aulas de uma turma, acessível via token."""

    template_name = "aulas/lista_publica.html"
    context_object_name = "aulas"

    def get_queryset(self):
        return Aula.objects.filter(turma=self.turma).order_by("ordem", "numero")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        qs = self.get_queryset()
        ctx["total_aulas"] = qs.count()
        ctx["aulas_realizadas"] = qs.filter(realizada=True).count()
        proxima = qs.filter(realizada=False).first()
        ctx["proxima_aula_pk"] = proxima.pk if proxima else None
        return ctx


class AulaDetalhePublicoView(TurmaPublicaMixin, AulaNavMixin, DetailView):
    """Detalhe público de uma aula com conteúdo Markdown renderizado."""

    template_name = "aulas/aula_detalhe.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(Aula, pk=self.kwargs["aula_pk"], turma=self.turma)

    def _build_aula_url(self, aula_pk):
        from django.urls import reverse

        return reverse(
            "turmas:portal_aulas_detalhe",
            kwargs={"token": self.turma.token_publico, "aula_pk": aula_pk},
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["back_url"] = reverse_lazy(
            "turmas:portal_aulas_lista", kwargs={"token": self.turma.token_publico}
        )
        ctx["back_label"] = "Aulas"
        ctx.update(self.get_nav_context(self.object))
        return ctx
