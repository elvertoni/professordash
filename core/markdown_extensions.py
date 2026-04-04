"""
Extensoes Markdown customizadas para o ProfessorDash.

Converte blocos :::tipo em componentes HTML ricos que ja possuem
estilizacao no template aula_detalhe.html.

Sintaxe suportada:

    :::objetivo
    Texto do objetivo da aula
    :::

    :::importante
    Texto de alerta importante
    :::

    :::dica
    Uma dica para os alunos
    :::

    :::exemplo
    Conteudo de exemplo
    :::

    :::atencao
    Aviso de atencao
    :::

    :::roteiro
    Notas de fala para o professor (ocultas no modo aluno)
    :::

    :::resumo
    - Topico 1
    - Topico 2
    :::

    :::questao Enunciado da pergunta?
    a) Alternativa A
    b) Alternativa B
    c) Alternativa C *
    d) Alternativa D
    > Explicacao do gabarito
    :::
"""

import re
import xml.etree.ElementTree as etree

from markdown import Extension
from markdown.preprocessors import Preprocessor


# ── Mapa de callouts ────────────────────────────────────────────────────

CALLOUT_MAP = {
    "objetivo": {
        "icon": "\U0001f3af",
        "title": "Objetivo",
        "css": "c-green",
    },
    "importante": {
        "icon": "\u26a0\ufe0f",
        "title": "Importante",
        "css": "c-amber",
    },
    "dica": {
        "icon": "\U0001f4a1",
        "title": "Dica",
        "css": "c-blue",
    },
    "exemplo": {
        "icon": "\U0001f4dd",
        "title": "Exemplo",
        "css": "c-violet",
    },
    "atencao": {
        "icon": "\U0001f6a8",
        "title": "Atencao",
        "css": "c-coral",
    },
    "conceito": {
        "icon": "\U0001f4d6",
        "title": "Conceito",
        "css": "c-blue",
    },
    "exercicio": {
        "icon": "\u270d\ufe0f",
        "title": "Exercicio",
        "css": "c-violet",
    },
    "curiosidade": {
        "icon": "\U0001f50d",
        "title": "Curiosidade",
        "css": "c-blue",
    },
}

# Regex para capturar blocos :::tipo ... :::
BLOCK_RE = re.compile(
    r"^:::(\w+)([ \t]+[^\n]*)?\s*\n(.*?)\n:::[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

LETTERS = "abcdefghijklmnopqrstuvwxyz"


class ProfessorDashPreprocessor(Preprocessor):
    """Preprocessor que converte blocos ::: em HTML antes do parser Markdown."""

    _question_counter = 0

    def run(self, lines):
        text = "\n".join(lines)
        ProfessorDashPreprocessor._question_counter = 0
        text = BLOCK_RE.sub(self._replace_block, text)
        return text.split("\n")

    def _stash(self, html):
        """Protege o HTML gerado de ser re-processado pelo parser Markdown."""
        return self.md.htmlStash.store(html)

    def _replace_block(self, match):
        block_type = match.group(1).lower().strip()
        inline_arg = (match.group(2) or "").strip()
        body = match.group(3).strip()

        if block_type == "questao":
            return self._stash(self._build_questao(inline_arg, body))
        if block_type == "roteiro":
            return self._stash(self._build_roteiro(body))
        if block_type == "resumo":
            return self._stash(self._build_resumo(body))
        if block_type in CALLOUT_MAP:
            return self._stash(self._build_callout(block_type, inline_arg, body))

        # Fallback: callout generico azul
        return self._stash(
            self._build_callout("dica", inline_arg or block_type.title(), body)
        )

    def _build_callout(self, block_type, custom_title, body):
        cfg = CALLOUT_MAP[block_type]
        title = custom_title if custom_title else cfg["title"]
        icon = cfg["icon"]
        css = cfg["css"]

        body_html = _escape(body).replace("\n", "<br>")

        return (
            f'<div class="callout {css}">'
            f'<div class="callout-icon">{icon}</div>'
            f'<div class="callout-body">'
            f'<div class="callout-title">{_escape(title)}</div>'
            f'<p class="callout-text">{body_html}</p>'
            f"</div>"
            f"</div>"
        )

    def _build_roteiro(self, body):
        body_html = _escape(body).replace("\n", "<br>")

        return (
            f'<div class="roteiro">'
            f'<div class="roteiro-header">'
            f"\U0001f399\ufe0f Roteiro de fala"
            f"</div>"
            f'<div class="roteiro-texto">{body_html}</div>'
            f"</div>"
        )

    def _build_resumo(self, body):
        items = []
        for line in body.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Remove leading - or * or number.
            line = re.sub(r"^[-*\d.)\]]+\s*", "", line).strip()
            if line:
                items.append(line)

        if not items:
            return ""

        li_html = "".join(
            f'<li><span class="resumo-check">\u2713</span> {_escape(item)}</li>'
            for item in items
        )

        return f'<ul class="resumo-list">{li_html}</ul>'

    def _build_questao(self, enunciado, body):
        ProfessorDashPreprocessor._question_counter += 1
        num = ProfessorDashPreprocessor._question_counter
        idx = f"q-{num}"

        lines = body.split("\n")
        alternativas = []
        gabarito_lines = []
        correta = ""
        in_gabarito = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith(">"):
                in_gabarito = True
                gabarito_lines.append(stripped.lstrip("> ").strip())
                continue

            if in_gabarito:
                gabarito_lines.append(stripped)
                continue

            # Parse alternativa: a) Texto ou a) Texto *
            alt_match = re.match(
                r"^([a-zA-Z])\)\s*(.+?)(\s*\*\s*)?$", stripped
            )
            if alt_match:
                letra = alt_match.group(1).upper()
                texto = alt_match.group(2).strip()
                is_correta = bool(alt_match.group(3))
                alternativas.append(
                    {"letra": letra, "texto": texto, "correta": is_correta}
                )
                if is_correta:
                    correta = letra

        # Build alternativas HTML
        alt_html_parts = []
        for alt in alternativas:
            correta_attr = ' data-correta="true"' if alt["correta"] else ""
            letra_attr = f' data-letra="{alt["letra"]}"'
            alt_html_parts.append(
                f'<li class="alt"{letra_attr}{correta_attr}>'
                f'<span class="alt-badge">{alt["letra"]}</span> '
                f"{_escape(alt['texto'])}"
                f"</li>"
            )
        alt_html = "".join(alt_html_parts)

        gabarito_text = " ".join(gabarito_lines).strip()
        gabarito_html = ""
        if gabarito_text:
            gabarito_html = (
                f'<div class="gabarito" data-explicacao="{_escape_attr(gabarito_text)}">'
                f'<span class="gab-texto">{_escape(gabarito_text)}</span>'
                f"</div>"
            )

        return (
            f'<div class="questao" data-idx="{idx}">'
            f'<div class="questao-num">Questao {num}</div>'
            f'<div class="questao-enunciado">{_escape(enunciado)}</div>'
            f'<ul class="alternativas" data-correct="{correta}">'
            f"{alt_html}"
            f"</ul>"
            f"{gabarito_html}"
            f"</div>"
        )


def _escape(text):
    """Escape HTML entities."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _escape_attr(text):
    """Escape for HTML attributes."""
    return _escape(text).replace('"', "&quot;").replace("'", "&#39;")


class ProfessorDashExtension(Extension):
    """Extensao Markdown que ativa blocos ::: do ProfessorDash."""

    def extendMarkdown(self, md):
        md.preprocessors.register(
            ProfessorDashPreprocessor(md),
            "professordash_blocks",
            priority=30,
        )


def makeExtension(**kwargs):
    """Entry point para o Python-Markdown."""
    return ProfessorDashExtension(**kwargs)
