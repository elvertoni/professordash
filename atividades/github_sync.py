"""
Sincroniza atividades HTML estáticas do repositório GitHub ProfToniCoimbra.

Heurística: todo arquivo `.html` encontrado dentro de
`publicadas/materias/<series>/<subject>/` é considerado uma atividade da
matéria correspondente. Quando o arquivo começa com o prefixo `aula-NN-`,
a atividade é vinculada à Aula de mesmo número na turma.

Reuso do mapeamento `CODIGO_TO_SUBJECT` definido em `aulas.github_sync`.
"""

from __future__ import annotations

import logging
import re
from datetime import timedelta

import requests
from django.utils import timezone

from aulas.github_sync import GITHUB_RAW, get_subject_from_codigo
from aulas.models import Aula
from atividades.models import Atividade

logger = logging.getLogger(__name__)

GITHUB_TREE_URL = (
    "https://api.github.com/repos/elvertoni/ProfToniCoimbra/git/trees/main?recursive=1"
)
MATERIAS_PREFIX = "publicadas/materias/"
HTML_SUFFIX = ".html"
AULA_PREFIX_RE = re.compile(r"^aula-(\d+)-", re.IGNORECASE)
TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_TAG_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAGS_RE = re.compile(r"<[^>]+>")

PRAZO_PADRAO_DIAS = 30


def fetch_tree(session: requests.Session | None = None) -> list[dict]:
    """Retorna a lista plana de blobs do repositório (via git/trees recursive)."""
    http = session or requests
    resp = http.get(GITHUB_TREE_URL, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        logger.warning("GitHub tree truncada — alguns arquivos podem não aparecer na sync.")
    return data.get("tree", [])


def build_activities_index(tree: list[dict]) -> dict[str, list[dict]]:
    """Indexa arquivos .html por subject extraído do path.

    Exemplo de path aceito:
        publicadas/materias/2a-serie/programacao-front-end/aula-01-foo.html
    Resultado:
        {"programacao-front-end": [{"path": ..., "subject": ..., "filename": ...}, ...]}
    """
    index: dict[str, list[dict]] = {}
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item.get("path", "")
        if not path.startswith(MATERIAS_PREFIX) or not path.endswith(HTML_SUFFIX):
            continue

        partes = path[len(MATERIAS_PREFIX):].split("/")
        if len(partes) < 3:
            continue
        _series, subject, *resto = partes
        filename = resto[-1]

        index.setdefault(subject, []).append(
            {"path": path, "subject": subject, "filename": filename}
        )
    return index


def _extrair_titulo(html: str, filename: str) -> str:
    """Tenta extrair título de <title>, depois <h1>, senão usa o nome do arquivo."""
    for regex in (TITLE_TAG_RE, H1_TAG_RE):
        match = regex.search(html)
        if match:
            bruto = TAGS_RE.sub("", match.group(1)).strip()
            if bruto:
                return bruto[:300]
    # fallback: nome do arquivo humanizado
    base = filename.removesuffix(HTML_SUFFIX)
    base = AULA_PREFIX_RE.sub("", base)
    return base.replace("-", " ").strip().capitalize()[:300] or filename


def _descobrir_aula(turma, filename: str):
    """Vincula à Aula de mesmo número se o arquivo começar com `aula-NN-`."""
    match = AULA_PREFIX_RE.match(filename)
    if not match:
        return None
    numero = int(match.group(1))
    return Aula.objects.filter(turma=turma, numero=numero).first()


def sync_turma(turma, activities_index: dict[str, list[dict]]) -> dict:
    """Sincroniza as atividades HTML de uma turma.

    Retorna dict com: subject, criadas, atualizadas, erros, ignorada.
    """
    subject = get_subject_from_codigo(turma.codigo)
    if not subject:
        return {"subject": None, "criadas": 0, "atualizadas": 0, "erros": 0, "ignorada": True}

    atividades_do_subject = activities_index.get(subject, [])
    criadas = atualizadas = erros = 0
    session = requests.Session()

    for item in atividades_do_subject:
        path = item["path"]
        filename = item["filename"]
        url = f"{GITHUB_RAW}/{path}"

        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
            html = resp.text
        except requests.RequestException as exc:
            logger.warning("Erro ao baixar atividade %s: %s", url, exc)
            erros += 1
            continue

        titulo = _extrair_titulo(html, filename)
        aula = _descobrir_aula(turma, filename)

        defaults = {
            "titulo": titulo,
            "conteudo_html": html,
            "descricao": f"Atividade sincronizada do GitHub: `{path}`",
            "aula": aula,
        }

        atividade = Atividade.objects.filter(turma=turma, origem_github=path).first()
        if atividade is None:
            Atividade.objects.create(
                turma=turma,
                origem_github=path,
                prazo=timezone.now() + timedelta(days=PRAZO_PADRAO_DIAS),
                **defaults,
            )
            criadas += 1
        else:
            for campo, valor in defaults.items():
                setattr(atividade, campo, valor)
            atividade.save(
                update_fields=["titulo", "conteudo_html", "descricao", "aula", "atualizado_em"]
            )
            atualizadas += 1

    logger.info(
        "Turma '%s' — subject=%s criadas=%s atualizadas=%s erros=%s",
        turma.codigo, subject, criadas, atualizadas, erros,
    )
    return {
        "subject": subject,
        "criadas": criadas,
        "atualizadas": atualizadas,
        "erros": erros,
        "ignorada": False,
    }
