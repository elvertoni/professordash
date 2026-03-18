"""
Extrator de conteúdo via URL usando BeautifulSoup.
Remove navegação, rodapés e outros elementos de UI.
"""

import logging
import re
from .base import ResultadoExtracao, TipoArquivo, limpar_texto

logger = logging.getLogger(__name__)

# Tags que geralmente contêm conteúdo útil
TAGS_CONTEUDO = ['article', 'main', 'section', '.content', '.post', '.entry']

# Tags para remover (ruído)
TAGS_REMOVER = ['nav', 'header', 'footer', 'aside', 'script', 'style',
                'noscript', 'iframe', 'form', 'button', 'advertisement']


def extrair_url(url: str, timeout: int = 15) -> ResultadoExtracao:
    """
    Extrai conteúdo textual de uma URL pública.
    Tenta newspaper3k primeiro (melhor para artigos), fallback para BeautifulSoup.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.URL,
            erro='URL inválida. Deve começar com http:// ou https://',
        )

    # Tenta newspaper3k (melhor para artigos e blogs)
    try:
        return _extrair_com_newspaper(url)
    except ImportError:
        logger.info('newspaper3k não disponível, usando BeautifulSoup.')
    except Exception as e:
        logger.warning(f'newspaper3k falhou em {url}: {e}. Tentando BS4.')

    # Fallback: BeautifulSoup
    try:
        return _extrair_com_bs4(url, timeout)
    except Exception as e:
        return ResultadoExtracao(
            conteudo='',
            tipo=TipoArquivo.URL,
            erro=str(e),
        )


def _extrair_com_newspaper(url: str) -> ResultadoExtracao:
    from newspaper import Article

    artigo = Article(url, language='pt')
    artigo.download()
    artigo.parse()

    partes = []
    if artigo.title:
        partes.append(f'# {artigo.title}')
    if artigo.text:
        partes.append(artigo.text)

    conteudo = '\n\n'.join(partes)
    conteudo = limpar_texto(conteudo)

    if not conteudo:
        raise ValueError('newspaper3k não encontrou conteúdo.')

    return ResultadoExtracao(
        conteudo=conteudo,
        tipo=TipoArquivo.URL,
        metadados={
            'titulo': artigo.title,
            'autores': artigo.authors,
            'data': str(artigo.publish_date) if artigo.publish_date else '',
            'url': url,
        },
    )


def _extrair_com_bs4(url: str, timeout: int) -> ResultadoExtracao:
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }

    resposta = requests.get(url, headers=headers, timeout=timeout)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Remove tags de ruído
    for tag in soup(TAGS_REMOVER):
        tag.decompose()

    # Tenta encontrar bloco principal de conteúdo
    conteudo_elem = None
    for seletor in TAGS_CONTEUDO:
        conteudo_elem = soup.select_one(seletor)
        if conteudo_elem:
            break

    alvo = conteudo_elem or soup.find('body') or soup

    # Extrai texto preservando estrutura de parágrafos
    partes = []
    titulo = soup.find('title')
    if titulo:
        partes.append(f'# {titulo.text.strip()}')

    for elem in alvo.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'pre', 'code']):
        texto = elem.get_text(separator=' ', strip=True)
        if not texto or len(texto) < 3:
            continue

        tag = elem.name
        if tag == 'h1':
            partes.append(f'\n# {texto}')
        elif tag == 'h2':
            partes.append(f'\n## {texto}')
        elif tag in ('h3', 'h4'):
            partes.append(f'\n### {texto}')
        elif tag == 'li':
            partes.append(f'  - {texto}')
        elif tag in ('pre', 'code'):
            partes.append(f'\n```\n{texto}\n```')
        else:
            partes.append(texto)

    conteudo = '\n\n'.join(partes)
    conteudo = limpar_texto(conteudo)

    return ResultadoExtracao(
        conteudo=conteudo,
        tipo=TipoArquivo.URL,
        metadados={'url': url},
    )
