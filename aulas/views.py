import json
import logging
import re
from html import unescape

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from core.templatetags.markdownx import markdownify
from turmas.models import Turma

from .forms import AulaForm
from .models import Aula

logger = logging.getLogger(__name__)

HEADING_RE = re.compile(r"<h([23])([^>]*)>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
FIRST_H1_RE = re.compile(r"^\s*<h1[^>]*>.*?</h1>\s*", re.IGNORECASE | re.DOTALL)
FIRST_PARAGRAPH_RE = re.compile(r"^\s*<p[^>]*>(.*?)</p>\s*", re.IGNORECASE | re.DOTALL)
LEADING_HR_RE = re.compile(r"^\s*<hr\s*/?>\s*", re.IGNORECASE)


def _heading_text(inner_html):
    return unescape(strip_tags(inner_html)).strip()


def _unique_slug(text, used):
    base = slugify(text) or "secao"
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def _prepare_apostila_html(rendered_html):
    """Remove capa duplicada, adiciona anchors e embrulha seções H2."""
    body = FIRST_H1_RE.sub("", rendered_html, count=1)

    resumo = ""
    intro_match = FIRST_PARAGRAPH_RE.match(body)
    if intro_match:
        resumo = _heading_text(intro_match.group(1))
        body = body[intro_match.end() :]

    body = LEADING_HR_RE.sub("", body, count=1)
    toc = []
    used_ids = set()

    def add_heading_id(match):
        level = int(match.group(1))
        attrs = re.sub(
            r'\s+id=(?:"[^"]*"|\'[^\']*\')',
            "",
            match.group(2) or "",
            flags=re.IGNORECASE,
        )
        inner = match.group(3)
        text = _heading_text(inner)
        heading_id = _unique_slug(text, used_ids)
        toc.append({"id": heading_id, "titulo": text, "nivel": level})
        return f'<h{level}{attrs} id="{heading_id}">{inner}</h{level}>'

    body = HEADING_RE.sub(add_heading_id, body)
    body = _wrap_h2_sections(body)
    return body, resumo, toc


def _wrap_h2_sections(html):
    parts = re.split(r"(<h2\b[^>]*>.*?</h2>)", html, flags=re.IGNORECASE | re.DOTALL)
    if len(parts) < 3:
        return html

    wrapped = [parts[0]]
    for index in range(1, len(parts), 2):
        heading = parts[index]
        section_body = parts[index + 1] if index + 1 < len(parts) else ""
        wrapped.append(f'<section class="section">{heading}{section_body}</section>')
    return "".join(wrapped)


def _build_apostila_context(aula):
    rendered_html = str(markdownify(aula.conteudo))
    conteudo_html, resumo, toc = _prepare_apostila_html(rendered_html)
    aula.conteudo_html = conteudo_html
    aula.toc = toc
    aula.resumo = resumo
    aula.eyebrow = f"Aula {aula.numero:02d} · {aula.turma.codigo}"
    aula.disciplina = aula.turma.nome
    aula.serie = str(aula.turma.ano_letivo)
    aula.duracao = "50 min"
    aula.entrega = "Atividade da aula"
    return {"aula": aula}


def _set_apostila_download_header(response, aula):
    slug = slugify(aula.titulo) or str(aula.pk)
    filename = f"aula-{aula.numero:02d}-{slug}.html"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class AulaMixin:
    """Resolve self.turma a partir do pk na URL para views admin de aula."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        turma_pk = kwargs.get("pk") or kwargs.get("turma_pk")
        self.aula = None

        if turma_pk is not None:
            self.turma = get_object_or_404(Turma, pk=turma_pk)
            return

        aula_pk = kwargs.get("aula_pk")
        if aula_pk is None:
            raise KeyError("Expected 'pk', 'turma_pk', or 'aula_pk' in URL kwargs.")

        self.aula = get_object_or_404(Aula.objects.select_related("turma"), pk=aula_pk)
        self.turma = self.aula.turma


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

    def get_nav_queryset(self):
        return Aula.objects.filter(turma=self.turma).order_by("ordem", "numero")

    def get_sidebar_aulas(self):
        return [
            {
                "pk": aula.pk,
                "numero": aula.numero,
                "titulo": aula.titulo,
                "href": self._build_aula_url(aula.pk),
            }
            for aula in self.get_nav_queryset()
        ]

    def get_nav_context(self, aula):
        aulas = list(
            self.get_nav_queryset().values_list("pk", "titulo", "numero")
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
        if self.aula is not None and self.aula.turma_id == self.turma.pk:
            return self.aula
        return get_object_or_404(Aula, pk=self.kwargs["aula_pk"], turma=self.turma)

    def _build_aula_url(self, aula_pk):
        return reverse("turmas:aulas_detalhe", kwargs={"pk": self.turma.pk, "aula_pk": aula_pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["back_url"] = reverse_lazy("turmas:aulas_lista", kwargs={"pk": self.turma.pk})
        ctx["back_label"] = "Aulas"
        ctx["is_admin_view"] = True
        ctx["edit_url"] = reverse(
            "turmas:aulas_editar",
            kwargs={"pk": self.turma.pk, "aula_pk": self.object.pk},
        )
        if self.object.gera_apostila:
            apostila_url = reverse(
                "turmas:aulas_apostila",
                kwargs={"pk": self.turma.pk, "aula_pk": self.object.pk},
            )
            ctx["apostila_url"] = apostila_url
            ctx["apostila_download_url"] = f"{apostila_url}?download=1"
        ctx["atividades_url"] = f"{reverse('turmas:detalhe', kwargs={'pk': self.turma.pk})}?tab=atividades"
        ctx["sidebar_aulas"] = self.get_sidebar_aulas()
        ctx.update(self.get_nav_context(self.object))
        return ctx


class AulaApostilaView(ProfessorRequiredMixin, AulaMixin, DetailView):
    """Exporta uma aula como apostila HTML standalone para o professor."""

    template_name = "aulas/apostila.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(
            Aula.objects.select_related("turma"),
            pk=self.kwargs["aula_pk"],
            turma=self.turma,
            gera_apostila=True,
        )

    def get_context_data(self, **kwargs):
        return _build_apostila_context(self.object)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.request.GET.get("download") == "1":
            return _set_apostila_download_header(response, self.object)
        return response


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

        _max_md = 5 * 1024 * 1024  # 5 MB
        if arquivo.size > _max_md:
            messages.error(request, "Arquivo muito grande. Máximo permitido: 5 MB.")
            return render(request, "aulas/importar_md.html", {"turma": self.turma})

        conteudo = arquivo.read().decode("utf-8", errors="replace")

        # Extrair título do primeiro H1
        match = re.search(r"^#\s+(.+)$", conteudo, re.MULTILINE)
        if match:
            titulo = match.group(1).strip()
        else:
            titulo = arquivo.name.removesuffix(".md")

        proximo_numero = (
            self.turma.aulas.order_by("-numero").values_list("numero", flat=True).first()
            or 0
        ) + 1
        aula = Aula.objects.create(
            turma=self.turma,
            titulo=titulo,
            conteudo=conteudo,
            numero=proximo_numero,
            ordem=proximo_numero,
        )
        logger.info(f"Aula importada de .md: '{titulo}' na turma pk={self.turma.pk}")
        messages.success(request, f'Aula "{titulo}" importada com sucesso.')
        return redirect("turmas:aulas_editar", pk=self.turma.pk, aula_pk=aula.pk)


class AulasSincronizarGithubView(ProfessorRequiredMixin, AulaMixin, View):
    """Sincroniza as aulas de uma turma com o repositório GitHub ProfToniCoimbra."""

    def post(self, request, pk):
        from .github_sync import build_lessons_index, fetch_manifest, get_subject_from_codigo, sync_turma

        subject = get_subject_from_codigo(self.turma.codigo)
        if not subject:
            messages.error(
                request,
                f"A turma {self.turma.codigo} não tem mapeamento no GitHub. "
                "Verifique o código da turma.",
            )
            return redirect("turmas:aulas_lista", pk=self.turma.pk)

        try:
            manifest = fetch_manifest()
            lessons_index = build_lessons_index(manifest)
            resultado = sync_turma(self.turma, lessons_index)
        except Exception as exc:
            logger.exception(
                "Falha ao sincronizar turma pk=%s codigo=%s subject=%s",
                self.turma.pk, self.turma.codigo, subject,
            )
            messages.error(
                request,
                f"Erro durante a sincronização ({type(exc).__name__}): {exc}",
            )
            return redirect("turmas:aulas_lista", pk=self.turma.pk)

        total = resultado["criadas"] + resultado["atualizadas"]
        msg = (
            f"Sincronização concluída: {resultado['criadas']} aulas novas, "
            f"{resultado['atualizadas']} atualizadas."
        )
        if resultado["erros"]:
            msg += f" ({resultado['erros']} erros — veja os logs.)"
        if total == 0 and resultado["erros"] == 0:
            msg = "Tudo já estava atualizado. Nenhuma alteração necessária."

        messages.success(request, msg)
        return redirect("turmas:aulas_lista", pk=self.turma.pk)


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
        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "aulas/_aula_item.html",
                {
                    "turma": self.turma,
                    "aula": aula,
                },
            )
        return redirect("turmas:aulas_lista", pk=self.turma.pk)


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
        return get_object_or_404(
            Aula,
            pk=self.kwargs["aula_pk"],
            turma=self.turma,
            realizada=True,
        )

    def _build_aula_url(self, aula_pk):
        return reverse(
            "turmas:portal_aulas_detalhe",
            kwargs={"token": self.turma.token_publico, "aula_pk": aula_pk},
        )

    def get_nav_queryset(self):
        return Aula.objects.filter(turma=self.turma, realizada=True).order_by("ordem", "numero")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["back_url"] = reverse_lazy(
            "turmas:portal_aulas_lista", kwargs={"token": self.turma.token_publico}
        )
        ctx["back_label"] = "Aulas"
        ctx["is_admin_view"] = False
        ctx["edit_url"] = None
        ctx["atividades_url"] = reverse(
            "turmas:portal_atividades_lista",
            kwargs={"token": self.turma.token_publico},
        )
        ctx["sidebar_aulas"] = self.get_sidebar_aulas()
        ctx.update(self.get_nav_context(self.object))
        return ctx


class AulaApostilaPublicaView(TurmaPublicaMixin, DetailView):
    """Exporta apostila pública apenas para aulas já publicadas."""

    template_name = "aulas/apostila.html"
    context_object_name = "aula"

    def get_object(self):
        return get_object_or_404(
            Aula.objects.select_related("turma"),
            pk=self.kwargs["aula_pk"],
            turma=self.turma,
            realizada=True,
            gera_apostila=True,
        )

    def get_context_data(self, **kwargs):
        return _build_apostila_context(self.object)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.request.GET.get("download") == "1":
            return _set_apostila_download_header(response, self.object)
        return response
