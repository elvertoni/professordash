"""
Testes unitários para gerador/extractors/url.py
Usa unittest.mock para não fazer requisições HTTP reais.
"""

from unittest.mock import MagicMock, patch

import pytest

from gerador.extractors.base import TipoArquivo
from gerador.extractors.url import extrair_url

# HTML de exemplo representando uma página de artigo
HTML_ARTIGO = """
<!DOCTYPE html>
<html>
<head><title>Introdução ao CSS Grid</title></head>
<body>
  <nav>Menu de navegação</nav>
  <main>
    <h1>Introdução ao CSS Grid</h1>
    <p>CSS Grid é um sistema de layout bidimensional para a web.</p>
    <h2>Propriedades principais</h2>
    <p>A propriedade grid-template-columns define as colunas.</p>
    <ul>
      <li>grid-template-columns</li>
      <li>grid-template-rows</li>
      <li>grid-gap</li>
    </ul>
  </main>
  <footer>Rodapé do site</footer>
</body>
</html>
"""


class TestExtrairUrl:

    def test_url_invalida_retorna_erro(self):
        """URL sem protocolo deve retornar erro sem fazer requisição."""
        resultado = extrair_url("nao-e-uma-url")

        assert not resultado.ok
        assert "inválida" in resultado.erro.lower() or resultado.erro != ""

    def test_url_sem_http_retorna_erro(self):
        """URL ftp:// deve retornar erro."""
        resultado = extrair_url("ftp://example.com/arquivo")

        assert not resultado.ok
        assert resultado.erro != ""

    def test_extrai_conteudo_via_beautifulsoup(self):
        """Deve extrair título e parágrafos de página HTML via BS4."""
        resposta_mock = MagicMock()
        resposta_mock.text = HTML_ARTIGO
        resposta_mock.raise_for_status = MagicMock()

        with patch("requests.get", return_value=resposta_mock):
            with patch.dict("sys.modules", {"newspaper": None, "newspaper.Article": None}):
                # Força fallback para BS4 desabilitando newspaper
                with patch("gerador.extractors.url._extrair_com_newspaper",
                           side_effect=ImportError):
                    resultado = extrair_url("https://example.com/css-grid")

        assert resultado.ok
        assert resultado.tipo == TipoArquivo.URL
        assert "CSS Grid" in resultado.conteudo

    def test_extrai_via_newspaper_quando_disponivel(self):
        """Deve usar newspaper3k como primeira opção quando disponível."""
        artigo_mock = MagicMock()
        artigo_mock.title = "Introdução ao CSS Grid"
        artigo_mock.text = "CSS Grid é um sistema de layout bidimensional."
        artigo_mock.authors = ["Autor Exemplo"]
        artigo_mock.publish_date = None

        with patch("gerador.extractors.url._extrair_com_newspaper") as mock_news:
            from gerador.extractors.base import ResultadoExtracao, TipoArquivo as TA
            mock_news.return_value = ResultadoExtracao(
                conteudo="# Introdução ao CSS Grid\n\nCSS Grid é um sistema de layout.",
                tipo=TA.URL,
                metadados={"titulo": "Introdução ao CSS Grid"},
            )
            resultado = extrair_url("https://example.com/css-grid")

        assert resultado.ok
        assert "CSS Grid" in resultado.conteudo

    def test_fallback_para_bs4_quando_newspaper_falha(self):
        """Quando newspaper falha, deve usar BS4 como fallback."""
        resposta_mock = MagicMock()
        resposta_mock.text = HTML_ARTIGO
        resposta_mock.raise_for_status = MagicMock()

        with patch("gerador.extractors.url._extrair_com_newspaper",
                   side_effect=Exception("newspaper falhou")):
            with patch("requests.get", return_value=resposta_mock):
                resultado = extrair_url("https://example.com/css-grid")

        assert resultado.ok
        assert "CSS Grid" in resultado.conteudo

    def test_metadados_incluem_url(self):
        """ResultadoExtracao deve conter a URL nos metadados."""
        resposta_mock = MagicMock()
        resposta_mock.text = HTML_ARTIGO
        resposta_mock.raise_for_status = MagicMock()

        with patch("gerador.extractors.url._extrair_com_newspaper",
                   side_effect=ImportError):
            with patch("requests.get", return_value=resposta_mock):
                resultado = extrair_url("https://example.com/css-grid")

        assert resultado.metadados.get("url") == "https://example.com/css-grid"
