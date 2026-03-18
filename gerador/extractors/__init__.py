"""
Extratores de conteúdo para o Gerador de Aulas — ProfessorDash
Suporta: PDF, PPTX, DOCX, TXT, MD, URL, texto livre
"""

from .pdf   import extrair_pdf
from .pptx  import extrair_pptx
from .docx  import extrair_docx
from .url   import extrair_url
from .rco   import detectar_papel_rco, extrair_rco, montar_conteudo_rco
from .base  import ExtratorBase, ResultadoExtracao, TipoArquivo, limpar_texto

__all__ = [
    'extrair_pdf',
    'extrair_pptx',
    'extrair_docx',
    'extrair_url',
    'detectar_papel_rco',
    'extrair_rco',
    'montar_conteudo_rco',
    'ExtratorBase',
    'ResultadoExtracao',
    'TipoArquivo',
    'limpar_texto',
    'extrair_arquivo',
    'extrair_multiplos',
]


def extrair_arquivo(arquivo, nome_arquivo: str = '') -> 'ResultadoExtracao':
    """
    Ponto de entrada único. Detecta o tipo e extrai automaticamente.

    Uso:
        resultado = extrair_arquivo(request.FILES['arquivo'])
        print(resultado.conteudo)
        print(resultado.tipo)
    """
    import os

    nome = nome_arquivo or getattr(arquivo, 'name', '') or ''
    ext  = os.path.splitext(nome)[1].lower()

    mapa = {
        '.pdf':  extrair_pdf,
        '.pptx': extrair_pptx,
        '.ppt':  extrair_pptx,
        '.docx': extrair_docx,
        '.doc':  extrair_docx,
        '.txt':  _extrair_txt,
        '.md':   _extrair_txt,
    }

    extrator = mapa.get(ext)
    if not extrator:
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.DESCONHECIDO,
            paginas=0,
            erro=f'Formato não suportado: {ext}',
        )

    return extrator(arquivo)


def extrair_multiplos(arquivos: list) -> str:
    """
    Extrai e concatena conteúdo de múltiplos arquivos.
    Retorna texto único com separadores de fonte.
    """
    partes = []
    for arq in arquivos:
        nome = getattr(arq, 'name', 'arquivo')
        resultado = extrair_arquivo(arq, nome)
        if resultado.conteudo:
            partes.append(
                f"{'='*60}\n"
                f"FONTE: {nome}\n"
                f"{'='*60}\n"
                f"{resultado.conteudo}"
            )
    return '\n\n'.join(partes)


def _extrair_txt(arquivo) -> 'ResultadoExtracao':
    try:
        conteudo = arquivo.read().decode('utf-8', errors='ignore')
        return ResultadoExtracao(
            conteudo=limpar_texto(conteudo),
            tipo=TipoArquivo.TXT,
            paginas=1,
        )
    except Exception as e:
        return ResultadoExtracao(conteudo='', tipo=TipoArquivo.TXT, paginas=0, erro=str(e))
