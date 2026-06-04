"""Templatetag library 'markdownx' — compatível com {% load markdownx %}.

Fornece o filtro |markdownify para renderizar Markdown como HTML seguro.
Delega para markdownx.utils.markdownify() que respeita MARKDOWNX_MARKDOWN_EXTENSIONS
do settings — incluindo md_in_html e extra necessários para HTML inline no Markdown.

Responsabilidades deste filtro:
- remover frontmatter YAML do topo antes do parser Markdown;
- ativar as extensões configuradas, incluindo os blocos ::: do ProfessorDash.

Blocos de código continuam saindo como <pre><code> pelo Python-Markdown. A
decoração visual, medição de blocos longos e botões de UI pertencem aos
templates de aula/apostila, porque dependem do DOM final renderizado.
"""

import re

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import markdown as md_module

from markdownx.utils import markdownify as _markdownx_markdownify

register = template.Library()

# Regex que captura frontmatter YAML no início do documento.
# Cobre variações com ou sem espaços antes do primeiro ---.
_FRONTMATTER_RE = re.compile(r'^\s*---[\s\S]*?---\s*\n', re.MULTILINE)


def _professordash_markdownify(text, is_staff=False):
    """Renderiza Markdown com as extensões do ProfessorDash e consciência de staff.

    Cria uma instância própria de Markdown (em vez de usar markdownx.utils.markdownify)
    para poder injetar a flag ``is_staff`` no preprocessador de blocos :::.
    """
    if not text:
        return ""

    # Strip do frontmatter YAML
    clean = _FRONTMATTER_RE.sub('', str(text), count=1)

    # Cria o parser Markdown com as mesmas extensões configuradas
    extensions = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSIONS', [])
    ext_configs = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS', {})
    md = md_module.Markdown(extensions=extensions, extension_configs=ext_configs)

    # Injeta is_staff no nosso preprocessador de blocos :::
    if 'professordash_blocks' in md.preprocessors:
        md.preprocessors['professordash_blocks'].is_staff = is_staff

    return md.convert(clean)


@register.filter(name="markdownify", is_safe=True)
def markdownify(value):
    """Converte texto Markdown em HTML, respeitando MARKDOWNX_MARKDOWN_EXTENSIONS.

    Remove automaticamente o bloco de frontmatter YAML (--- ... ---) antes de
    processar o Markdown, evitando que os metadados vazem como conteúdo HTML.

    Por padrão renderiza TODOS os blocos ::: (comportamento legado).
    Para ocultar :::roteiro de não-staff, use a tag {% render_markdown %}.
    """
    if not value:
        return ""
    return mark_safe(_professordash_markdownify(value, is_staff=False))


@register.simple_tag(takes_context=True)
def render_markdown(context, content):
    """Renderiza Markdown com tratamento staff-aware de :::roteiro.

    Uso: {% render_markdown aula.conteudo %}

    O bloco :::roteiro é renderizado apenas se request.user.is_staff for True.
    """
    if not content:
        return ""
    is_staff = context['request'].user.is_staff
    return mark_safe(_professordash_markdownify(content, is_staff=is_staff))
