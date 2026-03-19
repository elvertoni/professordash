"""
Views do Gerador de Aulas — ProfessorDash (Admin Only)

Todas as views requerem ProfessorRequiredMixin (is_staff=True).
"""

import json
import logging

from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView

from core.mixins import ProfessorRequiredMixin
from turmas.models import Turma

from .extractors import extrair_arquivo
from .extractors.rco import montar_conjunto_de_uploads, extrair_rco, montar_conteudo_rco
from .models import MaterialEntrada, SessaoGeracao
from .pipeline import executar_modo_rco, executar_modo_livre, juntar_conteudo
from .prompts import SYSTEM_PROMPT, prompt_planejar
from .providers import gerar_planejamento, validar_planejamento

logger = logging.getLogger(__name__)


def _parse_num_aulas(valor: str | None) -> int:
    """Normaliza o campo num_aulas para evitar ValueError em POST inválido."""
    try:
        num_aulas = int(valor or 1)
    except (TypeError, ValueError) as exc:
        raise ValueError("Informe um número de aulas válido.") from exc

    if num_aulas < 1 or num_aulas > 20:
        raise ValueError("O número de aulas deve estar entre 1 e 20.")

    return num_aulas


def _gerar_planejamento_para_sessao(sessao: SessaoGeracao) -> None:
    """Gera e persiste o planejamento da sessão no modo livre."""
    conteudo = juntar_conteudo(sessao.materiais.all())
    user_prompt = prompt_planejar(
        conteudo=conteudo,
        num_aulas=sessao.num_aulas,
        disciplina=sessao.disciplina.nome,
        nivel=sessao.nivel,
        foco=sessao.foco,
        instrucoes=sessao.instrucoes,
    )

    sessao.status = "planejando"
    sessao.save(update_fields=["status"])

    planejamento, uso = gerar_planejamento(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        provider=sessao.provider,
    )

    from .tokens import registrar_uso_na_sessao

    registrar_uso_na_sessao(sessao, uso)

    sessao.planejamento = planejamento
    sessao.status = "rascunho"
    sessao.save(update_fields=["planejamento", "status"])


# ── Tela principal ────────────────────────────────────────────────────────────

class GeradorIndexView(ProfessorRequiredMixin, TemplateView):
    """
    GET /painel/gerador/
    Exibe o formulário principal com seleção de modo (RCO ou Livre).
    """
    template_name = "gerador/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turmas"] = Turma.objects.filter(ativa=True).order_by("nome")
        return ctx


# ── Upload e extração de materiais ────────────────────────────────────────────

class UploadMaterialView(ProfessorRequiredMixin, View):
    """
    POST /painel/gerador/upload/

    Recebe arquivos, extrai o conteúdo, cria SessaoGeracao e MaterialEntrada.
    Redireciona para o fluxo correto conforme o modo:
      - RCO:   vai direto para /painel/gerador/<id>/gerar/
      - Livre: vai para /painel/gerador/<id>/planejar/ (análise do material)
    """

    def post(self, request):
        modo = request.POST.get("modo", "rco")
        turma_id = request.POST.get("turma")
        nivel = request.POST.get("nivel", "tecnico")
        foco = request.POST.get("foco", "equilibrado")
        provider = request.POST.get("provider", "claude")
        instrucoes = request.POST.get("instrucoes", "")

        try:
            num_aulas = _parse_num_aulas(request.POST.get("num_aulas"))
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("gerador:index")

        if not turma_id:
            messages.error(request, "Selecione uma turma antes de gerar a aula.")
            return redirect("gerador:index")

        turma = get_object_or_404(Turma, pk=turma_id)

        sessao = SessaoGeracao.objects.create(
            disciplina=turma,
            modo=modo,
            num_aulas=num_aulas,
            nivel=nivel,
            foco=foco,
            provider=provider,
            instrucoes=instrucoes,
            status="rascunho",
        )

        try:
            if modo == "rco":
                self._processar_rco(request, sessao)
                return redirect("gerador:gerar", sessao_id=sessao.id)

            self._processar_livre(request, sessao)
            _gerar_planejamento_para_sessao(sessao)
            return redirect("gerador:planejar", sessao_id=sessao.id)
        except Exception as e:
            sessao.status = "erro"
            sessao.save(update_fields=["status"])
            logger.exception("Erro ao iniciar sessão do gerador %s", sessao.id)
            messages.error(request, f"Não foi possível iniciar a geração: {e}")
            return redirect("gerador:index")

    def _processar_rco(self, request, sessao):
        """Detecta papéis RCO, extrai conteúdo e persiste MaterialEntrada."""
        conjunto = montar_conjunto_de_uploads(request.FILES)
        extracao = extrair_rco(conjunto)
        conteudo = montar_conteudo_rco(extracao)

        papel_arquivo = {
            "slides":    (conjunto.slides,    "pptx"),
            "atividade": (conjunto.atividade, "docx"),
            "pratica":   (conjunto.pratica,   "docx"),
        }
        for papel, (arquivo, tipo) in papel_arquivo.items():
            if arquivo:
                arquivo.seek(0)
                MaterialEntrada.objects.create(
                    sessao            = sessao,
                    tipo              = tipo,
                    papel_rco         = papel,
                    arquivo           = arquivo,
                    conteudo_extraido = conteudo.get(papel, ""),
                )

    def _processar_livre(self, request, sessao):
        """Extrai conteúdo de múltiplos arquivos/URLs/texto e persiste MaterialEntrada."""
        ordem = 0

        # Arquivos
        for arquivo in request.FILES.getlist("arquivos"):
            resultado = extrair_arquivo(arquivo, arquivo.name)
            arquivo.seek(0)
            MaterialEntrada.objects.create(
                sessao            = sessao,
                tipo              = resultado.tipo.value,
                arquivo           = arquivo,
                conteudo_extraido = resultado.conteudo,
                ordem             = ordem,
            )
            ordem += 1

        # URLs
        for url in request.POST.getlist("urls"):
            url = url.strip()
            if not url:
                continue
            from .extractors.url import extrair_url
            resultado = extrair_url(url)
            MaterialEntrada.objects.create(
                sessao            = sessao,
                tipo              = "url",
                url               = url,
                conteudo_extraido = resultado.conteudo,
                ordem             = ordem,
            )
            ordem += 1

        # Texto livre
        texto_livre = request.POST.get("texto_livre", "").strip()
        if texto_livre:
            MaterialEntrada.objects.create(
                sessao            = sessao,
                tipo              = "texto",
                texto_livre       = texto_livre,
                conteudo_extraido = texto_livre,
                ordem             = ordem,
            )


# ── Planejamento (Modo Livre) ─────────────────────────────────────────────────

class PlanejarView(ProfessorRequiredMixin, View):
    """
    GET  /painel/gerador/<id>/planejar/  → exibe tela de planejamento com proposta da IA
    POST /painel/gerador/planejar/       → chama LLM para gerar o planejamento
    """

    def get(self, request, sessao_id):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)
        if sessao.modo == "livre" and not sessao.planejamento:
            try:
                _gerar_planejamento_para_sessao(sessao)
            except Exception as e:
                sessao.status = "erro"
                sessao.save(update_fields=["status"])
                logger.exception("Erro ao gerar planejamento na sessão %s", sessao.id)
                messages.error(request, f"Não foi possível analisar o material: {e}")
                return redirect("gerador:index")
        return render(request, "gerador/planejamento.html", {"sessao": sessao})

    def post(self, request):
        """Recebe sessao_id, chama LLM para planejar e salva o JSON no banco."""
        sessao_id = request.POST.get("sessao_id")
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)

        try:
            _gerar_planejamento_para_sessao(sessao)
        except Exception as e:
            sessao.status = "erro"
            sessao.save(update_fields=["status"])
            logger.exception("Erro no planejamento da sessão %s", sessao.id)
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"erro": str(e)}, status=500)
            messages.error(request, f"Não foi possível analisar o material: {e}")
            return redirect("gerador:index")

        return redirect("gerador:planejar", sessao_id=sessao.id)


# ── Aprovação do planejamento ─────────────────────────────────────────────────

class AprovarPlanejamentoView(ProfessorRequiredMixin, View):
    """
    POST /painel/gerador/<id>/aprovar/

    Recebe o planejamento editado pelo professor (títulos ajustados),
    salva no banco e redireciona para a geração em lote.
    """

    def post(self, request, sessao_id):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)
        planejamento = sessao.planejamento or {}
        aulas = planejamento.get("aulas", [])

        # Atualiza títulos editados pelo professor
        for i, aula in enumerate(aulas):
            novo_titulo = request.POST.get(f"titulo_{aula['numero']}", "").strip()
            if novo_titulo:
                aulas[i]["titulo"] = novo_titulo

        planejamento["aulas"] = aulas

        try:
            validar_planejamento(planejamento)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("gerador:planejar", sessao_id=sessao.id)

        sessao.planejamento = planejamento
        sessao.save(update_fields=["planejamento"])

        return redirect("gerador:gerar", sessao_id=sessao.id)


# ── Geração com SSE ───────────────────────────────────────────────────────────

class GerarAulasView(ProfessorRequiredMixin, View):
    """
    GET /painel/gerador/<id>/gerar/

    Inicia a geração e envia progresso via Server-Sent Events (SSE).
    O frontend conecta com EventSource e atualiza o progress bar.

    Formato dos eventos:
        data: {"aula": 3, "total": 10}            ← progresso
        data: {"status": "concluido", "total": 10} ← fim
        data: {"status": "erro", "mensagem": "..."}← erro
    """

    def get(self, request, sessao_id):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)

        # Se já está na tela de progresso (não SSE), apenas renderiza o template
        if not request.headers.get("Accept", "").startswith("text/event-stream"):
            total = (
                len(sessao.planejamento.get("aulas", []))
                if sessao.planejamento
                else 1
            )
            return render(request, "gerador/gerando.html", {
                "sessao": sessao,
                "total": total,
            })

        return StreamingHttpResponse(
            self._stream(sessao),
            content_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # desativa buffer do Nginx
            },
        )

    def _stream(self, sessao):
        def _evento(dados: dict) -> str:
            return f"data: {json.dumps(dados, ensure_ascii=False)}\n\n"

        try:
            if sessao.modo == "rco":
                executar_modo_rco(sessao)
                yield _evento({"aula": 1, "total": 1, "status": "concluido"})
            else:
                total = len(sessao.planejamento.get("aulas", []))
                for numero in executar_modo_livre(sessao):
                    yield _evento({"aula": numero, "total": total})
                yield _evento({"status": "concluido", "total": total})

        except Exception as e:
            yield _evento({"status": "erro", "mensagem": str(e)})


# ── Preview de aula gerada ────────────────────────────────────────────────────

class PreviewAulaView(ProfessorRequiredMixin, View):
    """
    GET /painel/gerador/<id>/preview/<n>/

    Exibe o conteúdo da aula N gerada nesta sessão.
    """

    def get(self, request, sessao_id, numero):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)
        from aulas.models import Aula
        aula = get_object_or_404(Aula, turma=sessao.disciplina, numero=numero)
        return render(request, "gerador/preview.html", {
            "sessao": sessao,
            "aula":   aula,
        })


# ── Salvar/publicar rascunhos ─────────────────────────────────────────────────

class SalvarAulasView(ProfessorRequiredMixin, View):
    """
    POST /painel/gerador/<id>/salvar/

    Confirma as aulas geradas (já salvas como rascunho).
    Redireciona para a listagem de aulas da turma.
    """

    def post(self, request, sessao_id):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)
        # Aulas já estão salvas — apenas redireciona para a turma
        return redirect("turmas:detalhe", pk=sessao.disciplina.pk)


# ── Histórico de sessões ──────────────────────────────────────────────────────

class HistoricoView(ProfessorRequiredMixin, ListView):
    """
    GET /painel/gerador/historico/

    Lista todas as sessões de geração anteriores, mais recentes primeiro.
    """
    model = SessaoGeracao
    template_name = "gerador/historico.html"
    context_object_name = "sessoes"
    paginate_by = 20

    def get_queryset(self):
        return (
            SessaoGeracao.objects
            .select_related("disciplina")
            .order_by("-criado_em")
        )
