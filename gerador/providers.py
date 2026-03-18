"""
Provider de IA via OpenRouter — ProfessorDash Gerador de Aulas

OpenRouter é compatível com o SDK OpenAI (mesmo protocolo).
Suporta Claude, Gemini e GPT-4o em um único endpoint.
"""

import json
import logging

from django.conf import settings

from gerador.tokens import UsoTokens, extrair_uso_da_resposta

logger = logging.getLogger(__name__)


# ── Mapa de modelos ───────────────────────────────────────────────────────────

MODELOS = {
    "claude": "anthropic/claude-sonnet-4-5",
    "gemini": "google/gemini-2.5-pro",
    "gpt4o":  "openai/gpt-4o",
}

PROVIDER_PADRAO = "claude"


def _get_client():
    """Retorna cliente OpenRouter configurado com a API key do settings."""
    from openai import OpenAI  # lazy — não bloqueia o startup se não instalado

    api_key = getattr(settings, "OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY não configurada. "
            "Adicione ao .env: OPENROUTER_API_KEY=sk-or-..."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


# ── Geração de aula ───────────────────────────────────────────────────────────

def gerar_aula(
    system: str,
    user: str,
    provider: str = PROVIDER_PADRAO,
    max_tokens: int = 4096,
    sessao_id: int = None,
    aula_numero: int = None,
) -> tuple[str, UsoTokens]:
    """
    Chama o LLM via OpenRouter e retorna o conteúdo Markdown da aula gerada.

    Retorna:
        (conteudo_markdown, uso_tokens)

    Uso:
        markdown, uso = gerar_aula(SYSTEM_PROMPT, prompt_rco(...), provider='claude')
        print(markdown)
        print(uso)  # 'anthropic/claude-sonnet-4-5 | ↑1200 ↓2800 tokens | $0.0450'
    """
    modelo_id = MODELOS.get(provider)
    if not modelo_id:
        providers_validos = ", ".join(MODELOS.keys())
        raise ValueError(
            f"Provider '{provider}' inválido. Use: {providers_validos}"
        )

    client = _get_client()

    logger.info(f"Gerando aula via {modelo_id} | sessão={sessao_id} aula={aula_numero}")

    resposta = client.chat.completions.create(
        model=modelo_id,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        max_tokens=max_tokens,
    )

    conteudo = resposta.choices[0].message.content or ""
    uso = extrair_uso_da_resposta(
        resposta,
        modelo=modelo_id,
        sessao_id=sessao_id,
        aula_numero=aula_numero,
    )

    logger.info(f"Geração concluída | {uso}")
    return conteudo, uso


# ── Planejamento (Modo Livre) ─────────────────────────────────────────────────

def gerar_planejamento(
    system: str,
    user: str,
    provider: str = PROVIDER_PADRAO,
) -> tuple[dict, UsoTokens]:
    """
    Chama o LLM para gerar o planejamento de aulas (resposta JSON).
    Valida e retorna o dict estruturado.

    Retorna:
        (planejamento_dict, uso_tokens)

    Levanta:
        ValueError se a resposta não for JSON válido ou campos obrigatórios ausentes.
    """
    conteudo, uso = gerar_aula(
        system=system,
        user=user,
        provider=provider,
        max_tokens=2048,
    )

    planejamento = _parsear_json_planejamento(conteudo)
    return planejamento, uso


def _parsear_json_planejamento(conteudo: str) -> dict:
    """
    Extrai e valida o JSON de planejamento da resposta do LLM.

    O LLM às vezes envolve o JSON em blocos de código markdown (```json ... ```),
    então tentamos extrair o JSON de dentro do bloco se necessário.
    """
    texto = conteudo.strip()

    # Remove bloco de código markdown se presente
    if texto.startswith("```"):
        linhas = texto.split("\n")
        # Remove primeira linha (```json ou ```) e última (```)
        linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        texto = "\n".join(linhas).strip()

    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Resposta do planejamento não é JSON válido: {e}\n"
            f"Conteúdo recebido: {conteudo[:500]}"
        )

    validar_planejamento(dados)
    return dados


def validar_planejamento(dados: dict) -> None:
    """
    Valida que o dict de planejamento possui todos os campos obrigatórios.

    Campos obrigatórios:
        - tema_central (str)
        - fio_condutor (str)
        - observacoes  (str)
        - aulas        (list de dicts com 'numero' e 'titulo')

    Levanta:
        ValueError com descrição do campo faltando.
    """
    campos_obrigatorios = ["tema_central", "fio_condutor", "observacoes", "aulas"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ValueError(f"Planejamento inválido: campo obrigatório '{campo}' ausente.")

    if not isinstance(dados["aulas"], list) or len(dados["aulas"]) == 0:
        raise ValueError("Planejamento inválido: 'aulas' deve ser uma lista não vazia.")

    for i, aula in enumerate(dados["aulas"]):
        if "numero" not in aula:
            raise ValueError(f"Aula {i+1} sem campo 'numero'.")
        if "titulo" not in aula:
            raise ValueError(f"Aula {i+1} sem campo 'titulo'.")
