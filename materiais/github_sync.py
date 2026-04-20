"""
Sincroniza materiais HTML estáticos do repositório GitHub ProfToniCoimbra.

Heurística: todo arquivo .html encontrado dentro de
publicadas/apostilas/<series>/<subject>/ é considerado um material da
matéria correspondente. Quando o arquivo começa com o prefixo aula-NN-,
o material é vinculado à Aula de mesmo número na turma.
"""

from __future__ import annotations

import logging
import re

import requests

from aulas.github_sync import GITHUB_RAW, get_subject_from_codigo
from aulas.models import Aula
from materiais.models import Material, TipoMaterial

logger = logging.getLogger(__name__)

GITHUB_TREE_URL = "https://api.github.com/repos/elvertoni/ProfToniCoimbra/git/trees/main?recursive=1"
APOSTILAS_PREFIX = "publicadas/apostilas/"
HTML_SUFFIX = ".html"
AULA_PREFIX_RE = re.compile(r"^aula-(\d+)-", re.IGNORECASE)
TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_TAG_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAGS_RE = re.compile(r"<[^>]+>")


def fetch_tree(session: requests.Session | None = None) -> list[dict]:
    """Retorna a lista plana de blobs do repositório (via git/trees recursive)."""
    http = session or requests
    resp = http.get(GITHUB_TREE_URL, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        logger.warning("GitHub tree truncada — alguns arquivos podem não aparecer na sync.")
    return data.get("tree", [])


def build_materials_index(tree: list[dict]) -> dict[str, list[str]]:
    """Indexa arquivos .html por subject extraído do path."""
    index: dict[str, list[str]] = {}
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item.get("path", "")
        if not path.startswith(APOSTILAS_PREFIX) or not path.endswith(HTML_SUFFIX):
            continue

        partes = path[len(APOSTILAS_PREFIX) :].split("/")
        if len(partes) != 3:
            continue
        _series, subject, _filename = partes

        index.setdefault(subject.lower(), []).append(path)
    return index


def _extrair_titulo(html: str, filename: str) -> str:
    """Tenta extrair título de <title>, depois <h1>, senão usa o nome do arquivo."""
    for regex in (TITLE_TAG_RE, H1_TAG_RE):
        match = regex.search(html)
        if match:
            bruto = TAGS_RE.sub("", match.group(1)).strip()
            if bruto:
                return bruto[:300]
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


def sync_turma(turma, materials_index: dict[str, list[str]]) -> dict:
    """Sincroniza os materiais HTML de uma turma.

    Retorna dict com: subject, criadas, atualizadas, erros, ignorada.
    """
    subject = get_subject_from_codigo(turma.codigo)
    if not subject:
        return {"subject": None, "criadas": 0, "atualizadas": 0, "erros": 0, "ignorada": True}

    materiais_do_subject = materials_index.get(subject.lower())
    if materiais_do_subject is None:
        return {
            "subject": subject,
            "criadas": 0,
            "atualizadas": 0,
            "erros": 0,
            "ignorada": True,
        }

    criadas = atualizadas = erros = 0
    session = requests.Session()

    for path in materiais_do_subject:
        filename = path.rsplit("/", 1)[-1]
        url = f"{GITHUB_RAW}/{path}"

        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
            html_content = resp.text
        except requests.RequestException as exc:
            logger.warning("Erro ao baixar material %s: %s", url, exc)
            erros += 1
            continue

        titulo = _extrair_titulo(html_content, filename)
        aula_obj = _descobrir_aula(turma, filename)
        descricao = f"Material sincronizado do GitHub: `{path}`"

        obj = Material.objects.filter(turma=turma, origem_github=path).first()
        if obj is None:
            Material.objects.create(
                turma=turma,
                titulo=titulo,
                conteudo_html=html_content,
                origem_github=path,
                tipo=TipoMaterial.HTML,
                descricao=descricao,
                aula=aula_obj,
            )
            criadas += 1
        else:
            obj.titulo = titulo
            obj.conteudo_html = html_content
            obj.descricao = descricao
            obj.aula = aula_obj
            obj.save(update_fields=["titulo", "conteudo_html", "descricao", "aula", "atualizado_em"])
            atualizadas += 1

    logger.info(
        "Turma '%s' — subject=%s criadas=%s atualizadas=%s erros=%s",
        turma.codigo,
        subject,
        criadas,
        atualizadas,
        erros,
    )
    return {
        "subject": subject,
        "criadas": criadas,
        "atualizadas": atualizadas,
        "erros": erros,
        "ignorada": False,
    }


def sync_all_turmas(turmas=None) -> list[dict]:
    """Sincroniza materiais HTML para uma coleção de turmas."""
    from turmas.models import Turma

    session = requests.Session()
    tree = fetch_tree(session=session)
    materials_index = build_materials_index(tree)

    turmas_iter = turmas if turmas is not None else Turma.objects.filter(ativa=True)
    resultados = []
    for turma in turmas_iter:
        resultados.append(sync_turma(turma, materials_index))
    return resultados
