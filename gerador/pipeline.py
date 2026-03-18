"""
Pipeline de geração de aulas — ProfessorDash Gerador de Aulas

Orquestra o fluxo completo:
  Modo A (RCO):   extração → prompt → gerar → salvar 1 aula
  Modo B (Livre): planejamento → loop de geração → salvar N aulas via SSE
"""

import logging
import re

from gerador.extractors import extrair_arquivo
from gerador.models import MaterialEntrada, SessaoGeracao
from gerador.prompts import SYSTEM_PROMPT, prompt_aula_livre, prompt_rco
from gerador.providers import gerar_aula
from gerador.tokens import registrar_uso_na_sessao

logger = logging.getLogger(__name__)


# ── Utilitários ───────────────────────────────────────────────────────────────

def juntar_conteudo(materiais) -> str:
    """
    Concatena o conteúdo extraído de múltiplos MaterialEntrada com separadores.
    Usado no Modo Livre para montar o contexto enviado ao LLM.

    Args:
        materiais: QuerySet ou lista de MaterialEntrada

    Retorna:
        str: texto concatenado com separadores de fonte
    """
    partes = []
    for mat in materiais:
        conteudo = mat.conteudo_extraido or ""
        if not conteudo.strip():
            continue
        fonte = mat.arquivo.name if mat.arquivo else mat.url or "texto livre"
        partes.append(
            f"{'='*60}\n"
            f"FONTE: {fonte}\n"
            f"{'='*60}\n"
            f"{conteudo}"
        )
    return "\n\n".join(partes)


def extrair_titulo(markdown: str) -> str:
    """
    Extrai o título da aula gerada a partir do Markdown.
    Procura pela primeira linha de header # ou ## que não seja cabeçalho genérico.

    Args:
        markdown: conteúdo Markdown da aula gerada

    Retorna:
        str: título extraído ou "Aula Gerada" como fallback
    """
    for linha in markdown.splitlines():
        linha = linha.strip()
        match = re.match(r"^#{1,2}\s+(.+)$", linha)
        if match:
            titulo = match.group(1).strip()
            # Ignora cabeçalhos genéricos como "Cabeçalho", "Aula 1"
            if not re.match(r"^(Cabeçalho|Aula\s+\d+\s*$)", titulo, re.IGNORECASE):
                # Remove emojis se necessário (mantém texto limpo para o campo titulo)
                titulo_limpo = re.sub(r"[^\w\s\-\–\:\(\)áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ]", "", titulo).strip()
                if titulo_limpo:
                    return titulo_limpo
    return "Aula Gerada"


# ── Modo A: RCO ───────────────────────────────────────────────────────────────

def executar_modo_rco(sessao: SessaoGeracao):
    """
    Pipeline completo para o Modo RCO: lê os 3 materiais, gera 1 aula e salva.

    Args:
        sessao: SessaoGeracao com modo='rco' e materiais associados

    Retorna:
        Aula: objeto salvo no banco como rascunho (realizada=False)
    """
    from aulas.models import Aula

    sessao.status = "gerando"
    sessao.save(update_fields=["status"])

    # Lê os 3 papéis do conjunto RCO
    materiais = {m.papel_rco: m.conteudo_extraido for m in sessao.materiais.all()}

    user_prompt = prompt_rco(
        slides     = materiais.get("slides",    ""),
        atividade  = materiais.get("atividade", ""),
        pratica    = materiais.get("pratica",   ""),
        disciplina = sessao.disciplina.nome,
        numero     = sessao.num_aulas,
        nivel      = sessao.nivel,
        instrucoes = sessao.instrucoes,
    )

    try:
        markdown, uso = gerar_aula(
            system      = SYSTEM_PROMPT,
            user        = user_prompt,
            provider    = sessao.provider,
            sessao_id   = sessao.id,
            aula_numero = sessao.num_aulas,
        )
    except Exception as e:
        sessao.status = "erro"
        sessao.save(update_fields=["status"])
        logger.error(f"Erro ao gerar aula RCO (sessão {sessao.id}): {e}")
        raise

    registrar_uso_na_sessao(sessao, uso)

    titulo = extrair_titulo(markdown)

    # Trata conflito de número de aula (unique_together turma+numero)
    numero = sessao.num_aulas
    while Aula.objects.filter(turma=sessao.disciplina, numero=numero).exists():
        numero += 1

    aula = Aula.objects.create(
        turma     = sessao.disciplina,
        titulo    = titulo,
        numero    = numero,
        conteudo  = markdown,
        realizada = False,
    )

    sessao.status = "concluido"
    sessao.save(update_fields=["status"])

    logger.info(f"Aula RCO gerada: {aula} | sessão {sessao.id} | {uso}")
    return aula


# ── Modo B: Livre ─────────────────────────────────────────────────────────────

def executar_modo_livre(sessao: SessaoGeracao):
    """
    Pipeline de geração em lote para o Modo Livre.
    Gera N aulas sequencialmente, fazendo yield do número de cada aula concluída.
    Projetado para uso com SSE (Server-Sent Events).

    Args:
        sessao: SessaoGeracao com modo='livre', planejamento aprovado e materiais

    Yields:
        int: número da aula recém-concluída (para atualizar o progress bar)
    """
    from aulas.models import Aula

    conteudo    = juntar_conteudo(sessao.materiais.all())
    planejamento = sessao.planejamento.get("aulas", [])
    total       = len(planejamento)
    titulo_anterior = ""

    logger.info(f"Iniciando geração em lote: {total} aulas | sessão {sessao.id}")

    for aula_info in planejamento:
        sessao.status = "gerando"
        sessao.save(update_fields=["status"])

        user_prompt = prompt_aula_livre(
            aula           = aula_info,
            total          = total,
            conteudo       = conteudo,
            disciplina     = sessao.disciplina.nome,
            nivel          = sessao.nivel,
            foco           = sessao.foco,
            aula_anterior  = titulo_anterior,
            instrucoes     = sessao.instrucoes,
        )

        try:
            markdown, uso = gerar_aula(
                system      = SYSTEM_PROMPT,
                user        = user_prompt,
                provider    = sessao.provider,
                sessao_id   = sessao.id,
                aula_numero = aula_info["numero"],
            )
        except Exception as e:
            sessao.status = "erro"
            sessao.save(update_fields=["status"])
            logger.error(f"Erro na aula {aula_info['numero']} (sessão {sessao.id}): {e}")
            raise

        registrar_uso_na_sessao(sessao, uso)

        # Trata conflito de número de aula
        numero = aula_info["numero"]
        while Aula.objects.filter(turma=sessao.disciplina, numero=numero).exists():
            numero += 1

        Aula.objects.create(
            turma     = sessao.disciplina,
            titulo    = aula_info["titulo"],
            numero    = numero,
            conteudo  = markdown,
            realizada = False,
        )

        titulo_anterior = aula_info["titulo"]
        logger.info(f"Aula {aula_info['numero']}/{total} concluída | {uso}")

        yield aula_info["numero"]  # sinaliza progresso para SSE

    sessao.status = "concluido"
    sessao.save(update_fields=["status"])
    logger.info(f"Geração em lote concluída | sessão {sessao.id}")
