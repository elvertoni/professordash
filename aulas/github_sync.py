"""
Utilitário para sincronizar aulas do repositório GitHub ProfToniCoimbra.

O mapeamento entre o prefixo do código da turma e o subject do GitHub:
  AMS → analise-e-metodos-para-sistemas
  IC  → introducao-a-computacao
  PFE → programacao-front-end
  ITE → inovacao-tecnologia-e-empreendedorismo
  PS  → programacao-no-desenvolvimento-de-sistemas
  APS → analise-e-projeto-de-sistemas
"""

import logging

import requests

from aulas.models import Aula

logger = logging.getLogger(__name__)

GITHUB_RAW = "https://raw.githubusercontent.com/elvertoni/ProfToniCoimbra/main"
MANIFEST_URL = f"{GITHUB_RAW}/manifest.json"

CODIGO_TO_SUBJECT = {
    "AMS": "analise-e-metodos-para-sistemas",
    "IC": "introducao-a-computacao",
    "PFE": "programacao-front-end",
    "ITE": "inovacao-tecnologia-e-empreendedorismo",
    "PS": "programacao-no-desenvolvimento-de-sistemas",
    "APS": "analise-e-projeto-de-sistemas",
}


def get_subject_from_codigo(codigo: str) -> str | None:
    """Retorna o subject do GitHub a partir do prefixo do código da turma."""
    prefix = codigo.split("-")[0].upper()
    return CODIGO_TO_SUBJECT.get(prefix)


def fetch_manifest() -> dict:
    """Baixa e retorna o manifest.json do repositório."""
    resp = requests.get(MANIFEST_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_lessons_index(manifest: dict) -> dict[str, list]:
    """Indexa as lessons do manifest por subject."""
    index: dict[str, list] = {}
    for lesson in manifest.get("lessons", []):
        subject = lesson.get("subject")
        if subject:
            index.setdefault(subject, []).append(lesson)
    return index


def sync_turma(turma, lessons_index: dict) -> dict:
    """
    Sincroniza as aulas de uma turma com o GitHub.

    Retorna dict com: subject, criadas, atualizadas, erros, ignorada.
    """
    subject = get_subject_from_codigo(turma.codigo)
    if not subject:
        return {"subject": None, "criadas": 0, "atualizadas": 0, "erros": 0, "ignorada": True}

    lessons = lessons_index.get(subject, [])
    criadas = atualizadas = erros = 0

    for lesson in lessons:
        path = lesson.get("path", "")
        numero = lesson.get("lessonNumber")
        titulo = lesson.get("title", "")

        if not path or not numero:
            continue

        url = f"{GITHUB_RAW}/{path}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            conteudo = resp.text
        except requests.RequestException as exc:
            logger.warning(f"Erro ao baixar aula {url}: {exc}")
            erros += 1
            continue

        _, created = Aula.objects.update_or_create(
            turma=turma,
            numero=numero,
            defaults={
                "titulo": titulo,
                "conteudo": conteudo,
                "ordem": numero,
            },
        )
        if created:
            criadas += 1
        else:
            atualizadas += 1

    logger.info(
        f"Turma '{turma.codigo}' — subject={subject} "
        f"criadas={criadas} atualizadas={atualizadas} erros={erros}"
    )
    return {
        "subject": subject,
        "criadas": criadas,
        "atualizadas": atualizadas,
        "erros": erros,
        "ignorada": False,
    }
