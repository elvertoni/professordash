"""
Testes unitários para gerador/extractors/pdf.py
"""

import io
from unittest.mock import MagicMock, patch

import pytest

from gerador.extractors.base import TipoArquivo
from gerador.extractors.pdf import extrair_pdf


# ── Fixture: PDF mínimo válido em memória ─────────────────────────────────────

def _make_pdf_bytes(texto: str = "Conteúdo da página 1\n\nConteúdo da página 2") -> io.BytesIO:
    """Cria um PDF em memória via pdfplumber-mock ou via construção direta."""
    buf = io.BytesIO()
    buf.name = "teste.pdf"
    buf.write(texto.encode())
    buf.seek(0)
    return buf


# ── Testes ────────────────────────────────────────────────────────────────────

class TestExtrairPdf:

    def test_retorna_resultado_extracao_com_pdfplumber(self):
        """extrair_pdf() deve retornar ResultadoExtracao com conteúdo via pdfplumber."""
        pagina_mock = MagicMock()
        pagina_mock.extract_text.return_value = "Linha 1\nLinha 2"
        pagina_mock.extract_tables.return_value = []

        pdf_mock = MagicMock()
        pdf_mock.__enter__ = MagicMock(return_value=pdf_mock)
        pdf_mock.__exit__ = MagicMock(return_value=False)
        pdf_mock.pages = [pagina_mock]

        with patch("pdfplumber.open", return_value=pdf_mock):
            arquivo = io.BytesIO(b"fake")
            arquivo.name = "aula.pdf"
            resultado = extrair_pdf(arquivo)

        assert resultado.ok
        assert resultado.tipo == TipoArquivo.PDF
        assert "Linha 1" in resultado.conteudo
        assert resultado.paginas == 1

    def test_extrai_multiplas_paginas(self):
        """Deve extrair texto de múltiplas páginas e concatenar."""
        paginas = []
        for i in range(1, 4):
            p = MagicMock()
            p.extract_text.return_value = f"Texto da página {i}"
            p.extract_tables.return_value = []
            paginas.append(p)

        pdf_mock = MagicMock()
        pdf_mock.__enter__ = MagicMock(return_value=pdf_mock)
        pdf_mock.__exit__ = MagicMock(return_value=False)
        pdf_mock.pages = paginas

        with patch("pdfplumber.open", return_value=pdf_mock):
            arquivo = io.BytesIO(b"fake")
            resultado = extrair_pdf(arquivo)

        assert resultado.paginas == 3
        for i in range(1, 4):
            assert f"página {i}" in resultado.conteudo

    def test_pagina_sem_texto_ignorada(self):
        """Páginas sem texto não devem aparecer no conteúdo."""
        p_vazia = MagicMock()
        p_vazia.extract_text.return_value = None
        p_vazia.extract_tables.return_value = []

        p_com_texto = MagicMock()
        p_com_texto.extract_text.return_value = "Conteúdo real"
        p_com_texto.extract_tables.return_value = []

        pdf_mock = MagicMock()
        pdf_mock.__enter__ = MagicMock(return_value=pdf_mock)
        pdf_mock.__exit__ = MagicMock(return_value=False)
        pdf_mock.pages = [p_vazia, p_com_texto]

        with patch("pdfplumber.open", return_value=pdf_mock):
            resultado = extrair_pdf(io.BytesIO(b"fake"))

        assert "Conteúdo real" in resultado.conteudo

    def test_extrai_tabelas_da_pagina(self):
        """Tabelas extraídas pelo pdfplumber devem aparecer no conteúdo."""
        pagina = MagicMock()
        pagina.extract_text.return_value = "Título"
        pagina.extract_tables.return_value = [[["A", "B"], ["1", "2"]]]

        pdf_mock = MagicMock()
        pdf_mock.__enter__ = MagicMock(return_value=pdf_mock)
        pdf_mock.__exit__ = MagicMock(return_value=False)
        pdf_mock.pages = [pagina]

        with patch("pdfplumber.open", return_value=pdf_mock):
            resultado = extrair_pdf(io.BytesIO(b"fake"))

        assert "A | B" in resultado.conteudo

    def test_fallback_pypdf_quando_pdfplumber_falha(self):
        """Quando pdfplumber levanta exceção, deve tentar pypdf como fallback."""
        pypdf = pytest.importorskip("pypdf", reason="pypdf não instalado — fallback não testável")

        pagina_mock = MagicMock()
        pagina_mock.extract_text.return_value = "Texto via pypdf"

        reader_mock = MagicMock()
        reader_mock.pages = [pagina_mock]

        with patch("pdfplumber.open", side_effect=Exception("falhou")):
            with patch("pypdf.PdfReader", return_value=reader_mock):
                resultado = extrair_pdf(io.BytesIO(b"fake"))

        assert "Texto via pypdf" in resultado.conteudo

    def test_retorna_erro_quando_nenhuma_lib_disponivel(self):
        """Sem pdfplumber e sem pypdf, deve retornar ResultadoExtracao com erro."""
        with patch("pdfplumber.open", side_effect=Exception("falhou")):
            with patch.dict("sys.modules", {"pypdf": None}):
                resultado = extrair_pdf(io.BytesIO(b"fake"))

        assert not resultado.ok or resultado.erro != "" or resultado.conteudo == ""
