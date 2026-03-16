"""
Templatetag library 'markdownx' — compatível com {% load markdownx %}.

Fornece o filtro |markdownify para renderizar Markdown como HTML seguro.
Usa o pacote 'markdown' (já instalado como dependência do django-markdownx).
"""
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify", is_safe=True)
def markdownify(value):
    """Converte texto Markdown em HTML seguro."""
    if not value:
        return ""
    extensions = [
        "markdown.extensions.fenced_code",
        "markdown.extensions.tables",
        "markdown.extensions.nl2br",
        "markdown.extensions.toc",
    ]
    html = md.markdown(str(value), extensions=extensions)
    return mark_safe(html)
