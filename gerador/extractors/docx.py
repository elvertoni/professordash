"""
Extrator de DOCX usando python-docx.
Preserva: parágrafos, títulos, listas, tabelas e estrutura de questões.
"""

import logging
from .base import ResultadoExtracao, TipoArquivo, limpar_texto

logger = logging.getLogger(__name__)


def extrair_docx(arquivo) -> ResultadoExtracao:
    """
    Extrai todo o conteúdo de um documento Word.
    Detecta automaticamente questões de múltipla escolha (padrão SEED-PR).
    """
    if not arquivo:
        return ResultadoExtracao(conteudo='', tipo=TipoArquivo.DOCX, paginas=0)

    try:
        from docx import Document
    except ImportError:
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.DOCX,
            erro='python-docx não instalado. Execute: pip install python-docx',
        )

    try:
        doc = Document(arquivo)
        partes = []
        num_questoes = 0

        for elemento in _iterar_elementos(doc):
            tipo = elemento['tipo']
            texto = elemento['texto'].strip()

            if not texto:
                continue

            if tipo == 'titulo1':
                partes.append(f'\n# {texto}')
            elif tipo == 'titulo2':
                partes.append(f'\n## {texto}')
            elif tipo == 'titulo3':
                partes.append(f'\n### {texto}')
            elif tipo == 'lista':
                partes.append(f'  - {texto}')
            elif tipo == 'tabela':
                partes.append(texto)
            else:
                # Detecta questão (padrão: começa com número + ponto ou parênteses)
                if _eh_questao(texto):
                    num_questoes += 1
                    partes.append(f'\nQuestão {num_questoes}: {texto}')
                # Detecta alternativa (A) B) C) D) ou a) b) c) d))
                elif _eh_alternativa(texto):
                    partes.append(f'  {texto}')
                else:
                    partes.append(texto)

        conteudo = '\n'.join(partes)
        conteudo = limpar_texto(conteudo)

        return ResultadoExtracao(
            conteudo=conteudo,
            tipo=TipoArquivo.DOCX,
            metadados={'questoes_detectadas': num_questoes},
        )

    except Exception as e:
        logger.error(f'Erro ao extrair DOCX: {e}')
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.DOCX,
            erro=str(e),
        )


def _iterar_elementos(doc) -> list:
    """Itera parágrafos e tabelas na ordem em que aparecem no documento."""
    from docx.oxml.ns import qn

    elementos = []
    body = doc.element.body

    for child in body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':  # parágrafo
            from docx.text.paragraph import Paragraph
            para = Paragraph(child, doc)
            estilo = (para.style.name or '').lower()

            if 'heading 1' in estilo or 'título 1' in estilo:
                tipo = 'titulo1'
            elif 'heading 2' in estilo or 'título 2' in estilo:
                tipo = 'titulo2'
            elif 'heading 3' in estilo or 'título 3' in estilo:
                tipo = 'titulo3'
            elif 'list' in estilo or 'lista' in estilo:
                tipo = 'lista'
            else:
                tipo = 'paragrafo'

            elementos.append({'tipo': tipo, 'texto': para.text})

        elif tag == 'tbl':  # tabela
            from docx.table import Table
            tabela = Table(child, doc)
            texto_tabela = _extrair_tabela_docx(tabela)
            elementos.append({'tipo': 'tabela', 'texto': texto_tabela})

    return elementos


def _extrair_tabela_docx(tabela) -> str:
    """Converte tabela do DOCX para texto."""
    linhas = []
    for linha in tabela.rows:
        celulas = [cell.text.strip() for cell in linha.cells]
        # Remove células duplicadas (DOCX às vezes repete células mescladas)
        celulas_unicas = []
        ultimo = None
        for c in celulas:
            if c != ultimo:
                celulas_unicas.append(c)
                ultimo = c
        linhas.append(' | '.join(celulas_unicas))
    return '\n'.join(linhas)


def _eh_questao(texto: str) -> bool:
    """Detecta se o parágrafo é uma questão numerada."""
    import re
    # Padrões: "1.", "1)", "Questão 1", "Q1"
    return bool(re.match(r'^(\d+[\.\)]\s|[Qq]uestão\s+\d+)', texto))


def _eh_alternativa(texto: str) -> bool:
    """Detecta se o parágrafo é uma alternativa de múltipla escolha."""
    import re
    # Padrões: "A)", "a)", "A.", "a.", "(A)", "(a)"
    return bool(re.match(r'^[\(\[]?[A-Ea-e][\)\].]\s', texto))
