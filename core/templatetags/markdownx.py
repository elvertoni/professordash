"""
Templatetag library 'markdownx' — compatível com {% load markdownx %}.

Fornece o filtro |markdownify para renderizar Markdown como HTML seguro.
Delega para markdownx.utils.markdownify() que respeita MARKDOWNX_MARKDOWN_EXTENSIONS
do settings — incluindo md_in_html e extra necessários para HTML inline no Markdown.
"""
from django import template
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify as _markdownx_markdownify

register = template.Library()


@register.filter(name="markdownify", is_safe=True)
def markdownify(value):
    """Converte texto Markdown em HTML, respeitando MARKDOWNX_MARKDOWN_EXTENSIONS."""
    if not value:
        return ""
    return mark_safe(_markdownx_markdownify(str(value)))
