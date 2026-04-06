#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(
    r"^---[ \t]*\n.*?\n---[ \t]*(?:\n|$)",
    re.DOTALL,
)
QUESTION_HEADER_RE = re.compile(r"^:::questao\s+.+$", re.MULTILINE)
QUESTION_BLOCK_RE = re.compile(
    r"^:::questao[ \t]+[^\n]+$\n(.*?)\n:::[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
CORRECT_ALTERNATIVE_RE = re.compile(r"^[a-zA-Z]\)\s*.+ \*$", re.MULTILINE)


def first_nonempty_line(lines):
    for idx, line in enumerate(lines):
        if line.strip():
            return idx, line
    return None, None


def next_content_line(lines, start_index):
    for idx in range(start_index, len(lines)):
        line = lines[idx]
        if line.strip():
            return idx, line
    return None, None


def is_plain_paragraph_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("<", "#", "-", "*", ">", "|")):
        return False
    if re.match(r"^\d+\.\s", stripped):
        return False
    return True


def validate_markdown(text):
    errors = []
    warnings = []

    if re.search(r"<\s*aside\b", text, re.IGNORECASE):
        errors.append("Nao pode usar a tag aside.")

    # Frontmatter YAML é opcional — o |markdownify o remove antes de renderizar.
    # Se presente, stripamos para validar só o conteúdo da aula.
    frontmatter_match = FRONTMATTER_RE.match(text)
    content_text = text[frontmatter_match.end():] if frontmatter_match else text

    lines = content_text.splitlines()
    title_idx, title_line = first_nonempty_line(lines)
    if title_line is None:
        errors.append("Arquivo vazio.")
        return {"ok": False, "errors": errors, "warnings": warnings}

    if not re.match(r"^#\s+\S+", title_line.strip()):
        errors.append("A primeira linha util precisa ser um titulo H1.")

    intro_idx, intro_line = next_content_line(lines, (title_idx or 0) + 1)
    if intro_line is None:
        errors.append("Falta paragrafo introdutorio apos o titulo.")
    elif not is_plain_paragraph_line(intro_line):
        errors.append("O primeiro bloco apos o titulo precisa ser um paragrafo simples.")

    h2_headings = re.findall(r"^##\s+(.+?)\s*$", content_text, flags=re.MULTILINE)
    if "Questões de fixação" not in h2_headings and "Questoes de fixacao" not in h2_headings:
        errors.append("Falta a secao ## Questoes de fixacao.")
    if "Atividade prática" not in h2_headings and "Atividade pratica" not in h2_headings:
        errors.append("Falta a secao ## Atividade pratica.")
    if "Fechamento" not in h2_headings:
        errors.append("Falta a secao ## Fechamento.")

    question_headers = QUESTION_HEADER_RE.findall(content_text)
    if len(question_headers) != 2:
        errors.append("A aula precisa ter exatamente 2 blocos de questao.")

    for index, match in enumerate(QUESTION_BLOCK_RE.finditer(content_text), start=1):
        correct_count = len(CORRECT_ALTERNATIVE_RE.findall(match.group(1)))
        if correct_count != 1:
            errors.append(
                f"A questao {index} precisa ter exatamente uma alternativa terminando com ' *'."
            )

    if len(h2_headings) < 4:
        warnings.append("Poucas secoes H2; revisar estrutura da aula.")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Arquivo Markdown da aula")
    args = parser.parse_args()

    path = Path(args.path)
    result = validate_markdown(path.read_text(encoding="utf-8"))
    result["path"] = str(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


def run_self_test():
    valid_sample = """# Título da Aula

Parágrafo introdutório.

## Questões de fixação

:::questao Enunciado 1?
a) A errada
b) B certa *
> Explicação
:::

:::questao Enunciado 2?
a) A certa *
b) B errada
> Explicação
:::

## Atividade prática

:::exercicio
Texto da atividade.
:::

## Fechamento

:::resumo
- Ponto 1
:::
"""

    invalid_sample = """# Título da Aula

Parágrafo introdutório.

## Questões de fixação

## Atividade prática

:::exercicio
Texto da atividade.
:::

## Fechamento

:::resumo
- Ponto 1
:::
"""

    valid_result = validate_markdown(valid_sample)
    invalid_result = validate_markdown(invalid_sample)

    print(json.dumps({"case": "valid", **valid_result}, ensure_ascii=False, indent=2))
    print(json.dumps({"case": "invalid", **invalid_result}, ensure_ascii=False, indent=2))

    if valid_result["errors"]:
        raise SystemExit("Self-test falhou: o exemplo valido deveria ter zero erros.")
    if not any("2 blocos de questao" in error for error in invalid_result["errors"]):
        raise SystemExit(
            "Self-test falhou: o exemplo invalido deveria apontar ausencia de :::questao."
        )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        run_self_test()
