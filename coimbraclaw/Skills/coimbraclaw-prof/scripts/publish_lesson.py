#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from validate_lesson import validate_markdown


REPO_PATH = Path("/home/devuser/projects/ProfToniCoimbra")

COURSE_MAP = {
    ("1a-serie", "analise-e-metodos-para-sistemas"): "publicadas/materias/1a-serie/analise-e-metodos-para-sistemas",
    ("1a-serie", "introducao-a-computacao"): "publicadas/materias/1a-serie/introducao-a-computacao",
    ("2a-serie", "inovacao-tecnologia-e-empreendedorismo"): "publicadas/materias/2a-serie/inovacao-tecnologia-e-empreendedorismo",
    ("2a-serie", "programacao-front-end"): "publicadas/materias/2a-serie/programacao-front-end",
    ("3a-serie", "programacao-no-desenvolvimento-de-sistemas"): "publicadas/materias/3a-serie/programacao-no-desenvolvimento-de-sistemas",
    ("3a-serie", "analise-e-projeto-de-sistemas"): "publicadas/materias/3a-serie/analise-e-projeto-de-sistemas",
    ("disciplinas-extras", "inteligencia-artificial"): "publicadas/materias/disciplinas-extras/inteligencia-artificial",
}


def slugify(text):
    text = text.lower().strip()
    text = text.replace("ª", "a").replace("º", "o")
    text = re.sub(r"[áàãâä]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[íìîï]", "i", text)
    text = re.sub(r"[óòõôö]", "o", text)
    text = re.sub(r"[úùûü]", "u", text)
    text = re.sub(r"ç", "c", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def run_git(*args):
    return subprocess.run(
        ["git", "-C", str(REPO_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def update_manifest(entry):
    manifest_path = REPO_PATH / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lessons = manifest.get("lessons", [])
    lessons = [
        item
        for item in lessons
        if item.get("path") != entry["path"]
    ]
    lessons.append(entry)
    lessons.sort(key=lambda item: item["path"])
    manifest["lessons"] = lessons
    manifest["updatedAt"] = entry["publishedAt"]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def stage_rejected(source_text, rel_path):
    rejected_path = REPO_PATH / "staging" / "reprovadas" / rel_path
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.write_text(source_text, encoding="utf-8")
    return rejected_path


def ensure_repo():
    if not REPO_PATH.exists():
        raise RuntimeError(f"Repositorio nao encontrado: {REPO_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Arquivo Markdown de entrada")
    parser.add_argument("--series", required=True, help="Slug da serie")
    parser.add_argument("--subject", required=True, help="Slug da disciplina")
    parser.add_argument("--lesson-number", required=True, type=int, help="Numero da aula")
    parser.add_argument("--title", required=True, help="Titulo da aula")
    parser.add_argument("--push", action="store_true", help="Tenta push para o remoto")
    args = parser.parse_args()

    ensure_repo()

    key = (args.series, args.subject)
    if key not in COURSE_MAP:
        raise SystemExit(
            json.dumps(
                {
                    "ok": False,
                    "error": "Curso ou disciplina nao reconhecidos.",
                    "series": args.series,
                    "subject": args.subject,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    source_path = Path(args.input)
    source_text = source_path.read_text(encoding="utf-8")
    validation = validate_markdown(source_text)

    lesson_slug = slugify(args.title)
    filename = f"aula-{args.lesson_number:02d}-{lesson_slug}.md"
    rel_course_path = Path(COURSE_MAP[key])
    rel_output_path = rel_course_path / filename

    if not validation["ok"]:
        rejected_path = stage_rejected(source_text, Path(args.series) / args.subject / filename)
        print(
            json.dumps(
                {
                    "ok": False,
                    "validation": validation,
                    "rejectedPath": str(rejected_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(1)

    pending_path = REPO_PATH / "staging" / "pendentes" / args.series / args.subject / filename
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    pending_path.write_text(source_text, encoding="utf-8")

    final_path = REPO_PATH / rel_output_path
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(source_text, encoding="utf-8")
    pending_path.unlink(missing_ok=True)

    published_at = datetime.now(timezone.utc).isoformat()
    entry = {
        "series": args.series,
        "subject": args.subject,
        "lessonNumber": args.lesson_number,
        "title": args.title,
        "slug": lesson_slug,
        "path": str(rel_output_path),
        "status": "published",
        "publishedAt": published_at,
    }
    update_manifest(entry)

    run_git("add", str(rel_output_path), "manifest.json")
    status = run_git("status", "--short")
    commit_result = None
    if status.stdout.strip():
        commit_result = run_git(
            "commit",
            "-m",
            f"feat(aulas): publica aula {args.lesson_number:02d} de {args.subject}",
        )

    head = run_git("rev-parse", "HEAD")
    commit_sha = head.stdout.strip() if head.returncode == 0 else None

    push_status = "skipped"
    push_detail = None
    if args.push:
        remote = run_git("remote", "get-url", "origin")
        if remote.returncode != 0:
            push_status = "no-remote"
        else:
            push = run_git("push", "-u", "origin", "main")
            if push.returncode == 0:
                push_status = "ok"
            else:
                push_status = "failed"
                push_detail = (push.stderr or push.stdout).strip()

    print(
        json.dumps(
            {
                "ok": True,
                "validation": validation,
                "publishedPath": str(final_path),
                "repoPath": str(REPO_PATH),
                "commitSha": commit_sha,
                "commitCreated": bool(commit_result and commit_result.returncode == 0),
                "pushStatus": push_status,
                "pushDetail": push_detail,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
