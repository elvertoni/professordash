"""
Testes unitários para gerador/pipeline.py

Cobre: juntar_conteudo, extrair_titulo, executar_modo_rco, executar_modo_livre.
Todos os testes mocam gerar_aula() — sem chamadas reais ao OpenRouter.
"""

from unittest.mock import MagicMock, call, patch

import pytest

from gerador.pipeline import executar_modo_livre, executar_modo_rco, extrair_titulo, juntar_conteudo
from gerador.tokens import UsoTokens


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_uso_mock(tokens_input=500, tokens_output=1500):
    return UsoTokens(
        modelo="anthropic/claude-sonnet-4-5",
        tokens_input=tokens_input,
        tokens_output=tokens_output,
    )


def _make_material_mock(conteudo: str, papel_rco: str = "", arquivo_nome: str = ""):
    m = MagicMock()
    m.conteudo_extraido = conteudo
    m.papel_rco = papel_rco
    m.arquivo.name = arquivo_nome
    m.url = ""
    return m


def _make_sessao_mock(modo="rco", num_aulas=1, provider="claude", disciplina_nome="Front-End"):
    sessao = MagicMock()
    sessao.id = 42
    sessao.modo = modo
    sessao.num_aulas = num_aulas
    sessao.nivel = "tecnico"
    sessao.foco = "equilibrado"
    sessao.provider = provider
    sessao.instrucoes = ""
    sessao.disciplina.nome = disciplina_nome
    sessao.disciplina.pk = 1
    sessao.tokens_usados = 0
    sessao.custo_estimado = 0
    return sessao


# ── Testes: juntar_conteudo ───────────────────────────────────────────────────

class TestJuntarConteudo:

    def test_concatena_multiplos_materiais(self):
        materiais = [
            _make_material_mock("Conteúdo 1", arquivo_nome="slides.pptx"),
            _make_material_mock("Conteúdo 2", arquivo_nome="apostila.pdf"),
        ]
        resultado = juntar_conteudo(materiais)

        assert "Conteúdo 1" in resultado
        assert "Conteúdo 2" in resultado

    def test_inclui_separadores_de_fonte(self):
        materiais = [_make_material_mock("Texto", arquivo_nome="arquivo.pdf")]
        resultado = juntar_conteudo(materiais)

        assert "FONTE:" in resultado
        assert "=" * 20 in resultado

    def test_ignora_material_sem_conteudo(self):
        materiais = [
            _make_material_mock("",         arquivo_nome="vazio.pdf"),
            _make_material_mock("Válido",   arquivo_nome="valido.pdf"),
        ]
        resultado = juntar_conteudo(materiais)

        assert "Válido" in resultado
        assert resultado.count("FONTE:") == 1  # só 1 separador

    def test_retorna_string_vazia_para_lista_vazia(self):
        assert juntar_conteudo([]) == ""

    def test_usa_url_quando_sem_arquivo(self):
        m = MagicMock()
        m.conteudo_extraido = "Conteúdo da web"
        m.arquivo = None   # sem arquivo — pipeline usa m.url como fonte
        m.url = "https://example.com"
        resultado = juntar_conteudo([m])
        assert "Conteúdo da web" in resultado


# ── Testes: extrair_titulo ────────────────────────────────────────────────────

class TestExtrairTitulo:

    def test_extrai_header_h1(self):
        md = "# CSS Grid: Layout Avançado\n\nConteúdo aqui."
        titulo = extrair_titulo(md)
        assert "CSS Grid" in titulo
        assert "Layout" in titulo

    def test_extrai_header_h2_quando_h1_generico(self):
        md = "# Cabeçalho\n\n## Introdução ao JavaScript\n\nConteúdo."
        titulo = extrair_titulo(md)
        assert "JavaScript" in titulo

    def test_fallback_para_aula_gerada(self):
        md = "Texto sem nenhum header aqui."
        assert extrair_titulo(md) == "Aula Gerada"

    def test_ignora_header_so_com_numero(self):
        md = "# Aula 3\n\n## CSS Flexbox em Detalhes\n\nConteúdo."
        titulo = extrair_titulo(md)
        assert "Flexbox" in titulo

    def test_preserva_acentos(self):
        md = "# Introdução à Programação Orientada a Objetos\n\nConteúdo."
        titulo = extrair_titulo(md)
        assert "Programação" in titulo or "Introdução" in titulo


# ── Testes: executar_modo_rco ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestExecutarModoRco:

    def test_cria_aula_como_rascunho(self, turma):
        sessao = MagicMock()
        sessao.id = 1
        sessao.modo = "rco"
        sessao.num_aulas = 99  # número improvável de conflitar
        sessao.nivel = "tecnico"
        sessao.foco = "equilibrado"
        sessao.provider = "claude"
        sessao.instrucoes = ""
        sessao.disciplina = turma
        sessao.tokens_usados = 0
        sessao.custo_estimado = 0
        sessao.materiais.all.return_value = [
            _make_material_mock("Slides HTML", papel_rco="slides"),
            _make_material_mock("1. Questão?", papel_rco="atividade"),
            _make_material_mock("Crie um site", papel_rco="pratica"),
        ]

        uso_mock = _make_uso_mock()
        markdown_mock = "## HTML Semântico\n\nConteúdo desenvolvido."

        with patch("gerador.pipeline.gerar_aula", return_value=(markdown_mock, uso_mock)):
            with patch("gerador.pipeline.registrar_uso_na_sessao"):
                aula = executar_modo_rco(sessao)

        assert aula.turma == turma
        assert aula.realizada is False
        assert aula.numero == 99
        assert "HTML" in aula.titulo or aula.titulo == "Aula Gerada"

    def test_status_muda_para_gerando_e_concluido(self, turma):
        sessao = MagicMock()
        sessao.id = 1
        sessao.num_aulas = 88
        sessao.nivel = "tecnico"
        sessao.provider = "claude"
        sessao.instrucoes = ""
        sessao.disciplina = turma
        sessao.tokens_usados = 0
        sessao.custo_estimado = 0
        sessao.materiais.all.return_value = []
        status_values = []

        def _save(update_fields=None):
            status_values.append(sessao.status)

        sessao.save = _save
        uso_mock = _make_uso_mock()

        with patch("gerador.pipeline.gerar_aula", return_value=("## Aula\n\nConteúdo.", uso_mock)):
            with patch("gerador.pipeline.registrar_uso_na_sessao"):
                executar_modo_rco(sessao)

        assert "gerando"  in status_values
        assert "concluido" in status_values

    def test_status_vira_erro_quando_gerar_aula_falha(self, turma):
        sessao = MagicMock()
        sessao.id = 1
        sessao.num_aulas = 77
        sessao.nivel = "tecnico"
        sessao.provider = "claude"
        sessao.instrucoes = ""
        sessao.disciplina = turma
        sessao.tokens_usados = 0
        sessao.custo_estimado = 0
        sessao.materiais.all.return_value = []

        with patch("gerador.pipeline.gerar_aula", side_effect=Exception("API falhou")):
            with pytest.raises(Exception, match="API falhou"):
                executar_modo_rco(sessao)

        assert sessao.status == "erro"


# ── Testes: executar_modo_livre ───────────────────────────────────────────────

@pytest.mark.django_db
class TestExecutarModoLivre:

    def _make_sessao_livre(self, turma, num_aulas=3):
        sessao = MagicMock()
        sessao.id = 2
        sessao.modo = "livre"
        sessao.nivel = "tecnico"
        sessao.foco = "equilibrado"
        sessao.provider = "claude"
        sessao.instrucoes = ""
        sessao.disciplina = turma
        sessao.tokens_usados = 0
        sessao.custo_estimado = 0
        sessao.planejamento = {
            "aulas": [
                {"numero": 100 + i, "titulo": f"Aula {i}", "topicos_principais": ["tópico"]}
                for i in range(1, num_aulas + 1)
            ]
        }
        sessao.materiais.all.return_value = [
            _make_material_mock("Material de referência", arquivo_nome="apostila.pdf")
        ]
        return sessao

    def test_gera_n_aulas_em_lote(self, turma):
        sessao = self._make_sessao_livre(turma, num_aulas=3)
        uso_mock = _make_uso_mock()

        with patch("gerador.pipeline.gerar_aula", return_value=("## Aula\n\nConteúdo.", uso_mock)):
            with patch("gerador.pipeline.registrar_uso_na_sessao"):
                numeros = list(executar_modo_livre(sessao))

        assert len(numeros) == 3
        assert numeros == [101, 102, 103]

    def test_yield_progresso_em_ordem(self, turma):
        sessao = self._make_sessao_livre(turma, num_aulas=2)
        uso_mock = _make_uso_mock()

        with patch("gerador.pipeline.gerar_aula", return_value=("## T\n\nC.", uso_mock)):
            with patch("gerador.pipeline.registrar_uso_na_sessao"):
                numeros = list(executar_modo_livre(sessao))

        assert numeros[0] < numeros[1]

    def test_status_concluido_apos_lote(self, turma):
        sessao = self._make_sessao_livre(turma, num_aulas=1)
        uso_mock = _make_uso_mock()

        with patch("gerador.pipeline.gerar_aula", return_value=("## T\n\nC.", uso_mock)):
            with patch("gerador.pipeline.registrar_uso_na_sessao"):
                list(executar_modo_livre(sessao))

        assert sessao.status == "concluido"

    def test_erro_em_aula_para_geracao(self, turma):
        sessao = self._make_sessao_livre(turma, num_aulas=2)

        with patch("gerador.pipeline.gerar_aula", side_effect=Exception("timeout")):
            with pytest.raises(Exception, match="timeout"):
                list(executar_modo_livre(sessao))

        assert sessao.status == "erro"
