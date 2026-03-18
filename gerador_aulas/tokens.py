"""
Controle de consumo de tokens e estimativa de custos — ProfessorDash

Suporta todos os modelos via OpenRouter.
Tabela de preços atualizada: Março 2026.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# ── Tabela de preços por modelo (USD por 1M tokens) ───────────────────────────
# Fonte: openrouter.ai/models — atualizar periodicamente

PRECOS_MODELOS = {
    # Anthropic
    'anthropic/claude-sonnet-4-5': {
        'input':  3.00,
        'output': 15.00,
        'nome':   'Claude Sonnet 4.5',
    },
    'anthropic/claude-haiku-4-5': {
        'input':  0.80,
        'output': 4.00,
        'nome':   'Claude Haiku 4.5',
    },
    'anthropic/claude-opus-4-5': {
        'input':  15.00,
        'output': 75.00,
        'nome':   'Claude Opus 4.5',
    },
    # Google
    'google/gemini-2.5-pro': {
        'input':  1.25,
        'output': 5.00,
        'nome':   'Gemini 2.5 Pro',
    },
    'google/gemini-2.5-flash': {
        'input':  0.075,
        'output': 0.30,
        'nome':   'Gemini 2.5 Flash',  # melhor custo-benefício
    },
    # OpenAI
    'openai/gpt-4o': {
        'input':  2.50,
        'output': 10.00,
        'nome':   'GPT-4o',
    },
    'openai/gpt-4o-mini': {
        'input':  0.15,
        'output': 0.60,
        'nome':   'GPT-4o Mini',
    },
    # Meta (via OpenRouter — gratuito com limites)
    'meta-llama/llama-3.3-70b-instruct': {
        'input':  0.00,
        'output': 0.00,
        'nome':   'Llama 3.3 70B (gratuito)',
    },
}

# Modelo padrão caso não encontre na tabela
PRECO_PADRAO = {'input': 3.00, 'output': 15.00, 'nome': 'Desconhecido'}


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class UsoTokens:
    """Registra o uso de tokens de uma única chamada à API."""
    modelo:         str
    tokens_input:   int
    tokens_output:  int
    custo_usd:      Decimal = Decimal('0')
    sessao_id:      Optional[int] = None
    aula_numero:    Optional[int] = None

    def __post_init__(self):
        if not self.custo_usd:
            self.custo_usd = calcular_custo(
                self.modelo, self.tokens_input, self.tokens_output
            )

    @property
    def tokens_total(self) -> int:
        return self.tokens_input + self.tokens_output

    @property
    def custo_brl(self) -> Decimal:
        """Converte para BRL (taxa fixa de referência — ajuste conforme necessário)."""
        TAXA_USD_BRL = Decimal('5.80')
        return self.custo_usd * TAXA_USD_BRL

    def __str__(self):
        return (
            f'{self.modelo} | '
            f'↑{self.tokens_input:,} ↓{self.tokens_output:,} tokens | '
            f'${self.custo_usd:.4f}'
        )


@dataclass
class ResumoCustoSessao:
    """Resumo acumulado de tokens e custo de uma sessão de geração."""
    sessao_id:      int
    modelo:         str
    num_aulas:      int
    usos:           list = field(default_factory=list)

    @property
    def tokens_input_total(self) -> int:
        return sum(u.tokens_input for u in self.usos)

    @property
    def tokens_output_total(self) -> int:
        return sum(u.tokens_output for u in self.usos)

    @property
    def tokens_total(self) -> int:
        return self.tokens_input_total + self.tokens_output_total

    @property
    def custo_total_usd(self) -> Decimal:
        return sum(u.custo_usd for u in self.usos)

    @property
    def custo_por_aula_usd(self) -> Decimal:
        if not self.num_aulas:
            return Decimal('0')
        return self.custo_total_usd / self.num_aulas

    @property
    def nome_modelo(self) -> str:
        return PRECOS_MODELOS.get(self.modelo, PRECO_PADRAO)['nome']

    def adicionar(self, uso: UsoTokens):
        self.usos.append(uso)

    def para_dict(self) -> dict:
        return {
            'modelo':              self.nome_modelo,
            'num_aulas':           self.num_aulas,
            'tokens_input':        self.tokens_input_total,
            'tokens_output':       self.tokens_output_total,
            'tokens_total':        self.tokens_total,
            'custo_usd':           float(self.custo_total_usd),
            'custo_por_aula_usd':  float(self.custo_por_aula_usd),
            'detalhes_por_aula':   [
                {
                    'aula':    u.aula_numero,
                    'input':   u.tokens_input,
                    'output':  u.tokens_output,
                    'custo':   float(u.custo_usd),
                }
                for u in self.usos
            ],
        }

    def __str__(self):
        return (
            f'Sessão {self.sessao_id} | {self.nome_modelo} | '
            f'{self.num_aulas} aulas | '
            f'{self.tokens_total:,} tokens | '
            f'${self.custo_total_usd:.4f} USD'
        )


# ── Funções de cálculo ─────────────────────────────────────────────────────────

def calcular_custo(modelo: str, tokens_input: int, tokens_output: int) -> Decimal:
    """
    Calcula o custo em USD com base no modelo e tokens usados.
    Preço: USD por 1 milhão de tokens.
    """
    preco = PRECOS_MODELOS.get(modelo, PRECO_PADRAO)

    custo_input  = Decimal(str(preco['input']))  * Decimal(tokens_input)  / Decimal('1_000_000')
    custo_output = Decimal(str(preco['output'])) * Decimal(tokens_output) / Decimal('1_000_000')

    return (custo_input + custo_output).quantize(Decimal('0.000001'))


def estimar_custo(modelo: str, texto_entrada: str, num_aulas: int = 1) -> dict:
    """
    Estima o custo ANTES de gerar, baseado no texto de entrada.
    Útil para mostrar ao professor antes de confirmar a geração.

    Regra empírica:
      - ~1 token ≈ 4 caracteres em inglês / ~3 em português
      - Output estimado: ~2.500 tokens por aula (padrão 15 seções)
    """
    CHARS_POR_TOKEN    = 3.5
    TOKENS_OUTPUT_AULA = 2500

    tokens_input_estimados  = int(len(texto_entrada) / CHARS_POR_TOKEN)
    tokens_output_estimados = TOKENS_OUTPUT_AULA * num_aulas

    custo = calcular_custo(modelo, tokens_input_estimados, tokens_output_estimados)
    preco = PRECOS_MODELOS.get(modelo, PRECO_PADRAO)

    return {
        'modelo':           preco['nome'],
        'tokens_input_est': tokens_input_estimados,
        'tokens_output_est': tokens_output_estimados,
        'tokens_total_est': tokens_input_estimados + tokens_output_estimados,
        'custo_usd_est':    float(custo),
        'aviso':            'Estimativa aproximada. Custo real pode variar ±30%.',
    }


def registrar_uso_na_sessao(sessao, uso: UsoTokens) -> None:
    """
    Atualiza os campos de tokens e custo na SessaoGeracao do Django.

    Uso:
        uso = UsoTokens(modelo='anthropic/claude-sonnet-4-5',
                        tokens_input=1200, tokens_output=2800)
        registrar_uso_na_sessao(sessao, uso)
    """
    sessao.tokens_usados  = (sessao.tokens_usados  or 0) + uso.tokens_total
    sessao.custo_estimado = (sessao.custo_estimado or 0) + uso.custo_usd
    sessao.save(update_fields=['tokens_usados', 'custo_estimado'])
    logger.info(f'Sessão {sessao.id} | {uso}')


def montar_resumo_da_sessao(sessao) -> ResumoCustoSessao:
    """Monta o ResumoCustoSessao a partir de uma SessaoGeracao do banco."""
    return ResumoCustoSessao(
        sessao_id=sessao.id,
        modelo=sessao.provider,
        num_aulas=sessao.num_aulas,
    )


# ── Extração de tokens da resposta OpenRouter ─────────────────────────────────

def extrair_uso_da_resposta(resposta, modelo: str,
                             sessao_id: int = None,
                             aula_numero: int = None) -> UsoTokens:
    """
    Extrai tokens da resposta da API (compatível com formato OpenAI/OpenRouter).

    Uso após chamar client.chat.completions.create():
        uso = extrair_uso_da_resposta(resposta, modelo='anthropic/claude-sonnet-4-5')
    """
    usage = getattr(resposta, 'usage', None)

    if usage:
        tokens_input  = getattr(usage, 'prompt_tokens',     0)
        tokens_output = getattr(usage, 'completion_tokens', 0)
    else:
        # Fallback: estima pelo tamanho do conteúdo
        conteudo = resposta.choices[0].message.content or ''
        tokens_output = int(len(conteudo) / 3.5)
        tokens_input  = 0
        logger.warning('usage não disponível na resposta — tokens estimados.')

    return UsoTokens(
        modelo=modelo,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        sessao_id=sessao_id,
        aula_numero=aula_numero,
    )


# ── Modelos recomendados ───────────────────────────────────────────────────────

def recomendar_modelo(num_aulas: int, prioridade: str = 'qualidade') -> str:
    """
    Sugere o melhor modelo baseado na quantidade de aulas e prioridade.

    prioridade:
        'qualidade'  → melhor resultado pedagógico
        'custo'      → mais barato
        'equilibrio' → bom custo-benefício
    """
    if prioridade == 'qualidade':
        return 'anthropic/claude-sonnet-4-5'

    if prioridade == 'custo':
        if num_aulas > 10:
            return 'google/gemini-2.5-flash'   # muito barato para lotes grandes
        return 'meta-llama/llama-3.3-70b-instruct'  # gratuito

    # equilibrio
    if num_aulas <= 3:
        return 'anthropic/claude-sonnet-4-5'
    return 'google/gemini-2.5-pro'


def listar_modelos_disponiveis() -> list:
    """Retorna lista de modelos para popular o dropdown da interface."""
    return [
        {
            'id':    modelo_id,
            'nome':  info['nome'],
            'input': info['input'],
            'output': info['output'],
            'gratuito': info['input'] == 0.0,
        }
        for modelo_id, info in PRECOS_MODELOS.items()
    ]
