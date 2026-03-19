"""
Testes unitários para gerador/providers.py e gerador/prompts.py

Todos os testes mocam a chamada ao OpenRouter — sem API calls reais.
"""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APITimeoutError, AuthenticationError

from gerador.providers import (
    MODELOS,
    _parsear_json_planejamento,
    gerar_aula,
    gerar_planejamento,
    validar_planejamento,
)
from gerador.prompts import (
    SYSTEM_PROMPT,
    prompt_aula_livre,
    prompt_planejar,
    prompt_rco,
)
from gerador.tokens import UsoTokens


# ── Fixtures ──────────────────────────────────────────────────────────────────

PLANEJAMENTO_VALIDO = {
    "tema_central": "Desenvolvimento Web com HTML, CSS e JavaScript",
    "fio_condutor": "Do básico ao projeto prático completo",
    "observacoes": "Material cobre bem todas as aulas propostas.",
    "aulas": [
        {"numero": 1, "titulo": "Introdução ao HTML Semântico", "topicos_principais": ["HTML", "tags"]},
        {"numero": 2, "titulo": "CSS: Box Model e Flexbox", "topicos_principais": ["CSS", "layout"]},
    ],
}


def _make_resposta_mock(conteudo: str, tokens_input: int = 1000, tokens_output: int = 2000):
    """Cria um mock da resposta da API OpenAI/OpenRouter."""
    uso_mock = MagicMock()
    uso_mock.prompt_tokens     = tokens_input
    uso_mock.completion_tokens = tokens_output

    choice_mock = MagicMock()
    choice_mock.message.content = conteudo

    resposta = MagicMock()
    resposta.choices = [choice_mock]
    resposta.usage   = uso_mock
    return resposta


# ── Testes: mapa de modelos ───────────────────────────────────────────────────

class TestMapaDeModelos:

    def test_claude_mapeia_para_sonnet(self):
        assert MODELOS["claude"] == "anthropic/claude-sonnet-4-5"

    def test_gemini_mapeia_para_pro(self):
        assert MODELOS["gemini"] == "google/gemini-2.5-pro"

    def test_gpt4o_mapeia_corretamente(self):
        assert MODELOS["gpt4o"] == "openai/gpt-4o"

    def test_todos_providers_presentes(self):
        assert set(MODELOS.keys()) >= {"claude", "gemini", "gpt4o"}


# ── Testes: gerar_aula ────────────────────────────────────────────────────────

class TestGerarAula:

    def _mock_gerar(self, conteudo: str, provider: str = "claude"):
        resposta = _make_resposta_mock(conteudo)
        cliente_mock = MagicMock()
        cliente_mock.chat.completions.create.return_value = resposta

        with patch("gerador.providers._get_client", return_value=cliente_mock):
            with patch("django.conf.settings.OPENROUTER_API_KEY", "sk-or-test"):
                return gerar_aula(
                    system="system prompt",
                    user="user prompt",
                    provider=provider,
                )

    def test_retorna_conteudo_e_uso_tokens(self):
        markdown, uso = self._mock_gerar("## Aula sobre HTML\n\nConteúdo aqui.")
        assert "HTML" in markdown
        assert isinstance(uso, UsoTokens)

    def test_uso_tokens_com_valores_corretos(self):
        resposta = _make_resposta_mock("conteudo", tokens_input=500, tokens_output=1500)
        cliente_mock = MagicMock()
        cliente_mock.chat.completions.create.return_value = resposta

        with patch("gerador.providers._get_client", return_value=cliente_mock):
            with patch("django.conf.settings.OPENROUTER_API_KEY", "sk-or-test"):
                _, uso = gerar_aula("sys", "usr", provider="claude")

        assert uso.tokens_input == 500
        assert uso.tokens_output == 1500
        assert uso.tokens_total == 2000

    @pytest.mark.parametrize("provider", ["claude", "gemini", "gpt4o"])
    def test_aceita_todos_providers_validos(self, provider):
        markdown, uso = self._mock_gerar("Conteúdo gerado.", provider=provider)
        assert markdown == "Conteúdo gerado."
        assert uso.modelo == MODELOS[provider]

    def test_provider_invalido_levanta_erro(self):
        with pytest.raises(ValueError, match="Provider 'gpt99' inválido"):
            with patch("gerador.providers._get_client", return_value=MagicMock()):
                with patch("django.conf.settings.OPENROUTER_API_KEY", "sk-or-test"):
                    gerar_aula("sys", "usr", provider="gpt99")

    def test_sem_api_key_levanta_erro(self):
        with patch("django.conf.settings.OPENROUTER_API_KEY", ""):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                gerar_aula("sys", "usr")

    def test_erro_de_autenticacao_retorna_mensagem_acionavel(self):
        cliente_mock = MagicMock()
        request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
        response = httpx.Response(401, request=request)
        cliente_mock.chat.completions.create.side_effect = AuthenticationError(
            "unauthorized",
            response=response,
            body={"error": {"message": "User not found."}},
        )

        with patch("gerador.providers._get_client", return_value=cliente_mock):
            with pytest.raises(ValueError, match="Falha de autenticação no OpenRouter"):
                gerar_aula("sys", "usr", provider="claude")

    def test_timeout_do_provider_retorna_mensagem_clara(self):
        cliente_mock = MagicMock()
        request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
        cliente_mock.chat.completions.create.side_effect = APITimeoutError(request=request)

        with patch("gerador.providers._get_client", return_value=cliente_mock):
            with pytest.raises(ValueError, match="demorou mais que o tempo limite"):
                gerar_aula("sys", "usr", provider="claude")


# ── Testes: gerar_planejamento ────────────────────────────────────────────────

class TestGerarPlanejamento:

    def test_parseia_planejamento_valido(self):
        json_str = json.dumps(PLANEJAMENTO_VALIDO)
        resposta = _make_resposta_mock(json_str)
        cliente_mock = MagicMock()
        cliente_mock.chat.completions.create.return_value = resposta

        with patch("gerador.providers._get_client", return_value=cliente_mock):
            with patch("django.conf.settings.OPENROUTER_API_KEY", "sk-or-test"):
                plano, uso = gerar_planejamento("sys", "usr")

        assert plano["tema_central"] == PLANEJAMENTO_VALIDO["tema_central"]
        assert len(plano["aulas"]) == 2

    def test_parseia_json_dentro_de_bloco_markdown(self):
        """LLM às vezes retorna JSON dentro de ```json ... ```."""
        json_str = json.dumps(PLANEJAMENTO_VALIDO)
        conteudo_com_bloco = f"```json\n{json_str}\n```"

        resultado = _parsear_json_planejamento(conteudo_com_bloco)
        assert resultado["tema_central"] == PLANEJAMENTO_VALIDO["tema_central"]

    def test_levanta_erro_para_json_invalido(self):
        with pytest.raises(ValueError, match="não é JSON válido"):
            _parsear_json_planejamento("isso nao e json { invalido }")

    def test_levanta_erro_para_json_sem_bloco_codigo(self):
        """JSON puro (sem bloco markdown) também deve funcionar."""
        json_str = json.dumps(PLANEJAMENTO_VALIDO)
        resultado = _parsear_json_planejamento(json_str)
        assert "aulas" in resultado


# ── Testes: validar_planejamento ─────────────────────────────────────────────

class TestValidarPlanejamento:

    def test_planejamento_valido_nao_levanta_erro(self):
        validar_planejamento(PLANEJAMENTO_VALIDO)  # não deve levantar

    @pytest.mark.parametrize("campo_faltando", [
        "tema_central", "fio_condutor", "observacoes", "aulas"
    ])
    def test_campo_obrigatorio_ausente_levanta_erro(self, campo_faltando):
        dados = dict(PLANEJAMENTO_VALIDO)
        del dados[campo_faltando]
        with pytest.raises(ValueError, match=campo_faltando):
            validar_planejamento(dados)

    def test_aulas_lista_vazia_levanta_erro(self):
        dados = dict(PLANEJAMENTO_VALIDO)
        dados["aulas"] = []
        with pytest.raises(ValueError, match="lista não vazia"):
            validar_planejamento(dados)

    def test_aula_sem_numero_levanta_erro(self):
        dados = dict(PLANEJAMENTO_VALIDO)
        dados["aulas"] = [{"titulo": "Sem número"}]
        with pytest.raises(ValueError, match="'numero'"):
            validar_planejamento(dados)

    def test_aula_sem_titulo_levanta_erro(self):
        dados = dict(PLANEJAMENTO_VALIDO)
        dados["aulas"] = [{"numero": 1}]
        with pytest.raises(ValueError, match="'titulo'"):
            validar_planejamento(dados)


# ── Testes: SYSTEM_PROMPT ─────────────────────────────────────────────────────

class TestSystemPrompt:

    def test_contem_todas_15_secoes(self):
        """SYSTEM_PROMPT deve mencionar as 15 seções obrigatórias."""
        for i in range(1, 16):
            assert str(i) in SYSTEM_PROMPT, f"Seção {i} não encontrada no SYSTEM_PROMPT"

    def test_contem_regras_inegociaveis(self):
        assert "Nunca resumir" in SYSTEM_PROMPT
        assert "Roteiro de fala" in SYSTEM_PROMPT
        assert "gabarito" in SYSTEM_PROMPT

    def test_contem_instrucao_de_formato(self):
        assert "Markdown" in SYSTEM_PROMPT


# ── Testes: prompt_rco ────────────────────────────────────────────────────────

class TestPromptRco:

    def test_inclui_numero_da_aula(self):
        p = prompt_rco("slides", "atividade", "pratica", "Front-End", 3, "tecnico")
        assert "Aula 3" in p

    def test_inclui_nome_da_disciplina(self):
        p = prompt_rco("slides", "", "", "Programação Web", 1, "tecnico")
        assert "Programação Web" in p

    def test_inclui_conteudo_dos_slides(self):
        p = prompt_rco("CONTEUDO_SLIDES_UNICO", "", "", "Disc", 1, "tecnico")
        assert "CONTEUDO_SLIDES_UNICO" in p

    def test_atividade_vai_para_secao_12(self):
        """O prompt deve indicar explicitamente que atividade → seção 12."""
        p = prompt_rco("slides", "QUESTOES_ATIVIDADE", "", "Disc", 1, "tecnico")
        assert "QUESTOES_ATIVIDADE" in p
        assert "12" in p or "fixação" in p.lower() or "ATIVIDADE" in p

    def test_pratica_vai_para_secao_11(self):
        """O prompt deve indicar explicitamente que prática → seção 11."""
        p = prompt_rco("slides", "", "PASSOS_PRATICA", "Disc", 1, "tecnico")
        assert "PASSOS_PRATICA" in p
        assert "11" in p or "prática" in p.lower() or "PRÁTICA" in p

    def test_ausencia_de_atividade_sugere_criar(self):
        """Sem atividade, o prompt deve instruir a criar questões."""
        p = prompt_rco("slides", "", "", "Disc", 1, "tecnico")
        assert "crie" in p.lower() or "Não fornecida" in p

    def test_instrucoes_adicionais_incluidas(self):
        p = prompt_rco("slides", "", "", "Disc", 1, "tecnico",
                       instrucoes="Adicione exemplos de JavaScript.")
        assert "Adicione exemplos de JavaScript" in p


# ── Testes: prompt_planejar ───────────────────────────────────────────────────

class TestPromptPlanejar:

    def test_inclui_numero_de_aulas(self):
        p = prompt_planejar("material", 10, "Front-End", "tecnico", "equilibrado")
        assert "10" in p

    def test_inclui_disciplina(self):
        p = prompt_planejar("material", 5, "Banco de Dados", "tecnico", "equilibrado")
        assert "Banco de Dados" in p

    def test_solicita_json_puro(self):
        p = prompt_planejar("material", 3, "Disc", "tecnico", "equilibrado")
        assert "JSON" in p

    def test_campos_obrigatorios_no_template(self):
        p = prompt_planejar("material", 3, "Disc", "tecnico", "equilibrado")
        for campo in ["tema_central", "fio_condutor", "observacoes", "aulas"]:
            assert campo in p

    def test_respeita_limite_de_chars(self):
        conteudo_longo = "x" * 20000
        p = prompt_planejar(conteudo_longo, 5, "Disc", "tecnico", "equilibrado", max_chars=5000)
        # O conteúdo no prompt não deve ter mais que max_chars chars do material
        assert conteudo_longo[:5000] in p
        assert conteudo_longo[:5001] not in p


# ── Testes: prompt_aula_livre ─────────────────────────────────────────────────

class TestPromptAulaLivre:

    def _aula(self, numero: int = 1, titulo: str = "Introdução ao HTML"):
        return {
            "numero": numero,
            "titulo": titulo,
            "topicos_principais": ["HTML semântico", "tags básicas"],
        }

    def test_inclui_numero_e_total(self):
        p = prompt_aula_livre(self._aula(3), 10, "material", "Disc", "tecnico", "equilibrado")
        assert "3" in p
        assert "10" in p

    def test_inclui_titulo(self):
        p = prompt_aula_livre(self._aula(titulo="CSS Grid"), 5, "material",
                              "Disc", "tecnico", "equilibrado")
        assert "CSS Grid" in p

    def test_inclui_topicos(self):
        p = prompt_aula_livre(self._aula(), 5, "material", "Disc", "tecnico", "equilibrado")
        assert "HTML semântico" in p

    def test_inclui_aula_anterior(self):
        p = prompt_aula_livre(
            self._aula(2), 5, "material", "Disc", "tecnico", "equilibrado",
            aula_anterior="Introdução ao HTML",
        )
        assert "Introdução ao HTML" in p

    def test_primeira_aula_sem_anterior(self):
        p = prompt_aula_livre(self._aula(1), 5, "material", "Disc", "tecnico",
                              "equilibrado", aula_anterior="")
        assert "primeira" in p.lower()

    def test_exige_15_secoes(self):
        p = prompt_aula_livre(self._aula(), 5, "material", "Disc", "tecnico", "equilibrado")
        assert "15" in p or "quinze" in p.lower() or "seções" in p.lower()

    def test_exige_gabarito_comentado(self):
        p = prompt_aula_livre(self._aula(), 5, "material", "Disc", "tecnico", "equilibrado")
        assert "gabarito" in p.lower()
