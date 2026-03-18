"""
Extrator de PDF usando pdfplumber.
Fallback para pypdf2 se pdfplumber falhar.
"""

import logging
from .base import ExtratorBase, ResultadoExtracao, TipoArquivo, limpar_texto

logger = logging.getLogger(__name__)


def extrair_pdf(arquivo) -> ResultadoExtracao:
    """Extrai texto de um PDF preservando estrutura de parágrafos."""
    # Tenta pdfplumber primeiro (melhor para PDFs com layout complexo)
    try:
        return _extrair_com_pdfplumber(arquivo)
    except ImportError:
        logger.warning('pdfplumber não instalado, tentando pypdf2.')
    except Exception as e:
        logger.warning(f'pdfplumber falhou: {e}. Tentando pypdf2.')

    # Fallback: pypdf2
    try:
        if hasattr(arquivo, 'seek'):
            arquivo.seek(0)
        return _extrair_com_pypdf2(arquivo)
    except ImportError:
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.PDF,
            erro='Nenhuma biblioteca PDF disponível. Instale pdfplumber.',
        )
    except Exception as e:
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.PDF,
            erro=str(e),
        )


def _extrair_com_pdfplumber(arquivo) -> ResultadoExtracao:
    import pdfplumber

    paginas_texto = []

    with pdfplumber.open(arquivo) as pdf:
        num_paginas = len(pdf.pages)

        for i, pagina in enumerate(pdf.pages, start=1):
            # Texto da página
            texto = pagina.extract_text(x_tolerance=3, y_tolerance=3)

            # Tabelas da página (converte para texto)
            tabelas = pagina.extract_tables()
            texto_tabelas = _tabelas_para_texto(tabelas)

            conteudo_pagina = ''
            if texto:
                conteudo_pagina += texto.strip()
            if texto_tabelas:
                conteudo_pagina += f'\n\n{texto_tabelas}'

            if conteudo_pagina.strip():
                paginas_texto.append(f'[Página {i}]\n{conteudo_pagina.strip()}')

    conteudo = '\n\n'.join(paginas_texto)
    conteudo = limpar_texto(conteudo)

    return ResultadoExtracao(
        conteudo=conteudo,
        tipo=TipoArquivo.PDF,
        paginas=num_paginas,
    )


def _extrair_com_pypdf2(arquivo) -> ResultadoExtracao:
    from pypdf import PdfReader  # pypdf (fork moderno do PyPDF2)

    reader = PdfReader(arquivo)
    paginas_texto = []

    for i, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text()
        if texto and texto.strip():
            paginas_texto.append(f'[Página {i}]\n{texto.strip()}')

    conteudo = '\n\n'.join(paginas_texto)
    conteudo = limpar_texto(conteudo)

    return ResultadoExtracao(
        conteudo=conteudo,
        tipo=TipoArquivo.PDF,
        paginas=len(reader.pages),
    )


def _tabelas_para_texto(tabelas: list) -> str:
    """Converte tabelas extraídas pelo pdfplumber para texto legível."""
    if not tabelas:
        return ''

    linhas = []
    for tabela in tabelas:
        for linha in tabela:
            celulas = [str(c).strip() if c else '' for c in linha]
            linhas.append(' | '.join(celulas))
        linhas.append('')  # linha em branco entre tabelas

    return '\n'.join(linhas)
