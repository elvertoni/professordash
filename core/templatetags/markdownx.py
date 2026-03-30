"""
Templatetag library 'markdownx' — compatível com {% load markdownx %}.

Fornece o filtro |markdownify para renderizar Markdown como HTML seguro.
Delega para markdownx.utils.markdownify() que respeita MARKDOWNX_MARKDOWN_EXTENSIONS
do settings — incluindo md_in_html e extra necessários para HTML inline no Markdown.
"""
import re
from django import template
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify as _markdownx_markdownify

register = template.Library()

# Regex que captura frontmatter YAML no início do documento.
# Cobre variações com ou sem espaços antes do primeiro ---.
_FRONTMATTER_RE = re.compile(r'^\s*---[\s\S]*?---\s*\n', re.MULTILINE)


@register.filter(name="markdownify", is_safe=True)
def markdownify(value):
    """Converte texto Markdown em HTML, respeitando MARKDOWNX_MARKDOWN_EXTENSIONS.

    Remove automaticamente o bloco de frontmatter YAML (--- ... ---) antes de
    processar o Markdown, evitando que os metadados vazem como conteúdo HTML.
    """
    if not value:
        return ""
    # Strip do frontmatter YAML antes de passar ao parser
    clean = _FRONTMATTER_RE.sub('', str(value), count=1)
    return mark_safe(_markdownx_markdownify(clean))